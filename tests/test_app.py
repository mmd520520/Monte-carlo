"""Headless runs of the Streamlit app (streamlit.testing): every page in both languages, the simulator flow,
and the language switch."""

from pathlib import Path

import pytest
from streamlit.testing.v1 import AppTest

APP = str(Path(__file__).resolve().parent.parent / "app" / "streamlit_app.py")
PAGES = ["views/science_home.py", "views/simulator.py", "views/validation.py", "views/principles.py",
         "views/product_home.py",
         "views/muse_case.py", "views/headband_loop.py", "views/laser.py"]


def _app(lang: str = "zh") -> AppTest:
    at = AppTest.from_file(APP, default_timeout=180)
    at.session_state["lang"] = lang
    at.run()
    assert not at.exception, at.exception
    return at


@pytest.mark.slow
@pytest.mark.parametrize("lang", ["zh", "en"])
def test_every_page_renders(lang):
    at = _app(lang)
    for page in PAGES:
        at.switch_page(page).run()
        assert not at.exception, (lang, page, at.exception)
        assert at.title, (lang, page)


@pytest.mark.slow
def test_simulator_knee_then_skin():
    at = _app("zh")
    at.switch_page("views/simulator.py").run()
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
    at = _app("zh")
    at.switch_page("views/simulator.py").run()
    zh_total = at.metric[[m.label for m in at.metric].index("合计")].value

    at.session_state["lang"] = "en"  # what the 中文 | EN switch at the top right sets
    at.run()
    assert not at.exception, at.exception
    assert at.title[0].value == "Monte Carlo light transport simulation"
    assert any("Knee (980 nm)" in c.value for c in at.caption)
    labels = [m.label for m in at.metric]
    assert "Absorbed" in labels and "Total" in labels
    assert at.metric[labels.index("Total")].value == zh_total  # same run, only the words change
    # the dropdowns show English labels and keep the choice
    assert at.selectbox(key="preset_en").value == "knee_980nm"

    at.selectbox(key="preset_en").set_value("skin_500nm").run()
    at.session_state["lang"] = "zh"
    at.run()
    assert not at.exception, at.exception
    assert at.selectbox(key="preset_zh").value == "skin_500nm"


@pytest.mark.slow
@pytest.mark.parametrize("lang", ["zh", "en"])
def test_principles_page_answers_algorithm_and_gpu(lang):
    at = _app(lang)
    at.switch_page("views/principles.py").run()
    assert not at.exception, at.exception
    assert len(at.tabs) == 4
    assert len(at.get("graphviz_chart")) == 3  # one photon packet; batches and threads; CPU vs GPU
    text = " ".join(m.value for m in at.markdown)
    for term in ("Henyey", "Fresnel", "GPU", "MCX", "SIMT", "atomic", "10⁸", "S1", "V1", "A2"):
        assert term in text, (lang, term)


def test_photon_counts_are_readable():
    import sys

    sys.path.insert(0, str(Path(APP).parent))
    from common import PHOTON_OPTIONS, fmt_count

    assert PHOTON_OPTIONS[-1] == 100_000_000
    assert [fmt_count(n) for n in (50_000, 1_000_000, 2_000_000, 10_000_000, 100_000_000, 1_234_567)] == [
        "50,000", "10⁶", "2×10⁶", "10⁷", "10⁸", "1,234,567"]


@pytest.mark.slow
def test_server_can_hide_the_largest_grid(monkeypatch):
    monkeypatch.setenv("MCSIM_MAX_VOXELS", "10e6")
    import sys

    sys.modules.pop("common", None)  # re-read the limit
    at = _app("zh")
    at.switch_page("views/simulator.py").run()
    at.selectbox(key="preset_zh").set_value("skin_500nm").run()
    assert not at.exception, at.exception
    options = " ".join(at.selectbox(key="res_skin_500nm_zh").options)
    sys.modules.pop("common", None)  # later tests read the default limit again
    assert "20 μm" in options and "10 μm" not in options  # 8 million voxels shown, 64 million hidden


@pytest.mark.slow
def test_results_say_they_are_computed_live():
    import streamlit as st

    st.cache_resource.clear()  # start with no recent results on this "server"
    st.cache_data.clear()
    at = _app("zh")
    at.switch_page("views/simulator.py").run()
    assert any("实时计算，不是预设结果" in i.value for i in at.info)
    assert any("刚刚在服务器上实时算完" in c.value for c in at.caption)
    at.run()  # any widget change reruns the page: still this visitor's own run, not someone else's
    assert any("为你实时算出" in c.value for c in at.caption)

    other = _app("zh")  # a second visitor with the same default settings gets the identical recent result
    other.switch_page("views/simulator.py").run()
    assert any("有人用完全相同的参数" in c.value and "换一个随机种子" in c.value for c in other.caption)

    for page, intro in (("views/validation.py", "实时计算"), ("views/laser.py", "实时计算")):
        other.switch_page(page).run()
        assert not other.exception, (page, other.exception)
        assert any(intro in i.value for i in other.info), page
        assert any("实时算完" in c.value or "实时计算的结果" in c.value for c in other.caption), page
