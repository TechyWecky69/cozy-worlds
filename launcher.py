#!/usr/bin/env python3
"""Small terminal menu for the Cozy Worlds standalone Python animations."""
import curses
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
ANIMATIONS = ROOT / "animations"


def find_animations():
    if not ANIMATIONS.is_dir():
        return []
    return sorted(
        (p for p in ANIMATIONS.glob("*.py") if p.name != "__init__.py"),
        key=lambda p: p.stem.lower(),
    )


def display_name(path):
    return path.stem.replace("_", " ").replace("-", " ").title()


def menu(stdscr):
    curses.curs_set(0)
    stdscr.keypad(True)
    selected = 0
    message = "Choose an animation · Enter to play · Q to quit · R to rescan"

    while True:
        items = find_animations()
        stdscr.erase()
        height, width = stdscr.getmaxyx()
        title = "COZY WORLDS"
        stdscr.addstr(1, max(0, (width - len(title)) // 2), title, curses.A_BOLD)
        stdscr.addstr(3, 2, message[:max(0, width - 4)])

        if not items:
            stdscr.addstr(5, 2, "No animations found in the animations/ folder.")
            stdscr.addstr(6, 2, "Add your standalone .py animation files there.")
        else:
            selected = min(selected, len(items) - 1)
            visible = max(1, height - 7)
            start = max(0, min(selected - visible + 1, len(items) - visible))
            for row, path in enumerate(items[start:start + visible]):
                y = 5 + row
                label = f"  {display_name(path)}"
                if start + row == selected:
                    stdscr.addstr(y, 2, label[:max(0, width - 4)], curses.A_REVERSE)
                else:
                    stdscr.addstr(y, 2, label[:max(0, width - 4)])
        stdscr.refresh()

        key = stdscr.getch()
        if key in (ord("q"), ord("Q"), 27):
            return
        if key in (ord("r"), ord("R")):
            continue
        if key in (curses.KEY_UP, ord("k")) and items:
            selected = (selected - 1) % len(items)
        elif key in (curses.KEY_DOWN, ord("j")) and items:
            selected = (selected + 1) % len(items)
        elif key in (10, 13, curses.KEY_ENTER, ord(" ")) and items:
            chosen = items[selected]
            curses.endwin()
            try:
                subprocess.run([sys.executable, str(chosen)], check=False)
            except KeyboardInterrupt:
                pass
            stdscr.clear()
            stdscr.refresh()


if __name__ == "__main__":
    if not ANIMATIONS.exists():
        print(f"Missing animation folder: {ANIMATIONS}")
        raise SystemExit(1)
    try:
        curses.wrapper(menu)
    except KeyboardInterrupt:
        pass
