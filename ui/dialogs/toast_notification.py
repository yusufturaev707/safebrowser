"""
Toast Notification - Yengil ogohlantirish xabari
Material Design 3 styled toast component
"""
from PyQt6.QtWidgets import (
    QWidget, QLabel, QHBoxLayout, QGraphicsDropShadowEffect,
    QGraphicsOpacityEffect, QPushButton
)
from PyQt6.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve, pyqtSignal
from PyQt6.QtGui import QColor


class ToastNotification(QWidget):
    """
    Material Design 3 styled toast notification
    Ekran chekkasida chiqadigan yengil ogohlantirish
    """
    # Toast yopilganda signal
    closed = pyqtSignal()
    # Foydalanuvchi bosganda signal
    clicked = pyqtSignal()

    def __init__(
        self,
        parent=None,
        message: str = "",
        toast_type: str = "warning",  # warning, error, success, info
        duration: int = 5000,  # milliseconds, 0 = manual close
        position: str = "top-right"  # top-right, top-left, bottom-right, bottom-left
    ):
        super().__init__(parent)
        self.message = message
        self.toast_type = toast_type
        self.duration = duration
        self.position = position
        self._is_hovered = False

        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.Tool
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating)

        self._setup_ui()
        self._apply_style()
        self._setup_animation()

    def _setup_ui(self):
        """UI komponentlarini sozlash"""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(16, 12, 16, 12)
        layout.setSpacing(12)

        # Icon
        self.icon_label = QLabel()
        self.icon_label.setFixedSize(24, 24)
        self.icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Message
        self.message_label = QLabel(self.message)
        self.message_label.setWordWrap(True)
        self.message_label.setMinimumWidth(250)
        self.message_label.setMaximumWidth(400)

        # Close button
        self.close_btn = QPushButton("x")
        self.close_btn.setFixedSize(20, 20)
        self.close_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.close_btn.clicked.connect(self.hide_toast)

        layout.addWidget(self.icon_label)
        layout.addWidget(self.message_label, 1)
        layout.addWidget(self.close_btn)

        # Shadow effect
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(20)
        shadow.setXOffset(0)
        shadow.setYOffset(4)
        shadow.setColor(QColor(0, 0, 0, 60))
        self.setGraphicsEffect(shadow)

        self.setFixedHeight(56)
        self.adjustSize()

    def _apply_style(self):
        """Toast turiga qarab stil qo'llash"""
        styles = {
            "warning": {
                "bg": "#fef3c7",
                "border": "#f59e0b",
                "text": "#92400e",
                "icon": "!",
                "icon_bg": "#f59e0b"
            },
            "error": {
                "bg": "#fee2e2",
                "border": "#ef4444",
                "text": "#991b1b",
                "icon": "x",
                "icon_bg": "#ef4444"
            },
            "success": {
                "bg": "#d1fae5",
                "border": "#10b981",
                "text": "#065f46",
                "icon": "v",
                "icon_bg": "#10b981"
            },
            "info": {
                "bg": "#dbeafe",
                "border": "#3b82f6",
                "text": "#1e40af",
                "icon": "i",
                "icon_bg": "#3b82f6"
            }
        }

        style = styles.get(self.toast_type, styles["warning"])

        self.setStyleSheet(f"""
            ToastNotification {{
                background-color: {style['bg']};
                border: 2px solid {style['border']};
                border-radius: 12px;
            }}
        """)

        self.icon_label.setStyleSheet(f"""
            QLabel {{
                background-color: {style['icon_bg']};
                color: white;
                font-size: 14px;
                font-weight: bold;
                border-radius: 12px;
            }}
        """)
        self.icon_label.setText(style['icon'])

        self.message_label.setStyleSheet(f"""
            QLabel {{
                color: {style['text']};
                font-size: 14px;
                font-weight: 500;
                font-family: 'Inter', sans-serif;
                background: transparent;
            }}
        """)

        self.close_btn.setStyleSheet(f"""
            QPushButton {{
                background: transparent;
                color: {style['text']};
                font-size: 14px;
                font-weight: bold;
                border: none;
                border-radius: 10px;
            }}
            QPushButton:hover {{
                background-color: rgba(0, 0, 0, 0.1);
            }}
        """)

    def _setup_animation(self):
        """Animatsiyalarni sozlash"""
        # Opacity effect for fade animation
        self.opacity_effect = QGraphicsOpacityEffect(self)
        self.setGraphicsEffect(self.opacity_effect)
        self.opacity_effect.setOpacity(0)

        # Fade in animation
        self.fade_in_anim = QPropertyAnimation(self.opacity_effect, b"opacity")
        self.fade_in_anim.setDuration(300)
        self.fade_in_anim.setStartValue(0)
        self.fade_in_anim.setEndValue(1)
        self.fade_in_anim.setEasingCurve(QEasingCurve.Type.OutCubic)

        # Fade out animation
        self.fade_out_anim = QPropertyAnimation(self.opacity_effect, b"opacity")
        self.fade_out_anim.setDuration(300)
        self.fade_out_anim.setStartValue(1)
        self.fade_out_anim.setEndValue(0)
        self.fade_out_anim.setEasingCurve(QEasingCurve.Type.InCubic)
        self.fade_out_anim.finished.connect(self._on_fade_out_finished)

        # Auto-close timer
        self.auto_close_timer = QTimer(self)
        self.auto_close_timer.setSingleShot(True)
        self.auto_close_timer.timeout.connect(self.hide_toast)

    def show_toast(self, parent_widget=None):
        """Toast ko'rsatish"""
        if parent_widget:
            self.setParent(parent_widget)
            self._position_toast(parent_widget)

        self.show()
        self.raise_()
        self.fade_in_anim.start()

        # Auto-close timer
        if self.duration > 0:
            self.auto_close_timer.start(self.duration)

    def hide_toast(self):
        """Toast yashirish"""
        self.auto_close_timer.stop()
        self.fade_out_anim.start()

    def _on_fade_out_finished(self):
        """Fade out tugaganda"""
        self.hide()
        self.closed.emit()

    def _position_toast(self, parent):
        """Toast joylashuvini aniqlash"""
        margin = 20
        parent_rect = parent.rect()

        if self.position == "top-right":
            x = parent_rect.width() - self.width() - margin
            y = margin
        elif self.position == "top-left":
            x = margin
            y = margin
        elif self.position == "bottom-right":
            x = parent_rect.width() - self.width() - margin
            y = parent_rect.height() - self.height() - margin
        elif self.position == "bottom-left":
            x = margin
            y = parent_rect.height() - self.height() - margin
        else:
            x = parent_rect.width() - self.width() - margin
            y = margin

        self.move(x, y)

    def set_message(self, message: str):
        """Xabarni o'zgartirish"""
        self.message = message
        self.message_label.setText(message)
        self.adjustSize()

    def enterEvent(self, event):
        """Mouse kirganida - auto-close to'xtatish"""
        self._is_hovered = True
        self.auto_close_timer.stop()
        super().enterEvent(event)

    def leaveEvent(self, event):
        """Mouse chiqqanida - auto-close qayta boshlash"""
        self._is_hovered = False
        if self.duration > 0:
            self.auto_close_timer.start(self.duration)
        super().leaveEvent(event)

    def mousePressEvent(self, event):
        """Bosilganda signal yuborish"""
        self.clicked.emit()
        super().mousePressEvent(event)


class ToastManager:
    """
    Toast notification'larni boshqarish
    Bir nechta toast'ni stack qilib ko'rsatish
    """
    def __init__(self, parent=None):
        self.parent = parent
        self.toasts = []
        self.spacing = 10

    def show_toast(
        self,
        message: str,
        toast_type: str = "warning",
        duration: int = 5000,
        position: str = "top-right"
    ) -> ToastNotification:
        """Yangi toast ko'rsatish"""
        toast = ToastNotification(
            parent=self.parent,
            message=message,
            toast_type=toast_type,
            duration=duration,
            position=position
        )
        toast.closed.connect(lambda: self._on_toast_closed(toast))

        self.toasts.append(toast)
        toast.show_toast(self.parent)
        self._reposition_toasts()

        return toast

    def _on_toast_closed(self, toast: ToastNotification):
        """Toast yopilganda"""
        if toast in self.toasts:
            self.toasts.remove(toast)
            toast.deleteLater()
            self._reposition_toasts()

    def _reposition_toasts(self):
        """Barcha toast'larni qayta joylashtirish (position-aware)"""
        if not self.parent:
            return

        margin = 20
        parent_rect = self.parent.rect()

        # Bottom toastlar uchun — pastdan yuqoriga
        bottom_y = parent_rect.height() - margin
        # Top toastlar uchun — yuqoridan pastga
        top_y = margin

        for toast in self.toasts:
            if not toast.isVisible():
                continue

            if "right" in toast.position:
                x = parent_rect.width() - toast.width() - margin
            else:
                x = margin

            if "bottom" in toast.position:
                bottom_y -= toast.height()
                toast.move(x, bottom_y)
                bottom_y -= self.spacing
            else:
                toast.move(x, top_y)
                top_y += toast.height() + self.spacing

    def clear_all(self):
        """Barcha toast'larni yopish"""
        for toast in self.toasts[:]:
            toast.hide_toast()
