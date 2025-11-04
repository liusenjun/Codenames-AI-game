# Codenames AI Game

This is a micro Python AI game digitalizing the famous board game **Codenames** with AI players.

### Why I Want to Digitalize this Board Game
The core of this game is that to find all their team’s words faster than the opponent, the clue giver (Spymaster) needs to abstractly connect as many of their team’s words as possible. They must avoid selecting the opponent’s words or the death word (Assassin) in the process. 
This abstract connection may rely on various factors, such as cultural context, teammates’ cognitive levels, and mutual understanding. 
Notably, this ability to link words based on specific scenarios is almost identical to the capabilities of LLMs—even the underlying logic of NLP and LLMs lies in the associations between words.
Thus, I came up with the idea of playing this game with LLMs. We could act as Operatives to guess the clues given by AI, or play the role of Spymaster and let AI guess the words. Alternatively, we might watch AIs compete against each other.

## About the Board Game Codenames 🕶

Codenames is a word-based party game where two teams compete to identify their agents based on one-word clues given by their spymaster.

<img width="600" height="450" alt="image" src="https://github.com/user-attachments/assets/891e1656-fb1c-46d0-bfb8-3f829f78ad47" />

### 1. Game Objective
Two teams compete to identify all their team’s "agents" (codenames) on the game board before the other team. Avoid the "assassin"—if a team selects the assassin, they lose immediately.

### 2. Setup
- Divide players into two teams: **Red Team** and **Blue Team**. Each team chooses **a Spymaster**; **the rest are Operatives**.
- Place the **25 codename cards** on the table in a 5x5 grid.
- The Spymasters take the key card (shows which codenames belong to Red Team, Blue Team, Neutral, and the Assassin). Keep the key card hidden from Operatives.
- Red Team goes first (unless agreed otherwise).

### 3. Gameplay
#### 3.1 Spymaster’s Turn
- The Spymaster gives a **one-word clue** and a **number** (e.g., **"Ocean: 2"**).
- The clue must relate to the meanings of their team’s agents (codenames) without being too direct.
- The number indicates how many of their team’s agents the clue applies to.
- Clues cannot be:
  - A codename on the board.
  - A part of a codename (e.g., "car" for "Carrot" is invalid).
  - A homophone of a codename.
  - Multiple words (only one word allowed for the clue).

#### 3.2 Operatives’ Turn
- The Operatives discuss the clue and select one or more codenames (up to the number given by the Spymaster, plus one optional extra guess).
- For each selected codename:
  - If it’s their team’s agent: Place their team’s marker on it (continue guessing if they have remaining attempts).
  - If it’s Neutral: No marker is placed, and their turn ends.
  - If it’s the enemy team’s agent: Place the enemy’s marker on it, and their turn ends.
  - If it’s the Assassin: Their team loses immediately.
- After the Operatives finish guessing, the turn switches to the other team.

### 4. Winning Conditions
- A team wins if they identify **all their agents** before the other team.
- A team loses if they select the **Assassin** at any point.

### Quick summary of the board game (brief) 🌟
- Players: two teams (RED and BLUE). Each team has a Spymaster and one or more Field Operatives.
- Board: 25 words arranged in a 5×5 grid. Each word is secretly assigned to RED, BLUE, NEUTRAL, or ASSASSIN.
- Objective: Teams try to find all their words. Spymasters give one-word clues plus a number (e.g., "ROYAL, 2") that hint which words belong to their team.
- Guessing: The operative may guess up to `number + 1` times. Revealing an opponent card ends the turn; revealing the assassin causes an immediate loss.

## Mirco Python Codenames AI Game 

### We Have 3 Game Modes

1. **AI vs AI**: Watch AI spymasters and guessers play against each other
2. **Player as Field Operative**: You guess words based on AI-generated clues
3. **Player as Spymaster**: You provide clues and AI Operative will guess

A small Python implementation of the party game Codenames with AI players.

## How to play (GUI)

1. Start the GUI (`python codenames_gui.py`). The main menu lets you choose a mode:
   - Player as Field Operative — you guess, AI gives clues.
   - Player as Spymaster — you give clues (you see the secret board), AI guesses.
   - AI vs AI — watch two AIs play.
2. If you choose a player mode you'll be prompted to select RED or BLUE team.
3. During play:
   - Click cards to reveal them when it is your turn to guess.
   - The clue panel shows the current clue and remaining guesses.
   - Use the "Pass" button (when enabled) to end your guessing early.
4. History and status are shown on the right side of the GUI. Use "Main Menu" to return at any time.

This repository contains:
- `codenames.py` — text-based implementation and AI logic.
- `codenames_gui.py` — modern Tkinter GUI frontend (recommended).
- `pic/` — optional images (use `bg1.jpg` or similar for the menu background).

## Project overview

This project provides two ways to play:

- Graphical interface (`codenames_gui.py`) — a Tkinter-based UI with color-coded cards, history panel, translation toggle, and three play modes (AI vs AI, Player as Field Operative, Player as Spymaster).
- Command-line interface (`codenames.py`) — a compact terminal version useful for quick testing or running without GUI.

AI components:
- `AISpymaster` — simple clue generator based on word associations.
- `AIGuesser` — simple scoring-based guesser that selects likely words for a clue.

## Requirements

- Python 3.8+ recommended (should run on 3.6+, but features were tested on 3.10+).
- Recommended (optional):
  - Pillow — for better background-image handling in the GUI (install with `pip install Pillow`).
  - googletrans==4.0.0rc1 — optional translation support in the GUI.

Install dependencies (PowerShell example):

```powershell
python -m pip install -r requirements.txt
# Optional extras:
python -m pip install Pillow
```

> Note: `requirements.txt` contains `googletrans==4.0.0rc1` as an optional translation dependency. If you don't need translations you can skip installing it.

## How to run

From the project folder (PowerShell examples):

- Run the GUI (recommended):

```powershell
python .\codenames_gui.py
```

- Run the text/console version:

```powershell
python .\codenames.py
```

If you see errors about missing packages:
- Install Pillow to enable advanced image handling in the GUI.
- Install googletrans if you want the translation feature.

## License & Credits

This repository is provided for educational purposes. You may use and adapt it, but please keep attribution and don't claim the original Codenames IP.

---

Enjoy the game — try AI vs AI to watch how the agents perform, or jump into a player mode to compete with or coach the AI!















