"""The app's look, matching joulezmed.com: logo, stylesheet, page banner with the photon mascot, footer.

Colours and the theme itself live in .streamlit/config.toml; this file adds what the theme cannot express.
"""

from __future__ import annotations

import base64
from pathlib import Path

import streamlit as st

from art import scene

ASSETS = Path(__file__).resolve().parent / "assets"
LOGO_ON_DARK = ASSETS / "logo-light.png"
LOGO_MARK = ASSETS / "logo-mark.png"
SITE = "https://joulezmed.com"

# Concentric wavefronts, as in the hero of joulezmed.com, behind every page banner.
_RINGS = (
    '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 600 600" fill="none">'
    + "".join(f'<circle cx="300" cy="300" r="{r}" stroke="#00AADD" stroke-opacity="{0.2 - i * 0.04:.2f}"/>'
              for i, r in enumerate((110, 180, 250)))
    + "</svg>"
)
RINGS_URI = "data:image/svg+xml;base64," + base64.b64encode(_RINGS.encode()).decode()

CSS = f"""
h1, h2, h3 {{ letter-spacing: -0.025em; }}

/* Page banner: navy light field with the page's illustration */
.st-key-jz-banner {{
  background: url("{RINGS_URI}") right -150px top -170px / 560px no-repeat,
              radial-gradient(120% 130% at 85% 10%, #0d2a6b 0%, #081842 45%, #06102b 100%);
  border-radius: 20px;
  padding: 1.6rem 2rem 1.2rem;
  margin-bottom: 0.6rem;
  box-shadow: 0 24px 60px -34px rgba(13, 36, 114, 0.55);
}}
.st-key-jz-banner h1 {{ color: #fff; font-size: 2.1rem; line-height: 1.2; padding-bottom: 0.4rem; }}
.st-key-jz-banner p {{ color: rgba(255, 255, 255, 0.72); font-size: 1.05rem; line-height: 1.6; max-width: 34em; }}
.st-key-jz-banner [data-testid="stImage"] img {{ max-height: 210px; width: auto; margin-left: auto; }}
.st-key-jz-banner [data-testid="stElementToolbar"] {{ display: none; }}
@media (max-width: 640px) {{
  .st-key-jz-banner {{ padding: 1.2rem 1.1rem 0.8rem; }}
  .st-key-jz-banner [data-testid="stHorizontalBlock"] {{ gap: 0.25rem; }}
  .st-key-jz-banner h1 {{ font-size: 1.55rem; }}
  .st-key-jz-banner [data-testid="stImage"] img {{ max-height: 150px; margin: 0 auto; }}
}}

/* Metrics read as small cards */
[data-testid="stMetric"] {{
  background: #fff;
  border: 1px solid #e7ebf3;
  border-radius: 14px;
  padding: 0.75rem 1rem;
}}
[data-testid="stMetricValue"] {{ color: #0d2472; font-weight: 800; }}

/* Primary actions carry the brand-blue glow used on the website */
[data-testid="stBaseButton-primary"] {{
  box-shadow: 0 12px 28px -14px rgba(16, 64, 193, 0.75);
  font-weight: 600;
}}

/* Logo in the navy sidebar */
[data-testid="stSidebarHeader"] img, [data-testid="stHeaderLogo"] {{ height: 2.1rem; }}

.jz-footer {{
  margin-top: 3rem;
  padding-top: 1rem;
  border-top: 1px solid #e7ebf3;
  color: #475569;
  font-size: 0.85rem;
}}
.jz-footer a {{ color: #1040c1; text-decoration: none; }}
"""


def apply() -> None:
    """Logo (links to the website) and stylesheet; call once at the top of every run."""
    st.logo(str(LOGO_ON_DARK), link=SITE, icon_image=str(LOGO_MARK), size="large")
    st.html(f"<style>{CSS}</style>")


def banner(title: str, subtitle: str, art: str) -> None:
    """The page header: title and one line on the left, the page's illustration (art.SCENES) on the right."""
    with st.container(key="jz-banner"):
        text, picture = st.columns([3, 2], vertical_alignment="center", gap="large")
        with text:
            st.title(title, anchor=False)
            st.markdown(subtitle)
        with picture:
            st.image(scene(art), width="stretch")


def footer(text: str) -> None:
    st.html(f'<div class="jz-footer">{text}</div>')
