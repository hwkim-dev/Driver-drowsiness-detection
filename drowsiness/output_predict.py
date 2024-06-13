import cv2
import torch
import numpy as np
from ultralytics import YOLO
import constant
import ipywidgets as widgets
import openvino as ov

class predict:
    def __init__(self, xml_path, device):
        self.xml_path = xml_path
        self.class_names = {0: 'Face', 1: 'Eye open', 2: 'Eye closed', 3: 'Eye open', 4: 'Eye closed', 5: 'Mouth'}
        self.CONFIDENCE_THRESHOLD = 0.5
        self.prev_frame_time = 0
        self.eye_closed_detect = 0
        self.model_path = None

        self.face_device = device

        if self.face_device == constant.CUDA:
            self.model_path = xml_path.find('face_detect_model_Path').find('cuda_model_Path').text
        else:
            self.model_path = xml_path.find('face_detect_model_Path').find('cpu_model_Path').text

        self.model = YOLO(self.model_path, task="detect")

    def run(self, running, show_event, new_frame_event, cropped_frame_np, smemory_results, smemory_face_detected):
        det_model = None
        if self.face_device == constant.CUDA:
            det_model = YOLO(
                self.xml_path.find('drowsy_detect_model_Path').find('cuda_model_Path').text,
                task="detect")
        elif self.face_device == constant.LOCAL:
            det_model = YOLO(self.xml_path.find('default_model_Path').find('face').text)
            det_model()
            det_model_path = constant.DET_MODEL_PATH

            core = ov.Core()

            device = widgets.Dropdown(
                options=core.available_devices + ["AUTO"],
                value="AUTO",
                description="Device:",
                disabled=False,
            )

            det_ov_model = core.read_model(det_model_path)
            ov_config = {}

            if device.value != "CPU":
                det_ov_model.reshape({0: [1, 3, constant.CROP_HEIGHT, constant.CROP_WIDTH]})

            if "GPU" in device.value or ("AUTO" in device.value and "GPU" in core.available_devices):
                ov_config = {"GPU_DISABLE_WINOGRAD_CONVOLUTION": "YES", "GPU_HOST_TASK_PRIORITY": "HIGH"}

            compiled_model = core.compile_model(det_ov_model, device.value, ov_config)
            def infer(*args):
                rs = compiled_model(args)
                return torch.from_numpy(rs[0])

            det_model.predictor.inference = infer
            det_model.predictor.model.pt = False

        cv2.ocl.setUseOpenCL(True)
        cv2.setUseOptimized(True)

        cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, constant.TARGET_WIDTH)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, constant.TARGET_HEIGHT)

        x_min, y_min, x_max, y_max = 0, 0, 0, 0

        while cap.isOpened():
            ret, frame_resized = cap.read()
            if not ret:
                break
            new_frame_event.set()
            if smemory_face_detected.value == constant.FALSE:
                face_detect_results = self.model(frame_resized, max_det=1, classes=(0,), device=self.face_device)
                for face_detect_result in face_detect_results:
                    if len(face_detect_result.boxes.xyxy) != 0 and len(face_detect_result.boxes.cls) != 0:

                        smemory_face_detected.value = constant.TRUE
                        x1, y1, x2, y2 = face_detect_result.boxes.xyxy[0].int().tolist()
                        center_x = int((x1 + x2) / 2)
                        center_y = int((y1 + y2) / 2)

                        x_min = center_x - constant.CROP_SIZE_HALF
                        y_min = center_y - constant.CROP_SIZE_HALF
                        x_max = x_min + constant.CROP_WIDTH
                        y_max = y_min + constant.CROP_HEIGHT

                        if x_max < constant.CROP_WIDTH or y_max < constant.CROP_HEIGHT:
                            smemory_face_detected.value = constant.FALSE
                        elif x_max > constant.TARGET_WIDTH or y_max > constant.TARGET_HEIGHT:
                            smemory_face_detected.value = constant.FALSE



            elif smemory_face_detected.value == constant.TRUE:
                arr = np.frombuffer(cropped_frame_np.buf, dtype=np.uint8).reshape(constant.input_shape)
                arr[:] = np.resize(frame_resized[y_min:y_max, x_min:x_max, :], (320, 320, 3))
                resized_frame_torch = torch.from_numpy(arr).permute(2, 0, 1).unsqueeze(0).float() / 255
                face_results = det_model(resized_frame_torch, max_det=4)

                for result in face_results:
                    # n(탐지클래스) x 6(박스/ conf/ 클래스) 배열(텐서)
                    res_np_arr = np.ndarray(buffer=smemory_results.buf, dtype=np.float16, shape=constant.result_shape)
                    result_boxes = result.boxes.data.numpy()
                    res_np_arr[:result_boxes.shape[0], :] = result_boxes
                show_event.set()
            if running.value == constant.NOT_RUNNING:
                break
        cap.release()
        cv2.destroyAllWindows()
