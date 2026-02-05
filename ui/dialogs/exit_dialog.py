"""
Exit Dialog
Dasturdan chiqish uchun parol dialog - Material Design 3 style
Yashil (mint) rangga urg'u berilgan
"""
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QPushButton, QFrame, QWidget
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor
from PyQt6.QtWidgets import QGraphicsDropShadowEffect

from utils.graphics import create_lock_icon


class ExitDialog(QDialog):
    """
    Dasturdan chiqish uchun Material Design 3 parol dialog
    Yashil tema bilan
    """

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowTitle("Chiqish")
        self.setWindowModality(Qt.WindowModality.ApplicationModal)
        self.setWindowFlags(
            Qt.WindowType.Dialog |
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint
        )
        # Transparent background for proper border-radius
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setFixedSize(480, 400)

        self._setup_ui()

    def _setup_ui(self):
        # Main layout (no margins - container handles it)
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # ============ CONTAINER (visible modal) ============
        container = QFrame()
        container.setObjectName("modal_container")
        container.setStyleSheet("""
            QFrame#modal_container {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #f0fdf4,
                    stop:0.5 #ecfdf5,
                    stop:1 #e6f7ed);
                border: 2px solid rgba(34, 197, 94, 0.3);
                border-radius: 28px;
            }
        """)

        # Container shadow
        container_shadow = QGraphicsDropShadowEffect()
        container_shadow.setBlurRadius(40)
        container_shadow.setXOffset(0)
        container_shadow.setYOffset(12)
        container_shadow.setColor(QColor(0, 0, 0, 40))
        container.setGraphicsEffect(container_shadow)

        layout = QVBoxLayout(container)
        layout.setContentsMargins(32, 28, 32, 28)
        layout.setSpacing(0)

        main_layout.addWidget(container)

        # ============ ICON SECTION ============
        icon_widget = QWidget()
        icon_widget.setStyleSheet("background: transparent;")
        icon_layout = QHBoxLayout(icon_widget)
        icon_layout.setContentsMargins(0, 0, 0, 0)
        icon_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Icon container - Material Design 3 tonal style
        icon_container = QFrame()
        icon_container.setFixedSize(72, 72)
        icon_container.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #dcfce7,
                    stop:1 #bbf7d0);
                border: 2px solid rgba(34, 197, 94, 0.3);
                border-radius: 20px;
            }
        """)

        # Icon shadow
        icon_shadow = QGraphicsDropShadowEffect()
        icon_shadow.setBlurRadius(20)
        icon_shadow.setXOffset(0)
        icon_shadow.setYOffset(8)
        icon_shadow.setColor(QColor(34, 197, 94, 50))
        icon_container.setGraphicsEffect(icon_shadow)

        # Lock icon inside container
        icon_label = QLabel(icon_container)
        icon_label.setFixedSize(72, 72)
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lock_pixmap = create_lock_icon(36, 36, color="#16a34a")
        icon_label.setPixmap(lock_pixmap)
        icon_label.setStyleSheet("background: transparent; border: none;")

        icon_layout.addWidget(icon_container)
        layout.addWidget(icon_widget)

        layout.addSpacing(20)

        # ============ TEXT SECTION ============
        text_widget = QWidget()
        text_widget.setStyleSheet("background: transparent;")
        text_layout = QVBoxLayout(text_widget)
        text_layout.setContentsMargins(0, 0, 0, 0)
        text_layout.setSpacing(8)

        # Title
        title_label = QLabel("Dasturdan chiqish")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet("""
            QLabel {
                font-size: 24px;
                font-weight: 700;
                color: #14532d;
                font-family: 'Inter', 'Segoe UI', sans-serif;
                background: transparent;
            }
        """)
        text_layout.addWidget(title_label)

        # Subtitle
        subtitle_label = QLabel("Davom etish uchun admin parolini kiriting")
        subtitle_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle_label.setStyleSheet("""
            QLabel {
                font-size: 14px;
                font-weight: 500;
                color: #166534;
                font-family: 'Inter', 'Segoe UI', sans-serif;
                background: transparent;
            }
        """)
        text_layout.addWidget(subtitle_label)

        layout.addWidget(text_widget)

        layout.addSpacing(24)

        # ============ INPUT SECTION ============
        input_widget = QWidget()
        input_widget.setStyleSheet("background: transparent;")
        input_layout = QVBoxLayout(input_widget)
        input_layout.setContentsMargins(0, 0, 0, 0)
        input_layout.setSpacing(10)

        # Password field container - Material Design outlined style
        field_container = QFrame()
        field_container.setStyleSheet("""
            QFrame {
                background: #ffffff;
                border: 2px solid #86efac;
                border-radius: 16px;
            }
            QFrame:focus-within {
                border-color: #22c55e;
            }
        """)

        # Field shadow
        field_shadow = QGraphicsDropShadowEffect()
        field_shadow.setBlurRadius(16)
        field_shadow.setXOffset(0)
        field_shadow.setYOffset(4)
        field_shadow.setColor(QColor(34, 197, 94, 25))
        field_container.setGraphicsEffect(field_shadow)

        field_layout = QHBoxLayout(field_container)
        field_layout.setContentsMargins(0, 0, 0, 0)

        # Password input
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Admin paroli")
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_input.setFixedHeight(56)
        self.password_input.setStyleSheet("""
            QLineEdit {
                background: transparent;
                border: none;
                padding: 0 20px;
                font-size: 16px;
                font-weight: 600;
                color: #14532d;
                font-family: 'Inter', 'Segoe UI', sans-serif;
            }
            QLineEdit::placeholder {
                color: #86efac;
                font-weight: 500;
            }
            QLineEdit:focus {
                color: #166534;
            }
        """)
        self.password_input.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.password_input.returnPressed.connect(self.accept)
        field_layout.addWidget(self.password_input)

        input_layout.addWidget(field_container)

        # Helper text
        helper_label = QLabel("Parolni kiritib \"Chiqish\" tugmasini bosing")
        helper_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        helper_label.setStyleSheet("""
            QLabel {
                font-size: 12px;
                font-weight: 500;
                color: #4ade80;
                font-family: 'Inter', 'Segoe UI', sans-serif;
                background: transparent;
                padding-top: 4px;
            }
        """)
        input_layout.addWidget(helper_label)

        layout.addWidget(input_widget)

        layout.addSpacing(24)

        # ============ BUTTONS SECTION ============
        buttons_widget = QWidget()
        buttons_widget.setStyleSheet("background: transparent;")
        buttons_layout = QHBoxLayout(buttons_widget)
        buttons_layout.setContentsMargins(0, 0, 0, 0)
        buttons_layout.setSpacing(16)

        # Cancel button - Material Design outlined style
        btn_cancel = QPushButton("Bekor qilish")
        btn_cancel.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_cancel.setFixedHeight(52)
        btn_cancel.setMinimumWidth(140)
        btn_cancel.setStyleSheet("""
            QPushButton {
                background: transparent;
                color: #16a34a;
                border: 2px solid #86efac;
                border-radius: 14px;
                font-size: 15px;
                font-weight: 700;
                font-family: 'Inter', 'Segoe UI', sans-serif;
            }
            QPushButton:hover {
                background: #f0fdf4;
                border-color: #4ade80;
            }
            QPushButton:pressed {
                background: #dcfce7;
                border-color: #22c55e;
            }
        """)
        btn_cancel.clicked.connect(self.reject)
        buttons_layout.addWidget(btn_cancel)

        # Confirm button - Material Design filled style (green)
        btn_confirm = QPushButton("Chiqish")
        btn_confirm.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_confirm.setFixedHeight(52)
        btn_confirm.setMinimumWidth(140)
        btn_confirm.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #22c55e, stop:1 #16a34a);
                color: #ffffff;
                border: none;
                border-radius: 14px;
                font-size: 15px;
                font-weight: 700;
                font-family: 'Inter', 'Segoe UI', sans-serif;
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

        # Confirm button shadow
        confirm_shadow = QGraphicsDropShadowEffect()
        confirm_shadow.setBlurRadius(20)
        confirm_shadow.setXOffset(0)
        confirm_shadow.setYOffset(6)
        confirm_shadow.setColor(QColor(34, 197, 94, 80))
        btn_confirm.setGraphicsEffect(confirm_shadow)
        btn_confirm.clicked.connect(self.accept)
        buttons_layout.addWidget(btn_confirm)

        layout.addWidget(buttons_widget)

    def get_password(self) -> str:
        """Kiritilgan parolni olish"""
        return self.password_input.text()

    def showEvent(self, event):
        """Dialog ko'rsatilganda"""
        if self.parent():
            parent_geometry = self.parent().geometry()
            x = parent_geometry.x() + (parent_geometry.width() - self.width()) // 2
            y = parent_geometry.y() + (parent_geometry.height() - self.height()) // 2
            self.move(x, y)
        self.password_input.setFocus()
        self.password_input.clear()
        super().showEvent(event)
