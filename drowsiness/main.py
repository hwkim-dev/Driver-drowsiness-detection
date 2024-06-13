import multiprocessing
import time
import sys
from typing import Type
import winsound
import constant
import detection
import gui_manager
import output_predict
import xml.etree.ElementTree as ET
import shared_memory_Manager
import model_exporter
import torch


class ProcessManager:

    def __init__(self):
        self.processes = None
        self.s_memory = None
        self.predict_process = None
        self.detect_process = None
        self.detect_process: detection.detect_process
        self.predict_process: output_predict.predict
        self.s_memory: shared_memory_Manager.SharedMemoryManager
        self.processes: dict
        self.device: str
        if torch.cuda.is_available():
            self.device = constant.CUDA
        else:
            self.device = constant.LOCAL

    def init_program(self):
        path_tree = ET.parse('paths.xml').getroot()
        sound_path = path_tree.find('sound_Path').text
        model_path = path_tree.find('model_path')

        model_exporter.exporter(model_path, self.device)

        self.detect_process = detection.detect_process(sound_path)
        self.predict_process = output_predict.predict(model_path, self.device)
        self.s_memory = shared_memory_Manager.SharedMemoryManager()

        self.processes = {
            'eye_state_clock': Type[multiprocessing.Process],
            'detect': Type[multiprocessing.Process],
            'predict': Type[multiprocessing.Process],
            'image_show': Type[multiprocessing.Process],
        }

        self.s_memory.set_memory('running', constant.NOT_RUNNING)

    def start_processes(self):
        if self.s_memory.get_value('running') == constant.NOT_RUNNING:
            try:
                self.s_memory.set_memory('running', constant.RUNNING)
                self.processes['image_show'] = multiprocessing.Process(
                    target=self.detect_process.image_show,
                    args=(
                        *self.s_memory.get_memory('smemory_results', 'show_event', 'eye_closed_cnt', 'eye_open_cnt',
                                                  'cropped_frame_np', 'is_drowsy', 'fps').values(),
                    ),
                )
                self.processes['eye_state_clock'] = multiprocessing.Process(
                    target=self.detect_process.eye_state_clock,
                    args=(
                        *self.s_memory.get_memory('eye_open_cnt', 'new_frame_event', 'is_drowsy', 'eye_state',
                                                  'frame_cnt', 'eye_state_timeline', 'smemory_face_detected').values(),
                    ),
                )
                self.processes['detect'] = multiprocessing.Process(
                    target=self.detect_process.recur_time_calculator,
                    args=(
                        *self.s_memory.get_memory('fps', 'new_frame_event', 'eye_closed_cnt', 'eye_state',
                                                  'eye_state_timeline',
                                                  'frame_cnt', 'smemory_face_detected').values(),
                    ),
                )
                self.processes['predict'] = multiprocessing.Process(
                    target=self.predict_process.run,
                    args=(
                        *self.s_memory.get_memory('running', 'show_event', 'new_frame_event', 'cropped_frame_np',
                                                  'smemory_results',
                                                  'smemory_face_detected').values(),
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
        if self.s_memory.get_value('running') == constant.RUNNING:
            self.s_memory.set_memory('running', constant.NOT_RUNNING)
            time.sleep(1)

            winsound.PlaySound(None, winsound.SND_PURGE)
            for process in self.processes.values():
                if process is None:
                    continue
                else:
                    if process.is_alive():
                        process.terminate()

            self.s_memory.kill_process()

        elif self.s_memory.get_value('running') == constant.NOT_RUNNING:
            pass
        try:
            from IPython import get_ipython
            if get_ipython():
                time.sleep(1)
            else:
                sys.exit(0)
        except ImportError:
            sys.exit(0)


if __name__ == '__main__':
    manager = ProcessManager()
    manager.init_program()
    window = gui_manager.manager()
    window.start_window(manager)

