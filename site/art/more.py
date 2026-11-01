"""Artwork for pages, posts and the newer projects, in the same language as the project covers.

generate.py passes in its frame (the midnight card with glow, corners and peel), window and bars helpers; each function
here returns a complete SVG. Names with a slash are written into that folder of public/art/.
"""
import math
import random

MINT, TEAL, SEA, DEEP, MIST, FOAM, ABYSS = '#62EDD4', '#21BDB0', '#1388A6', '#0F5F78', '#A6D3D6', '#E9F7F7', '#043040'


def arts(frame, window, bars):
    def rack(x, y, units=6, w=300, uid='x'):
        """A server rack with blinking units."""
        out = [f'<rect x="{x}" y="{y}" width="{w}" height="{units * 62 + 40}" rx="22" fill="#08191E" '
               f'stroke="{MINT}" stroke-opacity="0.2" stroke-width="2"/>']
        for i in range(units):
            uy = y + 20 + i * 62
            out.append(f'<rect x="{x + 18}" y="{uy}" width="{w - 36}" height="48" rx="10" fill="#0E2B33"/>')
            for j in range(3):
                out.append(f'<circle cx="{x + 42 + j * 22}" cy="{uy + 24}" r="6" fill="{[MINT, TEAL, SEA][(i + j) % 3]}" '
                           f'fill-opacity="{0.95 if (i + j) % 2 == 0 else 0.4}"/>')
            for k in range(5):
                out.append(f'<rect x="{x + 120 + k * 30}" y="{uy + 14}" width="18" height="20" rx="4" fill="{MIST}" fill-opacity="0.18"/>')
        return ''.join(out)

    def editor(x, y, w, h, uid, seed=3):
        random.seed(seed)
        out = [window(x, y, w, h, uid)]
        ly = y + 92
        while ly < y + h - 40:
            indent = random.choice([0, 0, 28, 28, 56])
            parts = random.randint(1, 3)
            lx = x + 40 + indent
            for p in range(parts):
                width = random.randint(40, 150)
                color = random.choice([MINT, MIST, MIST, TEAL, FOAM])
                out.append(f'<rect x="{lx}" y="{ly}" width="{width}" height="13" rx="6.5" fill="{color}" '
                           f'fill-opacity="{0.85 if color in (MINT, TEAL) else 0.4}"/>')
                lx += width + 14
            ly += 34
        return ''.join(out)

    def check(x, y, r=20, color=MINT):
        return (f'<circle cx="{x}" cy="{y}" r="{r}" fill="{color}"/>'
                f'<path d="M{x - r * 0.45} {y}l{r * 0.32} {r * 0.32} {r * 0.6}-{r * 0.62}" fill="none" stroke="{ABYSS}" '
                f'stroke-width="{r * 0.22}" stroke-linecap="round" stroke-linejoin="round"/>')

    def cylinder(cx, cy, rx, ry, h, uid, layers=3):
        out = []
        for i in range(layers):
            top = cy + i * h
            out.append(f'<path d="M{cx - rx} {top}V{top + h}A{rx} {ry} 0 0 0 {cx + rx} {top + h}V{top}" fill="url(#{uid}-tile)" '
                       f'fill-opacity="{1 - i * 0.15}"/>')
            out.append(f'<path d="M{cx - rx} {top + h}A{rx} {ry} 0 0 0 {cx + rx} {top + h}" fill="none" stroke="#0A1A20" '
                       f'stroke-opacity="0.35" stroke-width="3"/>')
        out.append(f'<ellipse cx="{cx}" cy="{cy}" rx="{rx}" ry="{ry}" fill="{FOAM}" fill-opacity="0.92"/>')
        return ''.join(out)

    def padlock(cx, cy, s, uid, color=None):
        return (f'<path d="M{cx - 60 * s} {cy}V{cy - 50 * s}a{60 * s} {60 * s} 0 0 1 {120 * s} 0V{cy}" fill="none" '
                f'stroke="{FOAM}" stroke-width="{22 * s}" stroke-linecap="round"/>'
                f'<rect x="{cx - 100 * s}" y="{cy - 6 * s}" width="{200 * s}" height="{160 * s}" rx="{32 * s}" '
                f'fill="{color or f"url(#{uid}-tile)"}"/>'
                f'<circle cx="{cx}" cy="{cy + 64 * s}" r="{20 * s}" fill="{ABYSS}"/>'
                f'<rect x="{cx - 8 * s}" y="{cy + 70 * s}" width="{16 * s}" height="{44 * s}" rx="{8 * s}" fill="{ABYSS}"/>')

    # ------------------------------------------------------------------ projects

    def tide():
        u = 'td'
        b = [window(150, 150, 1300, 700, u)]
        # the hairline across the top of the app: the status channel
        b.append(f'<rect x="150" y="212" width="1300" height="4" fill="url(#{u}-tile)"/>')
        # the Orbit stage: the speaker in the lens, everyone else a portal around it
        b.append(f'<circle cx="640" cy="520" r="250" fill="{MINT}" fill-opacity="0.06"/>')
        b.append(f'<circle cx="640" cy="520" r="212" fill="#0E2B33" stroke="{MINT}" stroke-width="6"/>')
        b.append(f'<circle cx="640" cy="520" r="226" fill="none" stroke="{MINT}" stroke-opacity="0.25" stroke-width="4"/>')
        b.append(f'<circle cx="640" cy="470" r="70" fill="url(#{u}-tile)"/><path d="M520 640C540 560 740 560 760 640" fill="url(#{u}-tile)"/>')
        for i, (x, y, r, c) in enumerate([(990, 330, 74, TEAL), (1130, 470, 64, SEA), (1000, 640, 70, MIST), (300, 360, 60, SEA)]):
            b.append(f'<circle cx="{x}" cy="{y}" r="{r}" fill="#0E2B33" stroke="{MINT}" stroke-opacity="0.3" stroke-width="3"/>')
            b.append(f'<circle cx="{x}" cy="{y - r * 0.2:.0f}" r="{r * 0.36:.0f}" fill="{c}" fill-opacity="0.8"/>')
        # the control capsule
        b.append(f'<rect x="880" y="760" width="400" height="64" rx="32" fill="#071419" stroke="{MINT}" stroke-opacity="0.3" stroke-width="2"/>')
        for k in range(5):
            cx = 926 + k * 76
            fill = '#E5484D' if k == 4 else (MINT if k == 0 else MIST)
            b.append(f'<circle cx="{cx}" cy="792" r="20" fill="{fill}" fill-opacity="{0.9 if k in (0, 4) else 0.35}"/>')
        # a chat sheet
        b.append(f'<rect x="180" y="560" width="200" height="250" rx="24" fill="#0E2B33" stroke="{MINT}" stroke-opacity="0.18" stroke-width="2"/>')
        b.append(bars(204, 600, [140, 100, 150, 90, 130], gap=36, h=12, colors=[FOAM, MIST, MINT, MIST, FOAM]))
        return frame(u, ''.join(b), glow=(640, 520))

    def earport():
        u = 'ep'
        b = []
        # a bar along the top of a Hyprland desktop, with the plugin's widget
        b.append(f'<rect x="150" y="150" width="1300" height="64" rx="20" fill="#071419" stroke="{MINT}" stroke-opacity="0.2" stroke-width="2"/>')
        b.append(bars(184, 176, [70, 50, 90], gap=0, h=12, colors=[MIST]).replace('<rect ', '<rect ', 1))
        b.append(f'<rect x="1130" y="164" width="150" height="36" rx="18" fill="{TEAL}" fill-opacity="0.22"/>')
        b.append(f'<circle cx="1160" cy="182" r="10" fill="{MINT}"/><rect x="1180" y="176" width="80" height="12" rx="6" fill="{FOAM}"/>')
        # the panel it opens
        b.append(f'<g transform="translate(640 270)"><rect y="18" width="760" height="560" rx="36" fill="#000" fill-opacity="0.45" '
                 f'filter="url(#{u}-soft)"/><rect width="760" height="560" rx="36" fill="#0E2B33" stroke="{MINT}" stroke-opacity="0.35" '
                 f'stroke-width="2"/></g>')
        # battery rings: left, right, case
        for i, (cx, level) in enumerate([(780, 0.85), (980, 0.82), (1180, 0.64)]):
            r = 70
            circ = 2 * 3.14159 * r
            b.append(f'<circle cx="{cx}" cy="420" r="{r}" fill="none" stroke="{MIST}" stroke-opacity="0.15" stroke-width="16"/>')
            b.append(f'<circle cx="{cx}" cy="420" r="{r}" fill="none" stroke="url(#{u}-tile)" stroke-width="16" stroke-linecap="round" '
                     f'stroke-dasharray="{circ * level:.1f} {circ:.1f}" transform="rotate(-90 {cx} 420)"/>')
            if i < 2:
                b.append(f'<path d="M{cx - 12} 392a18 18 0 0 1 36 0v18c0 10-6 14-12 14v26a6 6 0 0 1-12 0Z" fill="{FOAM}"/>')
            else:
                b.append(f'<rect x="{cx - 30}" y="396" width="60" height="48" rx="14" fill="{FOAM}"/><path d="M{cx - 30} 412h60" stroke="#0E2B33" stroke-width="4"/>')
        # noise control: off, ANC, transparency, adaptive
        for k in range(4):
            x = 700 + k * 165
            on = k == 1
            b.append(f'<rect x="{x}" y="560" width="145" height="90" rx="22" fill="{TEAL if on else "#071419"}" fill-opacity="{0.35 if on else 0.8}" '
                     f'stroke="{MINT}" stroke-opacity="{0.8 if on else 0.15}" stroke-width="2"/>')
            b.append(f'<rect x="{x + 30}" y="598" width="{85 - k * 6}" height="14" rx="7" fill="{FOAM if on else MIST}" fill-opacity="{0.95 if on else 0.4}"/>')
        b.append(bars(700, 700, [380, 260], gap=34, h=12, colors=[MIST]))
        # a pair of AirPods
        b.append(f'<g transform="translate(250 380)" fill="url(#{u}-tile)"><path d="M60 0a60 60 0 0 1 60 60v40c0 30-20 40-36 40v120a24 24 0 0 1-48 0V130C14 120 0 100 0 70V60A60 60 0 0 1 60 0Z"/>'
                 f'<path d="M260 0a60 60 0 0 0-60 60v40c0 30 20 40 36 40v120a24 24 0 0 0 48 0V130c22-10 36-30 36-60V60A60 60 0 0 0 260 0Z"/></g>')
        return frame(u, ''.join(b), glow=(500, 480))

    def about():
        u = 'ab'
        b = [rack(160, 250, 7, 320, u)]
        b.append(editor(980, 200, 470, 560, u, seed=7))
        # the bridge between them
        b.append(f'<path d="M480 520C640 520 640 420 800 420S940 520 980 480" fill="none" stroke="url(#{u}-line)" stroke-width="6" '
                 f'stroke-dasharray="2 16" stroke-linecap="round"/>')
        b.append(f'<g transform="translate(720 430)"><circle r="92" fill="#21BDB0" fill-opacity="0.15"/>'
                 f'<circle r="66" fill="url(#{u}-tile)"/>'
                 f'<path d="M-30 -14l-22 14 22 14M30 -14l22 14-22 14M10 -26l-20 52" fill="none" stroke="{ABYSS}" stroke-width="9" '
                 f'stroke-linecap="round" stroke-linejoin="round"/></g>')
        # years as a row of ticks
        for i in range(18):
            x = 190 + i * 70
            b.append(f'<rect x="{x}" y="{170 - (16 if i % 5 == 0 else 0)}" width="6" height="{24 + (16 if i % 5 == 0 else 0)}" rx="3" '
                     f'fill="{MINT if i == 17 else MIST}" fill-opacity="{0.9 if i in (0, 17) else 0.35}"/>')
        return frame(u, ''.join(b), glow=(720, 430))

    def now():
        u = 'nw'
        b = [window(170, 190, 760, 620, u)]
        rows = [(True, 420), (True, 340), (True, 380), (False, 300), (False, 360)]
        for i, (done, w) in enumerate(rows):
            y = 300 + i * 96
            if done:
                b.append(check(230, y + 8, 20))
            else:
                b.append(f'<circle cx="230" cy="{y + 8}" r="20" fill="none" stroke="{MINT}" stroke-width="5" stroke-opacity="0.6"/>')
            b.append(f'<rect x="276" y="{y}" width="{w}" height="16" rx="8" fill="{FOAM}" fill-opacity="{0.45 if done else 0.85}"/>')
            b.append(f'<rect x="276" y="{y + 30}" width="{w - 120}" height="10" rx="5" fill="{MIST}" fill-opacity="0.3"/>')
        # a progress ring
        cx, cy, r = 1200, 470, 190
        circ = 2 * math.pi * r
        b.append(f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="{MINT}" stroke-opacity="0.12" stroke-width="36"/>')
        b.append(f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="url(#{u}-tile)" stroke-width="36" stroke-linecap="round" '
                 f'stroke-dasharray="{circ * 0.68:.1f} {circ:.1f}" transform="rotate(-90 {cx} {cy})"/>')
        b.append(f'<circle cx="{cx}" cy="{cy}" r="120" fill="#0E2B33"/>')
        b.append(f'<path d="M{cx} {cy - 70}V{cy}l46 30" fill="none" stroke="{FOAM}" stroke-width="14" stroke-linecap="round" '
                 f'stroke-linejoin="round"/><circle cx="{cx}" cy="{cy}" r="12" fill="{MINT}"/>')
        return frame(u, ''.join(b), glow=(1200, 470))

    def uses():
        u = 'us'
        b = []
        labels = ['F1', 'F2', 'F3', 'F4', 'F5', 'F6']
        rows = [(6, 0), (5, 50), (5, 90)]
        for r, (count, offset) in enumerate(rows):
            for c in range(count):
                x = 210 + offset + c * 200
                y = 230 + r * 190
                lit = (r, c) in ((0, 2), (1, 1), (2, 3))
                b.append(f'<rect x="{x}" y="{y + 18}" width="170" height="160" rx="30" fill="#000" fill-opacity="0.45" filter="url(#{u}-soft)"/>')
                b.append(f'<rect x="{x}" y="{y + 12}" width="170" height="156" rx="30" fill="{DEEP if lit else "#0A2128"}"/>')
                b.append(f'<rect x="{x}" y="{y}" width="170" height="150" rx="30" fill="{"url(#" + u + "-tile)" if lit else "#123640"}" '
                         f'stroke="{MINT}" stroke-opacity="{0.0 if lit else 0.18}" stroke-width="2"/>')
                b.append(f'<rect x="{x + 18}" y="{y + 14}" width="134" height="40" rx="14" fill="#FFFFFF" fill-opacity="{0.25 if lit else 0.05}"/>')
                if r == 0:
                    b.append(f'<text x="{x + 30}" y="{y + 56}" font-family="ui-monospace,Menlo,monospace" font-size="26" '
                             f'font-weight="700" fill="{ABYSS if lit else MIST}" fill-opacity="{1 if lit else 0.6}">{labels[c]}</text>')
                b.append(f'<rect x="{x + 30}" y="{y + 100}" width="{70 + (c * 17) % 50}" height="14" rx="7" '
                         f'fill="{ABYSS if lit else MIST}" fill-opacity="{0.8 if lit else 0.35}"/>')
        return frame(u, ''.join(b), glow=(800, 420))

    # ------------------------------------------------------------------ posts

    def seventeen_years():
        u = 's17'
        b = []
        # the line, with code on one side and servers on the other
        b.append(f'<path d="M800 120V880" stroke="{MINT}" stroke-opacity="0.5" stroke-width="4" stroke-dasharray="4 14" stroke-linecap="round"/>')
        b.append(editor(150, 220, 560, 520, u, seed=17))
        b.append(rack(900, 230, 7, 330, u))
        b.append(f'<g transform="translate(800 500)"><circle r="78" fill="#0A1A20" stroke="{MINT}" stroke-width="5"/>'
                 f'<text y="22" text-anchor="middle" font-family="ui-sans-serif,system-ui" font-size="64" font-weight="800" '
                 f'fill="{FOAM}">17</text></g>')
        b.append(f'<path d="M1280 330L1430 330M1280 420L1400 420M1280 510L1440 510" stroke="{MIST}" stroke-opacity="0.25" '
                 f'stroke-width="10" stroke-linecap="round"/>')
        return frame(u, ''.join(b), glow=(800, 500))

    def cms_i_built():
        u = 'cms'
        b = [window(160, 200, 500, 560, u)]
        y = 300
        for name_w, kind_w in [(200, 70), (150, 90), (230, 80), (130, 100), (180, 60)]:
            b.append(f'<rect x="200" y="{y}" width="14" height="14" rx="4" fill="{TEAL}"/>')
            b.append(f'<rect x="232" y="{y}" width="{name_w}" height="14" rx="7" fill="{FOAM}" fill-opacity="0.85"/>')
            b.append(f'<rect x="{620 - kind_w}" y="{y - 6}" width="{kind_w}" height="26" rx="13" fill="{TEAL}" fill-opacity="0.18" '
                     f'stroke="{TEAL}" stroke-opacity="0.5"/>')
            y += 80
        b.append(f'<path d="M680 480H860" stroke="url(#{u}-line)" stroke-width="6" stroke-dasharray="2 14" stroke-linecap="round"/>')
        b.append(f'<path d="M840 460l26 20-26 20" fill="none" stroke="{MINT}" stroke-width="6" stroke-linecap="round" stroke-linejoin="round"/>')
        # the rendered page, stacked with its own corner brackets
        b.append(window(900, 170, 540, 640, u, fill='#0E2B33'))
        b.append(f'<rect x="950" y="260" width="440" height="200" rx="22" fill="url(#{u}-tile)"/>')
        b.append(f'<path d="M985 300V284Q985 274 995 274H1011M1355 300V284Q1355 274 1345 274H1329M985 420V436Q985 446 995 446H1011" '
                 f'fill="none" stroke="#fff" stroke-width="7" stroke-linecap="round"/>')
        b.append(bars(950, 500, [380, 300, 340, 220], gap=40, h=16, colors=[FOAM]))
        b.append(f'<rect x="950" y="700" width="160" height="52" rx="26" fill="{MINT}"/>')
        return frame(u, ''.join(b), glow=(1170, 420))

    def sqlite_is_enough():
        u = 'sq'
        b = []
        # one file
        b.append(f'<g transform="translate(260 230)"><path d="M0 0H300L420 120V540H0Z" fill="#0E2B33" stroke="{MINT}" stroke-opacity="0.4" '
                 f'stroke-width="3"/><path d="M300 0V120H420" fill="#123640" stroke="{MINT}" stroke-opacity="0.4" stroke-width="3"/>'
                 + cylinder(210, 230, 110, 34, 64, u) +
                 f'<rect x="80" y="470" width="260" height="18" rx="9" fill="{FOAM}" fill-opacity="0.85"/></g>')
        # WAL pages flowing
        for i in range(4):
            b.append(f'<rect x="{760 + i * 40}" y="{330 + i * 34}" width="150" height="190" rx="18" fill="#123640" '
                     f'stroke="{MINT}" stroke-opacity="{0.2 + i * 0.15}" stroke-width="2"/>')
        b.append(f'<text x="880" y="520" font-family="ui-monospace,Menlo,monospace" font-size="34" font-weight="700" fill="{MINT}">-wal</text>')
        # an off-site backup
        b.append(f'<path d="M700 640C900 760 1060 760 1200 640" fill="none" stroke="url(#{u}-line)" stroke-width="6" '
                 f'stroke-dasharray="2 14" stroke-linecap="round"/>')
        b.append(f'<g transform="translate(1210 470)"><path d="M0 100a80 80 0 0 1 60-150a100 100 0 0 1 190 30a70 70 0 0 1 0 120Z" '
                 f'fill="url(#{u}-tile)"/><path d="M125 40V110M95 80l30 30 30-30" fill="none" stroke="{ABYSS}" stroke-width="12" '
                 f'stroke-linecap="round" stroke-linejoin="round"/></g>')
        return frame(u, ''.join(b), glow=(470, 500))

    def last_reading():
        u = 'lr'
        random.seed(5)
        b = [window(150, 180, 1000, 640, u)]
        gx, gy, gw, gh = 210, 300, 820, 420
        pts, v = [], 0.4
        for i in range(36):
            v = max(0.1, min(0.95, v + random.uniform(-0.06, 0.08) + (0.02 if i > 24 else 0)))
            pts.append((gx + i * gw / 40, gy + gh - v * gh))
        d = 'M' + ' L'.join(f'{x:.1f} {y:.1f}' for x, y in pts)
        b.append(f'<path d="{d} L{pts[-1][0]:.1f} {gy + gh} L{gx} {gy + gh}Z" fill="{MINT}" fill-opacity="0.12"/>')
        b.append(f'<path d="{d}" fill="none" stroke="{MINT}" stroke-width="6" stroke-linejoin="round" stroke-linecap="round"/>')
        lx, ly = pts[-1]
        b.append(f'<path d="M{lx:.0f} {gy - 20}V{gy + gh}" stroke="#FF8F8F" stroke-opacity="0.8" stroke-width="3" stroke-dasharray="8 8"/>')
        b.append(f'<circle cx="{lx:.0f}" cy="{ly:.0f}" r="16" fill="#0B2229" stroke="{MINT}" stroke-width="7"/>')
        # the bolt
        b.append(f'<path d="M{lx + 70:.0f} {gy + 20}l-50 110h44l-34 100 90-140h-46l40-70z" fill="#FFD27A"/>')
        # a disk that kept it
        b.append(f'<g transform="translate(1220 380)"><rect width="220" height="260" rx="28" fill="url(#{u}-tile)"/>'
                 f'<rect x="40" y="0" width="140" height="80" rx="8" fill="{ABYSS}" fill-opacity="0.45"/>'
                 f'<rect x="40" y="140" width="140" height="90" rx="14" fill="{FOAM}" fill-opacity="0.9"/>'
                 + check(110, 185, 26) + '</g>')
        b.append(f'<path d="M{lx + 20:.0f} {ly:.0f}C1150 {ly:.0f} 1150 500 1215 500" fill="none" stroke="url(#{u}-line)" '
                 f'stroke-width="5" stroke-dasharray="2 12" stroke-linecap="round"/>')
        return frame(u, ''.join(b), glow=(1000, 460))

    def gpui():
        u = 'gp'
        b = []
        # a GPU
        b.append(f'<g transform="translate(170 320)"><rect width="520" height="300" rx="34" fill="#0E2B33" stroke="{MINT}" '
                 f'stroke-opacity="0.35" stroke-width="2"/>'
                 + ''.join(f'<circle cx="{150 + i * 220}" cy="150" r="96" fill="#071419" stroke="{MINT}" stroke-opacity="0.3" stroke-width="3"/>'
                           f'<circle cx="{150 + i * 220}" cy="150" r="30" fill="url(#{u}-tile)"/>' for i in range(2))
                 + ''.join(f'<rect x="{40 + i * 40}" y="300" width="24" height="40" rx="4" fill="{MINT}" fill-opacity="0.5"/>' for i in range(11))
                 + '</g>')
        b.append(f'<path d="M700 470H820" stroke="url(#{u}-line)" stroke-width="6" stroke-dasharray="2 14" stroke-linecap="round"/>')
        # a native window with a smooth chart
        b.append(window(840, 200, 600, 560, u))
        random.seed(11)
        cx0, cy0, cw, ch = 880, 300, 520, 300
        v, pts = 0.5, []
        for i in range(30):
            v = max(0.15, min(0.9, v + random.uniform(-0.1, 0.1)))
            pts.append((cx0 + i * cw / 29, cy0 + ch - v * ch))
        d = 'M' + ' L'.join(f'{x:.1f} {y:.1f}' for x, y in pts)
        b.append(f'<path d="{d}" fill="none" stroke="{MINT}" stroke-width="5" stroke-linejoin="round"/>')
        b.append(f'<path d="{d} L{cx0 + cw} {cy0 + ch} L{cx0} {cy0 + ch}Z" fill="{MINT}" fill-opacity="0.1"/>')
        for i in range(4):
            b.append(f'<rect x="{880 + i * 132}" y="640" width="110" height="80" rx="16" fill="#0E2B33" stroke="{MINT}" stroke-opacity="0.15"/>'
                     f'<rect x="{900 + i * 132}" y="664" width="{50 + i * 12}" height="12" rx="6" fill="{[MINT, TEAL, SEA, MIST][i]}"/>')
        return frame(u, ''.join(b), glow=(1140, 470))

    def lock_screen():
        u = 'ls'
        b = []
        # supervisor loop
        cx, cy, r = 800, 500, 270
        b.append(f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="{MINT}" stroke-opacity="0.18" stroke-width="22"/>')
        b.append(f'<path d="M{cx} {cy - r}A{r} {r} 0 1 1 {cx - r * 0.95:.0f} {cy - r * 0.3:.0f}" fill="none" stroke="url(#{u}-tile)" '
                 f'stroke-width="22" stroke-linecap="round"/>')
        b.append(f'<path d="M{cx - r * 0.95 - 36:.0f} {cy - r * 0.3 - 10:.0f}l36 -44 30 50z" fill="{MINT}"/>')
        b.append(padlock(cx, cy - 10, 1.25, u))
        # the fallback prompt
        b.append(f'<g transform="translate(1150 640)"><rect width="300" height="90" rx="24" fill="#0E2B33" stroke="{MINT}" stroke-opacity="0.5" '
                 f'stroke-width="2"/>' + ''.join(f'<circle cx="{50 + i * 34}" cy="45" r="9" fill="{FOAM}"/>' for i in range(6)) + '</g>')
        # the helper's shield
        b.append(f'<g transform="translate(240 300)"><path d="M100 0L200 40V140C200 210 150 250 100 270C50 250 0 210 0 140V40Z" '
                 f'fill="#0E2B33" stroke="{MINT}" stroke-opacity="0.6" stroke-width="4"/>' + check(100, 130, 40) + '</g>')
        return frame(u, ''.join(b), glow=(800, 500))

    def ai_agents():
        u = 'ai'
        b = []
        agents = [(260, 280), (260, 500), (260, 720), (470, 390), (470, 610)]
        for x, y in agents:
            b.append(f'<path d="M{x + 50} {y}C620 {y} 620 500 700 500" fill="none" stroke="{MINT}" stroke-opacity="0.3" stroke-width="3" '
                     f'stroke-dasharray="3 12" stroke-linecap="round"/>')
        for x, y in agents:
            b.append(f'<circle cx="{x}" cy="{y}" r="64" fill="#21BDB0" fill-opacity="0.12"/><circle cx="{x}" cy="{y}" r="46" fill="url(#{u}-tile)"/>'
                     f'<rect x="{x - 22}" y="{y - 12}" width="14" height="22" rx="7" fill="{ABYSS}"/>'
                     f'<rect x="{x + 8}" y="{y - 12}" width="14" height="22" rx="7" fill="{ABYSS}"/>')
        # the gate: approval
        b.append(f'<g transform="translate(700 340)"><rect width="300" height="320" rx="40" fill="#0E2B33" stroke="{MINT}" stroke-opacity="0.6" '
                 f'stroke-width="3"/><rect x="40" y="50" width="220" height="16" rx="8" fill="{FOAM}" fill-opacity="0.8"/>'
                 f'<rect x="40" y="86" width="160" height="12" rx="6" fill="{MIST}" fill-opacity="0.35"/>'
                 + check(150, 200, 48) + '</g>')
        b.append(f'<path d="M1010 500H1130" stroke="url(#{u}-line)" stroke-width="6" stroke-dasharray="2 14" stroke-linecap="round"/>')
        # production
        b.append(rack(1150, 300, 6, 290, u))
        return frame(u, ''.join(b), glow=(850, 500))

    def release_scripts():
        u = 'rs'
        b = [window(160, 190, 620, 640, u)]
        for i in range(7):
            y = 290 + i * 70
            b.append(check(220, y + 8, 18))
            b.append(f'<rect x="258" y="{y}" width="{360 - (i * 37) % 160}" height="15" rx="7.5" fill="{FOAM}" fill-opacity="0.7"/>')
        b.append(f'<rect x="200" y="{290 + 7 * 70 - 6}" width="520" height="2" fill="{MINT}" fill-opacity="0.3"/>')
        # one question
        b.append(f'<g transform="translate(830 220)"><rect width="300" height="150" rx="30" fill="url(#{u}-tile)"/>'
                 f'<text x="150" y="102" text-anchor="middle" font-family="ui-sans-serif,system-ui" font-size="72" font-weight="800" '
                 f'fill="{ABYSS}">?</text></g>')
        # then everything
        stages = ['tag', 'build', 'notes', 'aur', 'brew', 'docs']
        for i, _ in enumerate(stages):
            x = 860 + (i % 3) * 190
            y = 470 + (i // 3) * 170
            b.append(f'<rect x="{x}" y="{y}" width="160" height="130" rx="26" fill="#0E2B33" stroke="{MINT}" stroke-opacity="0.35" '
                     f'stroke-width="2"/>' + check(x + 80, y + 52, 24) +
                     f'<rect x="{x + 40}" y="{y + 92}" width="80" height="12" rx="6" fill="{MIST}" fill-opacity="0.45"/>')
        return frame(u, ''.join(b), glow=(1000, 520))

    def default_post():
        u = 'df'
        b = []
        for i in range(5):
            r = 120 + i * 70
            b.append(f'<circle cx="800" cy="500" r="{r}" fill="none" stroke="{MINT}" stroke-opacity="{0.35 - i * 0.06:.2f}" stroke-width="3"/>')
        b.append(f'<rect x="680" y="380" width="240" height="240" rx="60" fill="url(#{u}-tile)"/>')
        b.append(f'<path d="M720 450V430Q720 420 730 420H750M880 450V430Q880 420 870 420H850M720 550V570Q720 580 730 580H750" '
                 f'fill="none" stroke="#fff" stroke-width="10" stroke-linecap="round"/>')
        return frame(u, ''.join(b), glow=(800, 500))

    def own_website_test_suite():
        u = 'ow'
        b = [window(150, 170, 820, 660, u)]
        # a documentation site: nested pages
        for i in range(10):
            depth = 1 if i in (2, 3, 6, 7, 8) else 0
            b.append(f'<rect x="{190 + depth * 26}" y="{262 + i * 52}" width="{150 - depth * 30}" height="12" rx="6" fill="{MIST}" '
                     f'fill-opacity="{0.9 if i == 5 else 0.35}"/>')
        b.append(f'<rect x="420" y="262" width="320" height="26" rx="13" fill="{FOAM}" fill-opacity="0.9"/>')
        b.append(bars(420, 320, [500, 460, 480, 300, 420], gap=34, h=12, colors=[MIST]))
        b.append(f'<rect x="420" y="520" width="500" height="220" rx="18" fill="#071419" stroke="{MINT}" stroke-opacity="0.2"/>')
        b.append(bars(450, 556, [200, 320, 260, 180], gap=40, h=12, colors=[MINT, TEAL, MIST, MIST]))
        # seven patch releases in one night
        for i in range(7):
            y = 210 + i * 86
            x = 1040 + (i % 2) * 30
            b.append(f'<rect x="{x}" y="{y}" width="360" height="64" rx="20" fill="#0E2B33" stroke="{MINT}" stroke-opacity="0.3" stroke-width="2"/>')
            b.append(f'<circle cx="{x + 34}" cy="{y + 32}" r="14" fill="url(#{u}-tile)"/>'
                     f'<path d="M{x + 27} {y + 32}l5 5 9-10" fill="none" stroke="{ABYSS}" stroke-width="4" stroke-linecap="round" stroke-linejoin="round"/>')
            b.append(f'<text x="{x + 64}" y="{y + 42}" font-family="ui-monospace,Menlo,monospace" font-size="26" font-weight="700" fill="{FOAM}">0.14.{i + 1}</text>')
            b.append(f'<rect x="{x + 200}" y="{y + 26}" width="{120 - (i * 13) % 50}" height="12" rx="6" fill="{MIST}" fill-opacity="0.4"/>')
        return frame(u, ''.join(b), glow=(1200, 480))

    def security_in_the_browser():
        u = 'sb'
        b = [window(150, 190, 820, 620, u)]
        # the lock that lived in the browser
        b.append(f'<rect x="170" y="250" width="780" height="540" rx="18" fill="#071419" fill-opacity="0.75"/>')
        b.append(padlock(560, 470, 1.0, u))
        b.append(f'<rect x="440" y="680" width="240" height="40" rx="20" fill="{FOAM}" fill-opacity="0.12" stroke="{MINT}" stroke-opacity="0.4"/>')
        # a reload walking round it
        b.append(f'<path d="M820 300a70 70 0 1 1-60 -35" fill="none" stroke="{MINT}" stroke-width="10" stroke-linecap="round"/>'
                 f'<path d="M742 236l20 30 30-22" fill="none" stroke="{MINT}" stroke-width="10" stroke-linecap="round" stroke-linejoin="round"/>')
        # the session on the server, which is where it ends now
        b.append(f'<g transform="translate(1080 280)"><rect y="16" width="340" height="440" rx="34" fill="#000" fill-opacity="0.4" '
                 f'filter="url(#{u}-soft)"/><rect width="340" height="440" rx="34" fill="#0E2B33" stroke="{MINT}" stroke-opacity="0.35" stroke-width="2"/>'
                 + ''.join(f'<rect x="40" y="{50 + k * 80}" width="260" height="56" rx="14" fill="#071419" stroke="{MINT}" stroke-opacity="0.2"/>'
                           f'<circle cx="74" cy="{78 + k * 80}" r="9" fill="{MINT if k < 3 else "#FF7A6B"}"/>'
                           f'<rect x="100" y="{72 + k * 80}" width="{150 - k * 15}" height="12" rx="6" fill="{MIST}" fill-opacity="0.5"/>' for k in range(4))
                 + f'<rect x="40" y="380" width="260" height="28" rx="14" fill="url(#{u}-tile)"/></g>')
        b.append(f'<path d="M980 500H1060" stroke="url(#{u}-line)" stroke-width="6" stroke-dasharray="2 14" stroke-linecap="round"/>')
        return frame(u, ''.join(b), glow=(1250, 500))

    def strangers_can_upgrade():
        u = 'su'
        b = []

        def folder(x, y, w, h, op):
            return (f'<g transform="translate({x} {y})" opacity="{op}"><path d="M0 30Q0 0 30 0H{w * 0.36:.0f}l30 34H{w - 30}Q{w} 34 {w} 64V{h - 30}'
                    f'Q{w} {h} {w - 30} {h}H30Q0 {h} 0 {h - 30}Z" fill="url(#{u}-tile)"/>'
                    f'<rect x="40" y="{h - 70}" width="{w * 0.5:.0f}" height="16" rx="8" fill="{ABYSS}" fill-opacity="0.6"/></g>')
        b.append(folder(210, 330, 380, 300, 0.35))
        b.append(folder(250, 290, 380, 300, 1))
        b.append(f'<text x="290" y="520" font-family="ui-monospace,Menlo,monospace" font-size="34" font-weight="700" fill="{ABYSS}">vendor/nibble</text>')
        # swap arrows
        b.append(f'<path d="M690 400H860M820 360l40 40-40 40" fill="none" stroke="{MINT}" stroke-width="10" stroke-linecap="round" stroke-linejoin="round"/>')
        b.append(f'<path d="M860 560H690M730 520l-40 40 40 40" fill="none" stroke="{MIST}" stroke-opacity="0.5" stroke-width="10" stroke-linecap="round" stroke-linejoin="round"/>')
        # the manifest: a checksum per file, one edit refused
        b.append(f'<g transform="translate(940 220)"><rect width="480" height="560" rx="30" fill="#0E2B33" stroke="{MINT}" stroke-opacity="0.35" stroke-width="2"/>'
                 + ''.join(f'<rect x="36" y="{44 + k * 66}" width="408" height="46" rx="12" fill="#071419" stroke="{"#FF7A6B" if k == 4 else MINT}" '
                           f'stroke-opacity="{0.9 if k == 4 else 0.15}"/><rect x="60" y="{61 + k * 66}" width="{120 + (k * 37) % 90}" height="12" rx="6" fill="{MIST}" fill-opacity="0.5"/>'
                           f'<rect x="300" y="{61 + k * 66}" width="90" height="12" rx="6" fill="{MINT if k != 4 else "#FF7A6B"}" fill-opacity="0.7"/>' for k in range(7))
                 + '</g>')
        return frame(u, ''.join(b), glow=(450, 460))

    def rewrite_history():
        u = 'rh'
        b = []
        # thirty-six migrations
        for i in range(36):
            col, row = i % 4, i // 4
            b.append(f'<rect x="{180 + col * 88}" y="{200 + row * 62}" width="76" height="44" rx="10" fill="#0E2B33" stroke="{MINT}" stroke-opacity="0.25"/>')
        b.append(f'<path d="M560 480C620 480 620 480 680 480M640 440l40 40-40 40" fill="none" stroke="{MINT}" stroke-width="10" stroke-linecap="round" stroke-linejoin="round"/>')
        # one per table
        for k in range(6):
            b.append(f'<rect x="720" y="{230 + k * 92}" width="260" height="70" rx="16" fill="url(#{u}-tile)" fill-opacity="{1 - k * 0.08:.2f}"/>'
                     f'<rect x="748" y="{259 + k * 92}" width="{150 - (k * 23) % 60}" height="12" rx="6" fill="{ABYSS}" fill-opacity="0.6"/>')
        # schema before and after, equal
        for j, x in enumerate((1060, 1270)):
            b.append(f'<rect x="{x}" y="260" width="170" height="440" rx="20" fill="#0E2B33" stroke="{MINT}" stroke-opacity="0.3" stroke-width="2"/>')
            b.append(bars(x + 24, 300, [110, 80, 120, 70, 100, 90, 60, 110, 80], gap=40, h=10, colors=[MIST]))
        b.append(f'<path d="M1240 450h22M1240 474h22" stroke="{MINT}" stroke-width="8" stroke-linecap="round"/>')
        return frame(u, ''.join(b), glow=(850, 480))

    return {
        'tide': tide,
        'earport': earport,
        'pages/about': about,
        'pages/now': now,
        'pages/uses': uses,
        'posts/seventeen-years': seventeen_years,
        'posts/cms-i-built': cms_i_built,
        'posts/sqlite-is-enough': sqlite_is_enough,
        'posts/last-reading': last_reading,
        'posts/gpui': gpui,
        'posts/lock-screen': lock_screen,
        'posts/ai-agents': ai_agents,
        'posts/release-scripts': release_scripts,
        'posts/own-website-test-suite': own_website_test_suite,
        'posts/security-in-the-browser': security_in_the_browser,
        'posts/strangers-can-upgrade': strangers_can_upgrade,
        'posts/rewrite-history': rewrite_history,
        'posts/default': default_post,
    }
