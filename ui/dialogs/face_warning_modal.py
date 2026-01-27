"""
Face Warning Modal - Yuz tekshiruvi ogohlantirishiga reaksiya so'rash
Material Design 3 styled modal
"""
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QGraphicsDropShadowEffect, QFrame, QWidget
)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from PyQt6.QtGui import QColor, QFont


class FaceWarningModal(QDialog):
    """
    Face Warning Modal - Yuz aniqlanmagan yoki tanilmagan holatda
    Material Design 3 stilida modal dialog
    """
    # Foydalanuvchi "Tushundim" bosganda
    acknowledged = pyqtSignal()
    # Vaqt tugaganda (reaksiya berilmadi)
    timeout_reached = pyqtSignal()

    def __init__(
        self,
        parent=None,
        message: str = "",
        warning_type: str = "face_not_detected",  # face_not_detected, face_mismatch
        timeout_seconds: int = 30
    ):
        super().__init__(parent)
        self.message = message
        self.warning_type = warning_type
        self.timeout_seconds = timeout_seconds
        self.remaining_seconds = timeout_seconds
        self._timeout_triggered = False

        self.setWindowFlags(
            Qt.WindowType.Dialog |
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint
        )
        self.setModal(True)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        self._setup_ui()
        self._setup_timer()

    def _setup_ui(self):
        """UI komponentlarini sozlash"""
        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)

        # Container frame
        self.container = QFrame()
        self.container.setObjectName("warning_modal_container")
        self.container.setFixedSize(480, 380)

        container_layout = QVBoxLayout(self.container)
        container_layout.setContentsMargins(32, 28, 32, 28)
        container_layout.setSpacing(20)

        # Warning icon
        icon_label = QLabel()
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icon_label.setStyleSheet("""
            QLabel {
                font-size: 64px;
                background: transparent;
            }
        """)

        # Title
        self.title_label = QLabel()
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.title_label.setWordWrap(True)

        # Message
        self.message_label = QLabel(self.message)
        self.message_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.message_label.setWordWrap(True)

        # Timer display
        self.timer_label = QLabel()
        self.timer_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Progress bar (visual timer)
        self.progress_frame = QFrame()
        self.progress_frame.setFixedHeight(6)
        self.progress_frame.setStyleSheet("""
            QFrame {
                background-color: rgba(0, 0, 0, 0.1);
                border-radius: 3px;
            }
        """)

        self.progress_bar = QFrame(self.progress_frame)
        self.progress_bar.setFixedHeight(6)
        self.progress_bar.setGeometry(0, 0, 416, 6)

        # Button
        self.acknowledge_btn = QPushButton("Tushundim")
        self.acknowledge_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.acknowledge_btn.clicked.connect(self._on_acknowledge)

        # Add to layout
        container_layout.addWidget(icon_label)
        container_layout.addWidget(self.title_label)
        container_layout.addWidget(self.message_label)
        container_layout.addStretch()
        container_layout.addWidget(self.timer_label)
        container_layout.addWidget(self.progress_frame)
        container_layout.addWidget(self.acknowledge_btn)

        main_layout.addWidget(self.container, alignment=Qt.AlignmentFlag.AlignCenter)

        # Apply styles based on warning type
        self._apply_style(icon_label)

        # Shadow effect
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(40)
        shadow.setXOffset(0)
        shadow.setYOffset(10)
        shadow.setColor(QColor(0, 0, 0, 80))
        self.container.setGraphicsEffect(shadow)

    def _apply_style(self, icon_label: QLabel):
        """Warning turiga qarab stil qo'llash"""
        if self.warning_type == "face_not_detected":
            icon = "!"
            title = "Yuz aniqlanmadi!"
            bg_gradient = "qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #fef3c7, stop:1 #fde68a)"
            border_color = "#f59e0b"
            title_color = "#92400e"
            text_color = "#78350f"
            btn_bg = "#f59e0b"
            btn_hover = "#d97706"
            progress_color = "#f59e0b"
        else:  # face_mismatch
            icon = "!"
            title = "Yuz tanilmadi!"
            bg_gradient = "qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #fee2e2, stop:1 #fecaca)"
            border_color = "#ef4444"
            title_color = "#991b1b"
            text_color = "#7f1d1d"
            btn_bg = "#ef4444"
            btn_hover = "#dc2626"
            progress_color = "#ef4444"

        icon_label.setText(icon)

        self.container.setStyleSheet(f"""
            QFrame#warning_modal_container {{
                background: {bg_gradient};
                border: 3px solid {border_color};
                border-radius: 24px;
            }}
        """)

        self.title_label.setText(title)
        self.title_label.setStyleSheet(f"""
            QLabel {{
                color: {title_color};
                font-size: 28px;
                font-weight: 700;
                font-family: 'Segoe UI', 'Roboto', sans-serif;
                background: transparent;
            }}
        """)

        if not self.message:
            self.message = "Iltimos, yuzingizni kameraga to'g'ri ko'rsating va yaxshi yoritilgan joyda turing."

        self.message_label.setText(self.message)
        self.message_label.setStyleSheet(f"""
            QLabel {{
                color: {text_color};
                font-size: 16px;
                font-weight: 500;
                font-family: 'Segoe UI', 'Roboto', sans-serif;
                line-height: 1.6;
                background: transparent;
                padding: 8px;
            }}
        """)

        self.timer_label.setStyleSheet(f"""
            QLabel {{
                color: {title_color};
                font-size: 14px;
                font-weight: 600;
                font-family: 'Segoe UI', 'Roboto', sans-serif;
                background: transparent;
            }}
        """)

        self.progress_bar.setStyleSheet(f"""
            QFrame {{
                background-color: {progress_color};
                border-radius: 3px;
            }}
        """)

        self.acknowledge_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {btn_bg};
                color: white;
                font-size: 18px;
                font-weight: 600;
                font-family: 'Segoe UI', 'Roboto', sans-serif;
                padding: 14px 32px;
                border: none;
                border-radius: 12px;
                min-width: 160px;
            }}
            QPushButton:hover {{
                background-color: {btn_hover};
            }}
            QPushButton:pressed {{
                background-color: {text_color};
            }}
        """)

    def _setup_timer(self):
        """Countdown timer sozlash"""
        self.countdown_timer = QTimer(self)
        self.countdown_timer.timeout.connect(self._update_countdown)

    def _update_countdown(self):
        """Countdown yangilash"""
        self.remaining_seconds -= 1

        if self.remaining_seconds <= 0:
            self.countdown_timer.stop()
            self._timeout_triggered = True
            self.timeout_reached.emit()
            self.accept()
            return

        # Timer text yangilash
        self.timer_label.setText(f"Javob berish uchun: {self.remaining_seconds} soniya")

        # Progress bar yangilash
        progress_width = int(416 * (self.remaining_seconds / self.timeout_seconds))
        self.progress_bar.setFixedWidth(max(0, progress_width))

    def _on_acknowledge(self):
        """Foydalanuvchi "Tushundim" bosganda"""
        self.countdown_timer.stop()
        self._timeout_triggered = False
        self.acknowledged.emit()
        self.accept()

    def showEvent(self, event):
        """Modal ko'rsatilganda"""
        super().showEvent(event)
        self.remaining_seconds = self.timeout_seconds
        self._timeout_triggered = False
        self.timer_label.setText(f"Javob berish uchun: {self.remaining_seconds} soniya")
        self.progress_bar.setFixedWidth(416)
        self.countdown_timer.start(1000)  # 1 second interval

    def hideEvent(self, event):
        """Modal yashirilganda"""
        self.countdown_timer.stop()
        super().hideEvent(event)

    def was_timeout(self) -> bool:
        """Vaqt tugaganligi tekshirish"""
        return self._timeout_triggered

    def set_message(self, message: str):
        """Xabarni o'zgartirish"""
        self.message = message
        self.message_label.setText(message)

    def keyPressEvent(self, event):
        """Escape tugmasini bloklash"""
        if event.key() == Qt.Key.Key_Escape:
            event.ignore()
        else:
            super().keyPressEvent(event)
