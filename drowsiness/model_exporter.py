# export model -> from pt to onnx & openvino & cuda(engine)
import os
import xml
from ultralytics import YOLO
import constant
import shutil
class exporter():
    def __init__(self, model_path, device):
        base_path = os.path.dirname(os.path.abspath(__file__)) + "\\"
        face_pt_path = base_path + model_path.find('default_model_Path').find('face').text.strip()
        drowsy_pt_path = base_path + model_path.find('default_model_Path').find('drowsy').text.strip()
        if device == 'cuda':
            cuda_face_model_full_path = base_path + model_path.find('face_detect_model_Path').find('cuda_model_Path').text.strip()
            cuda_detection_model_full_path = base_path + model_path.find('drowsy_detect_model_Path').find('cuda_model_Path').text.strip()

            if not os.path.exists(cuda_face_model_full_path):
                face_model_out_path = YOLO(face_pt_path, task="detect").export(format='engine', imgsz=(constant.TARGET_HEIGHT, constant.TARGET_WIDTH))
                cuda_face_path_parts = os.path.dirname(cuda_face_model_full_path)
                os.mkdir(cuda_face_path_parts)
                shutil.move(face_model_out_path, cuda_face_path_parts)

            if not os.path.exists(cuda_detection_model_full_path):
                detec_model_out_path = YOLO(drowsy_pt_path, task="detect").export(format='engine', imgsz=(constant.CROP_HEIGHT, constant.CROP_WIDTH))
                cuda_dt_path_parts = os.path.dirname(cuda_detection_model_full_path)
                os.mkdir(cuda_dt_path_parts)
                shutil.move(detec_model_out_path, cuda_dt_path_parts)
        else:
            onnx_full_path = base_path + model_path.find('face_detect_model_Path').find('cpu_model_Path').text.strip()
            ov_detection_model_full_path = base_path + model_path.find('drowsy_detect_model_Path').find('openvino_model_Path').text.strip()

            if not os.path.exists(onnx_full_path):
                onnx_f_out_path = YOLO(face_pt_path, task="detect").export(format='onnx', half=True, imgsz=(constant.TARGET_HEIGHT, constant.TARGET_WIDTH))
                onnx_face_path_parts = os.path.dirname(onnx_full_path)
                os.mkdir(onnx_face_path_parts)
                shutil.move(onnx_f_out_path, onnx_face_path_parts)
                test_ = YOLO(onnx_full_path)
                test_()

            if not os.path.exists(ov_detection_model_full_path):
                ov_d_out_path = YOLO(drowsy_pt_path, task="detect").export(format='openvino', dynamic=False, half=True,  imgsz=(constant.CROP_HEIGHT, constant.CROP_WIDTH))
                ov_dt_path_parts = os.path.dirname(os.path.dirname(ov_detection_model_full_path))
                os.mkdir(ov_dt_path_parts)
                shutil.move(ov_d_out_path, ov_dt_path_parts)


