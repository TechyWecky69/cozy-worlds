#!/usr/bin/env python3
"""
COZY FIREPLACE — a tiny animated cabin scene for your terminal.

Run:
    python3 cozy_fireplace.py

Press Q or Esc to quit. Ctrl+C also works.
Uses only the Python standard library.
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

def put(canvas, x, y, glyph, color=None):
    h, w = len(canvas), len(canvas[0])
    if 0 <= int(x) < w and 0 <= int(y) < h:
        canvas[int(y)][int(x)] = (glyph, color)

def centered(canvas, y, text, color):
    x = (len(canvas[0]) - len(text)) // 2
    for i, ch in enumerate(text):
        put(canvas, x + i, y, ch, color)

def rect(canvas, x1, y1, x2, y2, glyph, color):
    h, w = len(canvas), len(canvas[0])
    for y in range(max(0, y1), min(h, y2)):
        for x in range(max(0, x1), min(w, x2)):
            put(canvas, x, y, glyph, color)

def line(canvas, x1, y1, x2, y2, glyph, color):
    steps = max(abs(x2-x1), abs(y2-y1), 1)
    for i in range(steps + 1):
        t = i / steps
        put(canvas, round(x1+(x2-x1)*t), round(y1+(y2-y1)*t), glyph, color)

def main():
    reader = setup_terminal()
    sys.stdout.write("\033[?1049h\033[?25l\033[2J")
    sys.stdout.flush()

    random.seed()
    start = time.time()
    sparks = []
    stars = []
    last_size = (0, 0)

    try:
        while True:
            now = time.time() - start
            term = shutil.get_terminal_size((100, 34))
            w, h = max(60, term.columns), max(22, term.lines)
            if (w, h) != last_size:
                stars = [(random.randrange(w), random.randrange(2, max(3, int(h*.34))),
                          random.random()*math.tau) for _ in range(max(15, w*h//180))]
                sparks = []
                last_size = (w, h)

            canvas = [[(" ", None) for _ in range(w)] for _ in range(h)]

            # Deep blue cabin walls, timber beams and a dim window glow.
            rect(canvas, 0, 2, w, h-5, " ", (13, 19, 35))
            rect(canvas, 0, int(h*.72), w, h-3, " ", (29, 23, 32))
            for x in range(3, w, max(10, w//11)):
                rect(canvas, x, 2, x+1, int(h*.72), "│", (25, 34, 54))
            for y in (3, int(h*.18), int(h*.72)):
                rect(canvas, 0, y, w, y+1, "━", (35, 39, 61))

            # Two moonlit windows with pine silhouettes beyond.
            for x1, x2 in ((2, int(w*.24)), (int(w*.76), w-3)):
                top, bottom = int(h*.17), int(h*.59)
                rect(canvas, x1, top, x2, bottom, " ", (8, 29, 53))
                for sx in range(x1+2, x2-2, 5):
                    for sy in range(top+2, bottom-2):
                        if random.random() < .018:
                            put(canvas, sx, sy, "·", (130, 174, 205))
                # Distant mountain line and dark pines.
                for xx in range(x1+1, x2-1):
                    ridge = int(top+(bottom-top)*.57 + math.sin(xx*.17)*2)
                    put(canvas, xx, ridge, "▄", (22, 58, 82))
                for tx in range(x1+3, x2-3, max(5, (x2-x1)//5)):
                    base = bottom-2
                    th = random.Random(tx).randint(4, 8)
                    for level in range(th):
                        half = level//2
                        for dx in range(-half, half+1):
                            put(canvas, tx+dx, base-level, "▲" if dx == 0 else "♠",
                                (18, 65+level*3, 76+level*3))
                rect(canvas, x1-1, top-1, x1+1, bottom+1, "┃", (55, 48, 67))
                rect(canvas, x2-1, top-1, x2+1, bottom+1, "┃", (55, 48, 67))
                rect(canvas, x1-1, top-1, x2+1, top+1, "━", (55, 48, 67))
                rect(canvas, x1-1, bottom-1, x2+1, bottom+1, "━", (55, 48, 67))
                mid = (x1+x2)//2
                rect(canvas, mid, top, mid+1, bottom, "│", (39, 54, 72))
                rect(canvas, x1, (top+bottom)//2, x2, (top+bottom)//2+1, "─", (39, 54, 72))

            for sx, sy, phase in stars:
                tw = (math.sin(now*1.7+phase)+1)/2
                put(canvas, sx, sy, "·" if tw < .5 else "✦",
                    (int(80+tw*90), int(120+tw*95), int(160+tw*90)))

            # Fireplace stone chimney breast.
            cx = w//2
            fw = min(int(w*.43), 43)
            left, right = cx-fw//2, cx+fw//2
            top, base = int(h*.19), int(h*.76)
            rect(canvas, left-2, top, right+2, base, "▓", (72, 64, 75))
            # Stone blocks, staggered seams.
            for yy in range(top+1, base, 3):
                rect(canvas, left-2, yy, right+2, yy+1, "━", (43, 43, 59))
                offset = 0 if (yy//3)%2 else 4
                for xx in range(left+offset, right, 9):
                    put(canvas, xx, yy-1, "┊", (91, 72, 74))
            # Framed landscape above the mantel.
            pic_top, pic_bottom = top+2, int(h*.37)
            pic_l, pic_r = cx-9, cx+10
            rect(canvas, pic_l-1, pic_top-1, pic_r+1, pic_bottom+1, " ", (104, 68, 49))
            rect(canvas, pic_l, pic_top, pic_r, pic_bottom, " ", (19, 35, 55))
            centered(canvas, pic_top+1, "  ◔  ", (236, 184, 128))
            for xx in range(pic_l+1, pic_r-1):
                yy = pic_bottom-2-int(abs(xx-cx)*.35)
                put(canvas, xx, yy, "▲", (65, 74, 99))
            # Mantel shelf.
            my = int(h*.40)
            rect(canvas, left-5, my, right+5, my+2, "━", (126, 76, 49))
            rect(canvas, left-4, my+2, right+4, my+3, "─", (67, 43, 39))

            # Stockings hanging from the shelf.
            for sx, col in ((cx-7, (166, 62, 66)), (cx, (62, 103, 128)), (cx+7, (151, 65, 78))):
                put(canvas, sx, my+3, "│", (190, 145, 119))
                for dy in range(4):
                    put(canvas, sx, my+4+dy, "█", col)
                put(canvas, sx+1, my+7, "▰", col)
                put(canvas, sx+1, my+8, "▰", col)
                put(canvas, sx, my+4, "▔", (231, 213, 190))

            # Firebox opening.
            fire_top, fire_bottom = my+5, base-3
            box_l, box_r = left+3, right-3
            rect(canvas, box_l, fire_top, box_r, fire_bottom, " ", (8, 8, 15))
            rect(canvas, box_l-1, fire_bottom-2, box_r+1, fire_bottom, "━", (108, 65, 45))

            # Logs and coals.
            log_y = fire_bottom-4
            line(canvas, box_l+4, log_y+1, box_r-4, log_y-1, "━", (101, 55, 35))
            line(canvas, box_l+5, log_y-1, box_r-5, log_y+1, "━", (75, 43, 32))
            rect(canvas, box_l+5, fire_bottom-2, box_r-5, fire_bottom-1, "·", (255, 104, 25))
            for xx in range(box_l+3, box_r-3, 3):
                if random.random() < .7:
                    put(canvas, xx, fire_bottom-2, "•", random.choice([(255, 91, 22), (255, 165, 42), (255, 215, 95)]))

            # Organic flame tongues, changing height and shape every frame.
            palette = [(112, 31, 22), (194, 54, 20), (242, 91, 22),
                       (255, 145, 35), (255, 197, 74), (255, 231, 145)]
            for xx in range(box_l+3, box_r-3):
                u = (xx-(box_l+3))/max(1, box_r-box_l-6)
                envelope = math.sin(math.pi*u)**.65
                flicker = .72 + .28*math.sin(now*7.1+xx*.41) + .12*math.sin(now*11+xx*.17)
                flame_h = max(1, int((fire_bottom-fire_top)*.62*envelope*flicker))
                drift = int(math.sin(now*4+xx*.23)*1.4)
                for dy in range(flame_h):
                    yy = fire_bottom-3-dy
                    rel = dy/max(1, flame_h)
                    edge = abs((xx-cx)+drift)
                    if rel < .94 and edge < (box_r-box_l)*(.48-rel*.15):
                        jitter = random.random()
                        idx = min(5, int((1-rel)*5.2))
                        col = palette[idx]
                        if rel < .22 and jitter > .35:
                            col = palette[5 if jitter > .78 else 4]
                        glyph = random.choice(["▴", "▲", "▰", " "]) if rel > .6 else random.choice(["▲", "▴", "█"])
                        if glyph != " ":
                            put(canvas, xx, yy, glyph, col)

            # Warm wall glow around the hearth.
            for _ in range(100):
                gx = random.randint(left-5, right+5)
                gy = random.randint(my+2, base-1)
                if random.random() < .5:
                    put(canvas, gx, gy, "·", random.choice([(104, 49, 36), (128, 58, 34), (88, 48, 43)]))

            # Candles on the mantel.
            for candle_x in (left+3, right-4):
                rect(canvas, candle_x, my-3, candle_x+2, my, "▮", (210, 178, 129))
                put(canvas, candle_x, my-4-int(math.sin(now*8+candle_x)*1), "♨", (255, 190, 87))

            # Fire sparks rising from the hearth.
            if random.random() < .8:
                sparks.append([random.uniform(cx-5, cx+5), fire_bottom-4,
                               random.uniform(.3, 1.1), random.random()*math.tau])
            for spark in sparks[:]:
                spark[1] -= spark[2]*.55
                spark[0] += math.sin(now*2+spark[3])*.22
                spark[2] -= .006
                if spark[1] < fire_top or spark[2] <= 0:
                    sparks.remove(spark)
                else:
                    put(canvas, round(spark[0]), round(spark[1]), "·",
                        (255, random.randint(112, 190), random.randint(35, 75)))

            # Hearth tools and log basket.
            tool_x = min(w-8, right+7)
            for i in range(3):
                line(canvas, tool_x+i*2, base-10, tool_x+i*2, base-1, "│", (106, 91, 82))
                put(canvas, tool_x+i*2, base-11, "⌒", (133, 111, 91))
            basket_x = min(w-12, right+13)
            rect(canvas, basket_x, base-7, basket_x+7, base-2, "▥", (106, 65, 43))
            for i in range(3):
                put(canvas, basket_x+1+i*2, base-8, "▰", (151, 91, 48))

            # A little armchair and sleeping cat, left foreground.
            chair_x, chair_y = max(1, left-16), base-8
            rect(canvas, chair_x, chair_y, chair_x+10, chair_y+7, "▓", (91, 42, 48))
            rect(canvas, chair_x+1, chair_y+1, chair_x+9, chair_y+5, "▒", (125, 54, 58))
            line(canvas, chair_x, chair_y+6, chair_x, chair_y+9, "│", (68, 43, 43))
            line(canvas, chair_x+9, chair_y+6, chair_x+9, chair_y+9, "│", (68, 43, 43))
            put(canvas, chair_x+3, chair_y+3, "猫", (205, 190, 174))
            put(canvas, chair_x+4, chair_y+3, "﹏", (205, 190, 174))

            # Floorboards and a patterned rug.
            floor_y = int(h*.78)
            rect(canvas, 0, floor_y, w, h-3, " ", (34, 27, 34))
            for yy in range(floor_y+1, h-3, 3):
                rect(canvas, 0, yy, w, yy+1, "━", (48, 35, 39))
            for xx in range(0, w, 13):
                rect(canvas, xx, floor_y, xx+1, h-3, "┊", (45, 34, 39))
            rug_l, rug_r = int(w*.23), int(w*.77)
            rug_y = h-7
            rect(canvas, rug_l, rug_y, rug_r, h-3, " ", (103, 39, 44))
            rect(canvas, rug_l+2, rug_y+1, rug_r-2, h-4, " ", (133, 53, 48))
            for xx in range(rug_l+3, rug_r-3, 4):
                put(canvas, xx, rug_y+2, "✦", (179, 91, 58))
                put(canvas, xx, rug_y+1, "·", (197, 113, 69))

            # Small atmospheric dust motes in the firelight.
            for _ in range(12):
                dx = random.randint(left-8, right+8)
                dy = random.randint(top, base)
                if random.random() < .3:
                    put(canvas, dx, dy, "·", (122, 78, 52))

            centered(canvas, 0, "C O Z Y   F I R E P L A C E", (190, 218, 232))
            centered(canvas, 1, "A LITTLE WARMTH ON A WINTER NIGHT", (111, 153, 178))
            centered(canvas, h-2, "Q / ESC  •  QUIT     ✦     STAY A LITTLE WHILE", (132, 145, 161))

            # Write a single complete frame, changing ANSI colour only when needed.
            output = ["\033[H"]
            for row in canvas:
                parts, active = [], None
                for glyph, color in row:
                    if color != active:
                        if color is None:
                            parts.append("\033[0m")
                        else:
                            parts.append(f"\033[38;2;{color[0]};{color[1]};{color[2]}m")
                        active = color
                    parts.append(glyph)
                parts.append("\033[0m")
                output.append("".join(parts))
            sys.stdout.write("\n".join(output))
            sys.stdout.flush()

            if key_pressed(reader):
                key = read_key(reader).lower()
                if key in ("q", "\x1b", "\x03"):
                    break
            time.sleep(1/24)

    except KeyboardInterrupt:
        pass
    finally:
        restore_terminal()

if __name__ == "__main__":
    main()
