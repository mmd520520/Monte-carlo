"""产品 · 案例：Muse / Product · Case: Muse. The case summary plus a session you can try (simulated)."""

import numpy as np
import plotly.graph_objects as go
import streamlit as st

from common import content, lang
from mcsim.i18n import tr
from mcsim.plotting import FONT

L = lang()
CALM, LOW, SECONDS = 0.6, 0.35, 60


def session(skill: float, seed: int) -> np.ndarray:
    """A made-up 'calm' trace at 1 Hz: drifts around a level set by skill, with random lapses."""
    rng = np.random.default_rng(seed)
    x, out = 0.4, []
    for _ in range(SECONDS):
        x += 0.25 * (0.25 + 0.6 * skill - x) + rng.normal(0, 0.09)
        if rng.random() < 0.04:
            x -= 0.3  # a lapse: the mind wanders
        x = float(np.clip(x, 0, 1))
        out.append(x)
    return np.array(out)


def score(calm: np.ndarray):
    on = calm >= CALM
    birds, run = [], 0
    for t, c in enumerate(on):
        run = run + 1 if c else 0
        if run and run % 5 == 0:
            birds.append(t)  # every 5 s in a row of calm: a bird
    dips = np.flatnonzero(calm < LOW)
    recoveries = sum(1 for i in dips if np.any(calm[i + 1:i + 11] >= CALM))
    return 100 * on.mean(), birds, recoveries


st.title(tr("muse_title", L))
st.markdown(content("muse_case", L))

st.subheader(tr("muse_try", L))
left, right = st.columns([3, 1])
with right:
    skill = st.slider(tr("muse_skill", L), 0.0, 1.0, 0.5, 0.05)
    if st.button(tr("muse_run", L)):
        st.session_state["muse_seed"] = st.session_state.get("muse_seed", 0) + 1
seed = st.session_state.get("muse_seed", 0)
calm = session(skill, seed)
pct, birds, recov = score(calm)
with right:
    st.metric(tr("muse_calm_pct", L), f"{pct:.0f}%")
    st.metric(tr("muse_birds", L), len(birds))
    st.metric(tr("muse_recoveries", L), recov)

t = np.arange(SECONDS)
fig = go.Figure()
fig.add_trace(go.Scatter(x=t, y=1 - calm, name=tr("muse_sound", L), fill="tozeroy", mode="none",
                         fillcolor="rgba(91,101,115,0.18)"))
fig.add_trace(go.Scatter(x=t, y=calm, name=tr("muse_calm_axis", L), mode="lines", line=dict(color="#1B2A3A", width=2)))
fig.add_trace(go.Scatter(x=birds, y=calm[birds] if birds else [], name=tr("muse_birds", L), mode="markers",
                         marker=dict(symbol="star", size=12, color="#A51C30")))
fig.add_hline(y=CALM, line=dict(color="#A51C30", dash="dot", width=1))
fig.update_layout(height=320, margin=dict(l=10, r=10, t=10, b=10), font=FONT, plot_bgcolor="white",
                  legend=dict(orientation="h", y=1.08, x=0))
fig.update_xaxes(title=tr("muse_time", L), gridcolor="#E5E5E5")
fig.update_yaxes(range=[0, 1], gridcolor="#E5E5E5")
with left:
    st.plotly_chart(fig, use_container_width=True)

st.subheader(tr("muse_progress", L))
history = [score(session(min(1.0, skill + 0.03 * k), seed * 100 + k))[0] for k in range(10)]
baseline = float(np.mean(history[:3]))
fig2 = go.Figure(go.Bar(x=list(range(1, 11)), y=history, marker_color="#1B2A3A", name=tr("muse_score", L)))
fig2.add_hline(y=baseline, line=dict(color="#A51C30", dash="dash"), annotation_text=tr("muse_baseline", L),
               annotation_position="top left")
fig2.update_layout(height=280, margin=dict(l=10, r=10, t=30, b=10), font=FONT, plot_bgcolor="white")
fig2.update_xaxes(title=tr("muse_session_n", L), dtick=1)
fig2.update_yaxes(title=tr("muse_score", L), range=[0, 100], gridcolor="#E5E5E5")
st.plotly_chart(fig2, use_container_width=True)
st.caption(tr("muse_disclaimer", L))
