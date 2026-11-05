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


"""SLEEPER TRAIN — a warm compartment moving through a snowy night."""
import random, math


class SleeperTrain:
    def __init__(self):
        self.rng=random.Random()
        self.trees=[]
        self.snow=[]
        self.size=None

    def draw(self,w,h,t):
        r=self.rng
        if self.size!=(w,h):
            self.size=(w,h)
            self.trees=[[r.uniform(0,w),r.uniform(.22,.67),r.uniform(.65,1.5)] for _ in range(max(20,w//2))]
            self.snow=[[r.randrange(w),r.randrange(h),r.uniform(.2,.8)] for _ in range(w//3)]
        c=[[(" ",None) for _ in range(w)] for _ in range(h)]
        # Warm wooden compartment.
        rect(c,0,2,w,h-3," ",(58,35,29))
        for x in range(2,w,8): rect(c,x,2,x+1,h-3,"│",(82,51,38))
        rect(c,2,3,w-2,4,"━",(130,83,51))
        # Large window with cold night beyond.
        xl,xr=int(w*.13),int(w*.87)
        yt,yb=int(h*.14),int(h*.68)
        rect(c,xl,yt,xr,yb," ",(8,24,47))
        # Moon and distant stars.
        mx,my=int(w*.72),int(h*.25)
        for dy in range(-2,3):
            for dx in range(-2,3):
                if dx*dx+dy*dy<=5: put(c,mx+dx,my+dy,"●",(207,216,213))
        for i in range(w//12):
            sx=(i*37+11)%w
            sy=4+(i*13)%max(5,int(h*.25))
            put(c,sx,sy,"·",(119,151,181))
        # Scrolling snowy forest parallax.
        speed=t*9
        for x,y,scale in self.trees:
            xx=int((x-speed*scale)%(xr-xl)+xl)
            base=int(y*h)
            th=int(4+scale*4)
            for yy in range(th):
                half=yy//2
                for dx in range(-half,half+1):
                    put(c,xx+dx,base-yy,"▲",(20,58+int(scale*12),68+int(scale*13)))
                if yy%3==0: put(c,xx,base-yy,"·",(150,181,194))
        # A distant cabin glides through the landscape periodically.
        cabin_x=int((w*1.15-(t*2.2)%(w*1.45)))
        if xl<cabin_x<xr-8:
            cy=int(h*.52)
            rect(c,cabin_x,cy-4,cabin_x+8,cy," ",(22,36,48))
            line(c,cabin_x-1,cy-4,cabin_x+4,cy-7,"/",(70,74,82))
            line(c,cabin_x+4,cy-7,cabin_x+9,cy-4,"\\",(70,74,82))
            put(c,cabin_x+2,cy-2,"▪",(240,174,91))
            put(c,cabin_x+6,cy-2,"▪",(240,174,91))
        # Snow crosses the window.
        for flake in self.snow:
            flake[0]-=flake[2]*.7
            if flake[0]<xl: flake[0]=xr-1; flake[1]=r.uniform(yt,yb)
            put(c,round(flake[0]),round(flake[1]),"·",(148,179,198))
        # Window frame and reflections.
        rect(c,xl-2,yt-1,xr+2,yt+1,"━",(139,91,57))
        rect(c,xl-2,yb-1,xr+2,yb+1,"━",(139,91,57))
        rect(c,xl-2,yt-1,xl,yb+1,"┃",(139,91,57))
        rect(c,xr,yt-1,xr+2,yb+1,"┃",(139,91,57))
        rect(c,(xl+xr)//2,yt,xl+(xr-xl)//2+1,yb,"│",(102,72,56))
        # Compartment table and steaming mug.
        table_y=int(h*.76)
        rect(c,int(w*.50)-8,table_y,w*.50+10,table_y+2,"━",(151,94,55))
        line(c,int(w*.50)-6,table_y+2,int(w*.50)-6,h-4,"│",(108,67,43))
        line(c,int(w*.50)+8,table_y+2,int(w*.50)+8,h-4,"│",(108,67,43))
        mx2,my2=int(w*.63),table_y-4
        rect(c,mx2,my2,mx2+6,my2+4,"▥",(188,146,105))
        put(c,mx2+6,my2+1,")",(188,146,105)); put(c,mx2+6,my2+2,")",(188,146,105))
        if int(t*2)%2==0:
            put(c,mx2+2,my2-1,"~",(157,176,169))
            put(c,mx2+3,my2-2,"~",(157,176,169))
        # Gentle sway represented by a shifting lamp glow and small vibration line.
        glow=(math.sin(t*1.2)+1)/2
        put(c,int(w*.25),int(h*.79),"✦",(int(155+glow*75),int(91+glow*45),35))
        text(c,0,"S L E E P E R   T R A I N",(211,187,154))
        text(c,1,"THROUGH THE SNOW, INTO THE NIGHT",(145,119,102))
        text(c,h-2,"Q / ESC  •  QUIT     ✦     THE JOURNEY CONTINUES",(147,125,108))
        return c

if __name__ == "__main__":
    scene=SleeperTrain()
    run(scene.draw)
