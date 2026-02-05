"""
Page PINFL - PINFL kiritish sahifasi
Modern Glassmorphism UI/UX Design
Soft light blue gradient, emerald green accents, frosted glass effect
"""

from PyQt6.QtCore import Qt, QSize, QRectF
from PyQt6.QtGui import QPixmap, QColor, QPainter, QPen, QBrush, QFont, QLinearGradient, QPainterPath
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QFrame,
    QGraphicsDropShadowEffect, QSizePolicy
)


class IDCardWidget(QWidget):
    """3D Stylized ID Card - Emerald green with JSHSHIR text"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumSize(380, 200)
        self.setMaximumSize(600, 280)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        w, h = self.width(), self.height()

        # Main card with emerald gradient
        card_rect = QRectF(4, 4, w - 8, h - 8)

        # Emerald green gradient background
        gradient = QLinearGradient(0, 0, w, h)
        gradient.setColorAt(0, QColor(16, 120, 90))      # Dark emerald
        gradient.setColorAt(0.5, QColor(32, 150, 110))   # Mid emerald
        gradient.setColorAt(1, QColor(46, 170, 130))     # Light emerald

        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QBrush(gradient))
        painter.drawRoundedRect(card_rect, 20, 20)

        # Glass overlay effect (top highlight)
        highlight = QLinearGradient(0, 0, 0, h * 0.5)
        highlight.setColorAt(0, QColor(255, 255, 255, 60))
        highlight.setColorAt(1, QColor(255, 255, 255, 0))
        painter.setBrush(QBrush(highlight))
        painter.drawRoundedRect(QRectF(4, 4, w - 8, h * 0.4), 20, 20)

        # Subtle inner border
        painter.setPen(QPen(QColor(255, 255, 255, 80), 1.5))
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawRoundedRect(card_rect.adjusted(1, 1, -1, -1), 19, 19)

        # Decorative circles (3D effect)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QBrush(QColor(255, 255, 255, 20)))
        painter.drawEllipse(int(w * 0.65), int(-h * 0.2), int(w * 0.5), int(w * 0.5))
        painter.setBrush(QBrush(QColor(0, 80, 60, 30)))
        painter.drawEllipse(int(-w * 0.1), int(h * 0.6), int(w * 0.4), int(w * 0.4))

        # ID CARD label
        painter.setPen(QColor(255, 255, 255, 200))
        font = QFont("Inter", 10, QFont.Weight.Bold)
        font.setLetterSpacing(QFont.SpacingType.AbsoluteSpacing, 3)
        painter.setFont(font)
        painter.drawText(24, 35, "ID KARTA")

        # Avatar placeholder
        avatar_x, avatar_y = w - 80, 22
        avatar_size = 55

        # Avatar background
        painter.setPen(QPen(QColor(255, 255, 255, 60), 1))
        painter.setBrush(QBrush(QColor(255, 255, 255, 30)))
        painter.drawRoundedRect(avatar_x, avatar_y, avatar_size, avatar_size, 14, 14)

        # User icon
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QBrush(QColor(255, 255, 255, 120)))
        # Head
        head_r = 10
        painter.drawEllipse(avatar_x + avatar_size // 2 - head_r, avatar_y + 12, head_r * 2, head_r * 2)
        # Body
        painter.drawEllipse(avatar_x + 12, avatar_y + 34, avatar_size - 24, 14)

        # JSHSHIR main text
        painter.setPen(QColor(255, 255, 255, 245))
        font = QFont("Inter", 24, QFont.Weight.Black)
        font.setLetterSpacing(QFont.SpacingType.AbsoluteSpacing, 6)
        painter.setFont(font)
        painter.drawText(24, h - 50, "JSHSHIR")

        # Decorative lines
        painter.setPen(QColor(255, 255, 255, 140))
        font = QFont("Inter", 11, QFont.Weight.Bold)
        font.setLetterSpacing(QFont.SpacingType.AbsoluteSpacing, 3)
        painter.setFont(font)
        painter.drawText(24, h - 22, "• • • • •")
        painter.drawText(w - 90, h - 22, "• • • •")

        # Chip decoration
        chip_x, chip_y = 24, h // 2 - 5
        chip_w, chip_h = 45, 32
        chip_gradient = QLinearGradient(chip_x, chip_y, chip_x + chip_w, chip_y + chip_h)
        chip_gradient.setColorAt(0, QColor(255, 255, 255, 50))
        chip_gradient.setColorAt(1, QColor(255, 255, 255, 20))
        painter.setPen(QPen(QColor(255, 255, 255, 80), 1))
        painter.setBrush(QBrush(chip_gradient))
        painter.drawRoundedRect(chip_x, chip_y, chip_w, chip_h, 6, 6)

        # Chip lines
        painter.setPen(QPen(QColor(255, 255, 255, 40), 1))
        painter.drawLine(chip_x + 15, chip_y + 4, chip_x + 15, chip_y + chip_h - 4)
        painter.drawLine(chip_x + 30, chip_y + 4, chip_x + 30, chip_y + chip_h - 4)

        painter.end()


class PagePinfl(QWidget):
    """PINFL kiritish sahifasi - Modern Glassmorphism Design"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("page_pinfl")
        self._setup_ui()
        self._apply_styles()

    def _setup_ui(self):
        """UI elementlarini yaratish"""
        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        main_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # ============ STAGE (Main Glassmorphism Container) ============
        self.stage = QFrame()
        self.stage.setObjectName("stage")
        self.stage.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
        self.stage.setMinimumSize(950, 480)
        self.stage.setMaximumSize(1100, 620)
        stage_layout = QVBoxLayout(self.stage)
        stage_layout.setContentsMargins(40, 32, 40, 36)
        stage_layout.setSpacing(0)

        # ============ HEADER ============
        header_widget = QFrame()
        header_widget.setObjectName("header_widget")
        header_widget.setFixedHeight(80)
        header_layout = QVBoxLayout(header_widget)
        header_layout.setContentsMargins(20, 12, 20, 16)
        header_layout.setSpacing(0)
        header_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Title
        self.label = QLabel("Hurmatli talabgor, JSHSHIR raqamingizni kiriting")
        self.label.setObjectName("header_title")
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label.setWordWrap(True)
        header_layout.addWidget(self.label)

        stage_layout.addWidget(header_widget)
        stage_layout.addSpacing(16)

        # ============ CONTENT SECTION ============
        content_widget = QFrame()
        content_widget.setObjectName("content_widget")
        content_layout = QHBoxLayout(content_widget)
        content_layout.setContentsMargins(24, 24, 24, 24)
        content_layout.setSpacing(32)
        content_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # ============ LOGIN CARD (Left - 6fr) ============
        self.login_card = QFrame()
        self.login_card.setObjectName("login_card")
        self.login_card.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        self.login_card.setMinimumWidth(400)
        self.login_card.setMaximumWidth(800)
        login_layout = QVBoxLayout(self.login_card)
        login_layout.setContentsMargins(28, 28, 28, 28)
        login_layout.setSpacing(16)
        login_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Input label
        input_label = QLabel("JSHSHIR (14 xonali)")
        input_label.setObjectName("input_label")
        input_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
        login_layout.addWidget(input_label)

        # PINFL Input - Clean white field
        self.input_pinfl = QLineEdit()
        self.input_pinfl.setObjectName("input_pinfl")
        self.input_pinfl.setFixedHeight(56)
        self.input_pinfl.setMaxLength(14)
        self.input_pinfl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.input_pinfl.setPlaceholderText("_ _ _ _ _ _ _ _ _ _ _ _ _ _")
        self.input_pinfl.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        login_layout.addWidget(self.input_pinfl)

        # Error label (hidden by default)
        self.error_label = QLabel("JSHSHIR 14 ta raqam bo'lishi kerak.")
        self.error_label.setObjectName("error_label")
        self.error_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.error_label.setVisible(False)
        login_layout.addWidget(self.error_label)

        login_layout.addSpacing(8)

        # Submit button - Dark emerald green
        self.btn_check_im = QPushButton("Tizimga kirish")
        self.btn_check_im.setObjectName("btn_submit")
        self.btn_check_im.setFixedHeight(52)
        self.btn_check_im.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_check_im.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        login_layout.addWidget(self.btn_check_im)

        content_layout.addWidget(self.login_card, 8)

        # ============ ID CARD (Right - 8:4 ratio) ============
        id_card_container = QWidget()
        id_card_container.setStyleSheet("background: transparent;")
        id_card_container.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        id_card_layout = QVBoxLayout(id_card_container)
        id_card_layout.setContentsMargins(0, 0, 0, 0)
        id_card_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.id_card = IDCardWidget()
        self.id_card.setObjectName("id_card")
        self.id_card.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)

        id_card_layout.addWidget(self.id_card)
        content_layout.addWidget(id_card_container, 4)

        stage_layout.addWidget(content_widget, 1)
        main_layout.addWidget(self.stage)

        # Legacy attributes for compatibility
        self.label_4 = self.id_card
        self.label_5 = QLabel()
        self.label_10 = QLabel()
        self.glow_frame = self.login_card
        self.glow_inner = QFrame()

    def _apply_styles(self):
        """Modern Glassmorphism styles"""

        # ===== PAGE BACKGROUND - Soft light blue/white gradient =====
        self.setStyleSheet("""
            QWidget#page_pinfl {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #f0f7ff,
                    stop:0.3 #e8f4fc,
                    stop:0.7 #f5f9ff,
                    stop:1 #eef6ff);
            }
        """)

        # ===== STAGE - Main glassmorphism card =====
        self.stage.setStyleSheet("""
            QFrame#stage {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 rgba(255, 255, 255, 0.70),
                    stop:1 rgba(255, 255, 255, 0.40));
                border: 1px solid rgba(255, 255, 255, 0.80);
                border-radius: 32px;
            }
        """)

        # Stage shadow
        stage_shadow = QGraphicsDropShadowEffect()
        stage_shadow.setBlurRadius(60)
        stage_shadow.setXOffset(0)
        stage_shadow.setYOffset(20)
        stage_shadow.setColor(QColor(0, 40, 80, 30))
        self.stage.setGraphicsEffect(stage_shadow)

        # ===== HEADER =====
        self.findChild(QFrame, "header_widget").setStyleSheet("""
            QFrame#header_widget {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 rgba(16, 120, 90, 0.08),
                    stop:0.5 rgba(16, 120, 90, 0.12),
                    stop:1 rgba(16, 120, 90, 0.08));
                border: 1px solid rgba(255, 255, 255, 0.60);
                border-radius: 20px;
            }
        """)

        # ===== HEADER TITLE =====
        self.label.setStyleSheet("""
            QLabel#header_title {
                color: #1a4a4a;
                font-size: 22px;
                font-weight: 700;
                font-family: 'Inter', 'Segoe UI', sans-serif;
                letter-spacing: 0.3px;
                background: transparent;
            }
        """)

        # ===== CONTENT =====
        self.findChild(QFrame, "content_widget").setStyleSheet("""
            QFrame#content_widget {
                background: rgba(255, 255, 255, 0.25);
                border: 1px solid rgba(255, 255, 255, 0.50);
                border-radius: 24px;
            }
        """)

        # ===== LOGIN CARD - Frosted glass effect =====
        self.login_card.setStyleSheet("""
            QFrame#login_card {
                background: rgba(255, 255, 255, 0.75);
                border: 1px solid rgba(255, 255, 255, 0.90);
                border-radius: 20px;
            }
        """)

        # Login card shadow
        login_shadow = QGraphicsDropShadowEffect()
        login_shadow.setBlurRadius(30)
        login_shadow.setXOffset(0)
        login_shadow.setYOffset(12)
        login_shadow.setColor(QColor(0, 60, 80, 25))
        self.login_card.setGraphicsEffect(login_shadow)

        # ===== INPUT LABEL =====
        self.findChild(QLabel, "input_label").setStyleSheet("""
            QLabel#input_label {
                color: #2a5555;
                font-size: 13px;
                font-weight: 600;
                font-family: 'Inter', 'Segoe UI', sans-serif;
                background: transparent;
                padding-left: 4px;
            }
        """)

        # ===== INPUT - Clean white field =====
        self.input_pinfl.setStyleSheet("""
            QLineEdit#input_pinfl {
                background: #ffffff;
                border: 2px solid #e0e8f0;
                border-radius: 14px;
                padding: 0 20px;
                font-size: 24px;
                font-weight: 700;
                font-family: 'Inter', 'Consolas', monospace;
                letter-spacing: 0.25em;
                color: #1a4a4a;
            }
            QLineEdit#input_pinfl:focus {
                border: 2px solid #10785a;
                background: #ffffff;
            }
            QLineEdit#input_pinfl:hover {
                border: 2px solid #a0d0c0;
            }
            QLineEdit#input_pinfl::placeholder {
                color: #b0c4c4;
                letter-spacing: 0.20em;
                font-weight: 600;
            }
        """)

        # Input shadow
        input_shadow = QGraphicsDropShadowEffect()
        input_shadow.setBlurRadius(12)
        input_shadow.setXOffset(0)
        input_shadow.setYOffset(3)
        input_shadow.setColor(QColor(0, 60, 80, 15))
        self.input_pinfl.setGraphicsEffect(input_shadow)

        # ===== ERROR LABEL =====
        self.error_label.setStyleSheet("""
            QLabel#error_label {
                color: #c53030;
                font-size: 12px;
                font-weight: 600;
                font-family: 'Inter', sans-serif;
                background: transparent;
                padding: 4px 0;
            }
        """)

        # ===== BUTTON - Dark emerald green =====
        self.btn_check_im.setStyleSheet("""
            QPushButton#btn_submit {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #10785a,
                    stop:1 #0d6048);
                color: #ffffff;
                border: none;
                border-radius: 14px;
                font-size: 16px;
                font-weight: 700;
                font-family: 'Inter', 'Segoe UI', sans-serif;
                letter-spacing: 0.5px;
            }
            QPushButton#btn_submit:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #138a68,
                    stop:1 #10785a);
            }
            QPushButton#btn_submit:pressed {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #0d6048,
                    stop:1 #0a5038);
            }
        """)

        # Button shadow
        btn_shadow = QGraphicsDropShadowEffect()
        btn_shadow.setBlurRadius(20)
        btn_shadow.setXOffset(0)
        btn_shadow.setYOffset(8)
        btn_shadow.setColor(QColor(16, 120, 90, 80))
        self.btn_check_im.setGraphicsEffect(btn_shadow)

        # ID Card shadow
        id_shadow = QGraphicsDropShadowEffect()
        id_shadow.setBlurRadius(40)
        id_shadow.setXOffset(0)
        id_shadow.setYOffset(16)
        id_shadow.setColor(QColor(16, 100, 80, 50))
        self.id_card.setGraphicsEffect(id_shadow)

    def show_error(self, show: bool = True):
        """Xatolik labelini ko'rsatish/yashirish"""
        self.error_label.setVisible(show)
        if show:
            self.input_pinfl.setStyleSheet("""
                QLineEdit#input_pinfl {
                    background: #ffffff;
                    border: 2px solid #e53e3e;
                    border-radius: 14px;
                    padding: 0 20px;
                    font-size: 18px;
                    font-weight: 700;
                    font-family: 'Inter', 'Consolas', monospace;
                    letter-spacing: 0.25em;
                    color: #1a4a4a;
                }
            """)
        else:
            self.input_pinfl.setStyleSheet("""
                QLineEdit#input_pinfl {
                    background: #ffffff;
                    border: 2px solid #e0e8f0;
                    border-radius: 14px;
                    padding: 0 20px;
                    font-size: 18px;
                    font-weight: 700;
                    font-family: 'Inter', 'Consolas', monospace;
                    letter-spacing: 0.25em;
                    color: #1a4a4a;
                }
                QLineEdit#input_pinfl:focus {
                    border: 2px solid #10785a;
                    background: #ffffff;
                }
                QLineEdit#input_pinfl:hover {
                    border: 2px solid #a0d0c0;
                }
                QLineEdit#input_pinfl::placeholder {
                    color: #b0c4c4;
                    letter-spacing: 0.20em;
                    font-weight: 600;
                }
            """)
