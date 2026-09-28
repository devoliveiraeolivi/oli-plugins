#!/usr/bin/env python3
"""Calcula o digest canônico e reproduzível do pacote oli-indexer-ops."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path
from typing import Any

EXCLUDED_PARTS = {".git", ".pytest_cache", "__pycache__"}
EXCLUDED_NAMES = {".DS_Store"}
EXCLUDED_SUFFIXES = {".pyc"}


class PluginDigestError(RuntimeError):
    pass


def _canonical_sha256(value: Any) -> str:
    encoded = json.dumps(
        value, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def _included(path: Path, root: Path) -> bool:
    relative = path.relative_to(root)
    return not (
        set(relative.parts) & EXCLUDED_PARTS
        or path.name in EXCLUDED_NAMES
        or path.suffix in EXCLUDED_SUFFIXES
    )


def package_manifest(root: Path) -> dict[str, Any]:
    root = root.resolve()
    manifest_path = root / ".codex-plugin" / "plugin.json"
    if not manifest_path.is_file():
        raise PluginDigestError(f"manifesto ausente: {manifest_path}")
    try:
        plugin = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise PluginDigestError(f"manifesto inválido: {exc}") from exc
    files: list[dict[str, Any]] = []
    for path in sorted(root.rglob("*"), key=lambda item: item.as_posix()):
        if not _included(path, root):
            continue
        if path.is_symlink():
            raise PluginDigestError(f"symlink não permitido no pacote: {path.relative_to(root)}")
        if not path.is_file():
            continue
        content = path.read_bytes()
        files.append(
            {
                "path": path.relative_to(root).as_posix(),
                "size": len(content),
                "sha256": hashlib.sha256(content).hexdigest(),
            }
        )
    return {
        "contract_version": "plugin-package-digest/v1",
        "plugin_name": plugin.get("name"),
        "plugin_version": plugin.get("version"),
        "files": files,
    }


def digest_result(root: Path, *, include_manifest: bool = False) -> dict[str, Any]:
    manifest = package_manifest(root)
    result: dict[str, Any] = {
        "contract_version": "plugin-package-digest-result/v1",
        "plugin_name": manifest["plugin_name"],
        "plugin_version": manifest["plugin_version"],
        "plugin_digest": _canonical_sha256(manifest),
        "file_count": len(manifest["files"]),
    }
    if include_manifest:
        result["manifest"] = manifest
    return result


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--root", type=Path, default=Path(__file__).resolve().parents[1], help="Raiz do plugin"
    )
    parser.add_argument("--compare", type=Path, help="Segunda raiz que deve produzir o mesmo digest")
    parser.add_argument("--manifest", action="store_true", help="Inclui lista hash-only de arquivos")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        primary = digest_result(args.root, include_manifest=args.manifest)
        if args.compare is not None:
            compared = digest_result(args.compare, include_manifest=False)
            primary["comparison"] = {
                "root": str(args.compare.resolve()),
                "plugin_digest": compared["plugin_digest"],
                "matches": compared["plugin_digest"] == primary["plugin_digest"],
            }
            if not primary["comparison"]["matches"]:
                print(json.dumps(primary, ensure_ascii=False, indent=2, sort_keys=True))
                return 1
        print(json.dumps(primary, ensure_ascii=False, indent=2, sort_keys=True))
        return 0
    except PluginDigestError as exc:
        print(f"erro: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
