# ExecLauncher

_A Ulauncher extension for launching arbitrary executables_

ExecLauncher lets you quickly find and launch any executable file—ELF binaries, AppImages, shell scripts, or other non-installed / portable applications—without having to create menu entries or desktop shortcuts. Simply point it at your custom tool directories and invoke executables by name.

## Features

- **Custom Search Paths**  
  Define one or more directories to scan for executables (Example: `~/Tools`, `~/OtherTools`).

- **Executable Flag & ELF Validation**  
  Only files with the executable bit set are considered, and non-ELF files are skipped (except `.sh` scripts).

- **AppImage & Non-Installed / Portable App Support**  
  Since AppImages are ELF binaries, they’re automatically detected and listed—no extra configuration required.

- **Shell Script Support**  
  Files ending in `.sh` with execute permission are included even if they lack ELF headers.

- **Prefix-Prioritized Matching**  
  Results whose filenames start with your query are shown first, followed by other matches in alphabetical order.

- **Optional Library Filter** _(Experimental)_  
  Enable the “Experimental lib filter” in preferences to automatically exclude typical library files:
  - Filenames or parent folders containing `lib`
  - Files ending in `.so`

- **Lightweight, Non-Fuzzy Search**  
  Simple, case-insensitive substring matching for fast, predictable results—no approximate or “fuzzy” scoring.


# Installation
1. Install [Ulauncher](https://ulauncher.io/#Download). 
2. Just add `https://github.com/throwingshapes/executablelauncher` at Extensions section.

## Usage
- ex #     : launch exec given its filename
