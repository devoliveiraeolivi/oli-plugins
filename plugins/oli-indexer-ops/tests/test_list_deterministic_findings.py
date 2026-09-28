import importlib.util
from pathlib import Path

SCRIPT = (
    Path(__file__).parents[1]
    / "skills/preaprovar-indexacoes/scripts/list_deterministic_findings.py"
)
SPEC = importlib.util.spec_from_file_location("list_deterministic_findings", SCRIPT)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def test_consolidate_reune_snapshot_e_achados_atuais():
    job = {
        "id": "job-1",
        "search_key": "cnj",
        "status": "awaiting_approval",
        "output": {
            "achados_deterministicos": {
                "schema_version": "validation-findings/v1",
                "complete": True,
                "itens": [
                    {
                        "validador": "colapso_externo",
                        "severity": "warning",
                        "code": "MAPA_DOCUMENTAL_REF_DIVERGENTE",
                    }
                ],
            }
        },
    }
    actionable = [
        {
            "severidade": "warning",
            "codigo": "campo_obrigatorio_ausente",
            "mensagem": "falta campo",
            "produtor": "eventos.horizontal.canonicalizador",
            "id_andamento": "a1",
            "bloqueia_conclusao": True,
        }
    ]

    result = MODULE.consolidate(job, actionable)

    assert result["snapshot"]["complete"] is True
    assert result["counts"]["total"] == 2
    assert result["counts"]["blockers"] == 1
    assert result["counts"]["por_codigo"] == {
        "MAPA_DOCUMENTAL_REF_DIVERGENTE": 1,
        "campo_obrigatorio_ausente": 1,
    }


def test_consolidate_marca_job_legado_como_snapshot_incompleto():
    result = MODULE.consolidate({"id": "job-legacy", "output": {}}, [])

    assert result["snapshot"]["complete"] is False
    assert result["snapshot"]["reason"] == "validation_findings_snapshot_absent_or_legacy"
