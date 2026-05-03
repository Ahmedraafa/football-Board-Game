# Football Connect 4 — Ultimate Edition ⚽🏆

<img width="1412" height="1348" alt="image" src="https://github.com/user-attachments/assets/3d6d65a7-88ea-465f-bc69-7ff27477ed46" />


A highly advanced, professionally designed desktop version of the classic Connect 4 game, engineered with **PyQt6**. This "Ultimate Edition" introduces a unique **Grid Trivia (التقاطعات)** mechanic where players must possess deep football knowledge to make their moves.

## ✨ Features

- **Grid Trivia Mechanic (التقاطعات)**: The board is built on a matrix of 6 Clubs (Rows) and 7 Countries/Tournaments (Columns). To place a piece, you must correctly name a player who has played for **both** the club and the country/tournament intersecting at that cell.
- **Smart Penalty System**: 
  - Entering an incorrect player name forfeits your turn.
  - **Duplicate Tracking**: The game remembers all used players. Trying to use the same player twice results in a penalty (lost turn).
- **Gravity Engine**: True Connect 4 gravity physics! You can only place pieces on the bottom row or directly on top of another piece.
- **Glassmorphism UI**: Beautiful, modern UI featuring blurred backgrounds (Glassmorphism), animated piece dropping, vibrant gradients, and dynamic popups.
- **Dynamic Assets**: Automatically loads club logos, national flags, and tournament cups dynamically into the grid headers.

## 🏗️ Architecture (MVC Pattern)
- `core/`: Contains the Game Model and Logic (`board.py`, `game_logic.py`, `rules.py`).
- `ui/`: Contains the Views and custom UI components (`main_window.py`, `grid_view.py`, `custom_popups.py`).
- `data/`: Contains the `players.json` database holding all 42 grid intersections.
- `assets/`: Contains UI assets (logos, player pictures, flags).

## 🚀 Requirements & Installation
- Python 3.11+
- PyQt6

```bash
# Install dependencies
pip install PyQt6

# Run the game
python main.py
```

## 🎮 How to Play
1. **Choose a Cell**: Ensure the cell is at the bottom or rests on another piece (Gravity Rule).
2. **Read the Prompt**: The popup will ask you for a specific intersection (e.g., "أدخل لاعب: باريس سان جيرمان + كأس العالم قطر").
3. **Submit Answer**: 
   - **Correct**: The piece drops smoothly with an animation, and the turn switches.
   - **Incorrect/Duplicate**: You receive an error, the piece is rejected, and your turn passes to the opponent.
4. **Win**: Connect 4 pieces horizontally, vertically, or diagonally!

---
*Built with ❤️ for Football Fans.*
