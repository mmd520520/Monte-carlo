"""Page illustrations: the photon mascot (小光子 / Photon) and one small scene per page, as SVG.

Each scene is drawn for the navy page banner (brand.banner) on a 360 × 220 canvas, in the colours of
joulezmed.com. Plain SVG, no text inside, so the same picture works in both languages.
"""

from __future__ import annotations

NAVY = "#06102B"
BLUE = "#1040C1"
BLUE_MID = "#2C55C9"
CYAN = "#00AADD"
CYAN_BRIGHT = "#3FC7EC"
ICE = "#BDEFFC"
SKIN = "#FFE2CF"
HAIR = "#2B2238"
BLUSH = "#FF8FB1"

DEFS = f"""<defs>
<radialGradient id="body-cyan" cx="38%" cy="32%" r="75%"><stop offset="0" stop-color="#F4FDFF"/><stop offset=".42" stop-color="#8FE2F7"/><stop offset="1" stop-color="{CYAN}"/></radialGradient>
<radialGradient id="body-blue" cx="38%" cy="32%" r="75%"><stop offset="0" stop-color="#E6EDFF"/><stop offset=".42" stop-color="#7C9AF2"/><stop offset="1" stop-color="{BLUE}"/></radialGradient>
<radialGradient id="glow"><stop offset="0" stop-color="{CYAN_BRIGHT}" stop-opacity=".55"/><stop offset="1" stop-color="{CYAN_BRIGHT}" stop-opacity="0"/></radialGradient>
<linearGradient id="beam" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{CYAN_BRIGHT}" stop-opacity=".04"/><stop offset="1" stop-color="{CYAN_BRIGHT}" stop-opacity=".5"/></linearGradient>
<marker id="arrow" viewBox="0 0 10 10" refX="5" refY="5" markerWidth="4.5" markerHeight="4.5" orient="auto-start-reverse"><path d="M0 0 L10 5 L0 10 z" fill="{CYAN_BRIGHT}"/></marker>
<clipPath id="slab"><rect x="24" y="118" width="312" height="96" rx="18"/></clipPath>
</defs>"""


def _svg(body: str) -> str:
    return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 360 220" fill="none">{DEFS}{body}</svg>'


def photon(x: float, y: float, r: float = 22, mood: str = "happy", body: str = "cyan", glow: bool = True,
           glasses: bool = False) -> str:
    """The mascot. mood: happy (open eyes), joy (^ ^), calm (closed, peaceful), wow (open mouth)."""
    ex, ey = r * 0.34, -r * 0.06
    p = []
    if glow:
        p.append(f'<circle r="{r * 1.9:.1f}" fill="url(#glow)"/>')
    p.append(f'<circle r="{r}" fill="url(#body-{body})"/>')
    hx, hy = -r * 0.38, -r * 0.48
    p.append(f'<ellipse cx="{hx:.1f}" cy="{hy:.1f}" rx="{r * 0.26:.1f}" ry="{r * 0.15:.1f}" fill="#fff" '
             f'opacity=".75" transform="rotate(-30 {hx:.1f} {hy:.1f})"/>')
    w, sw = r * 0.13, r * 0.075
    for s in (-1, 1):
        cx = s * ex
        if mood == "joy":  # ^ ^
            p.append(f'<path d="M{cx - w:.1f} {ey + w * 0.4:.1f} Q{cx:.1f} {ey - w * 0.9:.1f} {cx + w:.1f} '
                     f'{ey + w * 0.4:.1f}" stroke="{NAVY}" stroke-width="{sw:.1f}" stroke-linecap="round"/>')
        elif mood == "calm":  # closed, curving down
            p.append(f'<path d="M{cx - w:.1f} {ey:.1f} Q{cx:.1f} {ey + w * 1.1:.1f} {cx + w:.1f} {ey:.1f}" '
                     f'stroke="{NAVY}" stroke-width="{sw:.1f}" stroke-linecap="round"/>')
        else:
            p.append(f'<ellipse cx="{cx:.1f}" cy="{ey:.1f}" rx="{r * 0.11:.1f}" ry="{r * 0.15:.1f}" fill="{NAVY}"/>')
            p.append(f'<circle cx="{cx + r * 0.04:.1f}" cy="{ey - r * 0.06:.1f}" r="{r * 0.045:.1f}" fill="#fff"/>')
        p.append(f'<ellipse cx="{s * r * 0.58:.1f}" cy="{r * 0.22:.1f}" rx="{r * 0.15:.1f}" ry="{r * 0.09:.1f}" '
                 f'fill="{BLUSH}" opacity=".6"/>')
        if glasses:
            p.append(f'<circle cx="{cx:.1f}" cy="{ey:.1f}" r="{r * 0.22:.1f}" stroke="{NAVY}" '
                     f'stroke-width="{r * 0.05:.1f}"/>')
    if glasses:
        p.append(f'<path d="M{-ex + r * 0.22:.1f} {ey:.1f} Q0 {ey - r * 0.08:.1f} {ex - r * 0.22:.1f} {ey:.1f}" '
                 f'stroke="{NAVY}" stroke-width="{r * 0.05:.1f}"/>')
    if mood == "wow":
        p.append(f'<ellipse cy="{r * 0.3:.1f}" rx="{r * 0.09:.1f}" ry="{r * 0.12:.1f}" fill="{NAVY}"/>')
    else:
        m = r * 0.16
        p.append(f'<path d="M{-m:.1f} {r * 0.22:.1f} Q0 {r * 0.38:.1f} {m:.1f} {r * 0.22:.1f}" stroke="{NAVY}" '
                 f'stroke-width="{sw:.1f}" stroke-linecap="round"/>')
    return f'<g transform="translate({x} {y})">{"".join(p)}</g>'


def dot(x: float, y: float, r: float = 3.5) -> str:
    """A tiny photon: a bright dot with a glow."""
    return (f'<circle cx="{x}" cy="{y}" r="{r * 3}" fill="url(#glow)"/>'
            f'<circle cx="{x}" cy="{y}" r="{r}" fill="{ICE}"/>')


def sparkle(x: float, y: float, s: float = 6, color: str = "#fff", opacity: float = 0.9) -> str:
    return (f'<path d="M{x} {y - s} Q{x} {y} {x + s} {y} Q{x} {y} {x} {y + s} Q{x} {y} {x - s} {y} '
            f'Q{x} {y} {x} {y - s} Z" fill="{color}" opacity="{opacity}"/>')


def _walk(points: str, color: str = BLUE) -> str:
    return (f'<path d="M{points}" stroke="{color}" stroke-width="1.6" stroke-dasharray="3 4" '
            f'stroke-linecap="round" stroke-linejoin="round"/>')


def _wave(y: float, x0: float = 24, x1: float = 336, amp: float = 6) -> str:
    """A gentle wavy line from x0 to x1 at height y (for tissue boundaries)."""
    step = (x1 - x0) / 4
    d = f"{x0} {y}"
    for i in range(4):
        a = x0 + step * i
        sign = 1 if i % 2 == 0 else -1
        d += f" C{a + step / 3:.1f} {y + sign * amp} {a + 2 * step / 3:.1f} {y + sign * amp} {a + step:.1f} {y}"
    return d


def _bird(x: float, y: float, s: float = 1, color: str = "#FFE9A8", flip: bool = False) -> str:
    t = f"translate({x} {y}) scale({-s if flip else s} {s})"
    return (f'<g transform="{t}"><ellipse rx="11" ry="8.5" fill="{color}"/>'
            f'<path d="M-3 -1 Q-12 -14 -16 -4 Q-9 2 -3 -1Z" fill="#fff" opacity=".85"/>'
            f'<path d="M10 -2 L17 0 L10 3Z" fill="#FFB054"/><circle cx="5" cy="-3" r="1.6" fill="{NAVY}"/></g>')


def _note(x: float, y: float, s: float = 1, opacity: float = 0.7) -> str:
    return (f'<g transform="translate({x} {y}) scale({s})" opacity="{opacity}">'
            f'<ellipse cx="0" cy="10" rx="4.5" ry="3.4" fill="{ICE}" transform="rotate(-20 0 10)"/>'
            f'<path d="M4 9 V-6 Q9 -4 11 1" stroke="{ICE}" stroke-width="2" stroke-linecap="round"/></g>')


def simulate() -> str:
    """Photon dives into skin layers; others random-walk, get absorbed by a vessel or come back out."""
    layers = (
        f'<g clip-path="url(#slab)"><rect x="24" y="118" width="312" height="96" fill="#C6ECF8"/>'
        f'<path d="M{_wave(133)} V174 H24 Z" fill="#F9CFCB"/>'
        f'<path d="M{_wave(133)} V118 H24 Z" fill="#FBE7C6"/>'
        f'<path d="M{_wave(174, amp=5)} V214 H24 Z" fill="#C6ECF8"/>'
        f'<ellipse cx="236" cy="155" rx="13" ry="8.5" fill="#EE5D69"/>'
        f'<ellipse cx="231" cy="152" rx="4.5" ry="2" fill="#fff" opacity=".6"/></g>'
    )
    walks = "".join(_walk(p) for p in (
        "180 132 L170 146 L188 156 L176 168 L196 182 L184 198",
        "180 132 L196 144 L212 139 L226 152",
        "180 132 L160 150 L138 160 L122 184 L100 194",
        "180 132 L164 142 L150 134 L136 118 L122 104",
    ))
    return _svg(
        '<path d="M150 0 H210 L196 128 H164 Z" fill="url(#beam)"/>'
        + layers + walks
        + f'<circle cx="184" cy="198" r="3.5" fill="{CYAN_BRIGHT}" stroke="#fff" stroke-width="1.2"/>'
        + f'<circle cx="100" cy="194" r="3.5" fill="{CYAN_BRIGHT}" stroke="#fff" stroke-width="1.2"/>'
        + sparkle(226, 152, 5, "#FFE9A8")
        + photon(112, 92, 11, "joy", glow=True)
        + '<path d="M168 30 v-10 M180 26 v-12 M192 30 v-10" stroke="#fff" stroke-width="2" stroke-linecap="round" opacity=".35"/>'
        + photon(180, 72, 26, "happy")
        + sparkle(70, 40, 6) + sparkle(292, 50, 5) + sparkle(322, 92, 3.5, ICE) + sparkle(44, 88, 3.5, ICE)
        + dot(250, 28, 2.5) + dot(112, 52, 2.5)
    )


def science() -> str:
    """Photon in glasses reading a book that glows."""
    rays = "".join(f'<path d="M180 118 L{x} {y}" stroke="{CYAN_BRIGHT}" stroke-width="2" stroke-linecap="round" '
                   f'opacity=".3"/>' for x, y in ((112, 44), (146, 26), (180, 20), (214, 26), (248, 44)))
    lines = "".join(f'<path d="M92 {y} Q128 {y - 6} 166 {y + 4}" stroke="#C9D5EE" stroke-width="2.4" '
                    f'stroke-linecap="round"/>' for y in (132, 144, 156, 168))
    return _svg(
        '<ellipse cx="180" cy="200" rx="112" ry="8" fill="#000" opacity=".25"/>'
        + rays
        + f'<path d="M70 186 C112 178 150 180 180 192 C210 180 248 178 290 186 V192 C248 184 210 186 180 198 '
          f'C150 186 112 184 70 192 Z" fill="{BLUE}"/>'
        + '<path d="M180 188 C150 176 112 174 76 182 V118 C112 110 150 112 180 124 Z" fill="#F1F5FD"/>'
        + '<path d="M180 188 C210 176 248 174 284 182 V118 C248 110 210 112 180 124 Z" fill="#fff"/>'
        + lines
        + '<path d="M198 136 V172 H270" stroke="#C9D5EE" stroke-width="2" stroke-linecap="round"/>'
        + f'<path d="M202 140 C216 158 236 164 266 167" stroke="{CYAN}" stroke-width="3" stroke-linecap="round"/>'
        + photon(180, 80, 30, "joy", glasses=True)
        + dot(96, 72, 3) + dot(268, 64, 3) + dot(300, 122, 2.5) + dot(58, 124, 2.5)
        + sparkle(128, 40, 6) + sparkle(240, 30, 7) + sparkle(302, 84, 4, ICE)
    )


def validate() -> str:
    """Monte Carlo (cyan) and adding–doubling (blue) balance on a scale: the answers agree."""
    pale = "#C9D6F5"
    return _svg(
        f'<path d="M150 206 H210 L202 194 H158 Z" fill="{pale}"/>'
        f'<rect x="176" y="58" width="8" height="140" rx="4" fill="{pale}"/>'
        f'<rect x="84" y="54" width="192" height="8" rx="4" fill="#E6ECFA"/>'
        f'<path d="M100 62 L78 124 M100 62 L122 124 M260 62 L238 124 M260 62 L282 124" stroke="{pale}" '
        f'stroke-width="1.5"/>'
        + photon(100, 106, 20, "joy", body="cyan")
        + photon(260, 106, 20, "joy", body="blue")
        + '<path d="M70 124 H130 A30 13 0 0 1 70 124 Z" fill="#E6ECFA"/>'
        + '<path d="M230 124 H290 A30 13 0 0 1 230 124 Z" fill="#E6ECFA"/>'
        + '<circle cx="180" cy="58" r="8" fill="#fff"/>'
        + '<circle cx="180" cy="24" r="15" fill="#fff"/>'
        + f'<path d="M172 24 L178 30 L189 18" stroke="{BLUE}" stroke-width="3.5" stroke-linecap="round" '
          f'stroke-linejoin="round"/>'
        + sparkle(150, 20, 5) + sparkle(212, 14, 4, ICE) + dot(40, 60, 2.5) + dot(322, 72, 2.5)
        + sparkle(48, 170, 4, ICE) + sparkle(318, 170, 5)
    )


def principles() -> str:
    """A little flowchart, and a chip full of photons with the mascot sitting on top."""
    node = "#EAF0FD"
    cores = "".join(
        f'<rect x="{208 + i * 26}" y="{106 + j * 24}" width="20" height="16" rx="4" fill="{BLUE}"/>'
        f'<circle cx="{218 + i * 26}" cy="{114 + j * 24}" r="2.6" fill="{ICE}"/>'
        for i in range(4) for j in range(3))
    pins = "".join(f'<rect x="{x}" y="186" width="6" height="9" rx="2" fill="{CYAN_BRIGHT}" opacity=".7"/>'
                   for x in range(212, 306, 16))
    pins += "".join(f'<rect x="187" y="{y}" width="9" height="6" rx="2" fill="{CYAN_BRIGHT}" opacity=".7"/>'
                    f'<rect x="316" y="{y}" width="9" height="6" rx="2" fill="{CYAN_BRIGHT}" opacity=".7"/>'
                    for y in range(104, 180, 18))
    return _svg(
        f'<rect x="38" y="30" width="84" height="26" rx="8" fill="{node}"/>'
        f'<path d="M50 43 H108" stroke="#9DB2E6" stroke-width="3" stroke-linecap="round"/>'
        f'<path d="M80 76 L110 96 L80 116 L50 96 Z" fill="{ICE}"/>'
        f'<rect x="38" y="136" width="84" height="26" rx="8" fill="{node}"/>'
        f'<path d="M50 149 H96" stroke="#9DB2E6" stroke-width="3" stroke-linecap="round"/>'
        f'<path d="M80 58 V72 M80 118 V132" stroke="{CYAN_BRIGHT}" stroke-width="2" marker-end="url(#arrow)"/>'
        f'<path d="M112 96 C146 96 146 43 126 43" stroke="{CYAN_BRIGHT}" stroke-width="2" '
        f'stroke-dasharray="4 4" marker-end="url(#arrow)"/>'
        + dot(80, 186, 3)
        + pins
        + f'<rect x="196" y="94" width="120" height="94" rx="14" fill="#0D2472" stroke="{CYAN_BRIGHT}" '
          f'stroke-width="2"/>'
        + cores
        + photon(256, 70, 26, "wow")
        + '<path d="M296 52 q10 -4 16 -14 M300 64 q12 0 22 -6" stroke="#fff" stroke-width="2" '
          'stroke-linecap="round" opacity=".35"/>'
        + sparkle(176, 30, 5) + sparkle(334, 30, 4, ICE) + sparkle(160, 186, 4, ICE)
    )


def product() -> str:
    """From the lab flask up the steps to a finished product, the mascot halfway up."""
    return _svg(
        '<rect x="40" y="160" width="92" height="56" rx="10" fill="#22409F"/>'
        f'<rect x="130" y="124" width="92" height="92" rx="10" fill="{BLUE_MID}"/>'
        f'<rect x="220" y="88" width="104" height="128" rx="10" fill="{BLUE}"/>'
        '<path d="M78 120 H94 V132 L106 152 A6 6 0 0 1 101 161 H71 A6 6 0 0 1 66 152 L78 132 Z" fill="#E9F9FE"/>'
        f'<path d="M71 146 H101 L106 152 A6 6 0 0 1 101 161 H71 A6 6 0 0 1 66 152 Z" fill="{CYAN}"/>'
        f'<circle cx="82" cy="140" r="2.5" fill="{CYAN}"/><circle cx="89" cy="133" r="1.8" fill="{CYAN}"/>'
        '<path d="M92 114 C114 76 142 76 158 92" stroke="#fff" stroke-width="2" stroke-dasharray="3 5" '
        'stroke-linecap="round" opacity=".45"/>'
        '<path d="M200 82 C214 56 234 52 244 58" stroke="#fff" stroke-width="2" stroke-dasharray="3 5" '
        'stroke-linecap="round" opacity=".45"/>'
        '<rect x="246" y="50" width="52" height="38" rx="9" fill="#fff"/>'
        f'<rect x="268" y="50" width="8" height="38" fill="{CYAN_BRIGHT}"/>'
        f'<path d="M272 50 C262 36 252 42 260 50 Z M272 50 C282 36 292 42 284 50 Z" fill="{CYAN_BRIGHT}"/>'
        '<path d="M312 30 V88" stroke="#fff" stroke-width="2.5" stroke-linecap="round"/>'
        f'<path d="M313 31 L336 39 L313 47 Z" fill="{CYAN_BRIGHT}"/>'
        + photon(176, 98, 24, "joy")
        + sparkle(236, 40, 5) + sparkle(304, 104, 4, ICE) + sparkle(46, 60, 5) + dot(140, 46, 2.5)
        + dot(330, 150, 2.5)
    )


def muse() -> str:
    """Someone meditating in an EEG headband; birds sing when the mind is calm."""
    return _svg(
        f'<circle cx="180" cy="98" r="54" stroke="{CYAN_BRIGHT}" stroke-width="1.5" opacity=".28"/>'
        f'<circle cx="180" cy="98" r="72" stroke="{CYAN_BRIGHT}" stroke-width="1.5" opacity=".14"/>'
        f'<path d="M40 204 C80 194 120 214 160 204 S240 194 320 204" stroke="{CYAN_BRIGHT}" stroke-width="2" '
        f'opacity=".35"/>'
        f'<ellipse cx="180" cy="184" rx="62" ry="16" fill="{BLUE_MID}"/>'
        '<path d="M150 184 C146 142 158 122 180 122 C202 122 214 142 210 184 Z" fill="#3A63D8"/>'
        '<path d="M156 140 C140 158 138 172 152 179 M204 140 C220 158 222 172 208 179" stroke="#3A63D8" '
        'stroke-width="12" stroke-linecap="round"/>'
        f'<circle cx="152" cy="179" r="7" fill="{SKIN}"/><circle cx="208" cy="179" r="7" fill="{SKIN}"/>'
        f'<rect x="172" y="114" width="16" height="12" fill="{SKIN}"/>'
        f'<circle cx="180" cy="96" r="30" fill="{SKIN}"/>'
        f'<path d="M150 94 C148 60 212 60 210 94 C204 80 192 74 180 76 C168 74 156 80 150 94 Z" fill="{HAIR}"/>'
        f'<path d="M151 86 C165 75 195 75 209 86" stroke="{BLUE}" stroke-width="7" stroke-linecap="round"/>'
        + "".join(f'<circle cx="{x}" cy="{y}" r="7" fill="url(#glow)"/><circle cx="{x}" cy="{y}" r="2.6" '
                  f'fill="{ICE}"/>' for x, y in ((166, 79.5), (180, 77), (194, 79.5)))
        + f'<path d="M164 99 q5 4 10 0 M186 99 q5 4 10 0" stroke="{NAVY}" stroke-width="2" stroke-linecap="round"/>'
        + f'<ellipse cx="163" cy="106" rx="4.5" ry="2.5" fill="{BLUSH}" opacity=".6"/>'
        + f'<ellipse cx="197" cy="106" rx="4.5" ry="2.5" fill="{BLUSH}" opacity=".6"/>'
        + f'<path d="M175 110 q5 4 10 0" stroke="{NAVY}" stroke-width="2" stroke-linecap="round"/>'
        + _bird(84, 64, 1.1) + _bird(282, 46, 0.95, "#CDEFFB", flip=True)
        + _note(110, 30, 0.9) + _note(250, 76, 0.8) + _note(306, 92, 0.7, 0.5)
        + sparkle(60, 120, 4, ICE) + sparkle(318, 140, 5)
    )


def headband() -> str:
    """A head in a light-emitting headband, inside a sense → decide → adjust loop."""
    return _svg(
        f'<path d="M124 216 C126 186 150 172 180 172 C210 172 234 186 236 216 Z" fill="{BLUE_MID}"/>'
        f'<rect x="170" y="148" width="20" height="28" fill="{SKIN}"/>'
        f'<circle cx="136" cy="118" r="7" fill="{SKIN}"/><circle cx="224" cy="118" r="7" fill="{SKIN}"/>'
        f'<circle cx="180" cy="112" r="44" fill="{SKIN}"/>'
        f'<path d="M136 108 C134 64 226 64 224 108 C214 90 200 82 180 84 C160 82 146 90 136 108 Z" fill="{HAIR}"/>'
        f'<path d="M137 100 C158 84 202 84 223 100" stroke="{BLUE}" stroke-width="9" stroke-linecap="round"/>'
        + "".join(f'<circle cx="{x}" cy="{y}" r="10" fill="url(#glow)"/><circle cx="{x}" cy="{y}" r="3.4" '
                  f'fill="{ICE}"/>' for x, y in ((158, 90), (180, 85.5), (202, 90)))
        + f'<path d="M158 120 q6 -7 12 0 M190 120 q6 -7 12 0" stroke="{NAVY}" stroke-width="2.6" '
          f'stroke-linecap="round"/>'
        + f'<ellipse cx="154" cy="130" rx="6" ry="3.4" fill="{BLUSH}" opacity=".6"/>'
        + f'<ellipse cx="206" cy="130" rx="6" ry="3.4" fill="{BLUSH}" opacity=".6"/>'
        + f'<path d="M172 132 q8 7 16 0" stroke="{NAVY}" stroke-width="2.6" stroke-linecap="round"/>'
        + f'<path d="M102.1 75.7 A86 86 0 0 1 257.9 75.7" stroke="{CYAN_BRIGHT}" stroke-width="2.5" '
          f'opacity=".75" marker-end="url(#arrow)"/>'
        + f'<path d="M257.9 148.3 A86 86 0 0 1 102.1 148.3" stroke="{CYAN_BRIGHT}" stroke-width="2.5" '
          f'opacity=".75" marker-end="url(#arrow)"/>'
        + f'<circle cx="90" cy="112" r="17" fill="#0D2472" stroke="{CYAN_BRIGHT}" stroke-width="2"/>'
        + f'<path d="M79 112 H83 L86 106 L90 118 L93 109 L96 114 H101" stroke="{ICE}" stroke-width="2" '
          f'stroke-linecap="round" stroke-linejoin="round"/>'
        + f'<circle cx="270" cy="112" r="17" fill="#0D2472" stroke="{CYAN_BRIGHT}" stroke-width="2"/>'
        + f'<path d="M270 120 C262 114 260 111 260 108 A4.5 4.5 0 0 1 270 106.5 A4.5 4.5 0 0 1 280 108 '
          f'C280 111 278 114 270 120 Z" fill="{BLUSH}"/>'
        + photon(300, 40, 14, "joy") + sparkle(56, 40, 5) + sparkle(326, 180, 4, ICE) + dot(46, 176, 2.5)
    )


def laser() -> str:
    """A laser handpiece shines on a knee; photons dive in and the mascot cheers."""
    hand = (
        '<g transform="translate(236 66) rotate(-35)">'
        '<rect x="0" y="0" width="90" height="26" rx="13" fill="#EEF2FF"/>'
        f'<rect x="54" y="0" width="12" height="26" fill="{BLUE}"/>'
        '<rect x="-12" y="7" width="16" height="12" rx="3" fill="#9DB2E6"/>'
        f'<circle cx="30" cy="13" r="4.5" fill="{CYAN_BRIGHT}"/></g>'
    )
    return _svg(
        f'<path d="M-30 118 C60 112 150 112 186 132 C204 142 214 170 228 230" stroke="{SKIN}" stroke-width="46" '
        f'stroke-linecap="round"/>'
        f'<path d="M-30 117 C10 115 40 114 66 114" stroke="{BLUE_MID}" stroke-width="50"/>'
        '<ellipse cx="190" cy="128" rx="16" ry="11" fill="#FFF0E6"/>'
        f'<path d="M229 80 L239 88 L204 113 L178 108 Z" fill="{CYAN_BRIGHT}" opacity=".35"/>'
        f'<ellipse cx="191" cy="110" rx="15" ry="5" fill="{CYAN_BRIGHT}" opacity=".55"/>'
        + _walk("188 114 L182 128 L194 138", CYAN)
        + _walk("194 114 L204 126 L198 140 L210 148", CYAN)
        + f'<circle cx="194" cy="138" r="3" fill="{CYAN}"/><circle cx="210" cy="148" r="3" fill="{CYAN}"/>'
        + hand
        + photon(300, 158, 24, "joy")
        + '<path d="M326 128 l8 -8 M332 140 l10 -3" stroke="#fff" stroke-width="2" stroke-linecap="round" opacity=".4"/>'
        + sparkle(120, 60, 6) + sparkle(328, 96, 4, ICE) + sparkle(60, 40, 4, ICE) + dot(150, 30, 2.5)
    )


def hero() -> str:
    """Landing page: the mascot leads a parade of photons into a dome of tissue layers."""
    dome = (
        '<ellipse cx="340" cy="262" rx="200" ry="160" fill="#FBE7C6"/>'
        '<ellipse cx="340" cy="262" rx="186" ry="146" fill="#F9CFCB"/>'
        '<ellipse cx="340" cy="262" rx="156" ry="116" fill="#C6ECF8"/>'
        '<ellipse cx="236" cy="168" rx="10" ry="6.5" fill="#EE5D69" transform="rotate(-35 236 168)"/>'
    )
    walks = "".join(_walk(p) for p in (
        "214 150 L230 162 L222 178 L246 186 L240 204",
        "214 150 L206 170 L228 172 L218 196",
        "268 122 L280 140 L268 150 L292 162 L300 184",
        "268 122 L284 128 L300 120 L320 132",
    ))
    trail = "".join(photon(x, y, r, m, glow=False) for x, y, r, m in ((60, 60, 13, "joy"), (32, 36, 9.5, "happy"),
                                                                      (14, 18, 7, "joy")))
    return _svg(
        dome + walks
        + f'<circle cx="240" cy="204" r="3.5" fill="{CYAN_BRIGHT}" stroke="#fff" stroke-width="1.2"/>'
        + f'<circle cx="300" cy="184" r="3.5" fill="{CYAN_BRIGHT}" stroke="#fff" stroke-width="1.2"/>'
        + '<path d="M136 104 Q186 108 210 146" stroke="#fff" stroke-width="2" stroke-dasharray="3 6" '
          'stroke-linecap="round" opacity=".5"/>'
        + '<path d="M196 50 Q236 60 262 116" stroke="#fff" stroke-width="2" stroke-dasharray="3 6" '
          'stroke-linecap="round" opacity=".35"/>'
        + trail
        + photon(108, 92, 34, "joy")
        + dot(190, 40, 4) + sparkle(160, 22, 6) + sparkle(318, 40, 7) + sparkle(250, 26, 4, ICE)
        + sparkle(40, 150, 5, ICE) + sparkle(120, 186, 4) + dot(78, 196, 2.5) + dot(340, 86, 2.5)
    )


def learn() -> str:
    """Science card: the mascot explains a photon's random walk at a little blackboard."""
    return _svg(
        '<path d="M80 150 L68 206 M170 150 L182 206" stroke="#9DB2E6" stroke-width="5" stroke-linecap="round"/>'
        f'<rect x="36" y="36" width="178" height="116" rx="12" fill="#0D2472" stroke="{CYAN_BRIGHT}" '
        f'stroke-width="2.5"/>'
        '<path d="M58 60 L78 82 L66 100 L94 110 L84 132 L112 120" stroke="#fff" stroke-width="2.2" '
        'stroke-dasharray="4 4" stroke-linecap="round" stroke-linejoin="round"/>'
        f'<circle cx="58" cy="60" r="4" fill="{ICE}"/><circle cx="112" cy="120" r="4" fill="{CYAN_BRIGHT}"/>'
        '<path d="M132 60 V134 H200" stroke="#5D78C9" stroke-width="2" stroke-linecap="round"/>'
        f'<path d="M136 66 C150 102 168 116 196 124" stroke="{CYAN_BRIGHT}" stroke-width="3" stroke-linecap="round"/>'
        '<path d="M236 112 L196 82" stroke="#FFE9A8" stroke-width="3.5" stroke-linecap="round"/>'
        + photon(266, 124, 32, "happy")
        + '<rect x="244" y="182" width="64" height="12" rx="3" fill="#3A63D8"/>'
          '<rect x="250" y="170" width="56" height="12" rx="3" fill="#EEF2FF"/>'
          f'<rect x="240" y="194" width="72" height="12" rx="3" fill="{CYAN}"/>'
        + sparkle(236, 40, 6) + sparkle(330, 70, 5, ICE) + sparkle(20, 170, 4) + dot(318, 30, 2.5)
    )


def devices() -> str:
    """Product card: our two products on display stands, the mascot peeking between them."""
    leds = "".join(f'<circle cx="{x}" cy="{y}" r="8" fill="url(#glow)"/><circle cx="{x}" cy="{y}" r="3" '
                   f'fill="{ICE}"/>' for x, y in ((78, 139), (104, 144), (130, 139)))
    return _svg(
        '<rect x="48" y="156" width="112" height="56" rx="10" fill="#22409F"/>'
        f'<ellipse cx="104" cy="156" rx="56" ry="11" fill="{BLUE_MID}"/>'
        '<ellipse cx="104" cy="128" rx="46" ry="16" stroke="#3A63D8" stroke-width="4"/>'
        f'<path d="M58 128 A46 16 0 0 0 150 128" stroke="{BLUE}" stroke-width="10" stroke-linecap="round"/>'
        + leds
        + '<rect x="230" y="156" width="92" height="56" rx="10" fill="#22409F"/>'
        f'<ellipse cx="276" cy="156" rx="46" ry="10" fill="{BLUE_MID}"/>'
        f'<path d="M266 50 H286 L310 0 H242 Z" fill="{CYAN_BRIGHT}" opacity=".22"/>'
        '<rect x="259" y="60" width="34" height="94" rx="17" fill="#EEF2FF"/>'
        f'<rect x="259" y="102" width="34" height="10" fill="{BLUE}"/>'
        '<rect x="267" y="48" width="18" height="14" rx="4" fill="#9DB2E6"/>'
        f'<circle cx="276" cy="82" r="5" fill="{CYAN_BRIGHT}"/>'
        + photon(190, 118, 26, "joy")
        + sparkle(176, 60, 6) + sparkle(54, 60, 5, ICE) + sparkle(330, 120, 5) + dot(214, 36, 2.5)
        + dot(26, 120, 2.5)
    )


def nirs() -> str:
    """Near-infrared sensing: a headband source and detector on a layered head; the mascot rides the
    banana-shaped path that light takes between them."""
    layers = "".join(f'<circle cx="180" cy="330" r="{r}" fill="{c}"/>' for r, c in (
        (250, "#FBE1CF"), (236, "#EFE7DA"), (222, "#BFE4F2"), (214, "#F4B9C0"), (190, "#F8D7DB")))
    hair = "".join(f'<path d="M{x} {y} q-3 -9 2 -14" stroke="{HAIR}" stroke-width="2.4" stroke-linecap="round"/>'
                   for x, y in ((150, 82), (162, 81), (198, 81), (210, 82), (100, 92), (260, 92)))
    return _svg(
        layers + hair
        + f'<path d="M122 86 C134 182 226 182 238 86" stroke="{CYAN_BRIGHT}" stroke-width="14" opacity=".28" '
          f'stroke-linecap="round"/>'
        + '<path d="M122 86 C134 182 226 182 238 86" stroke="#fff" stroke-width="2" stroke-dasharray="3 5" '
          'stroke-linecap="round"/>'
        + f'<path d="M92 89.6 A256 256 0 0 1 268 89.6" stroke="{BLUE}" stroke-width="9" stroke-linecap="round"/>'
        + f'<circle cx="120" cy="81" r="12" fill="url(#glow)"/><rect x="113" y="75" width="14" height="11" rx="3" '
          f'fill="{ICE}" stroke="{BLUE}" stroke-width="1.5"/>'
        + f'<rect x="233" y="75" width="14" height="11" rx="3" fill="{NAVY}" stroke="{CYAN_BRIGHT}" stroke-width="2"/>'
        + '<path d="M120 60 v-12 M110 64 l-7 -9 M130 64 l7 -9" stroke="#fff" stroke-width="2" stroke-linecap="round" '
          'opacity=".45"/>'
        + photon(180, 150, 16, "joy")
        + sparkle(64, 40, 6) + sparkle(300, 36, 5, ICE) + sparkle(328, 70, 4) + dot(40, 76, 2.5)
        + dot(240, 30, 2.5)
    )


SCENES = {
    "science": science, "simulate": simulate, "validate": validate, "principles": principles,
    "product": product, "muse": muse, "headband": headband, "laser": laser,
    "hero": hero, "learn": learn, "devices": devices, "nirs": nirs,
}


def scene(name: str) -> str:
    return SCENES[name]()
