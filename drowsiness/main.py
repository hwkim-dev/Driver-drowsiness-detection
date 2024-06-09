import multiprocessing
from multiprocessing import shared_memory
import time
import sys
from typing import Type
import winsound
import constant
import detection
import gui_manager
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
            'cropped_frame_np': multiprocessing.shared_memory.SharedMemory(
                create=True, size=int(np.prod(constant.input_shape))),
            'show_event': multiprocessing.Event(),
            'smemory_results': multiprocessing.shared_memory.SharedMemory(
                create=True, size=int(
                    np.prod(constant.result_shape) * np.dtype(np.float16).itemsize
                )),
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

            time.sleep(1)

        elif self.shared_memory['running'].value == constant.NOT_RUNNING:
            pass

        sys.exit(0)


if __name__ == '__main__':
    manager = ProcessManager()
    gui_manager.start_window(manager)

