"""SVG art for the duck race: the pond, the ducks, the roll buttons and icons.

Flat colours only. Everything is plain SVG built from strings: no scripts and
no external files, so it renders inside a GitHub README <img>.
"""

WIDTH, HEIGHT = 900, 204
CELL, PAD_X = 38, 60
TRACK_Y = 180
# Both ducks share one pond. The first team floats a little further back.
ROWS = [(98, 0.9), (146, 1.02)]  # (waterline y, scale) per team

FONT = "ui-rounded, 'SF Pro Rounded', system-ui, -apple-system, 'Segoe UI', Roboto, sans-serif"

INK = "#1B1530"
WATER = "#D3ECFB"
WATER_LIGHT = "#EAF6FE"
WATER_DEEP = "#B5DCF5"
DUCK = "#FFE070"
WING = "#FFD046"
BEAK = "#FF9F45"
BEAK_LOW = "#F47B20"
CAPE = "#F2545B"
CAPE_DARK = "#D63C48"
SHADES = "#1D1B2B"
GLINT = "#8FD8FF"
BUTTON = "#167EF3"  # donaldlee.xyz accent, oklch(0.605 0.196 256)
BOOST, SETBACK = "#BDEBB8", "#FFCFE0"


def square_x(square):
    return PAD_X + CELL * square + CELL / 2


# Side-on duck facing right. The waterline is y=0; anything below it is clipped.
DUCK_PARTS = f"""
  <g id="d-body">
    <path d="M-30 -18 C-38 -20 -42 -27 -40 -35 C-34 -31 -28 -29 -22 -26 Z" fill="{DUCK}"/>
    <rect x="-34" y="-26" width="64" height="40" rx="20" fill="{DUCK}"/>
    <path d="M-22 -11 C-19 -22 0 -23 4 -14 C0 -6 -14 -4 -22 -11 Z" fill="{WING}"/>
  </g>
  <g id="d-head">
    <path d="M8 -64 q-2 -8 -9 -7 M11 -64 q2 -8 8 -6" stroke="{DUCK}" stroke-width="3.4" stroke-linecap="round" fill="none"/>
    <circle cx="10" cy="-42" r="23" fill="{DUCK}"/>
  </g>
  <g id="d-eyes">
    <rect x="3" y="-53" width="6.5" height="12" rx="3.25" fill="{INK}"/>
    <rect x="19" y="-53" width="6.5" height="12" rx="3.25" fill="{INK}"/>
    <rect x="6.6" y="-51.4" width="2" height="2" rx=".5" fill="#fff"/>
    <rect x="22.6" y="-51.4" width="2" height="2" rx=".5" fill="#fff"/>
  </g>
  <g id="d-beak">
    <rect x="16" y="-31.5" width="17" height="6" rx="3" fill="{BEAK_LOW}"/>
    <rect x="13" y="-38.5" width="26" height="9" rx="4.5" fill="{BEAK}"/>
  </g>
  <g id="d-shades" transform="rotate(-4 16 -46)">
    <path d="M-6 -47.5 H34" stroke="{SHADES}" stroke-width="2.4" stroke-linecap="round"/>
    <rect x="-.5" y="-47.5" width="14" height="11.5" rx="4" fill="{SHADES}"/>
    <rect x="16" y="-47.5" width="14" height="11.5" rx="4" fill="{SHADES}"/>
    <path d="M2.2 -44.2 h4 M18.7 -44.2 h4" stroke="{GLINT}" stroke-width="1.4" stroke-linecap="round"/>
  </g>
  <g id="d-cape">
    <path d="M2 -34 C-16 -40 -40 -47 -60 -49 C-56 -40 -62 -32 -60 -22 C-40 -21 -18 -20 2 -20 Z" fill="{CAPE}"/>
    <path d="M-60 -22 C-40 -21 -18 -20 2 -20 L2 -24 C-18 -24.5 -40 -25.5 -60.5 -27 Z" fill="{CAPE_DARK}"/>
  </g>
  <path id="d-collar" d="M-9 -29 Q10 -14 30 -29" stroke="{CAPE}" stroke-width="4.6" stroke-linecap="round" fill="none"/>
  <g id="duck-sunglasses">
    <use href="#d-body"/><use href="#d-head"/><use href="#d-eyes"/><use href="#d-shades"/><use href="#d-beak"/>
  </g>
  <g id="duck-cape">
    <use href="#d-body"/><use href="#d-cape"/><use href="#d-head"/><use href="#d-collar"/><use href="#d-eyes"/><use href="#d-beak"/>
  </g>
  <clipPath id="above-water" clipPathUnits="userSpaceOnUse"><rect x="-90" y="-120" width="180" height="120"/></clipPath>"""

STYLE = """<style>
  .bob { animation: bob 2.6s cubic-bezier(.37,0,.63,1) infinite; transform-box: fill-box; transform-origin: 50% 100%; }
  .ring { animation: ring 2.6s cubic-bezier(.22,1,.36,1) infinite; transform-box: fill-box; transform-origin: center; }
  .late, .late .ring { animation-delay: -1.3s; }
  @keyframes bob { 0%, 100% { transform: translateY(0) rotate(0deg); } 50% { transform: translateY(-1.5px) rotate(-1.5deg); } }
  @keyframes ring { 0% { transform: scale(.85); opacity: .9; } 100% { transform: scale(1.3); opacity: 0; } }
  @media (prefers-reduced-motion: reduce) { .bob, .ring { animation: none; } }
</style>"""

# Special-square icons, centred on (0, 0), about 14px across.
ICONS = {
    "bread": (
        '<path d="M-7 2 V-1.5 A4 4 0 0 1 -5 -5 A6 4.5 0 0 1 5 -5 A4 4 0 0 1 7 -1.5 V2 Q7 5 4 5 H-4 Q-7 5 -7 2 Z" fill="#F5B23E"/>'
        '<path d="M-4.5 1.5 V-1 A2.5 2.5 0 0 1 -3 -3 A4 3 0 0 1 3 -3 A2.5 2.5 0 0 1 4.5 -1 V1.5 Q4.5 3 3 3 H-3 Q-4.5 3 -4.5 1.5 Z" fill="#FDE6BB"/>'
    ),
    "bug": (
        f'<path d="M-1 -7.5 l-2 -2.5 M1 -7.5 l2 -2.5 M-5 -1 h-2.5 M5 -1 h2.5 M-4.5 3 l-2.5 1.5 M4.5 3 l2.5 1.5" stroke="{INK}" stroke-width="1" stroke-linecap="round"/>'
        '<ellipse cx="0" cy="1" rx="5" ry="6" fill="#5FBF5C"/>'
        f'<circle cx="0" cy="-5.5" r="2.6" fill="{INK}"/>'
        f'<path d="M0 -3 V7" stroke="{INK}" stroke-width=".9"/>'
        f'<circle cx="-2.3" cy="1" r="1" fill="{INK}"/><circle cx="2.3" cy="3" r="1" fill="{INK}"/>'
    ),
    "rocket": (
        '<path d="M-1.8 4.5 L0 9 L1.8 4.5 Z" fill="#F5B23E"/>'
        '<path d="M-3 1 L-6.2 5.5 L-3 4.5 Z M3 1 L6.2 5.5 L3 4.5 Z" fill="#9877EE"/>'
        f'<path d="M0 -8.5 C4 -5.5 4 1 3 4.8 H-3 C-4 1 -4 -5.5 0 -8.5 Z" fill="#fff" stroke="{INK}" stroke-width=".9"/>'
        '<circle cx="0" cy="-1.8" r="1.8" fill="#5DB8F0"/>'
    ),
    "whirlpool": (
        '<path d="M0 0 a1.6 1.6 0 0 1 3.2 0 a3.2 3.2 0 0 1 -6.4 0 a4.8 4.8 0 0 1 9.6 0 a6.4 6.4 0 0 1 -12.8 0" '
        'transform="translate(-.8 0)" stroke="#C2407A" stroke-width="1.6" fill="none" stroke-linecap="round"/>'
    ),
    "nap": (
        '<path d="M-6.5 -.5 h5.5 l-5.5 6 h5.5 M1.5 -7 h4 l-4 4.4 h4" stroke="#7A55E0" stroke-width="1.7" '
        'fill="none" stroke-linecap="round" stroke-linejoin="round"/>'
    ),
}


def _defs(extra=""):
    return f"<defs>{DUCK_PARTS}{extra}\n</defs>"


def _pond():
    """Flat water with a few light ripples and two lily pads tucked along the top."""
    ripples = [(118, 30), (372, 22), (598, 34), (806, 26), (232, 118), (488, 156), (706, 112), (36, 156)]
    waves = "".join(f"M{x} {y} q4 -3 8 0 t8 0 t8 0 " for x, y in ripples)
    pad = '<path d="M0 0 L10 -4 A10.5 10.5 0 1 0 10 4 Z" fill="#A6DF9D"/>'
    return (
        f'<rect width="{WIDTH}" height="{HEIGHT}" rx="24" fill="{WATER}"/>'
        f'<path d="{waves}" stroke="{WATER_LIGHT}" stroke-width="2.4" fill="none" stroke-linecap="round"/>'
        f'<g transform="translate(676 20) rotate(-20)">{pad}</g>'
        f'<g transform="translate(284 16) rotate(150) scale(.7)">{pad}</g>'
    )


def _track(tiles, track_length):
    parts = []
    for square in range(track_length):
        x = square_x(square)
        if square in tiles:
            icon, delta = tiles[square]
            fill = BOOST if delta > 0 else SETBACK
            parts.append(f'<g transform="translate({x} {TRACK_Y})"><circle r="11.5" fill="{fill}"/>{ICONS[icon]}</g>')
        elif square and square % 5 == 0:
            parts.append(
                f'<text x="{x}" y="{TRACK_Y + 4}" text-anchor="middle" font-size="11" font-weight="700" fill="#5B8FB8">{square}</text>'
            )
        else:
            parts.append(f'<circle cx="{x}" cy="{TRACK_Y}" r="2.4" fill="{WATER_DEEP}"/>')
    finish_x = square_x(track_length) + 22
    parts.append(f'<rect x="{finish_x}" y="26" width="10" height="{TRACK_Y - 36}" rx="4" fill="url(#checker)"/>')
    return "".join(parts)


def _duck(x, waterline, scale, accessory, late):
    return (
        f'<g class="bob{" late" if late else ""}">'
        f'<g transform="translate({x} {waterline}) scale({scale})">'
        f'<ellipse cx="0" cy="7" rx="28" ry="3.5" fill="{DUCK}" opacity=".35"/>'
        f'<g clip-path="url(#above-water)"><use href="#duck-{accessory}"/></g>'
        '<path d="M-36 0 A36 4.5 0 0 0 36 0" stroke="#fff" stroke-width="2.2" fill="none" stroke-linecap="round"/>'
        '<ellipse class="ring" cx="0" cy="0" rx="38" ry="5" stroke="#fff" stroke-width="1.4" fill="none"/>'
        "</g></g>"
    )


CHECKER = f"""
  <pattern id="checker" width="10" height="10" patternUnits="userSpaceOnUse">
    <rect width="10" height="10" fill="#fff"/>
    <rect width="5" height="5" fill="{INK}"/><rect x="5" y="5" width="5" height="5" fill="{INK}"/>
  </pattern>"""


def board_svg(positions, teams, tiles, track_length, label):
    """The whole pond. `positions` maps team -> square; `tiles` maps square -> (icon, delta)."""
    out = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}" height="{HEIGHT}" viewBox="0 0 {WIDTH} {HEIGHT}" '
        f'font-family="{FONT}" role="img" aria-label="{label}">',
        STYLE,
        _defs(CHECKER),
        _pond(),
        _track(tiles, track_length),
    ]
    for i, team in enumerate(teams):
        waterline, scale = ROWS[i]
        out.append(_duck(square_x(positions[team]), waterline, scale, teams[team]["accessory"], i == 1))
    out.append("</svg>")
    return "\n".join(out) + "\n"


def _head(accessory):
    """Just the head and its accessory, for the roll buttons."""
    if accessory == "cape":
        return '<use href="#d-head"/><use href="#d-collar"/><use href="#d-eyes"/><use href="#d-beak"/>'
    return '<use href="#d-head"/><use href="#d-eyes"/><use href="#d-shades"/><use href="#d-beak"/>'


def button_svg(label, accessory):
    """A flat roll button with the duck's head on it."""
    width = round(62 + len(label) * 10.4 + 26)
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="52" viewBox="0 0 {width} 52" font-family="{FONT}" role="img" aria-label="{label}">
{_defs()}
<rect width="{width}" height="52" rx="26" fill="{BUTTON}"/>
<g transform="translate(26 49) scale(.6)">{_head(accessory)}</g>
<text x="60" y="32.5" font-size="19" font-weight="800" fill="#fff">{label}</text>
</svg>
"""


def duck_icon_svg(accessory):
    """One racing duck on a sliver of water, for inline use in the README."""
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="56" height="43" viewBox="-68 -76 112 86" role="img" aria-label="duck">
{_defs()}
<ellipse cx="-8" cy="2" rx="52" ry="6" fill="{WATER_DEEP}"/>
<g clip-path="url(#above-water)"><use href="#duck-{accessory}"/></g>
<path d="M-40 0 A40 5 0 0 0 34 0" stroke="#fff" stroke-width="2.6" fill="none" stroke-linecap="round"/>
</svg>
"""


def duck_front_svg():
    """A duck looking straight at you: the game's icon."""
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="64" height="64" viewBox="0 0 64 64" role="img" aria-label="duck">
<ellipse cx="25" cy="60.5" rx="5.5" ry="2.6" fill="{BEAK}"/><ellipse cx="39" cy="60.5" rx="5.5" ry="2.6" fill="{BEAK}"/>
<ellipse cx="32" cy="49" rx="20" ry="12.5" fill="{DUCK}"/>
<ellipse cx="13.5" cy="48" rx="4" ry="7" fill="{WING}" transform="rotate(14 13.5 48)"/>
<ellipse cx="50.5" cy="48" rx="4" ry="7" fill="{WING}" transform="rotate(-14 50.5 48)"/>
<path d="M30.5 8 q-2 -6 -7 -5 M33.5 8 q2 -6 6.5 -4.5" stroke="{DUCK}" stroke-width="3" stroke-linecap="round" fill="none"/>
<circle cx="32" cy="26" r="19" fill="{DUCK}"/>
<rect x="21" y="16.5" width="6" height="11" rx="3" fill="{INK}"/><rect x="37" y="16.5" width="6" height="11" rx="3" fill="{INK}"/>
<rect x="24.3" y="18" width="1.9" height="1.9" rx=".5" fill="#fff"/><rect x="40.3" y="18" width="1.9" height="1.9" rx=".5" fill="#fff"/>
<rect x="26" y="35" width="12" height="5" rx="2.5" fill="{BEAK_LOW}"/>
<rect x="22.5" y="29.5" width="19" height="7.5" rx="3.75" fill="{BEAK}"/>
</svg>
"""


LINK_FILL, LINK_TEXT = "#E3EFFE", "#0B55B5"
LINK_ICONS = {
    "globe": (
        f'<circle cx="10" cy="10" r="7.6" fill="none" stroke="{BUTTON}" stroke-width="1.8"/>'
        f'<ellipse cx="10" cy="10" rx="3.4" ry="7.6" fill="none" stroke="{BUTTON}" stroke-width="1.6"/>'
        f'<path d="M2.6 10 H17.4" stroke="{BUTTON}" stroke-width="1.6"/>'
    ),
    "linkedin": (
        f'<rect x="2" y="2" width="16" height="16" rx="3.6" fill="{BUTTON}"/>'
        '<circle cx="6.5" cy="6.6" r="1.4" fill="#fff"/><rect x="5.3" y="8.8" width="2.4" height="6" fill="#fff"/>'
        '<path d="M9.3 8.8 h2.3 v.9 c.5 -.7 1.3 -1.1 2.2 -1.1 c1.7 0 2.5 1 2.5 2.9 V14.8 h-2.4 v-3 c0 -.9 -.3 -1.4 -1.1 -1.4 c-.8 0 -1.2 .5 -1.2 1.5 V14.8 H9.3 Z" fill="#fff"/>'
    ),
    "mail": (
        f'<rect x="2.2" y="4.4" width="15.6" height="11.2" rx="2.6" fill="none" stroke="{BUTTON}" stroke-width="1.8"/>'
        f'<path d="M3.4 6.2 L10 11 L16.6 6.2" fill="none" stroke="{BUTTON}" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/>'
    ),
}


def link_button_svg(label, icon):
    """A soft rounded pill for the profile links, quieter than the roll buttons."""
    width = round(46 + len(label) * 8.5 + 18)
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="40" viewBox="0 0 {width} 40" font-family="{FONT}" role="img" aria-label="{label}">
<rect width="{width}" height="40" rx="20" fill="{LINK_FILL}"/>
<g transform="translate(16 10)">{LINK_ICONS[icon]}</g>
<text x="44" y="25.5" font-size="15.5" font-weight="700" fill="{LINK_TEXT}">{label}</text>
</svg>
"""
