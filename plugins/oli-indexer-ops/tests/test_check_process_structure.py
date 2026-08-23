from __future__ import annotations

import importlib.util
from pathlib import Path

SCRIPT = (
    Path(__file__).resolve().parents[1]
    / "skills"
    / "preaprovar-indexacoes"
    / "scripts"
    / "check_process_structure.py"
)
SPEC = importlib.util.spec_from_file_location("check_process_structure", SCRIPT)
assert SPEC is not None and SPEC.loader is not None
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)

CURRENT = "00000000-0000-0000-0000-000000000001"
OLD = "00000000-0000-0000-0000-000000000002"


def _row(
    row_id: str,
    *,
    job_id: str = CURRENT,
    start: int | None = 1,
    end: int | None = 1,
    status: str = "pendente",
) -> dict[str, object]:
    return {
        "id": row_id,
        "id_externo": f"ext-{row_id}",
        "job_id": job_id,
        "status_validacao": status,
        "folha_inicio": start,
        "folha_fim": end,
        "titulo": row_id,
    }


def test_clean_process_has_no_blockers() -> None:
    result = MODULE.analyze(
        [_row("a", start=1, end=2), _row("b", start=3, end=4)],
        current_job_id=CURRENT,
        expected_pages=range(1, 5),
    )

    assert result["blockers"] == 0
    assert result["coverage"]["gaps"] == []


def test_foreign_pending_exact_duplicate_is_exposed_and_blocking() -> None:
    result = MODULE.analyze(
        [
            _row("new", start=10, end=20),
            _row("old", job_id=OLD, start=10, end=20),
        ],
        current_job_id=CURRENT,
        expected_pages=range(10, 21),
    )

    codes = {finding["code"] for finding in result["findings"]}
    assert codes == {"FOREIGN_STAGING_ROWS", "EXACT_DUPLICATE_RANGES"}
    assert result["foreign_staging_rows"] == 1
    assert result["exact_duplicate_ranges"][0]["owners"] == [
        f"{CURRENT}:pendente",
        f"{OLD}:pendente",
    ]


def test_partial_overlap_is_blocking() -> None:
    result = MODULE.analyze(
        [_row("a", start=1, end=5), _row("b", start=5, end=8)],
        current_job_id=CURRENT,
        expected_pages=range(1, 9),
    )

    assert result["partial_overlaps"][0]["intersection"] == [5, 5]
    assert {finding["code"] for finding in result["findings"]} == {"PARTIAL_PAGE_OVERLAPS"}


def test_gaps_are_compressed_into_ranges() -> None:
    result = MODULE.analyze(
        [_row("a", start=1, end=2), _row("b", start=6, end=7)],
        current_job_id=CURRENT,
        expected_pages=range(1, 8),
    )

    assert result["coverage"]["gaps"] == [[3, 5]]
    assert {finding["code"] for finding in result["findings"]} == {"PAGE_GAPS"}


def test_concluded_history_contiguous_with_current_is_not_foreign_staging() -> None:
    result = MODULE.analyze(
        [
            _row("old", job_id=OLD, start=1, end=3, status="concluido"),
            _row("new", start=4, end=6),
        ],
        current_job_id=CURRENT,
        expected_pages=range(1, 7),
    )

    assert result["blockers"] == 0
    assert result["foreign_staging_rows"] == 0


def test_current_non_visible_and_invalid_ranges_are_blocking() -> None:
    result = MODULE.analyze(
        [
            _row("indexado", status="indexado"),
            _row("invalid", start=8, end=7),
        ],
        current_job_id=CURRENT,
        expected_pages=range(1, 9),
    )

    codes = {finding["code"] for finding in result["findings"]}
    assert "CURRENT_JOB_NON_VISIBLE_ROWS" in codes
    assert "INVALID_PAGE_RANGE" in codes
    assert "PAGE_GAPS" in codes
