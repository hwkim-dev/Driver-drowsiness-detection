def play_exit_sound(self):
    winsound.PlaySound(None, winsound.SND_PURGE)#import pyvolume
import time
import winsound

PLAY_TIME = 36


class Sound():
    def __init__(self):
        self.begin_time = 0

    def is_playing(self):
        if (time.time() - self.begin_time) < PLAY_TIME:
            return True
        else:
            return False

    def warn(self):
        self.begin_time = time.time()
        winsound.PlaySound(r'C:\D\github\Driver-drowsiness-detection\detect\militray_warn.wav', winsound.SND_ASYNC)
# import pyvolume
# import time
# import winsound
#
# PLAY_TIME = 36
#
#
# class Sound():
#     def __init__(self):
#         self.begin_time = 0
#
#     def is_playing(self):
#         if (time.time() - self.begin_time) < PLAY_TIME:
#             return True
#         else:
#             return False
#     def kill(self):
#         winsound.PlaySound(None, winsound.SND_PURGE)
#     def warn(self):
#         self.begin_time = time.time()
#         winsound.PlaySound(r'C:\\D\\DL_proj\\rngus\\militray_warn.wav', winsound.SND_ASYNC)
