#!/usr/bin/env python3
"""Cozy Worlds terminal animation launcher."""
import curses
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
ANIMATIONS = ROOT / "animations"
BIN_LINK = Path.home() / ".local" / "bin" / "cozy"
INSTALL_DIR = Path.home() / ".local" / "share" / "cozy-worlds"


def uninstall():
    """Remove the Cozy Worlds launcher and its installed files."""
    print("Thanks for spending some time in Cozy Worlds.")
    print("Preparing a little more room on your system...")

    # Only remove the command link if it points to this Cozy Worlds launcher.
    try:
        if BIN_LINK.is_symlink():
            target = BIN_LINK.resolve()
            if target == Path(__file__).resolve():
                BIN_LINK.unlink()
        elif BIN_LINK.exists():
            print(f"Leaving {BIN_LINK} untouched because it is not a symlink.")
    except OSError as exc:
        print(f"Couldn't remove the launcher command: {exc}")

    # The running Python process can safely finish after its own file is removed.
    try:
        if INSTALL_DIR.exists():
            shutil.rmtree(INSTALL_DIR)
    except OSError as exc:
        print(f"Couldn't completely remove {INSTALL_DIR}: {exc}")
        print("You can remove that folder manually once Cozy Worlds has exited.")
        return 1

    print()
    print("Cozy Worlds has been uninstalled.")
    print("Thanks for visiting. May your terminal always feel cosy. ☕")
    return 0


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
    if len(sys.argv) > 1:
        if sys.argv[1] in ("-uninstall", "--uninstall"):
            raise SystemExit(uninstall())
        print("Usage: cozy [-uninstall]")
        raise SystemExit(2)

    if not ANIMATIONS.exists():
        print(f"Missing animation folder: {ANIMATIONS}")
        raise SystemExit(1)
    try:
        curses.wrapper(menu)
    except KeyboardInterrupt:
        pass
