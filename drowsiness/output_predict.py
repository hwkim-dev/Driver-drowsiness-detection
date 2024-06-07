# # import cv2
# # import torch
# # import numpy as np
# # from ultralytics import YOLO
# # import time
# # import collections
# # import constant
# #
# #
# # class predict:
# #     def __init__(self, modelpath):
# #         self.class_names = {0: 'Face', 1: 'Eye open', 2: 'Eye closed', 3: 'Eye open', 4: 'Eye closed', 5: 'Mouth'}
# #         self.CONFIDENCE_THRESHOLD = 0.5
# #         self.prev_frame_time = 0
# #         self.eye_closed_detect = 0
# #         self.model_path = None
# #
# #         #r"models/cpu_model/best(9).onnx"
# #         device = None
# #         if torch.cuda.is_available():
# #             device = 'cuda'
# #             self.model_path = modelpath.find('cuda_model_Path').text
# #         else:
# #             device = 'cpu'
# #             self.model_path = modelpath.find('cpu_model_Path').text
# #
# #         self.model = YOLO(self.model_path, task="detect")
# #
# #     def run(self, running, smemory_fps, new_frame_event, smemory_eyeclosed, smemory_eyeopen, smemory_is_drowsy):
# #         cv2.ocl.setUseOpenCL(True)
# #         cv2.setUseOptimized(True)
# #         cap = cv2.VideoCapture(0)
# #         TARGET_WIDTH = 640
# #         TARGET_HEIGHT = 480
# #         # cap.set(cv2.CAP_PROP_FPS, 30)
# #         cap.set(cv2.CAP_PROP_FRAME_WIDTH, TARGET_WIDTH)
# #         cap.set(cv2.CAP_PROP_FRAME_HEIGHT, TARGET_HEIGHT)
# #
# #         while cap.isOpened():
# #             ret, frame_resized = cap.read()
# #             if not ret:
# #                 break
# #             # frame_resized = cv2.resize(frame_resized, (128, 128))
# #
# #             results = self.model(frame_resized)
# #
# #             new_frame_event.set()
# #
# #             for result in results:
# #                 for box in result.boxes:
# #                     x1, y1, x2, y2 = box.xyxy[0].int().tolist()
# #                     conf = box.conf[0]
# #                     cls = int(box.cls[0])
# #
# #                     if conf < self.CONFIDENCE_THRESHOLD:
# #                         continue
# #
# #                     label = self.class_names.get(cls, 'Unknown')
# #                     color = (255, 255, 255)
# #
# #                     if label == 'Eye closed':
# #                         self.eye_closed_detect += 0.5
# #                         color = (0, 0, 255)
# #                     elif label == 'Eye open':
# #                         smemory_eyeopen.value -= 0.5
# #                         color = (0, 255, 0)
# #
# #                     cv2.rectangle(frame_resized, (x1, y1), (x2, y2), color, 2)
# #                     cv2.putText(frame_resized, f'{label}', (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9,
# #                                 color, 2)
# #
# #             smemory_eyeclosed.value = self.eye_closed_detect
# #             self.eye_closed_detect = 0
# #
# #             if smemory_is_drowsy.value == constant.TRUE:
# #                 cv2.putText(frame_resized, 'Drowsiness Detected!', (50, 50), cv2.FONT_HERSHEY_SIMPLEX,
# #                             1.5, (0, 0, 255), 3)
# #             cv2.putText(frame_resized, f'FPS: {smemory_fps.value}', (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1,
# #                         (0, 255, 255), 2)
# #
# #             cv2.imshow('Drowsiness Detection', frame_resized)
# #
# #             cv2.waitKey(1)
# #
# #             if running.value == 0:
# #                 break
# #         cap.release()
# #         cv2.destroyAllWindows()
# import cv2
# import torch
# import numpy as np
# from ultralytics import YOLO
# import time
# import collections
# import constant
# import ipywidgets as widgets
# import openvino as ov
# import torchvision
# from openvino.preprocess import ResizeAlgorithm
#
#
# class predict:
#     def __init__(self, modelpath):
#         self.class_names = {0: 'Face', 1: 'Eye open', 2: 'Eye closed', 3: 'Eye open', 4: 'Eye closed', 5: 'Mouth'}
#         self.CONFIDENCE_THRESHOLD = 0.5
#         self.prev_frame_time = 0
#         self.eye_closed_detect = 0
#         self.model_path = None
#
#         #r"models/cpu_model/best(9).onnx"
#         device = None
#         if torch.cuda.is_available():
#             device = 'cuda'
#             self.model_path = modelpath.find('cuda_model_Path').text
#         else:
#             device = 'cpu'
#             self.model_path = modelpath.find('cpu_model_Path').text
#
#         self.model = YOLO(self.model_path, task="detect")
#
#     def run(self, running, smemory_fps, new_frame_event, smemory_eyeclosed, smemory_eyeopen, smemory_is_drowsy):
#         det_model = YOLO(r"C:\D\github\Driver-drowsiness-detection\drowsiness\models\pt_model\v8n_facedetect_model.pt")
#
#         det_model()
#         det_model_path = r"C:\D\DL_proj\rngus\models\cuda_model\v8m_facedetect_model_openvino_model\v8m_facedetect_model.xml"
#
#         core = ov.Core()
#
#         device = widgets.Dropdown(
#             options=core.available_devices + ["AUTO"],
#             value="AUTO",
#             description="Device:",
#             disabled=False,
#         )
#
#         source = 0
#
#         det_ov_model = core.read_model(det_model_path)
#         ov_config = {}
#         crop_width = 320
#         crop_height = 320
#         if device.value != "CPU":
#             det_ov_model.reshape({0: [1, 3, crop_height, crop_width]})
#
#         if "GPU" in device.value or ("AUTO" in device.value and "GPU" in core.available_devices):
#             ov_config = {"GPU_DISABLE_WINOGRAD_CONVOLUTION": "YES", "GPU_HOST_TASK_PRIORITY": "HIGH"}
#
#         compiled_model = core.compile_model(det_ov_model, device.value, ov_config)
#
#         def infer(*args):
#             rs = compiled_model(args)
#             return torch.from_numpy(rs[0])
#
#
#         from openvino.preprocess import PrePostProcessor
#
#         cv2.ocl.setUseOpenCL(True)
#         cv2.setUseOptimized(True)
#         det_model.predictor.inference = infer
#         det_model.predictor.model.pt = False
#
#
#         cap = cv2.VideoCapture(0)
#         TARGET_WIDTH = 640
#         TARGET_HEIGHT = 480
#         trch_resize = torchvision.transforms.Resize((320, 320))
#         cap.set(cv2.CAP_PROP_FRAME_WIDTH, TARGET_WIDTH)
#         cap.set(cv2.CAP_PROP_FRAME_HEIGHT, TARGET_HEIGHT)
#
#         x_min, y_min, x_max, y_max = 0, 0, 0, 0
#
#         past_time = time.perf_counter()
#         face_detected = False
#         while cap.isOpened():
#             ret, frame_resized = cap.read()
#             if not ret:
#                 break
#
#             if (time.perf_counter() - past_time) > 5:
#                 past_time = time.perf_counter()
#                 face_detected = False
#
#             new_frame_event.set()
#             if face_detected == False:
#
#                 results = self.model(frame_resized, max_det=1, classes=(0,))
#                 for result in results:
#                     if (len(result.boxes.xyxy) != 0 and len(result.boxes.cls) != 0):
#                         face_boxes = result.boxes.xyxy[0].tolist()
#
#                         if len(face_boxes) > 0:
#                             face_detected = True
#                             x1, y1, x2, y2 = face_boxes
#
#                             center_x = int((x1 + x2) / 2)
#                             center_y = int((y1 + y2) / 2)
#
#                             x_min = max(0, center_x - crop_width // 2)
#                             y_min = max(0, center_y - crop_height // 2)
#                             x_max = min(frame_resized.shape[1], center_x + crop_width // 2)
#                             y_max = min(frame_resized.shape[0], center_y + crop_height // 2)
#
#             elif face_detected == True:
#                 cropped_frame_np = frame_resized[y_min:y_max, x_min:x_max, :]
#                 resize_transform = trch_resize(
#                     torch.from_numpy(cropped_frame_np).permute(2, 0, 1).unsqueeze(0).float())
#
#                 results = det_model(resize_transform)
#
#                 for result in results:
#                     for box in result.boxes:
#                         x1, y1, x2, y2 = box.xyxy[0].int().tolist()
#                         conf = box.conf[0]
#                         cls = int(box.cls[0])
#
#                         if conf < self.CONFIDENCE_THRESHOLD:
#                             continue
#
#                         label = self.class_names.get(cls, 'Unknown')
#                         color = (255, 255, 255)
#
#                         if label == 'Eye closed':
#                             self.eye_closed_detect += 0.5
#                             color = (0, 0, 255)
#                         elif label == 'Eye open':
#                             smemory_eyeopen.value -= 0.5
#                             color = (0, 255, 0)
#
#                         cv2.rectangle(cropped_frame_np, (x1, y1), (x2, y2), color, 2)
#                         cv2.putText(cropped_frame_np, f'{label}', (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9,
#                                     color, 2)
#
#                 smemory_eyeclosed.value = self.eye_closed_detect
#                 print(self.eye_closed_detect)
#                 self.eye_closed_detect = 0
#
#                 if smemory_is_drowsy.value == constant.TRUE:
#                     cv2.putText(cropped_frame_np, 'Drowsiness Detected!', (50, 50), cv2.FONT_HERSHEY_SIMPLEX,
#                                 1.5, (0, 0, 255), 3)
#                 cv2.putText(cropped_frame_np, f'FPS: {smemory_fps.value}', (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1,
#                             (0, 255, 255), 2)
#                 cv2.imshow('Drowsiness Detection', cropped_frame_np)
#
#             cv2.waitKey(1)
#
#             if running.value == constant.NOT_RUNNING:
#                 break
#         cap.release()
#         cv2.destroyAllWindows()
# import cv2
# import torch
# import numpy as np
# from ultralytics import YOLO
# import time
# import collections
# import constant
#
#
# class predict:
#     def __init__(self, modelpath):
#         self.class_names = {0: 'Face', 1: 'Eye open', 2: 'Eye closed', 3: 'Eye open', 4: 'Eye closed', 5: 'Mouth'}
#         self.CONFIDENCE_THRESHOLD = 0.5
#         self.prev_frame_time = 0
#         self.eye_closed_detect = 0
#         self.model_path = None
#
#         #r"models/cpu_model/best(9).onnx"
#         device = None
#         if torch.cuda.is_available():
#             device = 'cuda'
#             self.model_path = modelpath.find('cuda_model_Path').text
#         else:
#             device = 'cpu'
#             self.model_path = modelpath.find('cpu_model_Path').text
#
#         self.model = YOLO(self.model_path, task="detect")
#
#     def run(self, running, smemory_fps, new_frame_event, smemory_eyeclosed, smemory_eyeopen, smemory_is_drowsy):
#         cv2.ocl.setUseOpenCL(True)
#         cv2.setUseOptimized(True)
#         cap = cv2.VideoCapture(0)
#         TARGET_WIDTH = 640
#         TARGET_HEIGHT = 480
#         # cap.set(cv2.CAP_PROP_FPS, 30)
#         cap.set(cv2.CAP_PROP_FRAME_WIDTH, TARGET_WIDTH)
#         cap.set(cv2.CAP_PROP_FRAME_HEIGHT, TARGET_HEIGHT)
#
#         while cap.isOpened():
#             ret, frame_resized = cap.read()
#             if not ret:
#                 break
#             # frame_resized = cv2.resize(frame_resized, (128, 128))
#
#             results = self.model(frame_resized)
#
#             new_frame_event.set()
#
#             for result in results:
#                 for box in result.boxes:
#                     x1, y1, x2, y2 = box.xyxy[0].int().tolist()
#                     conf = box.conf[0]
#                     cls = int(box.cls[0])
#
#                     if conf < self.CONFIDENCE_THRESHOLD:
#                         continue
#
#                     label = self.class_names.get(cls, 'Unknown')
#                     color = (255, 255, 255)
#
#                     if label == 'Eye closed':
#                         self.eye_closed_detect += 0.5
#                         color = (0, 0, 255)
#                     elif label == 'Eye open':
#                         smemory_eyeopen.value -= 0.5
#                         color = (0, 255, 0)
#
#                     cv2.rectangle(frame_resized, (x1, y1), (x2, y2), color, 2)
#                     cv2.putText(frame_resized, f'{label}', (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9,
#                                 color, 2)
#
#             smemory_eyeclosed.value = self.eye_closed_detect
#             self.eye_closed_detect = 0
#
#             if smemory_is_drowsy.value == constant.TRUE:
#                 cv2.putText(frame_resized, 'Drowsiness Detected!', (50, 50), cv2.FONT_HERSHEY_SIMPLEX,
#                             1.5, (0, 0, 255), 3)
#             cv2.putText(frame_resized, f'FPS: {smemory_fps.value}', (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1,
#                         (0, 255, 255), 2)
#
#             cv2.imshow('Drowsiness Detection', frame_resized)
#
#             cv2.waitKey(1)
#
#             if running.value == 0:
#                 break
#         cap.release()
#         cv2.destroyAllWindows()
import sys

import cv2
import torch
import numpy as np
from ultralytics import YOLO
import time
import collections
import constant
import ipywidgets as widgets
import openvino as ov
import torchvision
from openvino.preprocess import ResizeAlgorithm


class predict:
    def __init__(self, modelpath):
        self.class_names = {0: 'Face', 1: 'Eye open', 2: 'Eye closed', 3: 'Eye open', 4: 'Eye closed', 5: 'Mouth'}
        self.CONFIDENCE_THRESHOLD = 0.5
        self.prev_frame_time = 0
        self.eye_closed_detect = 0
        self.model_path = None

        #r"models/cpu_model/best(9).onnx"
        device = None
        if torch.cuda.is_available():
            device = 'cuda'
            self.model_path = modelpath.find('cuda_model_Path').text
        else:
            device = 'cpu'
            self.model_path = modelpath.find('cpu_model_Path').text

        self.model = YOLO(self.model_path, task="detect")

    def run(self, running, show_event, new_frame_event, cropped_frame_np, smemory_results, rectangle_size):
        det_model = YOLO(r"C:\D\github\Driver-drowsiness-detection\drowsiness\models\pt_model\v8m_facedetect_model.pt")

        det_model()
        det_model_path = r"C:\D\DL_proj\rngus\models\cuda_model\v8m_facedetect_model_openvino_model\v8m_facedetect_model.xml"

        core = ov.Core()

        device = widgets.Dropdown(
            options=core.available_devices + ["AUTO"],
            value="AUTO",
            description="Device:",
            disabled=False,
        )

        source = 0

        det_ov_model = core.read_model(det_model_path)
        ov_config = {}

        if device.value != "CPU":
            det_ov_model.reshape({0: [1, 3, constant.crop_height, constant.crop_width]})

        if "GPU" in device.value or ("AUTO" in device.value and "GPU" in core.available_devices):
            ov_config = {"GPU_DISABLE_WINOGRAD_CONVOLUTION": "YES", "GPU_HOST_TASK_PRIORITY": "HIGH"}

        compiled_model = core.compile_model(det_ov_model, device.value, ov_config)

        def infer(*args):
            rs = compiled_model(args)
            return torch.from_numpy(rs[0])

        from openvino.preprocess import PrePostProcessor

        cv2.ocl.setUseOpenCL(True)
        cv2.setUseOptimized(True)
        det_model.predictor.inference = infer
        det_model.predictor.model.pt = False

        cap = cv2.VideoCapture(0)

        trch_resize = torchvision.transforms.Resize((constant.crop_width, constant.crop_height))

        cap.set(cv2.CAP_PROP_FRAME_WIDTH, constant.TARGET_WIDTH)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, constant.TARGET_HEIGHT)

        x_min, y_min, x_max, y_max = 0, 0, 0, 0

        past_time = time.perf_counter()
        face_detected = False
        while cap.isOpened():
            ret, frame_resized = cap.read()
            if not ret:
                break

            if (time.perf_counter() - past_time) > 5:
                past_time = time.perf_counter()
                face_detected = False

            new_frame_event.set()
            if not face_detected:

                face_detect_results = self.model(frame_resized, max_det=1, classes=(0,))
                for face_detect_result in face_detect_results:
                    if len(face_detect_result.boxes.xyxy) != 0 and len(face_detect_result.boxes.cls) != 0:
                        face_boxes = face_detect_result.boxes.xyxy[0].int().tolist()
                        if len(face_boxes) > 0:
                            face_detected = True
                            x1, y1, x2, y2 = face_boxes

                            center_x = int((x1 + x2) / 2)
                            center_y = int((y1 + y2) / 2)

                            x_min = max(0, center_x - constant.crop_width // 2)
                            y_min = max(0, center_y - constant.crop_height // 2)
                            x_max = min(frame_resized.shape[1], center_x + constant.crop_width // 2)
                            y_max = min(frame_resized.shape[0], center_y + constant.crop_height // 2)
                            rectangle_size[0] = x_min
                            rectangle_size[1] = y_min
                            rectangle_size[2] = x_max
                            rectangle_size[3] = y_max


            elif face_detected == True:

                arr = np.frombuffer(cropped_frame_np.buf, dtype=np.uint8).reshape(constant.input_shape)
                arr[:] = frame_resized[y_min:y_max, x_min:x_max, :]

                resize_transform = trch_resize(
                    torch.from_numpy(arr).permute(2, 0, 1).unsqueeze(0).float() / 255)

                k = det_model(resize_transform, max_det=4)

                for result in k:
                    # n(탐지클래스) x 6(박스, conf, 클래스) 배열(텐서)
                    res_np_arr = np.ndarray(buffer=smemory_results.buf, dtype=np.float16, shape=constant.result_shape)
                    result_boxes = result.boxes.data.numpy()
                    res_np_arr[:result_boxes.shape[0], :] = result_boxes
                show_event.set()
            if running.value == constant.NOT_RUNNING:
                break
        cap.release()
        cv2.destroyAllWindows()
