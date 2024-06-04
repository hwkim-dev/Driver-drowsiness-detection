import time
import winsound




class Sound():
    def __init__(self):
        self.begin_time = 0
        self.PLAY_TIME = 36
        self.is_stopped = False

    def is_playing(self):
        if(self.is_stopped == True):
            return False
        if (time.perf_counter() - self.begin_time) < self.PLAY_TIME:
            return True
        else:
            return False

    def warn(self):
        self.is_stopped = False
        self.begin_time = time.perf_counter()
        winsound.PlaySound(r'audio/militray_warn.wav', winsound.SND_ASYNC)

    def warn_stop(self):
        self.is_stopped = True
        winsound.PlaySound(None, winsound.SND_PURGE)
