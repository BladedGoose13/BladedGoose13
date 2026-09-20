"""Write assets/snake.svg as a palette-matched placeholder.

The snake workflow overwrites this on its first run. It exists so the README
never shows a broken image in the window between merging and that first run.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from palette import BG0, BG1, LINE, MONO, MUTED, ramp

W, H = 880, 200
CELL, GAP = 11, 3
COLS, ROWS = 53, 7


def build():
    gw = COLS * (CELL + GAP) - GAP
    gh = ROWS * (CELL + GAP) - GAP
    ox, oy = (W - gw) / 2, (H - gh) / 2 - 8
    o = ['<svg xmlns="http://www.w3.org/2000/svg" width="%d" height="%d" viewBox="0 0 %d %d" '
         'role="img" aria-label="Contribution snake, generated on the first scheduled run">'
         % (W, H, W, H)]
    o.append('<rect width="%d" height="%d" rx="12" fill="%s"/>' % (W, H, BG0))
    for c in range(COLS):
        for r in range(ROWS):
            o.append('<rect x="%.1f" y="%.1f" width="%d" height="%d" rx="2.5" fill="%s"/>'
                     % (ox + c * (CELL + GAP), oy + r * (CELL + GAP), CELL, CELL, LINE))
    # a hint of the snake, so the placeholder still reads as the right thing
    body = [(8, 3), (9, 3), (10, 3), (11, 3), (12, 3)]
    for i, (c, r) in enumerate(body):
        o.append('<rect x="%.1f" y="%.1f" width="%d" height="%d" rx="2.5" fill="%s" '
                 'opacity="%.2f"/>' % (ox + c * (CELL + GAP), oy + r * (CELL + GAP),
                                       CELL, CELL, ramp(0.30 + 0.16 * i), 0.55 + 0.09 * i))
    o.append('<text x="%d" y="%d" text-anchor="middle" font-family=%s font-size="10.5" '
             'fill="%s" letter-spacing="1.6">contribution snake &#183; generated on the first '
             'scheduled run</text>' % (W // 2, H - 22, '"%s"' % MONO, MUTED))
    o.append('<rect x=".75" y=".75" width="%.1f" height="%.1f" rx="12" fill="none" stroke="%s"/>'
             % (W - 1.5, H - 1.5, LINE))
    o.append('</svg>')
    return "".join(o)


if __name__ == "__main__":
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    dest = os.path.join(root, "assets", "snake.svg")
    svg = build()
    with open(dest, "w", encoding="utf-8") as fh:
        fh.write(svg)
    print("wrote %s (%.1f KB)" % (dest, len(svg.encode()) / 1024.0))
