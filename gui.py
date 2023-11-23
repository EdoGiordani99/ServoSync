import tkinter as tk
from tkinter import ttk
import pygame
import threading
import time

from audioPlayer import AudioPlayer
from tkinter import PhotoImage, Menu
from datetime import datetime
from PIL import Image, ImageTk

BACKGROUND_COLOR = "#111224"
BLACK = "#000000"

def get_icon(path):
    icon_image = Image.open(path)
    resized_icon = icon_image.resize((40, 40))  # Adjust the size as needed
    return ImageTk.PhotoImage(resized_icon)


class TimeLine:

    def __init__(self, root, row, column, rowspan, columnspan) -> None:
        self.frame = tk.Frame(root, bg=BLACK)
        self.frame.grid(row=row, column=column, rowspan=rowspan, columnspan=columnspan)

        self.button = tk.Button(self.frame, text="PLAY", command=None)
        self.button.grid(row=0, column=0, padx=10)
        



class ServoSync:
    def __init__(self, root):
        self.root = root
        self.root.title("ServoSync")
        self.root.configure(background=BACKGROUND_COLOR)
        pygame.init()

        self.menubar = Menu(self.root)
        self.root.config(menu=self.menubar)

        self.file_menu = Menu(self.menubar)

        # add a menu item to the menu
        self.file_menu.add_command(label='Save', command=self.save)

        # add the File menu to the menubar
        self.menubar.add_cascade(
            label="File",
            menu=self.file_menu
        )

        self.audio_file = "mp3/Anna - Gasolina (Extended).mp3"  # Sostituisci con il percorso del tuo file audio
        self.playing = False

        self.audio_player = AudioPlayer()
        self.audio_player.load_file(self.audio_file)

        # Icons
        self.play_icon = get_icon(path="img/play_icon.png")
        self.pause_icon = get_icon(path="img/pause_icon.png")
        self.stop_icon = get_icon(path="img/stop_icon.png")

        # Creazione dell'interfaccia utente
        self.create_gui()
        self.root.after(1, self.update_gui)

    def save(self):
        print("Saved")

    def create_gui(self):
        # Creazione della track_timeline
        print(f"len: {self.audio_player.get_length()}")
        self.track_timeline = ttk.Scale(self.root, from_=0, to=self.audio_player.get_length(), orient="horizontal", length=400)
        self.track_timeline.grid(row=1, column=0, columnspan=2, pady=10)

        # Creazione dei bottoni
        self.play_button = tk.Button(self.root, text="PLAY", image=self.play_icon, background=BACKGROUND_COLOR, command=self.play_pause)
        self.play_button.grid(row=0, column=0, padx=10)
        self.stop_button = tk.Button(self.root, text="STOP", image=self.stop_icon, background=BACKGROUND_COLOR, command=self.stop)
        self.stop_button.grid(row=0, column=1, padx=10)
        
        # Timeline
        # self.timeline_f = TimeLine(root=root, row=3, column=0, rowspan=4, columnspan=4)


    def play_pause(self):
        if not self.playing:
            self.playing = True
            self.audio_player.play()
            self.play_button.config(text="PAUSE", image=self.pause_icon)
        else:
            self.playing = False
            self.audio_player.pause()
            self.play_button.config(text="PLAY", image=self.play_icon)

    def stop(self):
        self.playing = False
        self.play_button.config(text="PLAY", image=self.play_icon)
        self.audio_player.stop()

    def update_gui(self):
        print(self.audio_player.time)
        self.track_timeline.set(self.audio_player.time)
        self.root.after(1, self.update_gui)

    
        


    
if __name__ == "__main__":
    root = tk.Tk()
    app = ServoSync(root)
    root.mainloop()