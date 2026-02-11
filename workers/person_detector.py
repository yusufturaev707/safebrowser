"""
Person Detector Worker
YOLO v11 asosidagi odam sonini aniqlash
Test vaqtida kamera oldida faqat 1 ta odam bo'lishi kerak
"""
import os
from pathlib import Path

import cv2
import numpy as np
from PyQt6.QtCore import QThread, pyqtSignal, QMutex, QMutexLocker
from config import config
from utils.logger import info, debug, warning, error


class PersonDetectorWorker(QThread):
    """
    YOLO v11 asosidagi odam soni aniqlash worker.

    2 ta rejim:
    1. Tashqi frame rejimi: FaceDetectorWorker dan set_frame() orqali frame oladi
    2. Mustaqil kamera rejimi: camera_index berilsa, o'zi kamerani ochadi
       (is_face_identification=False, lekin YOLO enabled=true bo'lganda)
    """
    person_count_changed = pyqtSignal(object)

    def __init__(self, camera_index: int = None):
        super().__init__()
        self._running = True
        self._lock = QMutex()
        self._frame = None
        self._frame_ready = False

        # Kamera rejimi: camera_index berilsa o'zi kamerani ochadi
        self._camera_index = camera_index
        self._cap = None

        # YOLO model
        self._model = None

        # Config dan sozlamalar
        self._model_name = config.get("YOLO", "model_name", fallback="yolo11m.pt")
        self._classes = self._parse_classes(config.get("YOLO", "classes", fallback="0"))
        self._confidence = float(config.get("YOLO", "confidence", fallback="0.5"))

        # Performance: har N kadrda bir marta YOLO ishlatish
        self._frame_counter = 0
        self._frame_skip = config.getint("YOLO", "frame_skip", fallback=4)

        # Oldingi odam soni (faqat o'zgarganda signal emit qilish uchun)
        self._last_person_count = 0

        mode = "mustaqil kamera" if self._camera_index is not None else "tashqi frame"
        info(f"PersonDetector: model={self._model_name}, classes={self._classes}, "
             f"conf={self._confidence}, frame_skip={self._frame_skip}, rejim={mode}")

    @staticmethod
    def _parse_classes(classes_str: str) -> list:
        """Config dan class ID larni parse qilish (masalan: '0,67' -> [0, 67])"""
        try:
            return [int(c.strip()) for c in classes_str.split(",") if c.strip()]
        except ValueError:
            warning(f"PersonDetector: classes parse xatolik: '{classes_str}', default [0] ishlatiladi")
            return [0]

    def _init_camera(self) -> bool:
        """Mustaqil rejimda kamerani ochish"""
        from utils.system import open_camera

        try:
            self._cap = open_camera(
                camera_index=self._camera_index,
                width=config.getint("CAMERA", "width", fallback=640),
                height=config.getint("CAMERA", "height", fallback=480),
                fps=config.getint("CAMERA", "fps", fallback=30)
            )
            if self._cap is None or not self._cap.isOpened():
                error(f"PersonDetector: Camera {self._camera_index} ochilmadi")
                return False

            info(f"PersonDetector: Camera {self._camera_index} ochildi (mustaqil rejim)")
            return True
        except Exception as e:
            error(f"PersonDetector: Camera init xatolik: {e}")
            return False

    def _init_model(self) -> bool:
        """YOLO modelni yuklash (GPU/CPU avtomatik)"""
        try:
            from ultralytics import YOLO
            import torch

            base_dir = Path(__file__).resolve().parent.parent
            model_path = os.path.join(base_dir, "weights", self._model_name)
            self._model = YOLO(str(model_path))

            # GPU mavjud bo'lsa GPU da, bo'lmasa CPU da
            if torch.cuda.is_available():
                self._model.to("cuda")
                info(f"PersonDetector: YOLO model '{self._model_name}' GPU (CUDA) da yuklandi")
            else:
                info(f"PersonDetector: YOLO model '{self._model_name}' CPU da yuklandi")

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
        if self._cap:
            self._cap.release()
            self._cap = None
        info("PersonDetector Worker stopped")

    def _detect(self, frame: np.ndarray) -> dict:
        """
        YOLO orqali config dagi klasslarni aniqlash.
        Natija: {"person": 2, "cell phone": 1} shaklida
        """
        try:
            results = self._model.predict(
                frame,
                classes=self._classes,
                conf=self._confidence,
                verbose=False
            )
            detections = {}
            if results and len(results) > 0:
                boxes = results[0].boxes
                for box in boxes:
                    cls_id = int(box.cls[0])
                    cls_name = self._model.names.get(cls_id, f"class_{cls_id}")
                    detections[cls_name] = detections.get(cls_name, 0) + 1
            return detections
        except Exception as e:
            error(f"PersonDetector: detect xatolik: {e}")
            return {}

    def run(self):
        """Asosiy thread loop"""
        # Mustaqil kamera rejimi — o'zi kamerani ochadi
        if self._camera_index is not None:
            if not self._init_camera():
                error("PersonDetector: Kamera ochilmadi, worker to'xtatildi")
                return

        if not self._init_model():
            error("PersonDetector: Model yuklanmadi, worker to'xtatildi")
            return

        info("PersonDetector Worker started")

        while self.is_running():
            try:
                # Frame olish: kamera rejimi yoki tashqi frame rejimi
                if self._cap:
                    ret, frame = self._cap.read()
                    if not ret:
                        self.msleep(10)
                        continue
                else:
                    frame = self._get_frame()
                    if frame is None:
                        self.msleep(50)
                        continue

                self._frame_counter += 1

                # Frame skip — resurs tejash
                if self._frame_counter % self._frame_skip != 0:
                    continue

                # YOLO detect
                detections = self._detect(frame)
                person_count = detections.get("person", 0)

                # Taqiqlangan obyektlar (person dan boshqa hamma narsa)
                forbidden = {k: v for k, v in detections.items() if k != "person"}

                # Signal: odam soni o'zgarganda yoki taqiqlangan obyekt topilganda
                if person_count != self._last_person_count or forbidden:
                    self._last_person_count = person_count
                    self.person_count_changed.emit({
                        "count": person_count,
                        "detections": detections,
                        "forbidden": forbidden,
                        "frame": frame
                    })
            except Exception as e:
                error(f"PersonDetector: frame processing xatolik: {e}")
                self.msleep(100)

        if self._cap:
            self._cap.release()
            self._cap = None
        info("PersonDetector Worker finished")
