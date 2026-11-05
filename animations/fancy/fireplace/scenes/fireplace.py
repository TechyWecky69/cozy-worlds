"""A layered, continuously evolving pixel-art fireplace."""
import math
import random
from renderer import Frame

def mix(a, b, t):
    t = max(0.0, min(1.0, t))
    return tuple(int(a[i] * (1-t) + b[i] * t) for i in range(3))

class Fireplace:
    def __init__(self):
        self.rng = random.Random()
        self.sparks = []
        self.phase = 0.0
        self.last_spark = 0.0

    def update(self, elapsed, dt):
        self.phase += min(dt, 0.08)
        # A few embers drift upward, then fade.
        if self.rng.random() < 0.23:
            self.sparks.append([self.rng.uniform(-0.8, 0.8), 0.0,
                                self.rng.uniform(0.5, 1.6), self.rng.uniform(0.5, 1.3)])
        for p in self.sparks:
            p[1] += p[2] * dt
            p[0] += math.sin(elapsed * 2 + p[1] * 4) * dt * 0.22
            p[3] -= dt
        self.sparks = [p for p in self.sparks if p[1] < 1.0 and p[3] > 0]

    def render(self, width, terminal_rows):
        f = Frame(width, terminal_rows, (10, 12, 20))
        w, h = f.w, f.h
        rng = self.rng
        t = self.phase
        # Back wall: midnight blue, with warm light pooling around the hearth.
        for y in range(h):
            for x in range(w):
                nx = (x - w*.5)/(w*.55)
                ny = (y - h*.63)/(h*.55)
                glow = max(0, 1 - math.sqrt(nx*nx + ny*ny)) ** 2
                base = (12 + 13*glow, 16 + 8*glow, 27 + 2*glow)
                f.set(x, y, tuple(int(v) for v in base))
        # Timber wall panels and floor.
        f.rect(0, int(h*.79), w, h, (39, 25, 23))
        for x in range(0, w, max(8, w//13)):
            f.rect(x, 0, x+1, int(h*.79), (20, 22, 30))
        floor_y = int(h*.80)
        for y in range(floor_y, h, 5):
            f.rect(0, y, w, y+1, (48, 29, 24))
        for x in range(0, w, 17):
            f.rect(x + int(4*math.sin(t+x)), floor_y, x+1, h, (60, 36, 27))
        # Side shelves / framed pictures add depth without clutter.
        f.rect(int(w*.10), int(h*.20), int(w*.27), int(h*.22), (76, 49, 37))
        f.rect(int(w*.11), int(h*.205), int(w*.26), int(h*.215), (18, 25, 34))
        f.rect(int(w*.73), int(h*.24), int(w*.90), int(h*.26), (91, 61, 42))
        f.rect(int(w*.735), int(h*.19), int(w*.895), int(h*.245), (24, 34, 42))
        # Fireplace stone surround.
        left, right = int(w*.29), int(w*.71)
        top, bottom = int(h*.30), int(h*.79)
        f.rect(left-3, top-2, right+3, bottom, (91, 76, 67))
        f.rect(left, top, right, bottom, (130, 108, 91))
        # Stone seams.
        for yy in range(top+5, bottom, max(5, h//13)):
            f.rect(left-2, yy, right+2, yy+1, (78, 67, 62))
        for xx in range(left+5, right, max(7, w//12)):
            f.rect(xx, top, xx+1, bottom, (104, 88, 77))
        # Dark firebox and inner soot gradient.
        ix1, ix2 = left+5, right-5
        iy1, iy2 = top+7, bottom-5
        f.rect(ix1, iy1, ix2, iy2, (10, 9, 13))
        # Hearth lip and glowing coal bed.
        f.rect(left-5, bottom-4, right+5, bottom+2, (83, 65, 57))
        f.rect(ix1+2, iy2-7, ix2-2, iy2-2, (104, 30, 15))
        for x in range(ix1+3, ix2-3, 3):
            c = rng.choice([(255, 91, 20), (255, 139, 32), (177, 42, 18)])
            f.set(x, iy2-5+rng.randrange(3), c)
        # Logs, with bark highlights.
        log_y = iy2-8
        f.rect(ix1+8, log_y, ix2-8, log_y+4, (63, 35, 25))
        for k in range(0, ix2-ix1-20, 9):
            f.rect(ix1+10+k, log_y, ix1+12+k, log_y+1, (111, 61, 35))
        # Flame field: many independently varying tapered tongues.
        fire_w = ix2-ix1-8
        for x in range(ix1+4, ix2-4):
            u = (x-(ix1+4))/max(1, fire_w)
            flick = math.sin(t*7 + x*.31) * 2.3 + math.sin(t*3.7+x*.13)*1.8
            height = (h*.24) * (0.42 + 0.58*math.sin(math.pi*u)**.65)
            height *= 0.83 + 0.17*math.sin(t*5+x*.19)
            for yy in range(int(iy2-9-height), iy2-8):
                rel = (iy2-8-yy)/max(1, height)
                wave = math.sin(t*8 + x*.22 + rel*5)*1.8
                edge = abs((x - (ix1+fire_w*.5)) / (fire_w*.5))
                if rel < 0.92 and abs(x - (ix1+fire_w*.5) + wave) < fire_w*.52*(1-rel*.45):
                    noise = rng.random()
                    if rel < .24:
                        col = (255, 235, 150) if noise > .88 else (255, 173, 55)
                    elif rel < .55:
                        col = (255, 105+int(50*noise), 22)
                    else:
                        col = (150+int(80*noise), 35+int(30*noise), 15)
                    if noise > .97:
                        col = (255, 245, 195)
                    f.set(x, yy, col)
        # A warm halo around the firebox, rendered as soft light.
        for y in range(top, bottom):
            for x in range(left-8, right+8):
                if 0 <= x < w:
                    dx = abs(x-w*.5)/(w*.28)
                    dy = abs(y-h*.62)/(h*.35)
                    glow = max(0, 1-(dx*dx+dy*dy))*.12
                    old = f.pixels[y][x]
                    f.set(x, y, (old[0]+int(95*glow), old[1]+int(40*glow), old[2]+int(8*glow)))
        # Mantel: thick timber slab and a fine amber edge.
        my = int(h*.285)
        f.rect(int(w*.24), my, int(w*.76), my+5, (91, 53, 35))
        f.rect(int(w*.24), my, int(w*.76), my+1, (164, 105, 65))
        f.rect(int(w*.25), my+5, int(w*.75), my+6, (45, 29, 26))
        # Stockings hang from the mantel; small blocky silhouettes.
        for i, sx in enumerate((.39, .50, .61)):
            x = int(w*sx)
            f.rect(x, my+6, x+1, my+13, (186, 151, 119))
            col = [(139, 42, 42), (42, 83, 105), (117, 48, 66)][i]
            f.rect(x-2, my+13, x+3, my+22, col)
            f.rect(x-2, my+21, x+4, my+26, col)
            f.rect(x+1, my+24, x+6, my+27, col)
            f.rect(x-2, my+13, x+3, my+15, (225, 211, 184))
        # Rug in front of the hearth.
        rug_y = int(h*.86)
        f.rect(int(w*.27), rug_y, int(w*.73), min(h, rug_y+7), (93, 39, 38))
        f.rect(int(w*.29), rug_y+1, int(w*.71), rug_y+6, (125, 55, 48))
        f.rect(int(w*.31), rug_y+2, int(w*.69), rug_y+5, (94, 42, 42))
        for x in range(int(w*.30), int(w*.70), 5):
            f.rect(x, rug_y, x+1, rug_y+7, (151, 83, 61))
        # Floating sparks, softly fading.
        for sx, sy, speed, life in self.sparks:
            x = int(w*.5 + sx*w*.18)
            y = int(iy2 - 10 - sy*h*.48)
            if 0 <= x < w and 0 <= y < h:
                f.set(x, y, (255, 175, 69) if life > .5 else (178, 77, 30))
                if x+1 < w and rng.random() < .3:
                    f.set(x+1, y, (255, 117, 39))
        # Small candles on mantel ends.
        for x in (int(w*.31), int(w*.68)):
            f.rect(x, my-5, x+2, my, (215, 184, 129))
            f.set(x, my-7-int(1.5*math.sin(t*8+x)), (255, 205, 105))
        return f
