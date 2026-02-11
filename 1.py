import cv2
import mediapipe as mp
import numpy as np

# MediaPipe Face Mesh
mp_face_mesh = mp.solutions.face_mesh
mp_drawing = mp.solutions.drawing_utils
drawing_spec = mp_drawing.DrawingSpec(thickness=1, circle_radius=1)

face_mesh = mp_face_mesh.FaceMesh(
    max_num_faces=1,
    refine_landmarks=True,  # Iris uchun
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5
)


def get_gaze_direction(landmarks, frame_shape):
    """Ko'z yo'nalishini aniqlash"""
    h, w = frame_shape[:2]

    # Chap ko'z nuqtalari
    # 159 - ko'z markazi, 468 - iris markazi
    left_eye_center = np.array([
        landmarks.landmark[159].x * w,
        landmarks.landmark[159].y * h
    ])
    left_iris_center = np.array([
        landmarks.landmark[468].x * w,
        landmarks.landmark[468].y * h
    ])

    # O'ng ko'z nuqtalari
    # 386 - ko'z markazi, 473 - iris markazi
    right_eye_center = np.array([
        landmarks.landmark[386].x * w,
        landmarks.landmark[386].y * h
    ])
    right_iris_center = np.array([
        landmarks.landmark[473].x * w,
        landmarks.landmark[473].y * h
    ])

    # O'rtacha gorizontal va vertikal siljish
    left_horizontal = left_iris_center[0] - left_eye_center[0]
    right_horizontal = right_iris_center[0] - right_eye_center[0]
    horizontal = (left_horizontal + right_horizontal) / 2

    left_vertical = left_iris_center[1] - left_eye_center[1]
    right_vertical = right_iris_center[1] - right_eye_center[1]
    vertical = (left_vertical + right_vertical) / 2

    # Yo'nalishni aniqlash
    gaze_horizontal = "CENTER"
    gaze_vertical = "CENTER"

    if horizontal < -2.5:
        gaze_horizontal = "LEFT"
    elif horizontal > 2.5:
        gaze_horizontal = "RIGHT"

    if vertical < -2:
        gaze_vertical = "UP"
    elif vertical > 2:
        gaze_vertical = "DOWN"

    # Bosh burilishini ham tekshirish
    nose_tip = landmarks.landmark[1]
    chin = landmarks.landmark[152]

    # Agar bosh burilgan bo'lsa
    nose_x = nose_tip.x * w
    chin_x = chin.x * w
    head_turn = nose_x - chin_x

    if abs(head_turn) > 20:
        if head_turn < 0:
            gaze_horizontal = "HEAD_LEFT"
        else:
            gaze_horizontal = "HEAD_RIGHT"

    return gaze_horizontal, gaze_vertical, horizontal, vertical


# Webcam ni ochish
cap = cv2.VideoCapture(0)

# Kamera sozlamalari
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

print("Kamera ishga tushdi. Chiqish uchun 'q' tugmasini bosing...")

while cap.isOpened():
    success, frame = cap.read()
    if not success:
        print("Kameradan rasm olib bo'lmadi")
        break

    # Rasmni aks ettirish (mirror effect)
    frame = cv2.flip(frame, 1)

    # RGB ga o'tkazish (MediaPipe RGB bilan ishlaydi)
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    # Yuzni aniqlash
    results = face_mesh.process(rgb_frame)

    if results.multi_face_landmarks:
        for face_landmarks in results.multi_face_landmarks:
            # Ko'z yo'nalishini aniqlash
            gaze_h, gaze_v, h_value, v_value = get_gaze_direction(face_landmarks, frame.shape)

            # Yuzni chizish (ixtiyoriy)
            # mp_drawing.draw_landmarks(
            #     frame,
            #     face_landmarks,
            #     mp_face_mesh.FACEMESH_IRISES,
            #     landmark_drawing_spec=drawing_spec,
            #     connection_drawing_spec=drawing_spec
            # )

            # Natijalarni ko'rsatish
            text_y = 30

            # Gorizontal yo'nalish
            color_h = (0, 255, 0) if gaze_h == "CENTER" else (0, 0, 255)
            cv2.putText(frame, f"Gorizontal: {gaze_h}", (10, text_y),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, color_h, 2)

            # Vertikal yo'nalish
            text_y += 30
            color_v = (0, 255, 0) if gaze_v == "CENTER" else (0, 0, 255)
            cv2.putText(frame, f"Vertikal: {gaze_v}", (10, text_y),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, color_v, 2)

            # Qiymatlar
            text_y += 30
            cv2.putText(frame, f"H: {h_value:.2f} | V: {v_value:.2f}", (10, text_y),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)

            # Katta holat ko'rsatkichi
            status_text = ""
            if gaze_h == "LEFT":
                status_text = "CHAPGA"
            elif gaze_h == "RIGHT":
                status_text = "O'NGGA"
            elif gaze_h == "HEAD_LEFT":
                status_text = "BOSH CHAPGA"
            elif gaze_h == "HEAD_RIGHT":
                status_text = "BOSH O'NGGA"
            elif gaze_v == "UP":
                status_text = "TEPAGA"
            elif gaze_v == "DOWN":
                status_text = "PASTGA"
            else:
                status_text = "MARKAZDA"

            # Markazda katta matn
            text_size = cv2.getTextSize(status_text, cv2.FONT_HERSHEY_SIMPLEX, 1.5, 3)[0]
            text_x = (frame.shape[1] - text_size[0]) // 2
            text_y = frame.shape[0] - 50

            color = (0, 255, 0) if status_text == "MARKAZDA" else (0, 0, 255)
            cv2.putText(frame, status_text, (text_x, text_y),
                        cv2.FONT_HERSHEY_SIMPLEX, 1.5, color, 3)

    else:
        cv2.putText(frame, "Yuz topilmadi", (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

    # Ekranda ko'rsatish
    cv2.imshow('Gaze Detection - q tugmasi bilan chiqish', frame)

    # 'q' tugmasi bosilsa chiqish
    if cv2.waitKey(5) & 0xFF == ord('q'):
        break

# Tozalash
cap.release()
cv2.destroyAllWindows()
face_mesh.close()