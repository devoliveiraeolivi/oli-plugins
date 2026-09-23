#!/usr/bin/env python3
"""Consultas somente leitura aos bancos OPS e DATA do oli-indexer."""

from __future__ import annotations

import argparse
import asyncio
import hashlib
import json
import sys
from collections import Counter, defaultdict
from datetime import UTC, datetime
from html.parser import HTMLParser
from pathlib import Path
from typing import Any


class _ReportTextParser(HTMLParser):
    """Extrai texto legível do relatório HTML sem dependências externas."""

    _BLOCK_TAGS = {
        "article", "br", "div", "h1", "h2", "h3", "h4", "li", "p", "section", "table",
        "td", "th", "tr", "ul",
    }

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.parts: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag in self._BLOCK_TAGS:
            self.parts.append("\n")

    def handle_endtag(self, tag: str) -> None:
        if tag in self._BLOCK_TAGS:
            self.parts.append("\n")

    def handle_data(self, data: str) -> None:
        value = " ".join(data.split())
        if value:
            self.parts.append(value)

    def text(self) -> str:
        lines = (" ".join(line.split()) for line in "".join(self.parts).splitlines())
        return "\n".join(line for line in lines if line)


def _repo_root(value: str) -> Path:
    root = Path(value).expanduser().resolve()
    if not (root / "src" / "oli_indexer").is_dir():
        raise argparse.ArgumentTypeError(f"não é um checkout do oli-indexador: {root}")
    return root


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", required=True, type=_repo_root)
    sub = parser.add_subparsers(dest="command", required=True)

    pending = sub.add_parser("pending", help="Lista jobs aguardando aprovação")
    pending.add_argument("--area")
    pending.add_argument("--perfil")
    pending.add_argument("--natureza")
    pending.add_argument("--limit", type=int, default=200)
    pending.add_argument(
        "--summary",
        action="store_true",
        help="Resume a fila por perfil/natureza e mostra bloqueios operacionais",
    )

    snapshot = sub.add_parser("snapshot", help="Resumo seguro de um job")
    snapshot.add_argument("--job-id", required=True)

    indexacoes = sub.add_parser("indexacoes", help="Lista indexações do job")
    indexacoes.add_argument("--job-id", required=True)
    indexacoes.add_argument("--from-page", type=int, default=1)
    indexacoes.add_argument("--to-page", type=int)
    indexacoes.add_argument("--include-content", action="store_true")

    folhas = sub.add_parser("folhas", help="Lê envelope/mapeamento por página")
    folhas.add_argument("--cnj", required=True)
    folhas.add_argument("--from-page", type=int, default=1)
    folhas.add_argument("--to-page", type=int, required=True)
    folhas.add_argument("--include-text", action="store_true")

    costs = sub.add_parser("costs", help="Agrega llm_runs do job")
    costs.add_argument("--job-id", required=True)
    costs.add_argument("--since", help="ISO-8601; sem valor lê todo o histórico do job")
    costs.add_argument(
        "--include-errors",
        action="store_true",
        help="Inclui categoria, tentativa e mensagem truncada das chamadas com erro",
    )

    processo = sub.add_parser("processo", help="Lê metadados seguros de DATA.processos")
    processo.add_argument("--cnj", required=True)
    processo.add_argument("--include-analyses", action="store_true")

    prompts = sub.add_parser("prompts", help="Rastreia prompts runtime, git e histórico")
    prompts.add_argument("--area", required=True)
    prompts.add_argument("--perfil", required=True)
    prompts.add_argument("--operation")
    prompts.add_argument("--history", action="store_true")
    prompts.add_argument("--include-template", action="store_true")

    analyses = sub.add_parser("analises", help="Resume análises horizontais e verticais do job")
    analyses.add_argument("--job-id", required=True)
    analyses.add_argument("--from-page", type=int, default=1)
    analyses.add_argument("--to-page", type=int)
    analyses.add_argument("--since", help="ISO-8601 para limitar a telemetria ao run auditado")
    analyses.add_argument("--include-rows", action="store_true")
    analyses.add_argument("--include-content", action="store_true")

    validation = sub.add_parser("validation", help="Lê o relatório de Validation do job")
    validation.add_argument("--job-id", required=True)
    validation.add_argument("--include-html", action="store_true")
    return parser


def _bootstrap(root: Path) -> tuple[Any, Any]:
    sys.path.insert(0, str(root / "src"))
    from dotenv import load_dotenv

    load_dotenv(root / ".env", override=True)
    from oli_indexer.adapters.supabase.client import SupabaseClient
    from oli_indexer.config.settings import Config

    return Config.load_with_vault(), SupabaseClient


def _json(value: Any) -> None:
    print(json.dumps(value, ensure_ascii=False, indent=2, default=str))


def _sha256(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _resolve_git_prompt(root: Path, area: str, perfil: str, operation: str) -> dict[str, Any]:
    base = root / "flows-src" / "prompts"
    candidates = [
        base / area / f"{operation}--{perfil}.md",
        base / area / f"{operation}.md",
        base / "_default" / f"{operation}.md",
    ]
    for path in candidates:
        if path.is_file():
            template = path.read_text(encoding="utf-8")
            return {
                "path": str(path),
                "sha256": _sha256(template),
                "bytes": len(template.encode("utf-8")),
            }
    return {"path": None, "sha256": None, "bytes": 0}


def _prompt_public(row: dict[str, Any], *, include_template: bool) -> dict[str, Any]:
    template = str(row.get("template") or "")
    public = {key: row.get(key) for key in (
        "id", "app", "area", "operacao", "perfil", "model", "temperature",
        "max_input_tokens", "max_output_tokens", "metadata", "change_note",
        "created_at", "updated_at", "created_by", "updated_by",
    )}
    public["sha256"] = _sha256(template)
    public["bytes"] = len(template.encode("utf-8"))
    if include_template:
        public["template"] = template
    return public


def _trace_summary(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    grouped: dict[str, dict[str, Any]] = defaultdict(
        lambda: {
            "calls": 0, "statuses": Counter(), "models": set(), "template_hashes": set(),
            "grafo_ids": set(), "no_ids": set(), "andamento_refs": set(),
        }
    )
    for row in rows:
        item = grouped[str(row.get("operacao") or "<none>")]
        item["calls"] += 1
        item["statuses"][str(row.get("status") or "<none>")] += 1
        for field, target in (
            ("model", "models"), ("template_hash", "template_hashes"),
            ("grafo_id", "grafo_ids"), ("no_id", "no_ids"),
            ("andamento_ref", "andamento_refs"),
        ):
            if row.get(field):
                item[target].add(row[field])
    result = []
    for operation, item in sorted(grouped.items()):
        result.append({
            "operation": operation,
            "calls": item["calls"],
            "statuses": item["statuses"],
            "models": sorted(item["models"]),
            "template_hashes": sorted(item["template_hashes"]),
            "grafo_ids": sorted(item["grafo_ids"]),
            "no_ids": sorted(item["no_ids"]),
            "andamento_refs": sorted(item["andamento_refs"]),
        })
    return result


def _job_public(row: dict[str, Any]) -> dict[str, Any]:
    input_data = row.get("input") if isinstance(row.get("input"), dict) else {}
    output = row.get("output") if isinstance(row.get("output"), dict) else {}
    return {
        "id": row.get("id"),
        "search_key": row.get("search_key"),
        "queue": row.get("queue"),
        "status": row.get("status"),
        "approved_at": row.get("approved_at"),
        "approved_by": row.get("approved_by"),
        "created_at": row.get("created_at"),
        "updated_at": row.get("updated_at"),
        "worker_id": row.get("worker_id"),
        "heartbeat_at": row.get("heartbeat_at"),
        "error_code": row.get("error_code"),
        "validation_published_at": row.get("validation_published_at"),
        "human_edited_at": row.get("human_edited_at"),
        "revisao_secundaria_at": row.get("revisao_secundaria_at"),
        "area": output.get("area") or input_data.get("area"),
        "perfil": output.get("perfil"),
        "natureza": input_data.get("natureza"),
        "classe": input_data.get("classe"),
        "gap": input_data.get("gap"),
        "recalls": input_data.get("recalls"),
        "deletes": input_data.get("deletes"),
        "skip_reviewer": input_data.get("skip_reviewer", False),
        "output_keys": sorted(output),
        "has_report_html": bool(row.get("report_html")),
        "has_llm_results": bool(row.get("llm_results")),
        "review_publish_eligible": bool(
            row.get("queue") == "indexing"
            and row.get("status") == "awaiting_approval"
            and row.get("approved_at") is None
            and row.get("validation_published_at") is not None
        ),
    }


def _pending_summary(rows: list[dict[str, Any]]) -> dict[str, Any]:
    by_profile = Counter(
        (str(row.get("area") or "<null>"), str(row.get("perfil") or "<null>"))
        for row in rows
    )
    by_nature = Counter(
        (
            str(row.get("area") or "<null>"),
            str(row.get("perfil") or "<null>"),
            str(row.get("natureza") or "<null>"),
            str(row.get("classe") or "<null>"),
        )
        for row in rows
    )
    return {
        "by_profile": [
            {"area": area, "perfil": perfil, "count": count}
            for (area, perfil), count in sorted(
                by_profile.items(), key=lambda item: (-item[1], item[0])
            )
        ],
        "by_nature": [
            {
                "area": area,
                "perfil": perfil,
                "natureza": natureza,
                "classe": classe,
                "count": count,
            }
            for (area, perfil, natureza, classe), count in sorted(
                by_nature.items(), key=lambda item: (-item[1], item[0])
            )
        ],
        "operational": {
            "review_publish_eligible": sum(
                bool(row.get("review_publish_eligible")) for row in rows
            ),
            "missing_validation_checkpoint": sum(
                row.get("validation_published_at") is None for row in rows
            ),
            "missing_profile": [
                {"job_id": row.get("id"), "numero_processo": row.get("search_key")}
                for row in rows
                if row.get("perfil") is None
            ],
            "pipeline_error": [
                {
                    "job_id": row.get("id"),
                    "numero_processo": row.get("search_key"),
                    "error_code": row.get("error_code"),
                }
                for row in rows
                if row.get("error_code")
            ],
            "secondary_review_pending": [
                {"job_id": row.get("id"), "numero_processo": row.get("search_key")}
                for row in rows
                if row.get("human_edited_at")
                and not row.get("revisao_secundaria_at")
            ],
        },
    }


def _cost_summary(rows: list[dict[str, Any]]) -> dict[str, Any]:
    grouped: dict[str, dict[str, Any]] = defaultdict(
        lambda: {"calls": 0, "ok": 0, "errors": 0, "input_tokens": 0,
                 "output_tokens": 0, "cached_tokens": 0, "cost_usd": 0.0,
                 "models": set(), "error_categories": Counter()}
    )
    for row in rows:
        item = grouped[str(row.get("operacao") or "<none>")]
        item["calls"] += 1
        item["ok"] += row.get("status") == "ok"
        item["errors"] += row.get("status") != "ok"
        item["input_tokens"] += int(row.get("input_tokens") or 0)
        item["output_tokens"] += int(row.get("output_tokens") or 0)
        item["cached_tokens"] += int(row.get("cached_tokens") or 0)
        item["cost_usd"] += float(row.get("cost_usd") or 0)
        if row.get("model"):
            item["models"].add(row["model"])
        if row.get("status") != "ok":
            item["error_categories"][str(row.get("erro_categoria") or "unknown")] += 1
    by_operation = []
    for operation, item in grouped.items():
        item["cost_usd"] = round(item["cost_usd"], 8)
        item["models"] = sorted(item["models"])
        item["error_categories"] = dict(sorted(item["error_categories"].items()))
        by_operation.append({"operation": operation, **item})
    by_operation.sort(key=lambda item: item["cost_usd"], reverse=True)
    return {
        "calls": len(rows),
        "input_tokens": sum(int(row.get("input_tokens") or 0) for row in rows),
        "output_tokens": sum(int(row.get("output_tokens") or 0) for row in rows),
        "cached_tokens": sum(int(row.get("cached_tokens") or 0) for row in rows),
        "cost_usd": round(sum(float(row.get("cost_usd") or 0) for row in rows), 8),
        "by_operation": by_operation,
    }


async def _llm_rows(client: Any, job_id: str, since: str | None) -> list[dict[str, Any]]:
    params = {
        "contexto->>job_id": f"eq.{job_id}",
        "select": (
            "created_at,operacao,model,status,input_tokens,output_tokens,"
            "cached_tokens,cost_usd,erro_categoria,erro_msg,retry_count"
        ),
        "order": "created_at.asc",
    }
    if since:
        params["created_at"] = f"gte.{since}"
    return await client.get_all("llm_runs", params=params)


async def _trace_rows(client: Any, job_id: str, since: str | None) -> list[dict[str, Any]]:
    params = {
        "contexto->>job_id": f"eq.{job_id}",
        "select": "created_at,operacao,model,status,template_hash,grafo_id,no_id,andamento_ref,params_snapshot",
        "order": "created_at.asc",
    }
    if since:
        params["created_at"] = f"gte.{since}"
    return await client.get_all("llm_runs", params=params)


async def _run(args: argparse.Namespace) -> None:
    config, client_cls = _bootstrap(args.repo)
    observed_at = datetime.now(UTC).isoformat()

    if args.command == "pending":
        async with client_cls(config.supabase_jobs) as ops:
            rows = await ops.get_all(
                "jobs",
                params={"queue": "eq.indexing", "status": "eq.awaiting_approval", "order": "created_at.asc,id.asc"},
            )
        public = [_job_public(row) for row in rows]
        if args.area:
            public = [row for row in public if row.get("area") == args.area]
        if args.perfil:
            public = [row for row in public if row.get("perfil") == args.perfil]
        if args.natureza:
            public = [row for row in public if row.get("natureza") == args.natureza]
        selected = public[: args.limit]
        result = {"observed_at": observed_at, "count": len(selected)}
        if args.summary:
            result["summary"] = _pending_summary(selected)
        else:
            result["jobs"] = selected
        _json(result)
        return

    if args.command == "costs":
        async with client_cls(config.supabase_jobs) as ops:
            rows = await _llm_rows(ops, args.job_id, args.since)
        result = {
            "observed_at": observed_at,
            "job_id": args.job_id,
            "since": args.since,
            **_cost_summary(rows),
        }
        if args.include_errors:
            result["errors"] = [
                {
                    "created_at": row.get("created_at"),
                    "operation": row.get("operacao"),
                    "category": row.get("erro_categoria"),
                    "retry_count": row.get("retry_count"),
                    "message": row.get("erro_msg"),
                }
                for row in rows
                if row.get("status") != "ok"
            ]
        _json(result)
        return

    if args.command == "validation":
        async with client_cls(config.supabase_jobs) as ops:
            jobs = await ops.get("jobs", params={
                "id": f"eq.{args.job_id}",
                "queue": "eq.indexing",
                "select": "id,search_key,status,report_html,updated_at",
            })
        if len(jobs) != 1:
            raise RuntimeError(f"job não resolvido de forma única: {len(jobs)} rows")
        report_html = str(jobs[0].get("report_html") or "")
        parser = _ReportTextParser()
        parser.feed(report_html)
        result = {
            "observed_at": observed_at,
            "job_id": jobs[0].get("id"),
            "cnj": jobs[0].get("search_key"),
            "status": jobs[0].get("status"),
            "updated_at": jobs[0].get("updated_at"),
            "has_report_html": bool(report_html),
            "report_bytes": len(report_html.encode("utf-8")),
            "report_text": parser.text(),
        }
        if args.include_html:
            result["report_html"] = report_html
        _json(result)
        return

    if args.command == "processo":
        fields = [
            "id_processo", "numero_processo", "salesforce_id", "area", "classe", "natureza",
            "tribunal", "tribunal_sistema", "grupo_nome", "cliente_nome",
        ]
        if args.include_analyses:
            fields += [
                "resumo_processual", "julgamento_resumo", "julgamento_argumentos",
                "julgamento_insights", "passivo_tributario",
            ]
        async with client_cls(config.supabase) as data:
            rows = await data.get("processos", params={
                "numero_processo": f"eq.{args.cnj}", "select": ",".join(fields),
            })
            cascata = await data.get_all("cascata_estado", params={
                "numero_processo": f"eq.{args.cnj}",
                "select": "numero_processo,cascata,grupo,input_hash,output_hash,template_hash,eventos_hashes,job_id,processado_em",
                "order": "cascata.asc,grupo.asc",
            })
        _json({"observed_at": observed_at, "cnj": args.cnj, "count": len(rows), "rows": rows, "cascata_estado": cascata})
        return

    if args.command == "prompts":
        if args.history and not args.operation:
            raise ValueError("--history exige --operation para evitar varredura ampla")
        params = {
            "app": "eq.oli-indexer", "area": f"eq.{args.area}", "perfil": f"eq.{args.perfil}",
            "order": "operacao.asc",
        }
        if args.operation:
            params["operacao"] = f"eq.{args.operation}"
        async with client_cls(config.supabase) as data:
            rows = await data.get_all("prompts", params=params)
            histories: dict[str, list[dict[str, Any]]] = {}
            if args.history:
                for row in rows:
                    raw = await data.get_all("prompts_history", params={
                        "prompt_id": f"eq.{row['id']}", "order": "archived_at.desc", "limit": "50",
                    })
                    converted = []
                    for item in raw:
                        snapshot = item.get("snapshot") if isinstance(item.get("snapshot"), dict) else {}
                        converted.append({
                            "id": item.get("id"), "archived_at": item.get("archived_at"),
                            "snapshot": _prompt_public(snapshot, include_template=args.include_template),
                        })
                    histories[str(row["id"])] = converted
        public = []
        for row in rows:
            item = _prompt_public(row, include_template=args.include_template)
            item["git_current"] = _resolve_git_prompt(args.repo, args.area, args.perfil, str(row["operacao"]))
            item["matches_git_current"] = item["sha256"] == item["git_current"]["sha256"]
            if args.history:
                item["history"] = histories.get(str(row["id"]), [])
            public.append(item)
        _json({"observed_at": observed_at, "count": len(public), "prompts": public})
        return

    if args.command == "analises":
        params = {
            "job_id": f"eq.{args.job_id}", "folha_fim": f"gte.{args.from_page}",
            "select": "id_externo,folha_inicio,folha_fim,categoria,classe,subclasse,resultado,resultado_cliente,analise_estruturada",
            "order": "folha_inicio.asc,id_externo.asc",
        }
        if args.to_page is not None:
            params["folha_inicio"] = f"lte.{args.to_page}"
        async with client_cls(config.supabase_jobs) as ops:
            jobs = await ops.get("jobs", params={"id": f"eq.{args.job_id}", "queue": "eq.indexing"})
            traces = await _trace_rows(ops, args.job_id, args.since)
        if len(jobs) != 1:
            raise RuntimeError(f"job não resolvido de forma única: {len(jobs)} rows")
        async with client_cls(config.supabase) as data:
            rows = await data.get_all("indexacoes", params=params)
        classes = Counter()
        versions = Counter()
        with_analysis = 0
        invalid_envelopes = 0
        row_views = []
        for row in rows:
            envelope = row.get("analise_estruturada")
            if isinstance(envelope, dict) and envelope:
                with_analysis += 1
                classes[str(envelope.get("classificacao") or "<none>")] += 1
                versions[str(envelope.get("schema_version") or "<none>")] += 1
            elif envelope not in (None, {}):
                invalid_envelopes += 1
            if args.include_rows or args.include_content:
                view = {key: row.get(key) for key in (
                    "id_externo", "folha_inicio", "folha_fim", "categoria", "classe", "subclasse",
                    "resultado", "resultado_cliente",
                )}
                if isinstance(envelope, dict):
                    view["analise_classificacao"] = envelope.get("classificacao")
                    view["analise_schema_version"] = envelope.get("schema_version")
                if args.include_content:
                    view["analise_estruturada"] = envelope
                row_views.append(view)
        llm_results = jobs[0].get("llm_results") if isinstance(jobs[0].get("llm_results"), dict) else {}
        result = {
            "observed_at": observed_at,
            "job": _job_public(jobs[0]),
            "range": [args.from_page, args.to_page],
            "llm_since": args.since,
            "horizontal": {
                "rows": len(rows), "with_analysis": with_analysis,
                "without_analysis": len(rows) - with_analysis,
                "invalid_envelopes": invalid_envelopes,
                "classifications": classes, "schema_versions": versions,
            },
            "vertical": {"keys": sorted(llm_results), "content": llm_results if args.include_content else None},
            "llm_trace": _trace_summary(traces),
        }
        if args.include_rows or args.include_content:
            result["rows"] = row_views
        _json(result)
        return

    if args.command == "snapshot":
        async with client_cls(config.supabase_jobs) as ops:
            jobs = await ops.get("jobs", params={"id": f"eq.{args.job_id}", "queue": "eq.indexing"})
            costs = await _llm_rows(ops, args.job_id, None)
        if len(jobs) != 1:
            raise RuntimeError(f"job não resolvido de forma única: {len(jobs)} rows")
        cnj = jobs[0].get("search_key")
        async with client_cls(config.supabase) as data:
            indexacoes = await data.get_all(
                "indexacoes",
                params={"job_id": f"eq.{args.job_id}", "select": "folha_inicio,folha_fim,status_validacao", "order": "folha_inicio.asc"},
            )
            folhas = await data.get_all(
                "folhas",
                params={"numero_processo": f"eq.{cnj}", "select": "numero_pagina,mapeamento_relacao", "order": "numero_pagina.asc"},
            )
        versions = Counter()
        relation_pages = 0
        for row in folhas:
            mapping = row.get("mapeamento_relacao")
            versions[str(mapping.get("versao")) if isinstance(mapping, dict) else "none"] += 1
            if isinstance(mapping, dict) and mapping.get("relacoes_processuais"):
                relation_pages += 1
        statuses = Counter(row.get("status_validacao") for row in indexacoes)
        coverage = [
            min((row["folha_inicio"] for row in indexacoes), default=None),
            max((row["folha_fim"] for row in indexacoes), default=None),
        ]
        _json({
            "observed_at": observed_at,
            "job": _job_public(jobs[0]),
            "indexacoes": {"count": len(indexacoes), "status": statuses, "coverage": coverage},
            "folhas": {"count": len(folhas), "mapping_versions": versions, "relation_pages": relation_pages},
            "llm_runs_historical": _cost_summary(costs),
        })
        return

    if args.command == "indexacoes":
        params = {"job_id": f"eq.{args.job_id}", "order": "folha_inicio.asc,id.asc"}
        params["folha_fim"] = f"gte.{args.from_page}"
        if args.to_page is not None:
            params["folha_inicio"] = f"lte.{args.to_page}"
        async with client_cls(config.supabase) as data:
            rows = await data.get_all("indexacoes", params=params)
        fields = ["id_externo", "numero_processo", "job_id", "status_validacao", "folha_inicio", "folha_fim",
                  "data", "categoria", "classe", "subclasse", "funcao_responsavel", "nome_responsavel",
                  "numero_processo_ref", "resultado", "resultado_cliente", "titulo"]
        if args.include_content:
            fields += ["resumo", "analise_estruturada", "evidencias", "integra"]
        _json({"observed_at": observed_at, "count": len(rows), "rows": [{key: row.get(key) for key in fields} for row in rows]})
        return

    if args.command == "folhas":
        if args.to_page < args.from_page:
            raise ValueError("--to-page deve ser >= --from-page")
        select = ("numero_pagina,carimbo_sistema,carimbo_ato,carimbo_subato,carimbo_assinantes,"
                  "carimbo_data,carimbo_tipo,mapeamento_origem,mapeamento_ref,mapeamento_relacao,"
                  "mapeamento_ato,mapeamento_partes")
        if args.include_text:
            select += ",texto,texto_pymupdf"
        async with client_cls(config.supabase) as data:
            rows = await data.get_all("folhas", params={
                "numero_processo": f"eq.{args.cnj}",
                "numero_pagina": f"gte.{args.from_page}",
                "and": f"(numero_pagina.lte.{args.to_page})",
                "select": select,
                "order": "numero_pagina.asc",
            })
        _json({"observed_at": observed_at, "count": len(rows), "rows": rows})


def main() -> int:
    args = _parser().parse_args()
    asyncio.run(_run(args))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
