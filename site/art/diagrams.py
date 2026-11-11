"""Technical diagrams for blog posts, drawn on the same midnight card as the covers.

Posts show them at about 750 px wide, half the 1600 px card, so no text here is smaller than 30 units.
"""
import math
from xml.sax.saxutils import escape

MINT, TEAL, SEA, DEEP, MIST, FOAM, ABYSS = '#62EDD4', '#21BDB0', '#1388A6', '#0F5F78', '#A6D3D6', '#E9F7F7', '#043040'
CORAL = '#FF7A6B'
BOX = '#0E2B33'
SANS = 'Inter, ui-sans-serif, system-ui, sans-serif'
MONO = 'JetBrains Mono, ui-monospace, monospace'
# Monospace fonts draw → at half width; borrow the sans one.
ARROW = f'<tspan font-family="{SANS}">→</tspan>'


def diagrams(frame, window, bars):
    def text(x, y, s, size=30, fill=FOAM, mono=False, weight=None, anchor='start', extra=''):
        w = f' font-weight="{weight}"' if weight else ''
        a = f' text-anchor="{anchor}"' if anchor != 'start' else ''
        return (f'<text x="{x}" y="{y}" font-family="{MONO if mono else SANS}" font-size="{size}"{w}{a} '
                f'fill="{fill}"{extra}>{escape(s).replace("→", ARROW)}</text>')

    def title(s):
        return text(110, 138, s, size=44, weight=700, fill=FOAM)

    def rect(x, y, w, h, stroke=MINT, so=0.35, fill=BOX, dash=False, rx=18, sw=2):
        d = ' stroke-dasharray="14 10"' if dash else ''
        return (f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" fill="{fill}" stroke="{stroke}" '
                f'stroke-opacity="{so}" stroke-width="{sw}"{d}/>')

    def node(x, y, w, h, rows, stroke=MINT, so=0.35, dash=False, gap=42):
        """A box with centred lines; each row is (text, kind) with kind head, body, mono or code."""
        out = [rect(x, y, w, h, stroke=stroke, so=so, dash=dash)]
        sizes = {'head': 34, 'body': 30, 'mono': 30, 'code': 32}
        first = y + h / 2 - gap * (len(rows) - 1) / 2
        for i, (s, kind) in enumerate(rows):
            size = sizes[kind]
            out.append(text(x + w / 2, round(first + i * gap + size * 0.35), s, size=size, anchor='middle',
                            mono=kind in ('mono', 'code'),
                            weight=700 if kind in ('head', 'code') else None,
                            fill=FOAM if kind in ('head', 'code') else MIST))
        return ''.join(out)

    def arrow(points, color=MINT, width=4, head=18, dash=False):
        (x1, y1), (x2, y2) = points[-2], points[-1]
        a = math.atan2(y2 - y1, x2 - x1)
        bx, by = x2 - head * math.cos(a), y2 - head * math.sin(a)
        pts = points[:-1] + [(bx, by)]
        d = ' stroke-dasharray="12 10"' if dash else ''
        line = (f'<polyline points="{" ".join(f"{px:.0f},{py:.0f}" for px, py in pts)}" fill="none" stroke="{color}" '
                f'stroke-width="{width}" stroke-linecap="round" stroke-linejoin="round"{d}/>')
        l = head * 0.55
        tip = (f'<path d="M{x2:.0f} {y2:.0f}L{bx - l * math.sin(a):.0f} {by + l * math.cos(a):.0f}'
               f'L{bx + l * math.sin(a):.0f} {by - l * math.cos(a):.0f}Z" fill="{color}"/>')
        return line + tip

    # ------------------------------------------------------------ recording-a-window-you-cannot-see
    def pipeline():
        b = [title('Recording one window')]
        b.append(node(110, 200, 360, 180, [('Compositor', 'head'), ("window's own frames", 'body')]))
        b.append(node(560, 200, 480, 180, [('capture thread', 'head'), ('ext-image-copy-capture', 'mono'),
                                           ('own Wayland connection', 'body')]))
        b.append(node(1130, 200, 360, 180, [('one-slot mailbox', 'head'), ('newest wins', 'body')]))
        b.append(arrow([(470, 290), (560, 290)]))
        b.append(arrow([(1040, 290), (1130, 290)]))
        b.append(arrow([(1310, 380), (1310, 425), (330, 425), (330, 470)]))
        b.append(node(110, 470, 440, 220, [('pacer thread', 'head'), ('GStreamer clock', 'body'),
                                           ('repeats last frame', 'body'), ('letterboxes resizes', 'body')]))
        b.append(node(640, 470, 380, 220, [('encoder', 'head'), ('nvh264enc →', 'mono'), ('vah264enc →', 'mono'),
                                           ('x264enc', 'mono')]))
        b.append(node(1110, 520, 210, 120, [('MP4', 'code')], so=0.8, stroke=MINT))
        b.append(arrow([(550, 580), (640, 580)]))
        b.append(arrow([(1020, 580), (1110, 580)]))
        b.append(node(290, 744, 290, 66, [('system sound', 'body')], stroke=TEAL))
        b.append(node(290, 830, 290, 66, [('microphone', 'body')], stroke=TEAL))
        b.append(node(690, 787, 280, 66, [('Opus tracks', 'body')], stroke=TEAL))
        b.append(arrow([(580, 777), (635, 777), (635, 812), (690, 812)], color=TEAL))
        b.append(arrow([(580, 863), (635, 863), (635, 828), (690, 828)], color=TEAL))
        b.append(arrow([(970, 820), (1215, 820), (1215, 640)], color=TEAL))
        return frame('dg-pl', ''.join(b), glow=(360, 260))

    def supervision():
        b = [title('If the daemon dies, so does the recorder')]
        b.append(node(110, 200, 400, 100, [('easyshot daemon', 'head')]))
        b.append(rect(110, 440, 850, 280, stroke=MIST, so=0.55, fill='none', dash=True, rx=26))
        b.append(text(140, 692, 'process group', fill=MIST))
        b.append(node(140, 500, 340, 120, [('/bin/sh watcher', 'code')]))
        b.append(node(510, 500, 420, 120, [('gpu-screen-recorder', 'code')]))
        b.append(arrow([(310, 300), (310, 500)], width=6))
        b.append(text(336, 350, 'holds the write end of a pipe', fill=MIST))
        b.append(text(336, 420, 'the watcher reads it', fill=MIST))
        x, w = 1030, 440
        b.append(node(x, 200, w, 92, [('pipe closes (EOF)', 'head')]))
        b.append(arrow([(x + w / 2, 292), (x + w / 2, 356)]))
        b.append(node(x, 356, w, 92, [('SIGINT to the group', 'head')]))
        b.append(arrow([(x + w / 2, 448), (x + w / 2, 610)], dash=True))
        b.append(text(x + w / 2 + 26, 540, '10 s', mono=True, size=32, weight=700, fill=MINT))
        b.append(node(x, 610, w, 92, [('SIGKILL', 'code')], so=0.8))
        y = 830
        b.append(text(110, y, 'PR_SET_PDEATHSIG', mono=True, fill=FOAM))
        b.append(f'<path d="M104 {y - 10}H404" stroke="{CORAL}" stroke-width="3" stroke-linecap="round"/>')
        b.append(text(424, y, '— dropped on exec of a binary with file capabilities', fill=MIST))
        return frame('dg-sv', ''.join(b), glow=(320, 520))

    # ------------------------------------------------------------ the-compositor-is-still-drawing-it
    def settle():
        u = 'dg-st'
        x0, x1 = 520, 1460
        px = lambda ms: x0 + (x1 - x0) * ms / 400
        b = [title("Waiting for a bar that's already gone")]
        b.append(f'<defs><linearGradient id="{u}-fade" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="{MINT}"/>'
                 f'<stop offset="1" stop-color="{MINT}" stop-opacity="0"/></linearGradient></defs>')
        for ms in range(0, 401, 100):
            b.append(f'<path d="M{px(ms):.0f} 262V820" stroke="{MINT}" stroke-opacity="0.12" stroke-width="2"/>')
            b.append(text(round(px(ms)), 238, f'{ms} ms' if ms in (0, 400) else str(ms), mono=True, fill=MIST,
                          anchor='middle'))
        b.append(f'<path d="M{x0} 262H{x1}" stroke="{MIST}" stroke-opacity="0.6" stroke-width="2"/>')
        rows = [(340, 'Bar closed'), (460, 'Hyprland layer fade'), (630, 'Before: fixed 150 ms'),
                (770, 'After: fade + 50 ms')]
        for y, label in rows:
            b.append(text(110, y + 11, label, size=32, weight=600, fill=FOAM))
        b.append(f'<circle cx="{x0}" cy="340" r="16" fill="{MINT}"/>')
        b.append(f'<rect x="{x0}" y="436" width="{px(250) - x0:.0f}" height="48" rx="10" fill="url(#{u}-fade)"/>')
        b.append(text(x0 + 16, 471, '100%', mono=True, weight=700, fill=ABYSS))
        b.append(text(round(px(250)) + 14, 471, '0%', mono=True, fill=MIST))
        b.append(text(x0, 532, 'fadeLayersOut 270 ms, measured ~250 ms', fill=MIST))
        for ya, yb in [(420, 540), (592, 680), (730, 810)]:
            b.append(f'<path d="M{px(250):.0f} {ya}V{yb}" stroke="{MIST}" stroke-opacity="0.7" stroke-width="3" '
                     f'stroke-dasharray="10 10"/>')
        for y, ms, color, label, anchor in [(630, 150, CORAL, 'frame grabbed — bar caught mid-fade', 'start'),
                                            (770, 300, MINT, 'frame grabbed — 0 bar pixels', 'end')]:
            b.append(f'<rect x="{x0}" y="{y - 5}" width="{px(ms) - x0:.0f}" height="10" rx="5" fill="{color}" '
                     f'fill-opacity="0.35"/>')
            b.append(f'<path d="M{px(ms):.0f} {y - 40}V{y + 40}" stroke="{color}" stroke-width="5" stroke-linecap="round"/>')
            b.append(f'<circle cx="{px(ms):.0f}" cy="{y}" r="15" fill="{color}"/>')
            lx = px(ms) + 30 if anchor == 'start' else px(ms) - 30
            b.append(text(round(lx), y - 52, label, fill=color, anchor=anchor))
        return frame(u, ''.join(b), glow=(900, 520))

    def providers():
        b = [title('The app sees capabilities, not compositors')]
        rows = [('Capture', ['ext-image-copy-capture', 'wlr-screencopy']),
                ('WindowList', ['hyprland', 'wlroots', 'niri', 'frozen frame']),
                ('PointerQuery', ['hyprland', 'niri']),
                ('Recorder', ['gpu-screen-recorder', 'wf-recorder', 'own window recorder']),
                ('Clipboard', ['wayland data-control']),
                ('Tray', ['StatusNotifierItem']),
                ('Notifier', ['D-Bus notifications'])]
        top, pitch, h = 210, 82, 56
        for i, (cap, chips) in enumerate(rows):
            y = top + i * pitch
            b.append(text(110, y + h / 2 + 11, cap, mono=True, weight=700, fill=MINT))
            x = 380
            for j, chip in enumerate(chips):
                if j:
                    b.append(f'<path d="M{x + 4} {y + 18}L{x + 14} {y + 28}L{x + 4} {y + 38}" fill="none" stroke="{MIST}" '
                             f'stroke-opacity="0.7" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/>')
                    x += 26
                w = round(len(chip) * 14.8) + 30
                b.append(rect(x, y, w, h, so=0.3 if j else 0.6, rx=14))
                b.append(text(x + w / 2, y + h / 2 + 10, chip, fill=FOAM if j == 0 else MIST, anchor='middle'))
                x += w + 8
        bottom = top + 6 * pitch + h
        mid = (top + bottom) / 2
        b.append(f'<path d="M1290 {top}H1308V{bottom}H1290M1308 {mid}H1322" fill="none" stroke="{MINT}" '
                 f'stroke-opacity="0.7" stroke-width="4" stroke-linecap="round" stroke-linejoin="round"/>')
        b.append(arrow([(1322, mid), (1352, mid)]))
        b.append(node(1352, mid - 40, 140, 80, [('Caps', 'code')], so=0.8))
        b.append(arrow([(1422, mid + 40), (1422, mid + 110)]))
        b.append(node(1352, mid + 110, 140, 80, [('app', 'head')]))
        b.append(text(110, 846, 'grep-guard: no hyprctl, SWAYSOCK or NIRI_SOCKET', mono=True, fill=MIST))
        b.append(text(110, 888, 'outside es-backend/{hyprland,wlroots,niri}', mono=True, fill=MIST))
        return frame('dg-pv', ''.join(b), glow=(1300, 420))

    # ------------------------------------------------------------ what-the-terminal-engine-did-not-promise
    def readback():
        b = [title("Never send a snapshot you can't read")]
        b.append(node(110, 205, 270, 110, [('authoritative', 'head'), ('terminal', 'head')]))
        b.append(arrow([(380, 260), (650, 260)]))
        b.append(text(515, 240, 'encode snapshot', fill=MIST, anchor='middle'))
        b.append(node(650, 215, 240, 90, [('bytes held', 'head')]))
        b.append(arrow([(770, 305), (770, 430)]))
        b.append(text(796, 378, 'decode into a throwaway terminal', fill=MIST))
        cx, cy, rx, ry = 770, 520, 160, 90
        b.append(f'<path d="M{cx} {cy - ry}L{cx + rx} {cy}L{cx} {cy + ry}L{cx - rx} {cy}Z" fill="{BOX}" stroke="{MINT}" '
                 f'stroke-opacity="0.6" stroke-width="2" stroke-linejoin="round"/>')
        b.append(text(cx, cy + 11, 'reads back?', size=32, weight=700, anchor='middle'))
        b.append(arrow([(cx + rx, cy), (1130, cy)]))
        b.append(text(1020, cy - 18, 'yes', weight=700, fill=MINT, anchor='middle'))
        b.append(node(1130, cy - 48, 320, 96, [('send to window', 'head')], so=0.8))
        b.append(arrow([(cx, cy + ry), (cx, 694)], color=CORAL))
        b.append(text(cx + 22, 662, 'no', weight=700, fill=CORAL))
        b.append(node(600, 694, 340, 110, [('redraw a terminal', 'head'), ('from the replay', 'head')],
                      stroke=CORAL, so=0.6))
        b.append(arrow([(940, 749), (1000, 749)], color=CORAL))
        b.append(node(1000, 704, 320, 90, [('send that instead', 'head')], stroke=CORAL, so=0.6))
        b.append(text(600, 856, 'loses links, prompt marks, hidden screen', fill=MIST))
        return frame('dg-rb', ''.join(b), glow=(770, 480))

    def placements():
        b = [title('Kitty image placements: cost grows with the count')]
        data = [('1,000', 1.1, '1.1 ms'), ('4,000', 12.6, '12.6 ms'), ('16,000', 212, '212 ms'),
                ('32,000', 905, '905 ms'), ('100,000', 16280, '16.28 s')]
        x0, x1, lo, hi = 300, 1410, -1, 5
        px = lambda ms: x0 + (x1 - x0) * (math.log10(ms) - lo) / (hi - lo)
        top, pitch, h = 236, 90, 56
        axis = top + 4 * pitch + h + 30
        ticks = [(0.1, '0.1 ms'), (1, '1 ms'), (10, '10 ms'), (100, '100 ms'), (1000, '1 s'), (10000, '10 s'),
                 (100000, '100 s')]
        for v, label in ticks:
            b.append(f'<path d="M{px(v):.0f} {top - 16}V{axis}" stroke="{MINT}" stroke-opacity="0.12" stroke-width="2"/>')
            b.append(text(round(px(v)), axis + 42, label, mono=True, fill=MIST, anchor='middle'))
        b.append(f'<path d="M{x0} {axis}H{x1}" stroke="{MIST}" stroke-opacity="0.6" stroke-width="2"/>')
        b.append(text(270, 206, 'placements', fill=MIST, anchor='end'))
        for i, (count, ms, label) in enumerate(data):
            y = top + i * pitch
            last = i == len(data) - 1
            color = CORAL if last else [SEA, TEAL, TEAL, MINT][i]
            b.append(text(270, y + h / 2 + 11, count, mono=True, weight=700, fill=FOAM, anchor='end'))
            b.append(f'<rect x="{x0}" y="{y}" width="{px(ms) - x0:.0f}" height="{h}" rx="12" fill="{color}" '
                     f'fill-opacity="{0.9 if last else 0.75}"/>')
            b.append(text(round(px(ms)) + 18, y + h / 2 + 11, label, mono=True, weight=700,
                          fill=CORAL if last else FOAM))
        b.append(text(110, 860, 'debug build of the engine; each placement is 20 bytes', fill=MIST))
        return frame('dg-pc', ''.join(b), glow=(1200, 600))

    def osc7501():
        b = [title('Answer in the order you were asked')]
        lanes = {'Program': 300, 'Insensical': 800, 'Engine': 1250}
        for name, x in lanes.items():
            b.append(f'<path d="M{x} 270V790" stroke="{MIST}" stroke-opacity="0.45" stroke-width="3" stroke-dasharray="10 10"/>')
            b.append(node(x - 120, 196, 240, 74, [(name, 'head')], so=0.7 if name == 'Insensical' else 0.35))
        P, I, E = lanes['Program'], lanes['Insensical'], lanes['Engine']
        b.append(arrow([(P, 340), (I - 6, 340)], color=MIST))
        b.append(text((P + I) // 2, 324, 'OSC 7501 ; ?', mono=True, weight=700, anchor='middle'))
        b.append(arrow([(P, 410), (I - 6, 410)], color=MIST))
        b.append(text((P + I) // 2, 394, 'CSI c', mono=True, weight=700, anchor='middle'))
        b.append(arrow([(I, 518), (E - 6, 518)], color=TEAL))
        b.append(text((I + E) // 2, 462, 'only up to the end', fill=MIST, anchor='middle'))
        b.append(text((I + E) // 2, 500, 'of the first question', fill=MIST, anchor='middle'))
        b.append(arrow([(I, 596), (P + 6, 596)], width=5))
        b.append(text((P + I) // 2, 580, 'OSC 7501 answer', mono=True, weight=700, fill=MINT, anchor='middle'))
        b.append(arrow([(I, 670), (E - 6, 670)], color=TEAL))
        b.append(text((I + E) // 2, 654, 'the rest', fill=MIST, anchor='middle'))
        b.append(arrow([(E, 760), (P + 6, 760)], color=SEA))
        b.append(text((P + I) // 2, 744, 'CSI c → device attributes', mono=True, weight=700, anchor='middle'))
        b.append(text(110, 866, 'The program believes whichever answer comes first.', size=32, fill=FOAM))
        return frame('dg-os', ''.join(b), glow=(800, 460))

    # ------------------------------------------------------------ keeping-a-daemon-alive
    def spawn():
        b = [title('Restoring 1,000 panes')]
        x0 = 360
        s = (1300 - x0) / 32
        for v in range(0, 31, 10):
            b.append(f'<path d="M{x0 + v * s:.0f} 210V420" stroke="{MINT}" stroke-opacity="0.12" stroke-width="2"/>')
            b.append(text(round(x0 + v * s), 460, f'{v} s', mono=True, fill=MIST, anchor='middle'))
        b.append(f'<path d="M{x0} 420H1340" stroke="{MIST}" stroke-opacity="0.6" stroke-width="2"/>')
        b.append(text(110, 266, 'fork + exec', mono=True, weight=700))
        b.append(f'<rect x="{x0}" y="226" width="{20 * s:.0f}" height="62" rx="12" fill="{SEA}" fill-opacity="0.9"/>')
        b.append(f'<rect x="{x0 + 20 * s:.0f}" y="226" width="{12 * s:.0f}" height="62" rx="12" fill="{SEA}" '
                 f'fill-opacity="0.35" stroke="{SEA}" stroke-width="2" stroke-dasharray="10 8"/>')
        b.append(text(round(x0 + 26 * s), 268, '20–32 s', mono=True, weight=700, anchor='middle'))
        b.append(text(110, 356, 'posix_spawn', mono=True, weight=700))
        b.append(f'<rect x="{x0}" y="316" width="{s:.0f}" height="62" rx="8" fill="{MINT}"/>')
        b.append(text(round(x0 + s) + 18, 358, '~1 s', mono=True, weight=700, fill=MINT))
        b.append(text(110, 548, 'per pane', size=32, weight=600, fill=MIST))
        m = 30
        b.append(text(110, 612, 'fork + exec', mono=True, weight=700))
        b.append(f'<rect x="{x0}" y="578" width="{18 * m}" height="46" rx="10" fill="{SEA}" fill-opacity="0.9"/>')
        b.append(text(x0 + 18 * m + 18, 612, '18 ms', mono=True, weight=700))
        b.append(text(110, 682, 'posix_spawn', mono=True, weight=700))
        b.append(f'<rect x="{x0}" y="648" width="{3 * m}" height="46" rx="10" fill="{MINT}"/>')
        b.append(text(x0 + 3 * m + 18, 682, '3 ms', mono=True, weight=700, fill=MINT))
        b.append(text(110, 800, 'fork copies the memory map;', fill=MIST))
        b.append(text(110, 844, "its cost grows with the daemon's threads (one per pane)", fill=MIST))
        return frame('dg-sp', ''.join(b), glow=(700, 320))

    def handover():
        b = [title('Upgrading in place: same process, new program')]
        b.append(rect(110, 190, 900, 650, so=0.5, rx=28))
        b.append(text(150, 252, 'pid 4211', mono=True, size=32, weight=700, fill=MINT))
        b.append(text(320, 252, "— every pane's parent", size=32, weight=600, fill=FOAM))
        b.append(f'<path d="M110 282H1010" stroke="{MINT}" stroke-opacity="0.2" stroke-width="2"/>')
        steps = [['write state to an unnamed file'],
                 ['ask the new binary: can you read it?', '(isc carried, 10 s)'],
                 ['finish in-flight sends (up to 10 s)'],
                 None,
                 ['new daemon checks the fd,', 'clears the variable before any thread'],
                 ['panes carry on']]
        ys = [334, 410, 524, 600, 676, 790]
        b.append(f'<path d="M180 {ys[0]}V{ys[-1] - 30}" stroke="{MINT}" stroke-opacity="0.3" stroke-width="3"/>')
        for i, (y, lines) in enumerate(zip(ys, steps)):
            b.append(f'<circle cx="180" cy="{y - 11}" r="24" fill="{MINT if i in (3, 5) else TEAL}"/>')
            b.append(text(180, y, str(i + 1), mono=True, weight=700, fill=ABYSS, anchor='middle'))
            if lines is None:
                b.append(text(230, y, 'exec — fd number in', fill=FOAM))
                b.append(text(520, y, 'INSENSICAL_HANDOVER', mono=True, weight=700, fill=MINT))
                continue
            for k, line in enumerate(lines):
                b.append(text(230, y + k * 40, line, fill=FOAM if k == 0 else MIST))
        b.append(rect(1080, 340, 400, 170, stroke=CORAL, so=0.55, fill='none', dash=True))
        b.append(text(1110, 392, 'Rejected:', weight=700, fill=CORAL))
        b.append(text(1110, 434, 'passing descriptors', fill=MIST))
        b.append(text(1110, 474, 'to a new process', fill=MIST))
        return frame('dg-ho', ''.join(b), glow=(500, 480))

    # ------------------------------------------------------------ gpui-after-three-apps
    def primitives():
        b = [title('What GPUI gives you, and what you build')]
        cols = [('Insensical', ['grid renderer', 'glyph cache', 'row cache', 'box-drawing as geometry']),
                ('easyshot', ['layer-shell surfaces', 'tiny-skia renderer', 'custom cursors']),
                ('Sysman', ['charts', 'time-series scrubbing'])]
        w, gap = 430, 30
        for i, (app, items) in enumerate(cols):
            x = 110 + i * (w + gap)
            b.append(rect(x, 200, w, 360, so=0.35, rx=22))
            b.append(text(x + 30, 254, app, size=34, weight=700, fill=MINT))
            b.append(f'<path d="M{x} 282H{x + w}" stroke="{MINT}" stroke-opacity="0.2" stroke-width="2"/>')
            for k, item in enumerate(items):
                b.append(text(x + 30, 340 + k * 52, item, fill=FOAM))
        b.append(f'<rect x="110" y="590" width="{3 * w + 2 * gap}" height="140" rx="24" fill="{TEAL}" fill-opacity="0.22" '
                 f'stroke="{MINT}" stroke-opacity="0.7" stroke-width="2"/>')
        cx = 110 + (3 * w + 2 * gap) / 2
        b.append(text(cx, 652, 'GPUI: quads · paths · shaped text · glyphs · images', size=36, weight=700,
                      anchor='middle'))
        b.append(text(cx, 700, 'no custom shaders, pipelines or textures', fill=MIST, anchor='middle'))
        return frame('dg-pr', ''.join(b), glow=(800, 700))

    def budget():
        b = [title('A frame budget, set before the code')]
        x0, x1, ay = 160, 1400, 680
        px = lambda ms: x0 + (x1 - x0) * ms / 10
        b.append(f'<rect x="{x0}" y="{ay - 26}" width="{px(4) - x0:.0f}" height="26" fill="{MINT}" fill-opacity="0.16"/>')
        b.append(f'<rect x="{px(8):.0f}" y="{ay - 26}" width="{x1 - px(8):.0f}" height="26" fill="{CORAL}" fill-opacity="0.18"/>')
        b.append(f'<path d="M{x0} {ay}H{x1}" stroke="{MIST}" stroke-opacity="0.7" stroke-width="3"/>')
        for ms in range(11):
            b.append(f'<path d="M{px(ms):.0f} {ay}V{ay + 14}" stroke="{MIST}" stroke-opacity="0.7" stroke-width="3"/>')
            b.append(text(round(px(ms)), ay + 56, str(ms), mono=True, fill=MIST, anchor='middle'))
        b.append(text(x1 + 44, ay + 56, 'ms', mono=True, fill=MIST))
        m = px(2)
        b.append(f'<path d="M{m:.0f} {ay}V266" stroke="{MINT}" stroke-width="4"/>')
        b.append(f'<circle cx="{m:.0f}" cy="{ay}" r="16" fill="{MINT}"/>')
        b.append(text(round(m) + 22, 302, '2.0 ms', mono=True, size=32, weight=700, fill=MINT))
        b.append(text(round(m) + 22, 344, 'measured: 200×60,', fill=FOAM))
        b.append(text(round(m) + 22, 384, 'every cell styled (p50)', fill=MIST))
        g = px(4)
        b.append(f'<path d="M{g:.0f} {ay}V440" stroke="{FOAM}" stroke-width="4" stroke-dasharray="12 8"/>')
        b.append(text(round(g) + 22, 470, 'budget', size=34, weight=700))
        b.append(text(round(g) + 22, 510, '4 ms', mono=True, fill=MIST))
        c = px(8)
        b.append(f'<path d="M{c:.0f} {ay}V440" stroke="{CORAL}" stroke-width="4"/>')
        b.append(text(round(c) + 22, 470, 'past this,', fill=CORAL, weight=700))
        b.append(text(round(c) + 22, 510, 'switch toolkit', fill=CORAL))
        b.append(text(round(c) + 22, 550, '(iced + wgpu grid)', fill=MIST))
        return frame('dg-bd', ''.join(b), glow=(420, 520))

    def patches():
        b = [title('Two ways to live with a young toolkit')]
        base_y, base_h = 724, 96
        lx, lw, rx, rw = 110, 560, 790, 520
        b.append(text(lx, 220, 'easyshot', size=36, weight=700, fill=MINT))
        b.append(text(rx, 220, 'Insensical', size=36, weight=700, fill=MINT))
        for x, w, note in [(lx, lw, 'crates.io, vendored'), (rx, rw, 'pinned')]:
            b.append(f'<rect x="{x}" y="{base_y}" width="{w}" height="{base_h}" rx="16" fill="{SEA}" fill-opacity="0.45" '
                     f'stroke="{MINT}" stroke-opacity="0.6" stroke-width="2"/>')
            b.append(text(x + 28, base_y + 42, 'gpui-pre 0.3.10', mono=True, weight=700))
            b.append(text(x + 28, base_y + 80, note, fill=MIST))
        commits = [('P1', 'layer margin'), ('P5', 'custom cursors'), ('P6', 'drag icon'), ('P7', 'layer decorations'),
                   ('P8', 'cursor order'), ('P10', 'copy-only drags'), ('P11', 'tooltip timing'),
                   ('P12', 'element opacity'), ('P13', 'hover cleared on leave'), ('P14', 'tooltip hide-after')]
        h, pitch = 40, 46
        for i, (p, label) in enumerate(commits):
            y = base_y - 8 - h - i * pitch
            b.append(rect(lx + 20, y, lw - 40, h, so=0.45, rx=10))
            b.append(text(lx + 44, y + 31, p, mono=True, weight=700, fill=MINT))
            b.append(text(lx + 124, y + 31, label, fill=FOAM))
        notes = [['baseline_offset sign', '— work around'],
                 ['appearance learned late', '— ask the portal first'],
                 ['no window activation token', '— documented']]
        for i, (a, c) in enumerate(notes):
            y = 300 + i * 136
            b.append(f'<path d="M{rx} {y - 26}V{y + 46}" stroke="{TEAL}" stroke-width="4" stroke-linecap="round"/>')
            b.append(text(rx + 24, y, a, mono=i == 0, fill=FOAM))
            b.append(text(rx + 24, y + 42, c, fill=MIST))
        return frame('dg-pt', ''.join(b), glow=(400, 520))

    # ------------------------------------------------------------ the-483-gb-target-folder
    def bar(x, y, w, h, color, op=0.85, rx=12):
        return f'<rect x="{x:.0f}" y="{y:.0f}" width="{max(w, 2):.0f}" height="{h}" rx="{min(rx, w / 2):.0f}" fill="{color}" fill-opacity="{op}"/>'

    def range_bar(x, y, w, h, color):
        return (f'<rect x="{x:.0f}" y="{y:.0f}" width="{w:.0f}" height="{h}" rx="12" fill="none" '
                f'stroke="{color}" stroke-width="2" stroke-dasharray="10 8"/>')

    def where_it_went():
        b = [title('Where 483 GB went')]
        x0, x1, y, h = 110, 1490, 360, 140
        s = (x1 - x0) / 483
        b.append(text(x0, y - 30, 'target/debug', mono=True, weight=700))
        b.append(text(x1, y - 30, '483 GB', mono=True, weight=700, fill=CORAL, anchor='end'))
        x = x0
        for name, gb, color, ink in [('deps', 376, CORAL, ABYSS), ('examples', 65, TEAL, ABYSS),
                                     ('incremental', 43, SEA, FOAM)]:
            w = gb * s
            b.append(bar(x, y, w - 4, h, color, op=0.9))
            b.append(text(round(x + w / 2), y + h / 2 + 11, f'{gb} GB', mono=True, weight=700, fill=ink, anchor='middle'))
            if name == 'incremental':
                b.append(text(x1, y + h + 92, name, size=32, weight=600, fill=MIST, anchor='end'))
            else:
                b.append(text(round(x), y + h + 48, name, size=32, weight=600, fill=MIST))
            x += w
        b.append(text(x0, 690, '136 integration-test binaries, each 1–1.7 GB,', size=32, fill=FOAM))
        b.append(text(x0, 736, 'about half of it debug info', fill=MIST))
        return frame('dg-ww', ''.join(b), glow=(500, 420))

    def before_after():
        b = [title('target/ before and after the profile change')]
        data = [('easyshot', 483, '483 GB', 'before', 56, '56 GB', 'a week later'),
                ('Insensical', 100, '100+ GB', '', 31, '31 GB', ''),
                ('Sysman', 22, '22 GB', '', 3, '3 GB', ''),
                ('Darwan', 4.1, '4.1 GB', '', 1.9, '1.9 GB', ''),
                ('Quarry', 3.7, '3.7 GB', '', 1.7, '1.7 GB', '')]
        x0, x1 = 330, 1240
        px = lambda gb: x0 + (x1 - x0) * math.log10(gb) / 3
        top, pitch, h, gap = 214, 116, 38, 8
        axis = top + 4 * pitch + 2 * h + gap + 28
        for gb in (1, 10, 100, 1000):
            b.append(f'<path d="M{px(gb):.0f} {top - 16}V{axis}" stroke="{MINT}" stroke-opacity="0.12" stroke-width="2"/>')
            b.append(text(round(px(gb)), axis + 42, f'{gb} GB', mono=True, fill=MIST, anchor='middle'))
        b.append(f'<path d="M{x0} {axis}H{x1}" stroke="{MIST}" stroke-opacity="0.6" stroke-width="2"/>')
        for i, (name, before, bl, bnote, after, al, anote) in enumerate(data):
            y = top + i * pitch
            b.append(text(290, y + h + gap // 2 + 11, name, size=32, weight=600, anchor='end'))
            for yy, gb, label, note, color in [(y, before, bl, bnote, CORAL), (y + h + gap, after, al, anote, MINT)]:
                end = px(gb)
                b.append(bar(x0, yy, end - x0, h, color, rx=10))
                if label.endswith('+ GB'):
                    end = px(gb * 1.5)
                    b.append(range_bar(px(gb) + 4, yy, end - px(gb) - 4, h, color))
                b.append(text(round(end) + 16, yy + h / 2 + 11, label, mono=True, weight=700, fill=color))
                if note:
                    b.append(text(round(end) + 16 + len(label) * 18 + 16, yy + h / 2 + 11, note, fill=MIST))
        return frame('dg-ba', ''.join(b), glow=(700, 420))

    def binary_anatomy():
        b = [title('Half of every test binary was debug info')]
        x0 = 110
        s = (1250 - x0) / 640
        h = 50
        groups = [('Sysman · app binary', 540, 640, '540–640 MB', None, 44),
                  ('Darwan · largest test binary', 283, 283, '283 MB', 0.49, 91),
                  ('Quarry · largest binary', 262, 262, '262 MB', None, 67)]
        for i, (name, lo, hi, label, debug, after) in enumerate(groups):
            y = 236 + i * 190
            b.append(text(x0, y, name, size=32, weight=600))
            by = y + 22
            if debug:
                code = lo * (1 - debug)
                b.append(bar(x0, by, code * s - 4, h, MIST, op=0.75))
                b.append(text(x0 + 20, by + h / 2 + 11, 'code', fill=ABYSS, weight=600))
                b.append(bar(x0 + code * s, by, lo * debug * s, h, CORAL, op=0.9))
                b.append(text(round(x0 + code * s) + 20, by + h / 2 + 11, f'debug info {debug:.0%}', fill=ABYSS, weight=600))
            else:
                b.append(bar(x0, by, lo * s, h, CORAL, op=0.9))
            if hi > lo:
                b.append(range_bar(x0 + lo * s + 4, by, (hi - lo) * s - 4, h, CORAL))
            b.append(text(round(x0 + hi * s) + 16, by + h / 2 + 11, label, mono=True, weight=700, fill=CORAL))
            ay = by + h + 10
            b.append(bar(x0, ay, after * s, h, MINT, op=0.9))
            b.append(text(round(x0 + after * s) + 16, ay + h / 2 + 11, f'{after} MB', mono=True, weight=700, fill=MINT))
        b.append(text(x0, 846, 'debug = "line-tables-only"', mono=True, fill=MIST))
        b.append(text(x0, 890, '[profile.dev.package."*"] debug = false', mono=True, fill=MIST))
        return frame('dg-an', ''.join(b), glow=(600, 460))

    def stale_copies():
        b = [title('Cargo never throws anything away')]
        x0, y0 = 110, 214
        for c in range(13):
            for r in range(49):
                b.append(bar(x0 + c * 50, y0 + r * 12.5, 40, 9, MINT if r == 0 else MIST, op=0.95 if r == 0 else 0.2, rx=3))
        b.append(text(772, y0 + 12, 'newest', fill=MINT, weight=600))
        x = 880
        b.append(text(x, 300, '13 examples × 49 hashed copies', size=32, weight=600))
        b.append(text(x, 356, '≈ 22 GB', mono=True, size=40, weight=700, fill=CORAL))
        for k, (n, cols) in enumerate([(171, 19), (162, 18)]):
            gx = x + k * (19 * 15 + 40)
            for j in range(n):
                b.append(bar(gx + (j % cols) * 15, 470 + (j // cols) * 13, 11, 8, MIST, op=0.35, rx=2))
            b.append(text(gx, 640, str(n), mono=True, weight=700, fill=FOAM))
        b.append(text(x, 712, '171 + 162 stale test binaries', size=32, weight=600))
        b.append(text(x, 768, '≈ 35 GB', mono=True, size=40, weight=700, fill=CORAL))
        return frame('dg-sc', ''.join(b), glow=(450, 520))

    def suite_time():
        b = [title('The same 1,878 tests')]
        x0 = 110
        s = (1300 - x0) / 254
        rows = [('cargo test, binaries one after another', 254, '254 s', CORAL),
                ('nextest, 12 threads, name order', 161.7, '161.7 s', TEAL),
                ('nextest, slowest first', 134.0, '134.0 s', MINT)]
        axis = 690
        for v in range(0, 241, 60):
            b.append(f'<path d="M{x0 + v * s:.0f} 214V{axis}" stroke="{MINT}" stroke-opacity="0.12" stroke-width="2"/>')
            b.append(text(round(x0 + v * s), axis + 42, f'{v} s', mono=True, fill=MIST, anchor='middle'))
        b.append(f'<path d="M{x0} {axis}H1320" stroke="{MIST}" stroke-opacity="0.6" stroke-width="2"/>')
        for i, (label, sec, value, color) in enumerate(rows):
            y = 240 + i * 156
            b.append(text(x0, y, label, size=32, weight=600))
            b.append(bar(x0, y + 22, sec * s, 64, color, op=0.85))
            b.append(text(round(x0 + sec * s) + 18, y + 66, value, mono=True, weight=700, fill=FOAM if color == TEAL else color))
        b.append(text(x0, 846, '1,584 s of test time in total', fill=MIST))
        return frame('dg-su', ''.join(b), glow=(600, 420))

    def slowest_first():
        b = [title('Start the long ones first')]
        # Tenths of a second, in name order; four threads dispatched greedily reproduce both measured end times.
        jobs = [196, 77, 144, 195, 186, 192, 164, 197, 157, 219, 122, 216, 125, 140, 122, 96, 144, 220, 101, 172, 93, 88,
                190, 186, 215, 330, 130, 162, 178, 460, 129]

        def schedule(order):
            free, out = [0] * 4, []
            for d in order:
                lane = min(range(4), key=lambda k: (free[k], k))
                out.append((lane, free[lane], d))
                free[lane] += d
            return out, max(free)

        w = 630
        s = w / 1700
        for x, heading, order, color in [(110, 'name order', jobs, CORAL),
                                         (860, 'slowest first', sorted(jobs, reverse=True), MINT)]:
            b.append(text(x, 236, heading, size=34, weight=700, fill=MINT if color == MINT else FOAM))
            placed, end = schedule(order)
            for lane in range(4):
                b.append(bar(x, 290 + lane * 76, w, 62, MIST, op=0.05, rx=10))
            for lane, start, d in placed:
                long = d >= 330
                bx, by = x + start * s, 290 + lane * 76
                b.append(bar(bx + 1.5, by, d * s - 3, 62, TEAL if long else MIST, op=0.9 if long else 0.32, rx=8))
                if long:
                    b.append(text(round(bx + d * s / 2), by + 42, f'{d // 10} s', mono=True, weight=700, fill=ABYSS,
                                  anchor='middle'))
            ex = x + end * s
            b.append(f'<path d="M{ex:.0f} 270V612" stroke="{color}" stroke-width="4" stroke-linecap="round"/>')
            b.append(text(round(ex), 656, f'{end / 10:.1f} s', mono=True, weight=700, fill=color, anchor='middle'))
        b.append(text(110, 770, 'Each row is a thread: four drawn here, twelve in the measured runs.', fill=MIST))
        return frame('dg-sf', ''.join(b), glow=(800, 420))

    def deps_opt():
        b = [title('Optimise the dependencies, not your code')]
        x0 = 110
        s = (1300 - x0) / 60
        axis = 580
        for v in range(0, 61, 10):
            b.append(f'<path d="M{x0 + v * s:.0f} 214V{axis}" stroke="{MINT}" stroke-opacity="0.12" stroke-width="2"/>')
            b.append(text(round(x0 + v * s), axis + 42, f'{v} s', mono=True, fill=MIST, anchor='middle'))
        b.append(f'<path d="M{x0} {axis}H1320" stroke="{MIST}" stroke-opacity="0.6" stroke-width="2"/>')
        for i, (label, sec, color) in enumerate([('one window test, dependencies at opt-level 0', 58, CORAL),
                                                 ('opt-level 2', 5, MINT)]):
            y = 250 + i * 170
            b.append(text(x0, y, label, size=32, weight=600))
            b.append(bar(x0, y + 22, sec * s, 70, color, op=0.85))
            b.append(text(round(x0 + sec * s) + 18, y + 69, f'{sec} s', mono=True, weight=700, fill=color))
        b.append(text(x0, 730, '[profile.dev.package."*"] opt-level = 2', mono=True, fill=MIST))
        return frame('dg-do', ''.join(b), glow=(500, 420))

    def profiles():
        b = [title('One profile per job')]
        cards = [('dev', ['line tables only', 'deps: opt-level 2', 'deps: no debug info']),
                 ('dbg', ['inherits dev', 'full debug info,', 'when you need', 'a debugger']),
                 ('page/fast', ['inherits release', 'no LTO', '16 codegen units', '=36 s vs 126 s']),
                 ('release', ['thin LTO', '1 codegen unit', 'stripped', '=70 → 50 MB'])]
        w, gap, y = 324, 28, 240
        for i, (name, lines) in enumerate(cards):
            x = 110 + i * (w + gap)
            b.append(rect(x, y, w, 370, so=0.35, rx=22))
            b.append(text(x + 28, y + 64, name, mono=True, size=36, weight=700, fill=MINT))
            b.append(f'<path d="M{x} {y + 96}H{x + w}" stroke="{MINT}" stroke-opacity="0.2" stroke-width="2"/>')
            for k, line in enumerate(lines):
                if line.startswith('='):
                    b.append(text(x + 28, y + 156 + k * 52, line[1:], mono=True, weight=700, fill=FOAM))
                else:
                    b.append(text(x + 28, y + 156 + k * 52, line, fill=FOAM if k == 0 else MIST))
        return frame('dg-pf', ''.join(b), glow=(800, 460))

    def io_pressure():
        b = [title("It wasn't the CPU")]
        base, py = 760, 12.5
        for v in range(0, 41, 10):
            y = base - v * py
            b.append(f'<path d="M260 {y}H1080" stroke="{MINT}" stroke-opacity="{0.6 if v == 0 else 0.12}" stroke-width="2"/>')
            b.append(text(236, y + 11, f'{v}%', mono=True, fill=MIST, anchor='end'))
        b.append(text(110, 216, 'pressure stall, "full", during a build', fill=MIST))
        for i, (name, lo, hi, label, color) in enumerate([('io', 21, 27, '21–27%', CORAL), ('cpu', 0, 0, '≈ 0', MIST),
                                                          ('memory', 0, 0, '≈ 0', MIST)]):
            x = 320 + i * 280
            if hi:
                b.append(bar(x, base - lo * py, 180, lo * py, color, op=0.85, rx=10))
                b.append(range_bar(x, base - hi * py, 180, (hi - lo) * py - 4, color))
            else:
                b.append(bar(x, base - 6, 180, 6, color, op=0.7, rx=3))
            b.append(text(x + 90, base - max(hi, 0) * py - 22, label, mono=True, size=32, weight=700, fill=color,
                          anchor='middle'))
            b.append(text(x + 90, base + 48, name, mono=True, size=32, weight=700, anchor='middle'))
        b.append(text(1150, 330, '"full": the share of time', fill=FOAM))
        b.append(text(1150, 372, 'every non-idle task', fill=MIST))
        b.append(text(1150, 414, 'was stalled at once', fill=MIST))
        b.append(text(110, 890, 'links wrote ~1.3 GB every 2 s', fill=MIST))
        b.append(text(510, 890, '· /proc/pressure/io', mono=True, fill=MIST))
        return frame('dg-io', ''.join(b), glow=(500, 520))

    def build_slice():
        b = [title('Builds below the desktop')]

        def chip(x, y, label, mono=False):
            w = len(label) * (18 if mono else 15) + 40
            b.append(rect(x, y, w, 52, so=0.3, rx=14))
            b.append(text(x + w / 2, y + 37, label, mono=mono, fill=MIST if mono else FOAM, anchor='middle'))
            return x + w + 12

        b.append(rect(110, 220, 350, 400, so=0.35, rx=22))
        b.append(text(140, 272, 'desktop.slice /', mono=True, weight=700))
        b.append(text(140, 312, 'app.slice', mono=True, weight=700))
        b.append(text(140, 360, 'CPUWeight=100', mono=True, fill=MINT))
        b.append(f'<path d="M110 386H460" stroke="{MINT}" stroke-opacity="0.2" stroke-width="2"/>')
        for k, app in enumerate(['browser', 'terminal', 'editor']):
            chip(140, 412 + k * 64, app)
        b.append(rect(540, 220, 950, 410, so=0.6, rx=22))
        b.append(text(570, 272, 'build.slice', mono=True, size=34, weight=700))
        b.append(text(1460, 272, 'CPUWeight=10 · MemoryHigh=90G', mono=True, fill=MINT, anchor='end'))
        tools = [['rustc', 'rustc', 'linker'], ['rustc', 'nextest'], ['rustc', 'linker']]
        tube_y = 700
        for k, chips in enumerate(tools):
            y = 300 + k * 108
            b.append(rect(640, y, 820, 92, so=0.3, rx=16))
            b.append(text(670, y + 40, 'cargo (scope)', mono=True, weight=700))
            b.append(text(670, y + 78, f'worktree {k + 1}', fill=MIST))
            x = 920
            for c in chips:
                x = chip(x, y + 20, c, mono=True)
            lane = 572 + k * 20
            b.append(arrow([(640, y + 46), (lane, y + 46), (lane, tube_y)], color=TEAL, width=3, head=14))
        b.append(text(640, 676, 'CARGO_MAKEFLAGS', mono=True, fill=MIST))
        b.append(f'<rect x="540" y="{tube_y}" width="760" height="76" rx="38" fill="{BOX}" stroke="{TEAL}" stroke-opacity="0.7" '
                 f'stroke-width="3"/><ellipse cx="1262" cy="{tube_y + 38}" rx="16" ry="34" fill="none" stroke="{TEAL}" '
                 f'stroke-opacity="0.5" stroke-width="3"/>')
        b.append(''.join(f'<circle cx="{588 + i * 21.5:.0f}" cy="{tube_y + 38}" r="8" fill="{MINT}"/>' for i in range(31)))
        b.append(text(540, tube_y + 122, 'cargo-jobserver · 31 tokens', mono=True, weight=700))
        b.append(text(110, 890, 'a lone build uses all 32; five builds share them', mono=True, fill=MIST))
        return frame('dg-bs', ''.join(b), glow=(1000, 460))

    return {
        'posts/the-483-gb-target-folder/where-it-went': where_it_went,
        'posts/the-483-gb-target-folder/before-after': before_after,
        'posts/the-483-gb-target-folder/binary-anatomy': binary_anatomy,
        'posts/the-483-gb-target-folder/stale-copies': stale_copies,
        'posts/the-483-gb-target-folder/suite-time': suite_time,
        'posts/the-483-gb-target-folder/slowest-first': slowest_first,
        'posts/the-483-gb-target-folder/deps-opt': deps_opt,
        'posts/the-483-gb-target-folder/profiles': profiles,
        'posts/the-483-gb-target-folder/io-pressure': io_pressure,
        'posts/the-483-gb-target-folder/build-slice': build_slice,
        'posts/recording-a-window-you-cannot-see/pipeline': pipeline,
        'posts/recording-a-window-you-cannot-see/supervision': supervision,
        'posts/the-compositor-is-still-drawing-it/settle': settle,
        'posts/the-compositor-is-still-drawing-it/providers': providers,
        'posts/what-the-terminal-engine-did-not-promise/readback': readback,
        'posts/what-the-terminal-engine-did-not-promise/placements': placements,
        'posts/what-the-terminal-engine-did-not-promise/osc7501': osc7501,
        'posts/keeping-a-daemon-alive/spawn': spawn,
        'posts/keeping-a-daemon-alive/handover': handover,
        'posts/gpui-after-three-apps/primitives': primitives,
        'posts/gpui-after-three-apps/budget': budget,
        'posts/gpui-after-three-apps/patches': patches,
    }
