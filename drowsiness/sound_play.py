import time
import winsound
import constant

class Sound():
    def __init__(self, sound_path):
        self.begin_time = 0
        self.PLAY_TIME = constant.SOUND_PLAY_SEC
        self.is_stopped = False
        self.sound_path = sound_path

    def is_playing(self):
        if self.is_stopped == True:
            return False
        if (time.perf_counter() - self.begin_time) < self.PLAY_TIME:
            return True
        else:
            return False

    def warn(self):
        self.is_stopped = False
        self.begin_time = time.perf_counter()
        winsound.PlaySound(self.sound_path, winsound.SND_ASYNC)

    def warn_stop(self):
        self.is_stopped = True
        winsound.PlaySound(None, winsound.SND_PURGE)
