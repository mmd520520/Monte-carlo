"""Plotly figures for the app and notebooks. Coordinates are shown in the preset's display unit."""

from __future__ import annotations

import numpy as np
import plotly.graph_objects as go

from mcsim.config import Preset
from mcsim.geometry import Volume
from mcsim.results import SimulationResult

UNIT_SCALE = {"mm": 1.0, "cm": 0.1}  # mm -> display unit

# Same colours as the MATLAB figures (2demo Tissue.m, 5demo Tissue_knee.m).
TISSUE_COLORS = {
    "空气": "#F7F7F5",
    "表皮": "#B8A885",
    "真皮": "#EDC9C4",
    "血液": "#E60000",
    "软组织": "#1ABFED",
    "髌骨": "#FFD40D",
    "骨": "#FA4752",
}
FONT = dict(family="PingFang SC, Microsoft YaHei, Noto Sans SC, sans-serif", size=13)


def _axes(volume: Volume, unit: str):
    s = UNIT_SCALE[unit]
    return volume.centers(0) * s, volume.centers(1) * s, volume.centers(2) * s


def _y_index(volume: Volume, y_mm: float) -> int:
    return int(np.argmin(np.abs(volume.centers(1) - y_mm)))


def _layout(fig: go.Figure, title: str, unit: str, x: np.ndarray, z: np.ndarray, height: int = 460) -> go.Figure:
    fig.update_layout(
        title=dict(text=title, x=0, font=dict(size=15)), font=FONT, height=height,
        margin=dict(l=10, r=10, t=50, b=10), plot_bgcolor="white",
    )
    # constrain="domain": keep 1:1 aspect by shrinking the plot area, never by padding the axis range
    dx, dz = (x[1] - x[0]) / 2, (z[1] - z[0]) / 2
    fig.update_xaxes(title=f"x [{unit}]", showgrid=False, zeroline=False, constrain="domain",
                     range=[x[0] - dx, x[-1] + dx])
    fig.update_yaxes(title=f"深度 z [{unit}]", showgrid=False, zeroline=False, scaleanchor="x", scaleratio=1,
                     constrain="domain", range=[z[-1] + dz, z[0] - dz])  # reversed: depth grows downwards
    return fig


def tissue_section(volume: Volume, preset: Preset, y_mm: float = 0.0) -> go.Figure:
    unit = preset.display_unit
    x, _, z = _axes(volume, unit)
    j = _y_index(volume, y_mm)
    sec = volume.labels[:, j, :].T  # (z, x)
    present = [t for t in preset.tissues if np.any(volume.labels == t.label)]
    index = {t.label: i for i, t in enumerate(present)}
    mapped = np.vectorize(index.get)(sec).astype(float)
    k = len(present)
    scale = []
    for i, t in enumerate(present):
        c = TISSUE_COLORS.get(t.name, "#999999")
        scale += [[i / k, c], [(i + 1) / k, c]]
    names = np.vectorize(lambda v: present[int(v)].name)(mapped)
    fig = go.Figure(go.Heatmap(
        x=x, y=z, z=mapped, zmin=-0.5, zmax=k - 0.5, colorscale=scale, customdata=names,
        hovertemplate=f"x %{{x:.2f}} {unit}<br>z %{{y:.2f}} {unit}<br>%{{customdata}}<extra></extra>",
        colorbar=dict(tickvals=list(range(k)), ticktext=[t.name for t in present], title="组织"),
    ))
    return _layout(fig, f"组织模型：y = {volume.centers(1)[j] * UNIT_SCALE[unit]:.2f} {unit} 截面", unit, x, z)


def fluence_section(result: SimulationResult, y_mm: float = 0.0, power_w: float | None = None,
                    decades: float = 5.0) -> go.Figure:
    v, preset = result.volume, result.preset
    unit = preset.display_unit
    x, _, z = _axes(v, unit)
    j = _y_index(v, y_mm)
    field = result.phi[:, j, :].T
    if power_w:
        field = field * power_w * 100.0
        label = "光注量率 [W/cm²]"
    else:
        label = "光注量 [1/mm²，每单位入射能量]"
    with np.errstate(divide="ignore", invalid="ignore"):
        logf = np.where(field > 0, np.log10(field), np.nan)
    top = np.nanmax(logf) if np.isfinite(logf).any() else 0.0
    fig = go.Figure(go.Heatmap(
        x=x, y=z, z=logf, zmin=top - decades, zmax=top, colorscale="Turbo",
        colorbar=dict(title=f"log₁₀ {label}"),
        hovertemplate=f"x %{{x:.2f}} {unit}<br>z %{{y:.2f}} {unit}<br>log₁₀ = %{{z:.2f}}<extra></extra>",
    ))
    labels = v.labels[:, j, :].T.astype(float)
    fig.add_trace(go.Contour(
        x=x, y=z, z=labels, showscale=False, hoverinfo="skip",
        contours=dict(start=1.5, end=float(labels.max()) - 0.5 if labels.max() > 1 else 1.5, size=1, coloring="none"),
        line=dict(color="white", width=1),
    ))
    return _layout(fig, f"光分布（对数色标）：y = {v.centers(1)[j] * UNIT_SCALE[unit]:.2f} {unit} 截面", unit, x, z)


def axis_profile_figure(depth_mm: np.ndarray, phi: np.ndarray, unit: str, power_w: float | None = None) -> go.Figure:
    s = UNIT_SCALE[unit]
    yv = phi * power_w * 100.0 if power_w else phi
    ylab = "光注量率 [W/cm²]" if power_w else "光注量 [1/mm²，每单位入射能量]"
    fig = go.Figure(go.Scatter(x=depth_mm * s, y=yv, mode="lines", line=dict(color="#A51C30", width=2),
                               hovertemplate=f"皮下 %{{x:.2f}} {unit}<br>%{{y:.3g}}<extra></extra>"))
    fig.update_layout(title=dict(text="光束中心轴上的光随深度衰减", x=0, font=dict(size=15)), font=FONT,
                      height=360, margin=dict(l=10, r=10, t=50, b=10), plot_bgcolor="white")
    fig.update_xaxes(title=f"皮下深度 [{unit}]", gridcolor="#E5E5E5")
    fig.update_yaxes(title=ylab, type="log", gridcolor="#E5E5E5")
    return fig


def dose_figure(rows, unit: str, exposure_s: float) -> go.Figure:
    s = UNIT_SCALE[unit]
    d = [r.depth_mm * s for r in rows]
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=d, y=[r.axis_H_j_cm2 for r in rows], name="中心轴", mode="lines+markers",
                             line=dict(color="#A51C30", width=2)))
    fig.add_trace(go.Scatter(x=d, y=[r.disk_mean_H_j_cm2 for r in rows], name="圆面平均", mode="lines+markers",
                             line=dict(color="#1B2A3A", width=2, dash="dash")))
    fig.update_layout(title=dict(text=f"累计光注量 H（照射 {exposure_s:g} s）", x=0, font=dict(size=15)),
                      font=FONT, height=380, margin=dict(l=10, r=10, t=50, b=10), plot_bgcolor="white",
                      legend=dict(orientation="h", y=1.02, x=1, xanchor="right", yanchor="bottom"))
    fig.update_xaxes(title=f"皮下深度 [{unit}]", gridcolor="#E5E5E5")
    fig.update_yaxes(title="H [J/cm²]", type="log", gridcolor="#E5E5E5")
    return fig
