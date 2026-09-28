#!/usr/bin/env python3
"""Lista, em uma unica saida, achados deterministicos atuais de um job."""

from __future__ import annotations

import argparse
import asyncio
import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any


def consolidate(
    job: dict[str, Any],
    actionable_findings: list[dict[str, Any]],
) -> dict[str, Any]:
    snapshot = (job.get("output") or {}).get("achados_deterministicos") or {}
    schema = snapshot.get("schema_version")
    snapshot_complete = bool(schema == "validation-findings/v1" and snapshot.get("complete"))
    validation_items = list(snapshot.get("itens") or []) if isinstance(snapshot, dict) else []

    items: list[dict[str, Any]] = []
    for item in validation_items:
        if not isinstance(item, dict):
            continue
        items.append({"fonte": "validation", **item})
    for finding in actionable_findings:
        if not isinstance(finding, dict):
            continue
        items.append(
            {
                "fonte": "achados_indexacao",
                "severity": finding.get("severidade"),
                "code": finding.get("codigo"),
                "message": finding.get("mensagem"),
                "location": None,
                "campo": finding.get("caminho_campo"),
                "valor_atual": None,
                "sugestao": None,
                "andamento_id": finding.get("id_andamento"),
                "validador": finding.get("produtor"),
                "bloqueia_conclusao": bool(finding.get("bloqueia_conclusao")),
                "details": finding.get("detalhes") or {},
            }
        )

    items.sort(
        key=lambda item: (
            {"error": 0, "blocker": 0, "warning": 1, "info": 2, "note": 2}.get(
                str(item.get("severity")), 3
            ),
            str(item.get("fonte") or ""),
            str(item.get("validador") or ""),
            str(item.get("code") or ""),
            str(item.get("location") or ""),
            str(item.get("andamento_id") or ""),
        )
    )
    por_fonte = Counter(str(item.get("fonte") or "<none>") for item in items)
    por_severidade = Counter(str(item.get("severity") or "<none>") for item in items)
    por_codigo = Counter(str(item.get("code") or "<none>") for item in items)
    blockers = sum(
        item.get("bloqueia_conclusao") is True or item.get("severity") in {"error", "blocker"}
        for item in items
    )
    return {
        "job_id": job.get("id"),
        "cnj": job.get("search_key"),
        "status": job.get("status"),
        "validation_published_at": job.get("validation_published_at"),
        "snapshot": {
            "schema_version": schema,
            "complete": snapshot_complete,
            "reason": None
            if snapshot_complete
            else "validation_findings_snapshot_absent_or_legacy",
        },
        "counts": {
            "total": len(items),
            "blockers": blockers,
            "por_fonte": dict(sorted(por_fonte.items())),
            "por_severidade": dict(sorted(por_severidade.items())),
            "por_codigo": dict(sorted(por_codigo.items())),
        },
        "items": items,
    }


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Reune o snapshot final de Validation e os achados acionaveis atuais "
            "do DATA para a pre-aprovacao."
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
                "select": "id,search_key,status,validation_published_at,output",
                "limit": "2",
            },
        )
    if len(jobs) != 1:
        raise ValueError(f"job nao resolvido de forma unica: {len(jobs)}")

    async with SupabaseClient(config.supabase) as data:
        rpc_read = getattr(data, "rpc_read", data.rpc)
        achados = await rpc_read(
            "listar_achados_indexacao_job",
            {"p_id_job_origem": args.job_id},
        )
    if not isinstance(achados, list):
        raise ValueError(f"listar_achados_indexacao_job devolveu {type(achados).__name__}")

    result = consolidate(jobs[0], achados)
    print(json.dumps(result, ensure_ascii=False, indent=2, default=str))
    return 2 if (not result["snapshot"]["complete"] or result["counts"]["blockers"]) else 0


if __name__ == "__main__":
    raise SystemExit(asyncio.run(_main(_parser().parse_args())))
