# Driver-drowsiness-detection
YOLOv8 Driver drowsiness detection Deep learning project Enhanced by algorithm based on Facial Features  
  
<br/>
<br/>
<br/>  
  
# purpose
Receive driver's eye status data using a YOLOv8 model. If the eyes are closed for 70% of frames within a 4.5-second window, trigger a sound alarm. If the eyes are open for 0.5 seconds, turn off the alarm and consider it not drowsy.  
  
<br/>
<br/>
<br/>  
  
# operating principle
In Main.py, create and run four multiprocesses via multiprocessing:
 * Drowsiness detection algorithm
 * FPS and time calculation algorithm
 * OpenCV and model inference algorithm
 * process infrenced result and show true imshow function
Control these processes through a GUI.  
  
<br/>
<br/>
<br/>  
  
# models
![nano_model](https://github.com/hwkim-dev/Driver-drowsiness-detection/assets/54717101/7af48e4e-a9e3-4050-8fc3-9ee490b7af33)  

![medium_model](https://github.com/hwkim-dev/Driver-drowsiness-detection/assets/54717101/bd75f424-570f-40b0-beb6-f6adc461f618)

<br/>
<br/>
<br/>
  
# data
|source|purpose|link|
|------|---|---|
|Aihub의 운전자 및 탑승자 상태 및 이상행동 모니터링 데이터|detect drowsy, awake|https://www.aihub.or.kr/aihubdata/data/view.do?currMenu=115&topMenu=100&aihubDataSe=data&dataSetSn=173|  
  
<br/>
<br/>
<br/>  
# ppt
will be added soon.  

<br/>
<br/>
<br/>  
  
# environment
1. windows *linux env not runnable winsoud is used [🔗](drowsiness/sound_play.py), which is win32api
2. numpy
3. opencv
4. ipywidgets
5. pytorch
6. openvino (in case you don't have cuda)
