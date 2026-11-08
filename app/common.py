"""Helpers shared by the app's pages: current language, content files, private notes, cached runs."""

from __future__ import annotations

import os
import time
from pathlib import Path

import streamlit as st
import yaml

from mcsim import load_preset, simulate
from mcsim.runner import BusyError

APP = Path(__file__).resolve().parent
ROOT = APP.parent
CONTENT = APP / "content"
PRIVATE = ROOT / "project" / "private" / "app"  # git-ignored: present only on computers that have the private files


def lang() -> str:
    return st.session_state.get("lang", "zh")


def content(name: str, language: str) -> str:
    """Markdown from app/content/<name>.<zh|en>.md."""
    return (CONTENT / f"{name}.{language}.md").read_text(encoding="utf-8")


def private_content(name: str, language: str) -> str | None:
    """Markdown from project/private/app/<name>.<lang>.md, or None when this computer does not have it."""
    path = PRIVATE / f"{name}.{language}.md"
    return path.read_text(encoding="utf-8") if path.exists() else None


def papers() -> dict:
    return yaml.safe_load((CONTENT / "papers.yaml").read_text(encoding="utf-8"))


# Photon counts offered in the app. Published work typically uses 10^6-10^8; the error falls as 1/sqrt(N).
# A shared server can lower the ceiling with MCSIM_MAX_PHOTONS (one run at a time, so long runs make others wait).
MAX_PHOTONS = int(float(os.environ.get("MCSIM_MAX_PHOTONS", "1e8")))
PHOTON_OPTIONS = [n for n in (10_000, 20_000, 50_000, 100_000, 200_000, 500_000, 1_000_000, 2_000_000, 5_000_000,
                              10_000_000, 20_000_000, 50_000_000, 100_000_000) if n <= MAX_PHOTONS]
# Full 3-D results are large (the finest skin grid is ~2.5 GB each). A server shared with other services can
# keep fewer (MCSIM_MAX_KEPT_RESULTS) and hide the largest grids (MCSIM_MAX_VOXELS).
MAX_KEPT_RESULTS = int(os.environ.get("MCSIM_MAX_KEPT_RESULTS", "4"))
MAX_VOXELS = int(float(os.environ.get("MCSIM_MAX_VOXELS", "1e12")))
SUPERSCRIPT = str.maketrans("0123456789", "⁰¹²³⁴⁵⁶⁷⁸⁹")


def fmt_count(n: int) -> str:
    """50,000 · 10⁶ · 2×10⁷: powers of ten from a million up, so large counts stay readable."""
    if n < 1_000_000:
        return f"{n:,}"
    exp = len(str(n)) - 1
    lead = n // 10**exp
    if lead * 10**exp != n:
        return f"{n:,}"
    power = "10" + str(exp).translate(SUPERSCRIPT)
    return power if lead == 1 else f"{lead}×{power}"


def fmt_duration(seconds: float, language: str) -> str:
    from mcsim.i18n import tr

    if seconds < 90:
        return tr("dur_s", language, n=max(1, round(seconds)))
    if seconds < 90 * 60:
        return tr("dur_min", language, n=round(seconds / 60))
    return tr("dur_h", language, n=f"{seconds / 3600:.1f}")


@st.cache_resource(show_spinner=False)
def _shared() -> dict:
    """Shared by every visitor of this server: recent results and the measured speed of each model."""
    return {"results": {}, "rates": {}}


def photon_rate(name: str, stride: int) -> float | None:
    """Photons per second measured on this machine for this model and voxel size, if it has run before."""
    return _shared()["rates"].get((name, stride))


def run_cached(name: str, stride: int, photons: int, seed: int, theta: float, phi: float,
               diameter_mm: float, power_w: float | None, progress=None):
    """Run a preset (or reuse an identical recent run). ``progress(done, total)`` is called after each wave;
    it is not cached, so a long run can show a progress bar and be stopped between waves."""
    key = (name, stride, photons, seed, theta, phi, diameter_mm, power_w)
    store = _shared()
    results = store["results"]
    if key in results:
        results[key] = results.pop(key)  # most recently used goes last
        return results[key]
    preset = load_preset(name, photons=photons, seed=seed, stride=stride, theta_deg=theta, phi_deg=phi,
                         diameter=diameter_mm)
    preset.source.power_w = power_w  # None = no power set: results stay per unit power
    marks = []  # (time, photons done) after each wave

    def tracked(done: int, total: int) -> None:
        marks.append((time.perf_counter(), done))
        if progress is not None:
            progress(done, total)

    result = simulate(preset, workers=0, progress=tracked)
    rate_key = (name, stride)
    if len(marks) >= 2:  # speed between waves: includes merging, excludes set-up and loading the kernel
        (t0, d0), (t1, d1) = marks[0], marks[-1]
        store["rates"][rate_key] = (d1 - d0) / (t1 - t0)
    elif rate_key not in store["rates"] and result.elapsed_s > 0:
        store["rates"][rate_key] = photons / result.elapsed_s  # rough (one wave, set-up included) until a longer run
    results[key] = result
    while len(results) > MAX_KEPT_RESULTS:
        results.pop(next(iter(results)))
    return result


def live_note(language: str, finished_at: float, started_at: float, n: int, secs: float, again: str) -> None:
    """Say where the result on screen comes from: computed just now, by this visitor earlier, or reused from an
    identical recent run (same settings and seed give a bit-identical result). ``again`` is the i18n key that
    says what to change for a new run."""
    from mcsim.i18n import tr

    own = st.session_state.setdefault("own_runs", set())
    values = dict(n=fmt_count(n), secs=f"{secs:.1f}", ago=fmt_duration(time.time() - finished_at, language))
    if finished_at >= started_at:
        own.add(finished_at)
        st.caption(tr("live_done", language, **values))
    elif finished_at in own:
        st.caption(tr("live_done_earlier", language, **values))
    else:
        st.caption(tr("live_reused", language, again=tr(again, language), **values))


def run_with_bar(language: str, *params, again: str = "again_seed"):
    """run_cached() with a progress bar and the time left, then the note saying it was computed live."""
    from mcsim.i18n import tr

    bar = st.progress(0.0, text=tr("spinner", language))
    t0 = time.perf_counter()
    started_at = time.time()

    def show(done: int, total: int) -> None:
        left = (time.perf_counter() - t0) * (total - done) / max(done, 1)
        bar.progress(done / total, text=tr("progress", language, done=fmt_count(done), total=fmt_count(total),
                                           eta=fmt_duration(left, language)))

    try:
        result = run_cached(*params, progress=show)
    except BusyError:
        bar.empty()
        busy_and_stop(language)
    finally:
        bar.empty()
    live_note(language, result.finished_at, started_at, result.n_photons, result.elapsed_s, again)
    return result


def busy_and_stop(language: str):
    """Another visitor's run is still going on this server: say so and stop this page."""
    from mcsim.i18n import tr

    st.warning(tr("busy", language))
    st.stop()
