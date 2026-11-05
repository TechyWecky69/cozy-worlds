#!/usr/bin/env python3
"""
COZY WORLDS LAUNCHER

Place this file in the directory containing your standalone animation .py files.
A sibling directory named "fancy" can contain the multi-file fireplace project.

Controls:
    UP / DOWN   Select an animation
    ENTER/SPACE Run the selected animation
    F           Toggle animations inside ./fancy on or off
    R           Rescan files
    Q / ESC     Quit
"""
import curses
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
FANCY_DIR = ROOT / "fancy"
SKIP_DIRS = {".venv", "venv", "__pycache__", ".git", "node_modules"}


def discover_animations(include_fancy):
    """Find root-level scripts and, optionally, Python scripts below ./fancy."""
    found = []

    for path in ROOT.glob("*.py"):
        if path.resolve() != Path(__file__).resolve():
            found.append((path, "MAIN"))

    if include_fancy and FANCY_DIR.is_dir():
        for path in FANCY_DIR.rglob("*.py"):
            if any(part in SKIP_DIRS for part in path.parts):
                continue
            found.append((path, "FANCY"))

    return sorted(found, key=lambda item: (item[1] == "FANCY", item[0].name.lower(),
                                           str(item[0]).lower()))


def display_name(path):
    if path.parent == ROOT:
        return path.stem.replace("_", " ").replace("-", " ").title()
    try:
        return str(path.relative_to(ROOT)).replace(os.sep, "  /  ")
    except ValueError:
        return path.name


def safe_addstr(win, y, x, text, attr=0):
    """Avoid curses errors when text reaches the terminal's lower-right cell."""
    height, width = win.getmaxyx()
    if y < 0 or y >= height or x >= width:
        return
    try:
        win.addnstr(y, max(0, x), str(text), max(0, width - max(0, x) - 1), attr)
    except curses.error:
        pass


def draw(stdscr, items, selected, fancy_enabled, message=""):
    stdscr.erase()
    height, width = stdscr.getmaxyx()

    title_attr = curses.color_pair(1) | curses.A_BOLD
    muted_attr = curses.color_pair(2)
    selected_attr = curses.color_pair(3) | curses.A_BOLD
    fancy_attr = curses.color_pair(4)

    safe_addstr(stdscr, 1, 2, "C O Z Y   W O R L D S", title_attr)
    safe_addstr(stdscr, 2, 2, "ANIMATION LIBRARY", muted_attr)

    toggle_label = "[F] Fancy folder: " + ("ON" if fancy_enabled else "OFF")
    safe_addstr(stdscr, 1, max(2, width - len(toggle_label) - 3),
                toggle_label, fancy_attr if fancy_enabled else muted_attr)

    safe_addstr(stdscr, 4, 2, "Choose an animation", curses.A_BOLD)
    safe_addstr(stdscr, 5, 2, "↑ / ↓  Select     ENTER / SPACE  Run     F  Toggle fancy     R  Rescan",
                muted_attr)

    list_top = 7
    list_bottom = max(list_top + 1, height - 4)
    visible = max(1, list_bottom - list_top)
    start = 0
    if selected >= visible:
        start = selected - visible + 1

    if not items:
        safe_addstr(stdscr, list_top + 1, 4, "No Python animations found.", muted_attr)
        safe_addstr(stdscr, list_top + 2, 4, "Put .py files beside launcher.py or enable the fancy folder.", muted_attr)
    else:
        for screen_row, index in enumerate(range(start, min(len(items), start + visible))):
            path, group = items[index]
            prefix = " > " if index == selected else "   "
            tag = "[FANCY]" if group == "FANCY" else "[LOCAL]"
            label = f"{prefix}{display_name(path)}"
            attr = selected_attr if index == selected else curses.A_NORMAL
            safe_addstr(stdscr, list_top + screen_row, 3, label, attr)
            tag_x = min(width - len(tag) - 3, max(4, width - len(tag) - 4))
            safe_addstr(stdscr, list_top + screen_row, tag_x, tag,
                        fancy_attr if group == "FANCY" else muted_attr)

    safe_addstr(stdscr, height - 2, 2,
                message or f"{len(items)} animation(s) found    Q / ESC  Quit",
                muted_attr)
    stdscr.refresh()


def run_animation(stdscr, path):
    """Leave curses mode cleanly, run the chosen script, then restore the menu."""
    curses.def_prog_mode()
    curses.endwin()
    print(f"\nLaunching: {path.relative_to(ROOT)}\n")
    try:
        result = subprocess.run([sys.executable, str(path)], cwd=str(path.parent))
        if result.returncode:
            print(f"\nAnimation exited with status {result.returncode}.")
    except OSError as exc:
        print(f"\nCould not launch animation: {exc}")
    input("\nPress Enter to return to Cozy Worlds Launcher...")
    stdscr.clear()
    stdscr.refresh()


def app(stdscr):
    curses.curs_set(0)
    stdscr.keypad(True)
    curses.start_color()
    curses.use_default_colors()
    curses.init_pair(1, curses.COLOR_CYAN, -1)
    curses.init_pair(2, curses.COLOR_BLUE, -1)
    curses.init_pair(3, curses.COLOR_WHITE, curses.COLOR_BLUE)
    curses.init_pair(4, curses.COLOR_YELLOW, -1)

    fancy_enabled = False
    items = discover_animations(fancy_enabled)
    selected = 0
    message = ""

    while True:
        if items:
            selected = max(0, min(selected, len(items) - 1))
        else:
            selected = 0
        draw(stdscr, items, selected, fancy_enabled, message)
        message = ""

        key = stdscr.getch()
        if key in (ord("q"), ord("Q"), 27):
            break
        elif key in (curses.KEY_UP, ord("k")):
            selected = max(0, selected - 1)
        elif key in (curses.KEY_DOWN, ord("j")):
            selected = min(max(0, len(items) - 1), selected + 1)
        elif key in (ord("f"), ord("F")):
            fancy_enabled = not fancy_enabled
            items = discover_animations(fancy_enabled)
            selected = min(selected, max(0, len(items) - 1))
            message = "Fancy folder enabled." if fancy_enabled else "Fancy folder hidden."
        elif key in (ord("r"), ord("R")):
            items = discover_animations(fancy_enabled)
            selected = min(selected, max(0, len(items) - 1))
            message = "Animation list refreshed."
        elif key in (curses.KEY_ENTER, 10, 13, ord(" ")):
            if items:
                run_animation(stdscr, items[selected][0])
                message = "Back in the animation library."


def main():
    if not sys.stdin.isatty() or not sys.stdout.isatty():
        print("Please run the launcher inside a terminal.")
        return 1
    try:
        curses.wrapper(app)
    except KeyboardInterrupt:
        pass
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
