"""产品 · 康复激光 / Product · Rehab laser: settings → surface dose → dose at depth (knee model)."""

import math

import plotly.graph_objects as go
import streamlit as st

from brand import banner
from common import content, fmt_count, lang, private_content, run_with_bar
from mcsim.analysis import dose_table
from mcsim.i18n import tr
from mcsim.plotting import FONT

L = lang()
DEPTHS_CM = [0.5, 1.0, 2.0, 3.0, 4.0]

banner(tr("laser_title", L), tr("sub_laser", L), "laser")
st.markdown(content("laser_public", L))
st.info(tr("live_intro_laser", L), icon="⚡")

c = st.columns(4)
power = c[0].number_input(tr("laser_power", L), 0.1, 30.0, 20.0, 0.5)
spot_cm = c[1].number_input(tr("laser_spot", L), 0.5, 10.0, 8.0, 0.5)
time_s = c[2].number_input(tr("laser_time", L), 1.0, 1800.0, 300.0, 30.0)
photons = c[3].selectbox(tr("laser_photons", L), [100_000, 1_000_000, 10_000_000], format_func=fmt_count,
                         help=tr("photons_help", L))

area = math.pi * (spot_cm / 2) ** 2
irr = power / area
m = st.columns(2)
m[0].metric(tr("laser_irr", L), f"{irr:.3g} W/cm²")
m[1].metric(tr("laser_surface", L), f"{irr * time_s:.3g} J/cm²")

# Simulated per unit power: changing the power only rescales, so it does not trigger a new run.
result = run_with_bar(L, "knee_980nm", 2, int(photons), 1, 0.0, 0.0, spot_cm * 10, None, again="again_laser")
rows = dose_table(result, [d * 10 for d in DEPTHS_CM], time_s, min(spot_cm * 5, 5.0), power_w=float(power))
surface = irr * time_s
st.markdown(f"**{tr('laser_depth', L)}**")
table = [{tr("col_depth", L, unit="cm"): d, tr("col_axis_h", L): round(r.axis_H_j_cm2, 3),
          tr("laser_share", L): f"{r.axis_H_j_cm2 / surface:.1%}"} for d, r in zip(DEPTHS_CM, rows)]
left, right = st.columns([1, 1])
left.dataframe(table, hide_index=True, use_container_width=True)
fig = go.Figure(go.Scatter(x=DEPTHS_CM, y=[r.axis_H_j_cm2 for r in rows], mode="lines+markers",
                           line=dict(color="#1040C1", width=2)))
fig.update_layout(height=260, margin=dict(l=10, r=10, t=10, b=10), font=FONT, plot_bgcolor="white")
fig.update_xaxes(title=tr("fig_depth_below", L, unit="cm"), gridcolor="#E7EBF3")
fig.update_yaxes(title="H [J/cm²]", type="log", gridcolor="#E7EBF3")
right.plotly_chart(fig, use_container_width=True)
st.caption(tr("laser_caption", L))

notes = private_content("laser_case", L)
with st.expander(tr("internal_notes", L), expanded=notes is not None):
    if notes:
        st.markdown(notes)
    else:
        st.caption(tr("private_missing", L))
