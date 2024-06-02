import threading
import sound_play
import time
import sched
import sys
import numpy as np

EYE_CLOSED_RATE_FPS = 0.6
EYE_OPEN_RATE_FPS = -0.9
class detect_process:

    def __init__(self):
        self.eye_closed_start_time = None
        self.sound = sound_play.Sound()
        # self.prev_frame_time = 0
        # self.new_frame_time = 0

        self.eye_state_timeline = list()
        #self.total_eye_closed_cnt = 0
        self.start_time = 0

    def recur_time_calculator(self, frame_time, smemory_fps, smemory_event, smemory_eyeclosed, eye_state, fps_per_four_p_five_sec, eye_state_timeline, fps_per_p_five_sec):
        prev_frame_time = 0
        new_frame_time = 0
        while True:
            smemory_event.wait()
            fps_per_four_p_five_sec.value += 1
            fps_per_p_five_sec.value += 1
            new_frame_time = frame_time.value
            test = new_frame_time - prev_frame_time
            smemory_fps.value = (1 / (test))
            prev_frame_time = new_frame_time

            # queue형식으로 눈 감은거 타임라인으로 저장해놓기
            copy_eye_state = smemory_eyeclosed.value
            eye_state.value += copy_eye_state
            eye_state_timeline.value += copy_eye_state

            smemory_event.clear()


    #0.5초 단위로 queue에 쌓인 eye 상태를 전부 저장 시켜놈, 4.5초만큼 쌓이면




    # 프로그램이 시작하고 4.5초가 지나면 계속 eye_state의 변수를 매 프레임마다 삭제
    # 변경하기 -> 매 프레임 마다 삭제하지 말고 2초분량의 데이터를 2초마다 삭제하기.

    # 4.5초분량의 변수 데이터
    # 2초마다 실행시켜서 졸음인지 판단
    # 2초만큼 제거
    # 최초 2초에는 어떻게?...

    #0.5초에 한번 실행해서 눈 뜨고있는지 -> 눈을 뜨고있는데 현재 졸음상태로 판단하면 즉각적으로 졸음 아니라고 해놓기
    #2초에 한번씩 실행해서 눈 감고 있는지 -> 눈 감고있으면 바로 졸음상태로...
    def eye_state_clock(self,smemory_eyeopen, smemory_event, smemory_is_drowsy, eye_state, fps_per_four_p_five_sec, fps_per_p_five_sec, eye_state_timeline):
        begin_time = time.perf_counter()
        two_sec_clock = 0

        # 최초 시작은 4.5초가 지나면 실행시켜야함(데이터를 쌓고 반복해야함)
        while True:
            smemory_event.wait()
            if(time.perf_counter() - begin_time) > 4.5:
                break
            smemory_event.clear()

        begin_time = time.perf_counter()
        
        #0.5초에 while_count가 1증가
        while_count = 0
        while True:
            while_count += 1
            
            #0.5초마다 한번 실행
            self.is_Not_Drowsy(smemory_eyeopen, fps_per_p_five_sec, smemory_is_drowsy)

            #2초에 한번 실행
            if(while_count == 4):
                while_count = 0
                self.is_Drowsy(eye_state, fps_per_four_p_five_sec, smemory_is_drowsy)
                eye_state.value -= eye_state_timeline.value
                eye_state_timeline.value = 0
            time.sleep(0.5)

    def is_Not_Drowsy(self, smemory_eyeopen, fps_per_p_five_sec, smemory_is_drowsy):
        if fps_per_p_five_sec.value != 0:
            if (smemory_eyeopen.value / fps_per_p_five_sec.value) < EYE_OPEN_RATE_FPS:
                # 눈 뜨고있다면?
                smemory_is_drowsy.value = 0
                self.awake()
            smemory_eyeopen.value = 0
            fps_per_p_five_sec.value = 0

    def is_Drowsy(self, eye_state, fps_per_four_p_five_sec, smemory_is_drowsy):
        if fps_per_four_p_five_sec.value != 0:
            if (eye_state.value / fps_per_four_p_five_sec.value) > EYE_CLOSED_RATE_FPS:
                # 졸음이면
                smemory_is_drowsy.value = 1
                self.drowsy()
            #변수초기화
            fps_per_four_p_five_sec.value = 0

    def drowsy(self):
        if not self.sound.is_playing():
            self.sound.warn()

    def awake(self):
        if self.sound.is_playing():
            self.sound.warn_stop()