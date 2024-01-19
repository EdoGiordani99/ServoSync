import os
import time
import pickle
import threading
import tkinter as tk

from customtkinter import *
from PIL import Image, ImageTk
from tkinter import ttk, filedialog, messagebox, Menu, font

from scripts.colors import *
from scripts.utils import *
from scripts.editor import Editor
from scripts.controller import Controller
from scripts.audioPlayer import AudioPlayer
from scripts.tracks import FaderTrack, ButtonTrack, PanTiltTrack, CoupleTrack
from project import ProjectApp

TITLE_FONT = ("Proxima Nova", 28)
SUBTITLE_FONT = ("Proxima Nova", 18)
FONT = ("Proxima Nova", 16)

class HomePage:

    def __init__(self) -> None:
        self.start()
        self.welcome()
        self.root.mainloop()

    def start(self):
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

    def welcome(self):
        self.title_label = CTkLabel(self.root, text=f"Welcome to Servo Sync", font=TITLE_FONT)
        self.subtitle_label = CTkLabel(self.root, text=f"Craft Stunning Performances by Syncing Your Servo Motors to the Beat of Music!", font=SUBTITLE_FONT)
       
        self.title_label.grid(row=0, column=1, columnspan=3, pady=10)
        self.subtitle_label.grid(row=1, column=1, columnspan=3, pady=5)

        self.new_sequence_btn = CTkButton(self.root, 
                                         text="Create New\nSequence",
                                         image=self.icons.new_project_icon,
                                         corner_radius=10,
                                         fg_color=BUTTON_COLOR, hover_color=BUTTON_HOVER_COLOR,
                                         command=lambda: self.open_project(file=None),
                                         font=SUBTITLE_FONT)
        self.new_sequence_btn.grid(row=2, column=1, padx=20, pady=20, sticky="nsew")

        self.open_sequence_btn = CTkButton(self.root, 
                                         text="Open\nSequence",
                                         image=self.icons.open_project_icon,
                                         corner_radius=10,
                                         fg_color=BUTTON_COLOR, hover_color=BUTTON_HOVER_COLOR,
                                         command=self.menu_exit,
                                         font=SUBTITLE_FONT)
        self.open_sequence_btn.grid(row=3, column=1, padx=20, pady=20, sticky="nsew")

        self.playback_mode_btn = CTkButton(self.root, 
                                         text="Playback\nMode",
                                         image=self.icons.music_icon,
                                         corner_radius=10,
                                         fg_color=BUTTON_COLOR, hover_color=BUTTON_HOVER_COLOR,
                                         command=self.menu_exit, 
                                         font=SUBTITLE_FONT)
        self.playback_mode_btn.grid(row=2, column=2, padx=20, pady=20, sticky="nsew")

        self.help_btn = CTkButton(self.root, 
                                         text="Help &\nTutorial",
                                         image=self.icons.help_icon,
                                         corner_radius=10,
                                         fg_color=BUTTON_COLOR, hover_color=BUTTON_HOVER_COLOR,
                                         command=self.menu_exit, 
                                         font=SUBTITLE_FONT)
        self.help_btn.grid(row=3, column=2, padx=20, pady=20, sticky="nsew")
        
        self.show_open_recent()

        self.icon = CTkButton(self.root,
                            text="",
                            image=MAIN_ICON,
                            fg_color=BG_DARK_COLOR, 
                            hover_color=BG_DARK_COLOR)
        self.icon.grid(row=2, column=3, padx=20, pady=20, rowspan=6, sticky="nsew")
 
    def show_open_recent(self):

        self.open_recent_frame = CTkFrame(self.root, border_color=BUTTON_COLOR, fg_color=BG_DARK_COLOR, border_width=2)
        self.open_recent_frame.grid(row = 4, column=1, columnspan=2, padx=20, pady=10, sticky="nsew")

        self.open_recent_label = CTkLabel(self.open_recent_frame, text=f"Recent projects:", font=FONT)
        self.open_recent_label.grid(row=0, column=0, columnspan=2, padx=10, pady=10, sticky="w")

        recent_files = load_from_pickle("cache/recent_projects.pkl")
        files_btn_list = []

        for i, file in enumerate(recent_files[:10]):

            files_btn_list.append(RecentFileButton(root=self.open_recent_frame,
                                        file_path=file,
                                        callback = self.open_project,
                                        font=(FONT[0], FONT[1]-2),
                                        fg_color=BG_DARK_COLOR, 
                                        hover_color=BG_DARK_COLOR))
            
            files_btn_list[i].grid(row=1+i, column=0, padx=20, pady=3, sticky="w")
        
    def open_project(self, file):
        self.root.destroy()
        self.project_app = ProjectApp(path=file)
        
        # Reopen Homepage
        self.start()
        self.welcome()
        self.root.mainloop()

    def menu_exit(self):
        self.root.destroy()

    def center(self):
        self.root.columnconfigure(1, weight=1)
        self.root.columnconfigure(2, weight=1)


hp = HomePage()