"""
Page No Internet - Internet yo'q sahifasi
Material Design 3 Style
"""

from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QPixmap, QColor
from PyQt6.QtWidgets import (
    QWidget, QGridLayout, QVBoxLayout,
    QLabel, QSpacerItem, QSizePolicy,
    QGraphicsDropShadowEffect
)


class PageNoInternet(QWidget):
    """Internet yo'q sahifasi"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("page_no_internet")
        self._setup_ui()
        self._apply_styles()

    def _setup_ui(self):
        """UI elementlarini yaratish"""
        # Main grid layout
        self.gridLayout_7 = QGridLayout(self)
        self.gridLayout_7.setObjectName("gridLayout_7")
        self.gridLayout_7.setContentsMargins(50, 40, 50, 40)
        self.gridLayout_7.setSpacing(20)

        # Top spacer
        spacer_top = QSpacerItem(20, 60, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)
        self.gridLayout_7.addItem(spacer_top, 0, 1, 1, 1)

        # Left spacer
        spacer_left = QSpacerItem(150, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
        self.gridLayout_7.addItem(spacer_left, 1, 0, 1, 1)

        # Main vertical layout
        self.verticalLayout_8 = QVBoxLayout()
        self.verticalLayout_8.setObjectName("verticalLayout_8")
        self.verticalLayout_8.setSpacing(30)
        self.verticalLayout_8.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Title label
        self.label_8 = QLabel(self)
        self.label_8.setScaledContents(True)
        self.label_8.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label_8.setObjectName("label_8")
        self.label_8.setText("Internet bilan aloqa yo'q!")
        self.verticalLayout_8.addWidget(self.label_8)

        # Spacer
        spacer_middle = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed)
        self.verticalLayout_8.addItem(spacer_middle)

        # WiFi image
        self.label_7 = QLabel(self)
        self.label_7.setText("")
        self.label_7.setPixmap(QPixmap("resources/images/no-wifi.png"))
        self.label_7.setScaledContents(True)
        self.label_7.setMinimumSize(QSize(200, 200))
        self.label_7.setMaximumSize(QSize(280, 280))
        self.label_7.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label_7.setObjectName("label_7")
        self.verticalLayout_8.addWidget(self.label_7, alignment=Qt.AlignmentFlag.AlignCenter)

        self.gridLayout_7.addLayout(self.verticalLayout_8, 1, 1, 1, 1)

        # Right spacer
        spacer_right = QSpacerItem(150, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
        self.gridLayout_7.addItem(spacer_right, 1, 2, 1, 1)

        # Bottom spacer
        spacer_bottom = QSpacerItem(20, 80, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)
        self.gridLayout_7.addItem(spacer_bottom, 2, 1, 1, 1)

    def _apply_styles(self):
        """Material Design 3 stylelarni qo'llash"""
        # Page background - Glassmorphism with subtle red tint
        self.setStyleSheet("""
            QWidget#page_no_internet {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 rgba(255, 255, 255, 0.95),
                    stop:0.5 rgba(254, 242, 242, 0.92),
                    stop:1 rgba(254, 226, 226, 0.90));
                border-radius: 28px;
            }
        """)

        # Title style - Material Design 3 Error Typography
        self.label_8.setStyleSheet("""
            QLabel {
                color: #dc2626;
                font-size: 38px;
                font-weight: 700;
                font-family: 'Inter', sans-serif;
                letter-spacing: 0.5px;
                padding: 28px 60px;
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 rgba(220, 38, 38, 0.08),
                    stop:0.5 rgba(220, 38, 38, 0.15),
                    stop:1 rgba(220, 38, 38, 0.08));
                border-radius: 20px;
                border: 2px solid rgba(220, 38, 38, 0.2);
            }
        """)

        # Add shadow to title
        title_shadow = QGraphicsDropShadowEffect()
        title_shadow.setBlurRadius(25)
        title_shadow.setXOffset(0)
        title_shadow.setYOffset(8)
        title_shadow.setColor(QColor(220, 38, 38, 60))
        self.label_8.setGraphicsEffect(title_shadow)

        # WiFi icon style
        self.label_7.setStyleSheet("""
            QLabel {
                background: transparent;
                border: none;
                padding: 20px;
            }
        """)
