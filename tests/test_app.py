"""Headless run of the Streamlit app (streamlit.testing): both presets and both languages render without errors."""

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

    at.selectbox(key="preset_zh").set_value("skin_500nm").run()
    assert not at.exception, at.exception
    assert any("皮肤血管" in c.value for c in at.caption)
    # skin preset has no power: the dose tab asks for it instead of failing
    assert any("剂量需要总功率" in i.value for i in at.info)


@pytest.mark.slow
def test_language_switch_keeps_the_result():
    at = AppTest.from_file(APP, default_timeout=120)
    at.run()
    zh_total = at.metric[[m.label for m in at.metric].index("合计")].value

    at.session_state["lang"] = "en"  # what the 中文 | EN switch at the top right sets
    at.run()
    assert not at.exception, at.exception
    assert at.title[0].value == "Monte Carlo light transport simulation"
    assert any("Knee (980 nm)" in c.value for c in at.caption)
    labels = [m.label for m in at.metric]
    assert "Absorbed" in labels and "Total" in labels
    assert at.metric[labels.index("Total")].value == zh_total  # same run, only the words change
    assert not any("组织吸收" in m.label for m in at.metric)
    # the dropdowns show English labels and keep the choice
    assert at.selectbox(key="preset_en").value == "knee_980nm"
    assert at.selectbox(key="preset_en").format_func("knee_980nm") == "Knee · 980 nm"

    at.selectbox(key="preset_en").set_value("skin_500nm").run()
    at.session_state["lang"] = "zh"
    at.run()
    assert not at.exception, at.exception
    assert at.selectbox(key="preset_zh").value == "skin_500nm"
