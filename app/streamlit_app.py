"""交互界面：uv run streamlit run app/streamlit_app.py"""

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
from mcsim.plotting import (  # noqa: E402
    UNIT_SCALE, axis_profile_figure, dose_figure, fluence_section, tissue_section,
)

st.set_page_config(page_title="蒙特卡洛光传输仿真", layout="wide")

PRESETS = {"膝关节 · 980 nm": "knee_980nm", "皮肤血管 · 500 nm": "skin_500nm"}
RESOLUTION = {
    "knee_980nm": {"1.25 mm（原模型）": 1, "2.5 mm（更快）": 2},
    "skin_500nm": {"40 μm（推荐）": 4, "20 μm": 2, "100 μm（与 MATLAB 粗网格相同）": 10,
                   "10 μm（原模型，较慢，约 2 GB 内存）": 1},
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


# ---------------- sidebar ----------------
with st.sidebar:
    st.header("模拟设置")
    preset_label = st.selectbox("模型", list(PRESETS), key="preset")
    name = PRESETS[preset_label]
    base = load_preset(name)
    unit = base.display_unit
    s = UNIT_SCALE[unit]
    res_label = st.selectbox("体素大小", list(RESOLUTION[name]), key=f"res_{name}")
    stride = RESOLUTION[name][res_label]
    photons = st.select_slider("光子数", options=[2_000, 5_000, 10_000, 20_000, 50_000, 100_000, 200_000, 500_000],
                               value=20_000 if name == "knee_980nm" else 50_000, key=f"n_{name}")
    seed = st.number_input("随机种子", min_value=0, max_value=2**31 - 1, value=1, step=1, key=f"seed_{name}")
    st.subheader("光源")
    diameter = st.number_input(f"光斑直径 [{unit}]", min_value=0.01,
                               value=float(base.source.diameter * s), step=0.5 if unit == "cm" else 0.1,
                               key=f"d_{name}")
    theta = st.slider("入射角 θ [°]（0 = 垂直）", 0.0, 80.0, 0.0, 1.0, key=f"theta_{name}")
    phi_deg = st.slider("方位角 φ [°]", 0.0, 360.0, 0.0, 5.0, key=f"phi_{name}", disabled=theta == 0)
    has_power = st.checkbox("设定总功率（用于剂量）", value=base.source.power_w is not None, key=f"hp_{name}")
    power = st.number_input("总功率 [W]", min_value=0.0001, value=float(base.source.power_w or 0.1),
                            key=f"p_{name}", disabled=not has_power) if has_power else None
    run_clicked = st.button("开始模拟", type="primary", use_container_width=True)

params = (name, stride, int(photons), int(seed), float(theta), float(phi_deg), float(diameter / s),
          float(power) if power else None)
if run_clicked or st.session_state.get("last_params") is None or st.session_state.get("last_name") != name:
    st.session_state["last_params"] = params
    st.session_state["last_name"] = name
active = st.session_state["last_params"]
stale = active != params

# ---------------- header ----------------
st.title("蒙特卡洛光传输仿真")
st.caption(f"{base.title} · 基于 {base.based_on} 移植 · 长度单位 {unit}")

try:
    with st.spinner("正在模拟……第一次运行需要编译，约 10 秒"):
        result = run_cached(*active)
except ValueError as exc:
    st.error(f"参数有问题：{exc}")
    st.stop()

if stale:
    st.info("左侧设置已修改，点「开始模拟」用新设置重新计算。下面仍是上一次的结果。")

e = result.energy
items = [("absorbed", "组织吸收"), ("reflected", "从表面反射"), ("side", "从侧面离开"),
         ("transmitted", "从底部透射"), ("specular", "镜面反射")]
row1, row2 = st.columns(3), st.columns(3)
for c, (k, label) in zip(list(row1) + list(row2), items):
    c.metric(label, f"{e[k] * 100:.2f}%")
row2[2].metric("合计", f"{e['bookkeeping'] * 100:.2f}%", help="能量守恒自检：包含轮盘赌修正后应等于 100%")
st.caption(f"能量收支 {e['bookkeeping']:.12f} · {result.n_photons:,} 个光子 · 种子 {result.preset.run.seed} · 用时 {result.elapsed_s:.1f} s · "
           f"{result.workers} 路并行 · 体素 {result.volume.voxel[0] * s:g} {unit} · 网格 {result.volume.shape}")

tab_model, tab_light, tab_dose, tab_export = st.tabs(["组织模型", "光分布", "剂量", "导出"])

with tab_model:
    preset_v, vol = volume_cached(name, stride)
    st.plotly_chart(tissue_section(vol, preset_v), use_container_width=True)
    st.markdown("**光学参数**")
    rows = []
    for t in preset_v.tissues:
        rows.append({"组织": t.name, f"μa [1/{unit}]": round(t.mua / s, 4),
                     f"μs′ [1/{unit}]": round(t.mus * (1 - t.g) / s, 4), "g": t.g, "n": t.n, "来源": t.source})
    st.dataframe(rows, hide_index=True, use_container_width=True)
    if preset_v.notes:
        with st.expander("注意事项", expanded=True):
            for note in preset_v.notes:
                st.markdown(f"- {note}")

with tab_light:
    yv = st.slider(f"截面位置 y [{unit}]", float(result.volume.centers(1).min() * s),
                   float(result.volume.centers(1).max() * s), 0.0, key=f"y_{name}")
    st.plotly_chart(fluence_section(result, y_mm=yv / s, power_w=result.power_w), use_container_width=True)
    depth, prof = axis_profile(result)
    st.plotly_chart(axis_profile_figure(depth, prof, unit, result.power_w), use_container_width=True)
    st.caption("白线是组织分界。颜色是对数刻度：每差 1 就是 10 倍。光子数少时深处会出现噪点，可增加光子数。")

with tab_dose:
    if result.power_w is None:
        st.info("剂量需要总功率。在左侧勾选「设定总功率」后重新模拟。")
    else:
        d = DOSE_DEFAULTS[name]
        c1, c2, c3 = st.columns(3)
        depths_txt = c1.text_input(f"皮下深度 [{unit}]，逗号分隔", d["depths"], key=f"dd_{name}")
        exposure = c2.number_input("照射时间 [s]", min_value=1.0, value=d["exposure"], key=f"de_{name}")
        radius = c3.number_input(f"圆面半径 [{unit}]", min_value=0.01, value=d["radius"], key=f"dr_{name}")
        try:
            depths = [float(x) for x in depths_txt.replace("，", ",").split(",") if x.strip()]
            rows = dose_table(result, [x / s for x in depths], exposure, radius / s)
        except ValueError as exc:
            st.error(str(exc))
            rows = []
        if rows:
            st.plotly_chart(dose_figure(rows, unit, exposure), use_container_width=True)
            table = [{f"皮下深度 [{unit}]": r.depth_mm * s, "中心轴 H [J/cm²]": round(r.axis_H_j_cm2, 4),
                      "圆面平均 H [J/cm²]": round(r.disk_mean_H_j_cm2, 4), "圆面能量 [J]": round(r.disk_energy_j, 4),
                      "占总能量": f"{r.disk_energy_fraction:.2%}", "圆面含空气": "是" if r.disk_has_air else ""}
                     for r in rows]
            st.dataframe(table, hide_index=True, use_container_width=True)
            st.caption(f"皮肤表面（中心轴）在 z = {skin_surface_on_axis(result.volume) * s:.2f} {unit}。"
                       "H = 光注量率 × 照射时间，是到达该处的光，不是被吸收的能量。模型和参数是简化值，不代表真实患者剂量。")
            st.session_state["dose_rows"] = table

with tab_export:
    buf = io.BytesIO()
    np.savez_compressed(buf, labels=result.volume.labels, A=result.A, phi=result.phi, R2=result.R2, T2=result.T2,
                        meta=np.array(json.dumps({"preset": result.preset.to_dict(), "energy": result.energy},
                                                 ensure_ascii=False)))
    st.download_button("下载结果数据（.npz）", buf.getvalue(), file_name=f"{name}_results.npz")
    cfg = json.dumps(result.preset.to_dict(), ensure_ascii=False, indent=2)
    st.download_button("下载本次运行的完整参数（.json，可复现）", cfg, file_name=f"{name}_config.json")
    if st.session_state.get("dose_rows"):
        import csv

        out = io.StringIO()
        w = csv.DictWriter(out, fieldnames=list(st.session_state["dose_rows"][0]))
        w.writeheader()
        w.writerows(st.session_state["dose_rows"])
        st.download_button("下载剂量表（.csv）", out.getvalue().encode("utf-8-sig"), file_name=f"{name}_dose.csv")
    st.caption("所有长度在 .npz 里以 mm 为单位；A 单位 1/mm³，phi 单位 1/mm²，均按每单位入射能量归一化。")
