import cv2
from insightface.app import FaceAnalysis

# Faqat 'det' (detection) modulini yuklaymiz.
# 'rec' (recognition) va boshqalarni yuklamaslik orqali tezlikni oshiramiz.
app = FaceAnalysis(allowed_modules=['detection'])
app.prepare(ctx_id=0, det_size=(640, 640)) # ctx_id=0 agar GPU bo'lsa, -1 agar CPU bo'lsa

cap = cv2.VideoCapture(0)

while cap.isOpened():
    success, frame = cap.read()
    if not success: break

    # Yuzni aniqlash
    faces = app.get(frame)

    if len(faces) > 0:
        # Yuz topildi
        for face in faces:
            bbox = face.bbox.astype(int)
            cv2.rectangle(frame, (bbox[0], bbox[1]), (bbox[2], bbox[3]), (0, 255, 0), 2)
            cv2.putText(frame, "User Online", (bbox[0], bbox[1]-10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
    else:
        # Yuz topilmadi
        cv2.putText(frame, "WARNING: No Face Detected", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 3)

    cv2.imshow('InsightFace Proctoring', frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()