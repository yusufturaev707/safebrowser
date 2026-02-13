import mediapipe as mp
import cv2
import numpy as np


class SleepDetector:
    def __init__(self):
        self.mp_face_mesh = mp.solutions.face_mesh
        self.face_mesh = self.mp_face_mesh.FaceMesh(
            max_num_faces=1,
            refine_landmarks=True,
            min_detection_confidence=0.5
        )

        # Ko'z landmarklari (MediaPipe Face Mesh)
        self.LEFT_EYE = [362, 385, 387, 263, 373, 380]
        self.RIGHT_EYE = [33, 160, 158, 133, 153, 144]

        self.EAR_THRESHOLD = 0.2  # Threshold
        self.CONSEC_FRAMES = 20  # 20 frame ketma-ket yopiq bo'lsa uxlayapti
        self.frame_counter = 0

    def calculate_ear(self, eye_landmarks):
        """Eye Aspect Ratio hisoblash"""
        # Vertikal masofalar
        A = np.linalg.norm(eye_landmarks[1] - eye_landmarks[5])
        B = np.linalg.norm(eye_landmarks[2] - eye_landmarks[4])

        # Gorizontal masofa
        C = np.linalg.norm(eye_landmarks[0] - eye_landmarks[3])

        # EAR formulasi
        ear = (A + B) / (2.0 * C)
        return ear

    def get_eye_landmarks(self, landmarks, indices, frame_shape):
        """Ko'z nuqtalarini olish"""
        h, w = frame_shape[:2]
        coords = []
        for idx in indices:
            landmark = landmarks[idx]
            x = int(landmark.x * w)
            y = int(landmark.y * h)
            coords.append([x, y])
        return np.array(coords)

    def detect_sleep(self, frame):
        """Uxlashni aniqlash"""
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.face_mesh.process(rgb_frame)

        is_sleeping = False
        ear_value = 0

        if results.multi_face_landmarks:
            landmarks = results.multi_face_landmarks[0].landmark

            # Chap va o'ng ko'z uchun EAR hisoblash
            left_eye = self.get_eye_landmarks(landmarks, self.LEFT_EYE, frame.shape)
            right_eye = self.get_eye_landmarks(landmarks, self.RIGHT_EYE, frame.shape)

            left_ear = self.calculate_ear(left_eye)
            right_ear = self.calculate_ear(right_eye)

            ear_value = (left_ear + right_ear) / 2.0

            # Ko'z yopiq bo'lsa
            if ear_value < self.EAR_THRESHOLD:
                self.frame_counter += 1

                # Ma'lum vaqt yopiq bo'lsa - uxlayapti
                if self.frame_counter >= self.CONSEC_FRAMES:
                    is_sleeping = True
            else:
                self.frame_counter = 0

        return is_sleeping, ear_value, self.frame_counter


# Ishlatish
detector = SleepDetector()

cap = cv2.VideoCapture(0)
while True:
    ret, frame = cap.read()
    if not ret:
        break

    is_sleeping, ear, counter = detector.detect_sleep(frame)

    # Vizualizatsiya
    status = "UXLAYAPTI!" if is_sleeping else "HUSHYOR"
    color = (0, 0, 255) if is_sleeping else (0, 255, 0)

    cv2.putText(frame, f"Status: {status}", (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)
    cv2.putText(frame, f"EAR: {ear:.2f}", (10, 60),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
    cv2.putText(frame, f"Frames: {counter}/{detector.CONSEC_FRAMES}", (10, 90),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)

    cv2.imshow('Sleep Detection', frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()