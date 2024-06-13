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

# optimization & performance  
![performance](https://github.com/hwkim-dev/Driver-drowsiness-detection/assets/54717101/674875ea-35a4-49a9-98e1-499000b9df55)  

<br/>
<br/>
<br/>
  
# data
|source|purpose|link|
|------|---|---|
|Driver and Passenger State and Anomaly Behavior Monitoring Data from Aihub|detect face eye mouth|https://www.aihub.or.kr/aihubdata/data/view.do?currMenu=115&topMenu=100&aihubDataSe=data&dataSetSn=173|  
  
<br/>
<br/>
<br/>  

# ppt  

google drive link: [🔗](https://docs.google.com/presentation/d/1pbqiPMLQGaspg0C_ryWQmM1hd6Aktyi-/edit?usp=sharing&ouid=104335523960644232607&rtpof=true&sd=true)  

<h3>Presentation Format and Compatibility</h3>

* **Microsoft PowerPoint Format:** This presentation was created in Microsoft PowerPoint for optimal viewing.
* **Potential Animation Issues:** Please be aware that certain animations may not function properly when using other presentation software.
* **Recommendation:** For the best viewing experience, it is recommended to use Microsoft PowerPoint to open and present this file.

<br/>
<br/>
<br/>  
  
# environment
1. windows *linux env not runnable winsoud is used [🔗](drowsiness/sound_play.py), which is win32api
2. numpy
3. opencv
4. ipywidgets
5. pytorch
6. openvino (in case cuda unavailable)
