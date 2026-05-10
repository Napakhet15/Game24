# Game 24 Puzzle

## Project Description

- **Project by:** Napakhet Namsrioun
- **Game Genre:** Puzzle, Math

Game 24 Puzzle is a number puzzle game where players are given a set of numbers and must combine them using mathematical operations to reach the target value of 24. The game includes multiple difficulty modes, score tracking, and a statistics dashboard that visualizes gameplay data.

---

## Installation

To clone this project:

```sh
git clone https://github.com/<username>/game24-puzzle.git
```

### Windows

```bat
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

### Mac / Linux

```sh
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

---

## Running Guide

After activating the Python environment, run the game with:

### Windows

```bat
python Code/game24ui.py
```

### Mac / Linux

```sh
python3 Code/game24ui.py
```

> **Note:** Make sure you are running from the root directory of the project (`game24PJ/`).

---

## Tutorial / Usage

1. **Register / Login** — Create an account or log in with an existing one.
2. **Select Mode** — Choose a game mode from the Mode Select screen.
3. **Build an Expression** — Tap number tiles and operator buttons to build a math expression.
4. **Submit** — Press Submit to check if your expression equals 24.
5. **Hints** — Use the hint button if you are stuck (limited in most modes).
6. **View Stats** — After playing, visit the Statistics page to view your performance data and charts.

### Controls

| Input | Action |
|---|---|
| Mouse click | Select number tile or operator |
| Submit button | Check if expression equals 24 |
| Undo button | Remove last token |
| Clear button | Reset expression |
| Skip button | Give up current puzzle |
| Hint button | Reveal a hint number |
| Keyboard 1–9 | Shortcut for number tiles |
| Backspace | Undo last token |
| Enter | Submit expression |

---

## Game Features

- **Classic Mode** — 4 numbers, target 24, no time limit.
- **Speed Mode** — 4 numbers, target 24, 30-second countdown with tick sound.
- **Hard Mode** — 4 numbers, target 24, with a random condition (e.g. must use ÷, no ×).
- **Advanced Mode** — 5 numbers, target 24, with power (^) and square root (√) operators.
- **Practice Mode** — No score, unlimited hints, no time limit. Great for learning.
- **Score System** — Score calculated from base score, time bonus, and penalties for attempts and hints.
- **Achievements** — 8 unlockable achievements based on gameplay milestones.
- **Scoreboard** — Top 20 scores across all players.
- **Statistics Dashboard** — Personal performance charts: attempts distribution, time trends, win/loss ratio, and hint usage.
- **Solution Finder** — On loss, the game shows one valid solution automatically.

---

## Project Structure

```
game24PJ/
│
├── Code/
│   ├── game24ui.py           # Main UI — all pages and app entry point
│   ├── auth.py               # User registration, login, and account management
│   ├── game_session.py       # Game round logic — timer, attempts, score logging
│   ├── math_engine.py        # Safe expression evaluator using AST
│   ├── puzzle.py             # Puzzle generation with solvability check
│   ├── expression_builder.py # Token-based expression builder
│   ├── score_calculator.py   # Score calculation formula
│   ├── game_stats.py         # Statistics computation from CSV
│   ├── achievements.py       # Achievement evaluation logic
│   └── scoreboard.py         # Scoreboard read/write
│
├── data/
│   ├── game_log.csv          # Gameplay session records
│   ├── scoreboard.json       # Top 20 scoreboard entries
│   └── users.json            # User accounts (hashed passwords)
│
├── screenshots/
│   ├── gameplay/             # Gameplay screenshots
│   └── visualization/        # Statistics dashboard screenshots
│
├── README.md
├── DESCRIPTION.md
├── requirements.txt
├── LICENSE
└── .gitignore
```

---

## Known Bugs

- None known at this time.

---

## Unfinished Works

- All planned features have been implemented.

---

## External Sources

1. CustomTkinter — https://github.com/TomSchimansky/CustomTkinter [MIT License]
2. Pandas — https://pandas.pydata.org [BSD License]
3. Matplotlib — https://matplotlib.org [PSF License]
4. Seaborn — https://seaborn.pydata.org [BSD License]
5. NumPy — https://numpy.org [BSD License]
6. Sound effects — procedurally generated in Python using NumPy and Pygame (no external audio files used)
