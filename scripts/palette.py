"""Lofi-cafe design system for every generated asset.

Warm paper instead of a dark instrument panel, Arial instead of a mono
face, and soft stacked-paper cards instead of hairline frames.

Colour is not eyeballed here. The sequential ramp below was produced by
searching OKLCH space under the dataviz validator and passes its ordinal
checks against the kraft card surface:

    lightness monotone · adjacent dL >= 0.06 · light end >= 2:1 vs surface
    · single hue (3 deg spread)

An earlier attempt used four warm categorical hues for language share. A
search over cafe-plausible colour space found only 7 valid 4-hue sets in
the whole space, and every one of them needed a green or teal to pass CVD
separation -- i.e. an all-warm categorical palette does not exist. Since
language share is *ordered* (by size), the honest fix was to change the
form, not to force the colour: share and the contribution heatmap both use
the single-hue ramp, and single-series marks use one accent.
"""

# -- surfaces (warm paper) --------------------------------------------------
PAPER = "#F5EDE0"   # page ground
CARD = "#EFE4D0"    # kraft card the charts sit on
CARD_2 = "#E8DAC0"  # recessed well inside a card
EDGE = "#DFCDB0"    # hairline / card edge
SHADOW = "#D8C4A4"  # soft offset shadow under cards

# -- ink --------------------------------------------------------------------
INK = "#3D2B1F"     # primary text (espresso)
INK_2 = "#6B5442"   # secondary text
INK_3 = "#725C48"   # muted text, axis labels (4.99:1 on card -- AA for small text)

# -- marks ------------------------------------------------------------------
ACCENT = "#C0562F"      # terracotta: the single-series mark colour
ACCENT_SOFT = "#E0A88F"  # accent at low emphasis (area fills)
SAGE = "#7A8B5F"        # one supporting hue, used for non-data furniture only
CREAM = "#FBF6EC"       # highlight / paper white

# -- sequential ramp: caramel -> espresso (validated, see module docstring) --
RAMP = ["#CB955D", "#B97F43", "#A56B2D", "#8D591D", "#774711"]
EMPTY = "#E5D9C2"   # zero-value heatmap cell: reads as card, not as data

# -- type -------------------------------------------------------------------
# Arial by request. SVGs render inside GitHub's <img> sandbox where webfonts
# never load, so the stack stays to faces that are already on the machine.
FONT = "Arial, Helvetica, 'Liberation Sans', sans-serif"


def hex_to_rgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def rgb_to_hex(rgb):
    return "#%02X%02X%02X" % tuple(max(0, min(255, int(round(c)))) for c in rgb)


def lerp(c1, c2, t):
    a, b = hex_to_rgb(c1), hex_to_rgb(c2)
    return rgb_to_hex(tuple(a[i] + (b[i] - a[i]) * t for i in range(3)))


def ramp(t, colors=None):
    """Sample the sequential ramp at t in [0, 1]."""
    colors = colors or RAMP
    t = max(0.0, min(1.0, t))
    if t >= 1.0:
        return colors[-1]
    span = 1.0 / (len(colors) - 1)
    i = int(t / span)
    return lerp(colors[i], colors[i + 1], (t - i * span) / span)


def step(i, n=None):
    """Pick a discrete ramp step; used where bins, not a gradient, are wanted."""
    if n is None or n <= 1:
        return RAMP[min(i, len(RAMP) - 1)]
    return ramp(i / (n - 1))
