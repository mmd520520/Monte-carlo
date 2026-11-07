"""Headless run of the Streamlit app (streamlit.testing): both presets render without errors."""

from pathlib import Path

import pytest
from streamlit.testing.v1 import AppTest

APP = str(Path(__file__).resolve().parent.parent / "app" / "streamlit_app.py")


@pytest.mark.slow
def test_app_knee_then_skin():
    at = AppTest.from_file(APP, default_timeout=120)
    at.run()
    assert not at.exception, at.exception
    assert any("膝关节" in c.value for c in at.caption)
    labels = [m.label for m in at.metric]
    assert "组织吸收" in labels and "合计" in labels
    assert at.metric[labels.index("合计")].value == "100.00%"

    at.selectbox(key="preset").set_value("皮肤血管 · 500 nm").run()
    assert not at.exception, at.exception
    assert any("皮肤血管" in c.value for c in at.caption)
    # skin preset has no power: the dose tab asks for it instead of failing
    assert any("剂量需要总功率" in i.value for i in at.info)
