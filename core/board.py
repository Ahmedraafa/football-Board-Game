from core.rules import ROWS, COLS, EMPTY

class Board:
    def __init__(self):
        self.grid = [[EMPTY for _ in range(COLS)] for _ in range(ROWS)]
        
    def reset(self):
        self.grid = [[EMPTY for _ in range(COLS)] for _ in range(ROWS)]
        
    def is_valid_location(self, col):
        return self.grid[0][col] == EMPTY
        
    def get_next_open_row(self, col):
        for r in range(ROWS - 1, -1, -1):
            if self.grid[r][col] == EMPTY:
                return r
        return -1
        
    def drop_piece(self, row, col, piece):
        self.grid[row][col] = piece
