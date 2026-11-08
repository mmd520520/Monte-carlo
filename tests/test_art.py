"""Page illustrations (app/art.py) are valid SVG and self-contained: no links to other files or sites."""

import sys
import xml.dom.minidom
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "app"))

import art  # noqa: E402


def test_every_scene_is_valid_self_contained_svg():
    for name in art.SCENES:
        svg = art.scene(name)
        doc = xml.dom.minidom.parseString(svg)
        assert doc.documentElement.tagName == "svg", name
        assert "http" not in svg.replace("http://www.w3.org/2000/svg", ""), name
