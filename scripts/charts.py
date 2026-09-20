"""Small SVG chart primitives, built to the dataviz rules.

Shared by the dashboard generators. Every helper returns an SVG fragment.

Rules enforced here rather than remembered per call site:
  * one accent colour for a single series; never a value-ramp across
    nominal categories (that double-encodes length as hue)
  * sequential = one hue, light -> dark, for magnitude only
  * 4px rounded data-ends, 2px gaps between adjacent fills
  * hairline, solid (never dashed) grid; axes recede
  * direct labels, because a README image cannot have a tooltip
"""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from palette import (ACCENT, ACCENT_SOFT, CARD, CARD_2, EDGE, EMPTY, FONT,
                     INK, INK_2, INK_3, RAMP, ramp)

F = '"%s"' % FONT


def esc(s):
    return str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def card(x, y, w, h, title, note=""):
    """A kraft card with a soft offset shadow -- the 'stacked paper' motif."""
    o = ['<rect x="%d" y="%d" width="%d" height="%d" rx="14" fill="%s" opacity=".55"/>'
         % (x + 3, y + 4, w, h, EDGE)]
    o.append('<rect x="%d" y="%d" width="%d" height="%d" rx="14" fill="%s" stroke="%s"/>'
             % (x, y, w, h, CARD, EDGE))
    o.append('<text x="%d" y="%d" font-family=%s font-size="15" font-weight="700" fill="%s">'
             '%s</text>' % (x + 20, y + 32, F, INK, esc(title)))
    if note:
        o.append('<text x="%d" y="%d" text-anchor="end" font-family=%s font-size="11.5" '
                 'fill="%s">%s</text>' % (x + w - 20, y + 32, F, INK_3, esc(note)))
    return "".join(o)


def stat(x, y, w, label, value, unit=""):
    """A stat tile. The number IS the chart -- no one-bar bar charts."""
    o = ['<rect x="%d" y="%d" width="%d" height="96" rx="14" fill="%s" opacity=".55"/>'
         % (x + 3, y + 4, w, EDGE)]
    o.append('<rect x="%d" y="%d" width="%d" height="96" rx="14" fill="%s" stroke="%s"/>'
             % (x, y, w, CARD, EDGE))
    o.append('<text x="%d" y="%d" font-family=%s font-size="12" fill="%s">%s</text>'
             % (x + 20, y + 30, F, INK_3, esc(label)))
    o.append('<text x="%d" y="%d" font-family=%s font-size="38" font-weight="700" fill="%s">'
             '%s</text>' % (x + 20, y + 74, F, INK, esc(value)))
    if unit:
        o.append('<text x="%d" y="%d" text-anchor="end" font-family=%s font-size="12" '
                 'fill="%s">%s</text>' % (x + w - 18, y + 74, F, INK_3, esc(unit)))
    return "".join(o)


def _arc(cx, cy, r, a0, a1):
    x0, y0 = cx + r * math.cos(a0), cy + r * math.sin(a0)
    x1, y1 = cx + r * math.cos(a1), cy + r * math.sin(a1)
    large = 1 if (a1 - a0) > math.pi else 0
    return x0, y0, x1, y1, large


def donut(cx, cy, r_out, r_in, parts, total_label=""):
    """Part-to-whole, <= 5 segments, sequential ramp (share is ordered by size).

    Segments are separated by a 2px surface gap and direct-labelled, so
    identity never rests on colour alone.
    """
    o = []
    total = sum(v for _, v in parts) or 1
    ang = -math.pi / 2                      # start at 12 o'clock
    gap = 0.016                             # radians of surface between segments
    mid = (r_out + r_in) / 2.0
    width = r_out - r_in
    for i, (name, val) in enumerate(parts):
        sweep = 2 * math.pi * (val / total)
        a0, a1 = ang + gap / 2, ang + sweep - gap / 2
        if a1 <= a0:
            a1 = a0 + 0.004
        x0, y0, x1, y1, large = _arc(cx, cy, mid, a0, a1)
        col = ramp(i / max(1, len(parts) - 1))
        o.append('<path d="M%.2f,%.2f A%.2f,%.2f 0 %d 1 %.2f,%.2f" fill="none" stroke="%s" '
                 'stroke-width="%.1f"/>' % (x0, y0, mid, mid, large, x1, y1, col, width))
        ang += sweep
    if total_label:
        o.append('<text x="%d" y="%d" text-anchor="middle" font-family=%s font-size="13" '
                 'font-weight="700" fill="%s">%s</text>' % (cx, cy + 5, F, INK_2, esc(total_label)))
    return "".join(o)


def legend(x, y, items, pitch=26):
    """Swatch + name + value, one row each. Always present for >= 2 segments."""
    o = []
    for i, (name, val) in enumerate(items):
        yy = y + i * pitch
        o.append('<rect x="%d" y="%d" width="12" height="12" rx="3" fill="%s"/>'
                 % (x, yy - 10, ramp(i / max(1, len(items) - 1))))
        o.append('<text x="%d" y="%d" font-family=%s font-size="13" fill="%s">%s</text>'
                 % (x + 20, yy, F, INK_2, esc(name)))
        o.append('<text x="%d" y="%d" font-family=%s font-size="13" font-weight="700" '
                 'fill="%s">%s</text>' % (x + 180, yy, F, INK, esc(val)))
    return "".join(o)


def area(x, y, w, h, values, x_labels=None, peak_label=True):
    """Trend over time, one series -> one hue, soft fill, 2px line.

    No legend: with a single series the card title names it.
    """
    o = []
    if not values:
        return ('<text x="%d" y="%d" font-family=%s font-size="12.5" fill="%s">fills in after '
                'the first sync</text>' % (x, y + h / 2, F, INK_3))
    mx = max(values) or 1
    n = len(values)
    px = lambda i: x + (w * i / max(1, n - 1))
    py = lambda v: y + h - (v / mx) * h

    # recessive solid gridlines + value ticks
    for frac in (0, 0.5, 1.0):
        gy = y + h - frac * h
        o.append('<path d="M%d %.1f H%d" stroke="%s" stroke-width="1"/>' % (x, gy, x + w, EDGE))
        o.append('<text x="%d" y="%.1f" text-anchor="end" font-family=%s font-size="10.5" '
                 'fill="%s">%d</text>' % (x - 8, gy + 4, F, INK_3, round(mx * frac)))

    pts = [(px(i), py(v)) for i, v in enumerate(values)]
    fill = "M%.1f,%.1f " % (pts[0][0], y + h) + " ".join("L%.1f,%.1f" % p for p in pts) \
           + " L%.1f,%.1f Z" % (pts[-1][0], y + h)
    o.append('<path d="%s" fill="%s" opacity=".38"/>' % (fill, ACCENT_SOFT))
    line = "M%.1f,%.1f " % pts[0] + " ".join("L%.1f,%.1f" % p for p in pts[1:])
    o.append('<path d="%s" fill="none" stroke="%s" stroke-width="2" stroke-linejoin="round" '
             'stroke-linecap="round"/>' % (line, ACCENT))

    if peak_label:
        i = values.index(mx)
        cx_, cy_ = px(i), py(mx)
        o.append('<circle cx="%.1f" cy="%.1f" r="4.5" fill="%s" stroke="%s" stroke-width="2"/>'
                 % (cx_, cy_, ACCENT, CARD))
        anchor = "end" if cx_ > x + w * 0.75 else "start"
        dx = -10 if anchor == "end" else 10
        o.append('<text x="%.1f" y="%.1f" text-anchor="%s" font-family=%s font-size="11.5" '
                 'font-weight="700" fill="%s">peak %d</text>'
                 % (cx_ + dx, cy_ - 10, anchor, F, INK_2, mx))

    for i, lab in (x_labels or []):
        if 0 <= i < n:
            o.append('<text x="%.1f" y="%d" text-anchor="middle" font-family=%s font-size="10.5" '
                     'fill="%s">%s</text>' % (px(i), y + h + 18, F, INK_3, esc(lab)))
    return "".join(o)


def hbars(x, y, w, rows, pitch=34, value_fmt=str):
    """Magnitude across nominal categories -> ONE colour for every bar.

    Colouring these darker-where-bigger would double-encode length as hue.
    """
    o = []
    mx = max((v for _, v in rows), default=1) or 1
    track = w - 250
    for i, (name, val) in enumerate(rows):
        yy = y + i * pitch
        o.append('<text x="%d" y="%d" font-family=%s font-size="13" fill="%s">%s</text>'
                 % (x, yy, F, INK_2, esc(name)))
        o.append('<rect x="%d" y="%d" width="%d" height="10" rx="5" fill="%s"/>'
                 % (x + 200, yy - 9, track, CARD_2))
        bw = max(6, int(track * val / mx))
        o.append('<rect x="%d" y="%d" width="%d" height="10" rx="5" fill="%s">'
                 '<animate attributeName="width" values="0;%d" dur=".8s" begin="%.2fs" '
                 'fill="freeze" calcMode="spline" keySplines=".2 .8 .2 1"/></rect>'
                 % (x + 200, yy - 9, bw, ACCENT, bw, 0.2 + 0.08 * i))
        o.append('<text x="%d" y="%d" text-anchor="end" font-family=%s font-size="12" '
                 'fill="%s">%s</text>' % (x + w, yy, F, INK_3, esc(value_fmt(val))))
    return "".join(o)


def heatmap(x, y, weeks, peak, cell=11, gap=3):
    """Magnitude on a grid -> sequential, one hue, light -> dark."""
    o = []
    for wi, week in enumerate(weeks):
        for day in week:
            c = day["contributionCount"]
            wd = day["weekday"]
            fill = EMPTY if c == 0 else ramp(0.12 + 0.88 * min(1.0, (c / max(1, peak)) ** 0.6))
            o.append('<rect x="%d" y="%d" width="%d" height="%d" rx="2.5" fill="%s"/>'
                     % (x + wi * (cell + gap), y + wd * (cell + gap), cell, cell, fill))
    return "".join(o)


def heat_legend(x, y, cell=11, gap=3):
    o = ['<text x="%d" y="%d" text-anchor="end" font-family=%s font-size="11" fill="%s">less</text>'
         % (x - 10, y + cell - 1, F, INK_3)]
    o.append('<rect x="%d" y="%d" width="%d" height="%d" rx="2.5" fill="%s"/>' % (x, y, cell, cell, EMPTY))
    for i in range(5):
        o.append('<rect x="%d" y="%d" width="%d" height="%d" rx="2.5" fill="%s"/>'
                 % (x + (i + 1) * (cell + gap), y, cell, cell, RAMP[i]))
    o.append('<text x="%d" y="%d" font-family=%s font-size="11" fill="%s">more</text>'
             % (x + 6 * (cell + gap) + 10, y + cell - 1, F, INK_3))
    return "".join(o)
