"""首页 / Home: what this site does, its two halves (Science, Product), and how it runs and is maintained."""

import streamlit as st

from art import scene
from common import content, lang
from mcsim.i18n import tr

L = lang()

SCIENCE = [("views/science_home.py", "home_l_papers", ":material/menu_book:"),
           ("views/simulator.py", "home_l_simulate", ":material/science:"),
           ("views/validation.py", "home_l_validate", ":material/fact_check:"),
           ("views/principles.py", "home_l_principles", ":material/account_tree:")]
PRODUCT = [("views/product_home.py", "home_l_product", ":material/rocket_launch:"),
           ("views/muse_case.py", "home_l_muse", ":material/headphones:"),
           ("views/headband_loop.py", "home_l_headband", ":material/psychology:"),
           ("views/laser.py", "home_l_laser", ":material/flare:")]
MAINTAIN = [(":material/bolt:", "home_m_live"), (":material/verified:", "home_m_tested"),
            (":material/edit_note:", "home_m_content"), (":material/rocket_launch:", "home_m_publish")]

with st.container(key="jz-hero"):
    text, picture = st.columns([5, 4], vertical_alignment="center", gap="large")
    with text:
        st.title(tr("home_title", L), anchor=False)
        st.markdown(tr("home_sub", L))
        with st.container(horizontal=True, gap="small"):
            with st.container(key="jz-cta-main", width="content"):
                st.page_link("views/science_home.py", label=tr("home_cta_science", L), icon=":material/menu_book:")
            with st.container(key="jz-cta-alt", width="content"):
                st.page_link("views/product_home.py", label=tr("home_cta_product", L), icon=":material/rocket_launch:")
    with picture:
        st.image(scene("hero"), width="stretch")

left, right = st.columns(2, gap="medium")
for col, key, art, links in ((left, "science", "learn", SCIENCE), (right, "product", "devices", PRODUCT)):
    with col, st.container(border=True, key=f"jz-card-{key}"):
        with st.container(key=f"jz-art-{key}"):
            st.image(scene(art), width="stretch")
        st.subheader(tr(f"home_{key}_title", L), anchor=False)
        st.markdown(content(f"home_{key}", L))
        for page, label, icon in links:
            st.page_link(page, label=tr(label, L), icon=icon)

st.subheader(tr("home_maintain_title", L), anchor=False)
for col, (icon, key) in zip(st.columns(len(MAINTAIN), gap="medium"), MAINTAIN):
    with col, st.container(border=True, key=f"jz-fact-{key}"):
        st.markdown(f"**{icon} {tr(key + '_t', L)}**")
        st.markdown(tr(key, L))
st.markdown(tr("home_next", L))
