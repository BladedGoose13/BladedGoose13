"""A tiny pixel-art canvas that emits SVG.

Real pixel art, not a filter: every cell is one logical pixel, output is
snapped to integers and drawn with shape-rendering="crispEdges" so it stays
hard-edged at any zoom. Horizontal runs of one colour are merged into a
single <rect>, which is what keeps these files a few KB instead of
thousands of elements.

Animation is frame-based, the way a sprite sheet works: each frame is a
<g>, frame 0 is authored visible and the rest hidden, then SMIL cycles
them. A renderer that ignores SMIL simply shows frame 0 -- a correct
still, never a blank.
"""


# Ordered 4x4 Bayer thresholds. A pseudo-random dither reads as falling
# sand; an ordered one resolves into clean 50%/25% patterns, which is what
# makes stippled light look translucent rather than noisy.
BAYER4 = [[(v + 0.5) / 16.0 for v in row] for row in
          ([0, 8, 2, 10], [12, 4, 14, 6], [3, 11, 1, 9], [15, 7, 13, 5])]


def _rgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def mix(c1, c2, t):
    """Blend two hex colours. Used for lamp light, so a cone warms the wall,
    the desk and the book instead of covering them with a flat shape."""
    a, b = _rgb(c1), _rgb(c2)
    return "#%02X%02X%02X" % tuple(
        max(0, min(255, round(a[i] + (b[i] - a[i]) * t))) for i in range(3))


class Canvas:
    def __init__(self, w, h, bg=None):
        self.w, self.h = w, h
        self.px = [[bg for _ in range(w)] for _ in range(h)]

    def set(self, x, y, c):
        if c is not None and 0 <= x < self.w and 0 <= y < self.h:
            self.px[int(y)][int(x)] = c

    def rect(self, x, y, w, h, c):
        for yy in range(int(y), int(y + h)):
            for xx in range(int(x), int(x + w)):
                self.set(xx, yy, c)

    def frame(self, x, y, w, h, c):
        """Outline only."""
        self.hline(x, x + w - 1, y, c)
        self.hline(x, x + w - 1, y + h - 1, c)
        self.vline(x, y, y + h - 1, c)
        self.vline(x + w - 1, y, y + h - 1, c)

    def hline(self, x0, x1, y, c):
        for x in range(int(min(x0, x1)), int(max(x0, x1)) + 1):
            self.set(x, y, c)

    def vline(self, x, y0, y1, c):
        for y in range(int(min(y0, y1)), int(max(y0, y1)) + 1):
            self.set(x, y, c)

    def line(self, x0, y0, x1, y1, c):
        """Bresenham -- diagonals must stay pixel-exact, not anti-aliased."""
        x0, y0, x1, y1 = int(x0), int(y0), int(x1), int(y1)
        dx, dy = abs(x1 - x0), -abs(y1 - y0)
        sx, sy = (1 if x0 < x1 else -1), (1 if y0 < y1 else -1)
        err = dx + dy
        while True:
            self.set(x0, y0, c)
            if x0 == x1 and y0 == y1:
                break
            e2 = 2 * err
            if e2 >= dy:
                err += dy
                x0 += sx
            if e2 <= dx:
                err += dx
                y0 += sy

    def disc(self, cx, cy, r, c):
        for yy in range(int(cy - r), int(cy + r) + 1):
            for xx in range(int(cx - r), int(cx + r) + 1):
                if (xx - cx) ** 2 + (yy - cy) ** 2 <= r * r + 0.25:
                    self.set(xx, yy, c)

    def ring(self, cx, cy, r, c):
        for yy in range(int(cy - r), int(cy + r) + 1):
            for xx in range(int(cx - r), int(cx + r) + 1):
                d = (xx - cx) ** 2 + (yy - cy) ** 2
                if (r - 0.9) ** 2 <= d <= (r + 0.4) ** 2:
                    self.set(xx, yy, c)

    def tint(self, x, y, toward, amt):
        """Shift one existing pixel toward a colour. No-op on empty cells."""
        if not (0 <= x < self.w and 0 <= y < self.h):
            return
        cur = self.px[int(y)][int(x)]
        if cur is not None:
            self.px[int(y)][int(x)] = mix(cur, toward, amt)

    def cone(self, x, y, length, spread, toward, strength=0.55, bands=5):
        """A lamp cone: tints a widening wedge, fading with distance.

        The blend amount is quantised into `bands` discrete steps. That is
        how hand-drawn pixel art shades light -- in visible bands, not a
        smooth gradient -- and it also lets neighbouring cells share a
        colour so they merge into one <rect> instead of one rect per pixel.
        """
        for i in range(length):
            half = 1 + int(i * spread)
            amt = strength * (1.0 - i / float(length)) ** 1.25
            for xx in range(x - half, x + half + 1):
                edge = 1.0 - 0.45 * (abs(xx - x) / float(half + 1))
                q = round(amt * edge * bands) / float(bands)
                if q > 0.001:
                    self.tint(xx, y + i, toward, q)

    def glow(self, cx, cy, r, toward, strength=0.7, bands=4):
        """A radial warm-up around a light source, in discrete bands."""
        for yy in range(int(cy - r), int(cy + r) + 1):
            for xx in range(int(cx - r), int(cx + r) + 1):
                d = ((xx - cx) ** 2 + (yy - cy) ** 2) ** 0.5
                if d > r:
                    continue
                q = round(strength * (1 - d / r) ** 1.5 * bands) / float(bands)
                if q > 0.001:
                    self.tint(xx, yy, toward, q)

    def beam(self, x, y, length, spread, near, far, density=1.0):
        """A dithered light shaft.

        Interpolating a dark wall toward a warm bulb colour lands on khaki --
        the channels average out and the light reads as mud. Hand-drawn pixel
        art instead *stipples* the light colour itself over the surface and
        lets density carry the falloff, which is what this does: an ordered
        dither whose threshold drops with distance, in two warm steps.
        """
        for i in range(length):
            half = 1 + int(i * spread)
            t = (1.0 - i / float(length)) ** 0.8
            for xx in range(x - half, x + half + 1):
                edge = 1.0 - (abs(xx - x) / float(half + 1)) ** 1.6
                amt = t * edge * density
                if amt <= BAYER4[(y + i) % 4][xx % 4]:
                    continue
                self.set(xx, y + i, near if amt > 0.62 else far)

    def blit(self, x, y, rows, key):
        """Stamp an ASCII sprite. ' ' and '.' are transparent."""
        for j, row in enumerate(rows):
            for i, chx in enumerate(row):
                if chx in (" ", "."):
                    continue
                self.set(x + i, y + j, key.get(chx))

    def runs(self):
        """Merge horizontal runs of equal colour -> far fewer rects."""
        out = []
        for y in range(self.h):
            x = 0
            row = self.px[y]
            while x < self.w:
                c = row[x]
                if c is None:
                    x += 1
                    continue
                x2 = x
                while x2 + 1 < self.w and row[x2 + 1] == c:
                    x2 += 1
                out.append((x, y, x2 - x + 1, c))
                x = x2 + 1
        return out

    def svg_body(self, scale=1, ox=0, oy=0):
        parts = []
        for (x, y, w, c) in self.runs():
            parts.append('<rect x="%d" y="%d" width="%d" height="%d" fill="%s"/>'
                         % (ox + x * scale, oy + y * scale, w * scale, scale, c))
        return "".join(parts)


def _split(frames):
    """Split frames into (shared base, per-frame diff canvases).

    Neighbouring frames of these scenes differ only in steam, LEDs, stars and
    a sweep line -- a few hundred cells out of ~4000. Emitting the agreed
    pixels once and only the disagreements per frame cuts the files by an
    order of magnitude, with identical output.
    """
    w, h = frames[0].w, frames[0].h
    base = Canvas(w, h)
    diffs = [Canvas(w, h) for _ in frames]
    for y in range(h):
        for x in range(w):
            vals = [f.px[y][x] for f in frames]
            if all(v == vals[0] for v in vals):
                base.px[y][x] = vals[0]
            else:
                for k, f in enumerate(frames):
                    diffs[k].px[y][x] = f.px[y][x]
    return base, diffs


def sprite_svg(frames, scale, fps=6, title="", desc="", bg=None, pad=0):
    """Wrap frame canvases into one animated SVG.

    Frame 0 carries opacity="1"; the others start hidden and SMIL swaps
    them. Without SMIL the viewer sees frame 0, which is a valid still.
    """
    w = frames[0].w * scale + pad * 2
    h = frames[0].h * scale + pad * 2
    n = len(frames)
    dur = n / float(fps)
    o = ['<svg xmlns="http://www.w3.org/2000/svg" width="%d" height="%d" viewBox="0 0 %d %d" '
         'shape-rendering="crispEdges" role="img" aria-label="%s">' % (w, h, w, h, desc or title)]
    if bg:
        o.append('<rect width="%d" height="%d" fill="%s"/>' % (w, h, bg))
    base, diffs = _split(frames)
    o.append(base.svg_body(scale, pad, pad))
    for i, fr in enumerate(diffs):
        vis = "1" if i == 0 else "0"
        o.append('<g opacity="%s">' % vis)
        if n > 1:
            # keyTimes hold each frame for exactly one slot, then cut.
            kt = ";".join("%.4f" % (k / float(n)) for k in range(n)) + ";1"
            vals = ";".join("1" if k == i else "0" for k in range(n)) + \
                   (";1" if i == 0 else ";0")
            o.append('<animate attributeName="opacity" values="%s" keyTimes="%s" '
                     'calcMode="discrete" dur="%.3fs" repeatCount="indefinite"/>' % (vals, kt, dur))
        o.append(fr.svg_body(scale, pad, pad))
        o.append('</g>')
    o.append('</svg>')
    return "".join(o)
