import cv2
import torch
import numpy as np
from ultralytics import YOLO
import time
import collections
import constant

class predict:
    def __init__(self):
        self.class_names = {0: 'Face', 1: 'Eye open', 2: 'Eye closed', 3: 'Eye open', 4: 'Eye closed', 5: 'Mouth'}
        self.CONFIDENCE_THRESHOLD = 0.3
        self.prev_frame_time = 0
        self.eye_closed_detect = 0

    def run(self, running, smemory_fps, new_frame_event, smemory_eyeclosed, smemory_eyeopen, smemory_is_drowsy):
        model_path = r"models/cpu_model/best(9).onnx"
        cv2.ocl.setUseOpenCL(True)
        cap = cv2.VideoCapture(0)
        TARGET_WIDTH = 640
        TARGET_HEIGHT = 480
        # cap.set(cv2.CAP_PROP_FPS, 30)
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, TARGET_WIDTH)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, TARGET_HEIGHT)

        if torch.cuda.is_available():
            device = 'cuda'
        else:
            device = 'cpu'
        model = YOLO(model_path, task="detect")
        try:
            while cap.isOpened():
                ret, frame_resized = cap.read()
                if not ret:
                    break

                with torch.no_grad():
                    results = model(frame_resized)

                #멀티프로세스환경에서누time.time() 이 안먹힘
                # frame_time.value = time.perf_counter()
                new_frame_event.set()

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
                            self.eye_closed_detect += 0.5
                            color = (0, 0, 255)
                        elif label == 'Eye open':
                            smemory_eyeopen.value -= 0.5
                            color = (0, 255, 0)

                        cv2.rectangle(frame_resized, (int(x1), int(y1)), (int(x2), int(y2)), color, 2)
                        cv2.putText(frame_resized, f'{label}', (int(x1), int(y1) - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9,
                                    color, 2)

                smemory_eyeclosed.value = self.eye_closed_detect
                self.eye_closed_detect = 0

                if smemory_is_drowsy.value == constant.TRUE:
                    cv2.putText(frame_resized, 'Drowsiness Detected!', (50, 50), cv2.FONT_HERSHEY_SIMPLEX,
                                1.5, (0, 0, 255), 3)
                cv2.putText(frame_resized, f'FPS: {int(smemory_fps.value)}', (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1,
                            (0, 255, 255), 2)

                cv2.imshow('Drowsiness Detection', frame_resized)

                cv2.waitKey(1)

                if running.value == 0:
                    break
        except KeyboardInterrupt:
            pass
        finally:
            cap.release()
            cv2.destroyAllWindows()