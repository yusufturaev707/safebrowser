"""
Face Detector Worker
InsightFace asosidagi yuz aniqlash
Cross-platform qo'llab-quvvatlash
"""
import sys
import cv2
import numpy as np
from PyQt6.QtCore import QThread, pyqtSignal, QMutex, QMutexLocker
from PyQt6.QtGui import QImage
from utils.logger import info, debug, warning, error


class FaceDetectorWorker(QThread):
    """
    InsightFace asosidagi yuz aniqlash worker
    - Kam CPU/GPU resurs ishlatadi
    - Real-time kamera stream uchun optimallashtirilgan
    """
    face_detected = pyqtSignal(object)

    def __init__(self, app=None, camera_index: int = 0):
        super().__init__()
        self._running = True
        self._lock = QMutex()

        self.app = app
        self.camera_index = camera_index

        # Performance settings
        self.frame_skip = 2
        self.frame_counter = 0
        self.last_face_box = None
        self.detection_size = (320, 320)

        # Camera settings
        self.cap = None
        self.frame_width = 640
        self.frame_height = 480

    def set_app(self, app):
        """InsightFace app'ni o'rnatish"""
        self.app = app

    def is_running(self) -> bool:
        with QMutexLocker(self._lock):
            return self._running

    def stop(self):
        with QMutexLocker(self._lock):
            self._running = False
        self.wait()
        info("Face Detector Worker stopped")

    def _init_camera(self) -> bool:
        """Kamerani ishga tushirish (cross-platform)"""
        # Lazy import to avoid circular dependency
        from utils.system import open_camera, get_platform_name

        try:
            self.cap = open_camera(
                camera_index=self.camera_index,
                width=self.frame_width,
                height=self.frame_height,
                fps=30
            )

            if self.cap is None or not self.cap.isOpened():
                warning(f"Camera {self.camera_index} ochilmadi ({get_platform_name()})")
                return False

            info(f"Camera {self.camera_index} initialized ({get_platform_name()})")
            return True
        except Exception as e:
            error(f"Camera init error: {e}")
            return False

    def _detect_face_insightface(self, frame: np.ndarray):
        """
        InsightFace yordamida yuz aniqlash
        Multi-scale detection - yaqin va uzoqdan ham aniqlay oladi
        """
        if self.app is None:
            return None, None

        try:
            h, w = frame.shape[:2]
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            # Multi-scale detection
            scale_factor = 1.0

            # 1-urinish: Original o'lchamda detection
            faces = self.app.get(rgb_frame)

            # 2-urinish: 50% kichikroq (yaqindan qarash holati)
            if not faces:
                scale_factor = 0.5
                small_frame = cv2.resize(rgb_frame, None, fx=scale_factor, fy=scale_factor)
                faces = self.app.get(small_frame)

            # 3-urinish: 35% kichikroq
            if not faces:
                scale_factor = 0.35
                smaller_frame = cv2.resize(rgb_frame, None, fx=scale_factor, fy=scale_factor)
                faces = self.app.get(smaller_frame)

            # 4-urinish: 25% kichikroq (juda yaqin holat)
            if not faces:
                scale_factor = 0.25
                tiny_frame = cv2.resize(rgb_frame, None, fx=scale_factor, fy=scale_factor)
                faces = self.app.get(tiny_frame)

            if not faces:
                return None, None

            # Eng katta yuzni tanlash
            best_face = max(
                faces,
                key=lambda f: (f.bbox[2] - f.bbox[0]) * (f.bbox[3] - f.bbox[1])
            )

            # Bounding box ni original o'lchamga qaytarish
            bbox = best_face.bbox.astype(int)
            if scale_factor != 1.0:
                bbox = (bbox / scale_factor).astype(int)

            x1, y1, x2, y2 = bbox

            # Yuz o'lchami tekshiruvi
            face_width = x2 - x1
            face_height = y2 - y1
            face_area_ratio = (face_width * face_height) / (w * h)

            # Debug info
            debug(f"[FaceDetector] scale={scale_factor}, face_size={face_width}x{face_height}, ratio={face_area_ratio:.1%}")

            # Margin qo'shish - yaqin yuzlar uchun kichikroq margin
            if face_area_ratio > 0.4:  # Yuz juda yaqin (40% dan katta)
                margin_x, margin_y = 10, 15
            elif face_area_ratio > 0.2:  # O'rtacha masofa
                margin_x, margin_y = 20, 30
            else:  # Uzoqdan
                margin_x, margin_y = 25, 40

            x1 = max(0, x1 - margin_x)
            y1 = max(0, y1 - margin_y)
            x2 = min(w, x2 + margin_x)
            y2 = min(h, y2 + margin_y)

            cropped_face = frame[y1:y2, x1:x2].copy()
            return (x1, y1, x2, y2), cropped_face

        except Exception as e:
            error(f"Face detection error: {e}")
            return None, None

    def _draw_face_box(self, frame: np.ndarray, box: tuple):
        """Yuz atrofiga ramka chizish"""
        if box is None:
            return frame

        x1, y1, x2, y2 = box
        color = (0, 200, 100)
        thickness = 2
        corner_length = 20

        # Burchaklar
        cv2.line(frame, (x1, y1), (x1 + corner_length, y1), color, thickness)
        cv2.line(frame, (x1, y1), (x1, y1 + corner_length), color, thickness)
        cv2.line(frame, (x2, y1), (x2 - corner_length, y1), color, thickness)
        cv2.line(frame, (x2, y1), (x2, y1 + corner_length), color, thickness)
        cv2.line(frame, (x1, y2), (x1 + corner_length, y2), color, thickness)
        cv2.line(frame, (x1, y2), (x1, y2 - corner_length), color, thickness)
        cv2.line(frame, (x2, y2), (x2 - corner_length, y2), color, thickness)
        cv2.line(frame, (x2, y2), (x2, y2 - corner_length), color, thickness)

        return frame

    def _frame_to_qimage(self, frame: np.ndarray) -> QImage:
        """OpenCV frame'ni QImage'ga o'tkazish"""
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb_frame.shape
        bytes_per_line = ch * w
        return QImage(rgb_frame.data, w, h, bytes_per_line, QImage.Format.Format_RGB888)

    def run(self):
        """Asosiy thread loop"""
        if not self._init_camera():
            error("Camera initialization failed")
            return

        info("Face Detector Worker started")

        while self.is_running():
            try:
                ret, frame = self.cap.read()
                if not ret:
                    self.msleep(10)
                    continue

                self.frame_counter += 1
                cropped_face = None
                face_box = None

                # Frame skip
                if self.frame_counter % self.frame_skip == 0:
                    face_box, cropped_face = self._detect_face_insightface(frame)
                    if face_box:
                        self.last_face_box = face_box
                else:
                    face_box = self.last_face_box

                display_frame = self._draw_face_box(frame.copy(), face_box)
                qt_image = self._frame_to_qimage(display_frame)

                self.face_detected.emit({
                    "image": qt_image,
                    "crop_face": cropped_face,
                    "has_face": face_box is not None
                })

                self.msleep(33)

            except Exception as e:
                error(f"Frame processing error: {e}")
                self.msleep(50)

        if self.cap:
            self.cap.release()
        info("Face Detector Worker finished")
