import sys
from PyQt6.QtWidgets import QApplication
from core.game_logic import GameLogic
from core.game_logic import GameLogic
from ui.main_window import MainWindow

def main():
    app = QApplication(sys.argv)
    
    # Initialize Core Components
    game_logic = GameLogic()
    
    # Initialize and show UI
    window = MainWindow(game_logic, None)
    window.show()
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
