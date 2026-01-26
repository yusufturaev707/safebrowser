"""
Monitor Warning Modal Dialog
Qo'shimcha monitor aniqlanganda ko'rsatiladigan ogohlantirish oynasi
3 soniyadan keyin avtomatik yopiladi
"""
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont


class MonitorWarningModal(QDialog):
    """
    Monitor ogohlantirish modal oynasi
    Auto-close timer bilan
    """

    def __init__(self, parent=None, auto_close_seconds: int = 3):
        super().__init__(parent)

        self.auto_close_seconds = auto_close_seconds
        self.remaining_seconds = auto_close_seconds

        self.setWindowModality(Qt.WindowModality.ApplicationModal)
        self.setWindowFlags(
            Qt.WindowType.Dialog |
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint
        )
        self.setFixedSize(500, 300)

        self.setStyleSheet("""
            QDialog {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #fef2f2, stop:1 #fee2e2);
                border: 3px solid #ef4444;
                border-radius: 24px;
            }
            QLabel#icon {
                font-size: 48px;
                padding: 10px;
            }
            QLabel#title {
                font-size: 24px;
                font-weight: 700;
                color: #dc2626;
                padding: 10px;
            }
            QLabel#message {
                font-size: 16px;
                color: #7f1d1d;
                padding: 10px;
                line-height: 1.6;
            }
            QLabel#countdown {
                font-size: 18px;
                font-weight: 600;
                color: #b91c1c;
                padding: 15px;
                background: rgba(239, 68, 68, 0.15);
                border-radius: 12px;
            }
        """)

        layout = QVBoxLayout()
        layout.setContentsMargins(35, 30, 35, 30)
        layout.setSpacing(12)

        # Icon
        self.icon_label = QLabel("⚠️")
        self.icon_label.setObjectName("icon")
        self.icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Title
        self.title_label = QLabel("OGOHLANTIRISH!")
        self.title_label.setObjectName("title")
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.title_label.setFont(QFont("Segoe UI", 20, QFont.Weight.Bold))

        # Message
        self.message_label = QLabel(
            "Qo'shimcha monitor aniqlandi!\n\n"
            "Imtihon davomida faqat bitta monitor\n"
            "ishlatish mumkin."
        )
        self.message_label.setObjectName("message")
        self.message_label.setWordWrap(True)
        self.message_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.message_label.setFont(QFont("Segoe UI", 14))

        # Countdown
        self.countdown_label = QLabel(f"PINFL sahifasiga qaytish: {self.remaining_seconds} soniya")
        self.countdown_label.setObjectName("countdown")
        self.countdown_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.countdown_label.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))

        layout.addWidget(self.icon_label)
        layout.addWidget(self.title_label)
        layout.addWidget(self.message_label)
        layout.addStretch()
        layout.addWidget(self.countdown_label)

        self.setLayout(layout)

        # Timer for countdown
        self.countdown_timer = QTimer(self)
        self.countdown_timer.timeout.connect(self._update_countdown)

    def _update_countdown(self):
        """Countdown yangilash"""
        self.remaining_seconds -= 1

        if self.remaining_seconds <= 0:
            self.countdown_timer.stop()
            self.accept()
        else:
            self.countdown_label.setText(
                f"PINFL sahifasiga qaytish: {self.remaining_seconds} soniya"
            )

    def showEvent(self, event):
        """Modal ko'rsatilganda"""
        # Reset countdown
        self.remaining_seconds = self.auto_close_seconds
        self.countdown_label.setText(
            f"PINFL sahifasiga qaytish: {self.remaining_seconds} soniya"
        )

        # Markazga joylash
        if self.parent():
            parent_rect = self.parent().geometry()
            x = parent_rect.x() + (parent_rect.width() - self.width()) // 2
            y = parent_rect.y() + (parent_rect.height() - self.height()) // 2
            self.move(x, y)

        # Start countdown timer (1 second interval)
        self.countdown_timer.start(1000)

        super().showEvent(event)

    def closeEvent(self, event):
        """Modal yopilganda"""
        self.countdown_timer.stop()
        super().closeEvent(event)

    def set_message(self, title: str, message: str):
        """Xabarni o'zgartirish"""
        self.title_label.setText(title)
        self.message_label.setText(message)
