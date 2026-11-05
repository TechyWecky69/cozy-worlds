"""Small true-colour half-block terminal renderer."""
import sys

class Renderer:
    def __init__(self):
        self.last = None

    def overlay(self, frame, width, height, paused):
        # Header/footer are drawn into the top and bottom pixel rows.
        title = " COZY WORLDS  /  01 — FIREPLACE "
        hint = " 1 FIREPLACE   SPACE PAUSE   H UI   Q QUIT "
        status = " PAUSED " if paused else " LIVE "
        frame.text(1, 0, title, (244, 205, 143))
        frame.text(max(1, width - len(hint) - 2), 0, hint, (142, 155, 171))
        frame.text(1, frame.h - 2, " A quiet cabin, long after sunset ", (172, 142, 112))
        frame.text(max(1, width - len(status) - 2), frame.h - 2, status,
                   (255, 191, 105) if paused else (112, 178, 139))

    def present(self, frame):
        out = ["\x1b[H"]
        for y in range(0, frame.h - 1, 2):
            for x in range(frame.w):
                top = frame.pixels[y][x]
                bottom = frame.pixels[y + 1][x]
                out.append(f"\x1b[38;2;{top[0]};{top[1]};{top[2]}m"
                           f"\x1b[48;2;{bottom[0]};{bottom[1]};{bottom[2]}m▀")
            out.append("\x1b[0m\n")
        sys.stdout.write("".join(out))
        sys.stdout.flush()

class Frame:
    def __init__(self, width, terminal_rows, bg=(8, 10, 18)):
        self.w = width
        self.h = terminal_rows * 2
        self.pixels = [[bg for _ in range(width)] for _ in range(self.h)]

    def set(self, x, y, colour):
        if 0 <= x < self.w and 0 <= y < self.h:
            self.pixels[y][x] = tuple(max(0, min(255, int(v))) for v in colour)

    def rect(self, x1, y1, x2, y2, colour):
        for y in range(max(0, int(y1)), min(self.h, int(y2))):
            row = self.pixels[y]
            for x in range(max(0, int(x1)), min(self.w, int(x2))):
                row[x] = colour

    def text(self, x, y, value, colour):
        # Text is placed on both pixel rows so it remains legible at half-block scale.
        for i, ch in enumerate(value):
            xx = x + i
            if 0 <= xx < self.w and 0 <= y < self.h:
                self.set(xx, y, colour)
                if y + 1 < self.h:
                    self.set(xx, y + 1, colour)
