"""Render assets/hero.svg -- a lofi cafe scene.

Deliberately an illustration, not generative math art: flat warm shapes,
Arial, a window with afternoon light, a mug with rising steam. Type sits on
the left so nothing important is drawn over.

Same <img>-sandbox contract as every asset here: authored fully visible,
animation only ever overrides. Nothing disappears where SMIL does not run.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from palette import (ACCENT, ACCENT_SOFT, CARD, CARD_2, CREAM, EDGE, FONT,
                     INK, INK_2, INK_3, PAPER, RAMP, SAGE, SHADOW)

W, H = 1200, 380
F = '"%s"' % FONT


def build():
    o = []
    a = o.append
    a('<svg xmlns="http://www.w3.org/2000/svg" width="%d" height="%d" viewBox="0 0 %d %d" '
      'role="img" aria-label="Maximilien Tragarz Quintana, computational physics and '
      'scientific computing, illustrated as a cafe table by a sunny window">' % (W, H, W, H))

    a('<defs>')
    a('<linearGradient id="paper" x1="0" y1="0" x2="1" y2="1">'
      '<stop offset="0" stop-color="%s"/><stop offset="1" stop-color="%s"/></linearGradient>' % (CREAM, CARD))
    a('<linearGradient id="sky" x1="0" y1="0" x2="0" y2="1">'
      '<stop offset="0" stop-color="#F6DFB4"/><stop offset="1" stop-color="#EFC98E"/></linearGradient>')
    a('<linearGradient id="beam" x1="0" y1="0" x2="0" y2="1">'
      '<stop offset="0" stop-color="#F7DFAE" stop-opacity=".85"/>'
      '<stop offset="1" stop-color="#F7DFAE" stop-opacity="0"/></linearGradient>')
    a('<linearGradient id="mug" x1="0" y1="0" x2="1" y2="0">'
      '<stop offset="0" stop-color="%s"/><stop offset="1" stop-color="%s"/></linearGradient>' % (ACCENT, "#A8441F"))
    # paper grain, cheaper than thousands of dots
    a('<pattern id="grain" width="7" height="7" patternUnits="userSpaceOnUse">'
      '<circle cx="1" cy="1" r=".6" fill="%s" opacity=".22"/>'
      '<circle cx="4.5" cy="4.5" r=".5" fill="%s" opacity=".16"/></pattern>' % (SHADOW, EDGE))
    a('<clipPath id="win"><rect x="676" y="56" width="430" height="196" rx="10"/></clipPath>')
    a('<clipPath id="frame"><rect width="%d" height="%d" rx="18"/></clipPath>' % (W, H))
    a('</defs>')

    a('<g clip-path="url(#frame)">')
    a('<rect width="%d" height="%d" fill="url(#paper)"/>' % (W, H))
    a('<rect width="%d" height="%d" fill="url(#grain)"/>' % (W, H))

    # ---------------- window ------------------------------------------------
    a('<rect x="670" y="50" width="442" height="208" rx="14" fill="%s"/>' % SHADOW)
    a('<g clip-path="url(#win)">')
    a('<rect x="676" y="56" width="430" height="196" fill="url(#sky)"/>')
    a('<circle cx="1010" cy="116" r="30" fill="#F8E9C2"/>')           # low sun
    # rolling hills, back to front
    a('<path d="M676 200 q70-52 150-26 t130 14 q80-30 150 6 v58 H676 z" fill="%s" opacity=".42"/>' % SAGE)
    a('<path d="M676 222 q90-36 176-8 t150 18 q60-16 104 2 v18 H676 z" fill="%s" opacity=".58"/>' % SAGE)
    a('<path d="M676 240 q120-26 220 0 t210 4 v8 H676 z" fill="%s" opacity=".72"/>' % "#5F6F49")
    a('</g>')
    # muntins + frame
    a('<rect x="676" y="56" width="430" height="196" rx="10" fill="none" stroke="%s" stroke-width="7"/>' % CARD_2)
    a('<path d="M891 56 V252 M676 154 H1106" stroke="%s" stroke-width="6"/>' % CARD_2)
    a('<rect x="660" y="252" width="462" height="12" rx="5" fill="%s"/>' % EDGE)

    # light beams from the window, drifting
    for i, (x, w_, op, dur) in enumerate(((700, 58, .5, 11), (800, 42, .38, 14), (930, 66, .44, 13))):
        a('<g opacity="%.2f"><animate attributeName="opacity" values="%.2f;%.2f;%.2f" '
          'dur="%ds" repeatCount="indefinite"/>'
          '<path d="M%d 264 l%d 0 l%d 74 l%d 0 z" fill="url(#beam)"/></g>'
          % (op, op * .55, op, op * .55, dur, x, w_, 40, -40))

    # ---------------- table -------------------------------------------------
    a('<rect x="612" y="300" width="560" height="14" rx="7" fill="%s"/>' % "#B98C5A")
    a('<rect x="612" y="300" width="560" height="5" rx="2.5" fill="%s" opacity=".55"/>' % "#D3A874")

    # ---------------- books -------------------------------------------------
    for i, (bw, col) in enumerate(((104, RAMP[3]), (92, ACCENT), (110, RAMP[1]))):
        y = 300 - 14 * (i + 1)
        a('<rect x="%d" y="%d" width="%d" height="12" rx="3" fill="%s"/>' % (664 + i * 4, y, bw, col))
        a('<rect x="%d" y="%d" width="%d" height="3" rx="1.5" fill="%s" opacity=".45"/>'
          % (664 + i * 4 + 6, y + 4, bw - 12, CREAM))

    # ---------------- mug + steam -------------------------------------------
    mx, my = 872, 300
    a('<ellipse cx="%d" cy="%d" rx="52" ry="8" fill="%s" opacity=".55"/>' % (mx, my - 1, SHADOW))
    a('<path d="M%d %d h64 v30 a32 32 0 0 1-64 0 z" fill="url(#mug)"/>' % (mx - 32, my - 58))
    a('<path d="M%d %d a17 17 0 1 1 0 26" fill="none" stroke="%s" stroke-width="7" '
      'stroke-linecap="round"/>' % (mx + 34, my - 52, ACCENT))
    a('<ellipse cx="%d" cy="%d" rx="32" ry="8.5" fill="%s"/>' % (mx, my - 58, "#8A3A1A"))
    a('<ellipse cx="%d" cy="%d" rx="25" ry="6" fill="%s"/>' % (mx, my - 58, "#5B2A14"))
    # three steam ribbons
    for i, (dx, dur, op) in enumerate(((-15, 4.6, .5), (2, 5.4, .62), (17, 5.0, .44))):
        d = ("M%d %d c-9-13 9-20 0-33 c-8-12 7-19 1-30"
             % (mx + dx, my - 66))
        a('<path d="%s" fill="none" stroke="%s" stroke-width="4" stroke-linecap="round" '
          'opacity="%.2f"><animate attributeName="opacity" values="0;%.2f;0" dur="%.1fs" '
          'begin="%.1fs" repeatCount="indefinite"/>'
          '<animateTransform attributeName="transform" type="translate" values="0 6;0 -14" '
          'dur="%.1fs" begin="%.1fs" repeatCount="indefinite"/></path>'
          % (d, CREAM, op, op + .18, dur, i * .8, dur, i * .8))

    # ---------------- plant -------------------------------------------------
    px, py = 1024, 300
    a('<path d="M%d %d h56 l-8 40 h-40 z" fill="%s"/>' % (px - 28, py - 42, ACCENT_SOFT))
    a('<rect x="%d" y="%d" width="62" height="11" rx="4" fill="%s"/>' % (px - 31, py - 47, ACCENT))
    for ang, ln in ((-38, 44), (-13, 56), (14, 48), (36, 38)):
        a('<path d="M%d %d q%d %d %d %d" fill="none" stroke="%s" stroke-width="7" '
          'stroke-linecap="round"/>'
          % (px, py - 48, ang * 0.5, -ln * 0.6, ang * 0.9, -ln, SAGE))
        a('<ellipse cx="%d" cy="%d" rx="9" ry="13" fill="%s" transform="rotate(%d %d %d)"/>'
          % (px + ang * 0.9, py - 48 - ln, SAGE, ang, px + ang * 0.9, py - 48 - ln))

    # ---------------- dust motes -------------------------------------------
    for i, (dx, dy, r, dur) in enumerate(((742, 250, 2.4, 9), (820, 200, 1.9, 12), (960, 236, 2.6, 10),
                                          (700, 180, 1.7, 13), (1058, 190, 2.1, 11), (890, 150, 1.8, 14))):
        a('<circle cx="%d" cy="%d" r="%.1f" fill="%s" opacity=".55">'
          '<animateTransform attributeName="transform" type="translate" values="0 8;0 -18;0 8" '
          'dur="%ds" begin="%.1fs" repeatCount="indefinite"/>'
          '<animate attributeName="opacity" values=".2;.7;.2" dur="%ds" begin="%.1fs" '
          'repeatCount="indefinite"/></circle>' % (dx, dy, r, CREAM, dur, i * 1.3, dur, i * 1.3))

    # ---------------- type (left) -------------------------------------------
    a('<text x="74" y="126" font-family=%s font-size="52" font-weight="700" fill="%s">'
      'maximilien</text>' % (F, INK))
    a('<text x="74" y="184" font-family=%s font-size="52" font-weight="700" fill="%s">'
      'tragarz quintana</text>' % (F, INK))
    a('<rect x="76" y="204" width="86" height="5" rx="2.5" fill="%s"/>' % ACCENT)

    a('<text x="74" y="240" font-family=%s font-size="17" fill="%s">computational physics '
      '&#183; scientific computing &#183; sciml</text>' % (F, INK_2))
    a('<text x="74" y="266" font-family=%s font-size="15" fill="%s">i build pipelines that '
      'run themselves, and drink a lot of coffee doing it.</text>' % (F, INK_3))

    # little chips
    chips = (("engineering physics b.s.", 236), ("monterrey, mx", 196))
    x = 74
    for label, cw in chips:
        a('<rect x="%d" y="288" width="%d" height="30" rx="15" fill="%s" stroke="%s"/>'
          % (x, cw, CARD, EDGE))
        a('<text x="%d" y="308" font-family=%s font-size="13" fill="%s">%s</text>'
          % (x + 16, F, INK_2, label))
        x += cw + 10

    a('</g>')
    a('<rect x="1" y="1" width="%d" height="%d" rx="18" fill="none" stroke="%s" '
      'stroke-width="2"/>' % (W - 2, H - 2, EDGE))
    a('</svg>')
    return "".join(o)


if __name__ == "__main__":
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    dest = os.path.join(root, "assets", "hero.svg")
    svg = build()
    with open(dest, "w", encoding="ascii") as fh:
        fh.write(svg.encode("ascii", "xmlcharrefreplace").decode())
    print("wrote %s (%.1f KB)" % (dest, len(svg.encode()) / 1024.0))
