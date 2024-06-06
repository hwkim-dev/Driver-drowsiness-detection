import threading
import sound_play
import time
import sched
import sys
import numpy as np
import constant

class detect_process:

    def __init__(self, sound_path):
        self.eye_closed_start_time = None
        self.sound = sound_play.Sound(sound_path)
        # self.prev_frame_time = 0
        # self.new_frame_time = 0

        self.eye_state_timeline = list()
        #self.total_eye_closed_cnt = 0
        self.start_time = 0

    def recur_time_calculator(self, smemory_fps, new_frame_event, eye_closed_cnt, eye_state, eye_state_timeline, frame_cnt):
        prev_frame_time = 0
        new_frame_time = 0
        copy_eye_state = 0
        while True:
            new_frame_event.wait()
            new_frame_time = time.perf_counter()
            smemory_fps.value = int(1 / (new_frame_time - prev_frame_time))
            prev_frame_time = new_frame_time

            frame_cnt.value += 1

            # queue형식으로 눈 감은거 타임라인으로 저장해놓기
            copy_eye_state = eye_closed_cnt.value
            eye_state.value += copy_eye_state
            eye_state_timeline.value += copy_eye_state

            new_frame_event.clear()
            
    
    # 여기서 5초에 한번 실행시키고 이벤트 셋으로 밑에 함수 불러서 0.5초마다 fps개선하기
    def recur_time_calculator(self, smemory_fps, new_frame_event, eye_closed_cnt, eye_state, eye_state_timeline, frame_cnt):
        prev_frame_time = 0
        new_frame_time = 0
        copy_eye_state = 0

        while True:
            new_frame_event.wait()

            new_frame_time = time.perf_counter()
            smemory_fps.value = int(1 / (new_frame_time - prev_frame_time))
            prev_frame_time = new_frame_time

            frame_cnt.value += 1

            # queue형식으로 눈 감은거 타임라인으로 저장해놓기
            copy_eye_state = eye_closed_cnt.value
            eye_state.value += copy_eye_state
            eye_state_timeline.value += copy_eye_state
            new_frame_event.clear()

    #eye_state_timeline을 배열로 만들고 pointer를 만들어서 사용하기

    #0.5초 단위로 queue에 쌓인 eye 상태를 전부 저장 시켜놈, 4.5초만큼 쌓이면




    # 프로그램이 시작하고 4.5초가 지나면 계속 eye_state의 변수를 매 프레임마다 삭제
    # 변경하기 -> 매 프레임 마다 삭제하지 말고 2초분량의 데이터를 2초마다 삭제하기.

    # 4.5초분량의 변수 데이터
    # 2초마다 실행시켜서 졸음인지 판단
    # 2초만큼 제거
    # 최초 2초에는 어떻게?...

    #0.5초에 한번 실행해서 눈 뜨고있는지 -> 눈을 뜨고있는데 현재 졸음상태로 판단하면 즉각적으로 졸음 아니라고 해놓기
    #2초에 한번씩 실행해서 눈 감고 있는지 -> 눈 감고있으면 바로 졸음상태로...
    def eye_state_clock(self,smemory_eyeopen, new_frame_event, smemory_is_drowsy, eye_state, frame_cnt, eye_state_timeline):
        two_sec_clock = time.perf_counter()
        frame_cnt_0_5 = constant.INIT_VAL
        frame_cnt_2_0 = constant.INIT_VAL
        # 최초 시작은 4.5초가 지나면 실행시켜야함(데이터를 쌓고 반복해야함)
        while True:
            new_frame_event.wait()

            if(time.perf_counter() - two_sec_clock) > 4.5:
                break
            new_frame_event.clear()
        
        #0.5초에 while_count가 1증가
        while_count = constant.INIT_VAL
        eye_state_timeline.value = constant.INIT_VAL
        while True:
            while_count += 1
            frame_cnt_0_5 = frame_cnt.value
            frame_cnt.value = constant.INIT_VAL
            frame_cnt_2_0 += frame_cnt_0_5
            #0.5초마다 한번 실행
            self.is_Not_Drowsy(smemory_eyeopen, frame_cnt_0_5, smemory_is_drowsy)

            #2초에 한번 실행
            if while_count == 4:
                while_count = constant.INIT_VAL
                self.is_Drowsy(eye_state, frame_cnt_2_0, smemory_is_drowsy)
                eye_state.value -= eye_state_timeline.value
                eye_state_timeline.value = constant.INIT_VAL
                frame_cnt_2_0 = constant.INIT_VAL
            time.sleep(0.5)

    def is_Not_Drowsy(self, smemory_eyeopen, frame_cnt_0_5, smemory_is_drowsy):
        if frame_cnt_0_5 != 0:
            if (smemory_eyeopen.value / frame_cnt_0_5) < constant.EYE_OPEN_RATE_FPS:
                # 눈 뜨고있다면?
                smemory_is_drowsy.value = constant.FALSE
                self.awake()
            smemory_eyeopen.value = constant.INIT_VAL

    def is_Drowsy(self, eye_state, frame_cnt_2_0, smemory_is_drowsy):
        if frame_cnt_2_0 != 0:
            if (eye_state.value / frame_cnt_2_0) > constant.EYE_CLOSED_RATE_FPS:
                # 졸음이면
                smemory_is_drowsy.value = constant.TRUE
                self.drowsy()

    def drowsy(self):
        if not self.sound.is_playing():
            self.sound.warn()

    def awake(self):
        if self.sound.is_playing():
            self.sound.warn_stop()