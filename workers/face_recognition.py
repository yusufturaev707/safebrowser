"""
Face Recognition Workers
Yuzni tanib olish va tekshirish workerlari
"""
import base64
import time
import queue
import gc
import numpy as np
import cv2
import requests
from PyQt6.QtCore import QThread, pyqtSignal, QMutex, QMutexLocker

from utils.helpers import cosine_similarity, get_percentage
from config.config import config
from utils.logger import debug, info, warning, error


def add_padding_to_face(face_image: np.ndarray, padding_ratio: float = 0.5) -> np.ndarray:
    """
    Cropped face ga fon (padding) qo'shish
    InsightFace detection uchun kerak - faqat yuz bo'lsa aniqlamaydi

    Args:
        face_image: Kesib olingan yuz rasmi
        padding_ratio: Qo'shiladigan padding nisbati (0.5 = 50% har tomondan)

    Returns:
        Padded image
    """
    if face_image is None:
        return None

    h, w = face_image.shape[:2]

    # Padding o'lchami
    pad_x = int(w * padding_ratio)
    pad_y = int(h * padding_ratio)

    # Yangi o'lcham
    new_w = w + 2 * pad_x
    new_h = h + 2 * pad_y

    # Qora fon bilan yangi rasm
    if len(face_image.shape) == 3:
        padded = np.zeros((new_h, new_w, face_image.shape[2]), dtype=face_image.dtype)
    else:
        padded = np.zeros((new_h, new_w), dtype=face_image.dtype)

    # Yuzni markazga joylashtirish
    padded[pad_y:pad_y+h, pad_x:pad_x+w] = face_image

    return padded

class CPUOptimizedFaceIdWorker(QThread):
    """
    Nomzod yuzini tekshirish workeri
    - Base64 rasm bilan solishtirish
    - Rate limiting
    - Memory management
    """
    result_ready = pyqtSignal(object)

    def __init__(self, app=None):
        super().__init__()
        self._running = True
        self.app = app
        self._lock = QMutex()
        self._task_queue = queue.Queue(maxsize=1)
        self.processing = False
        self.last_process_time = 0
        self.min_interval = 500
        self.process_count = 0

    def is_running(self) -> bool:
        with QMutexLocker(self._lock):
            return self._running

    def stop(self):
        with QMutexLocker(self._lock):
            self._running = False

        try:
            while not self._task_queue.empty():
                self._task_queue.get_nowait()
        except queue.Empty:
            pass

        gc.collect()
        self.wait()


    def add_task(
        self,
        image_base64: str = None,
        cropped_face=None,
        score = 85
    ) -> bool:
        """Yangi task qo'shish"""
        current_time = time.time() * 1000

        if current_time - self.last_process_time < self.min_interval:
            return False

        if self.processing:
            return False

        task = {
            "image_base64": image_base64,
            "cropped_face": cropped_face,
            "score": score
        }

        try:
            if not self._task_queue.empty():
                try:
                    self._task_queue.get_nowait()
                except queue.Empty:
                    pass

            self._task_queue.put_nowait(task)

            if not self.isRunning():
                self.start()

            return True
        except queue.Full:
            return False

    def _decode_base64_image(self, image_base64: str):
        """Base64 rasmni decode qilish"""
        try:
            if not image_base64 or "," not in image_base64:
                return None, "Noto'g'ri format"

            image_data = image_base64.split(",")[1]
            img_bytes = base64.b64decode(image_data)
            np_arr = np.frombuffer(img_bytes, np.uint8)
            img = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

            if img is None:
                return None, "Rasm decode bo'lmadi"

            return cv2.cvtColor(img, cv2.COLOR_BGR2RGB), None
        except Exception as e:
            return None, str(e)

    def _get_embedding(self, image) -> tuple:
        """
        Rasmdan embedding olish
        Padding + Multi-scale detection
        """
        try:
            h, w = image.shape[:2]
            method_used = "original"

            # 1-urinish: Original o'lchamda
            faces = self.app.get(image)

            # 2-urinish: Padding qo'shish (cropped face uchun)
            if not faces:
                method_used = "padded"
                padded_image = add_padding_to_face(image, padding_ratio=0.6)
                faces = self.app.get(padded_image)

            # 3-urinish: Kichikroq padding
            if not faces:
                method_used = "padded_small"
                padded_image = add_padding_to_face(image, padding_ratio=0.4)
                faces = self.app.get(padded_image)

            # 4-urinish: Resize qilish
            if not faces and w > 200 and h > 200:
                method_used = "resized_0.5"
                small_image = cv2.resize(image, None, fx=0.5, fy=0.5)
                padded_small = add_padding_to_face(small_image, padding_ratio=0.5)
                faces = self.app.get(padded_small)

            if not faces:
                debug(f"[GetEmbedding] Yuz topilmadi! size={w}x{h}")
                return None, "Yuz topilmadi"

            debug(f"[GetEmbedding] OK: method={method_used}, size={w}x{h}")
            return faces[0].embedding, None
        except Exception as e:
            return None, str(e)

    def _process_task(self, task: dict):
        """Taskni bajarish"""
        self.processing = True
        self.process_count += 1

        try:
            image_base64 = task.get("image_base64")
            cropped_face = task.get("cropped_face")
            score = task.get("score", 85)

            ps_image, error = self._decode_base64_image(image_base64)
            if error:
                self.result_ready.emit({
                    "status": "error",
                    "is_verified": False,
                    "message": error
                })
                return

            ps_embedding, error = self._get_embedding(ps_image)
            if error:
                self.result_ready.emit({
                    "status": "error",
                    "is_verified": False,
                    "message": f"Pasport rasm: {error}"
                })
                return

            live_embedding, error = self._get_embedding(cropped_face)
            if error:
                self.result_ready.emit({
                    "status": "error",
                    "is_verified": False,
                    "message": f"Live yuz: {error}"
                })
                return

            similarity = cosine_similarity(ps_embedding, live_embedding)
            similarity_percent = get_percentage(similarity, threshold=0.5)
            is_match = 0 < score <= similarity_percent
            debug(f"Percentage: {similarity_percent}%, Required: {score}%")

            self.result_ready.emit({
                "status": "success",
                "is_verified": is_match,
                "similarity": similarity_percent,
                "threshold": score,
                "ps_embedding": live_embedding.tolist() if is_match else None,
                "message": f"O'xshashlik: {similarity_percent}%"
            })

        except Exception as e:
            self.result_ready.emit({
                "status": "error",
                "is_verified": False,
                "message": f"Xatolik: {e}"
            })
        finally:
            self.processing = False
            self.last_process_time = time.time() * 1000

            if self.process_count % 10 == 0:
                gc.collect()

    def run(self):
        """Asosiy loop"""
        while self.is_running():
            try:
                try:
                    task = self._task_queue.get(timeout=2)
                except queue.Empty:
                    continue

                self._process_task(task)
                self.msleep(200)

            except Exception as e:
                debug(f"CPUOptimizedFaceIdWorker error: {e}")
                self.msleep(500)


class FaceIdStaffWorker(QThread):
    """
    Xodim yuzini server orqali tekshirish workeri
    """
    result_ready = pyqtSignal(object)

    def __init__(self, app=None):
        super().__init__()
        self._running = True
        self.app = app
        self._lock = QMutex()
        self.cropped_face = None

    def is_running(self) -> bool:
        with QMutexLocker(self._lock):
            return self._running

    def stop(self):
        with QMutexLocker(self._lock):
            self._running = False
        self.wait()

    def set_face(self, cropped_face=None, **kwargs):
        """Yangi yuz o'rnatish"""
        with QMutexLocker(self._lock):
            self.cropped_face = cropped_face

    def _get_face(self):
        """Thread-safe face olish"""
        with QMutexLocker(self._lock):
            face = self.cropped_face
            self.cropped_face = None
            return face

    def _verify_staff(self, face):
        """Xodimni server orqali tekshirish"""
        try:
            if face is None:
                return {"is_verified": False, "message": "Yuz topilmadi"}

            if self.app is None:
                return {"is_verified": False, "message": "Model yuklanmadi"}

            # Padding + Multi-scale detection
            h, w = face.shape[:2]
            method_used = "original"
            faces = self.app.get(face)

            # Padding qo'shish (cropped face uchun asosiy yechim)
            if not faces:
                method_used = "padded"
                padded_face = add_padding_to_face(face, padding_ratio=0.6)
                faces = self.app.get(padded_face)

            # Kichikroq padding
            if not faces:
                method_used = "padded_small"
                padded_face = add_padding_to_face(face, padding_ratio=0.4)
                faces = self.app.get(padded_face)

            # Resize + padding
            if not faces and w > 200 and h > 200:
                method_used = "resized+padded"
                small_face = cv2.resize(face, None, fx=0.5, fy=0.5)
                padded_small = add_padding_to_face(small_face, padding_ratio=0.5)
                faces = self.app.get(padded_small)

            if not faces:
                debug(f"[StaffVerify] Yuz aniqlanmadi! size={w}x{h}")
                return {"is_verified": False, "message": "Yuz aniqlanmadi"}

            debug(f"[StaffVerify] OK: method={method_used}, size={w}x{h}")
            embedding = faces[0].embedding.tolist()

            response = requests.post(
                f"{config.api_base_url}users/face_identification/",
                json={"embedding": str(embedding)},
                timeout=10
            )

            data = response.json()

            return {
                "is_verified": data.get("verified", False),
                "message": data.get("message", "")
            }

        except requests.exceptions.Timeout:
            return {"is_verified": False, "message": "Server javob bermadi"}
        except requests.exceptions.RequestException as e:
            return {"is_verified": False, "message": f"Server xatolik: {e}"}
        except Exception as e:
            return {"is_verified": False, "message": f"Xatolik: {e}"}

    def run(self):
        """Asosiy loop"""
        while self.is_running():
            face = self._get_face()
            if face is not None:
                result = self._verify_staff(face)
                self.result_ready.emit(result)
            self.msleep(100)


class Camera1Worker(QThread):
    """
    Test vaqtida yuzni real-time tekshirish workeri
    """
    result_ready = pyqtSignal(object)

    def __init__(self, app=None):
        super().__init__()
        self._lock = QMutex()
        self.app = app
        self._running = False
        self.ps_embedding = None
        self.cropped_face = None
        self.score = 40
        self.check_timer = 10
        self.last_check_time = 0

    def is_running(self) -> bool:
        with QMutexLocker(self._lock):
            return self._running

    def stop(self):
        with QMutexLocker(self._lock):
            self._running = False
        self.wait()

    def set_face(
        self,
        ps_embedding=None,
        cropped_face=None,
        score: int = 40,
        check_timer: int = 10
    ):
        """Yangi yuz ma'lumotlarini o'rnatish"""
        with QMutexLocker(self._lock):
            if ps_embedding is not None:
                self.ps_embedding = ps_embedding
            if cropped_face is not None:
                self.cropped_face = cropped_face
            self.score = score
            self.check_timer = check_timer

            if not self._running:
                self._running = True
                self.last_check_time = 0
                if not self.isRunning():
                    self.start()

    def _get_data(self):
        """Thread-safe data olish"""
        with QMutexLocker(self._lock):
            embedding = self.ps_embedding
            face = self.cropped_face
            # ps_embedding ni saqlab qolish - bu test davomida doimiy
            # Faqat cropped_face ni tozalash
            self.cropped_face = None
            return embedding, face

    def _verify_face(self, ps_embedding, live_face) -> dict:
        """
        Yuzni tekshirish
        Multi-scale detection qo'llab-quvvatlash
        """
        try:
            if self.app is None:
                return {"is_verified": False, "message": "App not initialized"}

            # Padding + Multi-scale detection
            h, w = live_face.shape[:2]
            method_used = "original"
            faces = self.app.get(live_face)

            # Padding qo'shish (cropped face uchun asosiy yechim)
            if not faces:
                method_used = "padded"
                padded_face = add_padding_to_face(live_face, padding_ratio=0.6)
                faces = self.app.get(padded_face)

            # Kichikroq padding
            if not faces:
                method_used = "padded_small"
                padded_face = add_padding_to_face(live_face, padding_ratio=0.4)
                faces = self.app.get(padded_face)

            # Resize + padding
            if not faces and w > 200 and h > 200:
                method_used = "resized+padded"
                small_face = cv2.resize(live_face, None, fx=0.5, fy=0.5)
                padded_small = add_padding_to_face(small_face, padding_ratio=0.5)
                faces = self.app.get(padded_small)

            if not faces:
                debug(f"[Camera1Verify] Yuz topilmadi! size={w}x{h}")
                return {"is_verified": False, "message": "Yuz topilmadi"}

            debug(f"[Camera1Verify] OK: method={method_used}, size={w}x{h}")

            live_embedding = faces[0].embedding

            similarity = cosine_similarity(live_embedding, ps_embedding)
            similarity_percent = get_percentage(similarity, threshold=0.5)
            debug(f"Similarity_percent: {similarity_percent}%")
            debug(f"Required score: {self.score}%")

            is_match = 0 < self.score <= similarity_percent

            return {
                "is_verified": is_match,
                "similarity": similarity_percent,
                "message": "Tasdiqlandi" if is_match else "Tasdiqlanmadi"
            }

        except Exception as e:
            return {"is_verified": False, "message": f"Xatolik: {e}"}

    def run(self):
        """Asosiy loop"""
        while self.is_running():
            try:
                current_time = time.time()

                if current_time - self.last_check_time >= self.check_timer:
                    self.last_check_time = current_time

                    ps_embedding, cropped_face = self._get_data()

                    if ps_embedding is None or cropped_face is None:
                        self.result_ready.emit({
                            "is_verified": False,
                            "message": "Ma'lumot yo'q"
                        })
                    else:
                        result = self._verify_face(ps_embedding, cropped_face)
                        self.result_ready.emit(result)

                self.msleep(100)

            except Exception as e:
                debug(f"Camera1Worker error: {e}")
                self.msleep(500)
