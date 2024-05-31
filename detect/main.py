import multiprocessing
import multiprocessing.process
import output_predict
import winsound
import tkinter as tk
import detection
import time
import sched
import sys


class process_Manager:
    def __init__(self):
        self.detect_p = detection.detect_process()
        self.output_predict_main = output_predict.predict()
        self.running = False
        self.predict = None
        self.shared_value = None

    def play_exit_sound(self):
        winsound.PlaySound(None, winsound.SND_PURGE)

    #shared_memory 는 줄여서 smemory 으러 표현
    def process_run(self):
        if not self.running:
            try:
                self.smemory_fps = multiprocessing.Value('i', 0)
                self.smemory_time_table = multiprocessing.Queue(30)
                
                self.predict = multiprocessing.Process(target=self.output_predict_main.run, args=(self.detect_p,self.smemory_fps,smemory_time_table))
                self.predict.start()
                self.running = True
            except multiprocessing.ProcessError as err:
                self.predict.terminate()
                self.running = False
                print(f"Process error: {err}")
            except Exception as err:
                self.predict.terminate()
                self.running = False
                print(f"Unexpected error: {err}")
        else :
            pass

    def quit(self):
        self.running = False
        self.play_exit_sound()
        if self.predict is not None:
            self.predict.terminate()
        root.destroy()


if __name__ == '__main__':
    manager = process_Manager()

    root = tk.Tk()
    root.geometry("150x150")

    small_button = tk.Button(root, command=manager.quit, text="exit", width=5, height=2, font=10)
    small_button.pack()
    small_button = tk.Button(root, command=manager.process_run, text="start", width=5, height=2, font=10)
    small_button.pack()

    root.mainloop()

# import multiprocessing
# import output_predict
# import winsound
# import tkinter as tk
# import detection
# import time
# import sched
# import sys
#
#
# class process_Manager:
#     def __init__(self):
#         self.detect_p = detection.detect_process()
#         self.output_predict_main = output_predict.predict()
#         self.running = True
#         self.predict = None
#         self.check = None
#
#     def process_run(self):
#         # self.check = multiprocessing.Process(target=self.detect_p.check_warn)
#         self.predict = multiprocessing.Process(target=self.output_predict_main.run, args=(self.detect_p,))
#         # self.check.start()
#         self.predict.start()
#
#     def quit(self):
#         self.running = False
#         winsound.PlaySound(None, winsound.SND_PURGE)
#         if self.predict is not None:
#             self.predict.terminate()
#         if self.check is not None:
#             self.check.terminate()
#         root.destroy()
#
#
# if __name__ == '__main__':
#     manager = process_Manager()
#
#     root = tk.Tk()
#     root.geometry("150x150")
#
#     small_button = tk.Button(root, command=manager.quit, text="exit", width=5, height=2, font=10)
#     small_button.pack()
#     small_button = tk.Button(root, command=manager.process_run, text="start", width=5, height=2, font=10)
#     small_button.pack()
#
#     root.mainloop()