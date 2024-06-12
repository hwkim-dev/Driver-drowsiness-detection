FALSE = 0
TRUE = 1
EYE_CLOSED_RATE_FPS = 0.6
EYE_OPEN_RATE_FPS = -0.5
INIT_VAL = 0
DROWSINESS_CHECK_INTERVAL = 2
RUNNING = 0
NOT_RUNNING = 1

CONF_DROWSY_DETECT = 0.4

#sound play length(second)
SOUND_PLAY_SEC = 36


#for shared_memoru_size
input_shape = (320, 320, 3)
result_shape = (4,6)

#camera setting
TARGET_WIDTH = 640
TARGET_HEIGHT = 640

#device_name
CUDA = 'cuda'
LOCAL = 'cpu'
#crop setting
#320 x 320
CROP_SIZE_HALF = 160
MINIMUM_CROP_SIZE = 102400
CROP_WIDTH = 320
CROP_HEIGHT = 320

DET_MODEL_PATH = r"models/openVINO_model/v8m_drowsy_detect_model_openvino_model/v8m_drowsy_detect_model.xml"