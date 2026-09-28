from __future__ import annotations

import importlib.util
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("plugin_digest", ROOT / "scripts/plugin_digest.py")
assert SPEC and SPEC.loader
plugin_digest = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(plugin_digest)


def _plugin(root: Path, *, value: str = "conteúdo") -> None:
    (root / ".codex-plugin").mkdir(parents=True)
    (root / ".codex-plugin" / "plugin.json").write_text(
        '{"name":"oli-indexer-ops","version":"0.1.0"}', encoding="utf-8"
    )
    (root / "skills").mkdir()
    (root / "skills" / "á.md").write_text(value, encoding="utf-8")


def test_digest_e_reproduzivel_e_ignora_artefatos(tmp_path: Path) -> None:
    first = tmp_path / "first"
    second = tmp_path / "second"
    _plugin(first)
    _plugin(second)
    (first / ".pytest_cache").mkdir()
    (first / ".pytest_cache" / "noise").write_text("x", encoding="utf-8")
    (second / "__pycache__").mkdir()
    (second / "__pycache__" / "noise.pyc").write_bytes(b"x")

    left = plugin_digest.digest_result(first)
    right = plugin_digest.digest_result(second)

    assert left["plugin_digest"] == right["plugin_digest"]
    assert left["file_count"] == 2


def test_digest_muda_com_conteudo_utf8(tmp_path: Path) -> None:
    first = tmp_path / "first"
    second = tmp_path / "second"
    _plugin(first, value="Não enfrentado")
    _plugin(second, value="Nao enfrentado")

    assert (
        plugin_digest.digest_result(first)["plugin_digest"]
        != plugin_digest.digest_result(second)["plugin_digest"]
    )


def test_symlink_falha_fechado(tmp_path: Path) -> None:
    root = tmp_path / "plugin"
    _plugin(root)
    (root / "link").symlink_to(root / "skills" / "á.md")

    try:
        plugin_digest.package_manifest(root)
    except plugin_digest.PluginDigestError as exc:
        assert "symlink" in str(exc)
    else:
        raise AssertionError("symlink deveria bloquear o digest")
