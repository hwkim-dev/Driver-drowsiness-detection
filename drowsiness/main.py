import multiprocessing
import multiprocessing.process
import threading

import output_predict
import winsound
import tkinter as tk
import detection
import sys
import pickle
from tkinter import ttk
import time
class process_Manager:
    def __init__(self):
        self.smemory_event = None
        self.process_running = False
        self.detect_p = detection.detect_process()
        self.output_predict_main = output_predict.predict()
        self.running = None
        self.process_predict = None
        self.process_detect = None
        self.eye_state_pop = None
        self.eye_state_thd = None
        self.smemory_fps = None
        self.smemory_time_table = None
        self.smemory_eyeclosed_queue = None
        self.smemory_is_drowsy = None
        self.eye_state = None
        self.frame_time = None
        self.fps_per_four_p_five_sec = None
        self.fps_per_p_five_sec = None
        self.smemory_eyeopen = None


    def play_exit_sound(self):
        winsound.PlaySound(None, winsound.SND_PURGE)

    # shared_memory 는 줄여서 smemory 으러 표현
    def process_run(self):
        if not self.running:
            try:
                self.running = multiprocessing.Value('i', 1)
                self.smemory_fps = multiprocessing.Value('f', 0)
                # while 문이 한번씩 시행될 떄 마다 실행하는 코드
                self.smemory_event = multiprocessing.Event()
                self.smemory_eyeclosed = multiprocessing.Value('f', 0)
                self.smemory_is_drowsy = multiprocessing.Value('i', 0)
                self.eye_state = multiprocessing.Value('f', 0)
                self.frame_time = multiprocessing.Value('f', 0)
                self.fps_per_four_p_five_sec = multiprocessing.Value('i', 0)
                self.eye_state_timeline = multiprocessing.Queue()
                self.smemory_eyeopen = multiprocessing.Value('f', 0)
                self.fps_per_p_five_sec = multiprocessing.Value('i', 0)

                self.running.value = 1


                self.eye_state_thd = multiprocessing.Process(target=self.detect_p.eye_state_detect, args=(self.smemory_eyeopen, self.smemory_event, self.smemory_is_drowsy, self.eye_state, self.fps_per_four_p_five_sec, self.fps_per_p_five_sec))

                self.eye_state_pop = multiprocessing.Process(target=self.detect_p.eye_state_pop,
                                                             args=(self.smemory_event,self.eye_state, self.eye_state_timeline, ))

                self.process_detect = multiprocessing.Process(target=self.detect_p.recur_time_calculator,
                                                              args=(self.frame_time, self.smemory_fps, self.smemory_event,
                                                                    self.smemory_eyeclosed, self.eye_state, self.fps_per_four_p_five_sec, self.eye_state_timeline, self.fps_per_p_five_sec,))

                self.process_predict = multiprocessing.Process(target=self.output_predict_main.run,
                                                               args=(self.running,self.frame_time, self.smemory_fps, self.smemory_event,
                                                                     self.smemory_eyeclosed, self.smemory_eyeopen,
                                                                     self.smemory_is_drowsy))
                self.process_predict.start()
                self.eye_state_pop.start()
                self.process_detect.start()
                self.eye_state_thd.start()

                self.process_running = True
            except multiprocessing.ProcessError as err:
                self.process_predict.terminate()
                self.running = 0
                print(f"Process error: {err}")
            except Exception as err:
                self.process_predict.terminate()
                self.running = 0
                print(f"Unexpected error: {err}")
        else:
            pass

    def quit(self):
        self.running = 0
        self.play_exit_sound()
        if self.eye_state_thd is not None:
            self.eye_state_thd.terminate()
        if self.eye_state_pop is not None:
            self.eye_state_pop.terminate()
        if self.process_detect is not None:
            self.process_detect.terminate()
        #cv2 종료대기
        time.sleep(1)
        if self.process_predict is not None:
            self.process_predict.terminate()
        root.destroy()
        sys.exit(0)


if __name__ == '__main__':
    manager = process_Manager()
    root = tk.Tk()
    root.geometry("150x100")
    root.title("졸음 감지 프로그램")

    start_button = ttk.Button(root, text="시작", command=manager.process_run)
    start_button.pack(pady=10)

    stop_button = ttk.Button(root, text="종료", command=manager.quit)
    stop_button.pack()

    root.protocol("WM_DELETE_WINDOW", manager.quit)  # 창 닫기 버튼 처리
    root.mainloop()