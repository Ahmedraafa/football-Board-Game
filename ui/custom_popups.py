import json
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QLabel, QPushButton,
                              QLineEdit, QGraphicsBlurEffect, QWidget)
from PyQt6.QtCore import Qt, QRect, QPropertyAnimation, QEasingCurve, QTimer
from PyQt6.QtGui import QFont, QPainter, QColor, QBrush, QPen, QLinearGradient, QPainterPath

class BlurManager:
    @staticmethod
    def apply_blur(widget: QWidget):
        effect = QGraphicsBlurEffect(widget)
        effect.setBlurRadius(10)
        widget.setGraphicsEffect(effect)
        
    @staticmethod
    def remove_blur(widget: QWidget):
        widget.setGraphicsEffect(None)


class _BaseGlassPopup(QDialog):
    """Base class for glassmorphism popups with fade-in animation."""
    def __init__(self, parent=None, is_error=False):
        super().__init__(parent)
        self.is_error = is_error
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
        
        # Fade animation setup
        self.setWindowOpacity(0.0)
        self.fade_anim = QPropertyAnimation(self, b"windowOpacity")
        self.fade_anim.setDuration(300)
        self.fade_anim.setStartValue(0.0)
        self.fade_anim.setEndValue(1.0)
        self.fade_anim.setEasingCurve(QEasingCurve.Type.InOutQuad)

    def showEvent(self, event):
        super().showEvent(event)
        self.fade_anim.start()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        rect = self.rect()

        # Dark overlay
        painter.setBrush(QBrush(QColor(0, 0, 0, 140)))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRect(rect)

        # Glass card
        card = QRect(30, 30, rect.width() - 60, rect.height() - 60)

        grad = QLinearGradient(float(card.x()), float(card.y()),
                               float(card.right()), float(card.bottom()))
        if self.is_error:
            # Dark red glassmorphism
            grad.setColorAt(0.0, QColor(80, 10, 20, 220))
            grad.setColorAt(1.0, QColor(40, 5, 10, 240))
            border_color = QColor(255, 50, 50, 200)
        else:
            # Purple glassmorphism
            grad.setColorAt(0.0, QColor(60, 10, 100, 220))
            grad.setColorAt(1.0, QColor(30, 5, 60, 240))
            border_color = QColor(218, 165, 32, 180) # Gold

        painter.setBrush(QBrush(grad))
        painter.setPen(QPen(border_color, 2.5))
        
        path = QPainterPath()
        path.addRoundedRect(float(card.x()), float(card.y()),
                            float(card.width()), float(card.height()), 22.0, 22.0)
        painter.drawPath(path)

        # Inner glow line at top edge
        painter.setPen(QPen(QColor(255, 255, 255, 40), 1))
        painter.drawLine(card.x() + 22, card.y() + 1,
                         card.right() - 22, card.y() + 1)
        painter.end()


class ErrorPopup(_BaseGlassPopup):
    def __init__(self, message, parent=None):
        super().__init__(parent, is_error=True)
        self._build_ui(message)

    def _build_ui(self, message):
        outer = QVBoxLayout(self)
        outer.setContentsMargins(50, 50, 50, 50)

        title = QLabel("⚠️  عذراً!  ⚠️")
        title.setFont(QFont("Arial", 22, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("color: #ff5555; background: transparent;")
        outer.addWidget(title)

        outer.addSpacing(20)

        msg_label = QLabel(message)
        msg_label.setFont(QFont("Arial", 16))
        msg_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        msg_label.setWordWrap(True)
        msg_label.setStyleSheet("color: white; background: transparent;")
        outer.addWidget(msg_label)

        outer.addSpacing(30)

        btn = QPushButton("حسناً")
        btn.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        btn.setFixedHeight(45)
        btn.setCursor(Qt.CursorShape.PointingHandCursor)
        btn.setStyleSheet("""
            QPushButton {
                background-color: rgba(255, 50, 50, 0.3);
                border: 2px solid #ff5555;
                border-radius: 10px;
                color: #ffaaaa;
            }
            QPushButton:hover {
                background-color: rgba(255, 50, 50, 0.6);
                color: white;
            }
        """)
        btn.clicked.connect(self.accept)
        outer.addWidget(btn)
        outer.addStretch()


class AuthPopup(_BaseGlassPopup):
    def __init__(self, title_text, parent=None):
        super().__init__(parent, is_error=False)
        self.title_text = title_text
        self.entered_name = ""
        self._build_ui()

    def _build_ui(self):
        outer = QVBoxLayout(self)
        outer.setContentsMargins(50, 50, 50, 50)

        title = QLabel(self.title_text)
        title.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("color: #ffd700; background: transparent;")
        outer.addWidget(title)

        outer.addSpacing(15)

        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("اسم اللاعب...")
        self.name_input.setFont(QFont("Arial", 16))
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
        submit_btn.clicked.connect(self._submit)
        outer.addWidget(submit_btn)
        
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

    def _submit(self):
        self.entered_name = self.name_input.text().strip()
        self.accept()

class WinPopup(_BaseGlassPopup):
    def __init__(self, message, parent=None):
        super().__init__(parent, is_error=False)
        self.action = None
        self._build_ui(message)

    def _build_ui(self, message):
        outer = QVBoxLayout(self)
        outer.setContentsMargins(50, 50, 50, 50)

        title = QLabel("🎉  تهانينا!  🎉")
        title.setFont(QFont("Arial", 22, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("color: #ffd700; background: transparent;")
        outer.addWidget(title)

        outer.addSpacing(20)

        msg_label = QLabel(message)
        msg_label.setFont(QFont("Arial", 16))
        msg_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        msg_label.setWordWrap(True)
        msg_label.setStyleSheet("color: white; background: transparent;")
        outer.addWidget(msg_label)

        outer.addSpacing(30)

        btn_layout = QHBoxLayout()
        
        restart_btn = QPushButton("إعادة اللعبة")
        restart_btn.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        restart_btn.setFixedHeight(45)
        restart_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        restart_btn.setStyleSheet("""
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
        restart_btn.clicked.connect(self._restart)
        btn_layout.addWidget(restart_btn)

        quit_btn = QPushButton("خروج")
        quit_btn.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        quit_btn.setFixedHeight(45)
        quit_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        quit_btn.setStyleSheet("""
            QPushButton {
                background-color: rgba(255, 50, 50, 0.3);
                border: 2px solid #ff5555;
                border-radius: 10px;
                color: #ffaaaa;
            }
            QPushButton:hover {
                background-color: rgba(255, 50, 50, 0.6);
                color: white;
            }
        """)
        quit_btn.clicked.connect(self._quit)
        btn_layout.addWidget(quit_btn)

        outer.addLayout(btn_layout)
        outer.addStretch()

    def _restart(self):
        self.action = "RESTART"
        self.accept()

    def _quit(self):
        self.action = "QUIT"
        self.accept()
