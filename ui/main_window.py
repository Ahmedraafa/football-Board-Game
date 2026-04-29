import math
from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                              QPushButton, QLabel, QSizePolicy, QFrame)
from PyQt6.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve, QRect
from PyQt6.QtGui import QFont, QPainter, QColor, QBrush, QLinearGradient
from ui.grid_view import GridView
from ui.custom_popups import BlurManager, AuthPopup, ErrorPopup
from core.rules import PLAYER_1, PLAYER_2

class _BackgroundWidget(QWidget):
    """Deep purple gradient background for the whole window."""
    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        grad = QLinearGradient(0.0, 0.0, 0.0, float(self.height()))
        grad.setColorAt(0.0, QColor(30, 5, 40))
        grad.setColorAt(0.5, QColor(20, 2, 30))
        grad.setColorAt(1.0, QColor(10, 0, 15))
        p.setBrush(QBrush(grad))
        p.setPen(Qt.PenStyle.NoPen)
        p.drawRect(self.rect())
        p.end()

class AspectRatioWidget(QWidget):
    """A container that maintains the aspect ratio of its child widget."""
    def __init__(self, widget, aspect_ratio, parent=None):
        super().__init__(parent)
        self.aspect_ratio = aspect_ratio
        self.widget = widget
        self.widget.setParent(self)
        self.setMinimumSize(400, 300)

    def resizeEvent(self, event):
        w = self.width()
        h = self.height()
        target_w = h * self.aspect_ratio
        target_h = w / self.aspect_ratio
        
        if target_w <= w:
            # Match height, adjust width
            aw, ah = int(target_w), h
        else:
            # Match width, adjust height
            aw, ah = w, int(target_h)
            
        x = (w - aw) // 2
        y = (h - ah) // 2
        self.widget.setGeometry(QRect(x, y, aw, ah))

class MainWindow(QMainWindow):
    """Ultimate Pro Football Connect 4 Window"""

    def __init__(self, game_logic, _=None):
        super().__init__()
        self.game_logic = game_logic
        self.setWindowTitle("Football Connect 4 — Ultimate Edition")
        self.setMinimumSize(900, 850)
        self.resize(950, 900)
        
        # Set window icon
        from PyQt6.QtGui import QIcon
        import os
        logo_path = "assest logo.png"
        if os.path.exists(logo_path):
            self.setWindowIcon(QIcon(logo_path))

        self._build_ui()
        self._refresh_turn_display()

    # ------------------------------------------------------------------ #
    #  UI Builders (Simplified)                                           #
    # ------------------------------------------------------------------ #
    def _build_ui(self):
        self.central = _BackgroundWidget()
        self.setCentralWidget(self.central)

        self.root_layout = QVBoxLayout(self.central)
        self.root_layout.setContentsMargins(30, 20, 30, 20)
        self.root_layout.setSpacing(15)

        self._build_top_bar()
        self._build_grid()
        self._build_bottom_bar()

    def _build_top_bar(self):
        # ── Title with Logo ──
        title_layout = QHBoxLayout()
        title_layout.addStretch()

        import os
        from PyQt6.QtGui import QPixmap
        logo_path = "assest logo.png"
        if os.path.exists(logo_path):
            logo_label = QLabel()
            pm = QPixmap(logo_path).scaled(60, 60, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            logo_label.setPixmap(pm)
            title_layout.addWidget(logo_label)

        self.title_label = QLabel(" FOOTBALL CONNECT 4 ")
        self.title_label.setFont(QFont("Impact", 36, QFont.Weight.Bold))
        self.title_label.setStyleSheet("""
            color: #D4AF37;
            background: transparent;
            letter-spacing: 2px;
        """)
        title_layout.addWidget(self.title_label)
        title_layout.addStretch()
        
        self.root_layout.addLayout(title_layout)

        # ── Turn indicator ──
        self.turn_bar = QFrame()
        self.turn_bar.setFixedHeight(50)
        self.turn_bar.setStyleSheet("""
            QFrame {
                background-color: rgba(255, 255, 255, 0.05);
                border: 1px solid rgba(255, 255, 255, 0.1);
                border-radius: 12px;
            }
        """)
        turn_layout = QVBoxLayout(self.turn_bar)
        turn_layout.setContentsMargins(0, 0, 0, 0)
        self.turn_label = QLabel()
        self.turn_label.setFont(QFont("Arial", 18, QFont.Weight.Bold))
        self.turn_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.turn_label.setStyleSheet("background: transparent; border: none;")
        turn_layout.addWidget(self.turn_label)
        self.root_layout.addWidget(self.turn_bar)

    def _build_grid(self):
        # ── Grid view inside Aspect Ratio container ──
        self.grid_view = GridView(self.game_logic)
        self.grid_view.cell_clicked_callback = self._on_cell_click
        self.grid_view.drop_finished_callback = self._post_drop_check
        self.aspect_container = AspectRatioWidget(self.grid_view, 1.14)
        self.root_layout.addWidget(self.aspect_container, stretch=1)

    def _build_bottom_bar(self):
        # ── Bottom bar (Reset) ──
        bot = QHBoxLayout()
        reset_btn = QPushButton("🔄 إعادة اللعبة")
        reset_btn.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        reset_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        reset_btn.setFixedHeight(55)
        reset_btn.setMinimumWidth(250)
        reset_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #ff0844, stop:1 #ffb199);
                color: white;
                border: 2px solid rgba(255,255,255,0.4);
                border-radius: 25px;
            }
            QPushButton:hover { 
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #d10031, stop:1 #fa8b6b);
                border: 2px solid white;
            }
        """)
        reset_btn.clicked.connect(self._reset_game)
        bot.addStretch()
        bot.addWidget(reset_btn)
        bot.addStretch()
        self.root_layout.addLayout(bot)

    # ------------------------------------------------------------------ #
    #  Game-play flow                                                     #
    # ------------------------------------------------------------------ #
    def _show_error(self, message):
        BlurManager.apply_blur(self.central)
        popup = ErrorPopup(message, self)
        popup.exec()
        BlurManager.remove_blur(self.central)

    def _show_win(self, message):
        from ui.custom_popups import WinPopup
        import sys
        BlurManager.apply_blur(self.central)
        popup = WinPopup(message, self)
        popup.exec()
        BlurManager.remove_blur(self.central)
        if popup.action == "RESTART":
            self._reset_game()
        elif popup.action == "QUIT":
            sys.exit(0)

    def _on_cell_click(self, row, col):
        if self.game_logic.game_over:
            return
        if self.grid_view.is_animating:
            return

        if not self.game_logic.is_valid_gravity_move(row, col):
            self._show_error("عذراً! يجب وضع القطعة في الأسفل أو فوق قطعة أخرى.")
            return

        COLS_NAMES = ["كأس العالم قطر", "كأس العالم روسيا", "البرازيل", "ألمانيا", "إسبانيا", "فرنسا", "الأرجنتين"]
        ROWS_NAMES = ["ريال مدريد", "برشلونة", "مانشستر يونايتد", "مانشستر سيتي", "ليفربول", "باريس سان جيرمان"]
        row_name = ROWS_NAMES[row]
        col_name = COLS_NAMES[col]
        title_text = f"أدخل لاعب: {row_name} + {col_name}"
        
        BlurManager.apply_blur(self.central)
        popup = AuthPopup(title_text, self)
        res_dialog = popup.exec()
        BlurManager.remove_blur(self.central)

        if res_dialog:
            entered_name = popup.entered_name
            if not entered_name:
                return
                
            from core.game_logic import VALID, INVALID_TEAM_PLAYER, DUPLICATE_PLAYER
            val_result = self.game_logic.validate_player(entered_name, row, col)
            
            if val_result == VALID:
                self.grid_view.start_drop_animation(row, col, self.game_logic.current_turn)
            elif val_result == INVALID_TEAM_PLAYER:
                self._show_error(f"اسم اللاعب خطأ! لا يوجد لاعب معروف بـ {row_name} و {col_name} يحمل هذا الاسم.")
                self.game_logic.switch_turn()
                self._refresh_turn_display()
            elif val_result == DUPLICATE_PLAYER:
                self._show_error("هذا اللاعب تم اختياره مسبقاً!")
                self.game_logic.switch_turn()
                self._refresh_turn_display()

    def _post_drop_check(self):
        piece = self.game_logic.current_turn

        if self.game_logic.check_win(piece):
            self.game_logic.game_over = True
            self.game_logic.winner = piece
            self._refresh_turn_display()
            self.grid_view.update()
            
            name = "اللاعب الأول" if piece == PLAYER_1 else "اللاعب الثاني"
            self._show_win(f"🎉 فاز {name} بتوصيل 4 قطع! 🎉")
            return

        if self.game_logic.is_board_full():
            self.game_logic.game_over = True
            self._refresh_turn_display()
            self._show_win("انتهت اللعبة بالتعادل!")
            return

        self.game_logic.switch_turn()
        self._refresh_turn_display()

    # ------------------------------------------------------------------ #
    #  Helpers                                                            #
    # ------------------------------------------------------------------ #
    def _reset_game(self):
        self.game_logic.reset_game()
        self.grid_view.update()
        self._refresh_turn_display()

    def _refresh_turn_display(self):
        if self.game_logic.game_over:
            self.turn_label.setText("انتهت اللعبة!")
            self.turn_label.setStyleSheet("color: #D4AF37; background: transparent; border: none;")
            return

        # Use person icons 👤 instead of balls 🔴🔵
        if self.game_logic.current_turn == PLAYER_1:
            self.turn_label.setText("دور اللاعب الأول  👤")
            self.turn_label.setStyleSheet("color: #7882dc; background: transparent; border: none;")
        else:
            self.turn_label.setText("دور اللاعب الثاني  👤")
            self.turn_label.setStyleSheet("color: #f096a0; background: transparent; border: none;")

        self.grid_view.update()
