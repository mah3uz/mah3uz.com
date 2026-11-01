"""Generates the project cover art for the Neat theme into public/art/.

Every cover shares the banner's language — midnight teal canvas, a radial glow, three corner brackets and a peeled
corner — and draws its own centrepiece.
"""
import math
import random
import sys
from pathlib import Path

OUT = Path(sys.argv[1])
OUT.mkdir(parents=True, exist_ok=True)
W, H = 1600, 1000


def frame(uid, body, glow=(420, 380), hue='#21BDB0'):
    gx, gy = glow
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img">
<defs>
<linearGradient id="{uid}-bg" x1="0" y1="0" x2="{W}" y2="{H}" gradientUnits="userSpaceOnUse"><stop offset="0" stop-color="#0A1A20"/><stop offset="1" stop-color="#0D2A31"/></linearGradient>
<radialGradient id="{uid}-glow" cx="{gx}" cy="{gy}" r="760" gradientUnits="userSpaceOnUse"><stop offset="0" stop-color="{hue}" stop-opacity="0.34"/><stop offset="1" stop-color="{hue}" stop-opacity="0"/></radialGradient>
<linearGradient id="{uid}-tile" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#62EDD4"/><stop offset="0.55" stop-color="#21BDB0"/><stop offset="1" stop-color="#1388A6"/></linearGradient>
<linearGradient id="{uid}-back" x1="0" y1="{H-260}" x2="0" y2="{H}" gradientUnits="userSpaceOnUse"><stop offset="0" stop-color="#62EDD4"/><stop offset="1" stop-color="#21BDB0"/></linearGradient>
<linearGradient id="{uid}-flap" x1="{W-26}" y1="{H-26}" x2="{W-208}" y2="{H-208}" gradientUnits="userSpaceOnUse"><stop offset="0" stop-color="#A6D3D6"/><stop offset="0.5" stop-color="#E9F7F7"/><stop offset="1" stop-color="#FFFFFF"/></linearGradient>
<linearGradient id="{uid}-line" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#62EDD4" stop-opacity="0"/><stop offset="0.5" stop-color="#62EDD4"/><stop offset="1" stop-color="#62EDD4" stop-opacity="0"/></linearGradient>
<pattern id="{uid}-dots" width="28" height="28" patternUnits="userSpaceOnUse"><circle cx="2" cy="2" r="1.4" fill="#62EDD4" fill-opacity="0.12"/></pattern>
<filter id="{uid}-soft" x="-30%" y="-30%" width="160%" height="160%"><feGaussianBlur stdDeviation="24"/></filter>
<clipPath id="{uid}-cut"><path d="M0 0H{W}V{H-260}Q{W-210} {H-210} {W-260} {H}H0Z"/></clipPath>
</defs>
<rect width="{W}" height="{H}" fill="url(#{uid}-back)"/>
<g clip-path="url(#{uid}-cut)">
<rect width="{W}" height="{H}" fill="url(#{uid}-bg)"/>
<rect width="{W}" height="{H}" fill="url(#{uid}-dots)"/>
<rect width="{W}" height="{H}" fill="url(#{uid}-glow)"/>
{body}
</g>
<path d="M{W} {H-260}C{W-88.4} {H-267.8} {W-176.8} {H-244.4} {W-208} {H-208}C{W-244.4} {H-176.8} {W-267.8} {H-88.4} {W-260} {H}Q{W-145.6} {H-145.6} {W} {H-260}Z" fill="url(#{uid}-flap)"/>
<path d="M60 150V96Q60 60 96 60H150M{W-60} 150V96Q{W-60} 60 {W-96} 60H{W-150}M60 {H-150}V{H-96}Q60 {H-60} 96 {H-60}H150" fill="none" stroke="#21BDB0" stroke-opacity="0.6" stroke-width="8" stroke-linecap="round"/>
</svg>
'''


def window(x, y, w, h, uid, title_dots=True, fill='#0B2229'):
    dots = ''
    if title_dots:
        dots = ''.join(
            f'<circle cx="{x + 34 + i * 26}" cy="{y + 30}" r="7" fill="{c}"/>'
            for i, c in enumerate(['#62EDD4', '#21BDB0', '#1388A6'])
        )
    return (
        f'<rect x="{x}" y="{y + 18}" width="{w}" height="{h}" rx="28" fill="#000" fill-opacity="0.45" filter="url(#{uid}-soft)"/>'
        f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="28" fill="{fill}" stroke="#62EDD4" stroke-opacity="0.18" stroke-width="2"/>'
        f'<path d="M{x} {y + 60}H{x + w}" stroke="#62EDD4" stroke-opacity="0.12" stroke-width="2"/>' + dots
    )


def bars(x, y, widths, gap=34, h=12, colors=None):
    out = []
    for i, w in enumerate(widths):
        color = (colors or ['#A6D3D6'])[i % len(colors or ['#A6D3D6'])]
        opacity = 0.9 if i == 0 else 0.45
        out.append(f'<rect x="{x}" y="{y + i * gap}" width="{w}" height="{h}" rx="{h / 2}" fill="{color}" fill-opacity="{opacity}"/>')
    return ''.join(out)


# ---------------------------------------------------------------- Nibble: a schema becoming a page
def nibble():
    u = 'nb'
    b = []
    # schema window (left)
    b.append(window(170, 230, 520, 560, u))
    y = 330
    rows = [('title', 'text', 210), ('tagline', 'text', 160), ('body', 'markdown', 240), ('status', 'select', 130),
            ('stack', 'list', 180), ('cover', 'assets', 150)]
    for name, kind, w in rows:
        b.append(f'<rect x="214" y="{y}" width="14" height="14" rx="4" fill="#21BDB0"/>')
        b.append(f'<rect x="246" y="{y}" width="{w}" height="14" rx="7" fill="#E9F7F7" fill-opacity="0.85"/>')
        b.append(f'<rect x="{560}" y="{y - 6}" width="90" height="26" rx="13" fill="#21BDB0" fill-opacity="0.16" stroke="#21BDB0" stroke-opacity="0.5"/>')
        y += 72
    # flow arrows
    b.append('<path d="M712 510C780 510 800 440 868 440" fill="none" stroke="url(#nb-line)" stroke-width="4" stroke-dasharray="2 14" stroke-linecap="round"/>')
    b.append('<path d="M712 530C780 530 800 600 868 600" fill="none" stroke="url(#nb-line)" stroke-width="4" stroke-dasharray="2 14" stroke-linecap="round"/>')
    # rendered page (right)
    b.append(window(880, 170, 560, 640, u, fill='#0E2B33'))
    b.append('<rect x="930" y="270" width="460" height="210" rx="22" fill="url(#nb-tile)"/>')
    b.append('<path d="M970 320V302Q970 290 982 290H1000M1350 320V302Q1350 290 1338 290H1320M970 430V448Q970 460 982 460H1000" fill="none" stroke="#fff" stroke-width="7" stroke-linecap="round" stroke-opacity="0.9"/>')
    b.append('<circle cx="1160" cy="375" r="42" fill="#fff" fill-opacity="0.92"/><path d="M1146 355l34 20-34 20z" fill="#1388A6"/>')
    b.append(bars(930, 520, [380, 300, 340, 220], gap=40, h=16, colors=['#E9F7F7']))
    b.append('<rect x="930" y="700" width="170" height="54" rx="27" fill="#62EDD4"/><rect x="1120" y="700" width="130" height="54" rx="27" fill="none" stroke="#62EDD4" stroke-opacity="0.6" stroke-width="2"/>')
    # a crumb
    b.append('<g transform="translate(1400 150) rotate(18)"><path d="M0 0l40 -12 30 26 -12 40 -44 6 -26 -30z" fill="url(#nb-tile)"/></g>')
    b.append('<g transform="translate(130 820) rotate(-12)"><path d="M0 0l24 -8 18 16 -8 24 -26 4 -16 -18z" fill="#62EDD4" fill-opacity="0.6"/></g>')
    return frame(u, ''.join(b), glow=(1150, 420))


# ---------------------------------------------------------------- Nibble CLI: a prompt in a terminal
def nibble_cli():
    u = 'nc'
    b = [window(210, 190, 1180, 620, u)]
    lines = [
        ('$', 'nibble new', 360, '#62EDD4'),
        ('›', '', 520, '#A6D3D6'),
        ('›', '', 440, '#A6D3D6'),
        ('✓', '', 300, '#21BDB0'),
        ('$', 'nibble content pull', 420, '#62EDD4'),
        ('✓', '', 520, '#21BDB0'),
    ]
    y = 320
    for sym, _, w, color in lines:
        b.append(f'<text x="270" y="{y + 16}" font-family="ui-monospace,Menlo,monospace" font-size="34" font-weight="700" fill="{color}">{sym}</text>')
        b.append(f'<rect x="320" y="{y - 4}" width="{w}" height="22" rx="11" fill="{color}" fill-opacity="{0.85 if sym == "$" else 0.4}"/>')
        y += 72
    b.append(f'<rect x="320" y="{y - 6}" width="22" height="34" rx="3" fill="#62EDD4"/>')
    # a key = "as you, never more than you"
    b.append('<g transform="translate(1130 300)"><circle r="78" fill="url(#nc-tile)"/><circle r="30" fill="#0B2229"/><rect x="60" y="-16" width="190" height="32" rx="10" fill="url(#nc-tile)"/><rect x="190" y="16" width="22" height="40" rx="6" fill="#21BDB0"/><rect x="226" y="16" width="22" height="28" rx="6" fill="#1388A6"/></g>')
    # rust gear hint
    gear = []
    for i in range(12):
        a = i * math.pi / 6
        gear.append(f'<rect x="-10" y="-96" width="20" height="26" rx="5" transform="rotate({math.degrees(a):.1f})" fill="#1388A6" fill-opacity="0.55"/>')
    b.append(f'<g transform="translate(1240 690)">{"".join(gear)}<circle r="76" fill="none" stroke="#1388A6" stroke-opacity="0.55" stroke-width="18"/></g>')
    return frame(u, ''.join(b), glow=(700, 450))


# ---------------------------------------------------------------- Quarry: query editor + results + databases
def quarry():
    u = 'qy'
    b = [window(150, 170, 860, 660, u)]
    # editor lines with keyword chips
    y = 280
    for words in [[('#62EDD4', 120), ('#E9F7F7', 200), ('#62EDD4', 90), ('#E9F7F7', 140)],
                  [('#62EDD4', 90), ('#A6D3D6', 260)],
                  [('#62EDD4', 120), ('#A6D3D6', 180), ('#21BDB0', 80)]]:
        x = 200
        for color, w in words:
            b.append(f'<rect x="{x}" y="{y}" width="{w}" height="18" rx="9" fill="{color}" fill-opacity="0.8"/>')
            x += w + 18
        y += 46
    # result grid
    gx, gy = 200, 450
    cols = [150, 220, 160, 180]
    b.append(f'<rect x="{gx - 10}" y="{gy - 10}" width="{sum(cols) + 60}" height="330" rx="16" fill="#0E2B33"/>')
    x = gx
    for c in cols:
        b.append(f'<rect x="{x}" y="{gy + 6}" width="{c - 40}" height="14" rx="7" fill="#62EDD4"/>')
        x += c + 10
    for r in range(1, 6):
        yy = gy + r * 54
        b.append(f'<path d="M{gx - 10} {yy - 14}H{gx + sum(cols) + 50}" stroke="#62EDD4" stroke-opacity="0.1" stroke-width="2"/>')
        x = gx
        for i, c in enumerate(cols):
            ww = (c - 40) * (0.45 + ((r * 7 + i * 3) % 6) / 10)
            hl = r == 2
            b.append(f'<rect x="{x}" y="{yy + 4}" width="{ww:.0f}" height="12" rx="6" fill="{"#62EDD4" if hl else "#A6D3D6"}" fill-opacity="{0.9 if hl else 0.35}"/>')
            x += c + 10
    b.append(f'<rect x="{gx - 10}" y="{gy + 2 * 54 - 14}" width="{sum(cols) + 60}" height="54" fill="#21BDB0" fill-opacity="0.12"/>')
    # database cylinders
    def cyl(cx, cy, label_color, s=1.0):
        rx, ry, h = 110 * s, 34 * s, 70 * s
        out = []
        for i in range(3):
            top = cy + i * h
            out.append(f'<path d="M{cx - rx} {top}V{top + h}A{rx} {ry} 0 0 0 {cx + rx} {top + h}V{top}" fill="url(#qy-tile)" fill-opacity="{1 - i * 0.18}"/>')
            out.append(f'<ellipse cx="{cx}" cy="{top}" rx="{rx}" ry="{ry}" fill="#E9F7F7" fill-opacity="{0.9 if i == 0 else 0.0}"/>')
            out.append(f'<path d="M{cx - rx} {top + h}A{rx} {ry} 0 0 0 {cx + rx} {top + h}" fill="none" stroke="#0A1A20" stroke-opacity="0.35" stroke-width="3"/>')
        out.append(f'<circle cx="{cx + rx - 30 * s}" cy="{cy + 40 * s}" r="{8 * s}" fill="{label_color}"/>')
        return ''.join(out)
    b.append(cyl(1220, 250, '#043040', 1.0))
    b.append(cyl(1340, 560, '#043040', 0.7))
    b.append(cyl(1130, 610, '#043040', 0.55))
    b.append('<path d="M1010 420C1080 420 1080 320 1110 300M1010 560C1090 560 1110 610 1180 620M1010 640C1060 680 1180 720 1240 640" fill="none" stroke="url(#qy-line)" stroke-width="4" stroke-dasharray="2 14" stroke-linecap="round"/>')
    return frame(u, ''.join(b), glow=(1200, 380))


# ---------------------------------------------------------------- Sysman: history graphs
def sysman():
    u = 'sm'
    random.seed(7)
    b = [window(150, 160, 1300, 680, u)]
    # sidebar gauges
    for i, (pct, color) in enumerate([(0.72, '#62EDD4'), (0.46, '#21BDB0'), (0.28, '#1388A6')]):
        cx, cy, r = 300, 330 + i * 165, 58
        circ = 2 * math.pi * r
        b.append(f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="#62EDD4" stroke-opacity="0.12" stroke-width="16"/>')
        b.append(f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="{color}" stroke-width="16" stroke-linecap="round" stroke-dasharray="{circ * pct:.1f} {circ:.1f}" transform="rotate(-90 {cx} {cy})"/>')
        b.append(f'<rect x="{cx - 26}" y="{cy - 7}" width="52" height="14" rx="7" fill="#E9F7F7" fill-opacity="0.85"/>')
    # graph area
    gx, gy, gw, gh = 430, 250, 960, 520
    for i in range(6):
        y = gy + i * gh / 5
        b.append(f'<path d="M{gx} {y:.0f}H{gx + gw}" stroke="#62EDD4" stroke-opacity="0.08" stroke-width="2"/>')
    def series(base, amp, seed, color, fill):
        random.seed(seed)
        pts, v = [], base
        for i in range(49):
            v = max(0.08, min(0.95, v + random.uniform(-amp, amp)))
            pts.append((gx + i * gw / 48, gy + gh - v * gh))
        d = 'M' + ' L'.join(f'{x:.1f} {y:.1f}' for x, y in pts)
        out = ''
        if fill:
            out += f'<path d="{d} L{gx + gw} {gy + gh} L{gx} {gy + gh}Z" fill="{color}" fill-opacity="0.14"/>'
        out += f'<path d="{d}" fill="none" stroke="{color}" stroke-width="5" stroke-linejoin="round" stroke-linecap="round"/>'
        return out, pts
    s1, pts = series(0.55, 0.09, 3, '#62EDD4', True)
    s2, _ = series(0.3, 0.06, 11, '#1388A6', False)
    b.append(s2)
    b.append(s1)
    px, py = pts[34]
    b.append(f'<path d="M{px:.0f} {gy}V{gy + gh}" stroke="#E9F7F7" stroke-opacity="0.5" stroke-width="2" stroke-dasharray="6 8"/>')
    b.append(f'<circle cx="{px:.0f}" cy="{py:.0f}" r="14" fill="#0B2229" stroke="#62EDD4" stroke-width="6"/>')
    b.append(f'<rect x="{px + 26:.0f}" y="{py - 70:.0f}" width="170" height="64" rx="16" fill="#E9F7F7"/><rect x="{px + 46:.0f}" y="{py - 52:.0f}" width="90" height="12" rx="6" fill="#0F5F78"/><rect x="{px + 46:.0f}" y="{py - 32:.0f}" width="130" height="10" rx="5" fill="#1388A6" fill-opacity="0.5"/>')
    return frame(u, ''.join(b), glow=(900, 560))


# ---------------------------------------------------------------- Darwan: two gates — login screen + lock screen
def darwan():
    u = 'dw'
    b = []
    palettes = [('#62EDD4', '#1388A6'), ('#A6D3D6', '#0F5F78'), ('#21BDB0', '#043040')]
    # back cards fanned
    for i, (a, c) in enumerate(palettes[::-1]):
        ang = (-10 + i * 10)
        b.append(f'<g transform="translate(800 520) rotate({ang}) translate(-300 -330)" opacity="{0.5 + i * 0.25}">'
                 f'<rect x="0" y="18" width="600" height="420" rx="30" fill="#000" fill-opacity="0.4" filter="url(#dw-soft)"/>'
                 f'<rect width="600" height="420" rx="30" fill="#0E2B33" stroke="#62EDD4" stroke-opacity="0.25" stroke-width="2"/>'
                 f'<rect x="20" y="20" width="560" height="380" rx="20" fill="{c}"/>'
                 f'<circle cx="430" cy="140" r="150" fill="{a}" fill-opacity="0.35"/>'
                 f'<path d="M20 330Q170 250 300 300T580 260V400H20Z" fill="{a}" fill-opacity="0.45"/>'
                 '</g>')
    # front: lock screen
    b.append('<g transform="translate(800 520) translate(-300 -330)">'
             '<text x="300" y="150" text-anchor="middle" font-family="ui-sans-serif,system-ui" font-size="96" font-weight="800" fill="#E9F7F7">21:47</text>'
             '<rect x="210" y="190" width="180" height="14" rx="7" fill="#E9F7F7" fill-opacity="0.6"/>'
             '<circle cx="300" cy="275" r="38" fill="url(#dw-tile)" stroke="#E9F7F7" stroke-width="4"/>'
             '<rect x="170" y="335" width="260" height="46" rx="23" fill="#0A1A20" fill-opacity="0.55" stroke="#E9F7F7" stroke-opacity="0.5" stroke-width="2"/>'
             + ''.join(f'<circle cx="{215 + i * 26}" cy="358" r="6" fill="#E9F7F7"/>' for i in range(6)) +
             '</g>')
    # swatches row = 41 themes
    for i in range(14):
        x = 300 + i * 74
        col = ['#62EDD4', '#21BDB0', '#1388A6', '#0F5F78', '#A6D3D6', '#E9F7F7', '#167A8E'][i % 7]
        b.append(f'<rect x="{x}" y="900" width="52" height="52" rx="14" fill="{col}" fill-opacity="{0.95 if i == 4 else 0.55}"/>')
    b.append('<rect x="592" y="892" width="68" height="68" rx="18" fill="none" stroke="#E9F7F7" stroke-width="4"/>')
    return frame(u, ''.join(b), glow=(800, 480))


# ---------------------------------------------------------------- Insensical: multiplexer panes in a native window
def insensical():
    u = 'is'
    b = [window(140, 150, 1320, 700, u)]
    # tab strip
    for i, w in enumerate([210, 180, 160]):
        x = 300 + sum([210, 180, 160][:i]) + i * 14
        b.append(f'<rect x="{x}" y="166" width="{w}" height="30" rx="10" fill="{"#21BDB0" if i == 0 else "#62EDD4"}" fill-opacity="{0.9 if i == 0 else 0.15}"/>')
    # panes
    panes = [(170, 240, 640, 580), (830, 240, 600, 280), (830, 540, 600, 280)]
    for i, (x, y, w, h) in enumerate(panes):
        active = i == 0
        b.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="18" fill="#08191E" stroke="{"#62EDD4" if active else "#62EDD4"}" stroke-opacity="{0.8 if active else 0.15}" stroke-width="{4 if active else 2}"/>')
    # pane 1: agent conversation
    y = 290
    for w, c, o in [(380, '#62EDD4', 0.9), (520, '#A6D3D6', 0.4), (460, '#A6D3D6', 0.4), (300, '#A6D3D6', 0.4), (420, '#21BDB0', 0.9),
                    (500, '#A6D3D6', 0.4), (240, '#A6D3D6', 0.4)]:
        b.append(f'<rect x="210" y="{y}" width="{w}" height="16" rx="8" fill="{c}" fill-opacity="{o}"/>')
        y += 54
    b.append(f'<rect x="210" y="{y}" width="18" height="30" rx="3" fill="#62EDD4"/>')
    # pane 2: build output bars
    for i in range(7):
        h = 40 + ((i * 37) % 120)
        b.append(f'<rect x="{880 + i * 72}" y="{480 - h}" width="44" height="{h}" rx="10" fill="url(#is-tile)" fill-opacity="{0.4 + i * 0.08:.2f}"/>')
    # pane 3: log lines
    y = 585
    for i in range(5):
        b.append(f'<circle cx="884" cy="{y + 8}" r="8" fill="{["#62EDD4", "#21BDB0", "#1388A6"][i % 3]}"/>')
        b.append(f'<rect x="910" y="{y}" width="{300 + (i * 53) % 200}" height="14" rx="7" fill="#A6D3D6" fill-opacity="0.4"/>')
        y += 46
    return frame(u, ''.join(b), glow=(500, 500))


# ---------------------------------------------------------------- rrussat: peer-to-peer mesh, encrypted
def rrussat():
    u = 'rr'
    random.seed(21)
    nodes = [(380, 300), (640, 210), (900, 330), (1180, 240), (300, 620), (620, 520), (880, 640), (1200, 560), (1020, 470), (460, 800)]
    edges = [(0, 1), (1, 2), (2, 3), (0, 5), (4, 5), (5, 6), (6, 7), (2, 8), (8, 7), (5, 8), (4, 9), (9, 6), (1, 5), (3, 8)]
    b = []
    for a, c in edges:
        (x1, y1), (x2, y2) = nodes[a], nodes[c]
        b.append(f'<path d="M{x1} {y1}L{x2} {y2}" stroke="#62EDD4" stroke-opacity="0.35" stroke-width="3" stroke-dasharray="4 12" stroke-linecap="round"/>')
    # packets
    for a, c in [(0, 1), (5, 8), (6, 7), (2, 3)]:
        (x1, y1), (x2, y2) = nodes[a], nodes[c]
        mx, my = (x1 + x2) / 2, (y1 + y2) / 2
        b.append(f'<g transform="translate({mx:.0f} {my:.0f})"><rect x="-20" y="-14" width="40" height="28" rx="8" fill="#E9F7F7"/><path d="M-8 -14v-8a8 8 0 0 1 16 0v8" fill="none" stroke="#E9F7F7" stroke-width="5"/><circle r="4" fill="#0F5F78"/></g>')
    for i, (x, y) in enumerate(nodes):
        r = 46 if i in (5, 8) else 34
        b.append(f'<circle cx="{x}" cy="{y}" r="{r + 18}" fill="#21BDB0" fill-opacity="0.12"/>')
        b.append(f'<circle cx="{x}" cy="{y}" r="{r}" fill="url(#rr-tile)"/>')
        b.append(f'<path d="M{x - r * 0.42:.0f} {y - r * 0.2:.0f}l{r * 0.3:.0f} {r * 0.2:.0f}-{r * 0.3:.0f} {r * 0.2:.0f}M{x:.0f} {y + r * 0.22:.0f}h{r * 0.4:.0f}" fill="none" stroke="#043040" stroke-width="6" stroke-linecap="round" stroke-linejoin="round"/>')
    return frame(u, ''.join(b), glow=(760, 500))


ARTS = {
    'nibble': nibble,
    'nibble-cli': nibble_cli,
    'quarry': quarry,
    'sysman': sysman,
    'darwan': darwan,
    'insensical': insensical,
    'rrussat': rrussat,
}


# ---------------------------------------------------------------- TourHub: a lit stage, the crew behind it, paid up front
def tourhub():
    u = 'th'
    b = []
    # the stage: a truss with lamps throwing beams onto the deck, speaker stacks either side
    b.append('<rect x="150" y="180" width="760" height="22" rx="11" fill="#0E2B33" stroke="#62EDD4" stroke-opacity="0.25" stroke-width="2"/>')
    for k in range(12):
        x = 170 + k * 62
        b.append(f'<path d="M{x} 182L{x + 31} 200L{x + 62} 182" fill="none" stroke="#62EDD4" stroke-opacity="0.18" stroke-width="2"/>')
    for i, (x, tint) in enumerate([(250, '#62EDD4'), (420, '#21BDB0'), (640, '#62EDD4'), (810, '#1388A6')]):
        b.append(f'<path d="M{x - 14} 212L{x - 120 + i * 40} 720H{x + 130 - i * 30}L{x + 14} 212Z" fill="{tint}" fill-opacity="0.09"/>')
        b.append(f'<rect x="{x - 18}" y="200" width="36" height="30" rx="8" fill="url(#th-tile)"/>')
    b.append('<path d="M150 720H910" stroke="#62EDD4" stroke-opacity="0.35" stroke-width="4" stroke-linecap="round"/>')
    b.append('<rect x="150" y="724" width="760" height="70" rx="10" fill="#0E2B33"/>')
    for x in (150, 830):
        b.append(f'<rect x="{x}" y="470" width="80" height="250" rx="12" fill="#0B2229" stroke="#62EDD4" stroke-opacity="0.2" stroke-width="2"/>')
        for k, r in enumerate((22, 30, 22)):
            cy = 515 + k * 78
            b.append(f'<circle cx="{x + 40}" cy="{cy}" r="{r}" fill="none" stroke="#21BDB0" stroke-opacity="0.55" stroke-width="5"/><circle cx="{x + 40}" cy="{cy}" r="{r * 0.35:.0f}" fill="#21BDB0" fill-opacity="0.6"/>')
    # a mixing desk front of house
    b.append('<rect x="380" y="610" width="300" height="90" rx="14" fill="#0B2229" stroke="#62EDD4" stroke-opacity="0.25" stroke-width="2"/>')
    for k in range(10):
        x = 404 + k * 26
        h = 18 + (k * 7) % 30
        b.append(f'<rect x="{x}" y="{682 - h}" width="10" height="{h}" rx="5" fill="#62EDD4" fill-opacity="{0.35 + (k % 3) * 0.2}"/>')
    # crew cards: avatar, name, discipline, the tier earned on the road
    tiers = [('#A6D3D6', 1), ('#21BDB0', 2), ('#62EDD4', 3), ('#62EDD4', 4)]
    for i, (accent, level) in enumerate(tiers[1:]):
        y = 190 + i * 162
        x = 1000 + (i % 2) * 36
        b.append(f'<rect x="{x}" y="{y + 12}" width="440" height="132" rx="26" fill="#000" fill-opacity="0.35" filter="url(#th-soft)"/>')
        b.append(f'<rect x="{x}" y="{y}" width="440" height="132" rx="26" fill="#0E2B33" stroke="#62EDD4" stroke-opacity="0.18" stroke-width="2"/>')
        b.append(f'<circle cx="{x + 66}" cy="{y + 66}" r="38" fill="url(#th-tile)"/><circle cx="{x + 66}" cy="{y + 56}" r="13" fill="#0B2229" fill-opacity="0.55"/><path d="M{x + 42} {y + 92}C{x + 48} {y + 74} {x + 84} {y + 74} {x + 90} {y + 92}" fill="#0B2229" fill-opacity="0.55"/>')
        b.append(f'<path d="M{x + 92} {y + 34}l9 4v9c0 6-4 10-9 12-5-2-9-6-9-12v-9Z" fill="#62EDD4"/>')
        b.append(f'<rect x="{x + 128}" y="{y + 36}" width="{190 - i * 24}" height="16" rx="8" fill="#E9F7F7" fill-opacity="0.85"/>')
        b.append(f'<rect x="{x + 128}" y="{y + 66}" width="{130 + i * 18}" height="12" rx="6" fill="#A6D3D6" fill-opacity="0.4"/>')
        for k in range(4):
            on = k <= level - 1
            b.append(f'<rect x="{x + 128 + k * 44}" y="{y + 94}" width="36" height="10" rx="5" fill="{accent}" fill-opacity="{0.95 if on else 0.15}"/>')
    # payment secured before the show
    b.append('<rect x="1060" y="690" width="380" height="104" rx="26" fill="url(#th-tile)"/>')
    b.append('<path d="M1112 716l24 10v22c0 15-10 25-24 30-14-5-24-15-24-30v-22Z" fill="#043040" fill-opacity="0.85"/><path d="M1101 744l8 8 15-16" fill="none" stroke="#62EDD4" stroke-width="5" stroke-linecap="round" stroke-linejoin="round"/>')
    b.append('<rect x="1162" y="722" width="170" height="16" rx="8" fill="#043040" fill-opacity="0.8"/><rect x="1162" y="752" width="230" height="12" rx="6" fill="#043040" fill-opacity="0.45"/>')
    return frame(u, ''.join(b), glow=(520, 420))


# ---------------------------------------------------------------- TLC: a production web platform
def tlc():
    u = 'tl'
    b = [window(150, 150, 1300, 700, u, fill='#0B2229')]
    # address bar
    b.append('<rect x="300" y="166" width="560" height="30" rx="15" fill="#62EDD4" fill-opacity="0.1"/><circle cx="322" cy="181" r="6" fill="#62EDD4"/>')
    # sidebar nav
    for i in range(7):
        y = 260 + i * 70
        active = i == 1
        b.append(f'<rect x="180" y="{y}" width="230" height="48" rx="14" fill="#21BDB0" fill-opacity="{0.22 if active else 0}"/>')
        b.append(f'<rect x="200" y="{y + 16}" width="16" height="16" rx="5" fill="{"#62EDD4" if active else "#A6D3D6"}" fill-opacity="{1 if active else 0.5}"/>')
        b.append(f'<rect x="232" y="{y + 18}" width="{120 + (i * 29) % 50}" height="12" rx="6" fill="#E9F7F7" fill-opacity="{0.9 if active else 0.35}"/>')
    # kpi tiles
    for i in range(3):
        x = 450 + i * 320
        b.append(f'<rect x="{x}" y="250" width="290" height="150" rx="22" fill="#0E2B33" stroke="#62EDD4" stroke-opacity="0.14" stroke-width="2"/>')
        b.append(f'<rect x="{x + 28}" y="280" width="110" height="12" rx="6" fill="#A6D3D6" fill-opacity="0.5"/>')
        b.append(f'<rect x="{x + 28}" y="316" width="{150 - i * 20}" height="34" rx="10" fill="url(#tl-tile)"/>')
        pts = ' '.join(f'{x + 170 + k * 18},{360 - ((k * (i + 3) * 7) % 40)}' for k in range(6))
        b.append(f'<polyline points="{pts}" fill="none" stroke="#62EDD4" stroke-width="4" stroke-linecap="round" stroke-linejoin="round"/>')
    # table
    b.append('<rect x="450" y="430" width="930" height="380" rx="22" fill="#0E2B33" stroke="#62EDD4" stroke-opacity="0.14" stroke-width="2"/>')
    for r in range(6):
        y = 470 + r * 58
        if r:
            b.append(f'<path d="M470 {y - 18}H1360" stroke="#62EDD4" stroke-opacity="0.08" stroke-width="2"/>')
        b.append(f'<circle cx="500" cy="{y + 6}" r="14" fill="{["#62EDD4", "#21BDB0", "#1388A6"][r % 3]}" fill-opacity="{1 if r else 0}"/>')
        for c, w in enumerate([200, 160, 120, 140]):
            b.append(f'<rect x="{540 + c * 210}" y="{y}" width="{w * (0.6 + ((r + c) % 4) / 10):.0f}" height="12" rx="6" fill="{"#62EDD4" if r == 0 else "#A6D3D6"}" fill-opacity="{0.9 if r == 0 else 0.35}"/>')
        if r:
            b.append(f'<rect x="1270" y="{y - 6}" width="80" height="26" rx="13" fill="#21BDB0" fill-opacity="0.18" stroke="#21BDB0" stroke-opacity="0.5"/>')
    return frame(u, ''.join(b), glow=(900, 520))


ARTS['tourhub'] = tourhub
ARTS['tlc'] = tlc

# Pages, posts and the newer projects live in their own module, and add to ARTS.
sys.path.insert(0, str(Path(__file__).parent))
import more  # noqa: E402

ARTS.update(more.arts(frame, window, bars))

import marks  # noqa: E402

ARTS.update(marks.marks())

for name, fn in ARTS.items():
    target = OUT / f'{name}.svg'
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(fn())
    print('wrote', OUT / f'{name}.svg')
