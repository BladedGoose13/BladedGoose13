"""Build the animated pixel-art scenes in assets/art/.

Three panels on one theme -- coffee, study, HPC at home -- drawn on a
shared night palette so they read as a set beside the two cafe pieces.

Every scene is frame-animated (see pixel.sprite_svg): frame 0 is authored
visible, so a renderer that skips SMIL shows a correct still rather than
an empty box.
"""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from pixel import Canvas, sprite_svg

# -- night palette, tuned to sit beside the cafe artwork --------------------
NIGHT = "#0E0A1E"
WALL = "#241F3E"
WALL_D = "#191531"
FLOOR = "#261D22"
WOOD_D = "#3E2A1E"
WOOD = "#6B4A2F"
WOOD_L = "#8B6340"
WOOD_H = "#A87A50"
LAMP = "#F5C86B"
LAMP_H = "#FFE7B0"
WARM = "#FFF3D6"
GLOW = "#3A3A2A"
COF_D = "#2E1B10"
COF = "#5C3A20"
CREMA = "#C08B5C"
CERAM = "#C4553A"
CERAM_D = "#8E3A26"
SCREEN = "#141030"
CYAN = "#67E8F9"
AMBER = "#E8A34B"
LED_G = "#7FD97F"
LED_R = "#E85D5D"
METAL = "#332E52"
METAL_L = "#645C92"
PLANT = "#4A7A4A"
PLANT_L = "#6BA36B"
PAPER = "#EFE2C4"
PAPER_S = "#CDBC98"
INKC = "#5A4632"
STAR = "#EADCF7"
SHADOW = "#0C0818"

ART = "assets/art"
SCALE = 5
W, H = 72, 56


def steam(c, x, y, phase, col=WARM):
    """Three wisps that rise and fade; phase shifts them per frame."""
    for k, dx in enumerate((-2, 0, 2)):
        for i in range(5):
            yy = y - i - ((phase + k * 2) % 3)
            if yy < 0:
                continue
            wob = (1 if ((i + phase + k) % 4) < 2 else -1)
            if i >= 3 and (i + phase + k) % 2:
                continue
            c.set(x + dx + wob, yy, col)


def mug(c, x, y, body=CERAM, dark=CERAM_D):
    """A chunky 8x7 mug with a handle, sitting on its base row."""
    c.rect(x, y, 8, 6, body)
    c.rect(x, y, 8, 1, dark)
    c.rect(x + 1, y + 1, 6, 1, COF_D)
    c.rect(x + 2, y + 1, 3, 1, COF)
    c.vline(x + 8, y + 2, y + 4, body)
    c.set(x + 9, y + 3, body)
    c.rect(x, y + 6, 8, 1, dark)
    c.vline(x + 1, y + 2, y + 4, dark)


# Draw order per scene: background, then the light in the air, then the
# solid props, then the animated overlay.
#
# The beam is opaque stipple, so it has to go *behind* the props -- painted
# after them it simply erases the mug. Light in front of an object is haze;
# light on an object is a highlight, and those are placed explicitly.

# ---------------------------------------------------------------- scene 1
def scene_coffee(phase):
    c = Canvas(W, H)
    c.rect(0, 0, W, H, WALL)
    c.rect(0, 0, W, 22, WALL_D)
    c.vline(36, 0, 5, METAL)

    c.beam(36, 11, 21, 0.44, "#FFE7B0", "#D8A75E", 0.72)   # haze, behind props

    c.rect(30, 6, 13, 2, CERAM_D)
    c.rect(32, 8, 9, 1, LAMP)
    c.rect(34, 9, 5, 1, LAMP_H)
    c.disc(36, 9, 2, WARM)
    c.rect(4, 14, 18, 2, WOOD)
    c.rect(6, 8, 7, 6, "#373159")
    c.rect(7, 9, 5, 4, COF_D)
    for bx, by in ((8, 11), (10, 10), (9, 12), (11, 12)):
        c.set(bx, by, COF)
    c.rect(15, 10, 5, 4, CERAM)
    c.rect(0, 40, W, 3, WOOD_L)
    c.rect(0, 40, W, 1, WOOD_H)
    c.hline(27, 46, 40, "#D9A96E")            # counter, lit under the lamp
    c.rect(0, 43, W, H - 43, WOOD_D)
    for gx in range(0, W, 9):
        c.vline(gx, 44, H - 1, FLOOR)
    c.rect(28, 39, 16, 1, PAPER)
    mug(c, 31, 33)
    c.vline(31, 34, 37, "#E07A55")            # rim highlight facing the lamp
    c.line(48, 39, 54, 35, METAL_L)
    c.disc(47, 39, 1, METAL_L)
    for bx, by in ((20, 39), (23, 39), (21, 38)):
        c.disc(bx, by, 1, COF)
        c.set(bx, by, COF_D)
    mug(c, 58, 35, CERAM_D, "#6B2B1C")

    steam(c, 35, 31, phase)
    return c


# ---------------------------------------------------------------- scene 2
def scene_study(phase):
    c = Canvas(W, H)
    c.rect(0, 0, W, H, WALL)
    c.rect(4, 4, 26, 22, NIGHT)
    c.frame(4, 4, 26, 22, WOOD)
    c.vline(17, 5, 25, WOOD)
    c.hline(5, 28, 15, WOOD)
    c.disc(24, 10, 3, PAPER)
    c.disc(22, 9, 3, NIGHT)
    c.rect(38, 8, 30, 2, WOOD)
    for i, col in enumerate((CERAM_D, PLANT, WOOD_H, "#4E4886", CERAM)):
        c.rect(40 + i * 4, 2, 3, 6, col)
        c.set(41 + i * 4, 3, WARM)

    c.beam(21, 27, 12, 1.0, "#FFE7B0", "#D8A75E", 0.72)     # haze, behind props

    c.vline(12, 28, 37, METAL)
    c.rect(10, 37, 5, 1, METAL_L)
    c.line(12, 28, 17, 25, METAL)
    c.rect(16, 23, 8, 3, CERAM_D)
    c.disc(20, 26, 2, WARM)
    c.rect(0, 38, W, 3, WOOD_L)
    c.rect(0, 38, W, 1, WOOD_H)
    c.hline(14, 44, 38, "#D9A96E")            # desk, lit under the lamp
    c.rect(0, 41, W, H - 41, WOOD_D)
    c.rect(6, 41, 2, H - 41, FLOOR)
    c.rect(62, 41, 2, H - 41, FLOOR)
    c.rect(24, 32, 20, 6, PAPER)
    c.rect(24, 32, 10, 6, PAPER_S)
    c.rect(24, 32, 8, 6, "#FFF6E2")           # the lit half of the page
    c.vline(34, 31, 37, WOOD_D)
    for r in range(3):
        c.hline(26, 31, 33 + r * 2, INKC)
        c.hline(36, 42, 33 + r * 2, INKC)
    mug(c, 48, 32)
    c.rect(2, 30, 6, 8, CERAM)
    c.rect(2, 30, 6, 1, CERAM_D)
    for lx, ly in ((3, 28), (5, 26), (7, 28), (4, 25), (6, 24)):
        c.disc(lx, ly, 1, PLANT_L if (lx + ly) % 2 else PLANT)
    c.line(46, 38, 52, 38, AMBER)

    c.rect(17, 26, 6, 1, LAMP_H if phase % 2 == 0 else LAMP)
    stars = ((7, 8), (12, 11), (9, 20), (14, 22), (21, 19), (26, 22), (11, 7), (27, 17))
    for i, (sx, sy) in enumerate(stars):
        if (i + phase) % 3:
            c.set(sx, sy, STAR)
    steam(c, 52, 30, phase)
    return c


# ---------------------------------------------------------------- scene 3
def scene_hpc(phase):
    c = Canvas(W, H)
    c.rect(0, 0, W, H, WALL_D)
    c.rect(0, 0, W, 4, NIGHT)
    c.rect(10, 6, 34, 26, METAL)
    c.rect(12, 8, 30, 22, SCREEN)
    c.hline(12, 41, 19, "#32255E")            # Fermi level
    for k in range(4):
        base = 11 + k * 4
        for x in range(12, 42):
            t = (x - 12) / 29.0
            y = base + int(3.2 * math.sin(t * math.pi * (1 + k * 0.5) + k))
            c.set(x, y, CYAN if k % 2 == 0 else AMBER)
    c.rect(10, 32, 34, 2, METAL_L)
    c.rect(24, 34, 6, 3, METAL)
    c.rect(20, 37, 14, 1, METAL_L)
    c.rect(46, 10, 16, 22, METAL)
    c.rect(47, 11, 14, 20, "#0E1A12")
    c.rect(46, 32, 16, 2, METAL_L)
    c.rect(52, 34, 4, 3, METAL)
    c.rect(64, 12, 8, 26, METAL)
    c.frame(64, 12, 8, 26, METAL_L)
    c.ring(69, 22, 3, METAL_L)
    c.rect(0, 38, W, 3, WOOD_L)
    c.rect(0, 38, W, 1, WOOD_H)
    c.hline(10, 44, 38, "#7E76B8")            # desk under the screens, cool-lit
    c.rect(0, 41, W, H - 41, WOOD_D)
    c.rect(14, 42, 26, 5, METAL)
    for r in range(3):
        for k in range(11):
            c.set(16 + k * 2, 43 + r, METAL_L)
    mug(c, 2, 32)
    c.rect(44, 44, 8, 4, METAL)               # external drive

    # --- animated overlay ---------------------------------------------
    rows = ((2, 8), (3, 11), (2, 6), (4, 9), (2, 12), (3, 7), (2, 10))
    for i in range(6):
        src = rows[(i + phase) % len(rows)]
        yy = 13 + i * 3
        c.hline(48, 48 + src[0], yy, LED_G)
        c.hline(50 + src[0], 48 + src[1], yy, "#3E7A4E")
    for i in range(7):
        on = ((i + phase) % 7) < 4
        c.set(65, 15 + i * 3, LED_G if on else "#2A3A2E")
    spokes = ((0, -3), (3, 0), (0, 3), (-3, 0)) if phase % 2 == 0 else \
             ((2, -2), (2, 2), (-2, 2), (-2, -2))
    for dx, dy in spokes:
        c.line(69, 22, 69 + dx, 22 + dy, CYAN)
    c.set(69, 35, LED_R if phase % 3 == 0 else "#5A2A2A")
    c.set(46, 45, LED_G if phase % 2 else "#2A3A2E")
    steam(c, 6, 30, phase)
    return c


SCENES = (
    ("pixel-coffee", scene_coffee, 4, 5,
     "Pixel art: a cup of coffee steaming on a cafe counter at night"),
    ("pixel-study", scene_study, 4, 4,
     "Pixel art: a desk lamp, an open book and a mug beside a starry window"),
    ("pixel-hpc", scene_hpc, 6, 6,
     "Pixel art: a home workstation running a band-structure calculation, "
     "with a Slurm queue on the side monitor"),
)

if __name__ == "__main__":
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    os.makedirs(os.path.join(root, ART), exist_ok=True)
    for name, fn, nframes, fps, desc in SCENES:
        frames = [fn(p) for p in range(nframes)]
        svg = sprite_svg(frames, SCALE, fps=fps, desc=desc, bg=NIGHT, pad=4)
        dest = os.path.join(root, ART, "%s.svg" % name)
        with open(dest, "w", encoding="ascii") as fh:
            fh.write(svg.encode("ascii", "xmlcharrefreplace").decode())
        print("wrote %s (%.1f KB, %d frames)" % (dest, len(svg.encode()) / 1024.0, nframes))
