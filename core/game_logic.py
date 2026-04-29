import json
from core.board import Board
from core.rules import PLAYER_1, PLAYER_2, EMPTY, ROWS, COLS

# Validation Constants
VALID = 0
INVALID_TEAM_PLAYER = 1
DUPLICATE_PLAYER = 2

class GameLogic:
    def __init__(self):
        self.board = Board()
        self.current_turn = PLAYER_1
        self.game_over = False
        self.winner = None
        self.used_players = set()
        
        self.intersections = {}
        try:
            with open("data/players.json", "r", encoding="utf-8") as f:
                self.intersections = json.load(f)
        except Exception as e:
            print(f"Error loading intersections: {e}")

    def validate_player(self, name, row, col):
        """
        Validates the entered name against the intersection's roster and checks for duplicates.
        Adds to used_players if valid.
        """
        name_lower = name.strip().lower()
        
        # Check duplicates
        for used in self.used_players:
            if name_lower == used.lower():
                return DUPLICATE_PLAYER
                
        # Check intersection roster
        key = f"{row},{col}"
        roster = self.intersections.get(key, [])
        for p in roster:
            if name_lower == p.lower():
                self.used_players.add(name_lower)
                return VALID
                
        return INVALID_TEAM_PLAYER

    def switch_turn(self):
        self.current_turn = PLAYER_2 if self.current_turn == PLAYER_1 else PLAYER_1

    def reset_game(self):
        self.board.reset()
        self.current_turn = PLAYER_1
        self.game_over = False
        self.winner = None
        self.used_players.clear()

    def check_win(self, piece):
        # Check horizontal
        for c in range(COLS - 3):
            for r in range(ROWS):
                if (self.board.grid[r][c] == piece and self.board.grid[r][c+1] == piece and
                    self.board.grid[r][c+2] == piece and self.board.grid[r][c+3] == piece):
                    return True

        # Check vertical
        for c in range(COLS):
            for r in range(ROWS - 3):
                if (self.board.grid[r][c] == piece and self.board.grid[r+1][c] == piece and
                    self.board.grid[r+2][c] == piece and self.board.grid[r+3][c] == piece):
                    return True

        # Check positive diagonal
        for c in range(COLS - 3):
            for r in range(ROWS - 3):
                if (self.board.grid[r][c] == piece and self.board.grid[r+1][c+1] == piece and
                    self.board.grid[r+2][c+2] == piece and self.board.grid[r+3][c+3] == piece):
                    return True

        # Check negative diagonal
        for c in range(COLS - 3):
            for r in range(3, ROWS):
                if (self.board.grid[r][c] == piece and self.board.grid[r-1][c+1] == piece and
                    self.board.grid[r-2][c+2] == piece and self.board.grid[r-3][c+3] == piece):
                    return True

        return False

    def is_board_full(self):
        for c in range(COLS):
            if self.board.grid[0][c] == EMPTY:
                return False
        return True

    def is_valid_gravity_move(self, row, col):
        """
        Gravity Rule: A piece can ONLY be placed if:
        1. The cell is empty.
        2. The cell is in the bottom row OR the cell directly below it is already occupied.
        """
        if self.board.grid[row][col] != EMPTY:
            return False
            
        if row == ROWS - 1:
            return True
            
        if self.board.grid[row + 1][col] != EMPTY:
            return True
            
        return False
