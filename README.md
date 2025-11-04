# Codenames AI Game

This is a micro Python AI game digitalizing the famous board game **Codenames**, a word-guessing party game, with AI players.

### Why I Want to Digitalize this Board Game
The core of this game is that to find all their team’s words faster than the opponent, the clue giver (Spymaster) needs to **abstractly connect as many of their team’s words as possible**.

This abstract connection may rely on various factors, such as cultural context, teammates’ cognitive levels, and mutual understanding. 

Notably, and this ability to connect words based on specific contexts is almost identical to the capabilities of LLMs.

Thus, I came up with the idea of playing this word-guessing game with LLMs. We could act as Operatives to guess the clues given by AI, or play the role of Spymaster and let AI guess the words. Alternatively, we might watch AIs compete against each other.

## About the Board Game Codenames 🕶

Codenames is a word-based party game where two teams compete to identify their agents based on one-word clues given by their spymaster.

### Quick summary of the board game (brief) 🌟
- Players: two teams (RED and BLUE). Each team has a Spymaster and one or more Field Operatives.
- Board: 25 words arranged in a 5×5 grid. Each word is secretly assigned to RED, BLUE, NEUTRAL, or ASSASSIN.
- Objective: Teams try to find all their words. Spymasters give one-word clues plus a number (e.g., "ROYAL, 2") that hint which words belong to their team.
- Guessing: The operative may guess up to `number + 1` times. Revealing an opponent card ends the turn; revealing the assassin causes an immediate loss.

<img width="600" height="450" alt="image" src="https://github.com/user-attachments/assets/891e1656-fb1c-46d0-bfb8-3f829f78ad47" />

> more details below

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
- The Operatives discuss the clue and select one or more codenames (up to the number given by the Spymaster, **plus one optional extra guess**).
- For each selected codename:
  - If it’s their team’s agent: Place their team’s marker on it (continue guessing if they have remaining attempts).
  - If it’s Neutral: No marker is placed, and their turn ends.
  - If it’s the enemy team’s agent: Place the enemy’s marker on it, and their turn ends.
  - If it’s the Assassin: Their team loses immediately.
- After the Operatives finish guessing, the turn switches to the other team.

### 4. Winning Conditions
- A team wins if they identify **all their agents** before the other team.
- A team loses if they select the **Assassin** at any point.

## Mirco Python Codenames AI Game 

A small Python implementation of the party game Codenames with AI players.

### We Have 3 Game Modes

1. **AI vs AI**: Watch AI spymasters and guessers play against each other
2. **Player as Field Operative**: You guess words based on AI-generated clues
3. **Player as Spymaster**: You provide clues and AI Operative will guess

## How to Run

1. Start the GUI (`python codenames_gui.py`).
 ```powershell
python .\codenames_gui.py
```
2. The main menu lets you choose a mode:
   - AI vs AI — watch two AIs play.
   - Player as Field Operative — you guess, AI gives clues.
   - Player as Spymaster — you give clues (you see the secret board), AI guesses.

<img width="600" height="350" alt="image" src="https://github.com/user-attachments/assets/237768b4-f09e-40b5-9634-0530e2ad0b0d" />

3. If you choose a player mode you'll be prompted to select RED or BLUE team.

<img width="500" height="349" alt="image" src="https://github.com/user-attachments/assets/0dd859f0-9d92-47f3-9c1c-6b7836812eb2" />

4. During play:
   - Click cards to reveal them when it is your turn to guess.
   - The clue panel shows the current clue and remaining guesses.
   - Use the "Pass" button (when enabled) to end your guessing early.

5. History and status are shown on the right side of the GUI. Use "Main Menu" to return at any time.

<img width="1752" height="1020" alt="8a4be9f733e0c4c8bc9eb963ab8da5db" src="https://github.com/user-attachments/assets/8f6c7cf3-6b2f-4771-a63b-f2dbe0e1f206" />

## Limitations

The project currently has the following limitations that require further optimization:

- The AI integrated into the application is not a Large Language Model (LLM). Its capability is relatively limited, resulting in insufficient intelligence for complex clue-generation and word-association tasks.
- The game’s UI interface is relatively rudimentary. Additionally, the interaction logic (e.g., feedback on guess results, clue display flow) needs further refinement to enhance user experience.
- The clues generated by the AI occasionally violate the game’s rules. For example, clues may include parts of codenames on the board or fail to match the required number of target words.

---

Enjoy the game — try AI vs AI to watch how the agents perform, or jump into a player mode to compete with or coach the AI!
















