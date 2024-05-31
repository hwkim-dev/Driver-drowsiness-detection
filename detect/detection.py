import threading
import sound_play
import time
import sched
import sys

EYE_CLOSED_RATE_FPS = 0.7

class detect_process:

    def __init__(self):
        self.eye_closed_start_time = None
        self.sound = sound_play.Sound()
        self.new_frame_time = 0
        self.prev_frame_time = 0

    #4.5초 마다 졸음감지 + 특정 기준마다 calc_fps계산해서 shared_memory_fps에 저장
    def recur_drowsy_fps_calc(self, shared_memory_fps):
        pass

    def calc_fps(self, shared_memory_fps):
        new_frame_time = time.time()
        shared_memory_fps.Value = 1 / (new_frame_time - self.prev_frame_time)
        self.prev_frame_time = new_frame_time

    def eye_close_detect(self):
        if self.eye_closed_start_time is None:
            self.eye_closed_start_time = time.time()
        else:
            elapsed_time = time.time() - self.eye_closed_start_time
            if elapsed_time > EYE_CLOSED_RATE_FPS:
                self.eye_closed_start_time = None
                if not self.sound.is_playing():
                    threading.Thread(target=self.sound.warn()).start()
                return True
        return False

    def reset_eye_closed(self):
        self.eye_closed_start_time = None
# import threading
# import sound_play
# import time
# import sched
# import sys
#
# EYE_CLOSED_RATE_FPS = 0.4
# EYE_OPEN_RATE_FPS = 0.2
#
#
# class detect_process:
#
#     def __init__(self):
#         self.eye_closed_cnt = 0
#         self.eye_closed_time = None
#         self.sound = sound_play.Sound()
#         self.prev_frame_time = 0
#         self.prev_frame_time = 0
#         self.new_frame_time = 0
#         self.fps = 0
#         self.frame_count_detect = 0
#         self.close_calc_fps_calls = 0
#         self.open_calc_fps_calls = 0
#         self.eye_open_cnt = 0
#         self.drowsy = False
#         self.closed_time_count_begin_time = 0
#         self.open_time_count_begin_time = 0
#
#     def calc_fps(self):
#         self.close_calc_fps_calls += 1
#         self.open_calc_fps_calls += 1
#         self.new_frame_time = time.time()
#         self.fps = 1 / (self.new_frame_time - self.prev_frame_time)
#         self.prev_frame_time = self.new_frame_time
#
#         clock = self.new_frame_time - self.closed_time_count_begin_time
#         open_cock = self.new_frame_time - self.open_time_count_begin_time
#         #눈뜸감지
#         if open_cock > 0.5:
#             if self.eye_open_cnt != 0:
#                 if self.eye_closed_cnt / self.close_calc_fps_calls > EYE_OPEN_RATE_FPS:
#                     self.sound.kill()
#                     self.drowsy = False
#             self.open_calc_fps_calls = 0
#             self.eye_open_cnt = 0
#
#             #졸음감지
#             if clock > 4.5:
#                 if self.eye_closed_cnt != 0:
#                     if self.eye_closed_cnt / self.close_calc_fps_calls > EYE_CLOSED_RATE_FPS:
#                         self.drowsy = True
#                         self.warning_play()
#                 self.closed_time_count_begin_time = time.time()
#                 self.close_calc_fps_calls = 0
#                 self.eye_closed_cnt = 0
#
#         return self.fps
#         # self.fps = fps
#
#     def eye_close_detect(self):
#         self.eye_closed_cnt += 0.5
#         return self.drowsy
#
#     # eye_open이 1초 지나면 closed 리셋 및 음원제거
#     def eye_open(self):
#         self.eye_open_cnt += 0.5
#         # if self.eye_open_t == 0:
#         #     self.eye_open_t = time.time()
#         # elif (time.time() - self.eye_open_t) > 0.5:
#         #
#         #     self.eye_closed_cnt = 0
#         #     self.eye_open_t = 0
#         #     self.drowsy = False
#         #     return self.drowsy
#         return True
#
#     def warning_play(self):
#         if not self.sound.is_playing():
#             threading.Thread(target=self.sound.warn()).start()
