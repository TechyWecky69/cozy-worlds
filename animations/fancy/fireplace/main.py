#!/usr/bin/env python3
"""Cozy Worlds — terminal-native animated environments."""
import argparse
import os
import sys
import time
import shutil
import select
import termios
import tty
from renderer import Renderer
from scenes.fireplace import Fireplace

FPS = 24

def read_key(fd):
    """Read one key without blocking; recognise common terminal escape sequences."""
    if not select.select([fd], [], [], 0)[0]:
        return None
    data = os.read(fd, 32)
    if data in (b'\x1b', b'\x1b\x1b'):
        # Give arrow-key bytes a brief chance to arrive.
        time.sleep(0.008)
        while select.select([fd], [], [], 0)[0]:
            data += os.read(fd, 16)
    if data.startswith(b'\x1b['):
        return {"\x1b[A": "UP", "\x1b[B": "DOWN",
                "\x1b[C": "RIGHT", "\x1b[D": "LEFT"}.get(data.decode("ascii", "ignore"))
    if data in (b'\x1b', b'\x03'):
        return "QUIT"
    try:
        return data.decode("utf-8", "ignore").lower()
    except Exception:
        return None

def main():
    parser = argparse.ArgumentParser(description="Cozy Worlds — Fireplace edition")
    parser.add_argument("--fps", type=int, default=FPS, help="target frame rate (default: 24)")
    args = parser.parse_args()
    if not sys.stdin.isatty() or not sys.stdout.isatty():
        print("Cozy Worlds needs to run in an interactive terminal.")
        return 1

    fd = sys.stdin.fileno()
    old = termios.tcgetattr(fd)
    renderer = Renderer()
    scene = Fireplace()
    paused = False
    show_ui = True
    start = time.monotonic()
    frame_time = 1.0 / max(1, min(args.fps, 60))
    last_frame = 0.0
    try:
        tty.setcbreak(fd)
        sys.stdout.write("\x1b[?1049h\x1b[?25l\x1b[2J\x1b[H")
        sys.stdout.flush()
        while True:
            now = time.monotonic()
            key = read_key(fd)
            if key in ("q", "QUIT"):
                break
            elif key == " ":
                paused = not paused
            elif key == "h":
                show_ui = not show_ui
            if not paused:
                scene.update(now - start, now - last_frame if last_frame else frame_time)
            if now - last_frame >= frame_time:
                width, height = shutil.get_terminal_size((100, 32))
                frame = scene.render(max(50, width), max(16, height - (2 if show_ui else 0)))
                if show_ui:
                    renderer.overlay(frame, width, height, paused)
                renderer.present(frame)
                last_frame = now
            # Small sleep prevents a busy loop while keeping input responsive.
            time.sleep(max(0.001, min(0.006, frame_time / 5)))
    except KeyboardInterrupt:
        pass
    finally:
        sys.stdout.write("\x1b[0m\x1b[?25h\x1b[?1049l")
        sys.stdout.flush()
        termios.tcsetattr(fd, termios.TCSADRAIN, old)
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
