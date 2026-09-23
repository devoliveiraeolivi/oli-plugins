from __future__ import annotations

import importlib.util
from pathlib import Path

SCRIPT = (
    Path(__file__).resolve().parents[1]
    / "skills"
    / "preaprovar-indexacoes"
    / "scripts"
    / "check_prescricao_intercorrente.py"
)
SPEC = importlib.util.spec_from_file_location("check_prescricao_intercorrente", SCRIPT)
assert SPEC is not None and SPEC.loader is not None
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def _legacy(**overrides: object) -> dict[str, object]:
    result: dict[str, object] = {
        "Indicioprescricao__c": True,
        "DataInicial__c": "2017-03-09",
        "DataFinal__c": "2023-03-09",
        "InicioPrescricaoIntercorrente__c": "2017-03-09",
        "ConfiabilidadeDataFinal__c": "MÉDIA",
        "ClassificacaoProcessual__c": "Prescrição - Possível",
        "tag_prescricao_consumada": True,
    }
    result.update(overrides)
    return result


def test_accepts_consistent_legacy_output() -> None:
    result = MODULE.analyze(_legacy(), reference_date="2026-07-29")

    assert result["gate_status"] == "no_structural_issue"
    assert result["issues"] == []


def test_detects_consumed_without_final_date_without_choosing_patch_direction() -> None:
    result = MODULE.analyze(
        _legacy(
            DataInicial__c=None,
            DataFinal__c=None,
            InicioPrescricaoIntercorrente__c=None,
            ClassificacaoProcessual__c="Prescrição - Remota",
            ConfiabilidadeDataFinal__c="MUITO BAIXA",
        ),
        reference_date="2026-07-29",
    )

    assert [issue["code"] for issue in result["issues"]] == [
        "consumed_requires_final_date"
    ]
    assert result["automatic_patch"] is False


def test_detects_non_prescribed_result_that_asserts_indication_and_consumption() -> None:
    result = MODULE.analyze(
        _legacy(ClassificacaoProcessual__c="Não Prescrito - Parcelamento/Transação"),
        reference_date="2026-07-29",
    )

    assert {issue["code"] for issue in result["issues"]} == {
        "classification_forbids_indication",
        "classification_forbids_consumed",
    }


def test_supports_internal_vertical_inside_job_envelope() -> None:
    result = MODULE.analyze(
        {
            "llm_results": {
                "prescricao_intercorrente": {
                    "data_referencia": "2026-07-29",
                    "resultado_probabilistico": {
                        "indicio_prescricao": False,
                        "classificacao": "Não Classificado - Ausência de Informação",
                        "confiabilidade": "INDETERMINADA",
                        "prescricao_consumada_na_tese": False,
                    },
                    "marco_principal": {"data_inicial": None, "data_final": None},
                }
            }
        }
    )

    assert result["payload_format"] == "internal"
    assert result["payload_path"] == "llm_results.prescricao_intercorrente"
    assert result["gate_status"] == "no_structural_issue"


def test_missing_or_empty_legacy_vertical_is_not_applicable() -> None:
    for document in ({}, {"llm_results": {}}, {"llm_results": {"prescricao_intercorrente": {}}}):
        result = MODULE.analyze(document)

        assert result["applicable"] is False
        assert result["gate_status"] == "not_applicable"
        assert result["issues"] == []
