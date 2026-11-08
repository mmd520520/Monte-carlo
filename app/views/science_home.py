"""科普 · 论文与前沿 / Science · Papers & frontier."""

import streamlit as st

from brand import banner
from common import content, lang, papers
from mcsim.i18n import tr

L = lang()
SEP = "：" if L == "zh" else ": "

banner(tr("sci_title", L), tr("sub_science", L), "science")
st.markdown(content("science_intro", L))

P = papers()
for key, heading in (("classic", "sci_classic"), ("frontier", "sci_frontier")):
    st.subheader(tr(heading, L))
    cols = st.columns(2)
    for i, p in enumerate(P[key]):
        with cols[i % 2].container(border=True):
            st.markdown(f"**{p['title']}**")
            st.caption(f"{p['cite']} · [{tr('sci_open', L)}]({p['link']})")
            st.markdown(p[L])
            st.markdown(f"*{tr('sci_in_tool', L)}{SEP}{p['tool_' + L]}*")
