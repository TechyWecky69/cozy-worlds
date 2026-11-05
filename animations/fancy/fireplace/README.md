# Cozy Worlds — Fireplace Edition

A terminal-native, true-colour animated fireplace for Linux. The first scene of the
Cozy Worlds collection is implemented as a lightweight Python application; it uses
only the standard library and renders with 24-bit ANSI colours and Unicode half-blocks.

## Requirements

- Python 3.9+
- A terminal with ANSI escape-sequence and 24-bit colour support (kitty, foot,
  WezTerm, GNOME Terminal, Konsole, Alacritty and most modern terminals work well)
- A terminal at least 80 columns wide and 24 rows high is recommended

## Arch Linux / CachyOS

```bash
sudo pacman -S --needed python
cd cozy-worlds
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python main.py
```

There are no third-party Python dependencies, so `pip install -r requirements.txt`
is intentionally quick.

## Fullscreen

The application switches to the terminal's alternate screen automatically. For a
clean, immersive view, maximise the terminal window (or use your terminal's fullscreen
shortcut, commonly `F11`) before running `python main.py`.

Optional frame-rate override:

```bash
python main.py --fps 24
```

## Controls

| Key | Action |
|---|---|
| `SPACE` | Pause / resume |
| `H` | Hide / show interface |
| `Q` or `ESC` | Quit |
| `CTRL+C` | Quit safely |

The terminal is restored on exit, including the cursor and previous screen.

## Project layout

```text
cozy-worlds/
├── main.py
├── renderer.py
├── scenes/
│   ├── __init__.py
│   └── fireplace.py
├── requirements.txt
└── README.md
```

Each environment lives in its own module under `scenes/`, ready for additional scenes.
