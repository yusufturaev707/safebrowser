"""
Info Modal Dialog
Material Design 3 style - Zamonaviy ogohlantirish oynasi
"""
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QFrame, QWidget
)
from PyQt6.QtCore import Qt, QRect
from PyQt6.QtGui import QFont, QFontMetrics, QColor, QPainter, QPen
from PyQt6.QtWidgets import QGraphicsDropShadowEffect


class InfoModal(QDialog):
    """
    Material Design 3 modal oyna - ogohlantirish va xabarlar uchun
    Yashil tema bilan
    """

    # Message types
    TYPE_INFO = 0
    TYPE_WARNING = 1
    TYPE_ERROR = 2
    TYPE_SUCCESS = 3

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowModality(Qt.WindowModality.ApplicationModal)
        self.setWindowFlags(
            Qt.WindowType.Dialog |
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        # Dinamik o'lcham chegaralari
        self.setMinimumSize(340, 220)
        self.setMaximumSize(560, 450)

        self._message_type = self.TYPE_INFO
        self._setup_ui()

    def _setup_ui(self):
        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Container
        self.container = QFrame()
        self.container.setObjectName("modal_container")
        self._apply_container_style()

        # Container shadow
        container_shadow = QGraphicsDropShadowEffect()
        container_shadow.setBlurRadius(40)
        container_shadow.setXOffset(0)
        container_shadow.setYOffset(12)
        container_shadow.setColor(QColor(0, 0, 0, 45))
        self.container.setGraphicsEffect(container_shadow)

        layout = QVBoxLayout(self.container)
        layout.setContentsMargins(28, 24, 28, 24)
        layout.setSpacing(0)

        # ============ ICON SECTION ============
        icon_widget = QWidget()
        icon_widget.setStyleSheet("background: transparent;")
        icon_layout = QHBoxLayout(icon_widget)
        icon_layout.setContentsMargins(0, 0, 0, 0)
        icon_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Icon container
        self.icon_container = IconWidget()
        self.icon_container.setFixedSize(56, 56)
        icon_layout.addWidget(self.icon_container)

        layout.addWidget(icon_widget)
        layout.addSpacing(16)

        # ============ TEXT SECTION ============
        text_widget = QWidget()
        text_widget.setStyleSheet("background: transparent;")
        text_layout = QVBoxLayout(text_widget)
        text_layout.setContentsMargins(0, 0, 0, 0)
        text_layout.setSpacing(8)

        # Title
        self.title_label = QLabel()
        self.title_label.setObjectName("title")
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.title_label.setStyleSheet("""
            QLabel#title {
                font-size: 20px;
                font-weight: 700;
                color: #14532d;
                font-family: 'Inter', 'Segoe UI', sans-serif;
                background: transparent;
            }
        """)
        text_layout.addWidget(self.title_label)

        # Message
        self.message_label = QLabel()
        self.message_label.setObjectName("message")
        self.message_label.setWordWrap(True)
        self.message_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.message_label.setStyleSheet("""
            QLabel#message {
                font-size: 14px;
                font-weight: 500;
                color: #166534;
                font-family: 'Inter', 'Segoe UI', sans-serif;
                background: transparent;
                padding: 0 10px;
            }
        """)
        text_layout.addWidget(self.message_label)

        layout.addWidget(text_widget)
        layout.addSpacing(20)

        # ============ BUTTON SECTION ============
        button_widget = QWidget()
        button_widget.setStyleSheet("background: transparent;")
        button_layout = QHBoxLayout(button_widget)
        button_layout.setContentsMargins(0, 0, 0, 0)
        button_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # OK button
        self.ok_button = QPushButton("Tushunarli")
        self.ok_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.ok_button.setFixedHeight(48)
        self.ok_button.setMinimumWidth(160)
        self.ok_button.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #22c55e, stop:1 #16a34a);
                color: #ffffff;
                border: none;
                border-radius: 14px;
                font-size: 15px;
                font-weight: 700;
                font-family: 'Inter', 'Segoe UI', sans-serif;
                padding: 0 32px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #16a34a, stop:1 #15803d);
            }
            QPushButton:pressed {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #15803d, stop:1 #166534);
            }
        """)

        # Button shadow
        btn_shadow = QGraphicsDropShadowEffect()
        btn_shadow.setBlurRadius(16)
        btn_shadow.setXOffset(0)
        btn_shadow.setYOffset(4)
        btn_shadow.setColor(QColor(34, 197, 94, 70))
        self.ok_button.setGraphicsEffect(btn_shadow)
        self.ok_button.clicked.connect(self.accept)

        button_layout.addWidget(self.ok_button)
        layout.addWidget(button_widget)

        main_layout.addWidget(self.container)

    def _apply_container_style(self, msg_type=TYPE_INFO):
        """Apply container style based on message type"""
        styles = {
            self.TYPE_INFO: {
                "bg": "#f0fdf4, #ecfdf5, #e6f7ed",
                "border": "rgba(34, 197, 94, 0.3)"
            },
            self.TYPE_SUCCESS: {
                "bg": "#f0fdf4, #ecfdf5, #e6f7ed",
                "border": "rgba(34, 197, 94, 0.3)"
            },
            self.TYPE_WARNING: {
                "bg": "#fffbeb, #fef3c7, #fde68a",
                "border": "rgba(245, 158, 11, 0.3)"
            },
            self.TYPE_ERROR: {
                "bg": "#fef2f2, #fee2e2, #fecaca",
                "border": "rgba(239, 68, 68, 0.3)"
            }
        }

        style = styles.get(msg_type, styles[self.TYPE_INFO])
        bg_colors = style["bg"].split(", ")

        self.container.setStyleSheet(f"""
            QFrame#modal_container {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 {bg_colors[0]},
                    stop:0.5 {bg_colors[1]},
                    stop:1 {bg_colors[2]});
                border: 2px solid {style["border"]};
                border-radius: 24px;
            }}
        """)

    def _apply_text_styles(self, msg_type):
        """Apply text styles based on message type"""
        colors = {
            self.TYPE_INFO: ("#14532d", "#166534"),
            self.TYPE_SUCCESS: ("#14532d", "#166534"),
            self.TYPE_WARNING: ("#78350f", "#92400e"),
            self.TYPE_ERROR: ("#7f1d1d", "#991b1b")
        }

        title_color, msg_color = colors.get(msg_type, colors[self.TYPE_INFO])

        self.title_label.setStyleSheet(f"""
            QLabel#title {{
                font-size: 20px;
                font-weight: 700;
                color: {title_color};
                font-family: 'Inter', 'Segoe UI', sans-serif;
                background: transparent;
            }}
        """)

        self.message_label.setStyleSheet(f"""
            QLabel#message {{
                font-size: 14px;
                font-weight: 500;
                color: {msg_color};
                font-family: 'Inter', 'Segoe UI', sans-serif;
                background: transparent;
                padding: 0 10px;
            }}
        """)

    def _apply_button_style(self, msg_type):
        """Apply button style based on message type"""
        styles = {
            self.TYPE_INFO: {
                "gradient": "#22c55e, #16a34a",
                "hover": "#16a34a, #15803d",
                "pressed": "#15803d, #166534",
                "shadow": QColor(34, 197, 94, 70)
            },
            self.TYPE_SUCCESS: {
                "gradient": "#22c55e, #16a34a",
                "hover": "#16a34a, #15803d",
                "pressed": "#15803d, #166534",
                "shadow": QColor(34, 197, 94, 70)
            },
            self.TYPE_WARNING: {
                "gradient": "#f59e0b, #d97706",
                "hover": "#d97706, #b45309",
                "pressed": "#b45309, #92400e",
                "shadow": QColor(245, 158, 11, 70)
            },
            self.TYPE_ERROR: {
                "gradient": "#ef4444, #dc2626",
                "hover": "#dc2626, #b91c1c",
                "pressed": "#b91c1c, #991b1b",
                "shadow": QColor(239, 68, 68, 70)
            }
        }

        style = styles.get(msg_type, styles[self.TYPE_INFO])

        self.ok_button.setStyleSheet(f"""
            QPushButton {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 {style["gradient"].split(", ")[0]},
                    stop:1 {style["gradient"].split(", ")[1]});
                color: #ffffff;
                border: none;
                border-radius: 14px;
                font-size: 15px;
                font-weight: 700;
                font-family: 'Inter', 'Segoe UI', sans-serif;
                padding: 0 32px;
            }}
            QPushButton:hover {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 {style["hover"].split(", ")[0]},
                    stop:1 {style["hover"].split(", ")[1]});
            }}
            QPushButton:pressed {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 {style["pressed"].split(", ")[0]},
                    stop:1 {style["pressed"].split(", ")[1]});
            }}
        """)

        # Update shadow
        btn_shadow = QGraphicsDropShadowEffect()
        btn_shadow.setBlurRadius(16)
        btn_shadow.setXOffset(0)
        btn_shadow.setYOffset(4)
        btn_shadow.setColor(style["shadow"])
        self.ok_button.setGraphicsEffect(btn_shadow)

    def update_data(self, title: str, message: str, msg_type: int = None):
        """Modal ma'lumotlarini yangilash"""
        self.title_label.setText(title)
        self.message_label.setText(message)

        # Auto-detect message type from title
        if msg_type is None:
            title_upper = title.upper()
            if "XATO" in title_upper or "ERROR" in title_upper:
                msg_type = self.TYPE_ERROR
            elif "OGOHLANTIRISH" in title_upper or "WARNING" in title_upper:
                msg_type = self.TYPE_WARNING
            elif "MUVAFFAQIYAT" in title_upper or "SUCCESS" in title_upper:
                msg_type = self.TYPE_SUCCESS
            else:
                msg_type = self.TYPE_INFO

        self._message_type = msg_type
        self._apply_container_style(msg_type)
        self._apply_text_styles(msg_type)
        self._apply_button_style(msg_type)
        self.icon_container.set_type(msg_type)

        self._resize_to_content(message)

    def _resize_to_content(self, message: str):
        """Matn hajmiga qarab dialog width/height ni dinamik hisoblash"""
        # Matn kengligini o'lchash
        fm = QFontMetrics(self.message_label.font())
        text_width = fm.horizontalAdvance(message)
        # padding (28*2) + message padding (10*2) = 76
        padding = 76

        # Kenglik: matn bir qatorga sig'sa — shu kenglik, aks holda max gacha o'sadi
        ideal_width = text_width + padding
        width = max(self.minimumWidth(), min(ideal_width, self.maximumWidth()))
        self.setFixedWidth(width)

        # Balandlik: matn necha qatorga bo'linishini hisoblash
        available_text_width = width - padding
        text_rect = fm.boundingRect(
            QRect(0, 0, available_text_width, 0),
            Qt.TextFlag.TextWordWrap,
            message,
        )
        # icon(56) + spacing(16) + title(~28) + spacing(8) + text + spacing(20) + button(48) + paddings(48)
        fixed_height = 56 + 16 + 28 + 8 + 20 + 48 + 48
        height = fixed_height + text_rect.height()
        height = max(self.minimumHeight(), min(height, self.maximumHeight()))
        self.setFixedHeight(height)

    def showEvent(self, event):
        """Modalni markazga joylash"""
        if self.parent():
            parent_rect = self.parent().geometry()
            x = parent_rect.x() + (parent_rect.width() - self.width()) // 2
            y = parent_rect.y() + (parent_rect.height() - self.height()) // 2
            self.move(x, y)
        super().showEvent(event)


class IconWidget(QWidget):
    """Custom icon widget for different message types"""

    TYPE_INFO = 0
    TYPE_WARNING = 1
    TYPE_ERROR = 2
    TYPE_SUCCESS = 3

    def __init__(self, parent=None):
        super().__init__(parent)
        self._type = self.TYPE_INFO
        self.setStyleSheet("background: transparent;")

    def set_type(self, icon_type):
        self._type = icon_type
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        w, h = self.width(), self.height()
        cx, cy = w // 2, h // 2

        # Colors based on type
        colors = {
            self.TYPE_INFO: (QColor("#dcfce7"), QColor("#22c55e"), QColor("#16a34a")),
            self.TYPE_SUCCESS: (QColor("#dcfce7"), QColor("#22c55e"), QColor("#16a34a")),
            self.TYPE_WARNING: (QColor("#fef3c7"), QColor("#f59e0b"), QColor("#d97706")),
            self.TYPE_ERROR: (QColor("#fee2e2"), QColor("#ef4444"), QColor("#dc2626"))
        }

        bg_color, stroke_color, dark_color = colors.get(self._type, colors[self.TYPE_INFO])

        # Draw background circle
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(bg_color)
        painter.drawEllipse(4, 4, w - 8, h - 8)

        # Draw icon based on type
        pen = QPen(stroke_color)
        pen.setWidth(4)
        pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
        painter.setPen(pen)
        painter.setBrush(Qt.BrushStyle.NoBrush)

        if self._type == self.TYPE_ERROR:
            # X icon
            offset = 16
            painter.drawLine(offset, offset, w - offset, h - offset)
            painter.drawLine(w - offset, offset, offset, h - offset)

        elif self._type == self.TYPE_WARNING:
            # ! icon (exclamation)
            painter.drawLine(cx, cy - 10, cx, cy + 2)
            painter.setBrush(stroke_color)
            painter.drawEllipse(cx - 3, cy + 8, 6, 6)

        elif self._type == self.TYPE_SUCCESS:
            # Checkmark
            painter.drawLine(cx - 10, cy, cx - 3, cy + 8)
            painter.drawLine(cx - 3, cy + 8, cx + 12, cy - 8)

        else:  # TYPE_INFO
            # i icon
            painter.setBrush(stroke_color)
            painter.drawEllipse(cx - 3, cy - 12, 6, 6)
            painter.setBrush(Qt.BrushStyle.NoBrush)
            painter.drawLine(cx, cy - 2, cx, cy + 12)

        painter.end()
