"""
Page Main - Bosh sahifa (test tanlash)
HTML dizayniga asoslangan - Material Design 3
"""

from PyQt6.QtCore import QSize, Qt
from PyQt6.QtGui import QColor, QFont, QIcon, QPixmap
from PyQt6.QtWidgets import (
    QComboBox,
    QFrame,
    QGraphicsDropShadowEffect,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)


class PageMain(QWidget):
    """Bosh sahifa - test tanlash"""

    # CSS Variables (from HTML)
    COLORS = {
        "bg": "#f3f7fb",
        "card": "#ffffff",
        "text": "#0f172a",
        "muted": "#64748b",
        "green": "#2f9a6d",
        "green_dark": "#1f7f5a",
        "line": "rgba(15, 23, 42, 0.10)",
    }

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("page_main")
        self._setup_ui()
        self._apply_styles()
        self._setup_connections()

    def _setup_ui(self):
        """UI elementlarini yaratish"""
        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # ============ WRAPPER ============
        wrapper = QWidget()
        wrapper.setObjectName("wrapper")
        wrapper_layout = QVBoxLayout(wrapper)
        wrapper_layout.setContentsMargins(54, 34, 54, 18)
        wrapper_layout.setSpacing(0)

        # ============ PANEL (Main container) ============
        self.panel = QFrame()
        self.panel.setObjectName("panel")
        panel_layout = QVBoxLayout(self.panel)
        panel_layout.setContentsMargins(26, 26, 26, 26)
        panel_layout.setSpacing(0)

        # Cards row (left 5/12 + right 7/12)
        cards_row = QHBoxLayout()
        cards_row.setSpacing(22)

        # ============ LEFT WRAPPER CARD (5/12 columns) ============
        self.left_wrapper_card = QFrame()
        self.left_wrapper_card.setObjectName("left_wrapper_card")
        left_wrapper_layout = QVBoxLayout(self.left_wrapper_card)
        left_wrapper_layout.setContentsMargins(16, 16, 16, 16)
        left_wrapper_layout.setSpacing(16)

        # ===== ROW 1: Header Card (Logo + Title) =====
        self.header_card = QFrame()
        self.header_card.setObjectName("header_card")
        header_card_layout = QHBoxLayout(self.header_card)
        header_card_layout.setContentsMargins(20, 16, 20, 16)
        header_card_layout.setSpacing(14)
        header_card_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        header_card_layout.addStretch()

        # Logo image
        self.logo_mark = QLabel()
        self.logo_mark.setObjectName("logo_mark")
        self._logo_pixmap = QPixmap("resources/images/logo_bba.png")
        self.logo_mark.setPixmap(
            self._logo_pixmap.scaled(
                70,
                70,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation,
            )
        )
        self.logo_mark.setFixedSize(70, 70)
        self.logo_mark.setScaledContents(False)
        self.logo_mark.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header_card_layout.addWidget(self.logo_mark, alignment=Qt.AlignmentFlag.AlignVCenter)

        # Logo text
        self.logo_t1 = QLabel("Bilim va malakalarini\nbaholash agentligi")
        self.logo_t1.setObjectName("logo_t1")
        self.logo_t1.setAlignment(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft)
        header_card_layout.addWidget(self.logo_t1, alignment=Qt.AlignmentFlag.AlignVCenter)

        header_card_layout.addStretch()

        # Stretch before cards to center vertically
        left_wrapper_layout.addStretch()

        left_wrapper_layout.addWidget(self.header_card)

        # ===== ROW 2: Test Selection Card =====
        self.card = QFrame()
        self.card.setObjectName("card")
        card_layout = QVBoxLayout(self.card)
        card_layout.setContentsMargins(22, 22, 22, 22)
        card_layout.setSpacing(0)

        # Subtitle
        self.label_sub = QLabel("PROCTORING TIZIMI")
        self.label_sub.setObjectName("label_sub")
        card_layout.addWidget(self.label_sub)

        card_layout.addSpacing(18)

        # Field title
        self.label_field = QLabel("Testni tanlang")
        self.label_field.setObjectName("label_field")
        card_layout.addWidget(self.label_field)

        card_layout.addSpacing(10)

        # Select dropdown
        self.combo_choose_test = QComboBox()
        self.combo_choose_test.setObjectName("combo_choose_test")
        self.combo_choose_test.setMinimumHeight(46)
        self.combo_choose_test.setPlaceholderText("Testni tanlang")
        card_layout.addWidget(self.combo_choose_test)

        card_layout.addSpacing(14)

        # Camera field title
        self.label_camera_field = QLabel("Kamerani tanlang")
        self.label_camera_field.setObjectName("label_camera_field")
        card_layout.addWidget(self.label_camera_field)

        card_layout.addSpacing(10)

        # Camera select row (dropdown + refresh button)
        camera_row = QHBoxLayout()
        camera_row.setSpacing(8)
        camera_row.setContentsMargins(0, 0, 0, 0)

        self.combo_choose_camera = QComboBox()
        self.combo_choose_camera.setObjectName("combo_choose_camera")
        self.combo_choose_camera.setMinimumHeight(46)
        self.combo_choose_camera.setPlaceholderText("Kamerani tanlang")
        camera_row.addWidget(self.combo_choose_camera, 1)

        self.btn_refresh_camera = QPushButton()
        self.btn_refresh_camera.setObjectName("btn_refresh_camera")
        self.btn_refresh_camera.setFixedSize(46, 46)
        self.btn_refresh_camera.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_refresh_camera.setToolTip("Kameralarni yangilash")
        self.btn_refresh_camera.setIcon(QIcon("resources/images/refresh.svg"))
        self.btn_refresh_camera.setIconSize(QSize(22, 22))
        camera_row.addWidget(self.btn_refresh_camera)

        card_layout.addLayout(camera_row)

        # Camera warning label
        self.label_camera_warning = QLabel("Iltimos, kamerani tanlang!")
        self.label_camera_warning.setObjectName("label_camera_warning")
        self.label_camera_warning.hide()
        card_layout.addWidget(self.label_camera_warning)

        card_layout.addSpacing(14)

        # Button
        self.btn_next_page = QPushButton("Davom etish")
        self.btn_next_page.setObjectName("btn_next_page")
        self.btn_next_page.setMinimumHeight(48)
        self.btn_next_page.setCursor(Qt.CursorShape.PointingHandCursor)
        card_layout.addWidget(self.btn_next_page)

        card_layout.addSpacing(14)

        # Hint
        hint_layout = QHBoxLayout()
        hint_layout.setSpacing(10)
        hint_layout.setContentsMargins(0, 0, 0, 0)
        hint_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)

        self.hint_dot = QFrame()
        self.hint_dot.setObjectName("hint_dot")
        self.hint_dot.setFixedSize(18, 18)
        hint_layout.addWidget(self.hint_dot)

        self.hint_text = QLabel("Kamera va mikrofon ruxsati talab etiladi")
        self.hint_text.setObjectName("hint_text")
        hint_layout.addWidget(self.hint_text)
        hint_layout.addStretch()

        card_layout.addLayout(hint_layout)

        left_wrapper_layout.addWidget(self.card)

        # Stretch after card to center vertically
        left_wrapper_layout.addStretch()

        cards_row.addWidget(self.left_wrapper_card, 5)  # 5/12 columns

        # ============ RIGHT IMAGE CARD (7/12 columns) ============
        self.right_card = QFrame()
        self.right_card.setObjectName("right_card")
        right_card_layout = QVBoxLayout(self.right_card)
        right_card_layout.setContentsMargins(10, 10, 10, 10)
        right_card_layout.setSpacing(0)
        right_card_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Main image - responsive with aspect ratio
        self.illus_image = QLabel()
        self.illus_image.setObjectName("illus_image")
        self._original_pixmap = QPixmap("resources/images/page_main.png")
        self.illus_image.setPixmap(self._original_pixmap)
        self.illus_image.setScaledContents(False)
        self.illus_image.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.illus_image.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding
        )
        self.illus_image.setMinimumSize(200, 150)
        right_card_layout.addWidget(self.illus_image)

        cards_row.addWidget(self.right_card, 7)  # 7/12 columns

        panel_layout.addLayout(cards_row, 1)

        # Legacy compatibility
        self.label_3 = self.right_card

        wrapper_layout.addWidget(self.panel, 1)

        main_layout.addWidget(wrapper, 1)

        # ============ FOOTER ============
        footer = QWidget()
        footer.setObjectName("footer")
        footer.setFixedHeight(58)
        footer_layout = QHBoxLayout(footer)
        footer_layout.setContentsMargins(0, 16, 0, 26)

        footer_layout.addStretch()
        self.label_footer = QLabel("UZBMB  •  Safebrowser  •  Versiya 1.0")
        self.label_footer.setObjectName("label_footer")
        footer_layout.addWidget(self.label_footer)
        footer_layout.addStretch()

        main_layout.addWidget(footer)

        # Legacy
        self.label_logo_2 = self.logo_mark
        self.label_6 = QLabel("")

    def _apply_styles(self):
        """Stylelarni qo'llash (HTML dan)"""

        # ===== PAGE BACKGROUND #f3f7fb =====
        self.setStyleSheet("""
            QWidget#page_main {
                background: qradialgradient(cx:0.7, cy:0.4, radius:0.6,
                    fx:0.7, fy:0.4,
                    stop:0 rgba(47, 154, 109, 0.10),
                    stop:1 transparent),
                    qradialgradient(cx:0.25, cy:0.3, radius:0.6,
                    fx:0.25, fy:0.3,
                    stop:0 rgba(37, 99, 235, 0.08),
                    stop:1 transparent),
                    #f3f7fb;
                background-color: #f3f7fb;
            }
        """)

        # Wrapper
        self.findChild(QWidget, "wrapper").setStyleSheet("""
            QWidget#wrapper {
                background: transparent;
            }
        """)

        # ===== LEFT WRAPPER CARD =====
        self.left_wrapper_card.setStyleSheet("""
            QFrame#left_wrapper_card {
                background: transparent;
                border: none;
                border-radius: 20px;
            }
        """)

        # ===== HEADER CARD =====
        self.header_card.setStyleSheet("""
            QFrame#header_card {
                background: #ffffff;
                border: 1px solid rgba(15, 23, 42, 0.08);
                border-radius: 16px;
            }
        """)

        # Logo image
        self.logo_mark.setStyleSheet("""
            QLabel#logo_mark {
                background: transparent;
                border: none;
            }
        """)

        # Logo t1 - bold uppercase
        self.logo_t1.setStyleSheet("""
            QLabel#logo_t1 {
                color: #0f172a;
                font-size: 20px;
                font-weight: 800;
                font-family: 'Inter', sans-serif;
                letter-spacing: 0.3px;
                text-transform: uppercase;
                background: transparent;
            }
        """)

        # ===== PANEL =====
        self.panel.setStyleSheet("""
            QFrame#panel {
                background: rgba(255, 255, 255, 0.55);
                border: 1px solid rgba(15, 23, 42, 0.06);
                border-radius: 22px;
            }
        """)

        # Panel shadow
        panel_shadow = QGraphicsDropShadowEffect()
        panel_shadow.setBlurRadius(45)
        panel_shadow.setXOffset(0)
        panel_shadow.setYOffset(18)
        panel_shadow.setColor(QColor(15, 23, 42, 30))
        self.panel.setGraphicsEffect(panel_shadow)

        # ===== LEFT CARD =====
        self.card.setStyleSheet("""
            QFrame#card {
                background: #ffffff;
                border: 1px solid rgba(15, 23, 42, 0.08);
                border-radius: 18px;
            }
        """)

        # Subtitle
        self.label_sub.setStyleSheet("""
            QLabel#label_sub {
                color: #64748b;
                font-size: 16px;
                font-weight: 600;
                font-family: 'Inter', sans-serif;
                letter-spacing: 1.7px;
                text-transform: uppercase;
                background: transparent;
            }
        """)

        # Field title
        self.label_field.setStyleSheet("""
            QLabel#label_field {
                color: #111827;
                font-size: 16px;
                font-weight: 700;
                font-family: 'Inter', sans-serif;
                background: transparent;
            }
        """)

        # Camera field title
        self.label_camera_field.setStyleSheet("""
            QLabel#label_camera_field {
                color: #111827;
                font-size: 16px;
                font-weight: 700;
                font-family: 'Inter', sans-serif;
                background: transparent;
            }
        """)

        # Camera ComboBox
        self.combo_choose_camera.setStyleSheet("""
            QComboBox#combo_choose_camera {
                background-color: #f8fafc;
                border: 2px solid #e2e8f0;
                border-radius: 12px;
                padding: 0 14px;
                font-size: 14px;
                font-weight: 500;
                font-family: 'Inter', sans-serif;
                color: #0f172a;
            }

            QComboBox#combo_choose_camera:hover {
                background-color: #ffffff;
                border: 2px solid #2f9a6d;
            }

            QComboBox#combo_choose_camera:focus,
            QComboBox#combo_choose_camera:on {
                background-color: #ffffff;
                border: 2px solid #2f9a6d;
            }

            QComboBox#combo_choose_camera::drop-down {
                subcontrol-origin: padding;
                subcontrol-position: center right;
                width: 36px;
                border: none;
                background: transparent;
            }

            QComboBox#combo_choose_camera::down-arrow {
                image: url(resources/images/arrow-down.png);
                width: 14px;
                height: 14px;
            }

            QComboBox#combo_choose_camera QAbstractItemView {
                background-color: #ffffff;
                border: 2px solid #e2e8f0;
                border-radius: 12px;
                selection-background-color: #dcfce7;
                selection-color: #0f172a;
                padding: 8px;
                outline: none;
            }

            QComboBox#combo_choose_camera QAbstractItemView::item {
                padding: 12px 14px;
                border-radius: 8px;
                min-height: 32px;
                color: #0f172a;
                background-color: transparent;
            }

            QComboBox#combo_choose_camera QAbstractItemView::item:hover {
                background-color: #f0fdf4;
            }

            QComboBox#combo_choose_camera QAbstractItemView::item:selected {
                background-color: #dcfce7;
                color: #166534;
            }
        """)

        # Refresh camera button
        self.btn_refresh_camera.setStyleSheet("""
            QPushButton#btn_refresh_camera {
                background-color: #f8fafc;
                border: 2px solid #e2e8f0;
                border-radius: 12px;
                font-size: 20px;
                color: #64748b;
            }

            QPushButton#btn_refresh_camera:hover {
                background-color: #ffffff;
                border: 2px solid #2f9a6d;
                color: #2f9a6d;
            }

            QPushButton#btn_refresh_camera:pressed {
                background-color: #f0fdf4;
                border: 2px solid #1f7f5a;
                color: #1f7f5a;
            }
        """)

        # Camera warning label
        self.label_camera_warning.setStyleSheet("""
            QLabel#label_camera_warning {
                color: #dc2626;
                font-size: 13px;
                font-weight: 600;
                font-family: 'Inter', sans-serif;
                background: transparent;
                padding: 4px 0px;
            }
        """)

        # ComboBox
        self.combo_choose_test.setStyleSheet("""
            QComboBox#combo_choose_test {
                background-color: #f8fafc;
                border: 2px solid #e2e8f0;
                border-radius: 12px;
                padding: 0 14px;
                font-size: 14px;
                font-weight: 500;
                font-family: 'Inter', sans-serif;
                color: #0f172a;
            }

            QComboBox#combo_choose_test:hover {
                background-color: #ffffff;
                border: 2px solid #2f9a6d;
            }

            QComboBox#combo_choose_test:focus,
            QComboBox#combo_choose_test:on {
                background-color: #ffffff;
                border: 2px solid #2f9a6d;
            }

            QComboBox#combo_choose_test::drop-down {
                subcontrol-origin: padding;
                subcontrol-position: center right;
                width: 36px;
                border: none;
                background: transparent;
            }

            QComboBox#combo_choose_test::down-arrow {
                image: url(resources/images/arrow-down.png);
                width: 14px;
                height: 14px;
            }

            QComboBox#combo_choose_test QAbstractItemView {
                background-color: #ffffff;
                border: 2px solid #e2e8f0;
                border-radius: 12px;
                selection-background-color: #dcfce7;
                selection-color: #0f172a;
                padding: 8px;
                outline: none;
            }

            QComboBox#combo_choose_test QAbstractItemView::item {
                padding: 12px 14px;
                border-radius: 8px;
                min-height: 32px;
                color: #0f172a;
                background-color: transparent;
            }

            QComboBox#combo_choose_test QAbstractItemView::item:hover {
                background-color: #f0fdf4;
            }

            QComboBox#combo_choose_test QAbstractItemView::item:selected {
                background-color: #dcfce7;
                color: #166534;
            }
        """)

        # Button - green gradient
        self.btn_next_page.setStyleSheet("""
            QPushButton#btn_next_page {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #2f9a6d, stop:1 #1f7f5a);
                color: #ffffff;
                border: none;
                border-radius: 12px;
                font-size: 15px;
                font-weight: 800;
                font-family: 'Inter', sans-serif;
                letter-spacing: 0.2px;
            }

            QPushButton#btn_next_page:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #34a876, stop:1 #2f9a6d);
            }

            QPushButton#btn_next_page:pressed {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #1f7f5a, stop:1 #1b7b56);
            }
        """)

        # Button shadow
        btn_shadow = QGraphicsDropShadowEffect()
        btn_shadow.setBlurRadius(24)
        btn_shadow.setXOffset(0)
        btn_shadow.setYOffset(12)
        btn_shadow.setColor(QColor(47, 154, 109, 64))
        self.btn_next_page.setGraphicsEffect(btn_shadow)

        # Hint dot
        self.hint_dot.setStyleSheet("""
            QFrame#hint_dot {
                background: rgba(47, 154, 109, 0.10);
                border: 1px solid rgba(47, 154, 109, 0.18);
                border-radius: 8px;
            }
        """)

        # Hint text
        self.hint_text.setStyleSheet("""
            QLabel#hint_text {
                color: #64748b;
                font-size: 13px;
                font-weight: 400;
                font-family: 'Inter', sans-serif;
                line-height: 1.35;
                background: transparent;
            }
        """)


        # ===== RIGHT IMAGE CARD =====
        self.right_card.setStyleSheet("""
            QFrame#right_card {
                background: transparent;
                border: none;
                border-radius: 20px;
            }
        """)

        # Image style
        self.illus_image.setStyleSheet("""
            QLabel#illus_image {
                background: transparent;
                border-radius: 18px;
            }
        """)

        # ===== FOOTER =====
        self.findChild(QWidget, "footer").setStyleSheet("""
            QWidget#footer {
                background: transparent;
            }
        """)

        # Footer text
        self.label_footer.setStyleSheet("""
            QLabel#label_footer {
                color: rgba(100, 116, 139, 0.9);
                font-size: 13px;
                font-weight: 600;
                font-family: 'Inter', sans-serif;
                background: transparent;
            }
        """)

    def resizeEvent(self, event):
        """Rasmni ekranga mos ravishda o'lchamlash"""
        super().resizeEvent(event)
        self._update_image_size()

    def showEvent(self, event):
        """Sahifa ko'rsatilganda rasmni yangilash"""
        super().showEvent(event)
        self._update_image_size()

    def _update_image_size(self):
        """Rasmni aspect ratio saqlab o'lchamlash"""
        if hasattr(self, "_original_pixmap") and not self._original_pixmap.isNull():
            available_size = self.illus_image.size()
            scaled_pixmap = self._original_pixmap.scaled(
                available_size,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation,
            )
            self.illus_image.setPixmap(scaled_pixmap)

    def _setup_connections(self):
        """Signallarni ulash"""
        self.combo_choose_camera.currentIndexChanged.connect(self._on_camera_changed)

    def _on_camera_changed(self):
        """Kamera tanlanganda warningni yashirish"""
        camera_data = self.combo_choose_camera.currentData()
        if camera_data is not None and camera_data != -1:
            self.label_camera_warning.hide()

    def validate_camera(self):
        """Kamera tanlanganligini tekshirish. True - tanlangan, False - tanlanmagan"""
        camera_data = self.combo_choose_camera.currentData()
        if camera_data is None or camera_data == -1:
            self.label_camera_warning.show()
            return False
        self.label_camera_warning.hide()
        return True
