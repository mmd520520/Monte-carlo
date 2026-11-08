"""交互界面 / Interactive app: uv run streamlit run app/streamlit_app.py  (English: add ?lang=en to the URL)"""

from __future__ import annotations

import io
import json
import sys
from pathlib import Path

import numpy as np
import streamlit as st

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from mcsim import load_preset, simulate  # noqa: E402
from mcsim.analysis import axis_profile, dose_table, skin_surface_on_axis  # noqa: E402
from mcsim.geometry import build_volume  # noqa: E402
from mcsim.i18n import LANG_LABELS, LANGS, preset_notes, preset_title, tissue_name, tissue_source, tr  # noqa: E402
from mcsim.plotting import (  # noqa: E402
    UNIT_SCALE, axis_profile_figure, dose_figure, fluence_section, tissue_section,
)

# Language: the switch at the top right; ?lang=en opens the English version directly.
# Clicking the selected button of a segmented control clears it, so fall back to the last language.
if st.session_state.get("lang") not in LANGS:
    st.session_state["lang"] = st.session_state.get("_lang_prev") or (
        "en" if st.query_params.get("lang") == "en" else "zh")
lang = st.session_state["lang"]
st.session_state["_lang_prev"] = lang

st.set_page_config(page_title=tr("page_title", lang), layout="wide")
st.query_params["lang"] = lang  # keeps the current language in a shareable link

PRESETS = ["knee_980nm", "skin_500nm"]
RESOLUTION = {  # stride -> (label key, voxel size shown)
    "knee_980nm": {1: ("res_original", "1.25 mm"), 2: ("res_faster", "2.5 mm")},
    "skin_500nm": {4: ("res_recommended", "40 μm"), 2: (None, "20 μm"), 10: ("res_matlab_coarse", "100 μm"),
                   1: ("res_full_slow", "10 μm")},
}
DOSE_DEFAULTS = {  # depths and disk radius in display units
    "knee_980nm": dict(depths="1, 2, 4, 8", radius=1.0, exposure=300.0),
    "skin_500nm": dict(depths="0.1, 0.3, 0.5, 1.0", radius=0.25, exposure=60.0),
}


@st.cache_resource(show_spinner=False, max_entries=6)
def run_cached(name: str, stride: int, photons: int, seed: int, theta: float, phi: float,
               diameter_mm: float, power_w: float | None):
    preset = load_preset(name, photons=photons, seed=seed, stride=stride, theta_deg=theta, phi_deg=phi,
                         diameter=diameter_mm)
    preset.source.power_w = power_w  # None = no power set: results stay per unit power
    return simulate(preset, workers=0)


@st.cache_resource(show_spinner=False, max_entries=6)
def volume_cached(name: str, stride: int):
    preset = load_preset(name, stride=stride)
    return preset, build_volume(preset.geometry)


# ---------------- header with the language switch ----------------
_, switch = st.columns([5, 1])
with switch:
    st.segmented_control(tr("language", lang), LANGS, key="lang", format_func=LANG_LABELS.get,
                         selection_mode="single", label_visibility="collapsed", width="content")
st.title(tr("title", lang))

# ---------------- sidebar ----------------
with st.sidebar:
    st.header(tr("settings", lang))
    # Dropdowns are keyed per language (Streamlit keeps the old option label otherwise); the choice itself
    # lives in a separate session key, so switching language keeps it.
    current = st.session_state.get("preset", PRESETS[0])
    name = st.selectbox(tr("model", lang), PRESETS, index=PRESETS.index(current), key=f"preset_{lang}",
                        format_func=lambda n: tr(f"preset_{n}", lang))
    st.session_state["preset"] = name
    base = load_preset(name)
    unit = base.display_unit
    s = UNIT_SCALE[unit]
    res = RESOLUTION[name]
    strides = list(res)
    current = st.session_state.get(f"res_{name}", strides[0])
    stride = st.selectbox(tr("voxel_size", lang), strides, index=strides.index(current), key=f"res_{name}_{lang}",
                          format_func=lambda k: tr(res[k][0], lang, size=res[k][1]) if res[k][0] else res[k][1])
    st.session_state[f"res_{name}"] = stride
    photons = st.select_slider(tr("photons", lang),
                               options=[2_000, 5_000, 10_000, 20_000, 50_000, 100_000, 200_000, 500_000],
                               value=20_000 if name == "knee_980nm" else 50_000, key=f"n_{name}")
    seed = st.number_input(tr("seed", lang), min_value=0, max_value=2**31 - 1, value=1, step=1, key=f"seed_{name}")
    st.subheader(tr("source", lang))
    diameter = st.number_input(tr("diameter", lang, unit=unit), min_value=0.01,
                               value=float(base.source.diameter * s), step=0.5 if unit == "cm" else 0.1,
                               key=f"d_{name}")
    theta = st.slider(tr("theta", lang), 0.0, 80.0, 0.0, 1.0, key=f"theta_{name}")
    phi_deg = st.slider(tr("phi", lang), 0.0, 360.0, 0.0, 5.0, key=f"phi_{name}", disabled=theta == 0)
    has_power = st.checkbox(tr("has_power", lang), value=base.source.power_w is not None, key=f"hp_{name}")
    power = st.number_input(tr("power", lang), min_value=0.0001, value=float(base.source.power_w or 0.1),
                            key=f"p_{name}", disabled=not has_power) if has_power else None
    run_clicked = st.button(tr("run", lang), type="primary", use_container_width=True)

params = (name, stride, int(photons), int(seed), float(theta), float(phi_deg), float(diameter / s),
          float(power) if power else None)
if run_clicked or st.session_state.get("last_params") is None or st.session_state.get("last_name") != name:
    st.session_state["last_params"] = params
    st.session_state["last_name"] = name
active = st.session_state["last_params"]
stale = active != params

st.caption(tr("caption", lang, title=preset_title(base, lang), based_on=base.based_on, unit=unit))

try:
    with st.spinner(tr("spinner", lang)):
        result = run_cached(*active)
except ValueError as exc:
    st.error(tr("param_error", lang, error=exc))
    st.stop()

if stale:
    st.info(tr("stale", lang))

e = result.energy
items = [("absorbed", "m_absorbed"), ("reflected", "m_reflected"), ("side", "m_side"),
         ("transmitted", "m_transmitted"), ("specular", "m_specular")]
row1, row2 = st.columns(3), st.columns(3)
for c, (k, label) in zip(list(row1) + list(row2), items):
    c.metric(tr(label, lang), f"{e[k] * 100:.2f}%")
row2[2].metric(tr("m_total", lang), f"{e['bookkeeping'] * 100:.2f}%", help=tr("m_total_help", lang))
st.caption(tr("run_caption", lang, balance=f"{e['bookkeeping']:.12f}", n=f"{result.n_photons:,}",
              seed=result.preset.run.seed, secs=f"{result.elapsed_s:.1f}", workers=result.workers,
              voxel=f"{result.volume.voxel[0] * s:g}", unit=unit, shape=result.volume.shape))

tab_model, tab_light, tab_dose, tab_export = st.tabs(
    [tr("tab_model", lang), tr("tab_light", lang), tr("tab_dose", lang), tr("tab_export", lang)])

with tab_model:
    preset_v, vol = volume_cached(name, stride)
    st.plotly_chart(tissue_section(vol, preset_v, lang=lang), use_container_width=True)
    st.markdown(f"**{tr('optics', lang)}**")
    rows = []
    for t in preset_v.tissues:
        rows.append({tr("col_tissue", lang): tissue_name(t, lang), f"μa [1/{unit}]": round(t.mua / s, 4),
                     f"μs′ [1/{unit}]": round(t.mus * (1 - t.g) / s, 4), "g": t.g, "n": t.n,
                     tr("col_source", lang): tissue_source(t, lang)})
    st.dataframe(rows, hide_index=True, use_container_width=True)
    notes = preset_notes(preset_v, lang)
    if notes:
        with st.expander(tr("notes", lang), expanded=True):
            for note in notes:
                st.markdown(f"- {note}")

with tab_light:
    yv = st.slider(tr("section_y", lang, unit=unit), float(result.volume.centers(1).min() * s),
                   float(result.volume.centers(1).max() * s), 0.0, key=f"y_{name}")
    st.plotly_chart(fluence_section(result, y_mm=yv / s, power_w=result.power_w, lang=lang), use_container_width=True)
    depth, prof = axis_profile(result)
    st.plotly_chart(axis_profile_figure(depth, prof, unit, result.power_w, lang=lang), use_container_width=True)
    st.caption(tr("light_caption", lang))

with tab_dose:
    if result.power_w is None:
        st.info(tr("dose_needs_power", lang))
    else:
        d = DOSE_DEFAULTS[name]
        c1, c2, c3 = st.columns(3)
        depths_txt = c1.text_input(tr("depths", lang, unit=unit), d["depths"], key=f"dd_{name}")
        exposure = c2.number_input(tr("exposure", lang), min_value=1.0, value=d["exposure"], key=f"de_{name}")
        radius = c3.number_input(tr("radius", lang, unit=unit), min_value=0.01, value=d["radius"], key=f"dr_{name}")
        try:
            depths = [float(x) for x in depths_txt.replace("，", ",").split(",") if x.strip()]
            rows = dose_table(result, [x / s for x in depths], exposure, radius / s)
        except ValueError as exc:
            st.error(str(exc))
            rows = []
        if rows:
            st.plotly_chart(dose_figure(rows, unit, exposure, lang=lang), use_container_width=True)
            table = [{tr("col_depth", lang, unit=unit): r.depth_mm * s,
                      tr("col_axis_h", lang): round(r.axis_H_j_cm2, 4),
                      tr("col_disk_h", lang): round(r.disk_mean_H_j_cm2, 4),
                      tr("col_disk_e", lang): round(r.disk_energy_j, 4),
                      tr("col_share", lang): f"{r.disk_energy_fraction:.2%}",
                      tr("col_air", lang): tr("yes", lang) if r.disk_has_air else ""}
                     for r in rows]
            st.dataframe(table, hide_index=True, use_container_width=True)
            st.caption(tr("dose_caption", lang, z=f"{skin_surface_on_axis(result.volume) * s:.2f}", unit=unit))
            st.session_state["dose_rows"] = table

with tab_export:
    buf = io.BytesIO()
    np.savez_compressed(buf, labels=result.volume.labels, A=result.A, phi=result.phi, R2=result.R2, T2=result.T2,
                        meta=np.array(json.dumps({"preset": result.preset.to_dict(), "energy": result.energy},
                                                 ensure_ascii=False)))
    st.download_button(tr("dl_npz", lang), buf.getvalue(), file_name=f"{name}_results.npz")
    cfg = json.dumps(result.preset.to_dict(), ensure_ascii=False, indent=2)
    st.download_button(tr("dl_json", lang), cfg, file_name=f"{name}_config.json")
    if st.session_state.get("dose_rows"):
        import csv

        out = io.StringIO()
        w = csv.DictWriter(out, fieldnames=list(st.session_state["dose_rows"][0]))
        w.writeheader()
        w.writerows(st.session_state["dose_rows"])
        st.download_button(tr("dl_csv", lang), out.getvalue().encode("utf-8-sig"), file_name=f"{name}_dose.csv")
    st.caption(tr("export_caption", lang))
