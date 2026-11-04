"""Coldbit theme for profile SVGs — icy pixel-art, dark-only.

Every colour routes through the tokens below (mirrors coldbit.cz globals.css @theme).
Radius 0, hard offset shadows with zero blur, stepped motion, Pixelify Sans for display,
JetBrains Mono for body. Fonts are subset per SVG and embedded as data URIs, so the
images render identically on GitHub without any external requests.
"""
import base64, functools, html, io, os, re

from fontTools import subset
from fontTools.ttLib import TTFont

# ── tokens ───────────────────────────────────────────────────────────────────
BACKGROUND = "#080b11"
PANEL = "#0d1420"
PANEL_HIGH = "#122033"
BORDER = "#1b2a3a"
FG = "#cfe9f7"
MUTED = "#5d7e92"
ICE = "#7fd4f5"
ICE_LIGHT = "#bfe9ff"
ICE_MID = "#5cc3ec"
ICE_SHADOW = "#2f7099"
BIT_GLOW = "#eafffe"
WHITE = "#ffffff"
ON_ICE = "#06121c"

PX = "'CB Pixel'"   # Pixelify Sans — display / labels / UI
MONO = "'CB Mono'"  # JetBrains Mono — body / prose
STEP = "steps(2, end)"

FONT_DIR = os.path.join(os.path.dirname(__file__), "fonts")
FONTS = {  # (family, weight, file)
    "px400": ("CB Pixel", 400, "PixelifySans-400.woff2"),
    "px700": ("CB Pixel", 700, "PixelifySans-700.woff2"),
    "mono400": ("CB Mono", 400, "JetBrainsMono-400.woff2"),
    "mono700": ("CB Mono", 700, "JetBrainsMono-700.woff2"),
}


def esc(s):
    return html.escape(str(s), quote=True)


# ── fonts ────────────────────────────────────────────────────────────────────
@functools.lru_cache(maxsize=None)
def _font(key):
    return TTFont(os.path.join(FONT_DIR, FONTS[key][2]))


def text_width(text, size, key="px700", spacing=0.0):
    """Advance width of `text` in px (spacing = letter-spacing in em)."""
    f = _font(key)
    cmap, hmtx, upm = f.getBestCmap(), f["hmtx"], f["head"].unitsPerEm
    w = sum(hmtx[cmap.get(ord(c), cmap.get(32))][0] for c in text)
    return w * size / upm + spacing * size * len(text)


def _subset_b64(key, chars):
    opts = subset.Options()
    opts.flavor = "woff2"
    opts.layout_features = ["kern", "liga", "calt"]
    opts.name_IDs = [1, 2]
    s = subset.Subsetter(opts)
    s.populate(text=chars + " ")
    f = TTFont(os.path.join(FONT_DIR, FONTS[key][2]))
    s.subset(f)
    f.flavor = "woff2"
    buf = io.BytesIO()
    f.save(buf)
    return base64.b64encode(buf.getvalue()).decode()


def font_css(svg_body):
    """@font-face rules for the fonts actually used, subset to the glyphs in svg_body."""
    chars = "".join(sorted(set(html.unescape(re.sub(r"<[^>]+>", "", svg_body)))))
    used = {(m.group(1), int(m.group(2))) for m in re.finditer(r'class="(px|mono)\b[^"]*"[^>]*?font-weight="(\d+)"', svg_body)}
    css = []
    for key, (family, weight, _) in FONTS.items():
        if (("px" if family == "CB Pixel" else "mono"), weight) in used:
            css.append(f"@font-face{{font-family:'{family}';font-weight:{weight};"
                       f"src:url(data:font/woff2;base64,{_subset_b64(key, chars)}) format('woff2');}}")
    return "\n".join(css)


def svg(w, h, body, css="", title=None):
    """Wrap a body into a standalone SVG with embedded, subset fonts."""
    fonts = font_css(body)
    t = f"<title>{esc(title)}</title>" if title else ""
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" '
            f'shape-rendering="crispEdges" role="img">{t}\n<style>\n{fonts}\n'
            f".px{{font-family:{PX},monospace}} .mono{{font-family:{MONO},ui-monospace,monospace}}\n"
            f"{css}\n</style>\n{body}\n</svg>\n")


# ── primitives ───────────────────────────────────────────────────────────────
def text(x, y, s, size, fill=FG, font="mono", weight=None, spacing=None, anchor=None, extra="", cls=""):
    weight = weight or (700 if font == "px" else 400)
    klass = f"{font} {cls}".strip()
    attrs = [f'x="{x:g}"', f'y="{y:g}"', f'class="{klass}"',
             f'font-size="{size}"', f'font-weight="{weight}"', f'fill="{fill}"']
    if spacing:
        attrs.append(f'letter-spacing="{spacing}em"')
    if anchor:
        attrs.append(f'text-anchor="{anchor}"')
    return f'<text {" ".join(attrs)} {extra}>{esc(s) if not s.startswith("<tspan") else s}</text>'


def label(x, y, s, size=17, fill=ICE, anchor=None, extra=""):
    """Uppercase, widely tracked UI label in square brackets."""
    return text(x, y, f"[ {s.upper()} ]", size, fill, font="px", weight=400, spacing=0.18, anchor=anchor, extra=extra)


def pixels(grid, x, y, scale, colors, extra=""):
    """Draw pixel art from a list of strings; each char maps through `colors` ('.' = empty)."""
    out = []
    for r, row in enumerate(grid):
        for c, ch in enumerate(row):
            if ch in colors:
                out.append(f'<rect x="{x + c * scale:g}" y="{y + r * scale:g}" width="{scale}" height="{scale}" fill="{colors[ch]}"/>')
    return f'<g {extra}>' + "".join(out) + "</g>"


CLOSE = ["x...x", ".x.x.", "..x..", ".x.x.", "x...x"]
MAXI = ["xxxxx", "x...x", "x...x", "x...x", "xxxxx"]
MINI = [".....", ".....", ".....", ".....", "xxxxx"]


def window(x, y, w, h, title, body="", high=False, shadow=8, bar=36, buttons=True, fill=None):
    """Retro OS window: hard offset shadow, chunky border, ice titlebar, square buttons."""
    fill = fill or (PANEL_HIGH if high else PANEL)
    out = [
        f'<rect x="{x + shadow}" y="{y + shadow}" width="{w}" height="{h}" fill="{ICE_SHADOW}"/>',
        f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{fill}"/>',
        f'<rect x="{x}" y="{y}" width="{w}" height="{bar}" fill="{ICE_SHADOW}"/>',
        f'<rect x="{x}" y="{y + bar}" width="{w}" height="3" fill="{BORDER}"/>',
        text(x + 16, y + bar / 2 + 7, title.upper(), 22, ICE_LIGHT, font="px", weight=400, spacing=0.12),
    ]
    if buttons:
        bx = x + w - 14 - 3 * 20 + 4
        for i, g in enumerate((MINI, MAXI, CLOSE)):
            cx, cy = bx + i * 24 - 12, y + (bar - 20) / 2
            out.append(f'<rect x="{cx}" y="{cy}" width="20" height="20" fill="{PANEL}"/>')
            out.append(pixels(g, cx + 5, cy + 5, 2, {"x": ICE_LIGHT}))
    out.append(f'<rect x="{x + 1.5}" y="{y + 1.5}" width="{w - 3}" height="{h - 3}" fill="none" stroke="{BORDER}" stroke-width="3"/>')
    out.append(f'<rect x="{x + 1.5}" y="{y + 1.5}" width="{w - 3}" height="{bar}" fill="none" stroke="{ICE_SHADOW}" stroke-width="3"/>')
    out.append(body)
    return "\n".join(out)


def chip(x, y, s, size=15, fg=ICE, solid=False):
    """Square tag chip; returns (svg, width)."""
    w = text_width(s, size, "mono400") + 20
    if solid:
        r = f'<rect x="{x}" y="{y}" width="{w:.0f}" height="30" fill="{ICE}"/>'
        t = text(x + w / 2, y + 20, s, size, ON_ICE, anchor="middle", weight=700)
    else:
        r = (f'<rect x="{x}" y="{y}" width="{w:.0f}" height="30" fill="{PANEL}"/>'
             f'<rect x="{x + 1}" y="{y + 1}" width="{w - 2:.0f}" height="28" fill="none" stroke="{ICE_SHADOW}" stroke-width="2"/>')
        t = text(x + w / 2, y + 20, s, size, fg, anchor="middle")
    return r + t, w


def chips(x, y, items, maxw, size=15):
    out, cx, cy = [], x, y
    for it in items:
        s, w = chip(cx, cy, it, size)
        if cx + w > x + maxw and cx > x:
            cx, cy = x, cy + 40
            s, w = chip(cx, cy, it, size)
        out.append(s)
        cx += w + 8
    return "".join(out), cy + 30


def grid_dots(x, y, w, h, step=16, color=BORDER):
    pid = f"g{x}{y}{w}{h}"
    return (f'<defs><pattern id="{pid}" x="{x}" y="{y}" width="{step}" height="{step}" patternUnits="userSpaceOnUse">'
            f'<rect width="2" height="2" fill="{color}"/></pattern></defs>'
            f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="url(#{pid})"/>')


BLINK_CSS = "@keyframes blink{50%{opacity:0}} .blink{animation:blink 1s steps(1) infinite}"
