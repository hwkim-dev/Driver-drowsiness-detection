import sound_play
import time
import numpy as np
import constant
import cv2


class detect_process:

    def __init__(self, sound_path):
        self.sound = sound_play.Sound(sound_path)

    def recur_time_calculator(self, fps, new_frame_event, eye_closed_cnt, eye_state, eye_state_timeline,
                              frame_cnt, smemory_face_detected):
        prev_frame_time = 0
        new_frame_time = 0
        copy_eye_state = 0
        past_time = time.perf_counter()
        while True:
            new_frame_event.wait()
            new_frame_time = time.perf_counter()
            fps.value = int(1 / (new_frame_time - prev_frame_time))
            prev_frame_time = new_frame_time

            if smemory_face_detected.value == constant.TRUE:
                if (time.perf_counter() - past_time) > 2:
                    past_time = time.perf_counter()
                    smemory_face_detected.value = constant.FALSE

            frame_cnt.value += 1

            # queue형식으로 눈 감은거 타임라인으로 저장해놓기
            copy_eye_state = eye_closed_cnt.value
            eye_state.value += copy_eye_state
            eye_state_timeline.value += copy_eye_state

            new_frame_event.clear()

    # 프로그램이 시작하고 4.5초가 지나면 계속 eye_state의 변수를 매 프레임마다 삭제
    # 변경하기 -> 매 프레임 마다 삭제하지 말고 2초분량의 데이터를 2초마다 삭제하기.

    # 4.5초분량의 변수 데이터
    # 2초마다 실행시켜서 졸음인지 판단
    # 2초만큼 제거
    # 최초 2초에는 어떻게?...

    #0.5초에 한번 실행해서 눈 뜨고있는지 -> 눈을 뜨고있는데 현재 졸음상태로 판단하면 즉각적으로 졸음 아니라고 해놓기
    #2초에 한번씩 실행해서 눈 감고 있는지 -> 눈 감고있으면 바로 졸음상태로...
    def eye_state_clock(self, smemory_eyeopen, new_frame_event, smemory_is_drowsy, eye_state, frame_cnt,
                        eye_state_timeline, smemory_face_detected):
        two_sec_clock = time.perf_counter()
        frame_cnt_0_5 = constant.INIT_VAL
        frame_cnt_2_0 = constant.INIT_VAL
        # 최초 시작은 4.5초가 지나면 실행시켜야함(데이터를 쌓고 반복해야함)
        while True:
            new_frame_event.wait()

            if (time.perf_counter() - two_sec_clock) > 4.5:
                break
            new_frame_event.clear()

        # 0.5초에 while_count가 1증가
        # 2초면 while_count가 4dla
        while_count = constant.INIT_VAL
        eye_state_timeline.value = constant.INIT_VAL
        while True:
            while_count += 1
            frame_cnt_0_5 = frame_cnt.value
            frame_cnt.value = constant.INIT_VAL
            frame_cnt_2_0 += frame_cnt_0_5
            # 0.5초마다 한번 실행
            if smemory_face_detected.value == constant.TRUE:
                self.is_Not_Drowsy(smemory_eyeopen, frame_cnt_0_5, smemory_is_drowsy)

            if while_count == 4:
                while_count = constant.INIT_VAL
                if smemory_face_detected.value == constant.TRUE:
                    self.is_Drowsy(eye_state, frame_cnt_2_0, smemory_is_drowsy)
                eye_state.value -= eye_state_timeline.value
                eye_state_timeline.value = constant.INIT_VAL
                frame_cnt_2_0 = constant.INIT_VAL
            time.sleep(0.5)

    def is_Not_Drowsy(self, smemory_eyeopen, frame_cnt_0_5, smemory_is_drowsy):
        if frame_cnt_0_5 != 0:
            if (smemory_eyeopen.value / frame_cnt_0_5) < constant.EYE_OPEN_RATE_FPS:
                smemory_is_drowsy.value = constant.FALSE
                self.awake()
            smemory_eyeopen.value = constant.INIT_VAL

    def is_Drowsy(self, eye_state, frame_cnt_2_0, smemory_is_drowsy):
        if frame_cnt_2_0 != 0:
            if (eye_state.value / frame_cnt_2_0) > constant.EYE_CLOSED_RATE_FPS:
                smemory_is_drowsy.value = constant.TRUE
                self.drowsy()

    def drowsy(self):
        if not self.sound.is_playing():
            self.sound.warn()

    def awake(self):
        if self.sound.is_playing():
            self.sound.warn_stop()

    def image_show(self, smemory_results, show_event, smemory_eyeclosed, smemory_eyeopen, cropped_frame_np,
                   smemory_is_drowsy, smemory_fps):
        class_names = {0: 'Face', 1: 'Eye open', 2: 'Eye closed', 3: 'Eye open', 4: 'Eye closed', 5: 'Mouth'}
        eye_closed_detect = 0
        show_event.wait()
        show_event.clear()

        while True:
            show_event.wait()
            np_crop = np.frombuffer(cropped_frame_np.buf, dtype=np.uint8).reshape(constant.input_shape).copy()
            result_copy = np.ndarray(buffer=smemory_results.buf, dtype=np.float16, shape=constant.result_shape).copy()
            for box in result_copy:
                x1, y1, x2, y2 = box[:4]
                x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)
                conf = box[4]
                cls = int(box[5])

                if conf < 0.3:
                    continue

                label = class_names.get(cls, 'Unknown')
                color = (255, 255, 255)

                if label == 'Eye closed':
                    eye_closed_detect += 0.5
                    color = (0, 0, 255)
                elif label == 'Eye open':
                    smemory_eyeopen.value -= 0.5
                    color = (0, 255, 0)

                cv2.rectangle(np_crop, (x1, y1), (x2, y2), color, 2)
                cv2.putText(np_crop, f'{label}', (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9,
                            color, 2)

            smemory_eyeclosed.value = eye_closed_detect
            eye_closed_detect = 0

            if smemory_is_drowsy.value == constant.TRUE:
                cv2.putText(np_crop, 'Drowsiness!', (50, 50), cv2.FONT_HERSHEY_SIMPLEX,
                            1.1, (0, 0, 255), 3)
            cv2.putText(np_crop, f'FPS: {smemory_fps.value}', (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1,
                        (0, 255, 255), 2)
            cv2.imshow('Drowsiness Detection', np_crop)
            cv2.waitKey(1)
            show_event.clear()
