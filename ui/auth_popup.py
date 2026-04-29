from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QLabel, QPushButton,
                              QLineEdit, QMessageBox, QWidget)
from PyQt6.QtCore import Qt, QRect
from PyQt6.QtGui import QFont, QPainter, QColor, QBrush, QPen, QLinearGradient, QPainterPath
import json

class AuthPopup(QDialog):
    """
    Glassmorphism-styled authentication popup for player name validation.
    """
    def __init__(self, parent=None, data_path="data/players.json"):
        super().__init__(parent)
        self.is_valid = False
        self.valid_names = []
        
        try:
            with open(data_path, 'r', encoding='utf-8') as f:
                self.valid_names = json.load(f)
        except Exception as e:
            print(f"Error loading valid names: {e}")

        # --- Window setup ---
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Dialog)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setModal(True)
        self.setFixedSize(500, 350)

        # Center on parent
        if parent:
            geo = parent.geometry()
            self.move(
                geo.x() + (geo.width() - self.width()) // 2,
                geo.y() + (geo.height() - self.height()) // 2,
            )

        self.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        self._build_ui()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        rect = self.rect()

        # Semi-transparent dark overlay behind the card
        painter.setBrush(QBrush(QColor(0, 0, 0, 120)))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRect(rect)

        # Glass card
        card = QRect(30, 30, rect.width() - 60, rect.height() - 60)

        # Background gradient (purple glassmorphism)
        grad = QLinearGradient(float(card.x()), float(card.y()),
                               float(card.right()), float(card.bottom()))
        grad.setColorAt(0.0, QColor(60, 10, 100, 210))
        grad.setColorAt(1.0, QColor(30, 5, 60, 230))
        painter.setBrush(QBrush(grad))

        # Gold border
        painter.setPen(QPen(QColor(218, 165, 32, 180), 2.5))
        path = QPainterPath()
        path.addRoundedRect(float(card.x()), float(card.y()),
                            float(card.width()), float(card.height()), 22.0, 22.0)
        painter.drawPath(path)

        # Inner glow line at top edge
        painter.setPen(QPen(QColor(255, 255, 255, 40), 1))
        painter.drawLine(card.x() + 22, card.y() + 1,
                         card.right() - 22, card.y() + 1)
        painter.end()

    def _build_ui(self):
        outer = QVBoxLayout(self)
        outer.setContentsMargins(50, 50, 50, 50)

        # Title
        title = QLabel("🔒  التحقق من اللاعب  🔒")
        title.setFont(QFont("Arial", 20, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("color: #ffd700; background: transparent;")
        outer.addWidget(title)

        outer.addSpacing(15)

        # Input Field
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Enter Player Name...")
        self.name_input.setFont(QFont("Arial", 14))
        self.name_input.setFixedHeight(45)
        self.name_input.setStyleSheet("""
            QLineEdit {
                background-color: rgba(255, 255, 255, 0.1);
                border: 2px solid rgba(218, 165, 32, 0.5);
                border-radius: 10px;
                color: white;
                padding: 0 15px;
            }
            QLineEdit:focus {
                border: 2px solid #daa520;
                background-color: rgba(255, 255, 255, 0.15);
            }
        """)
        outer.addWidget(self.name_input)

        outer.addSpacing(20)

        # Submit Button
        submit_btn = QPushButton("تحقق")
        submit_btn.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        submit_btn.setFixedHeight(50)
        submit_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        submit_btn.setStyleSheet("""
            QPushButton {
                background-color: rgba(218, 165, 32, 0.3);
                border: 2px solid #daa520;
                border-radius: 10px;
                color: #ffd700;
            }
            QPushButton:hover {
                background-color: rgba(218, 165, 32, 0.6);
                color: white;
            }
        """)
        submit_btn.clicked.connect(self._validate_name)
        outer.addWidget(submit_btn)
        
        # Cancel Button
        cancel_btn = QPushButton("إلغاء")
        cancel_btn.setFont(QFont("Arial", 14))
        cancel_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        cancel_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: none;
                color: #aaa;
            }
            QPushButton:hover {
                color: white;
                text-decoration: underline;
            }
        """)
        cancel_btn.clicked.connect(self.reject)
        outer.addWidget(cancel_btn)

        outer.addStretch()

    def _validate_name(self):
        entered_name = self.name_input.text().strip()
        
        # Case insensitive check
        valid_names_lower = [name.lower() for name in self.valid_names]
        
        if entered_name.lower() in valid_names_lower:
            self.is_valid = True
            self.accept()
        else:
            self.is_valid = False
            QMessageBox.warning(self, "خطأ", "Invalid player name. Please try again.")
            self.name_input.clear()
            self.name_input.setFocus()
