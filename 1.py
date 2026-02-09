from ultralytics import YOLO
import cv2
import torch


class PersonDetector:
    def __init__(self):
        # GPU mavjudligini tekshirish
        self.device = 'cuda' if torch.cuda.is_available() else 'cpu'

        # Model yuklash
        self.model = YOLO('yolo11n.pt')
        self.model.to(self.device)

        print(f"🖥️ Qurilma: {self.device.upper()}")
        if self.device == 'cuda':
            print(f"🎮 GPU: {torch.cuda.get_device_name(0)}")

    def count_persons(self, frame):
        results = self.model.predict(
            frame,
            classes=[0],  # faqat odamlar
            conf=0.5,
            device=self.device,
            verbose=False
        )
        return len(results[0].boxes), results[0]


# Ishlatish
detector = PersonDetector()
cap = cv2.VideoCapture(0)

while True:
    ret, frame = cap.read()
    if not ret:
        break

    count, results = detector.count_persons(frame)

    annotated = results.plot()
    cv2.putText(annotated, f'Odamlar: {count}',
                (20, 50), cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 255, 0), 3)

    cv2.imshow('Detection', annotated)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()