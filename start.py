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
from project import ProjectApp

from gui import HomePage



class GUI:

    def __init__(self) -> None:

        self.root = CTk()
        self.start()
        self.home_page = HomePage(self.root, open_project_callback=self.open_project)

        self.project_is_open = False
        self.root.mainloop()

    def start(self):
        self.root.geometry("1500x800")
        self.appearance = "dark"
        set_appearance_mode(self.appearance)
        self.menubar = Menu(self.root)
        self.root.config(menu=self.menubar)
        self.root.protocol("WM_DELETE_WINDOW", self.exit)
        
        self.root.title("Servo Sync")
        
        self.root.iconbitmap("ServoSync.ico")
        
    def open_project(self, file):
        self.project_is_open = True
        self.home_page.destroy()
        self.project_page = ProjectApp(main_root=self.root, path=file, appearance=self.appearance, menubar=self.menubar)
        
    def exit(self):
        if self.project_is_open:
            check = self.project_page.popup_exit()
            if check:
                self.project_is_open = False
                self.home_page = HomePage(self.root, open_project_callback=self.open_project)
        else:
            self.root.destroy()

gui = GUI()