"""Cyberpunk-lofi glass design system.

Colours are sampled from the night-workstation artwork (assets/art/
workstation.jpg) rather than invented: a k-means pass in OKLab over the
image gave the surfaces (#100818, #20102B, #462F64, #4F1F43 ...), and a
second pass over its brightest, most saturated pixels gave the neon
(#F59D5A sunset, #D54C66 rose, #C42599 and #A52FBE monitor glow).

The ground was then pulled darker and bluer, and the data hue moved to
coffee. The sequential ramp was searched in OKLCH and checked with the
dataviz validator against the *effective* glass surface -- the page colour
seen through a 7% white card, #1C1A29 -- and passes its ordinal checks:

    lightness monotone · adjacent dL >= 0.06 · dim end 2.44:1 on glass
    · single hue (12 deg spread)

Dark mode here is a selected set, not an inversion of the old warm one.
Every ink below clears WCAG AA for small text on that same surface.
"""

# -- surfaces ---------------------------------------------------------------
PAGE = "#0B0819"     # page ground: deep blue-leaning violet
PAGE_2 = "#120E26"   # secondary ground
SHADOW = "#060411"   # depth under cards

# Glass is a translucent white over the blurred colour blobs behind it, so
# fill and opacity are carried separately.
GLASS_FILL = "#FFFFFF"
GLASS_OP = 0.07      # card
GLASS_OP_2 = 0.04    # recessed well inside a card
GLASS_HI = 0.22      # top highlight line
EDGE = "#7E74B8"     # stroke base; drawn at low opacity via the edge gradient

# Names kept from the previous system so call sites stay unchanged.
CARD = GLASS_FILL
CARD_2 = "#1E1B30"
PAPER = PAGE
CREAM = "#F4F1FC"

# -- blobs that give the glass something to refract -------------------------
# Blue-violet and indigo carry the ground; coffee and plum warm it.
BLOB_VIOLET = "#4A3B8C"
BLOB_INDIGO = "#33307A"
BLOB_COFFEE = "#6B4A2E"
BLOB_PLUM = "#4A2E5E"

# -- ink (all >= 4.5:1 on #1D1824) ------------------------------------------
INK = "#E6E3F5"
INK_2 = "#AFA8CC"
INK_3 = "#8A83A6"

# -- marks ------------------------------------------------------------------
ACCENT = "#D9A066"       # single-series mark: caramel
ACCENT_SOFT = "#7C4F1F"  # the same hue at low emphasis, for area fills
SAGE = "#8C7BD9"         # one supporting periwinkle, for furniture not data
EMPTY = "#1E1B30"        # zero-value heat cell: reads as glass, not as data

# -- sequential ramp: dim -> bright (see module docstring) ------------------
RAMP = ["#7C4F1F", "#9D6425", "#C1792E", "#E2912E", "#FDAF25"]

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
    colors = colors or RAMP
    t = max(0.0, min(1.0, t))
    if t >= 1.0:
        return colors[-1]
    span = 1.0 / (len(colors) - 1)
    i = int(t / span)
    return lerp(colors[i], colors[i + 1], (t - i * span) / span)


def step(i, n=None):
    if n is None or n <= 1:
        return RAMP[min(i, len(RAMP) - 1)]
    return ramp(i / (n - 1))


def backdrop(w, h, seed=0):
    """Page ground plus soft colour blobs.

    Glassmorphism only reads if there is something behind the glass. These
    blobs are what the translucent cards pick up; without them a 7% white
    fill on a flat ground just looks grey.
    """
    blobs = [(0.14, 0.12, 0.54, BLOB_VIOLET, 0.50),
             (0.84, 0.16, 0.46, BLOB_INDIGO, 0.46),
             (0.66, 0.86, 0.48, BLOB_PLUM, 0.34),
             (0.28, 0.82, 0.42, BLOB_COFFEE, 0.26)]
    o = ['<defs>']
    for i, (_, _, _, col, _) in enumerate(blobs):
        o.append('<radialGradient id="blob%d_%d" cx=".5" cy=".5" r=".5">'
                 '<stop offset="0" stop-color="%s" stop-opacity=".85"/>'
                 '<stop offset=".55" stop-color="%s" stop-opacity=".30"/>'
                 '<stop offset="1" stop-color="%s" stop-opacity="0"/></radialGradient>'
                 % (seed, i, col, col, col))
    o.append('<linearGradient id="edge_%d" x1="0" y1="0" x2="1" y2="1">'
             '<stop offset="0" stop-color="#FFFFFF" stop-opacity=".30"/>'
             '<stop offset=".5" stop-color="#FFFFFF" stop-opacity=".10"/>'
             '<stop offset="1" stop-color="#FFFFFF" stop-opacity=".05"/>'
             '</linearGradient>' % seed)
    o.append('</defs>')
    o.append('<rect width="%d" height="%d" rx="16" fill="%s"/>' % (w, h, PAGE))
    for i, (cx, cy, r, col, op) in enumerate(blobs):
        rr = r * max(w, h)
        o.append('<ellipse cx="%.0f" cy="%.0f" rx="%.0f" ry="%.0f" fill="url(#blob%d_%d)" '
                 'opacity="%.2f"/>' % (cx * w, cy * h, rr, rr * 0.78, seed, i, op))
    return "".join(o)
