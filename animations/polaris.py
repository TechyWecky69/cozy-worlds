#!/usr/bin/env python3
"""
POLARIS — a tiny animated winter world for your terminal.

Run:
    python3 polaris.py

Press Q or Esc to quit. Ctrl+C also works.
Uses only the Python standard library.
"""
import math
import os
import random
import shutil
import sys
import time

# ---------- terminal input / cleanup ----------
IS_WINDOWS = os.name == "nt"
old_term = None

def setup_terminal():
    global old_term
    if IS_WINDOWS:
        import msvcrt
        return msvcrt
    else:
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

# ---------- drawing helpers ----------
def rgb(r, g, b, text):
    return f"\033[38;2;{int(r)};{int(g)};{int(b)}m{text}\033[0m"

def bg_rgb(r, g, b, text):
    return f"\033[48;2;{int(r)};{int(g)};{int(b)}m{text}\033[0m"

def blend(a, b, t):
    return tuple(a[i] + (b[i] - a[i]) * t for i in range(3))

def put(canvas, x, y, text, color=None):
    h, w = len(canvas), len(canvas[0])
    if 0 <= y < h and 0 <= x < w:
        canvas[y][x] = (text, color)

def centered(canvas, y, text, color):
    x = (len(canvas[0]) - len(text)) // 2
    for i, ch in enumerate(text):
        put(canvas, x + i, y, ch, color)

def main():
    reader = setup_terminal()
    sys.stdout.write("\033[?1049h\033[?25l\033[2J")
    sys.stdout.flush()

    random.seed()
    start = time.time()
    stars = []
    flakes = []
    last_size = (0, 0)

    try:
        while True:
            now = time.time() - start
            term = shutil.get_terminal_size((100, 34))
            w, h = max(50, term.columns), max(20, term.lines)
            if (w, h) != last_size:
                stars = [(random.randrange(w), random.randrange(max(1, h - 5)),
                          random.random() * math.tau, random.choice(["·", "✦", "⋆", "•"]))
                         for _ in range(max(30, w * h // 100))]
                flakes = []
                last_size = (w, h)

            # Work in a virtual canvas, then print one frame.
            canvas = [[(" ", None) for _ in range(w)] for _ in range(h)]
            cx, cy = w // 2, int(h * 0.49)
            radius = min(w * 0.245, h * 0.34, 19)
            radius = max(7, radius)
            rx, ry = radius * 1.48, radius * 0.92
            top = max(2, int(cy - ry - 5))

            # Distant aurora ribbons.
            for y in range(1, max(2, int(h * 0.42))):
                for x in range(w):
                    wave = (math.sin(x * 0.035 + now * 0.55 + y * 0.07)
                            + math.sin(x * 0.018 - now * 0.32 + y * 0.11)) * 0.5
                    glow = max(0.0, 1.0 - abs(y - (h * 0.18 + wave * 5)) / 9)
                    glow *= 0.26 + 0.16 * math.sin(x * 0.012 + now * 0.2)
                    if glow > 0.025:
                        c = (int(8 + 20 * glow), int(22 + 155 * glow),
                             int(38 + 125 * glow))
                        put(canvas, x, y, "░", c)

            # Stars twinkle above and around the globe.
            for sx, sy, phase, glyph in stars:
                tw = (math.sin(now * 2.2 + phase) + 1) / 2
                if sy < h - 5:
                    col = (int(95 + tw * 110), int(135 + tw * 100), int(170 + tw * 85))
                    put(canvas, sx, sy, glyph if tw > .42 else "·", col)

            # Globe glass: softly shaded sphere with a bright rim.
            for yy in range(int(cy - ry), int(cy + ry) + 1):
                for xx in range(int(cx - rx), int(cx + rx) + 1):
                    nx, ny = (xx - cx) / rx, (yy - cy) / ry
                    d = nx * nx + ny * ny
                    if d <= 1:
                        shade = math.sqrt(max(0, 1 - d))
                        # Deep blue glass, brighter along the upper-left edge.
                        light = max(0, 1 - math.sqrt((nx + .42) ** 2 + (ny + .48) ** 2))
                        c = (int(8 + 13 * shade + 20 * light),
                             int(22 + 36 * shade + 42 * light),
                             int(45 + 70 * shade + 65 * light))
                        put(canvas, xx, yy, " ", c)

            # Snow-covered ground inside the globe.
            for xx in range(int(cx - rx * .91), int(cx + rx * .91)):
                nx = (xx - cx) / rx
                ground_y = int(cy + ry * (0.36 + 0.09 * math.sin(nx * 4.8 + .6)))
                for yy in range(ground_y, int(cy + ry * .91)):
                    depth = (yy - ground_y) / max(1, ry)
                    c = (int(105 + 70 * (1-depth)), int(165 + 65 * (1-depth)),
                         int(205 + 45 * (1-depth)))
                    put(canvas, xx, yy, " ", c)

            # Little pine trees, with a gentle sway.
            tree_specs = [(-.58, .28, 4), (-.32, .17, 6), (.42, .26, 5), (.67, .34, 3)]
            for tx, ty, th in tree_specs:
                x0 = int(cx + tx * rx)
                y0 = int(cy + ty * ry)
                for level in range(th):
                    width = level // 2 + 1
                    y = y0 - level
                    for dx in range(-width, width + 1):
                        put(canvas, x0 + dx, y, "▲" if dx == 0 else "♠",
                            (45, int(125 + level * 10), int(118 + level * 8)))
                put(canvas, x0, y0 + 1, "▮", (105, 78, 60))

            # Tiny cabin, warmly lit.
            hx, hy = int(cx + rx * .22), int(cy + ry * .22)
            for dy in range(3):
                for dx in range(7):
                    put(canvas, hx + dx - 3, hy + dy, "█", (105, 75, 68))
            for dx in range(-4, 5):
                put(canvas, hx + dx, hy - 1 + abs(dx)//2, "▲", (142, 91, 79))
            put(canvas, hx - 1, hy + 1, "▯", (255, 207, 111))
            put(canvas, hx + 1, hy + 1, "▯", (255, 207, 111))

            # A small moon.
            mx, my = int(cx - rx * .48), int(cy - ry * .45)
            put(canvas, mx, my, "◔", (255, 232, 176))
            put(canvas, mx + 1, my, "·", (255, 232, 176))

            # Snowflakes drift down with a slow sideways spiral.
            if random.random() < 0.8:
                flakes.append([random.uniform(cx-rx*.85, cx+rx*.85),
                               random.uniform(cy-ry*.85, cy+ry*.2),
                               random.uniform(.25, .85), random.random()*math.tau])
            for flake in flakes[:]:
                flake[1] += flake[2] * .42
                flake[0] += math.sin(now * 1.3 + flake[3]) * .24
                fx, fy = int(flake[0]), int(flake[1])
                nx, ny = (flake[0]-cx)/rx, (flake[1]-cy)/ry
                if nx*nx + ny*ny < .91 and fy < h:
                    put(canvas, fx, fy, random.choice(["·", "✧", "❄"]), (205, 229, 247))
                if fy > cy + ry * .92:
                    flakes.remove(flake)

            # Glass outline, double rim and glints.
            for step in range(720):
                a = step * math.tau / 720
                x = int(cx + rx * math.cos(a))
                y = int(cy + ry * math.sin(a))
                col = (int(125 + 80 * (1-math.sin(a))), int(190 + 55 * (1-math.sin(a))),
                       int(225 + 30 * (1-math.sin(a))))
                put(canvas, x, y, "◦", col)
            # Moving specular highlight.
            glint_a = -2.25 + math.sin(now * .45) * .16
            gx, gy = int(cx + rx * math.cos(glint_a)), int(cy + ry * math.sin(glint_a))
            put(canvas, gx, gy, "✧", (245, 253, 255))
            put(canvas, gx + 1, gy + 1, "·", (205, 238, 255))

            # Globe neck and pedestal.
            neck_y = int(cy + ry)
            for yy in range(neck_y, neck_y + 3):
                for xx in range(cx - 5, cx + 6):
                    put(canvas, xx, yy, " ", (104, 133, 157))
            base_y = neck_y + 3
            for yy, half in [(base_y, 9), (base_y+1, 12), (base_y+2, 14), (base_y+3, 12)]:
                for xx in range(cx-half, cx+half+1):
                    edge = abs(xx-cx) / half
                    col = (int(65 + 65*(1-edge)), int(91 + 75*(1-edge)),
                           int(122 + 80*(1-edge)))
                    put(canvas, xx, yy, "▄" if yy == base_y+3 else "█", col)
            for xx in range(cx-7, cx+8):
                put(canvas, xx, base_y+1, "━", (180, 207, 224))

            # Header / footer.
            centered(canvas, 0, "P O L A R I S", (183, 224, 245))
            centered(canvas, 1, "A LITTLE WINTER, IN A LITTLE WORLD", (104, 157, 187))
            footer = "Q / ESC  •  QUIT     ✦     LET IT SNOW"
            centered(canvas, h-2, footer, (112, 158, 184))

            # Render: true-colour terminal, no flicker.
            out = ["\033[H"]
            for row in canvas:
                line = []
                active = None
                for ch, color in row:
                    if color != active:
                        if color is None:
                            line.append("\033[0m")
                        else:
                            line.append(f"\033[38;2;{color[0]};{color[1]};{color[2]}m")
                        active = color
                    line.append(ch)
                line.append("\033[0m")
                out.append("".join(line))
            sys.stdout.write("\n".join(out))
            sys.stdout.flush()

            if key_pressed(reader):
                k = read_key(reader).lower()
                if k in ("q", "\x1b"):
                    break
            time.sleep(1 / 24)

    except KeyboardInterrupt:
        pass
    finally:
        restore_terminal()

if __name__ == "__main__":
    main()
