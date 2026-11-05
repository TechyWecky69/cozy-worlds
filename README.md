# Cozy Worlds

**A collection of cosy, animated worlds for your terminal.**

Cozy Worlds brings quiet scenes to your Linux terminal using lightweight, standalone Python animations and ANSI true-colour. Settle into a rainy evening, watch a campfire flicker beneath the mountains, or enjoy a moonlit pond — all without opening a separate graphics application.

## Scenes

Cozy Worlds currently includes:

- **Fireplace** — a warm, flickering fire.
- **Rainy Window** — rainfall against a window, with a cosy indoor view.
- **Mountain Campfire** — a campfire beneath a night sky, surrounded by mountains.
- **Moonlit Pond** — a peaceful pond beneath the moon.
- **Sleeper Train** — a quiet train compartment passing through a snowy night.

## Requirements

- Linux terminal with ANSI true-colour (24-bit) support
- Python 3
- Git (for the installer)

No Python packages need to be installed for the standard animations or launcher.

## Install

Run the following command:

```bash
curl -fsSL https://raw.githubusercontent.com/TechyWecky69/cozy-worlds/main/install.sh | bash
```

The installer downloads Cozy Worlds to:

```text
~/.local/share/cozy-worlds
```

It also creates a `cozy` command in:

```text
~/.local/bin
```

If `cozy` is not found after installation, add `~/.local/bin` to your `PATH`:

```bash
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc
```

If you use Zsh, add that line to `~/.zshrc` instead.

## Launch

Start the menu with:

```bash
cozy
```

Use the arrow keys to select a scene, then press **Enter** to play it.

### Launcher controls

| Key | Action |
|---|---|
| Up / Down | Select a scene |
| Enter / Space | Play selected scene |
| R | Rescan the animations folder |
| Q / Esc | Quit the launcher |

Individual animations can also be run directly:

```bash
python3 ~/.local/share/cozy-worlds/animations/moonlit_pond.py
```

The animation itself can be exited using **Q** or **Esc**.

## Update

Run the installation command again. If Cozy Worlds is already installed, the installer updates it from the GitHub repository.

## Uninstall

You can remove Cozy Worlds directly from its command:

```bash
cozy -uninstall
```

This removes the `cozy` launcher link and the installed Cozy Worlds folder at
`~/.local/share/cozy-worlds`. It does not remove Python, Git, or any of your
other files.

## Add your own scenes

The launcher automatically discovers Python animation files in the `animations/` directory.

To add a scene:

1. Create a standalone Python animation script.
2. Put the `.py` file in `animations/`.
3. Run `cozy` again, or press **R** in the menu to rescan.

Each animation should run independently with Python 3 and should manage terminal setup and restoration itself.

## Project layout

```text
cozy-worlds/
├── animations/
│   ├── fireplace.py
│   ├── rainy_window.py
│   ├── mountain_campfire.py
│   ├── moonlit_pond.py
│   └── sleeper_train.py
├── install.sh
├── launcher.py
├── README.md
└── .gitignore
```

## Notes

- Cozy Worlds is designed for terminal environments that support ANSI true-colour.
- Appearance may vary depending on terminal size, font, and colour support.
- The installer downloads and runs code from this repository. Only run it if you trust the source; you can inspect `install.sh` before installing.

## Contributing

Suggestions, bug reports, and new scene ideas are welcome. If you contribute an animation, keep it self-contained and make sure it restores the terminal cleanly when it exits.

---

Made for slower moments at the command line.
