import os
from PyQt6.QtWidgets import QWidget
from PyQt6.QtGui import (QPainter, QColor, QPen, QBrush, QPixmap,
                          QLinearGradient, QFont, QPainterPath)
from PyQt6.QtCore import Qt, QRectF, QPropertyAnimation, QEasingCurve, pyqtProperty
from core.rules import ROWS, COLS, PLAYER_1, PLAYER_2, EMPTY

# --- Colors ---
PURPLE_BG    = QColor(120, 50, 200)
GOLD_LINE    = QColor(212, 175, 55) # Hex #D4AF37
CELL_WHITE   = QColor(255, 255, 255)
PLAYER1_FILL = QColor(160, 170, 220, 180)
PLAYER2_FILL = QColor(240, 170, 175, 180)

# Exact Mapping required by Ultimate Prompt
COL_LOGOS = [
    "assets/clubs/world cup qatar.jpeg",
    "assets/clubs/world cup russia.jpeg",
    "assets/clubs/brazil.jpeg",
    "assets/clubs/german.jpeg",
    "assets/clubs/spain.jpeg",
    "assets/clubs/france.jpeg",
    "assets/clubs/Argentina.jpeg",
]
ROW_LOGOS = [
    "assets/clubs/real madrid.jpeg",
    "assets/clubs/Barcelona.jpeg",
    "assets/clubs/manchester united.jpeg",
    "assets/clubs/manchester city.jpeg",
    "assets/clubs/Liver Pool.jpeg",
    "assets/clubs/paris.jpeg",
]

class GridView(QWidget):
    """
    Pro Grid View with inner shadows, QPropertyAnimation, and specific JPEG assets.
    """

    cell_clicked_callback = None

    def __init__(self, game_logic, parent=None):
        super().__init__(parent)
        self.game_logic = game_logic
        self.setMouseTracking(True)
        self.hover_col = -1

        # Load logos
        self._col_logos = [QPixmap(path) if os.path.exists(path) else None for path in COL_LOGOS]
        self._row_logos = [QPixmap(path) if os.path.exists(path) else None for path in ROW_LOGOS]

        # Animation state
        self._anim_row = -1
        self._anim_col = -1
        self._anim_piece = EMPTY
        self._drop_y_val = 0.0

        self.drop_anim = QPropertyAnimation(self, b"drop_y")
        self.drop_anim.setDuration(500)
        self.drop_anim.setEasingCurve(QEasingCurve.Type.InQuad)
        self.drop_anim.finished.connect(self._on_drop_finished)

    @pyqtProperty(float)
    def drop_y(self):
        return self._drop_y_val

    @drop_y.setter
    def drop_y(self, val):
        self._drop_y_val = val
        self.update()

    def _metrics(self):
        w, h = self.width(), self.height()
        return w / (COLS + 1), h / (ROWS + 1)

    def start_drop_animation(self, row, col, piece):
        cell_w, cell_h = self._metrics()
        self._anim_row, self._anim_col, self._anim_piece = row, col, piece
        
        start_y = cell_h
        end_y = (row + 1) * cell_h + cell_h / 2
        
        self.drop_anim.setStartValue(start_y)
        self.drop_anim.setEndValue(end_y)
        self.drop_anim.start()

    def _on_drop_finished(self):
        if self._anim_piece != EMPTY:
            self.game_logic.board.drop_piece(self._anim_row, self._anim_col, self._anim_piece)
            self._anim_piece = EMPTY
            self.update()
            if hasattr(self, 'drop_finished_callback') and self.drop_finished_callback:
                self.drop_finished_callback()

    @property
    def is_animating(self):
        return self.drop_anim.state() == QPropertyAnimation.State.Running

    def mouseMoveEvent(self, event):
        cell_w, _ = self._metrics()
        col = int(event.position().x() / cell_w) - 1
        if 0 <= col < COLS and col != self.hover_col:
            self.hover_col = col
            self.update()
        elif col < 0 or col >= COLS:
            if self.hover_col != -1:
                self.hover_col = -1
                self.update()

    def leaveEvent(self, event):
        self.hover_col = -1
        self.update()

    def mousePressEvent(self, event):
        if event.button() != Qt.MouseButton.LeftButton: return
        cell_w, cell_h = self._metrics()
        col = int(event.position().x() / cell_w) - 1
        row = int(event.position().y() / cell_h) - 1
        if 0 <= col < COLS and 0 <= row < ROWS and self.cell_clicked_callback:
            self.cell_clicked_callback(row, col)

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)

        w, h = float(self.width()), float(self.height())
        cell_w, cell_h = self._metrics()
        pad = 3.0

        # --- Purple gradient frame ---
        grad = QLinearGradient(0.0, 0.0, w, h)
        grad.setColorAt(0.0, QColor(70, 20, 100))
        grad.setColorAt(1.0, QColor(40, 10, 60))
        p.setBrush(QBrush(grad))
        p.setPen(Qt.PenStyle.NoPen)
        p.drawRect(QRectF(0, 0, w, h))

        # --- Frame Inner Shadow (Metallic effect) ---
        p.setPen(QPen(QColor(0, 0, 0, 150), 4))
        p.drawRect(QRectF(2, 2, w-4, h-4))
        p.setPen(QPen(QColor(255, 255, 255, 40), 2))
        p.drawRect(QRectF(4, 4, w-8, h-8))

        # --- Draw cells ---
        board = self.game_logic.board.grid
        for r in range(ROWS + 1):
            for c in range(COLS + 1):
                x, y = c * cell_w, r * cell_h
                rect = QRectF(x + pad, y + pad, cell_w - pad*2, cell_h - pad*2)

                is_hdr_row, is_hdr_col = (r == 0), (c == 0)
                d_r, d_c = r - 1, c - 1

                fill = None
                if is_hdr_row and is_hdr_col: pass
                elif is_hdr_row or is_hdr_col: fill = CELL_WHITE
                else:
                    piece = board[d_r][d_c]
                    if piece == PLAYER_1: fill = PLAYER1_FILL
                    elif piece == PLAYER_2: fill = PLAYER2_FILL
                    else: fill = CELL_WHITE

                if fill:
                    # Cell background
                    p.setBrush(QBrush(fill))
                    p.setPen(Qt.PenStyle.NoPen)
                    p.drawRect(rect)
                    
                    # Cell inner shadow for depth
                    if fill == CELL_WHITE:
                        p.setPen(QPen(QColor(0, 0, 0, 60), 2))
                        p.drawLine(rect.topLeft(), rect.topRight())
                        p.drawLine(rect.topLeft(), rect.bottomLeft())

                # Gold Border
                p.setBrush(Qt.BrushStyle.NoBrush)
                p.setPen(QPen(GOLD_LINE, 2.5))
                p.drawRect(rect)

                # Draw logos
                if is_hdr_row and not is_hdr_col and 0 <= d_c < len(self._col_logos):
                    pm = self._col_logos[d_c]
                    if pm: self._draw_logo(p, pm, rect)

                if is_hdr_col and not is_hdr_row and 0 <= d_r < len(self._row_logos):
                    pm = self._row_logos[d_r]
                    if pm: self._draw_logo(p, pm, rect)

        # --- Hover highlight ---
        if self.hover_col >= 0:
            p.setBrush(QBrush(QColor(255, 255, 255, 20)))
            p.setPen(Qt.PenStyle.NoPen)
            p.drawRect(QRectF((self.hover_col + 1) * cell_w, 0, cell_w, h))

        # --- Drop animation ---
        if self._anim_piece != EMPTY and self.drop_anim.state() == QPropertyAnimation.State.Running:
            aw, ah = cell_w - pad*2, cell_h - pad*2
            ax = (self._anim_col + 1) * cell_w + pad
            ay = self._drop_y_val - ah / 2
            
            fill = PLAYER1_FILL if self._anim_piece == PLAYER_1 else PLAYER2_FILL
            p.setBrush(QBrush(fill))
            p.setPen(QPen(GOLD_LINE, 2.5))
            p.drawRect(QRectF(ax, ay, aw, ah))

        p.end()

    def _draw_logo(self, p, pm, rect):
        size = min(rect.width(), rect.height()) * 0.85
        scaled = pm.scaled(int(size), int(size), Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
        lx = rect.x() + (rect.width() - scaled.width()) / 2
        ly = rect.y() + (rect.height() - scaled.height()) / 2
        p.drawPixmap(int(lx), int(ly), scaled)
