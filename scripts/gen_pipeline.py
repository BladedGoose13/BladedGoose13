"""Render assets/pipeline.svg -- an animated view of the pipeline shape.

Same <img>-sandbox contract as the hero: every element is authored visible,
animation only enhances. Packets are advected along the connector paths with
<animateMotion>, and an activation wave walks the stages in sequence so the
diagram reads as a running system rather than a static box-and-arrow chart.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from palette import (AMBER, BG0, BG1, BG2, CREAM, LINE, MONO, MUTED, SAND,
                     SANS, ramp)

W, H = 1200, 320
STAGES = [
    # Subtitles are capped at ~24 glyphs: the box interior is 136px and the
    # mono face runs ~4.8px/glyph at 8px, so anything longer overflows.
    ("01", "INGEST", "instruments &#183; archives"),
    ("02", "VALIDATE", "schema &#183; units &#183; bounds"),
    ("03", "SIMULATE", "DFT/QE &#183; Slurm &#183; CUDA"),
    ("04", "REDUCE", "features &#183; descriptors"),
    ("05", "LEARN", "SciML surrogate &#183; UQ"),
    ("06", "SERVE", "API &#183; dashboards"),
]

BOX_W, BOX_H, BOX_Y = 168, 82, 104
PAD = 34
GAP = (W - 2 * PAD - len(STAGES) * BOX_W) / (len(STAGES) - 1)


def bx(i):
    return PAD + i * (BOX_W + GAP)


def build():
    o = []
    a = o.append
    a('<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" '
      'width="%d" height="%d" viewBox="0 0 %d %d" role="img" '
      'aria-label="Autonomous research pipeline: ingest, validate, simulate, reduce, '
      'learn, serve, with an active-learning feedback loop">' % (W, H, W, H))

    a('<defs>')
    a('<linearGradient id="pbg" x1="0" y1="0" x2="1" y2="1">'
      '<stop offset="0" stop-color="%s"/><stop offset="1" stop-color="%s"/></linearGradient>' % (BG1, BG0))
    a('<linearGradient id="box" x1="0" y1="0" x2="0" y2="1">'
      '<stop offset="0" stop-color="%s"/><stop offset="1" stop-color="%s"/></linearGradient>' % (BG2, BG1))
    a('<pattern id="plat" width="26" height="26" patternUnits="userSpaceOnUse">'
      '<circle cx="1" cy="1" r="1" fill="%s" opacity=".35"/></pattern>' % LINE)
    a('<marker id="ah" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" '
      'orient="auto-start-reverse"><path d="M0 0 L10 5 L0 10 z" fill="%s"/></marker>' % ramp(0.55))
    a('<clipPath id="pclip"><rect width="%d" height="%d" rx="14"/></clipPath>' % (W, H))
    a('</defs>')

    a('<g clip-path="url(#pclip)">')
    a('<rect width="%d" height="%d" fill="url(#pbg)"/>' % (W, H))
    a('<rect width="%d" height="%d" fill="url(#plat)"/>' % (W, H))

    # ---- header ----------------------------------------------------------
    a('<text x="%d" y="44" font-family=%s font-size="13" font-weight="700" fill="%s" '
      'letter-spacing="3.6">AUTONOMOUS RESEARCH PIPELINE</text>' % (PAD, '"%s"' % SANS, CREAM))
    a('<text x="%d" y="44" text-anchor="end" font-family=%s font-size="9.5" fill="%s" '
      'letter-spacing="1.2">every stage idempotent, versioned and restartable</text>'
      % (W - PAD, '"%s"' % MONO, MUTED))
    a('<path d="M%d 60 H%d" stroke="%s" stroke-width="1"/>' % (PAD, W - PAD, LINE))

    # ---- connectors (drawn under the boxes) -------------------------------
    for i in range(len(STAGES) - 1):
        x1 = bx(i) + BOX_W
        x2 = bx(i + 1)
        y = BOX_Y + BOX_H / 2
        a('<path id="c%d" d="M%.1f %.1f H%.1f" stroke="%s" stroke-width="1.4" fill="none" '
          'marker-end="url(#ah)"/>' % (i, x1, y, x2, ramp(0.42)))

    # ---- stage boxes ------------------------------------------------------
    for i, (num, title, sub) in enumerate(STAGES):
        x = bx(i)
        col = ramp(0.30 + 0.12 * i)
        a('<g opacity="1"><animate attributeName="opacity" values="0;1" dur=".5s" '
          'begin="%.2fs" fill="freeze"/>' % (0.12 * i))
        # activation wave: the stroke brightens as the wave reaches this stage
        a('<rect x="%.1f" y="%d" width="%d" height="%d" rx="11" fill="url(#box)" '
          'stroke="%s" stroke-width="1.2">'
          '<animate attributeName="stroke" values="%s;%s;%s" keyTimes="0;.12;1" dur="5.4s" '
          'begin="%.2fs" repeatCount="indefinite"/></rect>'
          % (x, BOX_Y, BOX_W, BOX_H, LINE, LINE, AMBER, LINE, 0.55 * i))
        a('<text x="%.1f" y="%d" font-family=%s font-size="9" fill="%s" letter-spacing="1.4">'
          '%s</text>' % (x + 16, BOX_Y + 24, '"%s"' % MONO, col, num))
        a('<text x="%.1f" y="%d" font-family=%s font-size="14.5" font-weight="700" fill="%s" '
          'letter-spacing="1.6">%s</text>' % (x + 16, BOX_Y + 47, '"%s"' % SANS, CREAM, title))
        a('<text x="%.1f" y="%d" font-family=%s font-size="8" fill="%s">%s</text>'
          % (x + 16, BOX_Y + 64, '"%s"' % MONO, MUTED, sub))
        # throughput ticker along the box foot
        a('<rect x="%.1f" y="%d" width="%d" height="2.5" rx="1.25" fill="%s" opacity=".30"/>'
          % (x + 16, BOX_Y + BOX_H - 12, BOX_W - 32, col))
        a('<rect x="%.1f" y="%d" width="34" height="2.5" rx="1.25" fill="%s">'
          '<animate attributeName="x" values="%.1f;%.1f" dur="2.8s" begin="%.2fs" '
          'repeatCount="indefinite"/></rect>'
          % (x + 16, BOX_Y + BOX_H - 12, col, x + 16, x + BOX_W - 50, 0.33 * i))
        a('</g>')

    # ---- packets in flight ------------------------------------------------
    for i in range(len(STAGES) - 1):
        for k in range(2):
            dur = 1.9
            begin = -(dur * (k * 0.5)) + 0.28 * i
            a('<g><rect x="-3" y="-2" width="6" height="4" rx="1.6" fill="%s">'
              '<animateMotion dur="%.2fs" begin="%.2fs" repeatCount="indefinite" '
              'calcMode="linear"><mpath xlink:href="#c%d" href="#c%d"/></animateMotion>'
              '<animate attributeName="opacity" values="0;1;1;0" keyTimes="0;.15;.8;1" '
              'dur="%.2fs" begin="%.2fs" repeatCount="indefinite"/></rect></g>'
              % (CREAM if k == 0 else AMBER, dur, begin, i, i, dur, begin))

    # ---- active-learning feedback loop ------------------------------------
    sx = bx(4) + BOX_W / 2
    ex = bx(2) + BOX_W / 2
    loop_y = 252
    d = ("M%.1f %d C%.1f %d %.1f %d %.1f %d"
         % (sx, BOX_Y + BOX_H, sx, loop_y, ex, loop_y, ex, BOX_Y + BOX_H))
    a('<path id="loop" d="%s" fill="none" stroke="%s" stroke-width="1.4" '
      'stroke-dasharray="6 5" marker-end="url(#ah)"/>' % (d, ramp(0.48)))
    for k in range(3):
        a('<circle r="2.6" fill="%s"><animateMotion dur="3.6s" begin="%.2fs" '
          'repeatCount="indefinite" calcMode="linear">'
          '<mpath xlink:href="#loop" href="#loop"/></animateMotion></circle>'
          % (SAND, -(3.6 * k / 3.0)))
    a('<text x="%.1f" y="%d" text-anchor="middle" font-family=%s font-size="9.5" fill="%s" '
      'letter-spacing="1.6">active learning &#183; the model chooses the next simulation</text>'
      % ((sx + ex) / 2, loop_y + 22, '"%s"' % MONO, SAND))

    # ---- base rail --------------------------------------------------------
    a('<path d="M%d %d H%d" stroke="%s" stroke-width="1"/>' % (PAD, H - 34, W - PAD, LINE))
    rail = ("provenance", "reproducibility", "CI &#183; tests", "containerised", "resumable")
    for i, label in enumerate(rail):
        x = PAD + i * ((W - 2 * PAD) / len(rail))
        a('<circle cx="%.1f" cy="%d" r="2.4" fill="%s"/>' % (x + 4, H - 17, ramp(0.35 + 0.1 * i)))
        a('<text x="%.1f" y="%d" font-family=%s font-size="8.5" fill="%s" letter-spacing="1">'
          '%s</text>' % (x + 14, H - 14, '"%s"' % MONO, MUTED, label))
    a('</g>')
    a('<rect x=".75" y=".75" width="%.1f" height="%.1f" rx="14" fill="none" stroke="%s" '
      'stroke-width="1.5"/>' % (W - 1.5, H - 1.5, ramp(0.28)))
    a('</svg>')
    return "".join(o)


if __name__ == "__main__":
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    dest = os.path.join(root, "assets", "pipeline.svg")
    svg = build()
    with open(dest, "w", encoding="utf-8") as fh:
        fh.write(svg)
    print("wrote %s (%.1f KB)" % (dest, len(svg.encode()) / 1024.0))
