#!/usr/bin/env python3
"""Detecta quebras intermediárias sem confundir remessa terminal com lacuna."""

from __future__ import annotations

import argparse
import asyncio
import json
import sys
import unicodedata
from pathlib import Path
from typing import Any


def _norm(value: Any) -> str:
    text = unicodedata.normalize("NFKD", str(value or ""))
    return " ".join("".join(char for char in text if not unicodedata.combining(char)).lower().split())


def _haystack(row: dict[str, Any]) -> str:
    return _norm(
        " ".join(
            str(row.get(field) or "")
            for field in ("categoria", "classe", "subclasse", "titulo", "resumo")
        )
    )


def _contains_any(text: str, needles: tuple[str, ...]) -> bool:
    return any(needle in text for needle in needles)


def _kind(row: dict[str, Any]) -> set[str]:
    text = _haystack(row)
    kinds: set[str] = set()
    if _contains_any(
        text,
        (
            "remessa a instancia superior",
            "remessa dos autos ao trf",
            "remessa dos autos ao tribunal",
            "remetidos os autos",
        ),
    ):
        kinds.add("remittance")
    if _contains_any(
        text,
        (
            "devolucao de instancia superior",
            "recebimento dos autos do trf",
            "recebidos os autos",
            "retorno de instancia superior",
        ),
    ):
        kinds.add("return")
    if _contains_any(text, ("transito em julgado", "transitada em julgado")):
        kinds.add("transit")
    if _contains_any(text, ("apelacao", "remessa necessaria", "reexame necessario")):
        kinds.add("appeal")

    judicial = _norm(row.get("categoria")) == "julgador"
    if judicial and _contains_any(
        text,
        (
            "acordao",
            "julgamento",
            "decisao monocratica",
            "admissibilidade",
            "negado seguimento",
            "desistencia do recurso",
            "extincao do recurso",
            "recurso prejudicado",
        ),
    ):
        kinds.add("outcome")
    return kinds


def _event(row: dict[str, Any], kinds: set[str]) -> dict[str, Any]:
    return {
        "id_externo": row.get("id_externo"),
        "job_id": row.get("job_id"),
        "pages": [row.get("folha_inicio"), row.get("folha_fim")],
        "date": row.get("data"),
        "category": row.get("categoria"),
        "class": row.get("classe"),
        "subclass": row.get("subclasse"),
        "title": row.get("titulo"),
        "kinds": sorted(kinds),
    }


def analyze(rows: list[dict[str, Any]]) -> dict[str, Any]:
    ordered = sorted(
        rows,
        key=lambda row: (
            str(row.get("data") or "9999-12-31"),
            int(row.get("folha_inicio") or 0),
            str(row.get("id_externo") or ""),
        ),
    )
    tagged = [(row, _kind(row)) for row in ordered]
    branches: list[dict[str, Any]] = []
    gaps: list[dict[str, Any]] = []

    for index, (row, kinds) in enumerate(tagged):
        if "remittance" not in kinds:
            continue
        later = tagged[index + 1 :]
        closing_index = next(
            (
                offset
                for offset, (_candidate, candidate_kinds) in enumerate(later)
                if candidate_kinds & {"return", "transit"}
            ),
            None,
        )
        bounded = later if closing_index is None else later[: closing_index + 1]
        outcomes = [
            _event(candidate, candidate_kinds)
            for candidate, candidate_kinds in bounded
            if "outcome" in candidate_kinds
        ]
        closing = None if closing_index is None else _event(*later[closing_index])
        branch = {
            "trigger": _event(row, kinds),
            "closing_signal": closing,
            "material_outcomes": outcomes,
            "status": "closed" if outcomes else ("open" if closing is None else "gap"),
        }
        branches.append(branch)
        # Uma remessa terminal sem ato posterior é apenas o estágio atual do processo.
        # O gap só existe quando retorno/trânsito demonstra que a cadeia avançou sem
        # preservar o desfecho intermediário que tornou esse avanço possível.
        if closing is not None and not outcomes:
            gaps.append(
                {
                    "code": "MISSING_EXTERNAL_JUDICIAL_OUTCOME",
                    "severity": "blocker",
                    "trigger": branch["trigger"],
                    "closing_signal": closing,
                    "reason": (
                        "A remessa externa foi seguida de retorno ou trânsito, mas nenhum "
                        "desfecho judicial da instância destinatária foi encontrado entre os atos."
                    ),
                    "required": (
                        "Localizar e incorporar o acórdão, decisão monocrática, admissibilidade, "
                        "desistência ou extinção que encerrou a ramificação antes de aprovar."
                    ),
                }
            )

    transit_positions = [i for i, (_row, kinds) in enumerate(tagged) if "transit" in kinds]
    remittance_positions = [i for i, (_row, kinds) in enumerate(tagged) if "remittance" in kinds]
    if transit_positions and not remittance_positions:
        first_transit = transit_positions[0]
        appeals = [
            (row, kinds)
            for row, kinds in tagged[:first_transit]
            if "appeal" in kinds
        ]
        outcomes = [
            (row, kinds)
            for row, kinds in tagged[:first_transit]
            if "outcome" in kinds
        ]
        if appeals and not outcomes:
            gaps.append(
                {
                    "code": "APPEAL_TO_TRANSIT_WITHOUT_OUTCOME",
                    "severity": "blocker",
                    "trigger": _event(*appeals[-1]),
                    "closing_signal": _event(*tagged[first_transit]),
                    "reason": (
                        "Há recurso seguido de trânsito, mas nenhum ato material encerra a etapa recursal."
                    ),
                    "required": "Localizar o desfecho do recurso antes de aprovar.",
                }
            )

    events = [_event(row, kinds) for row, kinds in tagged if kinds]
    return {
        "rows_examined": len(rows),
        "events": events,
        "branches": branches,
        "gaps": gaps,
        "blockers": sum(gap["severity"] == "blocker" for gap in gaps),
    }


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Confere quebras intermediárias em ramificações externas de DATA.indexacoes; "
            "remessa terminal pendente não é blocker."
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
                "select": "id,search_key,input,output,status,approved_at",
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
                    "id_externo,job_id,numero_processo,folha_inicio,folha_fim,data,categoria,"
                    "classe,subclasse,titulo,resumo,numero_processo_ref,status_validacao"
                ),
                "order": "data.asc,folha_inicio.asc,id_externo.asc",
            },
        )
    result = analyze(rows)
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
        raise SystemExit(f"check_logical_chain: {exc}") from exc


if __name__ == "__main__":
    raise SystemExit(main())
