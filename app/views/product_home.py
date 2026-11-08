"""产品 · 从研发到产品 / Product · From R&D to product."""

import streamlit as st

from common import content, lang, private_content
from mcsim.i18n import tr

L = lang()
st.title(tr("prod_title", L))
st.markdown(content("product_home", L))

notes = private_content("product_notes", L)
with st.expander(tr("internal_notes", L), expanded=notes is not None):
    if notes:
        st.markdown(notes)
    else:
        st.caption(tr("private_missing", L))
