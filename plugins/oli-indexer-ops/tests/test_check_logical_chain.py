from __future__ import annotations

import importlib.util
from pathlib import Path

SCRIPT = (
    Path(__file__).resolve().parents[1]
    / "skills"
    / "preaprovar-indexacoes"
    / "scripts"
    / "check_logical_chain.py"
)
SPEC = importlib.util.spec_from_file_location("check_logical_chain", SCRIPT)
assert SPEC is not None and SPEC.loader is not None
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def _row(
    *,
    external_id: str,
    page: int,
    date: str,
    category: str,
    title: str,
    subclass: str = "",
    process_reference: str | None = None,
) -> dict[str, object]:
    return {
        "id_externo": external_id,
        "job_id": "00000000-0000-0000-0000-000000000001",
        "folha_inicio": page,
        "folha_fim": page,
        "data": date,
        "categoria": category,
        "classe": "Movimentação" if category == "Cartório" else "Julgamento",
        "subclasse": subclass,
        "titulo": title,
        "resumo": title,
        "numero_processo_ref": process_reference,
    }


def test_multiple_initial_petitions_break_opening_sequence() -> None:
    result = MODULE.analyze(
        [
            _row(
                external_id="initial-native",
                page=4,
                date="2023-01-01",
                category="Parte",
                title="Petição Inicial",
                subclass="Petição Inicial",
                process_reference="5023707-17.2023.4.03.6100",
            ),
            _row(
                external_id="initial-copied",
                page=1128,
                date="2023-02-01",
                category="Parte",
                title="Petição Inicial trasladada",
                subclass="Petição Inicial",
                process_reference="48640.200225/2023-50",
            ),
        ]
    )

    assert result["gaps"][0]["code"] == "PETICAO_INICIAL_DUPLICADA"
    assert result["gaps"][0]["severity"] == "blocker"
    assert result["gaps"][0]["candidates"][1]["pages"] == [1128, 1128]
    assert result["gaps"][0]["candidates"][1]["process_reference"] == "48640.200225/2023-50"
    assert result["blockers"] == 1


def test_single_initial_petition_preserves_opening_sequence() -> None:
    result = MODULE.analyze(
        [
            _row(
                external_id="initial-native",
                page=4,
                date="2023-01-01",
                category="Parte",
                title="Petição Inicial",
                subclass="Petição Inicial",
            )
        ]
    )

    assert result["gaps"] == []
    assert result["blockers"] == 0


def test_terminal_remittance_is_pending_not_gap() -> None:
    result = MODULE.analyze(
        [
            _row(
                external_id="remessa",
                page=10,
                date="2026-01-01",
                category="Cartório",
                title="Remessa dos Autos ao Tribunal",
                subclass="Remessa a Instância Superior",
            )
        ]
    )

    assert result["branches"][0]["status"] == "open"
    assert result["gaps"] == []
    assert result["blockers"] == 0


def test_return_without_intermediate_outcome_is_gap() -> None:
    result = MODULE.analyze(
        [
            _row(
                external_id="remessa",
                page=10,
                date="2026-01-01",
                category="Cartório",
                title="Remessa dos Autos ao Tribunal",
                subclass="Remessa a Instância Superior",
            ),
            _row(
                external_id="retorno",
                page=20,
                date="2026-02-01",
                category="Cartório",
                title="Recebimento dos Autos do TRF",
            ),
        ]
    )

    assert result["branches"][0]["status"] == "gap"
    assert result["gaps"][0]["code"] == "MISSING_EXTERNAL_JUDICIAL_OUTCOME"
    assert result["blockers"] == 1


def test_outcome_before_return_closes_branch() -> None:
    result = MODULE.analyze(
        [
            _row(
                external_id="remessa",
                page=10,
                date="2026-01-01",
                category="Cartório",
                title="Remessa dos Autos ao Tribunal",
                subclass="Remessa a Instância Superior",
            ),
            _row(
                external_id="acordao",
                page=15,
                date="2026-01-20",
                category="Julgador",
                title="Acórdão de Julgamento da Apelação",
            ),
            _row(
                external_id="retorno",
                page=20,
                date="2026-02-01",
                category="Cartório",
                title="Recebimento dos Autos do TRF",
            ),
        ]
    )

    assert result["branches"][0]["status"] == "closed"
    assert result["gaps"] == []
    assert result["blockers"] == 0
