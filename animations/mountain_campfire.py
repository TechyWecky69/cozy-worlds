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


"""MOUNTAIN CAMPFIRE — stars, snow and a little fire in the hills."""
import random, math


class MountainCampfire:
    def __init__(self):
        self.rng=random.Random()
        self.snow=[]
        self.sparks=[]
        self.stars=[]
        self.size=None

    def draw(self,w,h,t):
        r=self.rng
        if self.size!=(w,h):
            self.size=(w,h)
            self.snow=[[r.randrange(w),r.randrange(h),r.uniform(.15,.65),r.random()*6] for _ in range(w//2)]
            self.stars=[(r.randrange(w),r.randrange(2,int(h*.4)),r.random()*6) for _ in range(w//10)]
        c=[[(" ",None) for _ in range(w)] for _ in range(h)]
        rect(c,0,2,w,h-3," ",(8,15,35))
        # Stars and moon.
        for x,y,p in self.stars:
            q=(math.sin(t*1.4+p)+1)/2
            put(c,x,y,"·" if q<.5 else "✦",(int(95+q*100),int(120+q*100),int(155+q*90)))
        mx,my=int(w*.78),int(h*.17)
        for dy in range(-2,3):
            for dx in range(-3,4):
                if dx*dx+dy*dy<=9 and (dx+2)**2+dy*dy>7:
                    put(c,mx+dx,my+dy,"●",(207,218,222))
        # Layered mountain silhouettes.
        ridge1=int(h*.49); ridge2=int(h*.55)
        for x in range(w):
            peak1=ridge1-int((math.sin(x*.035)+1)*h*.10)
            peak2=ridge2-int((math.sin(x*.022+2)+1)*h*.08)
            if peak1<h*.68:
                put(c,x,peak1,"▲",(37,54,82))
                for y in range(max(2,peak1+1),int(h*.72)):
                    if y>peak1+abs(math.sin(x*.08))*2: put(c,x,y,"▓",(21,37,64))
            if peak2<h*.72:
                put(c,x,peak2,"▲",(25,43,67))
        # Snow caps on mountain ridges.
        for x in range(w):
            if math.sin(x*.035)>.72:
                y=ridge1-int((math.sin(x*.035)+1)*h*.10)
                for dx in range(-2,3): put(c,x+dx,y+1,"·",(163,190,205))
        # Snowy ground.
        ground=int(h*.72)
        rect(c,0,ground,w,h-3," ",(17,31,47))
        for x in range(w):
            put(c,x,ground+int(1.5*math.sin(x*.05)),"_",(110,143,157))
        # Pine trees across the foreground.
        for tx, scale in [(int(w*.08),1),(int(w*.18),.8),(int(w*.87),1),(int(w*.94),.8)]:
            base=ground+2; height=int(8*scale)
            for yy in range(height):
                half=yy//2
                for dx in range(-half,half+1):
                    put(c,tx+dx,base-yy,"▲",(20,69+yy*2,69+yy))
                if yy%3==0: put(c,tx,base-yy,"·",(177,203,211))
        # Small tent.
        tx,ty=int(w*.27),ground-1
        line(c,tx-5,ty,tx,ty-7,"/",(145,108,91))
        line(c,tx,ty-7,tx+6,ty,"\\",(145,108,91))
        line(c,tx-5,ty,tx+6,ty,"_",(145,108,91))
        line(c,tx,ty-7,tx,ty,"│",(177,130,92))
        put(c,tx+2,ty-2,"·",(226,173,107))
        # Campfire stones, logs and animated flame.
        fx,fy=int(w*.57),ground+1
        for dx in range(-6,7,3): put(c,fx+dx,fy,"●",(86,94,101))
        line(c,fx-5,fy-1,fx+5,fy-1,"━",(91,56,40))
        for dx in range(-3,4):
            height=int((3+2*math.sin(t*6+dx*.8)+2*math.sin(t*3+dx))*max(.25,1-abs(dx)/5))
            for yy in range(max(1,height)):
                put(c,fx+dx,fy-2-yy,r.choice(["▲","▴"," "]),r.choice([(185,55,24),(238,105,28),(255,178,67)]))
        if r.random()<.7:
            self.sparks.append([fx+r.uniform(-3,3),fy-4,r.uniform(.3,.8)])
        for s in self.sparks[:]:
            s[1]-=s[2]
            if s[1]<ground-15: self.sparks.remove(s)
            else: put(c,round(s[0]),round(s[1]),"·",(255,177,83))
        # Gentle snowfall.
        for flake in self.snow:
            flake[1]+=flake[2]; flake[0]+=math.sin(t+flake[3])*.12
            if flake[1]>=h-3: flake[1]=2; flake[0]=r.randrange(w)
            put(c,round(flake[0]),round(flake[1]),"·",(157,184,201))
        text(c,0,"M O U N T A I N   C A M P F I R E",(176,207,221))
        text(c,1,"A SMALL FIRE UNDER THE WINTER SKY",(101,145,172))
        text(c,h-2,"Q / ESC  •  QUIT     ✦     SNOW FALLS QUIETLY",(104,143,163))
        return c

if __name__ == "__main__":
    scene=MountainCampfire()
    run(scene.draw)
