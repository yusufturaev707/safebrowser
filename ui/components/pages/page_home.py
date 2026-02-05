"""
Page Home - Xodim yuz tekshiruvi sahifasi
HTML page2.html dizayniga asoslangan
"""

from PyQt6.QtCore import (
    QEasingCurve,
    QPropertyAnimation,
    QRect,
    QRectF,
    QSequentialAnimationGroup,
    QSize,
    Qt,
    QTimer,
    pyqtProperty,
)
from PyQt6.QtGui import QBrush, QColor, QFont, QPainter, QPainterPath, QPen, QPixmap
from PyQt6.QtWidgets import (
    QFrame,
    QGraphicsDropShadowEffect,
    QGraphicsOpacityEffect,
    QHBoxLayout,
    QLabel,
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
        line_height = 36  # Taller for glow effect
        start_y = 14
        end_y = parent_height - 20

        # Create animation group for smooth back and forth
        self.anim_group = QSequentialAnimationGroup(self)

        # Forward animation
        self.anim_forward = QPropertyAnimation(self, b"geometry")
        self.anim_forward.setDuration(1800)
        self.anim_forward.setStartValue(QRect(10, start_y, width, line_height))
        self.anim_forward.setEndValue(QRect(10, end_y - line_height, width, line_height))
        self.anim_forward.setEasingCurve(QEasingCurve.Type.InOutQuad)

        # Backward animation
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

            # Create rounded rect
            border_offset = self._border_width / 2
            rect = QRectF(
                border_offset,
                border_offset,
                self.width() - self._border_width,
                self.height() - self._border_width,
            )

            # Create rounded rect path for clipping
            path = QPainterPath()
            path.addRoundedRect(rect, self._border_radius, self._border_radius)

            # Clip to rounded rect
            painter.setClipPath(path)

            # Scale and draw pixmap
            scaled_pixmap = self.pixmap().scaled(
                self.size(),
                Qt.AspectRatioMode.KeepAspectRatioByExpanding,
                Qt.TransformationMode.SmoothTransformation,
            )

            # Center the pixmap
            x = (self.width() - scaled_pixmap.width()) // 2
            y = (self.height() - scaled_pixmap.height()) // 2
            painter.drawPixmap(x, y, scaled_pixmap)

            # Draw border
            painter.setClipping(False)
            pen = QPen(self._border_color, self._border_width)
            painter.setPen(pen)
            painter.setBrush(QBrush(Qt.BrushStyle.NoBrush))
            painter.drawRoundedRect(rect, self._border_radius, self._border_radius)

            painter.end()
        else:
            super().paintEvent(event)


class PageHome(QWidget):
    """Xodim yuz tekshiruvi sahifasi - HTML page2.html style"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("page_home")
        self._setup_ui()
        self._apply_styles()
        self._setup_animations()

    def _setup_ui(self):
        """UI elementlarini yaratish"""
        # Main layout - centers the stage
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        main_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # ============ STAGE (Main Container) ============
        self.stage = QFrame()
        self.stage.setObjectName("stage")
        self.stage.setMinimumSize(1000, 560)
        self.stage.setMaximumSize(1120, 700)
        stage_layout = QVBoxLayout(self.stage)
        stage_layout.setContentsMargins(0, 0, 0, 0)
        stage_layout.setSpacing(0)

        # ============ HEADER ============
        header_widget = QWidget()
        header_widget.setObjectName("header_widget")
        header_widget.setFixedHeight(110)
        header_layout = QVBoxLayout(header_widget)
        header_layout.setContentsMargins(24, 20, 24, 20)
        header_layout.setSpacing(0)
        header_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Header title
        self.label_header_title = QLabel(
            "Ruxsat etilgan xodimlarni tizimga kirishi uchun"
        )
        self.label_header_title.setObjectName("label_header_title")
        self.label_header_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header_layout.addWidget(self.label_header_title)

        self.label_header_subtitle = QLabel("FACE ID tekshiruvi")
        self.label_header_subtitle.setObjectName("label_header_subtitle")
        self.label_header_subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header_layout.addWidget(self.label_header_subtitle)

        stage_layout.addWidget(header_widget)

        # ============ CONTENT ============
        content_widget = QWidget()
        content_widget.setObjectName("content_widget")
        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(24, 24, 24, 24)
        content_layout.setSpacing(0)
        content_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # ============ PANEL ============
        self.panel = QFrame()
        self.panel.setObjectName("panel")
        panel_layout = QVBoxLayout(self.panel)
        panel_layout.setContentsMargins(20, 20, 20, 20)
        panel_layout.setSpacing(18)
        panel_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # ============ CARDS GRID (7:5) ============
        cards_widget = QWidget()
        cards_widget.setObjectName("cards_widget")
        cards_layout = QHBoxLayout(cards_widget)
        cards_layout.setContentsMargins(8, 8, 8, 8)
        cards_layout.setSpacing(20)
        cards_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # ===== CAMERA WRAP (7fr) =====
        self.camera_wrap = QFrame()
        self.camera_wrap.setObjectName("camera_wrap")
        camera_wrap_layout = QVBoxLayout(self.camera_wrap)
        camera_wrap_layout.setContentsMargins(5, 5, 5, 5)
        camera_wrap_layout.setSpacing(0)

        # Glow Frame
        self.glow_frame = QFrame()
        self.glow_frame.setObjectName("glow_frame")
        glow_layout = QVBoxLayout(self.glow_frame)
        glow_layout.setContentsMargins(8, 8, 8, 8)
        glow_layout.setSpacing(0)
        glow_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Video / Camera label (RoundedLabel for border-radius clipping)
        self.label_face = RoundedLabel()
        self.label_face.setObjectName("label_face")
        self.label_face.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding
        )
        self.label_face.setAlignment(Qt.AlignmentFlag.AlignCenter)
        glow_layout.addWidget(self.label_face)

        # Scan line (overlay on video)
        self.scan_line = ScanLine(self.label_face)
        self.scan_line.setFixedHeight(36)  # Taller for glow effect
        self.scan_line.raise_()
        camera_wrap_layout.addWidget(self.glow_frame)
        cards_layout.addWidget(self.camera_wrap, 7)

        # ===== FACE CARD (5fr) =====
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
        self.label_illustration.setFixedSize(280, 396)  # 350x496 aspect ratio
        self.label_illustration.setAlignment(Qt.AlignmentFlag.AlignCenter)
        face_icon_layout.addWidget(self.label_illustration)

        face_card_layout.addWidget(self.face_icon)
        cards_layout.addWidget(self.face_card, 5)

        panel_layout.addWidget(cards_widget, 1)

        # ============ STATUS BAR ============
        self.status_bar = QFrame()
        self.status_bar.setObjectName("status_bar")
        self.status_bar.setFixedHeight(48)
        status_layout = QHBoxLayout(self.status_bar)
        status_layout.setContentsMargins(20, 0, 20, 0)
        status_layout.setSpacing(12)
        status_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Pulse indicator
        self.pulse_dot = QFrame()
        self.pulse_dot.setObjectName("pulse_dot")
        self.pulse_dot.setFixedSize(10, 10)
        status_layout.addWidget(self.pulse_dot)

        # Status text
        self.label_response = QLabel("Yuzingizni kameraga ko'rsating...")
        self.label_response.setObjectName("label_response")
        self.label_response.setAlignment(Qt.AlignmentFlag.AlignCenter)
        status_layout.addWidget(self.label_response)

        panel_layout.addWidget(self.status_bar)

        content_layout.addWidget(self.panel)
        stage_layout.addWidget(content_widget, 1)

        main_layout.addWidget(self.stage)

        # Legacy attributes for compatibility
        self.label_org = self.label_header_title
        self.label_9 = self.label_illustration
        self.label_note = self.label_response

    def _setup_animations(self):
        """Setup all animations"""
        # Start scan line animation after widget is shown
        QTimer.singleShot(500, self._start_scan_animation)

        # Setup pulse dot animation
        self._setup_pulse_animation()

    def _start_scan_animation(self):
        """Start the scan line animation"""
        if hasattr(self, "scan_line") and self.label_face.height() > 0:
            self.scan_line.start_animation(self.label_face.height())

    def _setup_pulse_animation(self):
        """Setup pulse dot animation"""
        # Apply opacity effect to pulse_dot
        self.pulse_opacity_effect = QGraphicsOpacityEffect(self.pulse_dot)
        self.pulse_dot.setGraphicsEffect(self.pulse_opacity_effect)

        # Create animation group for smooth pulse
        self.pulse_anim_group = QSequentialAnimationGroup(self)

        # Fade out animation
        self.pulse_fade_out = QPropertyAnimation(self.pulse_opacity_effect, b"opacity")
        self.pulse_fade_out.setDuration(800)
        self.pulse_fade_out.setStartValue(1.0)
        self.pulse_fade_out.setEndValue(0.3)
        self.pulse_fade_out.setEasingCurve(QEasingCurve.Type.InOutSine)

        # Fade in animation
        self.pulse_fade_in = QPropertyAnimation(self.pulse_opacity_effect, b"opacity")
        self.pulse_fade_in.setDuration(800)
        self.pulse_fade_in.setStartValue(0.3)
        self.pulse_fade_in.setEndValue(1.0)
        self.pulse_fade_in.setEasingCurve(QEasingCurve.Type.InOutSine)

        self.pulse_anim_group.addAnimation(self.pulse_fade_out)
        self.pulse_anim_group.addAnimation(self.pulse_fade_in)
        self.pulse_anim_group.setLoopCount(-1)  # Infinite loop
        self.pulse_anim_group.start()

    def showEvent(self, event):
        """Handle show event"""
        super().showEvent(event)
        QTimer.singleShot(100, self._start_scan_animation)
        # Resume pulse animation
        if hasattr(self, "pulse_anim_group"):
            self.pulse_anim_group.start()

    def hideEvent(self, event):
        """Handle hide event - stop animations"""
        super().hideEvent(event)
        if hasattr(self, "scan_line"):
            self.scan_line.stop_animation()
        # Stop pulse animation
        if hasattr(self, "pulse_anim_group"):
            self.pulse_anim_group.stop()

    def _apply_styles(self):
        """HTML page2.html stylelarini qo'llash"""

        # ===== MAIN PAGE BACKGROUND =====
        self.setStyleSheet("""
            QWidget#page_home {
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
        self.label_header_title.setStyleSheet("""
            QLabel#label_header_title {
                color: #1a3a3a;
                font-size: 22px;
                font-weight: 700;
                font-family: 'Inter', sans-serif;
                background: transparent;
                letter-spacing: 0.3px;
            }
        """)

        # Header subtitle (bold)
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

        # ===== VIDEO / CAMERA =====
        # Border va border-radius RoundedLabel.paintEvent() da chiziladi
        self.label_face.setStyleSheet("""
            QLabel#label_face {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #3a3a3a, stop:1 #777777);
                border-radius: 10px;
                border: 2px solid rgba(102, 210, 176, 0.9)
            }
        """)

        # ===== SCAN LINE =====
        # Custom paintEvent handles rendering with glow effect

        # ===== FACE CARD =====
        self.face_card.setStyleSheet("""
            QFrame#face_card {
                background: rgba(255, 255, 255, 0.7);
                border: 1px solid rgba(102, 210, 176, 0.25);
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

        # ===== STATUS BAR =====
        self.status_bar.setStyleSheet("""
            QFrame#status_bar {
                background: transparent;
                border: none;
            }
        """)

        # ===== PULSE DOT =====
        self.pulse_dot.setStyleSheet("""
            QFrame#pulse_dot {
                background: #74D6B6;
                border-radius: 5px;
            }
        """)

        # ===== STATUS TEXT =====
        self.label_response.setStyleSheet("""
            QLabel#label_response {
                color: #234b4b;
                font-size: 15px;
                font-family: 'Inter', sans-serif;
                background: transparent;
                padding: 8px 0px;
            }
        """)
