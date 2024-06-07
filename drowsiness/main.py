import multiprocessing
from multiprocessing import shared_memory
import tkinter as tk
from tkinter import ttk
import time
import sys
from typing import Type
import winsound
import constant
import detection
import output_predict
import xml.etree.ElementTree as ET
import numpy as np

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
            'eye_open_cnt': multiprocessing.Value('f', 0.0),
            'eye_state_timeline': multiprocessing.Value('f', 0),
            'cropped_frame_np': multiprocessing.shared_memory.SharedMemory(create=True, size=int(np.prod(constant.input_shape))),
            'show_event': multiprocessing.Event(),
            'smemory_results': multiprocessing.shared_memory.SharedMemory(create=True, size=int(np.prod(constant.result_shape) * np.dtype(np.float16).itemsize)),
            'rectangle_size': multiprocessing.Array('i', [0, 0, 0, 0]),
        }

        self.processes = {
            'eye_state_clock': Type[multiprocessing.Process],
            'detect': Type[multiprocessing.Process],
            'predict': Type[multiprocessing.Process],
            'image_show': Type[multiprocessing.Process],
        }

        self.shared_memory['running'].value = constant.NOT_RUNNING

    def play_exit_sound(self):
        winsound.PlaySound(None, winsound.SND_PURGE)

    def start_processes(self):
        if self.shared_memory['running'].value == constant.NOT_RUNNING:
            try:
                self.shared_memory['running'].value = constant.RUNNING

                self.processes['image_show'] = multiprocessing.Process(
                    target=self.detect_process.image_show,
                    args=(
                        self.shared_memory['smemory_results'],
                        self.shared_memory['show_event'],
                        self.shared_memory['eye_closed_cnt'],
                        self.shared_memory['eye_open_cnt'],
                        self.shared_memory['cropped_frame_np'],
                        self.shared_memory['is_drowsy'],
                        self.shared_memory['fps'],
                    ),
                )
                self.processes['eye_state_clock'] = multiprocessing.Process(
                    target=self.detect_process.eye_state_clock,
                    args=(
                        self.shared_memory['eye_open_cnt'],
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
                        self.shared_memory['show_event'],
                        self.shared_memory['event'],
                        self.shared_memory['cropped_frame_np'],
                        self.shared_memory['smemory_results'],
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
        if self.shared_memory['running'].value == constant.RUNNING:
            self.play_exit_sound()
            for process in self.processes.values():
                if process is None:
                    continue
                else:
                    if process.is_alive():
                        process.terminate()

            # OpenCV 종료 기다리기
            time.sleep(1)

            # 좀비 프로세스가 만약에 있다면 (혹시) 처리
            for process in self.processes.values():
                if process is not None:
                    process.join()
        elif self.shared_memory['running'].value == constant.NOT_RUNNING:
            return

    def quit(self):
        self.stop_processes()
        root.destroy()
        sys.exit(0)


if __name__ == '__main__':
    manager = ProcessManager()

    root = tk.Tk()
    root.geometry("400x250")
    root.title("drowsy-detection-program")

    text_frame = ttk.Frame(root, width=50, height=200)
    text_frame.pack(expand=True, fill=tk.BOTH, side=tk.LEFT)

    validation_frame = ttk.Frame(root, width=30, height=200)
    validation_frame.pack(expand=True, fill=tk.BOTH, side=tk.LEFT)

    button_frame = ttk.Frame(root, width=50, height=200)
    button_frame.pack(expand=True, fill=tk.BOTH, side=tk.LEFT)
    mg = tk.StringVar()
    mg.set("CUDA")
    mg1 = tk.StringVar()
    mg1.set("OPENVINO")
    mg2 = tk.StringVar()
    mg2.set("ONNX")
    mg3 = tk.StringVar()
    mg3.set("ss")

    gui_texts = [mg, mg1, mg2, mg3]

    for i in range(4):
        text = gui_texts[i]
        entry = ttk.Entry(text_frame, state="readonly", textvariable=text, width=1)
        entry.pack(expand=True, fill=tk.X, padx=3, pady=10, side=tk.TOP, ipadx=1)

    test1 = tk.StringVar()
    test1.set("TRUE")
    test2 = tk.StringVar()
    test2.set("FALSE")
    test3 = tk.StringVar()
    test3.set("TRUE")
    test4 = tk.StringVar()
    test4.set("FALSE")
    gui_texts1 = [test1, test2, test3, test4]

    for i in range(4):
        text = gui_texts1[i]
        entry = ttk.Entry(validation_frame, state="readonly", textvariable=text, width=1)
        entry.pack(expand=True, fill=tk.X, padx=1, pady=10, side=tk.TOP, ipadx=1)

    start_button = ttk.Button(button_frame, text="run", command=manager.start_processes)
    start_button.pack(expand=True, fill=tk.BOTH, padx=10, pady=10, side=tk.TOP)

    stop_button = ttk.Button(button_frame, text="exit", command=manager.quit)
    stop_button.pack(expand=True, fill=tk.BOTH, padx=10, pady=10,  side=tk.TOP)


    root.protocol("WM_DELETE_WINDOW", manager.quit)
    root.mainloop()

