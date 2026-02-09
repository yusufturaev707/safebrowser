"""
Person Detector Worker
YOLO v11 asosidagi odam sonini aniqlash
Test vaqtida kamera oldida faqat 1 ta odam bo'lishi kerak
"""
import numpy as np
from PyQt6.QtCore import QThread, pyqtSignal, QMutex, QMutexLocker
from utils.logger import info, debug, warning, error


class PersonDetectorWorker(QThread):
    """
    YOLO v11 asosidagi odam soni aniqlash worker.
    FaceDetectorWorker dan frame qabul qilib, odam sonini tekshiradi.
    Kamerani o'zi ochmaydi — frame set_frame() orqali beriladi.
    """
    person_count_changed = pyqtSignal(object)

    def __init__(self):
        super().__init__()
        self._running = True
        self._lock = QMutex()
        self._frame = None
        self._frame_ready = False

        # YOLO model
        self._model = None

        # Performance: har N kadrda bir marta YOLO ishlatish
        self._frame_counter = 0
        self._frame_skip = 4  # har 4-kadrda 1 marta detect

        # Oldingi odam soni (faqat o'zgarganda signal emit qilish uchun)
        self._last_person_count = 0

    def _init_model(self) -> bool:
        """YOLO modelni yuklash (GPU/CPU avtomatik)"""
        try:
            from ultralytics import YOLO
            import torch

            self._model = YOLO("yolo11n.pt")

            # GPU mavjud bo'lsa GPU da, bo'lmasa CPU da
            if torch.cuda.is_available():
                self._model.to("cuda")
                info("PersonDetector: YOLO model GPU (CUDA) da yuklandi")
            else:
                info("PersonDetector: YOLO model CPU da yuklandi")

            return True
        except Exception as e:
            error(f"PersonDetector: YOLO model yuklashda xatolik: {e}")
            return False

    def set_frame(self, frame: np.ndarray):
        """Thread-safe frame qabul qilish (FaceDetectorWorker dan)"""
        with QMutexLocker(self._lock):
            self._frame = frame
            self._frame_ready = True

    def _get_frame(self):
        """Thread-safe frame olish"""
        with QMutexLocker(self._lock):
            if self._frame_ready:
                frame = self._frame
                self._frame_ready = False
                return frame
            return None

    def is_running(self) -> bool:
        with QMutexLocker(self._lock):
            return self._running

    def stop(self):
        with QMutexLocker(self._lock):
            self._running = False
        self.wait()
        info("PersonDetector Worker stopped")

    def _detect_persons(self, frame: np.ndarray) -> int:
        """YOLO orqali faqat 'person' klassini aniqlash"""
        try:
            results = self._model.predict(
                frame,
                classes=[0],       # faqat person (COCO class 0)
                conf=0.5,
                verbose=False
            )
            if results and len(results) > 0:
                return len(results[0].boxes)
            return 0
        except Exception as e:
            error(f"PersonDetector: detect xatolik: {e}")
            return 0

    def run(self):
        """Asosiy thread loop"""
        if not self._init_model():
            error("PersonDetector: Model yuklanmadi, worker to'xtatildi")
            return

        info("PersonDetector Worker started")

        while self.is_running():
            try:
                frame = self._get_frame()
                if frame is None:
                    self.msleep(50)
                    continue

                self._frame_counter += 1

                # Frame skip — resurs tejash
                if self._frame_counter % self._frame_skip != 0:
                    continue

                # YOLO detect
                count = self._detect_persons(frame)

                # Signal: odam soni o'zgarganda
                if count != self._last_person_count:
                    self._last_person_count = count
                    self.person_count_changed.emit({
                        "count": count,
                        "frame": frame
                    })
            except Exception as e:
                error(f"PersonDetector: frame processing xatolik: {e}")
                self.msleep(100)

        info("PersonDetector Worker finished")
