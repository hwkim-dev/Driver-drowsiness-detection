FALSE = 0
TRUE = 1
EYE_CLOSED_RATE_FPS = 0.5
EYE_OPEN_RATE_FPS = -0.9
INIT_VAL = 0
DROWSINESS_CHECK_INTERVAL = 2
RUNNING = 0
NOT_RUNNING = 1

#for shared_memoru_size
input_shape = (320, 320, 3)
result_shape = (4,6)

#camera setting
TARGET_WIDTH = 1280
TARGET_HEIGHT = 720

#crop setting
crop_width = 320
crop_height = 320

DET_MODEL_PATH = r"models/openVINO_model/v8m_drowsy_detect_model_openvino_model/v8m_drowsy_detect_model.xml"