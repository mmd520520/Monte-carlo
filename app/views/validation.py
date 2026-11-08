"""科普 · 验证 / Science · Validation: any uniform slab, this engine against adding-doubling."""

import streamlit as st

from common import content, lang
from mcsim.i18n import tr
from mcsim.reference import compare_slab

L = lang()


@st.cache_data(show_spinner=False, max_entries=20)
def run(mua, mus, g, n, d, photons):
    c = compare_slab(mua, mus, g, n, d, launch_from_air=True, photons=photons, seed=11)
    return c


st.title(tr("val_title", L))
st.markdown(content("validation_intro", L))

with st.form("slab"):
    c = st.columns(6)
    mua = c[0].number_input(tr("val_mua", L), 0.0, 50.0, 0.1, 0.05, format="%.3f")
    mus = c[1].number_input(tr("val_mus", L), 0.0, 200.0, 10.0, 0.5)
    g = c[2].number_input(tr("val_g", L), -0.99, 0.99, 0.9, 0.05)
    n = c[3].number_input(tr("val_n", L), 1.0, 2.0, 1.4, 0.01)
    d = c[4].number_input(tr("val_d", L), 0.05, 3.0, 1.0, 0.05)
    photons = c[5].select_slider(tr("val_photons", L), [20_000, 100_000, 200_000, 1_000_000], value=100_000)
    submitted = st.form_submit_button(tr("run", L), type="primary")

if mua + mus <= 0:
    st.stop()
with st.spinner(tr("spinner", L)):
    r = run(float(mua), float(mus), float(g), float(n), float(d), int(photons))

rows = []
for q, key in (("R", "val_R"), ("T", "val_T"), ("A", "val_A")):
    mc = {"R": (r.R_mc, r.R_se), "T": (r.T_mc, r.T_se), "A": (r.A_mc, (r.R_se ** 2 + r.T_se ** 2) ** 0.5)}[q]
    ad = {"R": r.R_ad, "T": r.T_ad, "A": r.A_ad}[q]
    rows.append({tr("val_quantity", L): tr(key, L), tr("val_mc", L): f"{mc[0]:.4f} ± {mc[1]:.4f}",
                 tr("val_ad", L): f"{ad:.4f}", tr("val_z", L): f"{r.z(q):+.2f}"})
st.dataframe(rows, hide_index=True, use_container_width=True)
if all(abs(r.z(q)) <= 3 for q in "RTA"):
    st.success(tr("val_ok", L))
else:
    st.warning(tr("val_check", L))
st.caption(tr("val_caption", L, n=f"{photons:,}", secs=f"{r.elapsed_s:.1f}"))
