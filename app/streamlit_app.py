"""交互界面 / Interactive app: uv run streamlit run app/streamlit_app.py  (English: add ?lang=en to the URL)

Two sections: 科普 Science (papers, simulation, validation) and 产品 Product (from R&D to product).
Pages live in app/views/; long text in app/content/; internal notes, if present, in project/private/app/.
"""

from __future__ import annotations

import sys
from pathlib import Path

import streamlit as st

APP = Path(__file__).resolve().parent
sys.path.insert(0, str(APP.parent))
sys.path.insert(0, str(APP))

from mcsim.i18n import LANG_LABELS, LANGS, tr  # noqa: E402

# Language: the switch at the top right; ?lang=en opens the English version directly.
# Clicking the selected button of a segmented control clears it, so fall back to the last language.
if st.session_state.get("lang") not in LANGS:
    st.session_state["lang"] = st.session_state.get("_lang_prev") or (
        "en" if st.query_params.get("lang") == "en" else "zh")
lang = st.session_state["lang"]
st.session_state["_lang_prev"] = lang

st.set_page_config(page_title=tr("page_title", lang), layout="wide")
st.query_params["lang"] = lang  # keeps the current language in a shareable link

_, switch = st.columns([5, 1])
with switch:
    st.segmented_control(tr("language", lang), LANGS, key="lang", format_func=LANG_LABELS.get,
                         selection_mode="single", label_visibility="collapsed", width="content")

V = APP / "views"
pages = {
    tr("nav_science", lang): [
        st.Page(V / "science_home.py", title=tr("nav_science_home", lang), icon=":material/menu_book:",
                url_path="science", default=True),
        st.Page(V / "simulator.py", title=tr("nav_simulator", lang), icon=":material/science:", url_path="simulate"),
        st.Page(V / "validation.py", title=tr("nav_validation", lang), icon=":material/fact_check:", url_path="validate"),
    ],
    tr("nav_product", lang): [
        st.Page(V / "product_home.py", title=tr("nav_product_home", lang), icon=":material/rocket_launch:",
                url_path="product"),
        st.Page(V / "muse_case.py", title=tr("nav_muse", lang), icon=":material/headphones:", url_path="case-muse"),
        st.Page(V / "headband_loop.py", title=tr("nav_headband", lang), icon=":material/psychology:",
                url_path="headband"),
        st.Page(V / "laser.py", title=tr("nav_laser", lang), icon=":material/flare:", url_path="laser"),
    ],
}
st.navigation(pages).run()
