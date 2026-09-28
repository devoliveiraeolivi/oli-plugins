#!/usr/bin/env python3
"""Launcher portátil e fail-closed do runtime Docker do oli-indexer-ops."""

from __future__ import annotations

import argparse
import hashlib
import hmac
import json
import os
import platform as host_platform
import re
import subprocess
import sys
import tempfile
from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass
from datetime import UTC, datetime
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Any

import plugin_digest

PLUGIN_ROOT = Path(__file__).resolve().parents[1]
HOST_CONFIG_CONTRACT = "oli-indexer-ops-host/v1"
DOCTOR_CONTRACT = "oli-indexer-ops-doctor/v1"
INVOCATION_CONTRACT = "oli-indexer-ops-invocation/v1"
IMAGE_RE = re.compile(r"^[^\s]+@sha256:[0-9a-f]{64}$")
REPO_SHA_RE = re.compile(r"^[0-9a-f]{40}(?:[0-9a-f]{24})?$")
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
SITE_RE = re.compile(r"^[a-z0-9][a-z0-9._-]{0,63}$")
SIZE_RE = re.compile(r"^[1-9][0-9]*(?:[kKmMgG])$")
ENV_NAME_RE = re.compile(r"^[A-Z][A-Z0-9_]*$")
SUPPORTED_PLATFORMS = {"linux/amd64", "linux/arm64"}
EFFECTS = ("llm", "reviewer", "embedding", "vision_page")
SAFE_ENV_NAMES = {"LOG_LEVEL", "GOOGLE_SHEETS__TARGET_FOLDER_ID"}
SAFE_ENV_PREFIXES = (
    "PIPELINE_",
    "LLM_",
    "GATEWAY_",
    "EMBEDDING_",
    "GOOGLE_GEMINI_",
    "GOOGLE_VISION_",
    "HELICONE_",
)
SECRET_ENV_FRAGMENTS = (
    "API_KEY",
    "CREDENTIAL",
    "PASSWORD",
    "PRIVATE_KEY",
    "ROLE_ID",
    "SECRET",
    "TOKEN",
)
FORBIDDEN_ENV_PREFIXES = (
    "DOCKER_",
    "ORCHESTRATION_RUNTIME_",
    "SALESFORCE_",
    "SUPABASE_",
    "VAULT_",
)
TOOL_ENTRYPOINTS: dict[str, tuple[str, ...]] = {
    "orchestrationctl": ("python", "scripts/ops/orchestrationctl.py"),
    "run-batch": ("python", "scripts/ops/run_batch.py"),
    "reviewctl": ("reviewctl",),
    "extraction-reviewctl": ("extraction-reviewctl",),
}
FORBIDDEN_TOOL_FLAGS = {
    "--allow-multiple",
    "--delete-folhas",
    "--run-log",
}
ARTIFACT_PATH_FLAGS = {
    "--intent",
    "--json-output",
    "--output",
    "--patch",
    "--report",
    "--snapshot",
    "--targets",
}


class HostConfigError(RuntimeError):
    """Configuração local inválida ou runtime não atestado."""


@dataclass(frozen=True, slots=True)
class EffectBound:
    max_cost_usd: str
    wall_seconds: int


@dataclass(frozen=True, slots=True)
class HostConfig:
    path: Path
    executor_site: str
    expected_plugin_version: str
    expected_plugin_digest: str
    image_ref: str
    repo_sha: str
    uv_lock_sha256: str
    platform: str
    artifacts_dir: Path
    vault_role_id_file: Path
    vault_secret_id_file: Path
    oli_auth_url: str
    budget_mode: str
    bounds: Mapping[str, EffectBound]
    cpus: str
    memory: str
    pids_limit: int
    tmpfs_size: str
    environment: Mapping[str, str]


Run = Callable[..., subprocess.CompletedProcess[str]]


def _object(value: Any, label: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise HostConfigError(f"{label} deve ser objeto")
    return value


def _exact_keys(value: Mapping[str, Any], expected: set[str], label: str) -> None:
    missing = sorted(expected - set(value))
    extra = sorted(set(value) - expected)
    if missing or extra:
        raise HostConfigError(f"{label} diverge: ausentes={missing}, extras={extra}")


def _string(value: Any, label: str) -> str:
    if not isinstance(value, str) or not value or "\x00" in value or "\n" in value:
        raise HostConfigError(f"{label} deve ser texto não vazio em uma linha")
    return value


def _resolve_path(raw: Any, *, base: Path, label: str) -> Path:
    value = Path(_string(raw, label)).expanduser()
    if not value.is_absolute():
        value = base / value
    return Path(os.path.abspath(value))


def _cost(value: Any, label: str) -> str:
    if not isinstance(value, str):
        raise HostConfigError(f"{label} deve ser decimal JSON em formato texto")
    try:
        parsed = Decimal(value)
    except InvalidOperation as exc:
        raise HostConfigError(f"{label} deve ser decimal finito não negativo") from exc
    if not parsed.is_finite() or parsed < 0:
        raise HostConfigError(f"{label} deve ser decimal finito não negativo")
    return format(parsed, "f")


def _positive_int(value: Any, label: str) -> int:
    if not isinstance(value, int) or isinstance(value, bool) or value <= 0:
        raise HostConfigError(f"{label} deve ser inteiro positivo")
    return value


def _environment(value: Any) -> dict[str, str]:
    raw = _object(value, "environment")
    checked: dict[str, str] = {}
    for name, candidate in raw.items():
        if not isinstance(name, str) or not ENV_NAME_RE.fullmatch(name):
            raise HostConfigError(f"environment contém nome inválido: {name!r}")
        if name.startswith(FORBIDDEN_ENV_PREFIXES) or any(
            fragment in name for fragment in SECRET_ENV_FRAGMENTS
        ):
            raise HostConfigError(f"environment não aceita segredo ou override cercado: {name}")
        if name not in SAFE_ENV_NAMES and not name.startswith(SAFE_ENV_PREFIXES):
            raise HostConfigError(f"environment fora da allowlist: {name}")
        checked[name] = _string(candidate, f"environment.{name}")
    log_level = checked.get("LOG_LEVEL", "INFO")
    if log_level not in {"DEBUG", "INFO", "WARNING", "ERROR"}:
        raise HostConfigError("environment.LOG_LEVEL inválido")
    checked["LOG_LEVEL"] = log_level
    return checked


def load_config(path: Path) -> HostConfig:
    path = path.expanduser().resolve()
    try:
        document = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise HostConfigError(f"não foi possível ler host config: {exc}") from exc
    root = _object(document, "host config")
    _exact_keys(
        root,
        {
            "contract_version",
            "executor_site",
            "backend",
            "plugin",
            "runtime",
            "paths",
            "vault",
            "budgets",
            "resources",
            "environment",
        },
        "host config",
    )
    if root["contract_version"] != HOST_CONFIG_CONTRACT:
        raise HostConfigError(f"contract_version deve ser {HOST_CONFIG_CONTRACT}")
    if root["backend"] != "docker":
        raise HostConfigError("backend v1 aceita somente docker")
    executor_site = _string(root["executor_site"], "executor_site")
    if not SITE_RE.fullmatch(executor_site):
        raise HostConfigError("executor_site deve ser slug estável de até 64 caracteres")

    plugin = _object(root["plugin"], "plugin")
    _exact_keys(plugin, {"expected_version", "expected_digest"}, "plugin")
    expected_version = _string(plugin["expected_version"], "plugin.expected_version")
    expected_digest = _string(plugin["expected_digest"], "plugin.expected_digest")
    if not SHA256_RE.fullmatch(expected_digest):
        raise HostConfigError("plugin.expected_digest deve ser SHA-256")

    runtime = _object(root["runtime"], "runtime")
    _exact_keys(
        runtime,
        {"image_ref", "repo_sha", "uv_lock_sha256", "platform"},
        "runtime",
    )
    image_ref = _string(runtime["image_ref"], "runtime.image_ref")
    repo_sha = _string(runtime["repo_sha"], "runtime.repo_sha")
    uv_lock_sha256 = _string(runtime["uv_lock_sha256"], "runtime.uv_lock_sha256")
    selected_platform = _string(runtime["platform"], "runtime.platform")
    if not IMAGE_RE.fullmatch(image_ref):
        raise HostConfigError("runtime.image_ref deve usar referência OCI imutável por digest")
    if not REPO_SHA_RE.fullmatch(repo_sha):
        raise HostConfigError("runtime.repo_sha deve ser SHA Git completo")
    if not SHA256_RE.fullmatch(uv_lock_sha256):
        raise HostConfigError("runtime.uv_lock_sha256 deve ser SHA-256")
    if selected_platform not in SUPPORTED_PLATFORMS:
        raise HostConfigError(f"runtime.platform não suportada: {selected_platform}")

    paths = _object(root["paths"], "paths")
    _exact_keys(
        paths,
        {"artifacts_dir", "vault_role_id_file", "vault_secret_id_file"},
        "paths",
    )
    base = path.parent

    vault = _object(root["vault"], "vault")
    _exact_keys(vault, {"oli_auth_url"}, "vault")
    oli_auth_url = _string(vault["oli_auth_url"], "vault.oli_auth_url")
    if not oli_auth_url.startswith("https://"):
        raise HostConfigError("vault.oli_auth_url deve usar HTTPS")

    budgets = _object(root["budgets"], "budgets")
    _exact_keys(budgets, {"mode", *EFFECTS}, "budgets")
    budget_mode = _string(budgets["mode"], "budgets.mode")
    if budget_mode not in {"off", "enabled"}:
        raise HostConfigError("budgets.mode deve ser off ou enabled")
    bounds: dict[str, EffectBound] = {}
    for effect in EFFECTS:
        raw_bound = _object(budgets[effect], f"budgets.{effect}")
        _exact_keys(raw_bound, {"max_cost_usd", "wall_seconds"}, f"budgets.{effect}")
        bounds[effect] = EffectBound(
            max_cost_usd=_cost(raw_bound["max_cost_usd"], f"budgets.{effect}.max_cost_usd"),
            wall_seconds=_positive_int(raw_bound["wall_seconds"], f"budgets.{effect}.wall_seconds"),
        )
    positive = [Decimal(bound.max_cost_usd) > 0 for bound in bounds.values()]
    if budget_mode == "off" and any(positive):
        raise HostConfigError("budgets off exige quatro custos zero")
    if budget_mode == "enabled" and not all(positive):
        raise HostConfigError("budgets enabled exige quatro custos positivos")

    resources = _object(root["resources"], "resources")
    _exact_keys(resources, {"cpus", "memory", "pids_limit", "tmpfs_size"}, "resources")
    cpus = _cost(resources["cpus"], "resources.cpus")
    if Decimal(cpus) <= 0:
        raise HostConfigError("resources.cpus deve ser positivo")
    memory = _string(resources["memory"], "resources.memory")
    tmpfs_size = _string(resources["tmpfs_size"], "resources.tmpfs_size")
    if not SIZE_RE.fullmatch(memory) or not SIZE_RE.fullmatch(tmpfs_size):
        raise HostConfigError("resources.memory/tmpfs_size devem usar unidade k, m ou g")
    pids_limit = _positive_int(resources["pids_limit"], "resources.pids_limit")
    if pids_limit > 4096:
        raise HostConfigError("resources.pids_limit não pode exceder 4096")

    return HostConfig(
        path=path,
        executor_site=executor_site,
        expected_plugin_version=expected_version,
        expected_plugin_digest=expected_digest,
        image_ref=image_ref,
        repo_sha=repo_sha,
        uv_lock_sha256=uv_lock_sha256,
        platform=selected_platform,
        artifacts_dir=_resolve_path(paths["artifacts_dir"], base=base, label="paths.artifacts_dir"),
        vault_role_id_file=_resolve_path(
            paths["vault_role_id_file"], base=base, label="paths.vault_role_id_file"
        ),
        vault_secret_id_file=_resolve_path(
            paths["vault_secret_id_file"], base=base, label="paths.vault_secret_id_file"
        ),
        oli_auth_url=oli_auth_url,
        budget_mode=budget_mode,
        bounds=bounds,
        cpus=cpus,
        memory=memory.lower(),
        pids_limit=pids_limit,
        tmpfs_size=tmpfs_size.lower(),
        environment=_environment(root["environment"]),
    )


def _check(name: str, ok: bool, detail: str) -> dict[str, Any]:
    return {"name": name, "ok": ok, "detail": detail}


def _run_json(argv: Sequence[str], *, run: Run) -> tuple[bool, Any, str]:
    try:
        result = run(
            list(argv),
            check=False,
            capture_output=True,
            text=True,
            timeout=20,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        return False, None, f"{type(exc).__name__}: {exc}"
    if result.returncode != 0:
        return False, None, (result.stderr or result.stdout).strip()[:500]
    try:
        return True, json.loads(result.stdout), "ok"
    except json.JSONDecodeError as exc:
        return False, None, f"JSON inválido: {exc}"


def doctor_document(config: HostConfig, *, run: Run = subprocess.run) -> dict[str, Any]:
    checks: list[dict[str, Any]] = []
    manifest_path = PLUGIN_ROOT / ".codex-plugin" / "plugin.json"
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        version = str(manifest.get("version", ""))
    except (OSError, json.JSONDecodeError) as exc:
        version = ""
        checks.append(_check("plugin_manifest", False, str(exc)))
    else:
        checks.append(
            _check(
                "plugin_version",
                version == config.expected_plugin_version,
                f"expected={config.expected_plugin_version}, actual={version}",
            )
        )
    try:
        digest = str(plugin_digest.digest_result(PLUGIN_ROOT)["plugin_digest"])
    except (OSError, plugin_digest.PluginDigestError) as exc:
        digest = ""
        checks.append(_check("plugin_digest", False, str(exc)))
    else:
        checks.append(
            _check(
                "plugin_digest",
                digest == config.expected_plugin_digest,
                f"expected={config.expected_plugin_digest}, actual={digest}",
            )
        )

    checks.append(
        _check(
            "artifacts_dir",
            config.artifacts_dir.is_dir()
            and not config.artifacts_dir.is_symlink()
            and os.access(config.artifacts_dir, os.W_OK),
            str(config.artifacts_dir),
        )
    )
    for label, secret_path in (
        ("vault_role_id_file", config.vault_role_id_file),
        ("vault_secret_id_file", config.vault_secret_id_file),
    ):
        exists = (
            secret_path.is_file()
            and not secret_path.is_symlink()
            and os.access(secret_path, os.R_OK)
        )
        detail = str(secret_path)
        if exists and os.name == "posix" and secret_path.stat().st_mode & 0o077:
            exists = False
            detail += " (permissões devem negar grupo/outros)"
        checks.append(_check(label, exists, detail))

    docker_ok, server, docker_detail = _run_json(
        ["docker", "version", "--format", "{{json .Server}}"], run=run
    )
    checks.append(_check("docker_server", docker_ok, docker_detail))
    engine_arch = ""
    if docker_ok and isinstance(server, dict):
        engine_arch = str(server.get("Arch", ""))
        checks.append(_check("docker_os", server.get("Os") == "linux", str(server.get("Os"))))

    image_ok, images, image_detail = _run_json(
        ["docker", "image", "inspect", config.image_ref], run=run
    )
    image: dict[str, Any] = {}
    if image_ok and isinstance(images, list) and len(images) == 1 and isinstance(images[0], dict):
        image = images[0]
    else:
        image_ok = False
    checks.append(_check("runtime_image_local", image_ok, image_detail))
    if image:
        image_config = image.get("Config")
        if not isinstance(image_config, dict):
            image_config = {}
        labels = image_config.get("Labels")
        if not isinstance(labels, dict):
            labels = {}
        checks.extend(
            [
                _check("runtime_os", image.get("Os") == "linux", str(image.get("Os"))),
                _check(
                    "runtime_platform",
                    f"linux/{image.get('Architecture')}" == config.platform,
                    f"expected={config.platform}, actual=linux/{image.get('Architecture')}",
                ),
                _check(
                    "runtime_repo_sha",
                    labels.get("org.opencontainers.image.revision") == config.repo_sha,
                    f"expected={config.repo_sha}, actual={labels.get('org.opencontainers.image.revision')}",
                ),
                _check(
                    "runtime_uv_lock",
                    labels.get("com.oliveiraeolivi.oli-indexer.uv-lock-sha256")
                    == config.uv_lock_sha256,
                    "label OCI do lockfile",
                ),
                _check(
                    "runtime_non_root",
                    str(image_config.get("User") or "") not in {"", "0", "root"},
                    str(image_config.get("User") or "<empty>"),
                ),
            ]
        )

    ready = all(bool(check["ok"]) for check in checks)
    return {
        "contract_version": DOCTOR_CONTRACT,
        "ready": ready,
        "executor_site": config.executor_site,
        "host": {
            "system": host_platform.system(),
            "machine": host_platform.machine(),
            "docker_engine_arch": engine_arch,
        },
        "plugin": {"version": version, "digest": digest},
        "runtime": {
            "image_ref": config.image_ref,
            "repo_sha": config.repo_sha,
            "uv_lock_sha256": config.uv_lock_sha256,
            "platform": config.platform,
            "budget_mode": config.budget_mode,
        },
        "checks": checks,
    }


def _mount(source: Path, target: str, *, readonly: bool = False) -> str:
    raw = str(source)
    if "," in raw:
        raise HostConfigError(f"caminho com vírgula não é suportado pelo mount Docker: {raw}")
    suffix = ",readonly" if readonly else ""
    return f"type=bind,src={raw},dst={target}{suffix}"


def _runtime_environment(config: HostConfig) -> dict[str, str]:
    environment = {
        "ENVIRONMENT": "production",
        "JOB_SOURCE": "supabase",
        "OLI_AUTH_URL": config.oli_auth_url,
        "VAULT_ROLE_ID_FILE": "/run/secrets/oli_indexer_vault_role_id",
        "VAULT_SECRET_ID_FILE": "/run/secrets/oli_indexer_vault_secret_id",
        "OLI_INDEXER_EXECUTOR_SITE": config.executor_site,
        "ORCHESTRATION_RUNTIME_IMAGE_REF": config.image_ref,
        "ORCHESTRATION_RUNTIME_REPO_SHA": config.repo_sha,
        "PYTHONUNBUFFERED": "1",
        "HOME": "/tmp/home",
        "XDG_CACHE_HOME": "/tmp/home/.cache",
    }
    environment.update(config.environment)
    env_effect = {
        "llm": "LLM",
        "reviewer": "REVIEWER",
        "embedding": "EMBEDDING",
        "vision_page": "VISION_PAGE",
    }
    for effect, prefix in env_effect.items():
        bound = config.bounds[effect]
        environment[f"ORCHESTRATION_RUNTIME_{prefix}_MAX_COST_USD"] = bound.max_cost_usd
        environment[f"ORCHESTRATION_RUNTIME_{prefix}_WALL_SECONDS"] = str(bound.wall_seconds)
    return environment


def build_docker_command(config: HostConfig, *, tool: str, tool_args: Sequence[str]) -> list[str]:
    entrypoint = TOOL_ENTRYPOINTS.get(tool)
    if entrypoint is None:
        raise HostConfigError(f"tool não suportada: {tool}")
    _validate_tool_args(tool, tool_args)
    environment = _runtime_environment(config)
    command = [
        "docker",
        "run",
        "--rm",
        "--init",
        "--platform",
        config.platform,
        "--read-only",
        "--cap-drop",
        "ALL",
        "--security-opt",
        "no-new-privileges",
        "--network",
        "bridge",
        "--pids-limit",
        str(config.pids_limit),
        "--memory",
        config.memory,
        "--cpus",
        config.cpus,
        "--stop-timeout",
        "30",
        "--tmpfs",
        f"/tmp:rw,noexec,nosuid,nodev,size={config.tmpfs_size}",
        "--label",
        f"com.oliveiraeolivi.oli-indexer.executor-site={config.executor_site}",
        "--label",
        f"com.oliveiraeolivi.oli-indexer.plugin-digest={config.expected_plugin_digest}",
        "--mount",
        _mount(config.artifacts_dir, "/artifacts"),
        "--mount",
        _mount(
            config.vault_role_id_file,
            "/run/secrets/oli_indexer_vault_role_id",
            readonly=True,
        ),
        "--mount",
        _mount(
            config.vault_secret_id_file,
            "/run/secrets/oli_indexer_vault_secret_id",
            readonly=True,
        ),
    ]
    for name, value in sorted(environment.items()):
        command.extend(["--env", f"{name}={value}"])
    command.extend(["--entrypoint", entrypoint[0], config.image_ref, *entrypoint[1:], *tool_args])
    return command


def _flag_present(args: Sequence[str], flag: str) -> bool:
    return flag in args or any(value.startswith(f"{flag}=") for value in args)


def _flag_values(args: Sequence[str], flag: str) -> list[str]:
    values: list[str] = []
    for index, value in enumerate(args):
        if value == flag:
            if index + 1 >= len(args):
                raise HostConfigError(f"{flag} exige valor")
            values.append(args[index + 1])
        elif value.startswith(f"{flag}="):
            values.append(value.split("=", 1)[1])
    return values


def _validate_artifact_paths(args: Sequence[str]) -> None:
    for flag in ARTIFACT_PATH_FLAGS:
        for value in _flag_values(args, flag):
            normalized = value.replace("\\", "/")
            if normalized != "/artifacts" and not normalized.startswith("/artifacts/"):
                raise HostConfigError(f"{flag} deve apontar para /artifacts dentro do container")


def _validate_tool_args(tool: str, raw_args: Sequence[str]) -> None:
    args = list(raw_args)
    if args and args[0] == "--":
        args.pop(0)
    if not args:
        raise HostConfigError("a tool exige argumentos explícitos")
    for value in args:
        if "\x00" in value or "\n" in value or "\r" in value:
            raise HostConfigError("argumento contém controle de linha")
    for flag in FORBIDDEN_TOOL_FLAGS:
        if _flag_present(args, flag):
            raise HostConfigError(f"flag proibida pelo launcher portátil: {flag}")
    _validate_artifact_paths(args)

    if tool == "run-batch":
        modes = [
            flag
            for flag in ("--create-only", "--run-only", "--run-approved")
            if _flag_present(args, flag)
        ]
        if len(modes) != 1:
            raise HostConfigError("run-batch exige exatamente um modo explícito")
        if not _flag_present(args, "--orchestration-run-id"):
            raise HostConfigError("run-batch exige --orchestration-run-id")
        if not _flag_present(args, "--json-output"):
            raise HostConfigError("run-batch exige --json-output em /artifacts")
        if modes[0] == "--create-only":
            for required in ("--enable-extraction-review", "--enable-indexing-approval"):
                if not _flag_present(args, required):
                    raise HostConfigError(f"criação orquestrada exige {required}")
        else:
            if not _flag_present(args, "--job-id"):
                raise HostConfigError("execução orquestrada exige ao menos um --job-id")
            concurrency = _flag_values(args, "--concurrency")
            if concurrency != ["1"]:
                raise HostConfigError("execução orquestrada exige --concurrency 1")
    elif tool == "orchestrationctl":
        if args[0] not in {"preview", "register", "show", "reconcile-reaper"}:
            raise HostConfigError("subcomando orchestrationctl não suportado")
        if not _flag_present(args, "--output"):
            raise HostConfigError("orchestrationctl exige --output em /artifacts")


def _redacted_command(command: Sequence[str], config: HostConfig) -> list[str]:
    redacted: list[str] = []
    secret_paths = {str(config.vault_role_id_file), str(config.vault_secret_id_file)}
    for value in command:
        rendered = value
        for secret in secret_paths:
            rendered = rendered.replace(secret, "<secret-file>")
        redacted.append(rendered)
    return redacted


def invocation_document(
    config: HostConfig, *, tool: str, tool_args: Sequence[str]
) -> dict[str, Any]:
    normalized_args = list(tool_args)
    if normalized_args and normalized_args[0] == "--":
        normalized_args.pop(0)
    command = build_docker_command(config, tool=tool, tool_args=normalized_args)
    encoded = json.dumps(command, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
    return {
        "contract_version": INVOCATION_CONTRACT,
        "executor_site": config.executor_site,
        "tool": tool,
        "execute": False,
        "command_sha256": hashlib.sha256(encoded).hexdigest(),
        "command": _redacted_command(command, config),
    }


def _emit(document: Mapping[str, Any]) -> None:
    print(json.dumps(document, ensure_ascii=False, indent=2, sort_keys=True))


def _persist_invocation(config: HostConfig, document: dict[str, Any]) -> Path:
    if not config.artifacts_dir.is_dir() or config.artifacts_dir.is_symlink():
        raise HostConfigError("diretório de artefatos ausente ou inseguro")
    launcher_dir = config.artifacts_dir / "launcher"
    directory = launcher_dir / "invocations"
    for candidate in (launcher_dir, directory):
        if candidate.is_symlink():
            raise HostConfigError(f"diretório de auditoria não pode ser symlink: {candidate}")
        candidate.mkdir(exist_ok=True)
    target = directory / f"{document['command_sha256']}.json"
    document["artifact_path"] = str(target)
    temporary: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            dir=directory,
            prefix=f".{target.name}.",
            suffix=".tmp",
            delete=False,
        ) as stream:
            temporary = Path(stream.name)
            json.dump(document, stream, ensure_ascii=False, indent=2, sort_keys=True)
            stream.write("\n")
        os.replace(temporary, target)
    except OSError as exc:
        if temporary is not None:
            temporary.unlink(missing_ok=True)
        raise HostConfigError(f"não foi possível persistir a invocação: {exc}") from exc
    return target


def _doctor(args: argparse.Namespace) -> int:
    config = load_config(args.config)
    document = doctor_document(config)
    _emit(document)
    return 0 if document["ready"] else 1


def _pull(args: argparse.Namespace) -> int:
    config = load_config(args.config)
    plan = {
        "contract_version": "oli-indexer-ops-pull/v1",
        "execute": bool(args.execute),
        "executor_site": config.executor_site,
        "image_ref": config.image_ref,
        "platform": config.platform,
    }
    _emit(plan)
    if not args.execute:
        return 0
    result = subprocess.run(
        ["docker", "pull", "--platform", config.platform, config.image_ref],
        check=False,
    )
    if result.returncode != 0:
        return result.returncode
    doctor = doctor_document(config)
    _emit(doctor)
    return 0 if doctor["ready"] else 1


def _invoke(args: argparse.Namespace) -> int:
    config = load_config(args.config)
    tool_args = list(args.tool_args)
    if tool_args and tool_args[0] == "--":
        tool_args.pop(0)
    document = invocation_document(config, tool=args.tool, tool_args=tool_args)
    document["execute"] = bool(args.execute)
    document["status"] = "PREVIEW"
    if not args.execute:
        _persist_invocation(config, document)
        _emit(document)
        return 0
    if not args.expected_command_sha256:
        reason = "--execute exige --expected-command-sha256 do preview"
    elif not SHA256_RE.fullmatch(args.expected_command_sha256):
        reason = "--expected-command-sha256 deve ser SHA-256"
    elif not hmac.compare_digest(args.expected_command_sha256, str(document["command_sha256"])):
        reason = "comando/configuração divergiu do preview autorizado"
    else:
        reason = ""
    if reason:
        document.update({"status": "REJECTED", "reason": reason})
        _persist_invocation(config, document)
        _emit(document)
        raise HostConfigError(reason)
    document["status"] = "READY"
    _persist_invocation(config, document)
    _emit(document)
    doctor = doctor_document(config)
    if not doctor["ready"]:
        document.update(
            {
                "status": "BLOCKED_BY_DOCTOR",
                "finished_at": datetime.now(UTC).isoformat(),
            }
        )
        _persist_invocation(config, document)
        _emit(doctor)
        return 1
    command = build_docker_command(config, tool=args.tool, tool_args=tool_args)
    try:
        returncode = subprocess.run(command, check=False).returncode
    except OSError as exc:
        document.update(
            {
                "status": "LAUNCH_FAILED",
                "finished_at": datetime.now(UTC).isoformat(),
                "error_type": type(exc).__name__,
            }
        )
        _persist_invocation(config, document)
        raise HostConfigError(f"falha ao iniciar Docker: {type(exc).__name__}") from exc
    document.update(
        {
            "status": "COMPLETED" if returncode == 0 else "FAILED",
            "finished_at": datetime.now(UTC).isoformat(),
            "exit_code": returncode,
        }
    )
    _persist_invocation(config, document)
    return returncode


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    doctor = subparsers.add_parser("doctor", help="Valida host, plugin e imagem sem pull")
    doctor.add_argument("--config", required=True, type=Path)
    doctor.set_defaults(handler=_doctor)

    pull = subparsers.add_parser("pull", help="Planeja ou baixa a imagem imutável exata")
    pull.add_argument("--config", required=True, type=Path)
    pull.add_argument("--execute", action="store_true")
    pull.set_defaults(handler=_pull)

    invoke = subparsers.add_parser("invoke", help="Planeja ou executa uma tool cercada no Docker")
    invoke.add_argument("--config", required=True, type=Path)
    invoke.add_argument("--tool", required=True, choices=sorted(TOOL_ENTRYPOINTS))
    invoke.add_argument("--execute", action="store_true")
    invoke.add_argument("--expected-command-sha256")
    invoke.add_argument("tool_args", nargs=argparse.REMAINDER)
    invoke.set_defaults(handler=_invoke)
    return parser


def main(argv: list[str] | None = None) -> int:
    try:
        args = build_parser().parse_args(argv)
        return int(args.handler(args))
    except HostConfigError as exc:
        print(f"erro: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
