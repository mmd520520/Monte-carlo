"""科普 · 仿真 / Science · Simulation: the two presets, light distribution, dose and export."""

from __future__ import annotations

import io
import json

import numpy as np
import streamlit as st

from common import MAX_VOXELS, PHOTON_OPTIONS, fmt_count, fmt_duration, lang, photon_rate, run_with_bar
from mcsim import load_preset
from mcsim.analysis import axis_profile, dose_table, skin_surface_on_axis
from mcsim.geometry import build_volume
from mcsim.i18n import preset_notes, preset_title, tissue_name, tissue_source, tr
from mcsim.plotting import UNIT_SCALE, axis_profile_figure, dose_figure, fluence_section, tissue_section

L = lang()
PRESETS = ["knee_980nm", "skin_500nm"]
RESOLUTION = {  # stride -> (label key, voxel size shown, number of voxels)
    "knee_980nm": {1: ("res_original", "1.25 mm", 2_580_480), 2: ("res_faster", "2.5 mm", 322_560)},
    "skin_500nm": {4: ("res_recommended", "40 μm", 1_000_000), 2: (None, "20 μm", 8_000_000),
                   10: ("res_matlab_coarse", "100 μm", 64_000), 1: ("res_full_slow", "10 μm", 64_000_000)},
}
DOSE_DEFAULTS = {  # depths and disk radius in display units
    "knee_980nm": dict(depths="1, 2, 4, 8", radius=1.0, exposure=300.0),
    "skin_500nm": dict(depths="0.1, 0.3, 0.5, 1.0", radius=0.25, exposure=60.0),
}


@st.cache_resource(show_spinner=False, max_entries=6)
def volume_cached(name: str, stride: int):
    preset = load_preset(name, stride=stride)
    return preset, build_volume(preset.geometry)


st.title(tr("title", L))
st.info(tr("live_intro", L), icon="⚡")

# ---------------- sidebar ----------------
with st.sidebar:
    st.header(tr("settings", L))
    # Dropdowns are keyed per language (Streamlit keeps the old option label otherwise); the choice itself
    # lives in a separate session key, so switching language keeps it.
    current = st.session_state.get("preset", PRESETS[0])
    name = st.selectbox(tr("model", L), PRESETS, index=PRESETS.index(current), key=f"preset_{L}",
                        format_func=lambda n: tr(f"preset_{n}", L))
    st.session_state["preset"] = name
    base = load_preset(name)
    unit = base.display_unit
    s = UNIT_SCALE[unit]
    res = {k: v for k, v in RESOLUTION[name].items() if v[2] <= MAX_VOXELS}  # a shared server may hide the largest
    strides = list(res)
    current = st.session_state.get(f"res_{name}", strides[0])
    current = current if current in strides else strides[0]
    stride = st.selectbox(tr("voxel_size", L), strides, index=strides.index(current), key=f"res_{name}_{L}",
                          format_func=lambda k: tr(res[k][0], L, size=res[k][1]) if res[k][0] else res[k][1])
    st.session_state[f"res_{name}"] = stride
    photons = st.select_slider(tr("photons", L), options=PHOTON_OPTIONS, format_func=fmt_count,
                               value=20_000 if name == "knee_980nm" else 50_000, key=f"n_{name}",
                               help=tr("photons_help", L))
    rate = photon_rate(name, stride)
    if photons >= 1_000_000:
        st.caption(tr("eta", L, t=fmt_duration(photons / rate, L)) if rate else tr("eta_unknown", L))
    seed = st.number_input(tr("seed", L), min_value=0, max_value=2**31 - 1, value=1, step=1, key=f"seed_{name}")
    st.subheader(tr("source", L))
    diameter = st.number_input(tr("diameter", L, unit=unit), min_value=0.01,
                               value=float(base.source.diameter * s), step=0.5 if unit == "cm" else 0.1,
                               key=f"d_{name}")
    theta = st.slider(tr("theta", L), 0.0, 80.0, 0.0, 1.0, key=f"theta_{name}")
    phi_deg = st.slider(tr("phi", L), 0.0, 360.0, 0.0, 5.0, key=f"phi_{name}", disabled=theta == 0)
    has_power = st.checkbox(tr("has_power", L), value=base.source.power_w is not None, key=f"hp_{name}")
    power = st.number_input(tr("power", L), min_value=0.0001, value=float(base.source.power_w or 0.1),
                            key=f"p_{name}", disabled=not has_power) if has_power else None
    run_clicked = st.button(tr("run", L), type="primary", use_container_width=True)

params = (name, stride, int(photons), int(seed), float(theta), float(phi_deg), float(diameter / s),
          float(power) if power else None)
if run_clicked or st.session_state.get("last_params") is None or st.session_state.get("last_name") != name:
    st.session_state["last_params"] = params
    st.session_state["last_name"] = name
active = st.session_state["last_params"]
stale = active != params

st.caption(tr("caption", L, title=preset_title(base, L), based_on=base.based_on, unit=unit))

try:
    result = run_with_bar(L, *active)
except ValueError as exc:
    st.error(tr("param_error", L, error=exc))
    st.stop()

if stale:
    st.info(tr("stale", L))

e = result.energy
items = [("absorbed", "m_absorbed"), ("reflected", "m_reflected"), ("side", "m_side"),
         ("transmitted", "m_transmitted"), ("specular", "m_specular")]
row1, row2 = st.columns(3), st.columns(3)
for c, (k, label) in zip(list(row1) + list(row2), items):
    c.metric(tr(label, L), f"{e[k] * 100:.2f}%")
row2[2].metric(tr("m_total", L), f"{e['bookkeeping'] * 100:.2f}%", help=tr("m_total_help", L))
st.caption(tr("run_caption", L, balance=f"{e['bookkeeping']:.12f}", n=f"{result.n_photons:,}",
              seed=result.preset.run.seed, secs=f"{result.elapsed_s:.1f}", workers=result.workers,
              voxel=f"{result.volume.voxel[0] * s:g}", unit=unit, shape=result.volume.shape))

tab_model, tab_light, tab_dose, tab_export = st.tabs(
    [tr("tab_model", L), tr("tab_light", L), tr("tab_dose", L), tr("tab_export", L)])

with tab_model:
    preset_v, vol = volume_cached(name, stride)
    st.plotly_chart(tissue_section(vol, preset_v, lang=L), use_container_width=True)
    st.markdown(f"**{tr('optics', L)}**")
    rows = []
    for t in preset_v.tissues:
        rows.append({tr("col_tissue", L): tissue_name(t, L), f"μa [1/{unit}]": round(t.mua / s, 4),
                     f"μs′ [1/{unit}]": round(t.mus * (1 - t.g) / s, 4), "g": t.g, "n": t.n,
                     tr("col_source", L): tissue_source(t, L)})
    st.dataframe(rows, hide_index=True, use_container_width=True)
    notes = preset_notes(preset_v, L)
    if notes:
        with st.expander(tr("notes", L), expanded=True):
            for note in notes:
                st.markdown(f"- {note}")

with tab_light:
    yv = st.slider(tr("section_y", L, unit=unit), float(result.volume.centers(1).min() * s),
                   float(result.volume.centers(1).max() * s), 0.0, key=f"y_{name}")
    st.plotly_chart(fluence_section(result, y_mm=yv / s, power_w=result.power_w, lang=L), use_container_width=True)
    depth, prof = axis_profile(result)
    st.plotly_chart(axis_profile_figure(depth, prof, unit, result.power_w, lang=L), use_container_width=True)
    st.caption(tr("light_caption", L))

with tab_dose:
    if result.power_w is None:
        st.info(tr("dose_needs_power", L))
    else:
        d = DOSE_DEFAULTS[name]
        c1, c2, c3 = st.columns(3)
        depths_txt = c1.text_input(tr("depths", L, unit=unit), d["depths"], key=f"dd_{name}")
        exposure = c2.number_input(tr("exposure", L), min_value=1.0, value=d["exposure"], key=f"de_{name}")
        radius = c3.number_input(tr("radius", L, unit=unit), min_value=0.01, value=d["radius"], key=f"dr_{name}")
        try:
            depths = [float(x) for x in depths_txt.replace("，", ",").split(",") if x.strip()]
            rows = dose_table(result, [x / s for x in depths], exposure, radius / s)
        except ValueError as exc:
            st.error(str(exc))
            rows = []
        if rows:
            st.plotly_chart(dose_figure(rows, unit, exposure, lang=L), use_container_width=True)
            table = [{tr("col_depth", L, unit=unit): r.depth_mm * s,
                      tr("col_axis_h", L): round(r.axis_H_j_cm2, 4),
                      tr("col_disk_h", L): round(r.disk_mean_H_j_cm2, 4),
                      tr("col_disk_e", L): round(r.disk_energy_j, 4),
                      tr("col_share", L): f"{r.disk_energy_fraction:.2%}",
                      tr("col_air", L): tr("yes", L) if r.disk_has_air else ""}
                     for r in rows]
            st.dataframe(table, hide_index=True, use_container_width=True)
            st.caption(tr("dose_caption", L, z=f"{skin_surface_on_axis(result.volume) * s:.2f}", unit=unit))
            st.session_state["dose_rows"] = table

with tab_export:
    buf = io.BytesIO()
    np.savez_compressed(buf, labels=result.volume.labels, A=result.A, phi=result.phi, R2=result.R2, T2=result.T2,
                        meta=np.array(json.dumps({"preset": result.preset.to_dict(), "energy": result.energy},
                                                 ensure_ascii=False)))
    st.download_button(tr("dl_npz", L), buf.getvalue(), file_name=f"{name}_results.npz")
    cfg = json.dumps(result.preset.to_dict(), ensure_ascii=False, indent=2)
    st.download_button(tr("dl_json", L), cfg, file_name=f"{name}_config.json")
    if st.session_state.get("dose_rows"):
        import csv

        out = io.StringIO()
        w = csv.DictWriter(out, fieldnames=list(st.session_state["dose_rows"][0]))
        w.writeheader()
        w.writerows(st.session_state["dose_rows"])
        st.download_button(tr("dl_csv", L), out.getvalue().encode("utf-8-sig"), file_name=f"{name}_dose.csv")
    st.caption(tr("export_caption", L))
