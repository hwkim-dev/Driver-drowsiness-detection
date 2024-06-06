# Driver-drowsiness-detection
YOLOv8 Driver drowsiness detection Deep learning project Enhanced by algorithm based on Facial Features

# purpose
Receive driver's eye status data using a YOLOv8 model. If the eyes are closed for 70% of frames within a 4.5-second window, trigger a sound alarm. If the eyes are open for 0.5 seconds, turn off the alarm and consider it not drowsy.


# operating principle
In Main.py, create and run three multiprocesses via multiprocessing:
 * Drowsiness detection algorithm
 * FPS and time calculation algorithm
 * OpenCV and model inference algorithm
Control these processes through a GUI.


# flow-chart
deprecated


# data
|출처|목적|
|------|---|
|Aihub의 운전자 및 탑승자 상태 및 이상행동 모니터링 데이터|drowsy, awake 감지|

# environment
windows