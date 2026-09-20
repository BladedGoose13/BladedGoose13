"""Render assets/hero.svg.

The banner background is not decorative noise: it is the streamline portrait of
a real planar flow -- a superposition of point vortices in a uniform stream,

    w(z) = U + sum_k  Gamma_k / (2*pi*i*(z - z_k)),      u - iv = w(z)

integrated with fixed-step RK4 from a seed grid. The separatrices, stagnation
points and the vortex-street structure you can see are the actual solution, so
the artwork is a (small) piece of computational physics in its own right.

Animated particles are advected along those same integral curves via SMIL
<animateMotion>, which renders inside GitHub's <img> sandbox.
"""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from palette import (AMBER, BG0, BG1, CREAM, LINE, MONO, MUTED, SAND, SANS, ramp)

W, H = 1200, 340
ASPECT = W / H

# --- flow definition -------------------------------------------------------
U = 0.42                       # uniform stream speed, +x
VORTICES = [                   # (x, y, circulation)
    (0.30, 0.28, -0.55),
    (0.62, 0.66, +1.05),
    (1.30, 0.30, -0.95),
    (2.02, 0.72, +0.88),
    (2.80, 0.34, -1.00),
    (3.30, 0.74, +0.62),
]
CORE = 0.055                   # Rankine core radius; desingularises the centre


def velocity(x, y):
    """Return (u, v) of the vortex-in-uniform-stream field at (x, y)."""
    u, v = U, 0.0
    for (vx, vy, g) in VORTICES:
        dx, dy = x - vx, y - vy
        r2 = dx * dx + dy * dy
        if r2 < CORE * CORE:            # solid-body rotation inside the core
            r2 = CORE * CORE
        k = g / (2.0 * math.pi * r2)
        u += -k * dy
        v += k * dx
    return u, v


def rk4_step(x, y, h):
    k1u, k1v = velocity(x, y)
    k2u, k2v = velocity(x + 0.5 * h * k1u, y + 0.5 * h * k1v)
    k3u, k3v = velocity(x + 0.5 * h * k2u, y + 0.5 * h * k2v)
    k4u, k4v = velocity(x + h * k3u, y + h * k3v)
    return (x + h * (k1u + 2 * k2u + 2 * k3u + k4u) / 6.0,
            y + h * (k1v + 2 * k2v + 2 * k3v + k4v) / 6.0)


def streamline(x0, y0, h, n=340):
    """Integrate one integral curve, stopping when it leaves the frame."""
    pts, x, y = [(x0, y0)], x0, y0
    for _ in range(n):
        x, y = rk4_step(x, y, h)
        if not (-0.35 <= x <= ASPECT + 0.35 and -0.35 <= y <= 1.35):
            break
        sp = math.hypot(*velocity(x, y))
        if sp < 1e-4 or sp > 60:        # stagnation / near-singular: stop
            break
        pts.append((x, y))
    return pts


def to_px(pts):
    return [(p[0] / ASPECT * W, (1.0 - p[1]) * H) for p in pts]


def resample(px, spacing=20.0):
    """Arc-length resampling: the dominant lever on output file size.

    Streamlines come out of RK4 with ~340 densely spaced points each; emitting
    those verbatim produced a 1.3 MB banner. Resampling to a fixed arc-length
    spacing and smoothing on playback keeps the curve visually identical at a
    fraction of the bytes.
    """
    if len(px) < 3:
        return px
    out, carry = [px[0]], 0.0
    for i in range(len(px) - 1):
        (x0, y0), (x1, y1) = px[i], px[i + 1]
        seg = math.hypot(x1 - x0, y1 - y0)
        if seg < 1e-9:
            continue
        t = spacing - carry
        while t <= seg:
            out.append((x0 + (x1 - x0) * t / seg, y0 + (y1 - y0) * t / seg))
            t += spacing
        carry = (carry + seg) % spacing
    if math.hypot(out[-1][0] - px[-1][0], out[-1][1] - px[-1][1]) > spacing * 0.35:
        out.append(px[-1])
    return out


def path_d(px):
    """Midpoint-quadratic smoothing: M m0, then Q p_i mid(p_i, p_i+1).

    Chaining through segment midpoints is C1 by construction, so it cannot
    overshoot the way a reflected T-chain does, and costs 2 integer pairs per
    point instead of the 3 a Catmull-Rom cubic needs.
    """
    if len(px) < 2:
        return ""
    if len(px) == 2:
        return "M%d,%d L%d,%d" % (px[0][0], px[0][1], px[1][0], px[1][1])
    d = "M%d,%d" % (round(px[0][0]), round(px[0][1]))
    for i in range(1, len(px) - 1):
        mx = (px[i][0] + px[i + 1][0]) / 2.0
        my = (px[i][1] + px[i + 1][1]) / 2.0
        d += "Q%d,%d %d,%d" % (round(px[i][0]), round(px[i][1]), round(mx), round(my))
    d += "L%d,%d" % (round(px[-1][0]), round(px[-1][1]))
    return d


def arclength(px):
    return sum(math.hypot(px[i + 1][0] - px[i][0], px[i + 1][1] - px[i][1])
               for i in range(len(px) - 1))


def build():
    """Assemble the SVG.

    Hard constraint: GitHub embeds README images in an <img> sandbox, and some
    renderers there never advance the SMIL timeline. Anything whose *static*
    attribute value is opacity="0" would then stay invisible forever. So every
    element is authored fully visible and each <animate> merely overrides it
    when a timeline does run -- animation enhances, it never reveals.
    """
    # --- seed and integrate ------------------------------------------------
    curves = []
    rows, cols = 15, 9
    for i in range(cols):
        for j in range(rows):
            x0 = -0.28 + i * (ASPECT + 0.5) / (cols - 1)
            y0 = 0.02 + j * 0.96 / (rows - 1)
            y0 += 0.022 * math.sin(i * 2.1)          # break up grid regularity
            pts = streamline(x0, y0, 0.016)
            back = streamline(x0, y0, -0.016, n=150)
            pts = list(reversed(back[1:])) + pts
            px = to_px(pts)
            if len(px) > 14 and arclength(px) > 200:
                curves.append(resample(px, 26.0))

    curves.sort(key=arclength, reverse=True)
    curves = curves[:80]

    out = []
    a = out.append
    a('<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" '
      'width="%d" height="%d" viewBox="0 0 %d %d" role="img" '
      'aria-label="Maximilien Tragarz Quintana - computational physics, scientific '
      'computing, quantitative research">' % (W, H, W, H))

    # --- defs --------------------------------------------------------------
    a('<defs>')
    a('<linearGradient id="bg" x1="0" y1="0" x2="1" y2="1">'
      '<stop offset="0" stop-color="%s"/><stop offset=".55" stop-color="%s"/>'
      '<stop offset="1" stop-color="%s"/></linearGradient>' % (BG0, BG1, BG0))
    a('<radialGradient id="halo" cx=".5" cy=".5" r=".62">'
      '<stop offset="0" stop-color="%s" stop-opacity=".40"/>'
      '<stop offset="1" stop-color="%s" stop-opacity="0"/></radialGradient>' % (ramp(0.35), BG0))
    a('<linearGradient id="scrim" x1="0" y1="0" x2="0" y2="1">'
      '<stop offset="0" stop-color="%s" stop-opacity="0"/>'
      '<stop offset=".34" stop-color="%s" stop-opacity=".74"/>'
      '<stop offset=".66" stop-color="%s" stop-opacity=".74"/>'
      '<stop offset="1" stop-color="%s" stop-opacity="0"/></linearGradient>'
      % (BG0, BG0, BG0, BG0))
    a('<linearGradient id="sweep" x1="0" y1="0" x2="1" y2="0">'
      '<stop offset="0" stop-color="%s" stop-opacity="0"/>'
      '<stop offset=".5" stop-color="%s" stop-opacity=".95"/>'
      '<stop offset="1" stop-color="%s" stop-opacity="0"/></linearGradient>' % (AMBER, AMBER, AMBER))
    a('<linearGradient id="rule" x1="0" y1="0" x2="1" y2="0">'
      '<stop offset="0" stop-color="%s" stop-opacity="0"/>'
      '<stop offset=".22" stop-color="%s"/><stop offset=".78" stop-color="%s"/>'
      '<stop offset="1" stop-color="%s" stop-opacity="0"/></linearGradient>'
      % (AMBER, AMBER, ramp(0.2), ramp(0.2)))
    a('<filter id="glow" x="-300%" y="-300%" width="700%" height="700%">'
      '<feGaussianBlur stdDeviation="2.4" result="b"/>'
      '<feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>')
    a('<pattern id="lattice" width="30" height="30" patternUnits="userSpaceOnUse">'
      '<circle cx="1" cy="1" r="1" fill="%s" opacity=".30"/></pattern>' % LINE)
    a('<clipPath id="frame"><rect x="0" y="0" width="%d" height="%d" rx="14"/></clipPath>' % (W, H))

    title = "MAXIMILIEN TRAGARZ QUINTANA"
    a('<mask id="titlemask"><rect width="%d" height="%d" fill="#000"/>'
      '<text x="%d" y="171" text-anchor="middle" font-family=%s font-size="44" '
      'font-weight="700" letter-spacing="5.5" fill="#fff">%s</text></mask>'
      % (W, H, W // 2, '"%s"' % SANS, title))
    a('</defs>')

    a('<g clip-path="url(#frame)">')
    a('<rect width="%d" height="%d" fill="url(#bg)"/>' % (W, H))
    a('<rect width="%d" height="%d" fill="url(#halo)"/>' % (W, H))

    # --- dot lattice -------------------------------------------------------
    a('<rect width="%d" height="%d" fill="url(#lattice)"/>' % (W, H))

    # --- streamlines -------------------------------------------------------
    a('<g fill="none" stroke-linecap="round">')
    motion_paths = []
    for idx, px in enumerate(curves):
        t = (H - px[len(px) // 2][1]) / H            # colour by mean height
        col = ramp(0.18 + 0.72 * t)
        L = arclength(px)
        op = 0.13 + 0.26 * min(1.0, L / 900.0)
        sw = 0.9 + 0.75 * min(1.0, L / 1100.0)
        pid = ""
        if L > 520 and len(motion_paths) < 22 and idx % 3 == 0:
            pid = ' id="s%d"' % idx
            motion_paths.append((idx, L))
        a('<path%s d="%s" stroke="%s" stroke-width="%.2f" opacity="%.3f"/>'
          % (pid, path_d(px), col, sw, op))
    a('</g>')

    # --- advected tracer particles ----------------------------------------
    a('<g filter="url(#glow)">')
    for n, (idx, L) in enumerate(motion_paths):
        dur = max(7.0, min(20.0, L / 62.0))
        begin = -(dur * ((n * 0.37) % 1.0))
        r = 2.0 + 1.1 * ((n * 7) % 3) / 2.0
        col = CREAM if n % 4 == 0 else (AMBER if n % 4 == 1 else SAND)
        a('<circle r="%.1f" fill="%s">'
          '<animateMotion dur="%.2fs" begin="%.2fs" repeatCount="indefinite" '
          'rotate="auto" calcMode="linear">'
          '<mpath xlink:href="#s%d" href="#s%d"/></animateMotion>'
          '<animate attributeName="opacity" values="0;.95;.95;0" keyTimes="0;.08;.86;1" '
          'dur="%.2fs" begin="%.2fs" repeatCount="indefinite"/></circle>'
          % (r, col, dur, begin, idx, idx, dur, begin))
    a('</g>')

    # --- text block --------------------------------------------------------
    a('<rect width="%d" height="%d" fill="url(#scrim)"/>' % (W, H))

    a('<g opacity="1"><animate attributeName="opacity" values="0;1" dur=".9s" '
      'begin=".15s" fill="freeze"/>'
      '<text x="%d" y="96" text-anchor="middle" font-family=%s font-size="12.5" '
      'letter-spacing="7.2" fill="%s">C O M P U T A T I O N A L &#160; P H Y S I C S</text></g>'
      % (W // 2, '"%s"' % MONO, AMBER))

    a('<g opacity="1" transform="translate(0,0)">'
      '<animate attributeName="opacity" values="0;1" dur="1.0s" begin=".35s" fill="freeze"/>'
      '<animateTransform attributeName="transform" type="translate" from="0 10" to="0 0" '
      'dur="1.0s" begin=".35s" fill="freeze" calcMode="spline" keySplines=".2 .8 .2 1"/>'
      '<text x="%d" y="171" text-anchor="middle" font-family=%s font-size="44" '
      'font-weight="700" letter-spacing="5.5" fill="%s">%s</text></g>'
      % (W // 2, '"%s"' % SANS, CREAM, title))

    # specular sweep across the wordmark
    a('<g mask="url(#titlemask)"><rect x="-420" y="0" width="420" height="%d" fill="url(#sweep)">'
      '<animate attributeName="x" values="-420;%d" dur="4.5s" begin="2.2s" '
      'repeatCount="indefinite"/></rect></g>' % (H, W + 60))

    a('<g opacity="1"><animate attributeName="opacity" values="0;1" dur="1s" begin=".75s" fill="freeze"/>'
      '<path d="M330 196 H870" stroke="url(#rule)" stroke-width="1.4" '
      'stroke-dasharray="540" stroke-dashoffset="0">'
      '<animate attributeName="stroke-dashoffset" values="540;0" dur="1.3s" begin=".75s" '
      'fill="freeze" calcMode="spline" keySplines=".25 .9 .2 1"/></path></g>')

    a('<g opacity="1"><animate attributeName="opacity" values="0;1" dur="1s" begin="1.0s" fill="freeze"/>'
      '<text x="%d" y="232" text-anchor="middle" font-family=%s font-size="14.5" '
      'letter-spacing="2.4" fill="%s">scientific computing &#183; SciML &#183; '
      'quantitative research &#183; autonomous pipelines</text></g>'
      % (W // 2, '"%s"' % SANS, SAND))

    a('<g opacity="1"><animate attributeName="opacity" values="0;1" dur="1s" begin="1.25s" fill="freeze"/>'
      '<text x="%d" y="262" text-anchor="middle" font-family=%s font-size="11.5" '
      'letter-spacing="1.6" fill="%s">Engineering Physics B.S. &#183; Tecnol&#243;gico de '
      'Monterrey &#183; Monterrey, MX</text></g>' % (W // 2, '"%s"' % MONO, MUTED))

    # --- instrument chrome -------------------------------------------------
    a('<g stroke="%s" stroke-width="1.2" fill="none" opacity=".75">' % ramp(0.45))
    for (cx, cy, sx, sy) in ((22, 22, 1, 1), (W - 22, 22, -1, 1),
                             (22, H - 22, 1, -1), (W - 22, H - 22, -1, -1)):
        a('<path d="M%d %d h%d M%d %d v%d"/>' % (cx, cy, 20 * sx, cx, cy, 20 * sy))
    a('</g>')

    a('<text x="26" y="%d" font-family=%s font-size="9.5" fill="%s" opacity=".55">'
      '&#968;(z) = &#8721;&#8342; &#915;&#8342;/2&#960; &#183; ln|z &#8722; z&#8342;| + U&#183;y '
      '&#8212; RK4, h=0.016</text>' % (H - 16, '"%s"' % MONO, MUTED))
    a('<text x="%d" y="%d" text-anchor="end" font-family=%s font-size="9.5" fill="%s" '
      'opacity=".72">%d integral curves &#183; %d tracers</text>'
      % (W - 26, H - 16, '"%s"' % MONO, MUTED, len(curves), len(motion_paths)))
    a('</g>')
    a('<rect x=".75" y=".75" width="%.1f" height="%.1f" rx="14" fill="none" stroke="%s" '
      'stroke-width="1.5"/>' % (W - 1.5, H - 1.5, ramp(0.30)))
    a('</svg>')
    return "".join(out)


if __name__ == "__main__":
    here = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    dest = os.path.join(here, "assets", "hero.svg")
    svg = build()
    with open(dest, "w", encoding="utf-8") as fh:
        fh.write(svg)
    print("wrote %s (%.1f KB)" % (dest, len(svg.encode()) / 1024.0))
