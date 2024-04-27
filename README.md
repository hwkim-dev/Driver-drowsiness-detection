# Driver-drowsiness-detection
YOLOv8 Driver drowsiness detection Deep learning project Enhanced by algorithm based on Facial Features

# purpose
운전자의 졸음 여부를 모델을 통해 판단.

# 작동원리
1. yolo모델을 통한 졸음 여부 1차 식별.
2. 안면 특징을 통해 1차 식별 데이터의 확률과 합산 후 최종 졸음 확률 계산.
3. 최종 졸음 확률이 임계값을 넘을 경우 졸음으로 판단.

# flow-chart
![image](https://github.com/hwkim-dev/Driver-drowsiness-detection/assets/54717101/8492ddc2-2913-4c89-aed3-a2b55f3b06bb)


# 사용 데이터
|출처|목적|
|------|---|
|Aihub의 Face parsing 데이터|Facial Feature 감지|
|Aihub의 운전자 및 탑승자 상태 및 이상행동 모니터링 데이터|drowsy, awake 감지|
