import multiprocessing
import tkinter as tk
from tkinter import ttk
import time
import sys
from typing import Type
import winsound

import detection
import output_predict
import xml.etree.ElementTree as ET


class ProcessManager:

    def __init__(self):
        path_tree = ET.parse('paths.xml').getroot()
        sound_path = path_tree.find('sound_Path').text
        model_path = path_tree.find('model_path')

        self.detect_process = detection.detect_process(sound_path)
        self.predict_process = output_predict.predict(model_path)

        self.shared_memory = {
            'running': multiprocessing.Value('i', 0),
            'fps': multiprocessing.Value('i', 0),
            'event': multiprocessing.Event(),
            'eye_closed_cnt': multiprocessing.Value('f', 0.0),
            'is_drowsy': multiprocessing.Value('i', 0),
            'eye_state': multiprocessing.Value('f', 0.0),
            'frame_cnt': multiprocessing.Value('i', 0),
            'eye_open_time': multiprocessing.Value('f', 0.0),
            'eye_state_timeline': multiprocessing.Value('f', 0),
        }

        self.processes = {
            'eye_state_clock': Type[multiprocessing.Process],
            'detect': Type[multiprocessing.Process],
            'predict': Type[multiprocessing.Process],
        }

    def play_exit_sound(self):
        winsound.PlaySound(None, winsound.SND_PURGE)

    def start_processes(self):
        if self.shared_memory['running'].value == 0:
            try:
                self.shared_memory['running'].value = 1

                self.processes['eye_state_clock'] = multiprocessing.Process(
                    target=self.detect_process.eye_state_clock,
                    args=(
                        self.shared_memory['eye_open_time'],
                        self.shared_memory['event'],
                        self.shared_memory['is_drowsy'],
                        self.shared_memory['eye_state'],
                        self.shared_memory['frame_cnt'],
                        self.shared_memory['eye_state_timeline'],
                    ),
                )
                self.processes['detect'] = multiprocessing.Process(
                    target=self.detect_process.recur_time_calculator,
                    args=(
                        self.shared_memory['fps'],
                        self.shared_memory['event'],
                        self.shared_memory['eye_closed_cnt'],
                        self.shared_memory['eye_state'],
                        self.shared_memory['eye_state_timeline'],
                        self.shared_memory['frame_cnt'],
                    ),
                )
                self.processes['predict'] = multiprocessing.Process(
                    target=self.predict_process.run,
                    args=(
                        self.shared_memory['running'],
                        self.shared_memory['fps'],
                        self.shared_memory['event'],
                        self.shared_memory['eye_closed_cnt'],
                        self.shared_memory['eye_open_time'],
                        self.shared_memory['is_drowsy'],
                    ),
                )

                for process in self.processes.values():
                    process.start()

            except multiprocessing.ProcessError as err:
                self.stop_processes()
                print(f"Process error: {err}")
            except Exception as err:
                self.stop_processes()
                print(f"Unexpected error: {err}")

    def stop_processes(self):

        self.shared_memory['running'].value = 0
        self.play_exit_sound()

        for process in self.processes.values():
            if process.is_alive():
                process.terminate()

        #OpenCV 종료 기다리기
        time.sleep(1)

        #좀비 프로세스가 만약에 있다면 (혹시) 처리
        for process in self.processes.values():
            if process is not None:
                process.join()

    def quit(self):
        self.stop_processes()
        root.destroy()
        sys.exit(0)


if __name__ == '__main__':
    manager = ProcessManager()

    root = tk.Tk()
    root.geometry("150x100")
    root.title("졸음 감지 프로그램")

    start_button = ttk.Button(root, text="시작", command=manager.start_processes)
    start_button.pack(pady=10)

    stop_button = ttk.Button(root, text="종료", command=manager.quit)
    stop_button.pack()

    root.protocol("WM_DELETE_WINDOW", manager.quit)
    root.mainloop()
