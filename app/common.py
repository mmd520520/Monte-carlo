"""Helpers shared by the app's pages: current language, content files, private notes, cached runs."""

from __future__ import annotations

from pathlib import Path

import streamlit as st
import yaml

from mcsim import load_preset, simulate

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


@st.cache_resource(show_spinner=False, max_entries=8)
def run_cached(name: str, stride: int, photons: int, seed: int, theta: float, phi: float,
               diameter_mm: float, power_w: float | None):
    preset = load_preset(name, photons=photons, seed=seed, stride=stride, theta_deg=theta, phi_deg=phi,
                         diameter=diameter_mm)
    preset.source.power_w = power_w  # None = no power set: results stay per unit power
    return simulate(preset, workers=0)
