import os
import time
import pickle
import threading
import tkinter as tk

from customtkinter import *
from tkinter import ttk, filedialog, messagebox, Menu, font

from scripts.colors import *
from scripts.utils import Icons
from scripts.editor import Editor
from scripts.controller import Controller
from scripts.audioPlayer import AudioPlayer
from scripts.tracks import FaderTrack, ButtonTrack, PanTiltTrack, CoupleTrack
from project import ProjectApp

FONT = ("Proxima Nova", 18)

class HomePage:

    def __init__(self) -> None:
        self.root = CTk()
        self.root.geometry("1000x600")
        self.appearance = "dark"
        set_appearance_mode(self.appearance)
        self.menubar = Menu(self.root)
        self.root.config(menu=self.menubar)
        self.root.protocol("WM_DELETE_WINDOW", self.menu_exit)
        self.center()
        
        self.root.title("Servo Sync")
        
        self.root.iconbitmap("ServoSync.ico")
        self.icons = Icons(size=150)

        self.welcome()
    
        self.root.mainloop()

    def welcome(self):
        self.title_label = CTkLabel(self.root, text=f"Welcome to Servo Sync", font=FONT)
        self.subtitle_label = CTkLabel(self.root, text=f"Craft Stunning Performances by Syncing Your Servo Motors to the Beat of Music!", font=FONT)
       
        self.title_label.grid(row=0, column=1, columnspan=2, pady=10)
        self.subtitle_label.grid(row=1, column=1, columnspan=2, pady=5)


        self.new_sequence_btn = CTkButton(self.root, 
                                         text="Create New\nSequence",
                                         image=self.icons.music_icon,
                                         corner_radius=10,
                                         fg_color=BUTTON_COLOR, hover_color=BUTTON_HOVER_COLOR,
                                         command=self.menu_exit,
                                         font=FONT)
        self.new_sequence_btn.grid(row=2, column=1, padx=20, pady=20, sticky="nsew")

        self.open_sequence_btn = CTkButton(self.root, 
                                         text="Open\nSequence",
                                         image=self.icons.music_icon,
                                         corner_radius=10,
                                         fg_color=BUTTON_COLOR, hover_color=BUTTON_HOVER_COLOR,
                                         command=self.menu_exit,
                                         font=FONT)
        self.open_sequence_btn.grid(row=3, column=1, padx=20, pady=20, sticky="nsew")

        self.playback_mode_btn = CTkButton(self.root, 
                                         text="Playback\nMode",
                                         image=self.icons.music_icon,
                                         corner_radius=10,
                                         fg_color=BUTTON_COLOR, hover_color=BUTTON_HOVER_COLOR,
                                         command=self.menu_exit, 
                                         font=FONT)
        self.playback_mode_btn.grid(row=4, column=1, padx=20, pady=20, sticky="nsew")






    def menu_exit(self):
        print("Exit")

    def center(self):

        
        self.root.columnconfigure(1, weight=1)

        self.root.columnconfigure(2, weight=2)



hp = HomePage()