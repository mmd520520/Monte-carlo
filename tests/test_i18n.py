"""Every interface string exists in both languages, and every preset has its English text."""

import string

import pytest

from mcsim import load_preset
from mcsim.config import list_presets
from mcsim.i18n import TEXT, preset_notes, preset_title, tissue_name, tissue_source, tr


def _fields(s: str) -> set[str]:
    return {f for _, f, _, _ in string.Formatter().parse(s) if f}


def test_both_languages_with_same_placeholders():
    empty = [k for k, (zh, en) in TEXT.items() if not (zh.strip() and en.strip())]
    mismatched = [k for k, (zh, en) in TEXT.items() if _fields(zh) != _fields(en)]
    assert not empty, f"missing a language: {empty}"
    assert not mismatched, f"placeholders differ: {mismatched}"


def test_english_text_has_no_chinese():
    for key, (_, en) in TEXT.items():
        assert not any("一" <= ch <= "鿿" for ch in en), key


@pytest.mark.parametrize("name", list_presets())
def test_presets_have_english_text(name):
    p = load_preset(name)
    assert p.title_en and preset_title(p, "en") == p.title_en and preset_title(p, "zh") == p.title
    assert len(p.notes_en) == len(p.notes) and preset_notes(p, "en") == p.notes_en
    for t in p.tissues:
        assert t.name_en and tissue_name(t, "en") == t.name_en, t.name
        assert t.source_en and tissue_source(t, "en") == t.source_en, t.name


def test_tr_fills_placeholders():
    assert tr("diameter", "en", unit="cm") == "Beam diameter [cm]"
    assert tr("diameter", "zh", unit="cm") == "光斑直径 [cm]"


CONTENT = __import__("pathlib").Path(__file__).resolve().parents[1] / "app" / "content"


def test_content_files_in_both_languages():
    zh = {p.name.removesuffix(".zh.md") for p in CONTENT.glob("*.zh.md")}
    en = {p.name.removesuffix(".en.md") for p in CONTENT.glob("*.en.md")}
    assert zh and zh == en, f"only one language: {sorted(zh ^ en)}"


def test_papers_have_both_languages_and_links():
    import yaml

    for section in yaml.safe_load((CONTENT / "papers.yaml").read_text(encoding="utf-8")).values():
        for p in section:
            assert p["zh"] and p["en"] and p["tool_zh"] and p["tool_en"], p["title"]
            assert p["link"].startswith("https://"), p["title"]
