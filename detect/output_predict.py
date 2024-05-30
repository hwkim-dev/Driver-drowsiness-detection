import cv2
import torch
import numpy as np
from ultralytics import YOLO
import time

class predict:
    def __init__(self):
        self.class_names = {0: 'Face', 1: 'Eye open', 2: 'Eye closed', 3: 'Eye open', 4: 'Eye closed', 5: 'Mouth'}
        self.CONFIDENCE_THRESHOLD = 0.3
        self.prev_frame_time = 0

    def run(self, detect, shared_memory_fps):
        model = YOLO(r"C:\D\github\Driver-drowsiness-detection\detect\best (9).pt")
        cap = cv2.VideoCapture(0)
        TARGET_WIDTH = 640
        TARGET_HEIGHT = 480
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, TARGET_WIDTH)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, TARGET_HEIGHT)

        try:
            while cap.isOpened():
                ret, frame = cap.read()
                if not ret:
                    break

                frame_resized = cv2.resize(frame, (TARGET_WIDTH, TARGET_HEIGHT))
                results = model(frame_resized, device='cuda' if torch.cuda.is_available() else 'cpu', stream=True)

                
                detect.calc_fps(shared_memory_fps)

                for result in results:
                    for box in result.boxes:
                        x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                        conf = box.conf[0].cpu().numpy()
                        cls = int(box.cls[0].cpu().numpy())

                        if conf < self.CONFIDENCE_THRESHOLD:
                            continue

                        label = self.class_names.get(cls, 'Unknown')
                        color = (255, 255, 255)

                        if label == 'Eye closed':
                            if detect.eye_close_detect():
                                cv2.putText(frame_resized, 'Drowsiness Detected!', (50, 50), cv2.FONT_HERSHEY_SIMPLEX,
                                            1.5, (0, 0, 255), 3)
                            color = (0, 0, 255)
                        elif label == 'Eye open':
                            detect.reset_eye_closed()
                            color = (0, 255, 0)

                        cv2.rectangle(frame_resized, (int(x1), int(y1)), (int(x2), int(y2)), color, 2)
                        cv2.putText(frame_resized, f'{label}', (int(x1), int(y1) - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9,
                                    color, 2)

                cv2.putText(frame_resized, f'FPS: {int(shared_memory_fps.Value)}', (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1,
                            (0, 255, 255), 2)

                cv2.imshow('Drowsiness Detection', frame_resized)
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
        except KeyboardInterrupt:
            pass
        finally:
            cap.release()
            cv2.destroyAllWindows()
# import cv2
# import torch
# import numpy as np
# from ultralytics import YOLO
# import time
#
#
# class predict:
#     def __init__(self):
#         self.class_names = {0: 'Face', 1: 'Eye open', 2: 'Eye closed', 3: 'Eye open', 4: 'Eye closed', 5: 'Mouth'}
#         self.CONFIDENCE_THRESHOLD = 0.3
#         self.prev_frame_time = 0
#         self.drowsy_detected_t = 0
#         self.alarm_time = 2
#
#     def run(self, detect):
#         model = YOLO(r"best (9).pt")
#         cap = cv2.VideoCapture(0)
#         TARGET_WIDTH = 640
#         TARGET_HEIGHT = 480
#         cap.set(cv2.CAP_PROP_FRAME_WIDTH, TARGET_WIDTH)
#         cap.set(cv2.CAP_PROP_FRAME_HEIGHT, TARGET_HEIGHT)
#
#         try:
#             while cap.isOpened():
#                 ret, frame = cap.read()
#                 if not ret:
#                     break
#
#                 frame_resized = cv2.resize(frame, (TARGET_WIDTH, TARGET_HEIGHT))
#                 results = model(frame_resized, device='cuda' if torch.cuda.is_available() else 'cpu', stream=True)
#
#                 fps = detect.calc_fps()
#
#                 for result in results:
#                     for box in result.boxes:
#                         x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
#                         conf = box.conf[0].cpu().numpy()
#                         cls = int(box.cls[0].cpu().numpy())
#
#                         if conf < self.CONFIDENCE_THRESHOLD:
#                             continue
#
#                         label = self.class_names.get(cls, 'Unknown')
#                         color = (255, 255, 255)
#
#                         if label == 'Eye closed':
#                             if detect.eye_close_detect():
#                                 self.drowsy_detected_t = time.time()
#                             color = (0, 0, 255)
#                         elif label == 'Eye open':
#                             if not detect.eye_open():
#                                 self.drowsy_detected_t += 10
#                             color = (0, 255, 0)
#
#                         if time.time() - self.drowsy_detected_t < self.alarm_time:
#                             cv2.putText(frame_resized, 'Drowsiness Detected!', (50, 50), cv2.FONT_HERSHEY_SIMPLEX,
#                                         1.5, (0, 0, 255), 3)
#
#                         cv2.rectangle(frame_resized, (int(x1), int(y1)), (int(x2), int(y2)), color, 2)
#                         cv2.putText(frame_resized, f'{label}', (int(x1), int(y1) - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9,
#                                     color, 2)
#
#                 cv2.putText(frame_resized, f'FPS: {int(fps)}', (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1,
#                             (0, 255, 255), 2)
#
#                 cv2.imshow('Drowsiness Detection', frame_resized)
#                 if cv2.waitKey(1) & 0xFF == ord('q'):
#                     break
#         except KeyboardInterrupt:
#             pass
#         finally:
#             cap.release()
#             cv2.destroyAllWindows()
