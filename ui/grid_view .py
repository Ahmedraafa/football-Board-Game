import os
from PyQt6.QtWidgets import QWidget
from PyQt6.QtGui import (
    QPainter, QColor, QPen, QBrush, QPixmap,
    QLinearGradient, QFont, QPainterPath
)
from PyQt6.QtCore import Qt, QRectF

from core.rules import ROWS, COLS, PLAYER_1, PLAYER_2, EMPTY

# --- Colors ---
PURPLE_BG    = QColor(120, 50, 200)
GOLD_LINE    = QColor(212, 175, 55)
CELL_WHITE   = QColor(255, 255, 255)
PLAYER1_FILL = QColor(160, 170, 220, 180)
PLAYER2_FILL = QColor(240, 170, 175, 180)

# Logos mapping
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
    Grid View بدون أي Animation — عرض + hover + click + logos فقط
    """

    cell_clicked_callback = None
    drop_finished_callback = None
    is_animating = False

    def __init__(self, game_logic, parent=None):
        super().__init__(parent)

        self.game_logic = game_logic
        self.setMouseTracking(True)
        self.hover_col = -1

        # Load logos
        self._col_logos = [
            QPixmap(path) if os.path.exists(path) else None
            for path in COL_LOGOS
        ]
        self._row_logos = [
            QPixmap(path) if os.path.exists(path) else None
            for path in ROW_LOGOS
        ]

    # ---------- Helpers ----------
    def _metrics(self):
        w, h = self.width(), self.height()
        return w / (COLS + 1), h / (ROWS + 1)

    # ---------- Mouse ----------
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
        if event.button() != Qt.MouseButton.LeftButton:
            return

        cell_w, cell_h = self._metrics()
        col = int(event.position().x() / cell_w) - 1
        row = int(event.position().y() / cell_h) - 1

        if 0 <= col < COLS and 0 <= row < ROWS:
            if self.cell_clicked_callback:
                self.cell_clicked_callback(row, col)

    def start_drop_animation(self, row, col, piece):
        # Fallback method since we don't have real animations here
        self.game_logic.board.drop_piece(row, col, piece)
        self.update()
        if self.drop_finished_callback:
            self.drop_finished_callback()

    # ---------- Paint ----------
    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)

        w, h = self.width(), self.height()
        cell_w, cell_h = self._metrics()
        pad = 3.0

        # Background gradient
        grad = QLinearGradient(0, 0, w, h)
        grad.setColorAt(0.0, QColor(70, 20, 100))
        grad.setColorAt(1.0, QColor(40, 10, 60))
        p.setBrush(QBrush(grad))
        p.setPen(Qt.PenStyle.NoPen)
        p.drawRect(QRectF(0, 0, w, h))

        # Frame
        p.setPen(QPen(QColor(0, 0, 0, 150), 4))
        p.drawRect(QRectF(2, 2, w - 4, h - 4))

        p.setPen(QPen(QColor(255, 255, 255, 40), 2))
        p.drawRect(QRectF(4, 4, w - 8, h - 8))

        board = self.game_logic.board.grid

        # Grid
        for r in range(ROWS + 1):
            for c in range(COLS + 1):
                x, y = c * cell_w, r * cell_h
                rect = QRectF(x + pad, y + pad, cell_w - pad * 2, cell_h - pad * 2)

                is_hdr_row = (r == 0)
                is_hdr_col = (c == 0)
                d_r, d_c = r - 1, c - 1

                fill = None

                if not (is_hdr_row or is_hdr_col):
                    piece = board[d_r][d_c]
                    if piece == PLAYER_1:
                        fill = PLAYER1_FILL
                    elif piece == PLAYER_2:
                        fill = PLAYER2_FILL
                    else:
                        fill = CELL_WHITE
                elif is_hdr_row or is_hdr_col:
                    fill = CELL_WHITE

                if fill:
                    p.setBrush(QBrush(fill))
                    p.setPen(Qt.PenStyle.NoPen)
                    p.drawRect(rect)

                    if fill == CELL_WHITE:
                        p.setPen(QPen(QColor(0, 0, 0, 60), 2))
                        p.drawLine(rect.topLeft(), rect.topRight())
                        p.drawLine(rect.topLeft(), rect.bottomLeft())

                # Border
                p.setBrush(Qt.BrushStyle.NoBrush)
                p.setPen(QPen(GOLD_LINE, 2.5))
                p.drawRect(rect)

                # Logos (columns)
                if is_hdr_row and not is_hdr_col and 0 <= d_c < len(self._col_logos):
                    pm = self._col_logos[d_c]
                    if pm:
                        self._draw_logo(p, pm, rect)

                # Logos (rows)
                if is_hdr_col and not is_hdr_row and 0 <= d_r < len(self._row_logos):
                    pm = self._row_logos[d_r]
                    if pm:
                        self._draw_logo(p, pm, rect)

   

    # ---------- Logo helper ----------
    def _draw_logo(self, p, pm, rect):
        size = min(rect.width(), rect.height()) * 0.85
        scaled = pm.scaled(
            int(size), int(size),
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation
        )

        lx = rect.x() + (rect.width() - scaled.width()) / 2
        ly = rect.y() + (rect.height() - scaled.height()) / 2

        p.drawPixmap(int(lx), int(ly), scaled)
