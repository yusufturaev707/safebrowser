"""
Main Window - Asosiy oyna
Bu fayl legacy main.py dan re-export qiladi va yangi strukturaga bridge vazifasini bajaradi
"""
import sys
import os
import time

# Yangi strukturadan import
from ui.styles import get_full_stylesheet, COLORS
from ui.dialogs import InfoModal, ExitDialog, MonitorWarningModal, ToastManager
from ui.base_ui import Ui_MainWindow
from workers import (
    CameraCheckerWorker,
    FaceDetectorWorker,
    CPUOptimizedFaceIdWorker,
    FaceIdStaffWorker,
    Camera1Worker,
    InternetCheckWorker,
    MonitorWorker,
    ScreenRecorderWorker,
    AppLoaderWorker,
    TestLoaderWorker,
    PersonDetectorWorker,
)
from utils.graphics import (
    create_success_pixmap,
    create_id_card_pixmap,
    create_lock_icon,
)
from config import config
from utils.system import get_disk_with_most_free_space
from services.api_client import APIClient
from core.face_analyzer import FaceAnalyzer
from utils.system import is_windows, is_linux, is_macos, get_platform_name, get_available_cameras
from utils.logger import get_logger, info, debug, warning, error, exception

# Logger
log = get_logger()

# PyQt6 imports
import configparser
import requests
import cv2

# Platform-specific keyboard blocking
try:
    import keyboard
    KEYBOARD_AVAILABLE = True
except ImportError:
    KEYBOARD_AVAILABLE = False
    warning("keyboard moduli mavjud emas - tugmalarni bloklash ishlamaydi")

from PyQt6.QtCore import Qt, QUrl, QRegularExpression, pyqtSlot, QTimer
from PyQt6.QtGui import (
    QPixmap, QRegularExpressionValidator, QImage, QPainter,
    QColor, QFont, QPen, QBrush, QLinearGradient, QAction, QKeySequence
)
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWidgets import (
    QMainWindow, QMessageBox, QLabel, QDialog,
    QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton,
    QGraphicsDropShadowEffect, QFrame, QWidget, QSizePolicy,
)


class DraggableLabel(QLabel):
    """Mishka bilan siljitish mumkin bo'lgan label"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._dragging = False
        self._drag_start_pos = None
        self.setCursor(Qt.CursorShape.OpenHandCursor)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self._dragging = True
            self._drag_start_pos = event.pos()
            self.setCursor(Qt.CursorShape.ClosedHandCursor)
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self._dragging and self._drag_start_pos:
            # Yangi pozitsiyani hisoblash
            new_pos = self.mapToParent(event.pos() - self._drag_start_pos)

            # Parent chegarasidan chiqmaslik
            parent = self.parent()
            if parent:
                x = max(0, min(new_pos.x(), parent.width() - self.width()))
                y = max(0, min(new_pos.y(), parent.height() - self.height()))
                self.move(x, y)
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self._dragging = False
            self._drag_start_pos = None
            self.setCursor(Qt.CursorShape.OpenHandCursor)
        super().mouseReleaseEvent(event)


from PyQt6.QtCore import pyqtSignal as Signal


class CameraOverlayWidget(QFrame):
    """
    Material Design 3 styled kamera overlay widget
    Glassmorphism effekti va chiroyli dizayn bilan
    """
    # Chiqish tugmasi bosilganda signal
    exit_requested = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._dragging = False
        self._drag_start_pos = None
        self._is_minimized = False
        self._full_size = (256, 216)
        self._mini_size = (125, 32)
        self._pulse_state = True

        self.setObjectName("camera_overlay_container")
        self.setFixedSize(*self._full_size)
        self.setCursor(Qt.CursorShape.OpenHandCursor)

        self._setup_ui()
        self._apply_shadow()
        self._start_pulse_animation()

    def _setup_ui(self):
        """UI komponentlarini sozlash"""
        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Header bar
        self.header = QFrame()
        self.header.setObjectName("camera_header")
        self.header.setFixedHeight(32)

        header_layout = QHBoxLayout(self.header)
        header_layout.setContentsMargins(8, 0, 4, 0)
        header_layout.setSpacing(4)

        # Camera icon (emoji as text)
        camera_icon = QLabel("")
        camera_icon.setStyleSheet("""
            font-size: 12px;
            background: transparent;
            padding: 0;
        """)

        # Title
        self.title_label = QLabel("Kamera")
        self.title_label.setObjectName("camera_title")

        # Status dot (recording indicator)
        self.status_dot = QLabel()
        self.status_dot.setObjectName("camera_status_dot")
        self.status_dot.setToolTip("Yozilmoqda...")

        # Minimize button
        self.minimize_btn = QPushButton("")
        self.minimize_btn.setObjectName("camera_minimize_btn")
        self.minimize_btn.setToolTip("Kichiklashtirish")
        self.minimize_btn.clicked.connect(self._toggle_minimize)

        # Exit button (chiqish)
        self.exit_btn = QPushButton("✕")
        self.exit_btn.setObjectName("camera_exit_btn")
        self.exit_btn.setToolTip("Testdan chiqish")
        self.exit_btn.clicked.connect(self._on_exit_clicked)

        header_layout.addWidget(camera_icon)
        header_layout.addWidget(self.title_label)
        header_layout.addStretch()
        header_layout.addWidget(self.status_dot)
        header_layout.addWidget(self.minimize_btn)
        header_layout.addWidget(self.exit_btn)

        # Video display area
        self.video_label = QLabel()
        self.video_label.setObjectName("camera_video_label")
        self.video_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.video_label.setMinimumSize(252, 180)
        self.video_label.setScaledContents(False)

        # Add to main layout
        main_layout.addWidget(self.header)
        main_layout.addWidget(self.video_label, 1)

        # Apply container style
        self.setStyleSheet("""
            QFrame#camera_overlay_container {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 rgba(15, 23, 42, 0.97),
                    stop:0.5 rgba(30, 41, 59, 0.95),
                    stop:1 rgba(15, 23, 42, 0.97));
                border: 2px solid qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 rgba(34, 197, 94, 0.8),
                    stop:0.5 rgba(16, 185, 129, 0.6),
                    stop:1 rgba(34, 197, 94, 0.8));
                border-radius: 16px;
            }

            QFrame#camera_header {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 rgba(34, 197, 94, 0.95),
                    stop:0.3 rgba(16, 185, 129, 0.9),
                    stop:0.7 rgba(16, 185, 129, 0.9),
                    stop:1 rgba(34, 197, 94, 0.95));
                border: none;
                border-radius: 14px 14px 0px 0px;
            }

            QLabel#camera_title {
                color: #ffffff;
                font-size: 12px;
                font-weight: 600;
                background: transparent;
                letter-spacing: 0.3px;
            }

            QLabel#camera_status_dot {
                background: qradialgradient(cx:0.5, cy:0.5, radius:0.5,
                    fx:0.3, fy:0.3,
                    stop:0 #ffffff,
                    stop:0.4 #ef4444,
                    stop:1 #b91c1c);
                border: 1px solid rgba(255, 255, 255, 0.25);
                border-radius: 5px;
                min-width: 10px;
                max-width: 10px;
                min-height: 10px;
                max-height: 10px;
            }

            QLabel#camera_video_label {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #0f172a,
                    stop:0.5 #1e293b,
                    stop:1 #0f172a);
                border: none;
                border-radius: 0px 0px 14px 14px;
                padding: 4px;
            }

            /* Camera header buttons - shared style */
            QPushButton#camera_minimize_btn, QPushButton#camera_exit_btn {
                border: none;
                border-radius: 4px;
                color: white;
                font-size: 10px;
                font-weight: 600;
                min-width: 20px;
                max-width: 20px;
                min-height: 20px;
                max-height: 20px;
                padding: 0;
                margin: 0 1px;
            }

            QPushButton#camera_minimize_btn {
                background: rgba(255, 255, 255, 0.2);
            }
            QPushButton#camera_minimize_btn:hover {
                background: rgba(255, 255, 255, 0.35);
            }
            QPushButton#camera_minimize_btn:pressed {
                background: rgba(255, 255, 255, 0.5);
            }

            QPushButton#camera_exit_btn {
                background: rgba(220, 38, 38, 0.85);
            }
            QPushButton#camera_exit_btn:hover {
                background: rgba(239, 68, 68, 1.0);
            }
            QPushButton#camera_exit_btn:pressed {
                background: rgba(185, 28, 28, 1.0);
            }
        """)

    def _apply_shadow(self):
        """Drop shadow effekti qo'shish"""
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(25)
        shadow.setXOffset(0)
        shadow.setYOffset(4)
        shadow.setColor(QColor(0, 0, 0, 100))
        self.setGraphicsEffect(shadow)

    def _start_pulse_animation(self):
        """Recording indicator pulsatsiya animatsiyasi"""
        self._pulse_timer = QTimer(self)
        self._pulse_timer.timeout.connect(self._pulse_dot)
        self._pulse_timer.start(800)  # 800ms interval

    def _pulse_dot(self):
        """Status dot pulsatsiyasi"""
        base_style = """
            border-radius: 5px;
            min-width: 10px; max-width: 10px;
            min-height: 10px; max-height: 10px;
        """
        if self._pulse_state:
            self.status_dot.setStyleSheet(f"""
                background: qradialgradient(cx:0.5, cy:0.5, radius:0.5,
                    fx:0.3, fy:0.3, stop:0 #fff, stop:0.4 #ef4444, stop:1 #b91c1c);
                border: 1px solid rgba(255,255,255,0.25);
                {base_style}
            """)
        else:
            self.status_dot.setStyleSheet(f"""
                background: qradialgradient(cx:0.5, cy:0.5, radius:0.5,
                    fx:0.3, fy:0.3, stop:0 #fecaca, stop:0.4 #f87171, stop:1 #dc2626);
                border: 1px solid rgba(255,255,255,0.15);
                {base_style}
            """)
        self._pulse_state = not self._pulse_state

    def _toggle_minimize(self):
        """Kamera oynasini kichiklashtirish/kattalashtirish"""
        if self._is_minimized:
            # Restore
            self.setFixedSize(*self._full_size)
            self.video_label.show()
            self.minimize_btn.setText("")
            self.minimize_btn.setToolTip("Kichiklashtirish")
            self._is_minimized = False
        else:
            # Minimize
            self.setFixedSize(*self._mini_size)
            self.video_label.hide()
            self.minimize_btn.setText("")
            self.minimize_btn.setToolTip("Kattalashtirish")
            self._is_minimized = True

    def _on_exit_clicked(self):
        """Chiqish tugmasi bosilganda"""
        self.exit_requested.emit()

    def setPixmap(self, pixmap):
        """Video frame'ni ko'rsatish"""
        if not self._is_minimized:
            scaled = pixmap.scaled(
                self.video_label.size(),
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )
            self.video_label.setPixmap(scaled)

    def mousePressEvent(self, event):
        """Drag boshlash"""
        if event.button() == Qt.MouseButton.LeftButton:
            self._dragging = True
            self._drag_start_pos = event.pos()
            self.setCursor(Qt.CursorShape.ClosedHandCursor)
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        """Drag qilish"""
        if self._dragging and self._drag_start_pos:
            new_pos = self.mapToParent(event.pos() - self._drag_start_pos)
            parent = self.parent()
            if parent:
                x = max(0, min(new_pos.x(), parent.width() - self.width()))
                y = max(0, min(new_pos.y(), parent.height() - self.height()))
                self.move(x, y)
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        """Drag tugatish"""
        if event.button() == Qt.MouseButton.LeftButton:
            self._dragging = False
            self._drag_start_pos = None
            self.setCursor(Qt.CursorShape.OpenHandCursor)
        super().mouseReleaseEvent(event)


class MainWindow(QMainWindow, Ui_MainWindow):
    """
    SafeBrowser asosiy oynasi
    """

    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.setWindowFlag(Qt.WindowType.WindowStaysOnTopHint)
        self.setWindowFlag(Qt.WindowType.FramelessWindowHint)

        # Apply modern stylesheet
        self.setStyleSheet(get_full_stylesheet())

        # Material Design background
        self.stack.setStyleSheet("""
            QStackedWidget#stack {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #e8f4f8,
                    stop:0.3 #d1e8f0,
                    stop:0.6 #c9dde8,
                    stop:1 #b8d4e3);
            }
        """)

        # Initialize
        self._init_keys()
        self._init_validators()
        self._init_variables()
        self._init_workers()
        self._init_ui_components()
        self._connect_signals()
        # self.setup_actions()

        # Show window after all initialization is complete
        self.showFullScreen()

    def _init_keys(self):
        """
        Klaviatura tugmalarini bloklash (cross-platform)

        Windows: keyboard kutubxonasi yaxshi ishlaydi
        Linux: root/sudo talab qiladi
        macOS: Accessibility permissions talab qiladi
        """
        if not KEYBOARD_AVAILABLE:
            debug(f"Keyboard blocking not available on {get_platform_name()}")
            return

        try:
            if is_windows():
                # Windows: to'liq bloklash
                keys_to_block = ['alt', 'tab', 'win', 'f4', 'caps lock', 'print screen']
                for key in keys_to_block:
                    try:
                        keyboard.block_key(key)
                    except Exception as e:
                        debug(f"Cannot block {key}: {e}")
                debug("Windows klaviatura tugmalari bloklandi")

            elif is_linux():
                # Linux: faqat root da ishlaydi
                import os
                is_root = False
                try:
                    is_root = os.geteuid() == 0
                except AttributeError:
                    # geteuid Windows da mavjud emas
                    is_root = False

                if is_root:
                    keys_to_block = ['alt', 'tab', 'print_screen']
                    for key in keys_to_block:
                        try:
                            keyboard.block_key(key)
                        except Exception:
                            pass
                    debug("Linux klaviatura tugmalari bloklandi (root)")
                else:
                    debug("Linux: Tugmalarni bloklash uchun root kerak")

            elif is_macos():
                # macOS: keyboard library cheklangan ishlaydi
                # Accessibility permissions kerak
                debug("macOS: Tugmalarni bloklash qo'llab-quvvatlanmaydi")
                # macOS da boshqa yechim - PyObjC ishlatish mumkin
                # lekin bu qo'shimcha dependency talab qiladi

            else:
                debug(f"Platform {get_platform_name()}: Tugmalarni bloklash qo'llab-quvvatlanmaydi")

        except Exception as e:
            debug(f"Block keys error: {e}")

    def _init_validators(self):
        """Input validatorlarini o'rnatish"""
        regex = QRegularExpression(r'^[3-6][0-9]{13}$')
        validator = QRegularExpressionValidator(regex)
        self.input_pinfl.setValidator(validator)

    def _init_variables(self):
        """O'zgaruvchilarni boshlash"""
        self.msg_box = None
        self.quit = False
        self.webview = None
        self.modal = InfoModal(self)
        self.monitor_warning_modal = MonitorWarningModal(self, auto_close_seconds=3)

        self.stack.setCurrentIndex(0)
        self.current_index_page = 0

        # User data
        self.im = None
        self.test_url = None
        self.image_base64 = None
        self.cropped_face = None
        self.score = 0
        self.ps_embedding = None
        self.test_name = None
        self.is_verified = False
        self.chosen_test_key = None
        self.warning_text = None
        self.app = None
        self.face_analyzer = None
        self.state = None
        self.selected_camera_index = 0

        # Settings
        self.is_detect_monitor = None
        self.is_check_face_staff = None
        self.is_detect_camera = None
        self.is_check_face_candidate = None
        self.is_screen_record = None
        self.is_face_identification = None
        self.timer_face_id = None

        # Admin password
        self.admin_password = config.admin_password
        self.base_url = config.api_base_url

        # Face Monitoring Configuration (config.ini dan)
        self.face_identification_interval = config.face_identification_interval
        self.face_identification_max_fail = config.face_identification_max_fail

        # Face Monitoring State
        self.face_identification_fail_count = 0
        self.current_has_face = False
        self.current_is_verified = False

        # Toast Manager
        self.toast_manager = None

    def _init_workers(self):
        """Worker'larni boshlash"""
        self.checker_internet_worker = InternetCheckWorker(interval=5)
        self.checker_internet_worker.status_changed.connect(self._on_internet_status)
        self.checker_internet_worker.start()

        self.checker_monitor_worker = MonitorWorker(interval=1)
        self.checker_camera_worker = CameraCheckerWorker(interval=3)

        self.face_detector_worker = None
        self.face_identification_worker = None
        self.face_staff_worker = None
        self.camera1_worker = None
        self.screen_recorder_worker = None
        self.person_detector_worker = None
        self.load_app_worker = None
        self.test_loader_worker = None

        # InsightFace modelini yuklash
        self._init_face_analyzer()

    def _init_face_analyzer(self):
        """InsightFace modelini yuklash"""
        try:
            gpu_id = FaceAnalyzer.detect_best_device()
            debug(f"InsightFace modeli yuklanmoqda... (gpu_id={gpu_id})")
            self.face_analyzer = FaceAnalyzer(det_size=(640, 640), gpu_id=gpu_id)

            if self.face_analyzer.initialize():
                self.app = self.face_analyzer.app
                debug("InsightFace modeli muvaffaqiyatli yuklandi!")
            else:
                self.app = None
                debug("InsightFace modelini yuklashda xatolik!")
        except Exception as e:
            debug(f"FaceAnalyzer init error: {e}")
            self.app = None
            self.face_analyzer = None

    def _init_ui_components(self):
        """UI komponentlarini sozlash"""
        self.camera1_widget = None

        # Material Design 3 styled camera overlay widget
        self.camera_overlay = CameraOverlayWidget()
        self.camera_overlay.exit_requested.connect(self._on_camera_exit_requested)

        # Legacy camera_face_label reference (for backward compatibility)
        self.camera_face_label = self.camera_overlay

        # Toast Manager - yengil ogohlantirishlar uchun
        self.toast_manager = ToastManager(self)

        # ID card design
        self._setup_id_card()

        # Load tests
        self._load_tests()

        # Load available cameras
        self._load_cameras()

    def _connect_signals(self):
        """Signal-slot ulanishlar"""
        self.btn_check_im.clicked.connect(self._on_check_pinfl)
        self.btn_candidate_next.clicked.connect(self._on_candidate_continue)
        self.btn_candidate_next.hide()

        # btn_candidate_next - Yashil tema bilan uyg'unlashgan style
        self.btn_candidate_next.setText("Davom etish  →")
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

        self.btn_next_page.clicked.connect(self._on_staff_face_page)
        self.btn_refresh_camera.clicked.connect(self._load_cameras)

    def _setup_id_card(self):
        """ID karta dizaynini sozlash"""
        try:
            id_card = create_id_card_pixmap(340, 220)
            self.label_4.setPixmap(id_card)
            self.label_4.setScaledContents(False)
            self.label_4.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.label_4.setStyleSheet("background: transparent; border: none;")
        except Exception as e:
            debug(f"ID card setup error: {e}")

    def _load_tests(self):
        """Testlarni yuklash"""
        try:
            self.test_loader_worker = TestLoaderWorker(base_url=self.base_url)
            self.test_loader_worker.result.connect(self._on_tests_loaded)
            self.test_loader_worker.start()
        except Exception as e:
            debug(f"Test loader error: {e}")

    def _load_cameras(self):
        """Mavjud kameralarni yuklash"""
        try:
            cameras = get_available_cameras()
            self.combo_choose_camera.clear()
            if cameras:
                for index, name in cameras:
                    self.combo_choose_camera.addItem(name, index)
                self.selected_camera_index = cameras[0][0]
                debug(f"Kameralar yuklandi: {len(cameras)} ta")
            else:
                self.combo_choose_camera.addItem("Kamera topilmadi", -1)
                debug("Hech qanday kamera topilmadi")
        except Exception as e:
            debug(f"Camera loader error: {e}")

    @pyqtSlot(object)
    def _on_tests_loaded(self, data: dict):
        """Testlar yuklanganda"""
        try:
            if data.get("status"):
                tests = data.get("result", [])
                self.combo_choose_test.clear()
                self.combo_choose_test.addItem("Testni tanlang...", None)
                for test in tests:
                    test_name = test.get("name", "Nomsiz test")
                    test_key = test.get("key") or test.get("id")
                    # Test ma'lumotlarini userData sifatida saqlash
                    self.combo_choose_test.addItem(test_name, test)
                debug(f"Testlar yuklandi: {len(tests)} ta")
            else:
                message = data.get("message", "Testlarni yuklashda xatolik")
                debug(f"Test yuklash xatosi: {message}")
                self.show_message("Xatolik", message, 0)
        except Exception as e:
            debug(f"Tests loaded handler error: {e}")

    def show_message(self, title: str, message: str, code: int = 2):
        """Xabar ko'rsatish - Material Design 3 InfoModal"""
        try:
            # Code to InfoModal type mapping
            type_map = {
                0: InfoModal.TYPE_ERROR,      # Critical
                1: InfoModal.TYPE_WARNING,    # Warning
                2: InfoModal.TYPE_INFO,       # Information
                3: InfoModal.TYPE_INFO,       # Question
            }
            msg_type = type_map.get(code, InfoModal.TYPE_INFO)

            modal = InfoModal(self)
            modal.update_data(title, message, msg_type)
            modal.exec()
        except Exception as e:
            debug(f"Message error: {e}")

    @pyqtSlot(str)
    def _on_camera_error(self, message: str):
        """Kamera xatoligi yuz berganda warning ko'rsatish"""
        self.show_message("Ogohlantirish", message, 1)

    def request_exit_password(self) -> bool:
        """Chiqish parolini so'rash"""
        dialog = ExitDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            if dialog.get_password() == self.admin_password:
                self.quit = True
                return True
            else:
                self.show_message("Xatolik", "Parol noto'g'ri!", 0)
        return False

    def on_exit_requested(self):
        """Chiqish so'ralganda"""
        if self.request_exit_password():
            self.stop_all_workers()
            self.close()

    def stop_all_workers(self):
        """Barcha worker'larni to'xtatish"""
        workers = [
            self.checker_internet_worker,
            self.checker_monitor_worker,
            self.checker_camera_worker,
            self.face_identification_worker,
            self.face_detector_worker,
            self.face_staff_worker,
            self.camera1_worker,
            self.screen_recorder_worker,
            self.person_detector_worker,
            self.load_app_worker,
            self.test_loader_worker,
        ]

        for worker in workers:
            if worker:
                try:
                    if hasattr(worker, 'isRunning') and worker.isRunning():
                        worker.stop()
                        worker.wait(1000)
                except Exception as e:
                    debug(f"Worker stop error: {e}")

    def setup_actions(self):
        """Menu actions"""
        exit_action = QAction("Exit", self)
        exit_action.setShortcut(QKeySequence.StandardKey.Quit)  # ✅ Avtomatik!
        exit_action.triggered.connect(self.on_exit_requested)

        # Menu'ga qo'shish (ixtiyoriy)
        file_menu = self.menuBar().addMenu("File")
        file_menu.addAction(exit_action)

    #Event handlers
    def keyPressEvent(self, event):
        """Tugma bosilganda"""
        try:
            if event.modifiers() == Qt.KeyboardModifier.ControlModifier:
                if event.key() == Qt.Key.Key_Q:
                    if self.request_exit_password():
                        self.stop_all_workers()
                        self.close()
        except Exception as e:
            debug(f"KeyPress error: {e}")

    def closeEvent(self, event):
        """Oyna yopilganda"""
        if self.quit:
            event.accept()
        else:
            event.ignore()

    def resizeEvent(self, event):
        """Oyna o'lchami o'zgarganda - kamera overlay joylashuvini yangilash"""
        super().resizeEvent(event)
        self._update_camera_overlay_position()

    def _update_camera_overlay_position(self):
        """Kamera overlay joylashuvini yangilash"""
        try:
            if hasattr(self, 'camera_overlay') and self.camera_overlay.isVisible():
                parent = self.camera_overlay.parent()
                if parent:
                    # O'ng yuqori burchakda joylash
                    x = parent.width() - self.camera_overlay.width() - 20
                    y = 20
                    self.camera_overlay.move(x, y)
                    self.camera_overlay.raise_()
        except Exception as e:
            debug(f"Camera overlay position error: {e}")

    # Slot handlers
    @pyqtSlot(bool)
    def _on_internet_status(self, is_online: bool):
        """Internet holati o'zgarganda"""
        try:
            if is_online:
                self.stack.setCurrentIndex(self.current_index_page)
            else:
                self.current_index_page = self.stack.currentIndex()
                self._next_page_by_name('page_no_internet')
        except Exception as e:
            debug(f"Internet checker error: {e}")

    def _next_page_by_name(self, page_name: str):
        """Sahifaga o'tish"""
        for i in range(self.stack.count()):
            if self.stack.widget(i).objectName() == page_name:
                self.stack.setCurrentIndex(i)
                break

    # Button click handlers (placeholders - to be implemented)
    def _on_check_pinfl(self):
        """PINFL tekshirish va foydalanuvchi ma'lumotlarini olish"""
        try:
            if self.is_detect_monitor:
                if self.checker_monitor_worker.get_cheating_monitor():
                    self.show_message(
                        "Ogohlantirish",
                        "Qo'shimcha monitor aniqlandi!\n\n"
                        "Imtihon davomida faqat bitta monitor ishlatish mumkin.\n"
                        "Iltimos, qo'shimcha monitorni o'chiring va qaytadan urinib ko'ring.",
                        1
                    )
                    return

            pinfl = self.input_pinfl.text().strip()

            if not pinfl:
                self.show_message("Ogohlantirish", "Iltimos, JSHSHIR kiriting!", 1)
                return

            if len(pinfl) != 14:
                self.show_message("Ogohlantirish", "JSHSHIR 14 ta raqamdan iborat bo'lishi kerak!", 1)
                return

            if not pinfl.isdigit():
                self.show_message("Ogohlantirish", "JSHSHIR faqat raqamlardan iborat bo'lishi kerak!", 1)
                return

            # Loading ko'rsatish
            self.btn_check_im.setEnabled(False)
            self.btn_check_im.setText("Tekshirilmoqda...")

            # API orqali tekshirish
            api_client = APIClient(base_url=self.base_url)
            result = api_client.check_pinfl(pinfl, self.chosen_test_key)

            # Buttonni qayta yoqish
            self.btn_check_im.setEnabled(True)
            self.btn_check_im.setText("Tekshirish")

            if result['status']:
                user_data = result['data']
                if user_data['status']:
                    self.im = pinfl
                    self.test_url = user_data.get("test_link")
                    self.image_base64 = user_data.get("image_base64")  # Base64 rasm
                    self.score = user_data.get("score", 85)  # O'xshashlik chegarasi

                    debug(f"PINFL tasdiqlandi: {pinfl}")

                    if self.is_check_face_candidate and self.image_base64:
                        self._next_page_by_name('page_face')
                        self._start_candidate_face_verification()
                    else:
                        # Yuz tekshiruvi o'chirilgan - to'g'ridan-to'g'ri testni boshlash
                        self._on_start_test()
                else:
                    message = user_data.get("message", "12345")
                    self.show_message("DIQQAT!", message, 1)
            else:
                message = result.get("message", "12345")
                self.show_message("DIQQAT!", message, 0)
        except Exception as e:
            # Xatolik bo'lsa buttonni qayta yoqish
            self.btn_check_im.setEnabled(True)
            self.btn_check_im.setText("Tekshirish")
            debug(f"Check PINFL error: {e}")
            self.show_message("Xatolik", f"Tekshirishda xatolik: {e}", 0)

    def _on_candidate_continue(self):
        """Nomzod tasdiqlangandan keyin davom etish"""
        try:
            # Face detection worker'larni to'xtatish
            if self.face_detector_worker and self.face_detector_worker.isRunning():
                self.face_detector_worker.stop()

            if self.face_identification_worker and self.face_identification_worker.isRunning():
                self.face_identification_worker.stop()

            # Testni boshlash (page_note o'tkazib yuboriladi)
            self._on_start_test()

        except Exception as e:
            debug(f"Candidate continue error: {e}")

    def _start_candidate_face_verification(self):
        """Nomzod yuz tekshiruvini boshlash"""
        try:
            if self.app is None:
                self.show_message("Xatolik", "Yuz aniqlash modeli yuklanmagan!", 0)
                return

            if not self.image_base64:
                self.show_message("Xatolik", "Passport rasmi topilmadi!", 0)
                return

            # Verification holatini reset qilish
            self.is_verified = False

            # Oldingi worker'larni to'xtatish
            if self.face_detector_worker and self.face_detector_worker.isRunning():
                self.face_detector_worker.stop()

            if self.face_identification_worker and self.face_identification_worker.isRunning():
                self.face_identification_worker.stop()

            # Face Detector Worker'ni boshlash
            self.face_detector_worker = FaceDetectorWorker(app=self.app, camera_index=self.selected_camera_index)
            self.face_detector_worker.face_detected.connect(self._on_candidate_face_detected)
            self.face_detector_worker.camera_error.connect(self._on_camera_error)
            self.face_detector_worker.start()

            # Face ID Worker'ni boshlash (nomzod uchun)
            self.face_identification_worker = CPUOptimizedFaceIdWorker(app=self.app)
            self.face_identification_worker.result_ready.connect(self._on_candidate_face_result)
            self.face_identification_worker.start()

            # UI holatini yangilash - ko'k Material Design card
            self.label_result_face_candidate.setText("Yuzingizni kameraga ko'rsating...")
            self.label_result_face_candidate.setStyleSheet("""
                QLabel {
                    color: #f59e0b;
                    font-size: 15px;
                }
            """)
            self.btn_candidate_next.hide()

            debug("Candidate face verification boshlandi...")

        except Exception as e:
            debug(f"Start candidate face verification error: {e}")
            self.show_message("Xatolik", f"Yuz tekshiruvini boshlashda xatolik: {e}", 0)

    @pyqtSlot(object)
    def _on_candidate_face_detected(self, data: dict):
        """Nomzod yuzi aniqlanganda"""
        try:
            qt_image = data.get("image")
            cropped_face = data.get("crop_face")
            has_face = data.get("has_face", False)

            # Kamera tasvirini ko'rsatish
            if qt_image and not qt_image.isNull():
                pixmap = QPixmap.fromImage(qt_image)
                scaled = pixmap.scaled(
                    self.label_video_box.size(),
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation
                )
                self.label_video_box.setPixmap(scaled)

            # Yuz aniqlansa, face ID worker'ga yuborish
            if has_face and cropped_face is not None and self.face_identification_worker:
                # RGB formatga o'tkazish
                if len(cropped_face.shape) == 3:
                    rgb_face = cv2.cvtColor(cropped_face, cv2.COLOR_BGR2RGB)
                else:
                    rgb_face = cropped_face

                self.face_identification_worker.add_task(
                    image_base64=self.image_base64,
                    cropped_face=rgb_face,
                    score=self.score
                )
            else:
                # Yuz topilmadi - sariq ogohlantirish (faqat tasdiqlanmagan bo'lsa)
                if not self.is_verified:
                    self.label_result_face_candidate.setText("Yuzingizni kameraga ko'rsating...")
                    self.label_result_face_candidate.setStyleSheet("""
                        QLabel {
                            color: #f59e0b;
                            font-size: 15px;
                        }
                    """)
                    # Yuz topilmaganda buttonni yashirish
                    self.btn_candidate_next.hide()

        except Exception as e:
            debug(f"Candidate face detected handler error: {e}")

    @pyqtSlot(object)
    def _on_candidate_face_result(self, data: dict):
        """Nomzod yuz tekshiruvi natijasi - real-time o'xshashlik ko'rsatish"""
        try:
            is_verified = data.get("is_verified", False)
            similarity = data.get("similarity", 0)
            message = data.get("message", "")

            # Real-time o'xshashlik foizini DOIM ko'rsatish
            if similarity > 0:
                if is_verified:
                    # Muvaffaqiyatli - yashil rang
                    self.is_verified = True
                    self.ps_embedding = data.get("ps_embedding")

                    self.label_result_face_candidate.setText(f"O'xshashlik: {similarity}% ✓")
                    self.label_result_face_candidate.setStyleSheet("""
                        QLabel {
                            color: #16a34a;
                            font-size: 15px;
                        }
                    """)

                    # Davom etish tugmasini ko'rsatish (lekin worker'larni TO'XTATMAYMIZ)
                    self.btn_candidate_next.show()

                    debug(f"Nomzod tasdiqlandi: {similarity}% (webcam davom etmoqda)")

                else:
                    # Tasdiqlanmadi - foizga qarab rang berish
                    threshold = self.score if hasattr(self, 'score') and self.score else 40

                    if similarity >= threshold * 0.7:  # 70% dan yuqori - sariq (yaqin)
                        color = "#f59e0b"
                        status = "yaqin..."
                    elif similarity >= threshold * 0.4:  # 40% dan yuqori - to'q sariq
                        color = "#ea580c"
                        status = "tekshirilmoqda..."
                    else:  # Past - qizil
                        color = "#dc2626"
                        status = "past"

                    self.label_result_face_candidate.setText(f"O'xshashlik: {similarity}% ({status})")
                    self.label_result_face_candidate.setStyleSheet(f"""
                        QLabel {{
                            color: {color};
                            font-size: 15px;
                        }}
                    """)
                    # Yuz tanilmaganda buttonni yashirish
                    self.btn_candidate_next.hide()
            else:
                # Yuz tahlil qilinmoqda
                self.label_result_face_candidate.setText("Yuz tahlil qilinmoqda...")
                self.label_result_face_candidate.setStyleSheet("""
                    QLabel {
                        color: #6b7280;
                        font-size: 15px;
                    }
                """)
                # Yuz topilmaganda buttonni yashirish
                self.btn_candidate_next.hide()

        except Exception as e:
            debug(f"Candidate face result handler error: {e}")

    def _on_staff_face_page(self):
        """Xodim yuz sahifasiga o'tish - test tanlangandan keyin"""
        try:
            # Tanlangan testni olish
            current_index = self.combo_choose_test.currentIndex()
            test_data = self.combo_choose_test.currentData()

            # Test tanlanganligini tekshirish
            if current_index == 0 or test_data is None:
                self.show_message("Ogohlantirish", "Iltimos, testni tanlang!", 1)
                return

            # Kamera tanlanganligini tekshirish
            if not self.page_main.validate_camera():
                return

            # Tanlangan kamera indexni saqlash
            camera_data = self.combo_choose_camera.currentData()
            if camera_data is not None and camera_data != -1:
                self.selected_camera_index = camera_data
            debug(f"Tanlangan kamera: {self.selected_camera_index}")

            # Test ma'lumotlarini saqlash
            self.chosen_test_key = test_data.get("key") or test_data.get("id")
            self.test_name = test_data.get("name")

            # Serverdan kelgan sozlamalarni setting_mode dan olish
            setting_mode = test_data.get("setting_mode", {})
            self.is_check_face_staff = setting_mode.get("is_check_face_staff", False)
            self.is_check_face_candidate = setting_mode.get("is_check_face_candidate", False)
            self.is_detect_monitor = setting_mode.get("is_detect_monitor", False)
            self.is_detect_camera = setting_mode.get("is_detect_camera", False)
            self.is_screen_record = setting_mode.get("is_screen_record", False)
            self.is_face_identification = setting_mode.get("is_face_identification", False)
            self.timer_face_id = setting_mode.get("timer_face_id", 10)  # Default 10 soniya
            self.warning_text = test_data.get("warning_text")

            debug(f"Tanlangan test: {self.test_name}, key: {self.chosen_test_key}")
            debug(f"Staff face check: {self.is_check_face_staff}")
            debug(f"Face identification: {self.is_face_identification}, timer: {self.timer_face_id}s")
            debug(f"Monitor check: {self.is_detect_monitor}")

            # Agar xodim yuz tekshiruvi yoqilgan bo'lsa - page_home ga o'tish
            if self.is_check_face_staff:
                self._next_page_by_name('page_home')
                self._start_staff_face_recognition()
            else:
                # Aks holda to'g'ridan-to'g'ri PINFL sahifasiga o'tish
                self._next_page_by_name('page_pinfl')

        except Exception as e:
            debug(f"Staff face page error: {e}")
            self.show_message("Xatolik", f"Xatolik yuz berdi: {e}", 0)

    def _start_staff_face_recognition(self):
        """Xodim yuz tekshiruvini boshlash"""
        try:
            if self.app is None:
                self.show_message("Xatolik", "Yuz aniqlash modeli yuklanmagan!", 0)
                return

            # Boshlang'ich holat - kutish (ko'k Material Design card)
            self.label_response.setText("Yuzingizni kameraga ko'rsating...")
            self.label_response.setStyleSheet("""
                QLabel {
                    color: #F2B703;
                }
            """)

            # Oldingi worker'larni to'xtatish
            if self.face_detector_worker and self.face_detector_worker.isRunning():
                self.face_detector_worker.stop()

            if self.face_staff_worker and self.face_staff_worker.isRunning():
                self.face_staff_worker.stop()

            # Face Detector Worker'ni boshlash
            self.face_detector_worker = FaceDetectorWorker(app=self.app, camera_index=self.selected_camera_index)
            self.face_detector_worker.face_detected.connect(self._on_staff_face_detected)
            self.face_detector_worker.camera_error.connect(self._on_camera_error)
            self.face_detector_worker.start()

            # Staff Face ID Worker'ni boshlash
            self.face_staff_worker = FaceIdStaffWorker(app=self.app)
            self.face_staff_worker.result_ready.connect(self._on_staff_face_result)
            self.face_staff_worker.start()

            debug("Staff face recognition boshlandi...")

        except Exception as e:
            debug(f"Start staff face recognition error: {e}")
            self.show_message("Xatolik", f"Yuz tekshiruvini boshlashda xatolik: {e}", 0)

    @pyqtSlot(object)
    def _on_staff_face_detected(self, data: dict):
        """Xodim yuzi aniqlanganda"""
        try:
            qt_image = data.get("image")
            cropped_face = data.get("crop_face")
            has_face = data.get("has_face", False)

            # Kamera tasvirini ko'rsatish (label_face page_home da)
            if qt_image and not qt_image.isNull():
                pixmap = QPixmap.fromImage(qt_image)
                scaled = pixmap.scaled(
                    self.label_face.size(),
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation
                )
                self.label_face.setPixmap(scaled)

            # Yuz aniqlansa, staff worker'ga yuborish
            if has_face and cropped_face is not None and self.face_staff_worker:
                # RGB formatga o'tkazish
                if len(cropped_face.shape) == 3:
                    rgb_face = cv2.cvtColor(cropped_face, cv2.COLOR_BGR2RGB)
                else:
                    rgb_face = cropped_face

                self.face_staff_worker.set_face(cropped_face=rgb_face)
            else:
                # Yuz topilmadi - sariq ogohlantirish
                self.label_response.setText("Yuzingizni kameraga ko'rsating...")
                self.label_response.setStyleSheet("""
                                QLabel {
                                    color: #F2B703;
                                }
                            """)

        except Exception as e:
            debug(f"Staff face detected handler error: {e}")

    @pyqtSlot(object)
    def _on_staff_face_result(self, data: dict):
        """Xodim yuz tekshiruvi natijasi"""
        try:
            is_verified = data.get("is_verified", False)
            message = data.get("message", "")

            if is_verified:
                # Muvaffaqiyatli - yashil Material Design card
                self.label_response.setText("Xodim tasdiqlandi!")
                self.label_response.setStyleSheet("""
                    QLabel {
                        color: green;
                    }
                """)

                # Face detection'ni to'xtatish
                if self.face_detector_worker and self.face_detector_worker.isRunning():
                    self.face_detector_worker.stop()

                if self.face_staff_worker and self.face_staff_worker.isRunning():
                    self.face_staff_worker.stop()

                # PINFL sahifasiga o'tish
                self._next_page_by_name('page_pinfl')
                debug(f"Xodim tasdiqlandi: {message}")
            else:
                # Tasdiqlanmadi - qizil Material Design card
                display_message = message if message else "Yuz tanilmadi"
                self.label_response.setText(f"{display_message}")
                self.label_response.setStyleSheet("""
                    QLabel {
                        color: red;
                    }
                """)

        except Exception as e:
            debug(f"Staff face result handler error: {e}")

    def _on_start_test(self):
        """Testni boshlash - WebView'da test sahifasini ochish"""
        try:
            if not self.chosen_test_key:
                self.show_message("Xatolik", "Test tanlanmagan!", 0)
                return

            # WebView yaratish (agar mavjud bo'lmasa)
            if self.webview is None:
                self.webview = QWebEngineView()
                self.webview.setWindowTitle(self.test_name or "Test")
                # WebView ni page_test sahifasidagi layout_test ga qo'shish
                self.layout_test.addWidget(self.webview)

            debug(f"Test_url: {self.test_url}")

            # Test sahifasini yuklash
            self.webview.setUrl(QUrl(self.test_url))

            # Test sahifasiga o'tish
            self._next_page_by_name('page_test')

            # Agar page_test mavjud bo'lmasa, WebView'ni to'liq ekranda ko'rsatish
            # yoki stack'ga qo'shish

            # Screen recording boshlash (agar yoqilgan bo'lsa)
            if self.is_screen_record:
                self._start_screen_recording()

            # Monitor tekshiruvni boshlash (agar yoqilgan bo'lsa)
            if self.is_detect_monitor:
                self._start_monitor_checking()

            # Real-time face monitoring boshlash (agar yoqilgan bo'lsa)
            debug(f"Face monitoring check: is_face_identification={self.is_face_identification}, ps_embedding={self.ps_embedding is not None}")
            if self.is_face_identification and self.ps_embedding is not None:
                self._start_face_monitoring()
            elif self.is_face_identification and self.ps_embedding is None:
                debug("OGOHLANTIRISH: ps_embedding yo'q - face monitoring ishlamaydi!")

            # Face identification o'chirilgan, lekin YOLO yoqilgan bo'lsa — faqat YOLO ishga tushsin
            if not self.is_face_identification and config.getboolean("YOLO", "enabled", fallback=True):
                self._start_yolo_only()

            debug(f"Test boshlandi: {self.test_name}")

        except Exception as e:
            debug(f"Start test error: {e}")
            self.show_message("Xatolik", f"Testni boshlashda xatolik: {e}", 0)

    def _start_screen_recording(self):
        """Ekran yozishni boshlash"""
        try:
            if self.screen_recorder_worker and self.screen_recorder_worker.isRunning():
                return  # Allaqachon ishlayapti

            self.screen_recorder_worker = ScreenRecorderWorker()
            self.screen_recorder_worker.start()
            debug("Screen recording boshlandi")

        except Exception as e:
            debug(f"Start screen recording error: {e}")

    def _start_monitor_checking(self):
        """Test davomida monitor sonini tekshirishni boshlash"""
        try:
            # Avval signalni ulab, keyin ishga tushirish
            if self.checker_monitor_worker:
                # Oldingi ulanishni uzish
                try:
                    self.checker_monitor_worker.result.disconnect()
                except Exception:
                    pass

                # Yangi ulanish
                self.checker_monitor_worker.result.connect(self._on_monitor_detected)

                # Worker ishlayotgan bo'lmasa, ishga tushirish
                if not self.checker_monitor_worker.isRunning():
                    self.checker_monitor_worker.start()

                debug("Monitor checking boshlandi")

        except Exception as e:
            debug(f"Start monitor checking error: {e}")

    def _stop_monitor_checking(self):
        """Monitor tekshirishni to'xtatish"""
        try:
            if self.checker_monitor_worker and self.checker_monitor_worker.isRunning():
                self.checker_monitor_worker.stop()
                debug("Monitor checking to'xtatildi")
        except Exception as e:
            debug(f"Stop monitor checking error: {e}")

    @pyqtSlot(bool)
    def _on_monitor_detected(self, has_multiple_monitors: bool):
        """Test davomida qo'shimcha monitor aniqlanganda"""
        try:
            if has_multiple_monitors:
                debug("OGOHLANTIRISH: Qo'shimcha monitor aniqlandi!")

                # Barcha worker'larni to'xtatish
                self._stop_monitor_checking()
                if self.face_detector_worker and self.face_detector_worker.isRunning():
                    self.face_detector_worker.stop()
                if self.camera1_worker and self.camera1_worker.isRunning():
                    self.camera1_worker.stop()
                if self.screen_recorder_worker and self.screen_recorder_worker.isRunning():
                    self.screen_recorder_worker.stop()

                # Kamera overlay'ni yashirish
                if hasattr(self, 'camera_overlay'):
                    self.camera_overlay.hide()

                # Warning modal ko'rsatish (3 soniyadan keyin avtomatik yopiladi)
                self.monitor_warning_modal.exec()

                # Modal yopilgandan keyin PINFL sahifasiga qaytish
                self._return_to_pinfl_page()

        except Exception as e:
            debug(f"Monitor detected handler error: {e}")

    def _on_camera_exit_requested(self):
        """Kamera overlay'dan chiqish so'ralganda"""
        try:
            debug("Testdan chiqish so'raldi...")

            # Barcha monitoring worker'larni to'xtatish
            self._stop_monitor_checking()
            self._stop_face_monitoring()

            if self.screen_recorder_worker and self.screen_recorder_worker.isRunning():
                self.screen_recorder_worker.stop()

            # Toast'larni tozalash
            if self.toast_manager:
                self.toast_manager.clear_all()

            # Kamera overlay'ni yashirish
            if hasattr(self, 'camera_overlay'):
                self.camera_overlay.hide()

            # PINFL sahifasiga qaytish
            self._return_to_pinfl_page()

        except Exception as e:
            debug(f"Camera exit error: {e}")

    def _return_to_pinfl_page(self):
        """PINFL sahifasiga qaytish va holatni tozalash"""
        try:
            # WebView'ni tozalash
            if self.webview:
                self.webview.setUrl(QUrl("about:blank"))

            # Input'ni tozalash
            self.input_pinfl.clear()

            # PINFL sahifasiga o'tish
            self._next_page_by_name('page_pinfl')

            debug("PINFL sahifasiga qaytildi")

        except Exception as e:
            debug(f"Return to PINFL page error: {e}")

    def _start_face_monitoring(self):
        """
        Test vaqtida yuzni kuzatishni boshlash

        Face Identification monitoring:
        - Har identification_interval soniyada yuz tanilganligini tekshiradi
        - identification_max_fail marta tanilmasa → warning (5s) + serverga yuborish
        - Keyin counter=0 va monitoring qaytadan boshlanadi
        """
        try:
            if self.app is None:
                debug("Face monitoring: Model yuklanmagan")
                return

            # Reset monitoring state
            self._reset_face_monitoring_state()

            # Kamera widget'ini page_test ustida overlay qilish
            page_test = None
            for i in range(self.stack.count()):
                if self.stack.widget(i).objectName() == 'page_test':
                    page_test = self.stack.widget(i)
                    break

            if page_test:
                self.camera_overlay.setParent(page_test)
                self.camera_overlay.show()
                self.camera_overlay.raise_()
                self.toast_manager.parent = page_test
                QTimer.singleShot(100, self._update_camera_overlay_position)

            # Face detector worker (continuous) - InsightFace orqali yengil detect
            if self.face_detector_worker is None or not self.face_detector_worker.isRunning():
                self.face_detector_worker = FaceDetectorWorker(app=self.app, camera_index=self.selected_camera_index)
                self.face_detector_worker.face_detected.connect(self._on_monitoring_face_detected)
                self.face_detector_worker.camera_error.connect(self._on_camera_error)
                self.face_detector_worker.start()

            # Camera1Worker - face identification (embedding comparison)
            # check_timer = identification_interval — har N soniyada 1 marta tekshiradi
            from workers import Camera1Worker
            self.camera1_worker = Camera1Worker(app=self.app)
            self.camera1_worker.check_timer = self.face_identification_interval
            self.camera1_worker.result_ready.connect(self._on_monitoring_result)

            # PersonDetectorWorker - YOLO orqali odam sonini tekshirish
            if config.getboolean("YOLO", "enabled", fallback=True):
                self.person_detector_worker = PersonDetectorWorker()
                self.person_detector_worker.person_count_changed.connect(self._on_person_count_changed)
                self.person_detector_worker.start()
            else:
                info("YOLO o'chirilgan (config: enabled=false)")

            debug(f"Face monitoring boshlandi:")
            debug(f"  - Identification interval: {self.face_identification_interval}s")
            debug(f"  - Identification max fail: {self.face_identification_max_fail}")
            debug(f"  - Monitoring score: {config.face_monitoring_score}%")

        except Exception as e:
            debug(f"Start face monitoring error: {e}")

    def _start_yolo_only(self):
        """
        Faqat YOLO ni mustaqil ishga tushirish.
        is_face_identification=False, lekin YOLO enabled=true bo'lganda.
        O'zi kamerani ochadi, FaceDetectorWorker ga bog'liq emas.
        """
        try:
            from workers import PersonDetectorWorker

            if self.person_detector_worker and self.person_detector_worker.isRunning():
                return  # Allaqachon ishlayapti

            self.person_detector_worker = PersonDetectorWorker(camera_index=self.selected_camera_index)
            self.person_detector_worker.person_count_changed.connect(self._on_person_count_changed)
            self.person_detector_worker.start()

            debug("YOLO mustaqil rejimda ishga tushdi (face identification o'chirilgan)")
        except Exception as e:
            debug(f"Start YOLO only error: {e}")

    def _reset_face_monitoring_state(self):
        """Face monitoring holatini qayta tiklash"""
        self.face_identification_fail_count = 0
        self.current_has_face = False
        self.current_is_verified = False
        self.current_person_count = 1  # Optimistik: YOLO yuklanguncha odam bor deb hisoblaymiz
        self.person_warning_shown = False

    def _stop_face_monitoring(self):
        """Face monitoring'ni to'xtatish"""
        try:
            if self.face_detector_worker and self.face_detector_worker.isRunning():
                self.face_detector_worker.stop()

            if self.camera1_worker and self.camera1_worker.isRunning():
                self.camera1_worker.stop()

            if self.person_detector_worker and self.person_detector_worker.isRunning():
                self.person_detector_worker.stop()

            debug("Face monitoring to'xtatildi")
        except Exception as e:
            debug(f"Stop face monitoring error: {e}")

    def _show_identification_warning(self):
        """
        Face identification warning — ekran o'rtasida sariq modal, 5 soniyada avtomatik yopiladi.
        """
        try:
            modal = InfoModal(self)
            modal.update_data(
                "Ogohlantirish!",
                "Yuz tanilmadi!\nIltimos, yuzingizni kameraga to'g'ri ko'rsating.",
                InfoModal.TYPE_WARNING  # Sariq rang: fon, tugma, icon — hammasi sariq
            )
            debug(f"[IDENTIFICATION] Warning modal ko'rsatilmoqda (TYPE_WARNING={InfoModal.TYPE_WARNING})")
            QTimer.singleShot(5000, modal.accept)
            modal.exec()
        except Exception as e:
            debug(f"Show identification warning error: {e}")

    def _send_warning_to_server(self, message: str):
        """Serverga warning yuborish"""
        try:
            if not self.im:
                debug("Warning yuborilmadi: PINFL mavjud emas")
                return

            api_client = APIClient(base_url=self.base_url)
            result = api_client.send_warning(
                pinfl=self.im,
                message=message,
                warning_type="face_monitoring_failed"
            )

            if result.get("status"):
                debug(f"Warning serverga yuborildi: {message}")
            else:
                debug(f"Warning yuborishda xatolik: {result.get('message')}")

        except Exception as e:
            debug(f"Send warning to server error: {e}")

    @pyqtSlot(object)
    def _on_monitoring_face_detected(self, data: dict):
        """Monitoring paytida yuz aniqlanganda"""
        try:
            qt_image = data.get("image")
            cropped_face = data.get("crop_face")
            has_face = data.get("has_face", False)

            # Face detection holatini yangilash (yangi state variable)
            self.current_has_face = has_face
            self.last_face_detected = has_face

            # Kamera tasvirini UI da ko'rsatish
            if qt_image and not qt_image.isNull():
                pixmap = QPixmap.fromImage(qt_image)
                self.camera_overlay.setPixmap(pixmap)

            # Agar yuz aniqlangan bo'lsa va Camera1Worker mavjud bo'lsa, yuzni yuborish
            # Test monitoring da config dagi monitoring_score ishlatiladi (serverdan kelgan score emas)
            if has_face and cropped_face is not None and hasattr(self, 'camera1_worker'):
                if self.camera1_worker:
                    rgb_face = cv2.cvtColor(cropped_face, cv2.COLOR_BGR2RGB)
                    self.camera1_worker.set_face(
                        ps_embedding=self.ps_embedding,
                        cropped_face=rgb_face,
                        score=config.face_monitoring_score
                    )

            # PersonDetectorWorker ga raw frame yuborish (YOLO odam soni tekshiruvi)
            raw_frame = data.get("raw_frame")
            if raw_frame is not None and self.person_detector_worker and self.person_detector_worker.isRunning():
                self.person_detector_worker.set_frame(raw_frame)

            # Agar yuz yo'q bo'lsa, identification natijasini ham reset qilish
            if not has_face:
                self.current_is_verified = False

        except Exception as e:
            debug(f"Monitoring face detected error: {e}")

    @pyqtSlot(object)
    def _on_monitoring_result(self, data: dict):
        """
        Camera1Worker natijasi — har identification_interval soniyada keladi.
        Fail hisoblash shu yerda — Camera1Worker haqiqiy tekshiruv qilgandan keyin.
        """
        try:
            is_verified = data.get("is_verified", False)
            similarity = data.get("similarity", 0)
            message = data.get("message", "")

            self.current_is_verified = is_verified

            if is_verified:
                # Yuz tanilib — fail count reset
                if self.face_identification_fail_count > 0:
                    self.face_identification_fail_count = 0
                    debug(f"[IDENTIFICATION] Yuz tanilib ({similarity}%) - fail count reset")
            else:
                # Yuz tanilmadi — fail count oshadi
                self.face_identification_fail_count += 1
                debug(f"[IDENTIFICATION] Tanilmadi ({similarity}%): "
                      f"{self.face_identification_fail_count}/{self.face_identification_max_fail}")

                if self.face_identification_fail_count >= self.face_identification_max_fail:
                    # 1. Warning dialog (5 soniya)
                    self._show_identification_warning()

                    # 2. Serverga yuborish
                    self._send_warning_to_server(
                        f"Yuz tanilmadi - {self.face_identification_max_fail} marta ketma-ket fail"
                    )

                    # 3. Counter reset — monitoring qaytadan boshlanadi
                    self.face_identification_fail_count = 0
                    debug("[IDENTIFICATION] Counter reset, monitoring davom etadi")

        except Exception as e:
            debug(f"Monitoring result error: {e}")

    @pyqtSlot(object)
    def _on_person_count_changed(self, data: dict):
        """YOLO orqali aniqlangan obyektlar o'zgarganda"""
        try:
            count = data.get("count", 0)
            forbidden = data.get("forbidden", {})
            self.current_person_count = count

            # Taqiqlangan obyektlar aniqlandi (person dan boshqa: telefon, sumka va h.k.)
            if forbidden:
                items = ", ".join(f"{name} ({cnt})" for name, cnt in forbidden.items())
                debug(f"[YOLO] Taqiqlangan obyektlar: {items}")
                self._show_yolo_toast(
                    f"Taqiqlangan obyekt aniqlandi: {items}",
                    toast_type="error"
                )
                self._send_warning_to_server(f"Taqiqlangan obyekt: {items}")

            if count == 0:
                debug("[PERSON_DETECT] Kamera oldida hech kim yo'q")

            elif count > 1:
                debug(f"[PERSON_DETECT] Kamera oldida {count} ta odam aniqlandi!")

                if not self.person_warning_shown:
                    self.person_warning_shown = True
                    self._show_yolo_toast(
                        f"Kamera oldida {count} ta odam aniqlandi! Faqat 1 ta odam bo'lishi kerak.",
                        toast_type="warning"
                    )
                    self._send_warning_to_server(
                        f"Kamera oldida {count} ta odam aniqlandi"
                    )
            else:
                # count == 1: normal holat — warning reset
                self.person_warning_shown = False

        except Exception as e:
            debug(f"Person count changed error: {e}")

    def _show_yolo_toast(self, message: str, toast_type: str = "error"):
        """YOLO ogohlantirish — pastki o'ng burchakda toast."""
        try:
            if self.toast_manager:
                self.toast_manager.show_toast(
                    message=message,
                    toast_type=toast_type,
                    duration=3000,
                    position="bottom-right"
                )
        except Exception as e:
            debug(f"YOLO toast error: {e}")
