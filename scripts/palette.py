"""Shared visual language for every generated asset.

Palette is carried over from the badge row in the original profile so the
generated SVGs and the shields.io badges read as one system.
"""

BG0 = "#0E1716"   # deepest ground
BG1 = "#14201F"   # card ground
BG2 = "#1B2A28"   # raised surface
LINE = "#263835"  # hairlines / grid

PINE = "#2E4A47"
SLATE = "#3A4E4C"
ESPRESSO = "#4A3527"
BROWN = "#6B4E3A"
COFFEE = "#6F4E37"

CREAM = "#E8DFD1"   # primary text
SAND = "#C9B99A"    # secondary text
MUTED = "#7E908C"   # tertiary text
AMBER = "#D8A657"   # single hot accent

# Ordered ramp used for streamlines, language bars and heat cells.
RAMP = [PINE, SLATE, "#4B6B60", BROWN, "#9A7A55", SAND, CREAM]

SANS = "'Segoe UI',Ubuntu,-apple-system,BlinkMacSystemFont,Helvetica,Arial,sans-serif"
MONO = "'SFMono-Regular',Consolas,'Liberation Mono',Menlo,monospace"


def hex_to_rgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def rgb_to_hex(rgb):
    return "#%02X%02X%02X" % tuple(max(0, min(255, int(round(c)))) for c in rgb)


def lerp(c1, c2, t):
    a, b = hex_to_rgb(c1), hex_to_rgb(c2)
    return rgb_to_hex(tuple(a[i] + (b[i] - a[i]) * t for i in range(3)))


def ramp(t, colors=None):
    """Sample the palette ramp at t in [0, 1]."""
    colors = colors or RAMP
    t = max(0.0, min(1.0, t))
    if t >= 1.0:
        return colors[-1]
    span = 1.0 / (len(colors) - 1)
    i = int(t / span)
    return lerp(colors[i], colors[i + 1], (t - i * span) / span)
