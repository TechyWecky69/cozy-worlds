#!/usr/bin/env python3
"""A small standard-style Cozy Worlds terminal animation. Q / Esc quits."""
import math
import os
import random
import select
import shutil
import sys
import termios
import time
import tty

def put(canvas, x, y, ch, color):
    h, w = len(canvas), len(canvas[0])
    x, y = int(x), int(y)
    if 0 <= x < w and 0 <= y < h:
        canvas[y][x] = (ch, color)

def line(canvas, x1, y1, x2, y2, ch, color):
    steps = max(abs(x2-x1), abs(y2-y1), 1)
    for i in range(steps + 1):
        t = i / steps
        put(canvas, round(x1+(x2-x1)*t), round(y1+(y2-y1)*t), ch, color)

def rect(canvas, x1, y1, x2, y2, ch, color):
    h, w = len(canvas), len(canvas[0])
    for y in range(max(0, int(y1)), min(h, int(y2))):
        for x in range(max(0, int(x1)), min(w, int(x2))):
            put(canvas, x, y, ch, color)

def text(canvas, y, value, color):
    x = (len(canvas[0])-len(value))//2
    for i, ch in enumerate(value):
        put(canvas, x+i, y, ch, color)

def encode(canvas):
    rows = []
    for row in canvas:
        parts, active = [], None
        for ch, color in row:
            if color != active:
                if color is None:
                    parts.append("\033[0m")
                else:
                    parts.append(f"\033[38;2;{color[0]};{color[1]};{color[2]}m")
                active = color
            parts.append(ch)
        parts.append("\033[0m")
        rows.append("".join(parts))
    return "\n".join(rows)

def run(draw):
    if not sys.stdin.isatty() or not sys.stdout.isatty():
        print("Please run this animation inside a terminal.")
        return
    fd = sys.stdin.fileno()
    old = termios.tcgetattr(fd)
    start = time.monotonic()
    try:
        tty.setcbreak(fd)
        sys.stdout.write("\033[?1049h\033[?25l\033[2J")
        sys.stdout.flush()
        while True:
            now = time.monotonic() - start
            size = shutil.get_terminal_size((100, 32))
            w, h = max(60, size.columns), max(22, size.lines)
            frame = draw(w, h, now)
            sys.stdout.write("\033[H" + encode(frame))
            sys.stdout.flush()
            ready, _, _ = select.select([sys.stdin], [], [], 0)
            if ready:
                key = os.read(fd, 32)
                if key in (b"q", b"Q", b"\x1b", b"\x03"):
                    break
                if key.startswith(b"\x1b["):
                    # Consume arrow-key sequences; these scenes do not need them.
                    pass
            time.sleep(1/24)
    except KeyboardInterrupt:
        pass
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old)
        sys.stdout.write("\033[0m\033[?25h\033[?1049l")
        sys.stdout.flush()


"""RAINY WINDOW — a quiet rainy evening, in simple POLARIS-style terminal art."""
import random, math


class RainyWindow:
    def __init__(self):
        self.rng = random.Random()
        self.drops = []
        self.steam = []
        self.city = []
        self.size = None

    def draw(self, w, h, t):
        r = self.rng
        if self.size != (w,h):
            self.size = (w,h)
            self.drops = [[r.uniform(2,w-3), r.uniform(3,h*.65), r.uniform(.35,1.25), r.randint(1,3)] for _ in range(w//2)]
            self.city = [(x, r.randint(int(h*.27),int(h*.43)), r.random()) for x in range(2,w-2,4)]
            self.steam = []
        c = [[(" ", None) for _ in range(w)] for _ in range(h)]
        rect(c,0,2,w,h-3," ",(20,24,39))
        # Warm room wall and dark blue window glass.
        rect(c,2,4,w-2,h-7," ",(12,31,53))
        # Distant skyline with scattered lit windows.
        ground = int(h*.57)
        for x, top, seed in self.city:
            rect(c,x,top,x+3,ground," ",(12,25,43))
            for yy in range(top+2,ground-1,3):
                if (math.sin(x*3+yy*7+seed*9) > .48):
                    put(c,x+1,yy,"·",(180,154,112))
        for x in range(3,w-3):
            put(c,x,ground,"─",(48,72,91))
        # Rain trails: several speeds and lengths.
        for d in self.drops:
            d[1] += d[2]
            if d[1] > ground-1:
                d[0] = r.uniform(3,w-4); d[1] = r.uniform(4,8); d[2] = r.uniform(.35,1.25)
            put(c,d[0],d[1],"│" if d[3]>1 else "·",(76,132,165))
            if d[3]>1: put(c,d[0],d[1]-1,"·",(48,96,131))
        # Occasional soft lightning pulse.
        flash = max(0, 1-abs((t%31)-15.5)/.45) if (t%31)<16 else 0
        if flash:
            for x in range(3,w-3):
                for y in range(4,ground):
                    if r.random()<.025:
                        put(c,x,y,"·",(int(110+flash*90),int(155+flash*80),int(190+flash*60)))
        # Window frame and crossbars.
        rect(c,1,3,w-1,4,"━",(95,70,57)); rect(c,1,h-8,w-1,h-7,"━",(95,70,57))
        rect(c,1,3,2,h-7,"┃",(95,70,57)); rect(c,w-2,3,w-1,h-7,"┃",(95,70,57))
        rect(c,w//2,4,w//2+1,h-8,"│",(79,68,66))
        rect(c,2,int(h*.31),w-2,int(h*.31)+1,"─",(79,68,66))
        # Windowsill and steaming mug.
        sill = h-8
        rect(c,0,sill,w,sill+2,"━",(124,79,52))
        mx,my = int(w*.70),sill-4
        rect(c,mx,my,mx+7,my+4," ",(177,137,104))
        rect(c,mx,my,mx+6,my+3,"▥",(185,146,112))
        put(c,mx+7,my+1,")",(185,146,112))
        put(c,mx+7,my+2,")",(185,146,112))
        if r.random()<.5: self.steam.append([mx+3+r.uniform(-1,1),my-1,0])
        for s in self.steam[:]:
            s[1]-=.35; s[0]+=math.sin(t*2+s[2])*.12; s[2]+=.1
            if s[1]<my-7: self.steam.remove(s)
            else: put(c,round(s[0]),round(s[1]),"~",(126,157,163))
        text(c,0,"R A I N Y   W I N D O W",(186,211,224))
        text(c,1,"A QUIET EVENING IN THE CITY",(104,151,180))
        text(c,h-2,"Q / ESC  •  QUIT     ✦     RAIN AGAINST THE GLASS",(104,143,163))
        return c

if __name__ == "__main__":
    scene=RainyWindow()
    run(scene.draw)
