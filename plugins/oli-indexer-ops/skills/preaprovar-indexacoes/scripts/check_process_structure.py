#!/usr/bin/env python3
"""Audita cobertura e colisões no universo processual de DATA.indexacoes."""

from __future__ import annotations

import argparse
import asyncio
import json
import sys
from collections import Counter, defaultdict
from collections.abc import Iterable
from pathlib import Path
from typing import Any

VISIBLE_STATUSES = frozenset({"pendente", "aprovado", "concluido"})
STAGING_STATUSES = frozenset({"pendente", "aprovado"})


def _status(row: dict[str, Any]) -> str:
    return str(row.get("status_validacao") or "").strip().lower()


def _page(value: Any) -> int | None:
    return value if isinstance(value, int) and not isinstance(value, bool) else None


def _row_ref(row: dict[str, Any]) -> dict[str, Any]:
    return {
        "id": row.get("id"),
        "id_externo": row.get("id_externo"),
        "job_id": row.get("job_id"),
        "status_validacao": row.get("status_validacao"),
        "pages": [row.get("folha_inicio"), row.get("folha_fim")],
    }


def _compress_pages(pages: Iterable[int]) -> list[list[int]]:
    ordered = sorted(set(pages))
    if not ordered:
        return []
    ranges: list[list[int]] = []
    start = previous = ordered[0]
    for page in ordered[1:]:
        if page == previous + 1:
            previous = page
            continue
        ranges.append([start, previous])
        start = previous = page
    ranges.append([start, previous])
    return ranges


def analyze(
    rows: list[dict[str, Any]],
    *,
    current_job_id: str,
    expected_pages: Iterable[int] | None = None,
) -> dict[str, Any]:
    """Compara o job corrente com todas as rows visíveis do processo."""
    visible = [row for row in rows if _status(row) in VISIBLE_STATUSES]
    statuses = Counter(_status(row) or "<none>" for row in rows)
    owners = Counter((str(row.get("job_id") or "<none>"), _status(row) or "<none>") for row in rows)

    foreign_staging = [
        row
        for row in visible
        if row.get("job_id") != current_job_id and _status(row) in STAGING_STATUSES
    ]
    current_non_visible = [
        row
        for row in rows
        if row.get("job_id") == current_job_id and _status(row) not in VISIBLE_STATUSES
    ]

    valid: list[tuple[int, int, dict[str, Any]]] = []
    invalid_ranges: list[dict[str, Any]] = []
    for row in visible:
        start = _page(row.get("folha_inicio"))
        end = _page(row.get("folha_fim"))
        if start is None or end is None or start < 1 or end < start:
            invalid_ranges.append(_row_ref(row))
            continue
        valid.append((start, end, row))

    by_range: dict[tuple[int, int], list[dict[str, Any]]] = defaultdict(list)
    for start, end, row in valid:
        by_range[(start, end)].append(row)
    exact_duplicates = [
        {
            "pages": [start, end],
            "count": len(group),
            "owners": sorted(
                {f"{row.get('job_id') or '<none>'}:{_status(row) or '<none>'}" for row in group}
            ),
            "rows": [_row_ref(row) for row in group],
        }
        for (start, end), group in sorted(by_range.items())
        if len(group) > 1
    ]

    partial_overlaps: list[dict[str, Any]] = []
    active: list[tuple[int, int, dict[str, Any]]] = []
    for start, end, row in sorted(
        valid, key=lambda item: (item[0], item[1], str(item[2].get("id") or ""))
    ):
        active = [item for item in active if item[1] >= start]
        for other_start, other_end, other in active:
            if (other_start, other_end) == (start, end):
                continue
            partial_overlaps.append(
                {
                    "intersection": [start, min(end, other_end)],
                    "left": _row_ref(other),
                    "right": _row_ref(row),
                }
            )
        active.append((start, end, row))

    covered: set[int] = set()
    for start, end, _row in valid:
        covered.update(range(start, end + 1))
    if expected_pages is None:
        expected = set(range(min(covered), max(covered) + 1)) if covered else set()
        expected_source = "indexacoes_bounds_fallback"
    else:
        expected = {page for page in expected_pages if isinstance(page, int) and page >= 1}
        expected_source = "data.folhas"
    gap_ranges = _compress_pages(expected - covered)

    findings: list[dict[str, Any]] = []
    if foreign_staging:
        findings.append(
            {
                "code": "FOREIGN_STAGING_ROWS",
                "count": len(foreign_staging),
                "reason": (
                    "O processo contém rows pendentes/aprovadas de outro job; a fila do "
                    "job não delimita o universo exibido nem auditado."
                ),
                "rows": [_row_ref(row) for row in foreign_staging],
            }
        )
    if current_non_visible:
        findings.append(
            {
                "code": "CURRENT_JOB_NON_VISIBLE_ROWS",
                "count": len(current_non_visible),
                "reason": "O job atual contém staging em estado fora da união visível.",
                "rows": [_row_ref(row) for row in current_non_visible],
            }
        )
    if invalid_ranges:
        findings.append(
            {
                "code": "INVALID_PAGE_RANGE",
                "count": len(invalid_ranges),
                "rows": invalid_ranges,
            }
        )
    if exact_duplicates:
        findings.append(
            {
                "code": "EXACT_DUPLICATE_RANGES",
                "count": len(exact_duplicates),
                "reason": "Duas ou mais rows ocupam exatamente as mesmas folhas.",
                "ranges": exact_duplicates,
            }
        )
    if partial_overlaps:
        findings.append(
            {
                "code": "PARTIAL_PAGE_OVERLAPS",
                "count": len(partial_overlaps),
                "overlaps": partial_overlaps,
            }
        )
    if gap_ranges:
        findings.append(
            {
                "code": "PAGE_GAPS",
                "count": len(gap_ranges),
                "ranges": gap_ranges,
                "expected_source": expected_source,
            }
        )

    return {
        "rows_examined": len(rows),
        "visible_rows": len(visible),
        "current_job_rows": sum(row.get("job_id") == current_job_id for row in rows),
        "foreign_staging_rows": len(foreign_staging),
        "statuses": dict(sorted(statuses.items())),
        "owners": [
            {"job_id": job_id, "status_validacao": status, "count": count}
            for (job_id, status), count in sorted(owners.items())
        ],
        "coverage": {
            "expected_source": expected_source,
            "expected_pages": len(expected),
            "covered_pages": len(expected & covered),
            "gaps": gap_ranges,
            "first_page": min(expected) if expected else None,
            "last_page": max(expected) if expected else None,
        },
        "exact_duplicate_ranges": exact_duplicates,
        "partial_overlaps": partial_overlaps,
        "invalid_ranges": invalid_ranges,
        "findings": findings,
        "blockers": len(findings),
    }


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Confere gaps, overlaps, duplicidades exatas e staging de outros jobs "
            "no universo processual de DATA.indexacoes."
        )
    )
    parser.add_argument("--repo", type=Path, required=True)
    parser.add_argument("--job-id", required=True)
    return parser


async def _main(args: argparse.Namespace) -> int:
    repo = args.repo.resolve()
    sys.path.insert(0, str(repo / "src"))
    from dotenv import load_dotenv

    load_dotenv(repo / ".env", override=True)
    from oli_indexer.adapters.supabase.client import SupabaseClient
    from oli_indexer.config.settings import Config

    config = Config.load_with_vault()
    async with SupabaseClient(config.supabase_jobs) as ops:
        jobs = await ops.get(
            "jobs",
            params={
                "id": f"eq.{args.job_id}",
                "queue": "eq.indexing",
                "select": "id,search_key,output,status,approved_at",
                "limit": "2",
            },
        )
    if len(jobs) != 1:
        raise ValueError(f"job não resolvido de forma única: {len(jobs)}")
    cnj = jobs[0].get("search_key")
    if not isinstance(cnj, str) or not cnj.strip():
        raise ValueError("job sem search_key/CNJ")

    async with SupabaseClient(config.supabase) as data:
        rows = await data.get_all(
            "indexacoes",
            params={
                "numero_processo": f"eq.{cnj}",
                "select": (
                    "id,id_externo,job_id,numero_processo,status_validacao,folha_inicio,folha_fim"
                ),
                "order": "folha_inicio.asc,folha_fim.asc,id.asc",
            },
        )
        folhas = await data.get_all(
            "folhas",
            params={
                "numero_processo": f"eq.{cnj}",
                "select": "numero_pagina",
                "order": "numero_pagina.asc",
            },
        )
    expected_pages = [
        page
        for row in folhas
        if (page := _page(row.get("numero_pagina"))) is not None and page >= 1
    ]
    result = analyze(
        rows,
        current_job_id=args.job_id,
        expected_pages=expected_pages or None,
    )
    result.update(
        {
            "job_id": args.job_id,
            "numero_processo": cnj,
            "profile": (jobs[0].get("output") or {}).get("perfil"),
        }
    )
    print(json.dumps(result, ensure_ascii=False, indent=2, default=str))
    return 2 if result["blockers"] else 0


def main() -> int:
    args = _parser().parse_args()
    try:
        return asyncio.run(_main(args))
    except (OSError, ValueError) as exc:
        raise SystemExit(f"check_process_structure: {exc}") from exc


if __name__ == "__main__":
    raise SystemExit(main())
