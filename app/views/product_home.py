"""产品 · 从研发到产品 / Product · From R&D to product."""

import streamlit as st

from brand import banner
from common import content, lang, open_questions
from mcsim.i18n import tr

L = lang()
banner(tr("prod_title", L), tr("sub_product", L), "product")
st.markdown(content("product_home", L))

open_questions("product", L)
