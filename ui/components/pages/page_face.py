"""
Page Face - Nomzod yuz tekshiruvi sahifasi
Modern Glassmorphism UI - page_home.py uslubida
Soft shadows, frosted glass effect, minimalist aesthetic, 4k
"""

from PyQt6.QtCore import (
    QEasingCurve,
    QPropertyAnimation,
    QRect,
    QRectF,
    QSequentialAnimationGroup,
    Qt,
    QTimer,
)
from PyQt6.QtGui import QBrush, QColor, QPainter, QPainterPath, QPen, QPixmap
from PyQt6.QtWidgets import (
    QFrame,
    QGraphicsDropShadowEffect,
    QGraphicsOpacityEffect,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)


class ScanLine(QWidget):
    """Animated scan line with glow effect for camera"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("scan_line")
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

    def paintEvent(self, event):
        """Custom paint with glow effect"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        width = self.width()
        height = self.height()
        center_y = height // 2

        # Draw multiple glow layers (outer to inner)
        glow_layers = [
            (16, QColor(102, 210, 176, 25)),
            (12, QColor(102, 210, 176, 40)),
            (8, QColor(102, 210, 176, 60)),
            (5, QColor(102, 210, 176, 90)),
            (3, QColor(116, 214, 182, 140)),
        ]

        for blur_height, color in glow_layers:
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(QBrush(color))
            rect = QRectF(0, center_y - blur_height / 2, width, blur_height)
            painter.drawRoundedRect(rect, blur_height / 2, blur_height / 2)

        # Draw main bright line
        painter.setBrush(QBrush(QColor(150, 230, 210, 220)))
        main_rect = QRectF(0, center_y - 1.5, width, 3)
        painter.drawRoundedRect(main_rect, 1.5, 1.5)

        # Draw center highlight (white core)
        painter.setBrush(QBrush(QColor(255, 255, 255, 180)))
        highlight_rect = QRectF(width * 0.1, center_y - 0.5, width * 0.8, 1)
        painter.drawRoundedRect(highlight_rect, 0.5, 0.5)

        painter.end()

    def start_animation(self, parent_height):
        """Start the scan animation"""
        width = self.parent().width() - 20
        line_height = 36
        start_y = 14
        end_y = parent_height - 20

        self.anim_group = QSequentialAnimationGroup(self)

        self.anim_forward = QPropertyAnimation(self, b"geometry")
        self.anim_forward.setDuration(1800)
        self.anim_forward.setStartValue(QRect(10, start_y, width, line_height))
        self.anim_forward.setEndValue(QRect(10, end_y - line_height, width, line_height))
        self.anim_forward.setEasingCurve(QEasingCurve.Type.InOutQuad)

        self.anim_backward = QPropertyAnimation(self, b"geometry")
        self.anim_backward.setDuration(1800)
        self.anim_backward.setStartValue(QRect(10, end_y - line_height, width, line_height))
        self.anim_backward.setEndValue(QRect(10, start_y, width, line_height))
        self.anim_backward.setEasingCurve(QEasingCurve.Type.InOutQuad)

        self.anim_group.addAnimation(self.anim_forward)
        self.anim_group.addAnimation(self.anim_backward)
        self.anim_group.setLoopCount(-1)
        self.anim_group.start()

    def stop_animation(self):
        """Stop the scan animation"""
        if hasattr(self, "anim_group"):
            self.anim_group.stop()


class RoundedLabel(QLabel):
    """QLabel with rounded corners that clips pixmap content"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._border_radius = 12
        self._border_color = QColor(102, 210, 176, 153)
        self._border_width = 2

    def setBorderRadius(self, radius):
        self._border_radius = radius
        self.update()

    def setBorderColor(self, color):
        self._border_color = color
        self.update()

    def setBorderWidth(self, width):
        self._border_width = width
        self.update()

    def paintEvent(self, event):
        if self.pixmap() and not self.pixmap().isNull():
            painter = QPainter(self)
            painter.setRenderHint(QPainter.RenderHint.Antialiasing)

            border_offset = self._border_width / 2
            rect = QRectF(
                border_offset,
                border_offset,
                self.width() - self._border_width,
                self.height() - self._border_width,
            )

            path = QPainterPath()
            path.addRoundedRect(rect, self._border_radius, self._border_radius)
            painter.setClipPath(path)

            scaled_pixmap = self.pixmap().scaled(
                self.size(),
                Qt.AspectRatioMode.KeepAspectRatioByExpanding,
                Qt.TransformationMode.SmoothTransformation,
            )

            x = (self.width() - scaled_pixmap.width()) // 2
            y = (self.height() - scaled_pixmap.height()) // 2
            painter.drawPixmap(x, y, scaled_pixmap)

            painter.setClipping(False)
            pen = QPen(self._border_color, self._border_width)
            painter.setPen(pen)
            painter.setBrush(Qt.BrushStyle.NoBrush)
            painter.drawRoundedRect(rect, self._border_radius, self._border_radius)

            painter.end()
        else:
            super().paintEvent(event)


class PageFace(QWidget):
    """Nomzod yuz tekshiruvi sahifasi - Modern Glassmorphism"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("page_face")
        self._setup_ui()
        self._apply_styles()
        self._setup_animations()

    def _setup_ui(self):
        """UI elementlarini yaratish"""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        main_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # ============ STAGE (Main Container) ============
        self.stage = QFrame()
        self.stage.setObjectName("stage")
        self.stage.setMinimumSize(1000, 640)
        self.stage.setMaximumSize(1180, 800)
        stage_layout = QVBoxLayout(self.stage)
        stage_layout.setContentsMargins(0, 0, 0, 0)
        stage_layout.setSpacing(0)

        # ============ HEADER ============
        header_widget = QWidget()
        header_widget.setObjectName("header_widget")
        header_widget.setFixedHeight(100)
        header_layout = QVBoxLayout(header_widget)
        header_layout.setContentsMargins(24, 20, 24, 20)
        header_layout.setSpacing(4)
        header_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Header title
        self.label_face_check = QLabel("Talabgorni yuz tekshiruvidan o'tkazish")
        self.label_face_check.setObjectName("label_header_title")
        self.label_face_check.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header_layout.addWidget(self.label_face_check)

        # Header subtitle
        self.label_header_subtitle = QLabel("FACE ID tekshiruvi")
        self.label_header_subtitle.setObjectName("label_header_subtitle")
        self.label_header_subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header_layout.addWidget(self.label_header_subtitle)

        stage_layout.addWidget(header_widget)

        # ============ CONTENT ============
        content_widget = QWidget()
        content_widget.setObjectName("content_widget")
        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(24, 16, 24, 24)
        content_layout.setSpacing(0)
        content_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # ============ PANEL ============
        self.panel = QFrame()
        self.panel.setObjectName("panel")
        panel_layout = QVBoxLayout(self.panel)
        panel_layout.setContentsMargins(20, 16, 20, 16)
        panel_layout.setSpacing(12)

        # ============ CARDS GRID (8:4) ============
        cards_widget = QWidget()
        cards_widget.setObjectName("cards_widget")
        cards_widget.setFixedHeight(500)  # Fixed height - button ta'sir qilmasligi uchun
        cards_layout = QHBoxLayout(cards_widget)
        cards_layout.setContentsMargins(8, 8, 8, 8)
        cards_layout.setSpacing(20)
        cards_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # ===== LEFT COLUMN (8fr) - Camera + Result =====
        left_column = QWidget()
        left_column.setObjectName("left_column")
        left_column_layout = QVBoxLayout(left_column)
        left_column_layout.setContentsMargins(0, 0, 0, 0)
        left_column_layout.setSpacing(12)

        # ===== CAMERA WRAP =====
        self.camera_wrap = QFrame()
        self.camera_wrap.setObjectName("camera_wrap")
        camera_wrap_layout = QVBoxLayout(self.camera_wrap)
        camera_wrap_layout.setContentsMargins(5, 5, 5, 5)
        camera_wrap_layout.setSpacing(0)

        # Glow frame
        self.glow_frame = QFrame()
        self.glow_frame.setObjectName("glow_frame")
        glow_layout = QVBoxLayout(self.glow_frame)
        glow_layout.setContentsMargins(8, 8, 8, 8)
        glow_layout.setSpacing(0)
        glow_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Video label (camera feed) - RoundedLabel for border-radius clipping
        self.label_video_box = RoundedLabel()
        self.label_video_box.setObjectName("label_video_box")
        self.label_video_box.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding
        )
        self.label_video_box.setAlignment(Qt.AlignmentFlag.AlignCenter)
        glow_layout.addWidget(self.label_video_box)

        # Scan line overlay
        self.scan_line = ScanLine(self.label_video_box)
        self.scan_line.setFixedHeight(33)
        self.scan_line.raise_()

        camera_wrap_layout.addWidget(self.glow_frame)
        left_column_layout.addWidget(self.camera_wrap, 1)

        # ===== RESULT RESPONSE CARD =====
        self.result_card = QFrame()
        self.result_card.setObjectName("result_card")
        self.result_card.setFixedHeight(45)
        result_card_layout = QHBoxLayout(self.result_card)
        result_card_layout.setContentsMargins(16, 8, 16, 8)
        result_card_layout.setSpacing(12)
        result_card_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Result pulse dot
        self.result_pulse_dot = QFrame()
        self.result_pulse_dot.setObjectName("result_pulse_dot")
        self.result_pulse_dot.setFixedSize(10, 10)
        result_card_layout.addWidget(self.result_pulse_dot)

        # Result label
        self.label_result_response = QLabel("Yuzingizni kameraga qarating...")
        self.label_result_response.setObjectName("label_result_response")
        self.label_result_response.setAlignment(Qt.AlignmentFlag.AlignCenter)
        result_card_layout.addWidget(self.label_result_response, 1)

        left_column_layout.addWidget(self.result_card)

        cards_layout.addWidget(left_column, 8)

        # ===== FACE CARD (4fr) =====
        self.face_card = QFrame()
        self.face_card.setObjectName("face_card")
        face_card_layout = QVBoxLayout(self.face_card)
        face_card_layout.setContentsMargins(14, 14, 14, 14)
        face_card_layout.setSpacing(0)
        face_card_layout.setAlignment(
            Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignVCenter
        )

        # Face Icon container
        self.face_icon = QFrame()
        self.face_icon.setObjectName("face_icon")
        face_icon_layout = QVBoxLayout(self.face_icon)
        face_icon_layout.setContentsMargins(8, 8, 8, 8)
        face_icon_layout.setAlignment(
            Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignVCenter
        )

        # Face illustration (PNG with face landmarks)
        self.label_illustration = QLabel()
        self.label_illustration.setObjectName("label_illustration")
        self.label_illustration.setPixmap(QPixmap("resources/images/face_icon.png"))
        self.label_illustration.setScaledContents(True)
        self.label_illustration.setFixedSize(240, 340)
        self.label_illustration.setAlignment(Qt.AlignmentFlag.AlignCenter)
        face_icon_layout.addWidget(self.label_illustration)

        face_card_layout.addWidget(self.face_icon)
        cards_layout.addWidget(self.face_card, 4)

        panel_layout.addWidget(cards_widget)

        # Legacy attribute - eski kod bilan moslik uchun
        self.label_result_face_candidate = self.label_result_response
        self.pulse_dot = self.result_pulse_dot

        # ============ BUTTON ============
        button_container = QWidget()
        button_container.setObjectName("button_container")
        button_container.setFixedHeight(80)  # Fixed height - har doim joy bo'lishi uchun
        button_container.setStyleSheet("background: transparent;")
        button_layout = QHBoxLayout(button_container)
        button_layout.setContentsMargins(0, 8, 0, 8)
        button_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.btn_candidate_next = QPushButton("Davom etish  →")
        self.btn_candidate_next.setObjectName("btn_submit")
        self.btn_candidate_next.setFixedSize(260, 56)
        self.btn_candidate_next.setCursor(Qt.CursorShape.PointingHandCursor)
        button_layout.addWidget(self.btn_candidate_next)

        panel_layout.addWidget(button_container)

        content_layout.addWidget(self.panel)
        stage_layout.addWidget(content_widget, 1)
        main_layout.addWidget(self.stage)


    def _setup_animations(self):
        """Setup animations"""
        QTimer.singleShot(500, self._start_scan_animation)
        self._setup_pulse_animation()

    def _start_scan_animation(self):
        """Start scan line animation"""
        if hasattr(self, "scan_line") and self.label_video_box.height() > 0:
            self.scan_line.start_animation(self.label_video_box.height())

    def _setup_pulse_animation(self):
        """Setup pulse dot animation"""
        self.pulse_opacity_effect = QGraphicsOpacityEffect(self.pulse_dot)
        self.pulse_dot.setGraphicsEffect(self.pulse_opacity_effect)

        self.pulse_anim_group = QSequentialAnimationGroup(self)

        self.pulse_fade_out = QPropertyAnimation(self.pulse_opacity_effect, b"opacity")
        self.pulse_fade_out.setDuration(800)
        self.pulse_fade_out.setStartValue(1.0)
        self.pulse_fade_out.setEndValue(0.3)
        self.pulse_fade_out.setEasingCurve(QEasingCurve.Type.InOutSine)

        self.pulse_fade_in = QPropertyAnimation(self.pulse_opacity_effect, b"opacity")
        self.pulse_fade_in.setDuration(800)
        self.pulse_fade_in.setStartValue(0.3)
        self.pulse_fade_in.setEndValue(1.0)
        self.pulse_fade_in.setEasingCurve(QEasingCurve.Type.InOutSine)

        self.pulse_anim_group.addAnimation(self.pulse_fade_out)
        self.pulse_anim_group.addAnimation(self.pulse_fade_in)
        self.pulse_anim_group.setLoopCount(-1)
        self.pulse_anim_group.start()

    def showEvent(self, event):
        """Handle show event"""
        super().showEvent(event)
        QTimer.singleShot(100, self._start_scan_animation)
        if hasattr(self, "pulse_anim_group"):
            self.pulse_anim_group.start()

    def hideEvent(self, event):
        """Handle hide event"""
        super().hideEvent(event)
        if hasattr(self, "scan_line"):
            self.scan_line.stop_animation()
        if hasattr(self, "pulse_anim_group"):
            self.pulse_anim_group.stop()

    def _apply_styles(self):
        """Modern Glassmorphism styles - page_home.py uslubida"""

        # ===== PAGE BACKGROUND =====
        self.setStyleSheet("""
            QWidget#page_face {
                background: qradialgradient(cx:0.3, cy:0.25, radius:0.6,
                    fx:0.3, fy:0.25,
                    stop:0 rgba(102, 210, 176, 0.20),
                    stop:1 transparent),
                    qradialgradient(cx:0.7, cy:0.35, radius:0.6,
                    fx:0.7, fy:0.35,
                    stop:0 rgba(116, 214, 182, 0.18),
                    stop:1 transparent),
                    qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #eef9f5, stop:1 #e6f5f0);
                background-color: #eef9f5;
            }
        """)

        # ===== STAGE =====
        self.stage.setStyleSheet("""
            QFrame#stage {
                background: rgba(255, 255, 255, 0.55);
                border: 1px solid rgba(102, 210, 176, 0.30);
                border-radius: 26px;
            }
        """)

        # Stage shadow
        stage_shadow = QGraphicsDropShadowEffect()
        stage_shadow.setBlurRadius(60)
        stage_shadow.setXOffset(0)
        stage_shadow.setYOffset(26)
        stage_shadow.setColor(QColor(0, 0, 0, 46))
        self.stage.setGraphicsEffect(stage_shadow)

        # ===== HEADER =====
        self.findChild(QWidget, "header_widget").setStyleSheet("""
            QWidget#header_widget {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 rgba(102, 210, 176, 0.18),
                    stop:1 rgba(255, 255, 255, 0.12));
                border-bottom: 1px solid rgba(102, 210, 176, 0.25);
                border-top-left-radius: 26px;
                border-top-right-radius: 26px;
            }
        """)

        # Header title
        self.label_face_check.setStyleSheet("""
            QLabel#label_header_title {
                color: #1a3a3a;
                font-size: 22px;
                font-weight: 700;
                font-family: 'Inter', sans-serif;
                background: transparent;
                letter-spacing: 0.3px;
            }
        """)

        # Header subtitle
        self.label_header_subtitle.setStyleSheet("""
            QLabel#label_header_subtitle {
                color: #1a3a3a;
                font-size: 22px;
                font-weight: 900;
                font-family: 'Inter', sans-serif;
                background: transparent;
                letter-spacing: 0.5px;
            }
        """)

        # ===== CONTENT =====
        self.findChild(QWidget, "content_widget").setStyleSheet("""
            QWidget#content_widget {
                background: transparent;
            }
        """)

        # ===== PANEL =====
        self.panel.setStyleSheet("""
            QFrame#panel {
                background: rgba(255, 255, 255, 0.45);
                border: 1px solid rgba(102, 210, 176, 0.20);
                border-radius: 22px;
            }
        """)

        # ===== LEFT COLUMN =====
        self.findChild(QWidget, "left_column").setStyleSheet("""
            QWidget#left_column {
                background: transparent;
            }
        """)

        # ===== CAMERA WRAP =====
        self.camera_wrap.setStyleSheet("""
            QFrame#camera_wrap {
                background: rgba(255, 255, 255, 0.55);
                border: 1px solid rgba(102, 210, 176, 0.25);
                border-radius: 18px;
            }
        """)

        # ===== GLOW FRAME =====
        self.glow_frame.setStyleSheet("""
            QFrame#glow_frame {
                background: rgba(46, 154, 120, 0.08);
                border: 2px solid rgba(102, 210, 176, 0.9);
                border-radius: 16px;
            }
        """)

        # Glow shadow
        glow_shadow = QGraphicsDropShadowEffect()
        glow_shadow.setBlurRadius(26)
        glow_shadow.setXOffset(0)
        glow_shadow.setYOffset(0)
        glow_shadow.setColor(QColor(102, 210, 176, 153))
        self.glow_frame.setGraphicsEffect(glow_shadow)

        # ===== VIDEO BOX =====
        self.label_video_box.setStyleSheet("""
            QLabel#label_video_box {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #3a3a3a, stop:1 #777777);
                border-radius: 10px;
                border: 2px solid rgba(102, 210, 176, 0.9);
            }
        """)

        # ===== FACE CARD =====
        self.face_card.setStyleSheet("""
            QFrame#face_card {
                background: rgba(255, 255, 255, 0.35);
                border: none;
                border-radius: 18px;
            }
        """)

        # ===== FACE ICON =====
        self.face_icon.setStyleSheet("""
            QFrame#face_icon {
                background: transparent;
                border: none;
            }
        """)

        # ===== ILLUSTRATION =====
        self.label_illustration.setStyleSheet("""
            QLabel#label_illustration {
                background: transparent;
            }
        """)

        # ===== RESULT CARD =====
        self.result_card.setStyleSheet("""
            QFrame#result_card {
                border-radius: 10px;
            }
        """)

        # Result card shadow
        result_shadow = QGraphicsDropShadowEffect()
        result_shadow.setBlurRadius(16)
        result_shadow.setXOffset(0)
        result_shadow.setYOffset(4)
        result_shadow.setColor(QColor(102, 210, 176, 60))
        self.result_card.setGraphicsEffect(result_shadow)

        # ===== RESULT PULSE DOT =====
        self.result_pulse_dot.setStyleSheet("""
            QFrame#result_pulse_dot {
                background: #74D6B6;
                border-radius: 5px;
            }
        """)

        # ===== RESULT LABEL =====
        self.label_result_response.setStyleSheet("""
            QLabel#label_result_response {
                color: #234b4b;
                font-size: 16px;
                font-weight: 500;
                font-family: 'Inter', sans-serif;
                background: transparent;
                border-radius: 10px;
            }
        """)

        # ===== BUTTON - page_main.py uslubida =====
        self.btn_candidate_next.setStyleSheet("""
            QPushButton#btn_submit {
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

            QPushButton#btn_submit:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #34a876, stop:1 #2f9a6d);
            }

            QPushButton#btn_submit:pressed {
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
        self.btn_candidate_next.setGraphicsEffect(btn_shadow)
