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
            eye_state_timeline.put(copy_eye_state)

            smemory_event.clear()


    #0.5초 단위로 queue에 쌓인 eye 상태를 전부 저장 시켜놈, 4.5초만큼 쌓이면


    def eye_state_pop(self, smemory_event, eye_state, eye_state_timeline):
        smemory_event.wait()
        smemory_event.clear()
        time.sleep(4.5)
        while True:
            smemory_event.wait()
            test = eye_state_timeline.get()
            eye_state.value -= test
            smemory_event.clear()

    # 프로그램이 시작하고 4.5초가 지나면 계속 eye_state의 변수를 매 프레임마다 삭제
    #0.5초에 한번 실행해서 눈 뜨고있는지 -> 눈을 뜨고있는데 현재 졸음상태로 판단하면 즉각적으로 졸음 아니라고 해놓기
    #2초에 한번씩 실행해서 눈 감고 있는지 -> 눈 감고있으면 바로 졸음상태로...
    def eye_state_detect(self,smemory_eyeopen, smemory_event, smemory_is_drowsy, eye_state, fps_per_four_p_five_sec, fps_per_p_five_sec):
        current_time = time.perf_counter()
        two_sec_clock = 0
        while True:
            begin_time = time.perf_counter()
            smemory_event.wait()
            # cv의 while문이 한번 실행될 떄마다
            point_f_clock = begin_time - current_time
            two_sec_clock += point_f_clock

            #0.5초에 한번 실행(눈 뜨고있는지)
            # 0.5초동안의 fps 개수로 눈 상태를 나눠서
            # 눈을 뜨고있는 상태라면 음수가 나올거다... 값은 -1~0사이값
            # 만약 눈을 뜨고있는 상태의 비율이 0.2 이상이면 바로 졸음 아니다 판단.
            if(point_f_clock) > 0.5:
                current_time = time.perf_counter()
                if fps_per_four_p_five_sec.value != 0:
                    if (smemory_eyeopen.value / fps_per_p_five_sec.value) < EYE_OPEN_RATE_FPS:
                        # 눈 뜨고있다면?
                        smemory_is_drowsy.value = 0
                        self.awake()
                smemory_eyeopen.value = 0
                fps_per_p_five_sec.value = 0


            # 2초에 1번 실행(눈 감고있는지)
            # eye_state.value는 최초 시작 4.5초동안 데이터가 쌓이고
            # 4.5초가 지나면 맨 처음 들어온 데이터부터 삭제됨.
            if (two_sec_clock) > 2:
                two_sec_clock = 0
                if (eye_state.value / fps_per_four_p_five_sec.value) > EYE_CLOSED_RATE_FPS:
                    # 졸음이면
                    smemory_is_drowsy.value = 1
                    self.drowsy()
                #변수초기화
                fps_per_four_p_five_sec.value = 0

            # 4초에 1번 실행

            smemory_event.clear()

    def drowsy(self):
        if not self.sound.is_playing():
            self.sound.warn()

    def awake(self):
        if self.sound.is_playing():
            self.sound.warn_stop()