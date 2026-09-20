"""Cyberpunk-lofi glass design system.

Colours are sampled from the night-workstation artwork (assets/art/
workstation.jpg) rather than invented: a k-means pass in OKLab over the
image gave the surfaces (#100818, #20102B, #462F64, #4F1F43 ...), and a
second pass over its brightest, most saturated pixels gave the neon
(#F59D5A sunset, #D54C66 rose, #C42599 and #A52FBE monitor glow).

The sequential ramp was then searched in OKLCH and checked with the
dataviz validator against the *effective* glass surface -- the page colour
seen through a 7% white card, #1D1824 -- and passes its ordinal checks:

    lightness monotone · adjacent dL >= 0.06 · dim end >= 2:1 on glass
    · single hue (14 deg spread)

Dark mode here is a selected set, not an inversion of the old warm one.
Every ink below clears WCAG AA for small text on that same surface.
"""

# -- surfaces ---------------------------------------------------------------
PAGE = "#0C0714"     # page ground, a shade darker than the artwork's own black
PAGE_2 = "#140B1F"   # secondary ground
SHADOW = "#07040D"   # depth under cards

# Glass is a translucent white over the blurred colour blobs behind it, so
# fill and opacity are carried separately.
GLASS_FILL = "#FFFFFF"
GLASS_OP = 0.07      # card
GLASS_OP_2 = 0.04    # recessed well inside a card
GLASS_HI = 0.22      # top highlight line
EDGE = "#8E74B8"     # stroke base; drawn at low opacity via the edge gradient

# Names kept from the previous system so call sites stay unchanged.
CARD = GLASS_FILL
CARD_2 = "#241A2E"
PAPER = PAGE
CREAM = "#F6EFFB"

# -- blobs that give the glass something to refract -------------------------
BLOB_MAGENTA = "#C42599"
BLOB_VIOLET = "#7D3DC1"
BLOB_ORANGE = "#F59D5A"
BLOB_ROSE = "#D54C66"

# -- ink (all >= 4.5:1 on #1D1824) ------------------------------------------
INK = "#EFE7F7"
INK_2 = "#C3B2D8"
INK_3 = "#9B87B4"

# -- marks ------------------------------------------------------------------
ACCENT = "#F0559A"       # single-series mark: neon rose
ACCENT_SOFT = "#8E3A66"  # the same hue at low emphasis, for area fills
SAGE = "#A78BFA"         # one supporting violet, for furniture not data
EMPTY = "#241A2E"        # zero-value heat cell: reads as glass, not as data

# -- sequential ramp: dim -> bright (see module docstring) ------------------
RAMP = ["#7F2E55", "#A33D6A", "#C44F85", "#E861A0", "#FD73D0"]

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
    blobs = [(0.16, 0.10, 0.52, BLOB_VIOLET, 0.55),
             (0.82, 0.18, 0.46, BLOB_MAGENTA, 0.42),
             (0.62, 0.88, 0.50, BLOB_ROSE, 0.34),
             (0.30, 0.78, 0.40, BLOB_ORANGE, 0.20)]
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
