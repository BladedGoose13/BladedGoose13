"""Render assets/pipeline.svg -- how a project moves, in cafe terms.

Warm rounded cards on kraft paper, Arial lowercase, a dotted route with a
bean travelling along it. Deliberately friendly rather than an enterprise
architecture diagram.

Same <img>-sandbox contract: authored visible, animation only overrides.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from palette import (ACCENT, ACCENT_SOFT, CREAM, FONT, GLASS_FILL, GLASS_HI,
                     GLASS_OP, INK, INK_2, INK_3, RAMP, SAGE, backdrop)

W, H = 1200, 340
F = '"%s"' % FONT

STAGES = [
    ("ingest", "instruments, archives"),
    ("check", "units, schema, bounds"),
    ("simulate", "quantum espresso, slurm"),
    ("reduce", "features, descriptors"),
    ("learn", "sciml surrogate"),
    ("serve", "api, plots, papers"),
]

BOX_W, BOX_H, BOX_Y = 168, 92, 106
PAD = 30
GAP = (W - 2 * PAD - len(STAGES) * BOX_W) / (len(STAGES) - 1)


def bx(i):
    return PAD + i * (BOX_W + GAP)


def build():
    o = []
    a = o.append
    a('<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" '
      'width="%d" height="%d" viewBox="0 0 %d %d" role="img" '
      'aria-label="How a project moves: ingest, check, simulate, reduce, learn, serve, '
      'with the model choosing the next simulation">' % (W, H, W, H))

    a(backdrop(W, H, seed=5))

    a('<text x="%d" y="46" font-family=%s font-size="17" font-weight="700" fill="%s">'
      'how a project actually moves</text>' % (PAD, F, INK))
    a('<text x="%d" y="46" text-anchor="end" font-family=%s font-size="11.5" fill="%s">'
      'every step restartable, nothing lives only on my laptop</text>' % (W - PAD, F, INK_3))

    # dotted route between stages, with a bean rolling along it
    for i in range(len(STAGES) - 1):
        x1, x2 = bx(i) + BOX_W, bx(i + 1)
        y = BOX_Y + BOX_H / 2
        a('<path id="r%d" d="M%.1f %.1f H%.1f" stroke="%s" stroke-width="2.5" fill="none" '
          'stroke-linecap="round" stroke-dasharray="1 7" opacity=".45"/>'
          % (i, x1 + 3, y, x2 - 6, GLASS_FILL))
        a('<path d="M%.1f %.1f l-6 -4.5 v9 z" fill="%s"/>' % (x2 - 3, y, ACCENT_SOFT))
        a('<circle r="4" fill="%s"><animateMotion dur="2.2s" begin="%.2fs" '
          'repeatCount="indefinite" calcMode="linear">'
          '<mpath xlink:href="#r%d" href="#r%d"/></animateMotion>'
          '<animate attributeName="opacity" values="0;1;1;0" keyTimes="0;.18;.8;1" dur="2.2s" '
          'begin="%.2fs" repeatCount="indefinite"/></circle>'
          % (ACCENT, 0.3 * i, i, i, 0.3 * i))

    for i, (title, sub) in enumerate(STAGES):
        x = bx(i)
        a('<rect x="%.1f" y="%d" width="%d" height="%d" rx="16" fill="%s" '
          'fill-opacity="%.3f"/>' % (x, BOX_Y, BOX_W, BOX_H, GLASS_FILL, GLASS_OP))
        a('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" rx="15.5" fill="none" '
          'stroke="url(#edge_5)" stroke-width="1"/>'
          % (x + .5, BOX_Y + .5, BOX_W - 1, BOX_H - 1))
        a('<path d="M%.1f %.1f H%.1f" stroke="%s" stroke-opacity="%.2f" stroke-width="1"/>'
          % (x + 14, BOX_Y + 1.5, x + BOX_W - 14, GLASS_FILL, GLASS_HI))
        a('<circle cx="%.1f" cy="%d" r="13" fill="%s"/>' % (x + 30, BOX_Y + 30, RAMP[min(i, 4)]))
        a('<text x="%.1f" y="%d" text-anchor="middle" font-family=%s font-size="12" '
          'font-weight="700" fill="%s">%d</text>' % (x + 30, BOX_Y + 35, F, CREAM, i + 1))
        a('<text x="%.1f" y="%d" font-family=%s font-size="16" font-weight="700" fill="%s">'
          '%s</text>' % (x + 52, BOX_Y + 36, F, INK, title))
        # subtitle wraps to two lines so nothing overflows the 168px card
        words, line, lines = sub.split(), "", []
        for wd in words:
            probe = (line + " " + wd).strip()
            if len(probe) > 19 and line:
                lines.append(line)
                line = wd
            else:
                line = probe
        lines.append(line)
        for j, ln in enumerate(lines[:2]):
            a('<text x="%.1f" y="%d" font-family=%s font-size="11.5" fill="%s">%s</text>'
              % (x + 18, BOX_Y + 62 + j * 15, F, INK_3, ln))

    # the loop that makes it autonomous
    sx, ex = bx(4) + BOX_W / 2, bx(2) + BOX_W / 2
    ly = 258
    a('<path id="loop" d="M%.1f %d C%.1f %d %.1f %d %.1f %d" fill="none" stroke="%s" '
      'stroke-width="2.5" stroke-linecap="round" stroke-dasharray="1 7"/>'
      % (sx, BOX_Y + BOX_H, sx, ly, ex, ly, ex, BOX_Y + BOX_H, ACCENT_SOFT))
    a('<path d="M%.1f %d l-4.5 6 h9 z" fill="%s"/>' % (ex, BOX_Y + BOX_H + 2, ACCENT_SOFT))
    for k in range(2):
        a('<circle r="3.5" fill="%s"><animateMotion dur="3.4s" begin="%.2fs" '
          'repeatCount="indefinite" calcMode="linear">'
          '<mpath xlink:href="#loop" href="#loop"/></animateMotion></circle>'
          % (SAGE, -(3.4 * k / 2.0)))
    a('<text x="%.1f" y="%d" text-anchor="middle" font-family=%s font-size="12.5" fill="%s">'
      'the model picks what to simulate next, so i don’t have to</text>'
      % ((sx + ex) / 2, ly + 26, F, INK_2))
    a('<rect x=".5" y=".5" width="%.1f" height="%.1f" rx="15.5" fill="none" '
      'stroke="url(#edge_5)" stroke-width="1"/>' % (W - 1, H - 1))
    a('</svg>')
    return "".join(o)


if __name__ == "__main__":
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    dest = os.path.join(root, "assets", "pipeline.svg")
    svg = build()
    with open(dest, "w", encoding="ascii") as fh:
        fh.write(svg.encode("ascii", "xmlcharrefreplace").decode())
    print("wrote %s (%.1f KB)" % (dest, len(svg.encode()) / 1024.0))
