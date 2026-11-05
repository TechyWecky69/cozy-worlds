# Cozy Worlds

A collection of standalone Python terminal animations for Linux.

## Requirements

- Linux/macOS terminal with ANSI true-colour support
- Python 3
- Git (for the installer)

The animations are plain Python scripts. They do not need a separate graphics engine.

## Add the animations

Copy the standalone animation `.py` files into `animations/`. For example:

```text
animations/
├── fireplace.py
├── rainy_window.py
├── mountain_campfire.py
├── moonlit_pond.py
└── sleeper_train.py
```

Each animation should run by itself with `python3 animations/name.py`.

## Publish this repository

1. Create a GitHub repository named `cozy-worlds`.
2. Upload `install.sh`, `launcher.py`, `README.md`, `.gitignore`, and the `animations/` folder with your animation scripts.
3. In `install.sh`, replace `USERNAME` in the `REPO_URL` with your GitHub username.
4. Make sure the repository is public if you want anyone to install it without signing in.

## Install for users

Once published, users can run:

```bash
curl -fsSL https://raw.githubusercontent.com/USERNAME/cozy-worlds/main/install.sh | bash
```

Replace `USERNAME` with your GitHub username.

The installer clones the repository into `~/.local/share/cozy-worlds` and creates a `cozy` command in `~/.local/bin`.

Then run:

```bash
cozy
```

If the terminal says `cozy: command not found`, add this to `~/.bashrc` (Bash) or `~/.zshrc` (Zsh), then open a new terminal:

```bash
export PATH="$HOME/.local/bin:$PATH"
```

## Update

Run the same curl installer command again. It will pull the latest version from GitHub.

## Uninstall

```bash
rm -f ~/.local/bin/cozy
rm -rf ~/.local/share/cozy-worlds
```

## Notes

- The installer runs downloaded shell code, so users should inspect `install.sh` before running it if they do not trust the source.
- The animations are downloaded as part of the Git clone; they are not executed directly from GitHub's web page.
- The launcher scans `animations/` for `.py` files automatically.
