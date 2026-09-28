from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
from pathlib import Path

import pytest

PLUGIN_ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = PLUGIN_ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))

SPEC = importlib.util.spec_from_file_location("oli_ops", SCRIPTS / "oli_ops.py")
assert SPEC and SPEC.loader
oli_ops = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = oli_ops
SPEC.loader.exec_module(oli_ops)


def _config_document(tmp_path: Path) -> tuple[Path, dict[str, object]]:
    tmp_path.mkdir(parents=True, exist_ok=True)
    artifacts = tmp_path / "artifacts"
    secrets = tmp_path / "secrets"
    artifacts.mkdir()
    secrets.mkdir()
    for name in ("vault-role-id", "vault-secret-id"):
        path = secrets / name
        path.write_text(f"{name}-value", encoding="utf-8")
        path.chmod(0o600)

    plugin_manifest = json.loads(
        (PLUGIN_ROOT / ".codex-plugin" / "plugin.json").read_text(encoding="utf-8")
    )
    digest = oli_ops.plugin_digest.digest_result(PLUGIN_ROOT)["plugin_digest"]
    document: dict[str, object] = {
        "contract_version": "oli-indexer-ops-host/v1",
        "executor_site": "mac-studio-local",
        "backend": "docker",
        "plugin": {
            "expected_version": plugin_manifest["version"],
            "expected_digest": digest,
        },
        "runtime": {
            "image_ref": "ghcr.io/acme/oli-indexer@sha256:" + "a" * 64,
            "repo_sha": "b" * 40,
            "uv_lock_sha256": "c" * 64,
            "platform": "linux/arm64",
        },
        "paths": {
            "artifacts_dir": "./artifacts",
            "vault_role_id_file": "./secrets/vault-role-id",
            "vault_secret_id_file": "./secrets/vault-secret-id",
        },
        "vault": {"oli_auth_url": "https://auth.example.test"},
        "budgets": {
            "mode": "off",
            "llm": {"max_cost_usd": "0", "wall_seconds": 180},
            "reviewer": {"max_cost_usd": "0", "wall_seconds": 180},
            "embedding": {"max_cost_usd": "0", "wall_seconds": 120},
            "vision_page": {"max_cost_usd": "0", "wall_seconds": 120},
        },
        "resources": {
            "cpus": "2",
            "memory": "2g",
            "pids_limit": 256,
            "tmpfs_size": "1g",
        },
        "environment": {
            "LOG_LEVEL": "INFO",
            "PIPELINE_EXTRACTION_APPROVAL_MODE": "required",
            "PIPELINE_INDEXING_APPROVAL_MODE": "required",
        },
    }
    path = tmp_path / "host.json"
    path.write_text(json.dumps(document), encoding="utf-8")
    return path, document


def _rewrite(path: Path, document: dict[str, object]) -> None:
    path.write_text(json.dumps(document), encoding="utf-8")


def _run_only_args() -> list[str]:
    return [
        "--run-only",
        "--concurrency",
        "1",
        "--job-id",
        "2ff66a7e-1eb7-47b7-bdd7-4f7f2aec9717",
        "--orchestration-run-id",
        "8ad8b233-95c9-4ac9-b2ee-180f414774b1",
        "--json-output",
        "/artifacts/run.json",
    ]


def test_config_e_comando_docker_sao_portateis_e_cercados(tmp_path: Path) -> None:
    path, document = _config_document(tmp_path)
    config = oli_ops.load_config(path)

    command = oli_ops.build_docker_command(config, tool="run-batch", tool_args=_run_only_args())
    invocation = oli_ops.invocation_document(config, tool="run-batch", tool_args=_run_only_args())

    assert command[:2] == ["docker", "run"]
    assert "--read-only" in command
    assert command[command.index("--cap-drop") + 1] == "ALL"
    assert command[command.index("--security-opt") + 1] == "no-new-privileges"
    assert command[command.index("--platform") + 1] == "linux/arm64"
    assert config.image_ref in command
    assert "latest" not in " ".join(command)
    assert config.vault_role_id_file.as_posix() not in json.dumps(invocation)
    assert config.vault_secret_id_file.as_posix() not in json.dumps(invocation)
    assert invocation["command_sha256"]

    document["resources"]["memory"] = "4g"  # type: ignore[index]
    _rewrite(path, document)
    changed = oli_ops.invocation_document(
        oli_ops.load_config(path), tool="run-batch", tool_args=_run_only_args()
    )
    assert changed["command_sha256"] != invocation["command_sha256"]


@pytest.mark.parametrize(
    ("mutation", "message"),
    [
        (
            lambda document: document["runtime"].__setitem__(  # type: ignore[union-attr]
                "image_ref", "ghcr.io/acme/oli-indexer:latest"
            ),
            "referência OCI imutável",
        ),
        (
            lambda document: document["environment"].__setitem__(  # type: ignore[union-attr]
                "SUPABASE_JOBS_KEY", "segredo"
            ),
            "segredo ou override cercado",
        ),
        (
            lambda document: document["budgets"].__setitem__(  # type: ignore[union-attr]
                "mode", "enabled"
            ),
            "quatro custos positivos",
        ),
    ],
)
def test_config_rejeita_pin_mutavel_segredo_e_budget_parcial(
    tmp_path: Path, mutation, message: str
) -> None:
    path, document = _config_document(tmp_path)
    mutation(document)
    _rewrite(path, document)

    with pytest.raises(oli_ops.HostConfigError, match=message):
        oli_ops.load_config(path)


@pytest.mark.parametrize(
    ("args", "message"),
    [
        (
            [value for value in _run_only_args() if value != "1"],
            "--concurrency 1",
        ),
        (_run_only_args() + ["--run-log"], "flag proibida"),
        (
            [
                "--create-only",
                "--orchestration-run-id",
                "8ad8b233-95c9-4ac9-b2ee-180f414774b1",
                "--json-output",
                "/artifacts/create.json",
            ],
            "--enable-extraction-review",
        ),
        (
            [*_run_only_args()[:-1], "C:/host/run.json"],
            "deve apontar para /artifacts",
        ),
    ],
)
def test_launcher_rejeita_ampliacao_e_caminho_do_host(
    tmp_path: Path, args: list[str], message: str
) -> None:
    path, _ = _config_document(tmp_path)
    config = oli_ops.load_config(path)

    with pytest.raises(oli_ops.HostConfigError, match=message):
        oli_ops.build_docker_command(config, tool="run-batch", tool_args=args)


def test_doctor_atesta_plugin_imagem_e_segredos_sem_rede(tmp_path: Path) -> None:
    path, _ = _config_document(tmp_path)
    config = oli_ops.load_config(path)

    def fake_run(argv, **_kwargs):
        if argv[:2] == ["docker", "version"]:
            return subprocess.CompletedProcess(
                argv, 0, stdout=json.dumps({"Os": "linux", "Arch": "arm64"}), stderr=""
            )
        if argv[:3] == ["docker", "image", "inspect"]:
            return subprocess.CompletedProcess(
                argv,
                0,
                stdout=json.dumps(
                    [
                        {
                            "Os": "linux",
                            "Architecture": "arm64",
                            "Config": {
                                "User": "appuser",
                                "Labels": {
                                    "org.opencontainers.image.revision": config.repo_sha,
                                    "com.oliveiraeolivi.oli-indexer.uv-lock-sha256": config.uv_lock_sha256,
                                },
                            },
                        }
                    ]
                ),
                stderr="",
            )
        raise AssertionError(argv)

    document = oli_ops.doctor_document(config, run=fake_run)

    assert document["ready"] is True
    assert all(check["ok"] for check in document["checks"])
    assert document["executor_site"] == "mac-studio-local"


def test_doctor_falha_fechado_com_plugin_ou_imagem_divergente(tmp_path: Path) -> None:
    path, document = _config_document(tmp_path)
    document["plugin"]["expected_digest"] = "d" * 64  # type: ignore[index]
    _rewrite(path, document)
    config = oli_ops.load_config(path)

    def fake_run(argv, **_kwargs):
        if argv[:2] == ["docker", "version"]:
            payload = {"Os": "linux", "Arch": "amd64"}
        else:
            payload = [{"Os": "linux", "Architecture": "amd64", "Config": {}}]
        return subprocess.CompletedProcess(argv, 0, stdout=json.dumps(payload), stderr="")

    result = oli_ops.doctor_document(config, run=fake_run)

    assert result["ready"] is False
    failed = {item["name"] for item in result["checks"] if not item["ok"]}
    assert {"plugin_digest", "runtime_platform", "runtime_repo_sha", "runtime_non_root"} <= failed


def test_argumento_com_quebra_de_linha_nunca_chega_ao_docker(tmp_path: Path) -> None:
    path, _ = _config_document(tmp_path)
    config = oli_ops.load_config(path)

    with pytest.raises(oli_ops.HostConfigError, match="controle de linha"):
        oli_ops.build_docker_command(
            config,
            tool="reviewctl",
            tool_args=["snapshot", "--job-id", "ok\n--execute"],
        )


def test_execute_exige_hash_exato_do_preview(tmp_path: Path, capsys) -> None:
    path, _ = _config_document(tmp_path)
    args = oli_ops.build_parser().parse_args(
        [
            "invoke",
            "--config",
            str(path),
            "--tool",
            "run-batch",
            "--execute",
            "--expected-command-sha256",
            "d" * 64,
            "--",
            *_run_only_args(),
        ]
    )

    with pytest.raises(oli_ops.HostConfigError, match="divergiu do preview"):
        oli_ops._invoke(args)
    emitted = json.loads(capsys.readouterr().out)
    assert emitted["execute"] is True
    assert emitted["status"] == "REJECTED"
    artifact = Path(emitted["artifact_path"])
    assert artifact.is_file()
    persisted = json.loads(artifact.read_text(encoding="utf-8"))
    assert persisted["command_sha256"] == emitted["command_sha256"]
    assert "vault-role-id" not in artifact.read_text(encoding="utf-8")


def test_doctor_rejeita_secret_file_symlink(tmp_path: Path) -> None:
    path, document = _config_document(tmp_path)
    target = tmp_path / "secrets" / "vault-role-target"
    target.write_text("role", encoding="utf-8")
    target.chmod(0o600)
    link = tmp_path / "secrets" / "vault-role-link"
    try:
        link.symlink_to(target)
    except OSError:
        pytest.skip("host sem permissão para criar symlink")
    document["paths"]["vault_role_id_file"] = str(link)  # type: ignore[index]
    _rewrite(path, document)
    config = oli_ops.load_config(path)

    def unavailable(argv, **_kwargs):
        return subprocess.CompletedProcess(argv, 1, stdout="", stderr="unavailable")

    result = oli_ops.doctor_document(config, run=unavailable)
    check = next(item for item in result["checks"] if item["name"] == "vault_role_id_file")
    assert check["ok"] is False
