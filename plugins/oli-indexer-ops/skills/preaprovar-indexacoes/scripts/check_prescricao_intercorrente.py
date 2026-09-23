"""Detect structural inconsistencies in an existing prescription result.

Exit 1 means that human pre-approval is required.  This checker is deliberately
offline and must never be wired into the worker as a fatal subprocess.
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import date
from pathlib import Path
from typing import Any

LEGACY_FIELDS = frozenset(
    {
        "Indicioprescricao__c",
        "DataInicial__c",
        "DataFinal__c",
        "InicioPrescricaoIntercorrente__c",
        "ConfiabilidadeDataFinal__c",
        "ClassificacaoProcessual__c",
        "tag_prescricao_consumada",
    }
)


def _mapping(value: Any) -> dict[str, Any] | None:
    return value if isinstance(value, dict) else None


def _locate_payload(document: dict[str, Any]) -> tuple[dict[str, Any], str] | None:
    if LEGACY_FIELDS & document.keys() or "resultado_probabilistico" in document:
        return document, "root"

    parsed = _mapping(document.get("parsed"))
    if parsed is not None and LEGACY_FIELDS & parsed.keys():
        return parsed, "parsed"

    direct = _mapping(document.get("prescricao_intercorrente"))
    if direct:
        return direct, "prescricao_intercorrente"

    llm_results = _mapping(document.get("llm_results"))
    if llm_results is not None:
        vertical = _mapping(llm_results.get("prescricao_intercorrente"))
        if vertical:
            return vertical, "llm_results.prescricao_intercorrente"
    return None


def _parse_iso_date(value: Any) -> date | None:
    if value is None:
        return None
    if not isinstance(value, str):
        raise ValueError("date must be an ISO string or null")
    return date.fromisoformat(value)


def _normalized_fields(payload: dict[str, Any]) -> tuple[dict[str, Any], str]:
    probabilistic = _mapping(payload.get("resultado_probabilistico"))
    if probabilistic is not None:
        principal = _mapping(payload.get("marco_principal")) or {}
        return (
            {
                "classification": probabilistic.get("classificacao"),
                "indication": probabilistic.get("indicio_prescricao"),
                "confidence": probabilistic.get("confiabilidade"),
                "consumed": probabilistic.get("prescricao_consumada_na_tese"),
                "initial_date": principal.get("data_inicial"),
                "final_date": principal.get("data_final"),
                "legacy_start_date": None,
            },
            "internal",
        )
    return (
        {
            "classification": payload.get("ClassificacaoProcessual__c"),
            "indication": payload.get("Indicioprescricao__c"),
            "confidence": payload.get("ConfiabilidadeDataFinal__c"),
            "consumed": payload.get("tag_prescricao_consumada"),
            "initial_date": payload.get("DataInicial__c"),
            "final_date": payload.get("DataFinal__c"),
            "legacy_start_date": payload.get("InicioPrescricaoIntercorrente__c"),
        },
        "legacy",
    )


def _reference_date(
    document: dict[str, Any], payload: dict[str, Any], explicit: str | None
) -> date | None:
    candidates = (
        explicit,
        payload.get("data_referencia"),
        document.get("reference_date"),
        document.get("timestamp"),
    )
    for candidate in candidates:
        if candidate is not None:
            return _parse_iso_date(candidate)
    return None


def analyze(
    document: dict[str, Any], *, reference_date: str | None = None
) -> dict[str, Any]:
    located = _locate_payload(document)
    if located is None:
        return {
            "schema_version": "prescricao-intercorrente-preapproval-check/v1",
            "applicable": False,
            "automatic_patch": False,
            "gate_status": "not_applicable",
            "issue_count": 0,
            "issues": [],
            "payload_format": None,
            "payload_path": None,
            "reference_date": None,
        }
    payload, payload_path = located
    fields, payload_format = _normalized_fields(payload)
    issues: list[dict[str, Any]] = []

    def add(code: str, field_names: list[str], message: str) -> None:
        issues.append(
            {
                "code": code,
                "fields": field_names,
                "message": message,
                "patch_direction": "source_or_human_decision_required",
            }
        )

    classification = fields["classification"]
    indication = fields["indication"]
    consumed = fields["consumed"]
    confidence = fields["confidence"]

    if indication is not None and not isinstance(indication, bool):
        add("indication_type_invalid", ["indication"], "Indication must be boolean or null.")
    if consumed is not None and not isinstance(consumed, bool):
        add("consumed_type_invalid", ["consumed"], "Consumed tag must be boolean or null.")

    if isinstance(classification, str) and isinstance(indication, bool):
        requires_true = classification.startswith("Prescrição - ") or (
            classification == "Extinto - Prescrição"
        )
        requires_false = classification.startswith(
            ("Não Prescrito - ", "Suspenso - ", "Não Classificado - ")
        )
        if requires_true and indication is not True:
            add(
                "classification_requires_indication",
                ["classification", "indication"],
                "The selected prescription classification requires a true indication.",
            )
        if requires_false and indication is not False:
            add(
                "classification_forbids_indication",
                ["classification", "indication"],
                "The selected non-prescription classification requires a false indication.",
            )
        if requires_false and consumed is True:
            add(
                "classification_forbids_consumed",
                ["classification", "consumed"],
                "A non-prescription classification cannot simultaneously assert consumption.",
            )

    parsed_dates: dict[str, date | None] = {}
    for key in ("initial_date", "final_date", "legacy_start_date"):
        try:
            parsed_dates[key] = _parse_iso_date(fields[key])
        except (TypeError, ValueError):
            parsed_dates[key] = None
            add("date_invalid", [key], "Date must use YYYY-MM-DD or null.")

    initial = parsed_dates["initial_date"]
    final = parsed_dates["final_date"]
    if initial is not None and final is not None and final <= initial:
        add(
            "final_not_after_initial",
            ["initial_date", "final_date"],
            "Final date must be later than the initial marker.",
        )

    if payload_format == "legacy" and fields["legacy_start_date"] != fields["initial_date"]:
        add(
            "legacy_start_mismatch",
            ["initial_date", "legacy_start_date"],
            "Legacy start date must match the selected initial marker, including null.",
        )

    resolved_reference: date | None = None
    try:
        resolved_reference = _reference_date(document, payload, reference_date)
    except (TypeError, ValueError):
        add("reference_date_invalid", ["reference_date"], "Reference date must use YYYY-MM-DD.")

    if consumed is True and final is None:
        add(
            "consumed_requires_final_date",
            ["consumed", "final_date"],
            "Consumption cannot be asserted without a final date.",
        )
    elif consumed is True and resolved_reference is not None and resolved_reference <= final:
        add(
            "consumed_before_final_date",
            ["consumed", "final_date", "reference_date"],
            "Consumption cannot be asserted before the calculated final date has passed.",
        )

    if confidence == "INDETERMINADA" and not (
        isinstance(classification, str) and classification.startswith("Não Classificado - ")
    ):
        add(
            "indeterminate_confidence_requires_unclassified",
            ["classification", "confidence"],
            "Indeterminate confidence requires a non-classified result.",
        )

    return {
        "schema_version": "prescricao-intercorrente-preapproval-check/v1",
        "applicable": True,
        "automatic_patch": False,
        "gate_status": "review_required" if issues else "no_structural_issue",
        "issue_count": len(issues),
        "issues": issues,
        "payload_format": payload_format,
        "payload_path": payload_path,
        "reference_date": resolved_reference.isoformat() if resolved_reference else None,
    }


def _load(path: str) -> dict[str, Any]:
    raw = sys.stdin.read() if path == "-" else Path(path).read_text(encoding="utf-8")
    value = json.loads(raw)
    if not isinstance(value, dict):
        raise ValueError("input JSON must be an object")
    return value


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Check an existing prescription result without deciding the legal thesis."
    )
    parser.add_argument("--input", default="-", help="JSON file path, or - for stdin.")
    parser.add_argument("--reference-date", help="Override reference date as YYYY-MM-DD.")
    args = parser.parse_args(argv)

    try:
        result = analyze(_load(args.input), reference_date=args.reference_date)
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        print(
            json.dumps(
                {
                    "schema_version": "prescricao-intercorrente-preapproval-check/v1",
                    "error": str(exc),
                },
                ensure_ascii=False,
                sort_keys=True,
            )
        )
        return 2
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 1 if result["issues"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
