#!/usr/bin/env python3
"""
ROSE IN WINTER — an animated terminal flower.

Run with: python3 rose_in_winter.py
Press Q or Esc to quit. Ctrl+C also works.
No third-party packages required.
"""
import math
import os
import random
import shutil
import sys
import time

IS_WINDOWS = os.name == "nt"
old_term = None

def setup():
    global old_term
    if not IS_WINDOWS:
        import termios, tty
        old_term = termios.tcgetattr(sys.stdin.fileno())
        tty.setcbreak(sys.stdin.fileno())
        return None
    import msvcrt
    return msvcrt

def restore():
    if not IS_WINDOWS and old_term is not None:
        import termios
        termios.tcsetattr(sys.stdin.fileno(), termios.TCSADRAIN, old_term)
    sys.stdout.write("\033[0m\033[?25h\033[?1049l")
    sys.stdout.flush()

def key_ready(reader):
    if IS_WINDOWS:
        return reader.kbhit()
    import select
    return bool(select.select([sys.stdin], [], [], 0)[0])

def get_key(reader):
    if IS_WINDOWS:
        return reader.getch().decode(errors="ignore")
    return sys.stdin.read(1)

def put(buf, x, y, glyph, color):
    h, w = len(buf), len(buf[0])
    ix, iy = int(round(x)), int(round(y))
    if 0 <= ix < w and 0 <= iy < h:
        buf[iy][ix] = (glyph, color)

def line(buf, x0, y0, x1, y1, glyph, color, width=1):
    steps = max(1, int(math.hypot(x1-x0, y1-y0) * 2))
    for i in range(steps + 1):
        t = i / steps
        x = x0 + (x1-x0)*t
        y = y0 + (y1-y0)*t
        for ox in range(-width//2, width//2 + 1):
            put(buf, x+ox, y, glyph, color)

def ellipse_fill(buf, cx, cy, rx, ry, angle, color, glyphs="·:░▒▓"):
    ca, sa = math.cos(angle), math.sin(angle)
    reach = int(max(rx, ry) * 1.5) + 2
    for yy in range(int(cy-reach), int(cy+reach)+1):
        for xx in range(int(cx-reach), int(cx+reach)+1):
            dx, dy = xx-cx, yy-cy
            u = (dx*ca + dy*sa) / max(.01, rx)
            v = (-dx*sa + dy*ca) / max(.01, ry)
            d = u*u + v*v
            if d <= 1:
                # A little unevenness makes the petal edges feel organic.
                edge = math.sin(math.atan2(v, u)*5 + angle*2) * .035
                if d < 1 + edge:
                    shade = max(0, min(1, 1-math.sqrt(d)))
                    idx = min(len(glyphs)-1, int((1-shade)*(len(glyphs)-1)))
                    put(buf, xx, yy, glyphs[idx], color)

def main():
    reader = setup()
    sys.stdout.write("\033[?1049h\033[?25l\033[2J")
    sys.stdout.flush()
    random.seed()
    start = time.time()
    flakes = []
    stars = []
    last_size = None
    try:
        while True:
            t = time.time()-start
            size = shutil.get_terminal_size((100, 34))
            w, h = max(60, size.columns), max(22, size.lines)
            if size != last_size:
                stars = [(random.randrange(w), random.randrange(h), random.random()*6.28)
                         for _ in range(w*h//105)]
                flakes = []
                last_size = size

            buf = [[(" ", None) for _ in range(w)] for _ in range(h)]
            # Deep winter-night backdrop with a soft, distant teal haze.
            for y in range(h):
                for x in range(w):
                    haze = max(0, 1-abs(y-h*.24)/max(1,h*.27))
                    haze *= max(0, math.sin(x*.018+t*.13)*.5+.5)
                    c = (int(4+3*haze), int(9+20*haze), int(20+30*haze))
                    buf[y][x] = (" ", c)

            for sx, sy, phase in stars:
                tw = .5 + .5*math.sin(t*2+phase)
                put(buf, sx, sy, "·" if tw < .6 else "✦",
                    (int(85+90*tw), int(115+100*tw), int(145+100*tw)))

            # Distant snowy ground.
            ground = int(h*.87)
            for x in range(w):
                y = ground + int(1.2*math.sin(x*.035))
                put(buf, x, y, "▄", (90, 132, 164))
                if x % 3 == 0:
                    put(buf, x, y-1, "·", (125, 169, 197))

            # Flower geometry: a graceful stem and two leaves.
            base_x, base_y = w*.50, ground+1
            head_x, head_y = w*.50, h*.37
            sway = math.sin(t*.7)*1.2
            stem_x = base_x + sway
            line(buf, base_x, base_y, stem_x, head_y+5, "╱", (65, 151, 105), 1)
            # Stem highlight.
            line(buf, base_x+1, base_y, stem_x+1, head_y+5, "·", (100, 180, 127), 1)

            # Leaves, each a pointed little shape made from a line and leaf texture.
            for side, frac, length in [(-1, .64, 9), (1, .48, 8)]:
                anchor_x = base_x + (stem_x-base_x)*frac
                anchor_y = base_y + (head_y+5-base_y)*frac
                tip_x = anchor_x + side*length
                tip_y = anchor_y - 3
                line(buf, anchor_x, anchor_y, tip_x, tip_y, "╱", (73, 157, 105))
                for q in range(1, 8):
                    u = q/8
                    px = anchor_x + (tip_x-anchor_x)*u
                    py = anchor_y + (tip_y-anchor_y)*u
                    spread = math.sin(u*math.pi)*2.0
                    for k in range(-int(spread), int(spread)+1):
                        put(buf, px, py+k, "·" if abs(k) else "░",
                            (int(55+8*u), int(130+25*u), int(87+12*u)))

            # Bloom opens over the first 11 seconds, then gently breathes.
            opening = min(1, max(0, (t-1.0)/10.0))
            opening = opening*opening*(3-2*opening)
            breathe = 1 + .025*math.sin(t*1.1)
            head_sway = math.sin(t*.7)*.025
            cx, cy = head_x+sway*.25, head_y

            # Back petals first, then inner petals. Each layer unfurls outward.
            layers = [
                (7, 8.8, 3.4, .88, .12, (116, 28, 54)),
                (6, 7.0, 3.0, .70, .55, (174, 38, 75)),
                (5, 5.0, 2.45, .53, 1.05, (218, 67, 105)),
                (4, 3.1, 1.9, .34, 1.65, (245, 112, 139)),
            ]
            for layer_i, (count, reach, width, closed, phase, base) in enumerate(layers):
                spread = .28 + opening*.72
                scale = (.35 + .65*opening) * breathe
                for i in range(count):
                    a = (i/count)*math.tau + phase + head_sway
                    # Petal centres move outwards as the bloom opens.
                    dist = (reach*(.22 + .78*opening))*scale
                    px = cx + math.cos(a)*dist
                    py = cy + math.sin(a)*dist*.56
                    rx = (width*(.45 + .55*opening))*scale
                    ry = (width*.66*(.50 + .50*opening))*scale
                    # Petals point away from the heart.
                    col = (min(255,base[0]+i*2), max(0,base[1]-i), min(255,base[2]+i))
                    ellipse_fill(buf, px, py, rx, ry, a+math.pi/2, col)
                    # Fine bright rim along a few outer petal tips.
                    if i % 2 == 0 and opening > .35:
                        tipx = cx + math.cos(a)*dist*1.35
                        tipy = cy + math.sin(a)*dist*.76
                        put(buf, tipx, tipy, "✧", (255, 166, 184))

            # Dark central cup, then a warm golden heart.
            ellipse_fill(buf, cx, cy, 2.5*(.5+.5*opening), 1.8*(.5+.5*opening),
                         0, (119, 24, 56), "·░▒")
            for i in range(13):
                a = i*2.399
                r = (i%4)*.48
                put(buf, cx+math.cos(a)*r, cy+math.sin(a)*r*.55,
                    "•" if i%3 else "✦", (255, 202, 117))

            # Snow falls in front of and behind the flower.
            if random.random() < .9:
                flakes.append([random.uniform(1,w-2), -1, random.uniform(.25,.9),
                               random.random()*math.tau, random.random()])
            for f in flakes[:]:
                f[1] += f[2]*.65
                f[0] += math.sin(t*.8+f[3])*.18
                if f[1] >= h-2:
                    flakes.remove(f)
                else:
                    glyph = "❄" if f[4] > .83 else ("✧" if f[4] > .52 else "·")
                    put(buf, f[0], f[1], glyph, (int(145+f[4]*80), int(185+f[4]*65), 245))

            # A quiet, distant crescent moon.
            moon_x, moon_y = int(w*.78), int(h*.19)
            put(buf, moon_x, moon_y, "◕", (220, 231, 226))
            put(buf, moon_x+1, moon_y, "·", (220, 231, 226))

            def centered(y, text, color):
                x = (w-len(text))//2
                for j,ch in enumerate(text):
                    put(buf, x+j, y, ch, color)
            centered(0, "R O S E   I N   W I N T E R", (218, 190, 204))
            centered(1, "even the cold cannot keep beauty asleep", (117, 151, 172))
            centered(h-2, "Q / ESC  ·  QUIT     ✦     BLOOMING THROUGH THE SNOW",
                     (119, 153, 177))

            # Flush one complete frame.
            out = ["\033[H"]
            for row in buf:
                pieces, active = [], None
                for ch, col in row:
                    if col != active:
                        if col is None:
                            pieces.append("\033[0m")
                        else:
                            pieces.append(f"\033[38;2;{col[0]};{col[1]};{col[2]}m")
                        active = col
                    pieces.append(ch)
                pieces.append("\033[0m")
                out.append("".join(pieces))
            sys.stdout.write("\n".join(out))
            sys.stdout.flush()

            if key_ready(reader):
                k = get_key(reader).lower()
                if k in ("q", "\x1b"):
                    break
            time.sleep(1/24)
    except KeyboardInterrupt:
        pass
    finally:
        restore()

if __name__ == "__main__":
    main()
