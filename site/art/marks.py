"""Marks for the About timeline: one small tile for each milestone that has no logo of its own.

They share the site's tile — the teal gradient of the brand mark, rounded like an app icon — with a white line glyph
for what the milestone is about, so they read in both themes and sit beside the products' own logos without looking
borrowed. generate.py writes them to public/art/marks/.
"""
import math

GRAD = ('<defs><linearGradient id="t" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#62EDD4"/>'
        '<stop offset="0.55" stop-color="#21BDB0"/><stop offset="1" stop-color="#1388A6"/></linearGradient>'
        '<radialGradient id="g" cx="0.3" cy="0.2" r="0.9"><stop offset="0" stop-color="#FFFFFF" stop-opacity="0.35"/>'
        '<stop offset="1" stop-color="#FFFFFF" stop-opacity="0"/></radialGradient></defs>')
LINE = 'fill="none" stroke="#FFFFFF" stroke-width="3.5" stroke-linecap="round" stroke-linejoin="round"'


def tile(title, glyph):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64" role="img"><title>{title}</title>{GRAD}'
            f'<rect width="64" height="64" rx="16" fill="url(#t)"/><rect width="64" height="64" rx="16" fill="url(#g)"/>'
            f'{glyph}</svg>\n')


def linux():
    # a terminal and its prompt
    return tile('Linux from the start',
                f'<rect x="12" y="15" width="40" height="34" rx="7" {LINE}/><path d="M12 23h40" {LINE} stroke-opacity="0.55"/>'
                f'<path d="M20 31l6 5-6 5M30 41h12" {LINE}/>')


def freelance():
    # a globe: clients anywhere
    return tile('Freelancing',
                f'<circle cx="32" cy="32" r="18" {LINE}/><ellipse cx="32" cy="32" rx="8" ry="18" {LINE}/>'
                f'<path d="M15 26h34M15 38h34" {LINE} stroke-opacity="0.7"/>'
                f'<circle cx="49" cy="17" r="4" fill="#FFFFFF"/>')


def commits():
    # a commit graph with a branch
    return tile('A public footprint',
                f'<path d="M24 14v36" {LINE}/><path d="M24 36c0-8 16-6 16-14" {LINE}/>'
                f'<circle cx="24" cy="18" r="4.5" fill="#21BDB0" stroke="#FFFFFF" stroke-width="3.5"/>'
                f'<circle cx="24" cy="46" r="4.5" fill="#21BDB0" stroke="#FFFFFF" stroke-width="3.5"/>'
                f'<circle cx="40" cy="20" r="4.5" fill="#FFFFFF"/>')


def radar():
    # agents watching the web
    return tile('Agents that act on your behalf',
                f'<circle cx="32" cy="32" r="18" {LINE} stroke-opacity="0.55"/><circle cx="32" cy="32" r="10" {LINE} stroke-opacity="0.8"/>'
                f'<path d="M32 32L45 19" {LINE}/><circle cx="32" cy="32" r="3" fill="#FFFFFF"/>'
                f'<circle cx="41" cy="38" r="3.5" fill="#FFFFFF"/>')


def server_sun():
    # a server, and a rising sun for a Japanese company
    return tile('System engineer at Jacos',
                f'<circle cx="44" cy="20" r="7" fill="#FF7A6B"/>'
                f'<rect x="13" y="25" width="34" height="11" rx="4" {LINE}/><rect x="13" y="40" width="34" height="11" rx="4" {LINE}/>'
                f'<circle cx="20" cy="30.5" r="2" fill="#FFFFFF"/><circle cx="20" cy="45.5" r="2" fill="#FFFFFF"/>'
                f'<path d="M30 30.5h10M30 45.5h10" {LINE} stroke-opacity="0.6"/>')


def network():
    # a shield joining three machines: private networking
    return tile('Self-hosted private networking',
                f'<path d="M32 12l17 6v12c0 11-7 18-17 22-10-4-17-11-17-22V18Z" {LINE}/>'
                f'<path d="M25 37l7-11 7 11Z" {LINE} stroke-opacity="0.75"/>'
                f'<circle cx="32" cy="26" r="3.2" fill="#FFFFFF"/><circle cx="25" cy="37" r="3.2" fill="#FFFFFF"/>'
                f'<circle cx="39" cy="37" r="3.2" fill="#FFFFFF"/>')


def rack():
    # bare metal: a rack of servers
    rows = ''.join(f'<rect x="15" y="{14 + i * 13}" width="34" height="9" rx="3" {LINE}/>'
                   f'<circle cx="{43}" cy="{18.5 + i * 13}" r="1.8" fill="#FFFFFF"/>'
                   f'<path d="M20 {18.5 + i * 13}h12" {LINE} stroke-opacity="0.6"/>' for i in range(3))
    return tile('Bare metal and home servers', rows)


def gear():
    # still taking things apart: a gear, and a spark of something new
    teeth, r1, r2, cx, cy = 8, 13.5, 17.5, 29, 35
    pts = []
    for i in range(teeth * 2):
        a = math.pi * 2 * i / (teeth * 2)
        r = r2 if i % 2 == 0 else r1
        for d in (-0.16, 0.16):
            pts.append(f'{cx + r * math.cos(a + d):.2f} {cy + r * math.sin(a + d):.2f}')
    path = 'M' + 'L'.join(pts) + 'Z'
    return tile('Still taking things apart',
                f'<path d="{path}" {LINE}/><circle cx="{cx}" cy="{cy}" r="5.5" {LINE}/>'
                f'<path d="M48 10v10M43 15h10" {LINE}/>')


def marks():
    return {
        'marks/linux': linux,
        'marks/freelance': freelance,
        'marks/commits': commits,
        'marks/radar': radar,
        'marks/server-sun': server_sun,
        'marks/network': network,
        'marks/rack': rack,
        'marks/gear': gear,
    }
