"""Plotly figures for the app and notebooks. Coordinates are shown in the preset's display unit.

Every function takes ``lang`` ("zh" or "en") for its labels; text lives in ``mcsim.i18n``.
"""

from __future__ import annotations

import numpy as np
import plotly.graph_objects as go

from mcsim.config import Preset
from mcsim.geometry import Volume
from mcsim.i18n import tissue_name, tr
from mcsim.results import SimulationResult

UNIT_SCALE = {"mm": 1.0, "cm": 0.1}  # mm -> display unit

# Same colours as the MATLAB figures (2demo Tissue.m, 5demo Tissue_knee.m), keyed by the preset's tissue name.
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


def _layout(fig: go.Figure, title: str, unit: str, x: np.ndarray, z: np.ndarray, lang: str, height: int = 460) -> go.Figure:
    fig.update_layout(
        title=dict(text=title, x=0, font=dict(size=15)), font=FONT, height=height,
        margin=dict(l=10, r=10, t=50, b=10), plot_bgcolor="white",
    )
    # constrain="domain": keep 1:1 aspect by shrinking the plot area, never by padding the axis range
    dx, dz = (x[1] - x[0]) / 2, (z[1] - z[0]) / 2
    fig.update_xaxes(title=f"x [{unit}]", showgrid=False, zeroline=False, constrain="domain",
                     range=[x[0] - dx, x[-1] + dx])
    fig.update_yaxes(title=tr("fig_depth_z", lang, unit=unit), showgrid=False, zeroline=False, scaleanchor="x",
                     scaleratio=1, constrain="domain", range=[z[-1] + dz, z[0] - dz])  # reversed: depth grows downwards
    return fig


def tissue_section(volume: Volume, preset: Preset, y_mm: float = 0.0, lang: str = "zh") -> go.Figure:
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
    shown = [tissue_name(t, lang) for t in present]
    names = np.vectorize(lambda v: shown[int(v)])(mapped)
    fig = go.Figure(go.Heatmap(
        x=x, y=z, z=mapped, zmin=-0.5, zmax=k - 0.5, colorscale=scale, customdata=names,
        hovertemplate=f"x %{{x:.2f}} {unit}<br>z %{{y:.2f}} {unit}<br>%{{customdata}}<extra></extra>",
        colorbar=dict(tickvals=list(range(k)), ticktext=shown, title=tr("fig_tissue_bar", lang)),
    ))
    y_shown = f"{volume.centers(1)[j] * UNIT_SCALE[unit]:.2f}"
    return _layout(fig, tr("fig_tissue_title", lang, y=y_shown, unit=unit), unit, x, z, lang)


def fluence_section(result: SimulationResult, y_mm: float = 0.0, power_w: float | None = None,
                    decades: float = 5.0, lang: str = "zh") -> go.Figure:
    v, preset = result.volume, result.preset
    unit = preset.display_unit
    x, _, z = _axes(v, unit)
    j = _y_index(v, y_mm)
    field = result.phi[:, j, :].T
    if power_w:
        field = field * power_w * 100.0
        label = tr("fig_fluence_rate", lang)
    else:
        label = tr("fig_fluence", lang)
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
    y_shown = f"{v.centers(1)[j] * UNIT_SCALE[unit]:.2f}"
    return _layout(fig, tr("fig_light_title", lang, y=y_shown, unit=unit), unit, x, z, lang)


def axis_profile_figure(depth_mm: np.ndarray, phi: np.ndarray, unit: str, power_w: float | None = None,
                        lang: str = "zh") -> go.Figure:
    s = UNIT_SCALE[unit]
    yv = phi * power_w * 100.0 if power_w else phi
    ylab = tr("fig_fluence_rate", lang) if power_w else tr("fig_fluence", lang)
    fig = go.Figure(go.Scatter(x=depth_mm * s, y=yv, mode="lines", line=dict(color="#1040C1", width=2),
                               hovertemplate=f"{tr('fig_hover_depth', lang)} %{{x:.2f}} {unit}<br>%{{y:.3g}}<extra></extra>"))
    fig.update_layout(title=dict(text=tr("fig_axis_title", lang), x=0, font=dict(size=15)), font=FONT,
                      height=360, margin=dict(l=10, r=10, t=50, b=10), plot_bgcolor="white")
    fig.update_xaxes(title=tr("fig_depth_below", lang, unit=unit), gridcolor="#E7EBF3")
    fig.update_yaxes(title=ylab, type="log", gridcolor="#E7EBF3")
    return fig


def dose_figure(rows, unit: str, exposure_s: float, lang: str = "zh") -> go.Figure:
    s = UNIT_SCALE[unit]
    d = [r.depth_mm * s for r in rows]
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=d, y=[r.axis_H_j_cm2 for r in rows], name=tr("fig_on_axis", lang), mode="lines+markers",
                             line=dict(color="#1040C1", width=2)))
    fig.add_trace(go.Scatter(x=d, y=[r.disk_mean_H_j_cm2 for r in rows], name=tr("fig_disk_mean", lang), mode="lines+markers",
                             line=dict(color="#0D2472", width=2, dash="dash")))
    fig.update_layout(title=dict(text=tr("fig_dose_title", lang, t=f"{exposure_s:g}"), x=0, font=dict(size=15)),
                      font=FONT, height=380, margin=dict(l=10, r=10, t=50, b=10), plot_bgcolor="white",
                      legend=dict(orientation="h", y=1.02, x=1, xanchor="right", yanchor="bottom"))
    fig.update_xaxes(title=tr("fig_depth_below", lang, unit=unit), gridcolor="#E7EBF3")
    fig.update_yaxes(title="H [J/cm²]", type="log", gridcolor="#E7EBF3")
    return fig
