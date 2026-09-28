#!/usr/bin/env python3
"""Validate the local oli-indexer-ops source without third-party dependencies."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKILLS = ROOT / "skills"
AUTO_SKILLS = {
    "consultar-oli-indexer",
    "inspecionar-configuracao-indexacao",
    "orquestrar-indexacoes",
    "preaprovar-extracoes",
    "preaprovar-indexacoes",
    "preaprovar-insumos-indexacao",
}
PROFILE_ALIASES = {
    "preaprovar-agravos-tributarios": "references/profiles/agravo-instrumento.md",
    "preaprovar-cautelares-fiscais": "references/profiles/cautelar-fiscal.md",
    "preaprovar-compactacoes-documentais": "references/overlays/compactacao-documental.md",
    "preaprovar-conhecimento-tributario": "references/profiles/conhecimento-tributario.md",
    "preaprovar-embargos-execucao-fiscal": "references/profiles/embargos-execucao-fiscal.md",
    "preaprovar-execucoes-fiscais": "references/profiles/execucao-fiscal.md",
    "preaprovar-prescricao-intercorrente": "references/overlays/prescricao-intercorrente.md",
    "preaprovar-processos-administrativos": "references/profiles/processos-administrativos.md",
    "preaprovar-restituicoes-tributarias": "references/profiles/restituicoes-judiciais.md",
}
ORCHESTRATION_ALIAS = "rodar-e-preaprovar-indexacao"
CONCLUSION_SKILL = "concluir-indexacoes-aprovadas"
REAPER_RECONCILIATION_SKILL = "reconciliar-orquestracao-pos-reaper"
EXPLICIT_SKILLS = set(PROFILE_ALIASES) | {
    ORCHESTRATION_ALIAS,
    CONCLUSION_SKILL,
    REAPER_RECONCILIATION_SKILL,
}
EXTRACTION_EVAL_IDS = {
    "runtime-capability-missing",
    "source-pdf-drift",
    "native-repair-eligible",
    "retry-before-mutation",
    "failure-after-mutation",
    "stale-head-release",
    "backlog-without-proof",
    "legal-classification-handoff",
    "ambiguous-canary",
}
EXTRACTION_CONTRACT_FRAGMENTS = {
    "0141_extraction_treatment_budget_data",
    "0142_extraction_gate_fencing_ops",
    "BLOQUEADO_POR_CAPACIDADE",
    "page.native_text.repair/v1",
    "mutation_started_at",
    "retry_of_run_id",
    "extraction_treatment_mutations",
    "begin_extraction_indexing",
    "OCR/Vision exige autorização e orçamento separados",
    "Nunca escolha um job produtivo por posição na fila",
}
CONCLUSION_EVAL_IDS = {
    "approved-exact-scope",
    "approval-missing",
    "active-lease",
    "dry-run-mismatch",
    "postgres-timeout",
    "approval-consumed",
    "cli-ok-without-readback",
    "reindex-only-forbidden",
    "standalone-intent-required",
    "budget-enforcement-missing",
    "approved-snapshot-toctou",
    "runtime-proof-insufficient",
    "persistence-manifest-required",
    "run-only-snapshot-toctou",
    "manifest-payload-drift",
    "effect-plan-before-external-effects",
    "manifest-self-describing-fields",
}
CONCLUSION_CONTRACT_FRAGMENTS = {
    "queue=indexing",
    "status=awaiting_approval",
    "approved_at IS NOT NULL",
    "--dry-run --run-approved --concurrency 1",
    "--job-id",
    "--reindex-only",
    "57014",
    "orchestration-intent/v1",
    "persistence-manifest/v1",
    "conclusion-effect-plan/v1",
    "identity_fields",
    "material_fields",
    "terminal_ops_expectation",
    "janela TOCTOU",
    "2.500 folhas",
    "checkout local",
    "Não acrescente flags `--max-*`",
    "digest canônico",
    "hashes dos valores materiais",
    "UNKNOWN_REQUIRES_READBACK",
    "CANONICALLY_PERSISTED",
}
ORCHESTRATION_CONTRACT_FRAGMENTS = {
    "orchestration-intent/v1",
    "expected_pages",
    "large_scope_authorized",
    "local-env",
    "uv run",
    ".env",
    "2.500 folhas",
    "conclude_human_approved",
    "PIPELINE_ENABLE_MAPEAMENTO=false",
    "--run-only",
    "oli-indexer-patch",
}
DOCUMENTARY_BOUNDARY_EVAL_IDS = {
    "pje-six-parts-physical-order",
    "internal-tcu-reference",
    "same-subato-artificial-fragments",
    "same-cnj-distinct-attachments",
}
DOCUMENTARY_BOUNDARY_CONTRACT_FRAGMENTS = {
    "carimbo_subato",
    "ordem física das folhas",
    "mesmo CNJ",
    "referência interna",
    "parte_N",
}
EDITORIAL_QUALITY_EVAL_IDS = {
    "report-unaccented-before-save",
    "persisted-analysis-human-label",
    "technical-literal-preserved",
    "conclusion-accent-loss-readback",
}
EDITORIAL_QUALITY_CONTRACT_FRAGMENTS = {
    "JSON UTF-8",
    "julgamento_argumentos",
    "indexacao.analysis.replace",
    "persistence-manifest/v1",
    "Perda de acentos",
}
REAPER_RECONCILIATION_EVAL_IDS = {
    "reaper-not-confirmed",
    "started-effect-unknown",
    "reserved-effect-released",
    "accounting-drift",
    "retry-after-reconcile",
    "reaper-preview-drift",
}
REAPER_RECONCILIATION_CONTRACT_FRAGMENTS = {
    "ZOMBIE_NO_HEARTBEAT",
    "REAPED_AFTER_DISPATCH",
    "REAPED_BEFORE_DISPATCH",
    "post-reaper-reconciliation/v1",
    "target=UNKNOWN",
    "run=BLOCKED",
    "unknown_cost_usd",
    "service_role",
    "scripts/ops/orchestrationctl.py reconcile-reaper",
    "--expected-request-sha256",
}
PORTABILITY_EVAL_IDS = {
    "local-worker-env",
    "dirty-checkout",
    "no-worker-deploy",
    "service-deploy-boundary",
    "large-scope-gate",
    "no-arbitrary-budgets",
}
PORTABILITY_CONTRACT_FRAGMENTS = {
    "checkout local",
    "oli-indexador",
    "uv run",
    ".env",
    "git pull --ff-only",
    "Não subir Docker local",
    "Portainer",
    "oli-indexer-patch",
    "2.500 folhas",
}
EXPECTED_SKILLS = AUTO_SKILLS | EXPLICIT_SKILLS
NAME_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
SEMVER_RE = re.compile(
    r"^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)"
    r"(?:-[0-9A-Za-z.-]+)?(?:\+[0-9A-Za-z.-]+)?$"
)
MARKDOWN_LINK_RE = re.compile(r"\[[^\]]+\]\(([^)]+\.md(?:#[^)]+)?)\)")


class ValidationError(Exception):
    pass


def _unquote(value: str) -> str:
    value = value.strip()
    if len(value) >= 2 and value[0] == value[-1] and value[0] in {'"', "'"}:
        return value[1:-1]
    return value


def _frontmatter(path: Path) -> tuple[dict[str, str], str]:
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines()
    if not lines or lines[0] != "---":
        raise ValidationError(f"{path}: frontmatter must start on line 1")
    try:
        end = lines.index("---", 1)
    except ValueError as exc:
        raise ValidationError(f"{path}: frontmatter is not closed") from exc

    metadata: dict[str, str] = {}
    for line in lines[1:end]:
        if not line.strip() or line.startswith((" ", "\t")):
            continue
        if ":" not in line:
            raise ValidationError(f"{path}: invalid frontmatter line: {line!r}")
        key, value = line.split(":", 1)
        metadata[key.strip()] = _unquote(value)
    return metadata, text


def _validate_manifest() -> None:
    path = ROOT / ".codex-plugin" / "plugin.json"
    manifest = json.loads(path.read_text(encoding="utf-8"))
    if manifest.get("name") != "oli-indexer-ops":
        raise ValidationError(f"{path}: unexpected plugin name")
    version = str(manifest.get("version", ""))
    if not SEMVER_RE.fullmatch(version):
        raise ValidationError(f"{path}: invalid semantic version {version!r}")
    if manifest.get("skills") != "./skills/":
        raise ValidationError(f"{path}: skills must point to ./skills/")
    digest_tool = ROOT / "scripts" / "plugin_digest.py"
    if not digest_tool.is_file():
        raise ValidationError(f"{digest_tool}: canonical plugin digest tool is required")
    if "plugin-package-digest/v1" not in digest_tool.read_text(encoding="utf-8"):
        raise ValidationError(f"{digest_tool}: canonical digest contract is missing")
    for required in (
        ROOT / ".gitattributes",
        ROOT / "assets" / "host-config.example.json",
        ROOT / "scripts" / "oli_ops.py",
    ):
        if not required.is_file():
            raise ValidationError(f"{required}: portable runtime asset is required")


def _validate_links(path: Path, text: str) -> None:
    for raw_target in MARKDOWN_LINK_RE.findall(text):
        target = raw_target.split("#", 1)[0]
        if target.startswith(("http://", "https://")):
            continue
        resolved = (path.parent / target).resolve()
        if not resolved.is_file():
            raise ValidationError(f"{path}: broken markdown link {raw_target!r}")


def _quoted_yaml_value(text: str, key: str) -> str | None:
    match = re.search(rf'^\s*{re.escape(key)}:\s*["\'](.*)["\']\s*$', text, re.MULTILINE)
    return match.group(1) if match else None


def _allow_implicit_invocation(text: str) -> bool:
    match = re.search(
        r"^\s*allow_implicit_invocation:\s*(true|false)\s*$",
        text,
        re.MULTILINE | re.IGNORECASE,
    )
    return match is None or match.group(1).lower() == "true"


def _validate_skill(skill_dir: Path) -> int:
    skill_file = skill_dir / "SKILL.md"
    metadata, text = _frontmatter(skill_file)
    name = metadata.get("name", "")
    description = metadata.get("description", "")

    if name != skill_dir.name or not NAME_RE.fullmatch(name):
        raise ValidationError(f"{skill_file}: name must match folder")
    if not description:
        raise ValidationError(f"{skill_file}: description is required")
    if len(description) > 360:
        raise ValidationError(
            f"{skill_file}: description has {len(description)} characters; keep discovery concise"
        )
    if "[TODO:" in text:
        raise ValidationError(f"{skill_file}: unfinished TODO placeholder")
    _validate_links(skill_file, text)

    metadata_file = skill_dir / "agents" / "openai.yaml"
    metadata_text = metadata_file.read_text(encoding="utf-8")
    short_description = _quoted_yaml_value(metadata_text, "short_description")
    default_prompt = _quoted_yaml_value(metadata_text, "default_prompt")
    if short_description is None or not 25 <= len(short_description) <= 64:
        raise ValidationError(
            f"{metadata_file}: short_description must contain 25 to 64 characters"
        )
    if default_prompt is None or f"${name}" not in default_prompt:
        raise ValidationError(f"{metadata_file}: default_prompt must mention ${name}")

    allow_implicit = _allow_implicit_invocation(metadata_text)
    if name in EXPLICIT_SKILLS:
        if allow_implicit:
            raise ValidationError(
                f"{metadata_file}: explicit skill must disable implicit invocation"
            )
    elif not allow_implicit:
        raise ValidationError(f"{metadata_file}: automatic skill cannot be explicit-only")

    if name in PROFILE_ALIASES:
        if "../preaprovar-indexacoes/SKILL.md" not in text:
            raise ValidationError(f"{skill_file}: alias must route to preaprovar-indexacoes")
        if PROFILE_ALIASES[name] not in text:
            raise ValidationError(f"{skill_file}: alias must route to {PROFILE_ALIASES[name]}")
        allowed_files = {skill_file.resolve(), metadata_file.resolve()}
        unexpected = [
            path
            for path in skill_dir.rglob("*")
            if path.is_file() and path.resolve() not in allowed_files
        ]
        if unexpected:
            raise ValidationError(f"{skill_dir}: alias contains duplicated resources {unexpected}")
    elif name == ORCHESTRATION_ALIAS:
        if "../orquestrar-indexacoes/SKILL.md" not in text:
            raise ValidationError(f"{skill_file}: alias must route to orquestrar-indexacoes")
        allowed_files = {skill_file.resolve(), metadata_file.resolve()}
        unexpected = [
            path
            for path in skill_dir.rglob("*")
            if path.is_file() and path.resolve() not in allowed_files
        ]
        if unexpected:
            raise ValidationError(f"{skill_dir}: alias contains duplicated resources {unexpected}")
    elif name == CONCLUSION_SKILL:
        if "references/protocolo.md" not in text:
            raise ValidationError(f"{skill_file}: conclusion skill must route to its protocol")
    elif name == REAPER_RECONCILIATION_SKILL:
        if "references/protocolo.md" not in text:
            raise ValidationError(f"{skill_file}: post-reaper skill must route to its protocol")

    for markdown in skill_dir.rglob("*.md"):
        markdown_text = markdown.read_text(encoding="utf-8")
        if "[TODO:" in markdown_text:
            raise ValidationError(f"{markdown}: unfinished TODO placeholder")
        _validate_links(markdown, markdown_text)
    return len(description)


def _validate_discovery_cases() -> int:
    path = ROOT / "evals" / "discovery.jsonl"
    ids: set[str] = set()
    automatic_validation_coverage: set[str] = set()
    alias_validation_coverage: set[str] = set()
    count = 0
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        try:
            case = json.loads(line)
        except json.JSONDecodeError as exc:
            raise ValidationError(f"{path}:{line_number}: invalid JSON") from exc
        case_id = case.get("id")
        if not isinstance(case_id, str) or not case_id or case_id in ids:
            raise ValidationError(f"{path}:{line_number}: missing or duplicate id")
        ids.add(case_id)
        expected = case.get("expected_skill")
        if expected is not None and expected not in EXPECTED_SKILLS:
            raise ValidationError(f"{path}:{line_number}: unknown expected skill {expected!r}")
        mode = case.get("mode", "implicit")
        if mode not in {"implicit", "explicit"}:
            raise ValidationError(f"{path}:{line_number}: invalid mode {mode!r}")
        if expected in EXPLICIT_SKILLS:
            if mode != "explicit" or f"${expected}" not in str(case.get("prompt", "")):
                raise ValidationError(
                    f"{path}:{line_number}: explicit skill cases must invoke ${expected}"
                )
            alias_validation_coverage.add(expected)
        elif mode == "explicit":
            raise ValidationError(
                f"{path}:{line_number}: explicit mode requires an explicit-only skill"
            )
        for forbidden in case.get("must_not_select", []):
            if forbidden not in EXPECTED_SKILLS:
                raise ValidationError(
                    f"{path}:{line_number}: unknown forbidden skill {forbidden!r}"
                )
        if case.get("split") == "validation" and expected in AUTO_SKILLS and mode == "implicit":
            automatic_validation_coverage.add(expected)
        count += 1

    missing_auto = AUTO_SKILLS - automatic_validation_coverage
    if missing_auto:
        raise ValidationError(f"{path}: validation split misses {sorted(missing_auto)}")
    missing_aliases = EXPLICIT_SKILLS - alias_validation_coverage
    if missing_aliases:
        raise ValidationError(f"{path}: explicit skill cases miss {sorted(missing_aliases)}")
    return count


def _validate_behavior_cases(filename: str, expected_ids: set[str], label: str) -> int:
    path = ROOT / "evals" / filename
    ids: set[str] = set()
    count = 0
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        try:
            case = json.loads(line)
        except json.JSONDecodeError as exc:
            raise ValidationError(f"{path}:{line_number}: invalid JSON") from exc
        case_id = case.get("id")
        if not isinstance(case_id, str) or not case_id or case_id in ids:
            raise ValidationError(f"{path}:{line_number}: missing or duplicate id")
        ids.add(case_id)
        for key in ("prompt", "expected_outcome"):
            if not isinstance(case.get(key), str) or not case[key].strip():
                raise ValidationError(f"{path}:{line_number}: {key} is required")
        for key in ("must_include", "must_not_do"):
            values = case.get(key)
            if (
                not isinstance(values, list)
                or not values
                or not all(isinstance(value, str) and value.strip() for value in values)
            ):
                raise ValidationError(f"{path}:{line_number}: {key} must be non-empty strings")
        count += 1

    if ids != expected_ids:
        raise ValidationError(
            f"{path}: expected {label} cases {sorted(expected_ids)}, got {sorted(ids)}"
        )
    return count


def _validate_extraction_contract() -> int:
    skill = SKILLS / "preaprovar-extracoes" / "SKILL.md"
    protocol = skill.parent / "references" / "protocolo.md"
    contract_text = skill.read_text(encoding="utf-8") + "\n" + protocol.read_text(encoding="utf-8")
    missing_fragments = sorted(
        fragment for fragment in EXTRACTION_CONTRACT_FRAGMENTS if fragment not in contract_text
    )
    if missing_fragments:
        raise ValidationError(f"{skill}: extraction safety contract misses {missing_fragments}")

    return _validate_behavior_cases("extraction_gate.jsonl", EXTRACTION_EVAL_IDS, "extraction")


def _validate_conclusion_contract() -> int:
    skill = SKILLS / CONCLUSION_SKILL / "SKILL.md"
    protocol = skill.parent / "references" / "protocolo.md"
    contract_text = skill.read_text(encoding="utf-8") + "\n" + protocol.read_text(encoding="utf-8")
    missing_fragments = sorted(
        fragment for fragment in CONCLUSION_CONTRACT_FRAGMENTS if fragment not in contract_text
    )
    if missing_fragments:
        raise ValidationError(f"{skill}: conclusion safety contract misses {missing_fragments}")

    return _validate_behavior_cases("conclusion_gate.jsonl", CONCLUSION_EVAL_IDS, "conclusion")


def _validate_orchestration_contract() -> None:
    skill_dir = SKILLS / "orquestrar-indexacoes"
    paths = [
        skill_dir / "SKILL.md",
        skill_dir / "references" / "intent.md",
        skill_dir / "references" / "workflow.md",
        skill_dir / "references" / "runtime-portatil.md",
    ]
    contract_text = "\n".join(path.read_text(encoding="utf-8") for path in paths)
    missing_fragments = sorted(
        fragment for fragment in ORCHESTRATION_CONTRACT_FRAGMENTS if fragment not in contract_text
    )
    if missing_fragments:
        raise ValidationError(
            f"{skill_dir}: orchestration safety contract misses {missing_fragments}"
        )


def _validate_portability_contract() -> int:
    paths = [
        SKILLS / "orquestrar-indexacoes" / "SKILL.md",
        SKILLS / "orquestrar-indexacoes" / "references" / "runtime-portatil.md",
        SKILLS / "orquestrar-indexacoes" / "references" / "workflow.md",
        SKILLS / "orquestrar-indexacoes" / "references" / "intent.md",
    ]
    contract_text = "\n".join(path.read_text(encoding="utf-8") for path in paths)
    missing_fragments = sorted(
        fragment for fragment in PORTABILITY_CONTRACT_FRAGMENTS if fragment not in contract_text
    )
    if missing_fragments:
        raise ValidationError(f"local runtime contract misses {missing_fragments}")
    if "/private/tmp" in contract_text:
        raise ValidationError("portable runtime contract contains a macOS-only path")

    return _validate_behavior_cases(
        "runtime_portability.jsonl", PORTABILITY_EVAL_IDS, "local runtime"
    )


def _validate_documentary_boundary_contract() -> int:
    paths = [
        SKILLS / "preaprovar-indexacoes" / "references" / "protocolo.md",
        SKILLS / "preaprovar-indexacoes" / "references" / "profiles" / "agravo-instrumento.md",
        SKILLS / "preaprovar-insumos-indexacao" / "references" / "protocolo.md",
    ]
    contract_text = "\n".join(path.read_text(encoding="utf-8") for path in paths)
    missing_fragments = sorted(
        fragment
        for fragment in DOCUMENTARY_BOUNDARY_CONTRACT_FRAGMENTS
        if fragment not in contract_text
    )
    if missing_fragments:
        raise ValidationError(f"documentary boundary contract misses {missing_fragments}")

    return _validate_behavior_cases(
        "documentary_boundaries.jsonl",
        DOCUMENTARY_BOUNDARY_EVAL_IDS,
        "documentary boundary",
    )


def _validate_editorial_quality_contract() -> int:
    paths = [
        SKILLS / "preaprovar-indexacoes" / "references" / "protocolo.md",
        SKILLS / CONCLUSION_SKILL / "references" / "protocolo.md",
    ]
    contract_text = "\n".join(path.read_text(encoding="utf-8") for path in paths)
    missing_fragments = sorted(
        fragment
        for fragment in EDITORIAL_QUALITY_CONTRACT_FRAGMENTS
        if fragment not in contract_text
    )
    if missing_fragments:
        raise ValidationError(f"editorial quality contract misses {missing_fragments}")

    return _validate_behavior_cases(
        "editorial_quality.jsonl", EDITORIAL_QUALITY_EVAL_IDS, "editorial quality"
    )


def _validate_reaper_reconciliation_contract() -> int:
    skill = SKILLS / REAPER_RECONCILIATION_SKILL / "SKILL.md"
    protocol = skill.parent / "references" / "protocolo.md"
    contract_text = skill.read_text(encoding="utf-8") + "\n" + protocol.read_text(encoding="utf-8")
    missing_fragments = sorted(
        fragment
        for fragment in REAPER_RECONCILIATION_CONTRACT_FRAGMENTS
        if fragment not in contract_text
    )
    if missing_fragments:
        raise ValidationError(f"{skill}: post-reaper contract misses {missing_fragments}")

    return _validate_behavior_cases(
        "reaper_reconciliation.jsonl",
        REAPER_RECONCILIATION_EVAL_IDS,
        "post-reaper",
    )


def _validate_hygiene() -> None:
    ignored_roots = {".git"}
    unwanted: list[str] = []
    for path in ROOT.rglob("*"):
        if any(part in ignored_roots for part in path.parts):
            continue
        if path.name == ".pytest_cache" or path.name == "__pycache__" or path.suffix == ".pyc":
            unwanted.append(str(path.relative_to(ROOT)))
    if unwanted:
        raise ValidationError(f"generated cache artifacts present: {unwanted[:8]}")


def main() -> int:
    try:
        _validate_manifest()
        actual_skills = {path.parent.name for path in SKILLS.glob("*/SKILL.md")}
        if actual_skills != EXPECTED_SKILLS:
            raise ValidationError(
                f"public skill set differs: expected={sorted(EXPECTED_SKILLS)} "
                f"actual={sorted(actual_skills)}"
            )
        description_lengths = {
            name: _validate_skill(SKILLS / name) for name in sorted(EXPECTED_SKILLS)
        }
        description_chars = sum(description_lengths[name] for name in AUTO_SKILLS)
        case_count = _validate_discovery_cases()
        extraction_case_count = _validate_extraction_contract()
        conclusion_case_count = _validate_conclusion_contract()
        _validate_orchestration_contract()
        portability_case_count = _validate_portability_contract()
        documentary_boundary_case_count = _validate_documentary_boundary_contract()
        editorial_quality_case_count = _validate_editorial_quality_contract()
        reaper_reconciliation_case_count = _validate_reaper_reconciliation_contract()
        _validate_hygiene()
    except (OSError, ValueError, ValidationError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    print(
        f"OK: {len(AUTO_SKILLS)} automatic skills + "
        f"{len(EXPLICIT_SKILLS)} explicit skills, "
        f"{description_chars} automatic description characters, "
        f"{case_count} discovery cases, "
        f"{extraction_case_count} extraction behavior cases, "
        f"{conclusion_case_count} conclusion behavior cases, "
        f"{documentary_boundary_case_count} documentary boundary cases, "
        f"{editorial_quality_case_count} editorial quality cases, "
        f"{reaper_reconciliation_case_count} post-reaper behavior cases"
        f", {portability_case_count} runtime portability cases"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
