"""Shared design tokens and SVG helpers.

Colours follow GitHub's Primer palette so every asset sits naturally on
github.com in both colour modes. The accent is GitHub's "merged" purple,
which also matches the contribution snake.
"""

from html import escape

DARK = {
    "name": "dark",
    "canvas": "#0d1117",
    "subtle": "#161b22",
    "inset": "#010409",
    "border": "#30363d",
    "border_muted": "#21262d",
    "fg": "#e6edf3",
    "muted": "#8b949e",
    "faint": "#6e7681",
    "accent": "#a371f7",
    "accent_em": "#8957e5",
    "accent_soft": "#d2a8ff",
    "blue": "#4493f8",
    "green": "#3fb950",
    "green_em": "#238636",
    "yellow": "#d29922",
    "red": "#f85149",
    "on_em": "#ffffff",
    "add_row": "#2ea043",
    "add_row_op": ".15",
    "add_gutter_op": ".3",
    "glow_op": ".32",
    "dot": "#30363d",
    # syntax highlighting (GitHub dark default)
    "s_kw": "#ff7b72",
    "s_str": "#a5d6ff",
    "s_ent": "#d2a8ff",
    "s_const": "#79c0ff",
    "s_var": "#ffa657",
}

LIGHT = {
    "name": "light",
    "canvas": "#ffffff",
    "subtle": "#f6f8fa",
    "inset": "#f6f8fa",
    "border": "#d0d7de",
    "border_muted": "#d8dee4",
    "fg": "#1f2328",
    "muted": "#59636e",
    "faint": "#818b98",
    "accent": "#8250df",
    "accent_em": "#8250df",
    "accent_soft": "#6639ba",
    "blue": "#0969da",
    "green": "#1a7f37",
    "green_em": "#1f883d",
    "yellow": "#9a6700",
    "red": "#cf222e",
    "on_em": "#ffffff",
    "add_row": "#2da44e",
    "add_row_op": ".12",
    "add_gutter_op": ".25",
    "glow_op": ".14",
    "dot": "#d0d7de",
    "s_kw": "#cf222e",
    "s_str": "#0a3069",
    "s_ent": "#8250df",
    "s_const": "#0550ae",
    "s_var": "#953800",
}

THEMES = (DARK, LIGHT)

SANS = "-apple-system, BlinkMacSystemFont, 'Segoe UI', 'Noto Sans', Helvetica, Arial, sans-serif"
MONO = "ui-monospace, SFMono-Regular, 'SF Mono', Menlo, Consolas, 'Liberation Mono', monospace"

# Linguist colours, nudged where the official colour vanishes on a dark canvas.
LANG = {
    "Python": "#3572A5",
    "Java": "#b07219",
    "C": "#8a8f98",
    "C++": "#f34b7d",
    "SQL": "#e38c00",
    "JavaScript": "#f1e05a",
    "TypeScript": "#3178c6",
    "HTML": "#e34c26",
    "CSS": "#663399",
    "Shell": "#89e051",
    "Jupyter Notebook": "#DA5B0B",
    "Dockerfile": "#384d54",
}

BASE_CSS = f"""
    .sans {{ font-family: {SANS}; }}
    .mono {{ font-family: {MONO}; }}
    .rise {{ animation: rise .9s cubic-bezier(.2,.8,.2,1) backwards; }}
    @keyframes rise {{ from {{ opacity: 0; transform: translateY(10px); }} to {{ opacity: 1; transform: none; }} }}
    @media (prefers-reduced-motion: reduce) {{ * {{ animation: none !important; }} }}
"""


def esc(text):
    return escape(str(text), quote=True)


def svg(width, height, body, label, css=""):
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
        f'viewBox="0 0 {width} {height}" role="img" aria-label="{esc(label)}">\n'
        f"<title>{esc(label)}</title>\n"
        f"<style>{BASE_CSS}{css}</style>\n{body}\n</svg>\n"
    )


def kt(times, total):
    """Format absolute seconds as a SMIL keyTimes list."""
    return ";".join(f"{min(max(t / total, 0), 1):.4f}" for t in times)


def window_opacity(start, end, total, fade=0.25, attr="opacity"):
    """SMIL animation: hidden, fades in at `start`, fades out at `end`."""
    times = [0, max(start - 0.001, 0), start + fade, end, min(end + fade, total), total]
    if start <= 0.001:
        times = [0, 0.001, fade, end, min(end + fade, total), total]
        return (f'<animate attributeName="{attr}" values="0;1;1;1;0;0" keyTimes="{kt(times, total)}" '
                f'dur="{total}s" repeatCount="indefinite"/>')
    return (f'<animate attributeName="{attr}" values="0;0;1;1;0;0" keyTimes="{kt(times, total)}" '
            f'dur="{total}s" repeatCount="indefinite"/>')


def draw_line(start, end, total, hide=None):
    """SMIL stroke-dashoffset draw for a path with pathLength="1"."""
    hide = hide if hide is not None else total
    times = [0, start, end, hide, total]
    return (f'<animate attributeName="stroke-dashoffset" values="1;1;0;0;1" keyTimes="{kt(times, total)}" '
            f'calcMode="spline" keySplines="0 0 1 1;.45 0 .25 1;0 0 1 1;0 0 1 1" '
            f'dur="{total}s" repeatCount="indefinite"/>')


def text_width(text, size, mono=False, bold=False):
    """Rough advance width; good enough for laying out pills and buttons."""
    if mono:
        return len(text) * size * 0.6
    narrow = set("ilI.,:;'|!·() []tfj-/")
    wide = set("mwMW@%")
    w = 0.0
    for ch in text:
        if ch in narrow:
            w += 0.3
        elif ch in wide:
            w += 0.85
        elif ch.isupper() or ch.isdigit():
            w += 0.64
        else:
            w += 0.54
    return w * size * (1.06 if bold else 1.0)


# 20x20 line icons, drawn for this profile in the spirit of Octicons.
ICONS = {
    "person": '<circle cx="10" cy="6.5" r="3.5"/><path d="M3.5 18c0-4.2 3-6.5 6.5-6.5s6.5 2.3 6.5 6.5"/>',
    "briefcase": '<rect x="2" y="6" width="16" height="11" rx="2"/><path d="M7 6V4.5A1.5 1.5 0 0 1 8.5 3h3A1.5 1.5 0 0 1 13 4.5V6M2 11h16"/>',
    "code": '<path d="M7 5 2 10l5 5M13 5l5 5-5 5"/>',
    "sparkle": '<path d="M10 2.5 11.6 8.4 17.5 10l-5.9 1.6L10 17.5l-1.6-5.9L2.5 10l5.9-1.6z"/>',
    "stack": '<path d="M10 3l8 4-8 4-8-4zM2 10.5l8 4 8-4M2 14l8 4 8-4"/>',
    "trophy": '<path d="M6 3h8v5a4 4 0 0 1-8 0zM6 5H3.5v1A2.5 2.5 0 0 0 6 8.5M14 5h2.5v1A2.5 2.5 0 0 1 14 8.5M10 12v3.5M6.5 17.5h7"/>',
    "graph": '<path d="M2.5 17.5h15M5.5 14v-3M9 14V5M12.5 14V8M16 14v-5"/>',
    "mail": '<rect x="2" y="4.5" width="16" height="11" rx="2"/><path d="m2.5 5.5 7.5 5.5 7.5-5.5"/>',
    "workflow": '<circle cx="4" cy="10" r="2"/><circle cx="16" cy="4.5" r="2"/><circle cx="16" cy="15.5" r="2"/><path d="M6 10h2c2.5 0 2.5-5.5 6-5.5M8 10c2.5 0 2.5 5.5 6 5.5"/>',
    "repo": '<path d="M4 16.5V4.5A2 2 0 0 1 6 2.5h10v12H6a2 2 0 0 0-2 2zm0 0a2 2 0 0 0 2 2h10M7.5 6.5h5"/>',
    "globe": '<circle cx="10" cy="10" r="7.5"/><path d="M2.5 10h15M10 2.5c2.2 2.3 3 4.8 3 7.5s-.8 5.2-3 7.5c-2.2-2.3-3-4.8-3-7.5s.8-5.2 3-7.5z"/>',
    "check": '<path d="m5 10.5 3.2 3.2L15.5 6.5"/>',
    "merge": '<circle cx="5.5" cy="4" r="2"/><circle cx="5.5" cy="16" r="2"/><circle cx="14.5" cy="11" r="2"/><path d="M5.5 6v8M5.5 6c0 3.5 3 5 7 5"/>',
    "pr": '<circle cx="5.5" cy="4" r="2"/><circle cx="5.5" cy="16" r="2"/><circle cx="14.5" cy="16" r="2"/><path d="M5.5 6v8M14.5 14V8a2.5 2.5 0 0 0-2.5-2.5H9M10.5 3.5 8.5 5.5l2 2"/>',
    "file": '<path d="M5 2.5h6.5L15.5 6.5v11H5zM11.5 2.5v4h4"/>',
    "branch": '<circle cx="6" cy="4" r="2"/><circle cx="6" cy="16" r="2"/><circle cx="14" cy="6" r="2"/><path d="M6 6v8M14 8c0 4-8 3-8 6"/>',
}


def icon(name, x, y, color, size=20, width=1.6):
    scale = size / 20
    return (f'<g transform="translate({x} {y}) scale({scale:g})" fill="none" stroke="{color}" '
            f'stroke-width="{width / scale:g}" stroke-linecap="round" stroke-linejoin="round">{ICONS[name]}</g>')
