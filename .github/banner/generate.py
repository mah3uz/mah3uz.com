"""Draws the README banner, in dark and light, into .github/banner/.

The banner follows the site's own brand banners: a rounded card with a radial glow, three viewfinder corners and a
peeled bottom-right corner, the bracketed "m" tile, and the product logos. Text is drawn as outlines, so the banner
looks the same wherever it is shown, whatever fonts the viewer has.

    python3 -m pip install fonttools
    python3 .github/banner/generate.py
    INTER_FONTS=~/Library/Fonts MONO_FONTS=~/Library/Fonts python3 .github/banner/generate.py   # fonts elsewhere
"""
import os
import re
from pathlib import Path

from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.ttLib import TTFont

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).parent
# Inter and JetBrains Mono. Point these at wherever the fonts live on your machine, if not here.
INTER = Path(os.environ.get('INTER_FONTS', '/usr/share/fonts/opentype/inter'))
MONO = Path(os.environ.get('MONO_FONTS', '/usr/share/fonts/truetype/jetbrains-mono'))

W, H = 1280, 400

THEMES = {
    'dark': {
        'bg': ('#0A1A20', '#0D2A31'), 'glow': ('#21BDB0', 0.24), 'back': ('#62EDD4', '#21BDB0'),
        'edge': ('#62EDD4', 0.14), 'corners': 0.6, 'title': '#FFFFFF', 'accent': '#62EDD4',
        'text': '#E9F7F7', 'muted': '#A6D3D6', 'lift': 0.4, 'chip': ('#62EDD4', 0.08), 'chip_edge': ('#62EDD4', 0.22),
    },
    'light': {
        'bg': ('#F3FCFA', '#DDF4F0'), 'glow': ('#62EDD4', 0.38), 'back': ('#167A8E', '#0F5F78'),
        'edge': ('#1388A6', 0.14), 'corners': 0.55, 'title': '#043040', 'accent': '#1388A6',
        'text': '#0F5F78', 'muted': '#0F5F78', 'lift': 0.16, 'chip': ('#FFFFFF', 0.7), 'chip_edge': ('#1388A6', 0.2),
    },
}

PRODUCTS = ['nibble', 'quarry', 'sysman', 'darwan', 'insensical', 'rrussat']


class Font:
    def __init__(self, path):
        self.font = TTFont(path)
        self.glyphs = self.font.getGlyphSet()
        self.cmap = self.font.getBestCmap()
        self.upm = self.font['head'].unitsPerEm
        self.advance = self.font['hmtx'].metrics

    def width(self, text, size, tracking=0.0):
        scale = size / self.upm
        total = sum(self.advance[self.cmap[ord(c)]][0] * scale for c in text)
        return total + tracking * size * (len(text) - 1)

    def path(self, text, x, y, size, tracking=0.0):
        """Outlines for text whose baseline starts at (x, y)."""
        scale = size / self.upm
        pen = SVGPathPen(self.glyphs)
        cursor = x
        for char in text:
            name = self.cmap[ord(char)]
            # font units are y-up; SVG is y-down
            self.glyphs[name].draw(TransformPen(pen, (scale, 0, 0, -scale, cursor, y)))
            cursor += self.advance[name][0] * scale + tracking * size
        return pen.getCommands()


def prefixed(svg, prefix):
    """An SVG's inner markup, with every id made unique to this banner."""
    inner = re.sub(r'^.*?<svg[^>]*>', '', svg, count=1, flags=re.S)
    inner = re.sub(r'</svg>\s*$', '', inner.strip())
    inner = re.sub(r'<title[^>]*>.*?</title>', '', inner, flags=re.S)
    inner = re.sub(r'\bid="([^"]+)"', rf'id="{prefix}-\1"', inner)
    inner = re.sub(r'url\(#([^)]+)\)', rf'url(#{prefix}-\1)', inner)
    inner = re.sub(r'href="#([^"]+)"', rf'href="#{prefix}-\1"', inner)
    return inner


def view_box(svg):
    return re.search(r'viewBox="([^"]+)"', svg).group(1)


def brand_tile():
    """The bracketed "m" tile from the theme's BrandMark component, made static."""
    vue = (ROOT / 'site/themes/neat/components/BrandMark.vue').read_text()
    svg = re.search(r'(<svg.*?</svg>)', vue, re.S).group(1)
    svg = re.sub(r'\s:?class="[^"]*"', '', svg)
    svg = re.sub(r'\saria-hidden="true"', '', svg)
    return svg


def banner(name, t, fonts):
    bold, medium, mono = fonts
    g = []
    a = g.append

    a(f'''<defs>
<linearGradient id="bg" x1="0" y1="0" x2="{W}" y2="{H}" gradientUnits="userSpaceOnUse"><stop offset="0" stop-color="{t['bg'][0]}"/><stop offset="1" stop-color="{t['bg'][1]}"/></linearGradient>
<radialGradient id="glow" cx="277.77" cy="200" r="308.57" gradientUnits="userSpaceOnUse"><stop offset="0" stop-color="{t['glow'][0]}" stop-opacity="{t['glow'][1]}"/><stop offset="1" stop-color="{t['glow'][0]}" stop-opacity="0"/></radialGradient>
<radialGradient id="glow2" cx="1040" cy="60" r="420" gradientUnits="userSpaceOnUse"><stop offset="0" stop-color="{t['glow'][0]}" stop-opacity="{t['glow'][1] * 0.55:.3f}"/><stop offset="1" stop-color="{t['glow'][0]}" stop-opacity="0"/></radialGradient>
<linearGradient id="back" x1="0" y1="296" x2="0" y2="400" gradientUnits="userSpaceOnUse"><stop offset="0" stop-color="{t['back'][0]}"/><stop offset="1" stop-color="{t['back'][1]}"/></linearGradient>
<linearGradient id="flap" x1="1269.6" y1="389.6" x2="1196.8" y2="316.8" gradientUnits="userSpaceOnUse"><stop offset="0" stop-color="#A6D3D6"/><stop offset="0.5" stop-color="#E9F7F7"/><stop offset="1" stop-color="#FFFFFF"/></linearGradient>
<linearGradient id="ink" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#62EDD4"/><stop offset="0.45" stop-color="#21BDB0"/><stop offset="1" stop-color="#1388A6"/></linearGradient>
<pattern id="dots" width="24" height="24" patternUnits="userSpaceOnUse"><circle cx="2" cy="2" r="1.1" fill="{t['accent']}" fill-opacity="0.12"/></pattern>
<filter id="flapShadow" x="-30%" y="-30%" width="160%" height="160%"><feGaussianBlur stdDeviation="5"/></filter>
<filter id="lift" x="-30%" y="-30%" width="160%" height="170%"><feDropShadow dx="0" dy="6" stdDeviation="6" flood-color="#043040" flood-opacity="{t['lift']}"/></filter>
<clipPath id="cardClip"><rect width="{W}" height="{H}" rx="28"/></clipPath>
<clipPath id="cutClip"><path d="M0 0H{W}V296Q1221.76 341.76 1176 400H0Z"/></clipPath>
</defs>''')

    # the card, its peeled corner and the viewfinder corners: the same shapes as the site's own banners
    a(f'''<g clip-path="url(#cardClip)">
<rect width="{W}" height="{H}" rx="28" fill="url(#back)"/>
<g clip-path="url(#cutClip)">
<rect width="{W}" height="{H}" fill="url(#bg)"/>
<rect width="{W}" height="{H}" fill="url(#dots)"/>
<rect width="{W}" height="{H}" fill="url(#glow)"/>
<rect width="{W}" height="{H}" fill="url(#glow2)"/>
<path d="M1280 296C1244.64 292.88 1209.28 302.24 1196.8 316.8C1182.24 329.28 1172.88 364.64 1176 400Q1221.76 341.76 1280 296Z" transform="translate(-5 6)" fill="#043040" fill-opacity="0.28" filter="url(#flapShadow)"/>
</g>
<path d="M1280 296C1244.64 292.88 1209.28 302.24 1196.8 316.8C1182.24 329.28 1172.88 364.64 1176 400Q1221.76 341.76 1280 296Z" fill="url(#flap)"/>
</g>
<rect x="0.5" y="0.5" width="1279" height="399" rx="27.5" fill="none" stroke="{t['edge'][0]}" stroke-opacity="{t['edge'][1]}" clip-path="url(#cutClip)"/>
<path d="M30 76V44Q30 30 44 30H76M1250 76V44Q1250 30 1236 30H1204M30 324V356Q30 370 44 370H76" fill="none" stroke="#21BDB0" stroke-opacity="{t['corners']}" stroke-width="5" stroke-linecap="round"/>''')

    # the bracketed "m" tile
    tile = brand_tile()
    a(f'<svg x="120" y="92" width="216" height="216" viewBox="{view_box(tile)}" overflow="visible">{prefixed(tile, "mark")}</svg>')

    x = 392
    # eyebrow
    eyebrow = 'SOFTWARE ENGINEER  ·  SINCE 2009'
    a(f'<path d="{mono.path(eyebrow, x + 2, 126, 15, tracking=0.12)}" fill="{t["accent"]}"/>')
    # wordmark: mah3uz, with the 3 in the brand gradient
    size = 96
    parts = [('mah', t['title']), ('3', 'url(#ink)'), ('uz', t['title'])]
    cursor = x
    for text, fill in parts:
        a(f'<path d="{bold.path(text, cursor, 214, size, tracking=-0.035)}" fill="{fill}"/>')
        cursor += bold.width(text, size, tracking=-0.035) - 0.035 * size
    # tagline
    a(f'<path d="{medium.path("Products, developer tools & Linux desktop software.", x + 2, 262, 26, tracking=-0.01)}" fill="{t["text"]}"/>')

    # product logos, each on its own lifted chip
    lx, ly, size = x, 292, 46
    for i, product in enumerate(PRODUCTS):
        svg = (ROOT / 'public/logos' / f'{product}.svg').read_text()
        px = lx + i * (size + 14)
        a(f'<svg x="{px}" y="{ly}" width="{size}" height="{size}" viewBox="{view_box(svg)}" filter="url(#lift)">{prefixed(svg, f"{name}-{product}")}</svg>')

    # site address, bottom right of the text column, clear of the peel
    url = 'mah3uz.com'
    a(f'<path d="{mono.path(url, 1112 - mono.width(url, 18, 0.04), 324, 18, tracking=0.04)}" fill="{t["muted"]}"/>')

    title = 'mah3uz — software engineer since 2009, building products, developer tools and Linux desktop software'
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" '
            f'aria-label="{title}"><title>{title}</title>' + '\n'.join(g) + '</svg>\n')


def main():
    fonts = (
        Font(INTER / 'Inter-ExtraBold.otf'),
        Font(INTER / 'Inter-Medium.otf'),
        Font(MONO / 'JetBrainsMono-Medium.ttf'),
    )
    for name, theme in THEMES.items():
        target = OUT / f'banner-{name}.svg'
        target.write_text(banner(name, theme, fonts))
        print(f'wrote {target.relative_to(ROOT)} ({target.stat().st_size // 1024} KB)')


if __name__ == '__main__':
    main()
