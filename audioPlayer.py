import pygame
import threading
import time
import os 

from datetime import datetime

class AudioPlayer:
    
    def __init__(self):
        self.is_playing = False
        self.stopped = False
        self.mixer = pygame.mixer
        self.mixer.init()
        self.startTimestamp = None
        self.track = None
        self.time = 0
        self.loaded = False
        self.paused_at = 0
    
    def load_file(self, file_path):
        self.track = self.mixer.Sound(file_path)
        self.mixer.music.load(file_path)
        self.loaded = True
        
    def count_time(self):
        while not self.stopped:
            if self.is_playing:
                self.time = round(self.paused_at + self.mixer.music.get_pos()/1000, 4)
            time.sleep(0.0001)
        self.time = 0.0

    def play(self):
        if self.loaded:
            if not self.is_playing:
                self.stopped = False
                self.is_playing = True
                self.timer_thread = threading.Thread(target=self.count_time)
                self.mixer.music.play(start=self.paused_at)
                self.startTimestamp = datetime.now()
                self.timer_thread.start()

        else:
            print("ERROR: No track loaded on the Audio Player!")

    def pause(self):
        self.paused_at += self.mixer.music.get_pos()/1000
        self.mixer.music.pause()
        self.is_playing = False
   
    def stop(self):

        if not self.is_playing:
            self.paused_at = 0.0
        
        self.mixer.music.stop()
        self.is_playing = False
        self.stopped = True

    def get_length(self):
        return self.track.get_length() if self.track else None

    def get_time_int(self):
        if self.time:
            return self.time.total_seconds()
        else: 
            return 0


if __name__ == "__main__":
    a = AudioPlayer()

    a.load_file("mp3/Anna - Gasolina (Extended).mp3")
    a.play()
    time.sleep(2)
    a.pause()
    time.sleep(2)
    a.play()
