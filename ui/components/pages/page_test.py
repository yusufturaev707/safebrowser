"""
Page Test - Test sahifasi (WebView)
Material Design 3 Style
"""

from PyQt6.QtWidgets import (
    QWidget, QGridLayout, QVBoxLayout
)


class PageTest(QWidget):
    """Test sahifasi - WebView shu yerga qo'shiladi"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("page_test")
        self._setup_ui()
        self._apply_styles()

    def _setup_ui(self):
        """UI elementlarini yaratish"""
        # Main grid layout
        self.gridLayout_2 = QGridLayout(self)
        self.gridLayout_2.setContentsMargins(0, 0, 0, 0)
        self.gridLayout_2.setSpacing(0)
        self.gridLayout_2.setObjectName("gridLayout_2")

        # Test layout - WebView shu yerga qo'shiladi
        self.layout_test = QVBoxLayout()
        self.layout_test.setObjectName("layout_test")
        self.layout_test.setContentsMargins(0, 0, 0, 0)
        self.layout_test.setSpacing(0)

        self.gridLayout_2.addLayout(self.layout_test, 0, 0, 1, 1)

    def _apply_styles(self):
        """Material Design 3 stylelarni qo'llash"""
        # Page background - Clean white for WebView
        self.setStyleSheet("""
            QWidget#page_test {
                background: #ffffff;
                border-radius: 0px;
            }
        """)
