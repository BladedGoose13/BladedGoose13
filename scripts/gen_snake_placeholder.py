"""Write assets/snake.svg as a warm placeholder.

The snake workflow overwrites this on its first run; it exists so the README
never shows a broken image in the window between merging and that run.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from palette import ACCENT, EMPTY, FONT, GLASS_FILL, GLASS_OP, INK_3, RAMP, backdrop

W, H = 900, 220
CELL, GAP = 11, 3
COLS, ROWS = 53, 7
F = '"%s"' % FONT


def build():
    gw, gh = COLS * (CELL + GAP) - GAP, ROWS * (CELL + GAP) - GAP
    ox, oy = (W - gw) / 2, (H - gh) / 2 - 10
    o = ['<svg xmlns="http://www.w3.org/2000/svg" width="%d" height="%d" viewBox="0 0 %d %d" '
         'role="img" aria-label="Contribution snake, drawn on the first scheduled run">'
         % (W, H, W, H)]
    o.append(backdrop(W, H, seed=6))
    o.append('<rect x="14" y="14" width="%d" height="%d" rx="14" fill="%s" '
             'fill-opacity="%.3f"/>' % (W - 28, H - 28, GLASS_FILL, GLASS_OP))
    o.append('<rect x="14.5" y="14.5" width="%.1f" height="%.1f" rx="13.5" fill="none" '
             'stroke="url(#edge_6)" stroke-width="1"/>' % (W - 29, H - 29))
    for c in range(COLS):
        for r in range(ROWS):
            o.append('<rect x="%.1f" y="%.1f" width="%d" height="%d" rx="2.5" fill="%s"/>'
                     % (ox + c * (CELL + GAP), oy + r * (CELL + GAP), CELL, CELL, EMPTY))
    for i, (c, r) in enumerate([(9, 3), (10, 3), (11, 3), (12, 3), (13, 3)]):
        o.append('<rect x="%.1f" y="%.1f" width="%d" height="%d" rx="2.5" fill="%s"/>'
                 % (ox + c * (CELL + GAP), oy + r * (CELL + GAP), CELL, CELL,
                    RAMP[min(4 - i, 4)] if i < 4 else ACCENT))
    o.append('<text x="%d" y="%d" text-anchor="middle" font-family=%s font-size="12.5" '
             'fill="%s">the snake eats my contribution grid here, once the workflow first '
             'runs</text>' % (W // 2, H - 34, F, INK_3))
    o.append('</svg>')
    return "".join(o)


if __name__ == "__main__":
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    dest = os.path.join(root, "assets", "snake.svg")
    svg = build()
    with open(dest, "w", encoding="ascii") as fh:
        fh.write(svg.encode("ascii", "xmlcharrefreplace").decode())
    print("wrote %s (%.1f KB)" % (dest, len(svg.encode()) / 1024.0))
