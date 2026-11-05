#!/usr/bin/env python3
"""
COZY WORLDS — MOONLIT POND

A standalone, single-file terminal animation inspired by the supplied POLARIS
example. Uses only Python's standard library and ANSI true-colour output.

Run:
    python3 moonlit_pond.py

Press Q or Esc to quit. Ctrl+C also works.
"""

import math
import os
import random
import shutil
import sys
import time

IS_WINDOWS = os.name == "nt"
old_term = None


def setup_terminal():
    global old_term
    if IS_WINDOWS:
        import msvcrt
        return msvcrt
    import termios
    import tty
    old_term = termios.tcgetattr(sys.stdin.fileno())
    tty.setcbreak(sys.stdin.fileno())
    return None


def restore_terminal():
    if not IS_WINDOWS and old_term is not None:
        import termios
        termios.tcsetattr(sys.stdin.fileno(), termios.TCSADRAIN, old_term)
    sys.stdout.write("\033[0m\033[?25h\033[?1049l")
    sys.stdout.flush()


def key_pressed(reader):
    if IS_WINDOWS:
        return reader.kbhit()
    import select
    return bool(select.select([sys.stdin], [], [], 0)[0])


def read_key(reader):
    if IS_WINDOWS:
        return reader.getch().decode(errors="ignore")
    return sys.stdin.read(1)


import math
import random

def rgb(col, glyph):
    r, g, b = (max(0, min(255, int(v))) for v in col)
    return f'\x1b[38;2;{r};{g};{b}m{glyph}\x1b[0m'

def blend(a, b, t):
    t = max(0.0, min(1.0, t))
    return tuple((a[i] + (b[i] - a[i]) * t for i in range(3)))

class MoonlitPond:

    def __init__(self):
        self.rng = random.Random()
        self.stars = []
        self.fireflies = []
        self.petals = []
        self.ripples = []
        self.koi_x = -0.35
        self.last_size = (0, 0)

    def _reset(self, w, h):
        self.stars = [(self.rng.randrange(w), self.rng.randrange(2, int(h * 0.42)), self.rng.random() * math.tau, self.rng.choice(['·', '✦', '⋆', '•'])) for _ in range(max(24, w * h // 115))]
        self.fireflies = []
        self.petals = []
        self.ripples = []

    def render(self, w, h, now):
        if (w, h) != self.last_size:
            self._reset(w, h)
            self.last_size = (w, h)
        rng = self.rng
        canvas = [[(' ', None) for _ in range(w)] for _ in range(h)]

        def put(x, y, glyph, color):
            if 0 <= int(x) < w and 0 <= int(y) < h:
                canvas[int(y)][int(x)] = (glyph, color)

        def line(x1, y1, x2, y2, glyph, color):
            steps = max(abs(x2 - x1), abs(y2 - y1), 1)
            for i in range(steps + 1):
                t = i / steps
                put(round(x1 + (x2 - x1) * t), round(y1 + (y2 - y1) * t), glyph, color)

        def centered(y, text, color):
            x = (w - len(text)) // 2
            for i, ch in enumerate(text):
                put(x + i, y, ch, color)
        for sx, sy, phase, glyph in self.stars:
            twinkle = (math.sin(now * 1.8 + phase) + 1) / 2
            col = (int(82 + twinkle * 100), int(123 + twinkle * 95), int(155 + twinkle * 90))
            put(sx, sy, glyph if twinkle > 0.38 else '·', col)
        for y in range(2, int(h * 0.46)):
            for x in range(w):
                wave = math.sin(x * 0.035 + now * 0.22 + y * 0.08)
                glow = max(0, 1 - abs(y - (h * 0.24 + wave * 2)) / (h * 0.2))
                if glow > 0.15 and rng.random() < 0.055:
                    put(x, y, '░', (int(8 + 8 * glow), int(37 + 26 * glow), int(54 + 28 * glow)))
        mx, my = (int(w * 0.73), max(4, int(h * 0.15)))
        for dy in range(-3, 4):
            for dx in range(-4, 5):
                if dx * dx + dy * dy <= 14 and (dx + 2) ** 2 + (dy + 1) ** 2 > 11:
                    put(mx + dx, my + dy, '◦' if abs(dx) + abs(dy) > 4 else '●', (225, 226, 202) if dx < 1 else (184, 204, 201))
        put(mx - 5, my - 2, '✧', (210, 229, 222))
        shore = int(h * 0.48)
        for x in range(w):
            contour = shore + int(1.6 * math.sin(x * 0.025) + 1.1 * math.sin(x * 0.071 + 1))
            put(x, contour, '▄', (56, 99, 92))
            for y in range(contour + 1, int(h * 0.56)):
                if rng.random() < 0.11:
                    put(x, y, '·', (25, 61, 59))
        for tx, ty, scale in [(int(w * 0.12), int(h * 0.39), 1.0), (int(w * 0.88), int(h * 0.4), 0.9)]:
            line(tx, ty + 5, tx + int(2 * scale), ty - 3, '╱', (82, 72, 66))
            for bx, by in [(-4, -4), (0, -6), (4, -4), (-2, -1), (3, -1)]:
                for ox, oy in [(0, 0), (1, 0), (0, 1)]:
                    put(tx + int(bx * scale) + ox, ty + by + oy, rng.choice(['✿', '·', '✧']), (130, 105, 128) if rng.random() < 0.7 else (173, 137, 151))
        water_top = int(h * 0.55)
        for y in range(water_top, h - 3):
            depth = (y - water_top) / max(1, h - water_top)
            for x in range(w):
                shimmer = math.sin(x * 0.11 + now * 1.15 + y * 0.21)
                if (x + int(now * 3 + y * 0.17)) % 13 == 0 and shimmer > 0.25:
                    put(x, y, '─', (int(30 + 18 * depth), int(105 + 26 * shimmer), int(125 + 30 * shimmer)))
                elif rng.random() < 0.018:
                    put(x, y, '·', (38, 92, 108))
        for y in range(water_top + 1, h - 3):
            spread = 2 + int((y - water_top) * 0.17)
            centre = mx + int(math.sin(y * 0.12 + now * 0.3) * 2)
            for dx in range(-spread, spread + 1):
                if rng.random() < 0.23:
                    put(centre + dx, y, rng.choice(['·', '─', '˙']), (int(104 + rng.random() * 45), int(154 + rng.random() * 42), int(158 + rng.random() * 48)))
        pads = [(int(w * 0.2), int(h * 0.7)), (int(w * 0.39), int(h * 0.83)), (int(w * 0.78), int(h * 0.73)), (int(w * 0.62), int(h * 0.91))]
        for px, py in pads:
            sway = int(math.sin(now * 0.45 + px) * 1.2)
            put(px + sway, py, '◕', (66, 139, 112))
            put(px + 1 + sway, py, '━', (72, 151, 121))
            if (px, py) in (pads[0], pads[2]):
                put(px + 2 + sway, py - 1, '✿', (206, 155, 177))
        self.koi_x = now * 0.055 % 1.35 - 0.17
        kx = int(self.koi_x * w)
        ky = int(h * 0.76 + math.sin(now * 0.65) * 1.4)
        facing = 1
        put(kx, ky, '◁' if facing else '▷', (227, 174, 112))
        put(kx + 1, ky, '◉', (238, 208, 157))
        put(kx + 2, ky, '▰', (219, 153, 94))
        put(kx + 3, ky, '◁', (192, 123, 81))
        put(kx + 1, ky - 1, '·', (255, 235, 198))
        if 0 <= kx < w:
            put(kx - 2, ky + 1, '﹏', (57, 119, 130))
            put(kx - 4, ky + 2, '～', (44, 94, 111))
        if rng.random() < 0.045:
            self.ripples.append([rng.randrange(int(w * 0.15), int(w * 0.85)), rng.randrange(water_top + 3, h - 5), 0.0])
        for ripple in self.ripples[:]:
            ripple[2] += 0.12
            radius = ripple[2]
            if radius > 5:
                self.ripples.remove(ripple)
                continue
            rx, ry = (ripple[0], ripple[1])
            for dx in range(-int(radius * 2), int(radius * 2) + 1):
                if abs(abs(dx) - radius * 2) < 1.2:
                    put(rx + dx, ry, '﹏', (42, 111, 124))
        for base_x in [int(w * 0.04), int(w * 0.95), int(w * 0.97)]:
            for n in range(3):
                bx = base_x + n * 2
                sway = int(math.sin(now * 0.8 + n + base_x) * 1.5)
                line(bx, h - 4, bx + sway, int(h * 0.54) + n * 2, '╱', (66, 128, 105))
                put(bx + sway, int(h * 0.54) + n * 2, '│', (92, 151, 117))
        if rng.random() < 0.12:
            self.fireflies.append([rng.uniform(w * 0.08, w * 0.92), rng.uniform(h * 0.35, h * 0.72), rng.random() * math.tau, rng.uniform(2.5, 5.0)])
        for fly in self.fireflies[:]:
            fly[0] += math.sin(now * 0.7 + fly[2]) * 0.16
            fly[1] += math.cos(now * 0.55 + fly[2]) * 0.08
            fly[3] -= 1 / 24
            if fly[3] <= 0:
                self.fireflies.remove(fly)
            else:
                pulse = (math.sin(now * 4 + fly[2]) + 1) / 2
                if pulse > 0.35:
                    put(round(fly[0]), round(fly[1]), '·', (int(115 + 120 * pulse), int(155 + 90 * pulse), int(91 + 35 * pulse)))
        if rng.random() < 0.025:
            self.petals.append([rng.uniform(w * 0.15, w * 0.85), -1, rng.uniform(0.25, 0.55), rng.random() * math.tau])
        for petal in self.petals[:]:
            petal[1] += petal[2]
            petal[0] += math.sin(now * 0.8 + petal[3]) * 0.18
            if petal[1] >= h - 4:
                self.petals.remove(petal)
            else:
                put(round(petal[0]), round(petal[1]), '✿', (179, 131, 157))
        centered(0, 'M O O N L I T   P O N D', (174, 214, 218))
        centered(1, 'A QUIET GARDEN BENEATH THE MOON', (100, 157, 164))
        centered(h - 2, 'Q / ESC  •  QUIT     ✦     STILL WATERS, SOFT LIGHT', (94, 145, 154))
        rows = []
        for row in canvas:
            parts = []
            active = None
            for glyph, color in row:
                if color != active:
                    parts.append('\x1b[0m' if color is None else f'\x1b[38;2;{color[0]};{color[1]};{color[2]}m')
                    active = color
                parts.append(glyph)
            parts.append('\x1b[0m')
            rows.append(''.join(parts))
        return '\n'.join(rows)


def main():
    reader = setup_terminal()
    sys.stdout.write("\033[?1049h\033[?25l\033[2J")
    sys.stdout.flush()

    scene = MoonlitPond()
    start = time.time()
    last_size = (0, 0)

    try:
        while True:
            now = time.time() - start
            term = shutil.get_terminal_size((100, 34))
            width, height = max(60, term.columns), max(22, term.lines)

            # The scene handles its own resize-dependent particles and stars.
            frame = scene.render(width, height, now)
            sys.stdout.write("\033[H" + frame)
            sys.stdout.flush()

            if key_pressed(reader):
                key = read_key(reader).lower()
                if key in ("q", "\x1b", "\x03"):
                    break
            time.sleep(1 / 24)

    except KeyboardInterrupt:
        pass
    finally:
        restore_terminal()


if __name__ == "__main__":
    main()
