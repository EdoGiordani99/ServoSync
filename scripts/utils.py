from customtkinter import *
from PIL import Image, ImageTk

import pickle

class Icons:
    def __init__(self, size:int = 60) -> None:
        self.play_icon = self.get_icon(path="img/play_icon.png", height=size, width=size)
        self.pause_icon = self.get_icon(path="img/pause_icon.png", height=size, width=size)
        self.stop_icon = self.get_icon(path="img/stop_icon.png", height=size, width=size)
        self.rec_start_icon = self.get_icon(path="img/rec_start.png", height=size, width=size)
        self.rec_stop_icon = self.get_icon(path="img/rec_stop.png", height=size, width=size)
        self.music_icon = self.get_icon(path="img/music_icon.png", height=size/3, width=size/3)
        self.connected_icon = self.get_icon(path="img/connected_icon.png", height=size/3, width=size/3)
        self.disconnected_icon = self.get_icon(path="img/disconnected_icon.png", height=size/3, width=size/3)
        self.app_icon = self.get_icon(path="img/ServoSyncIcon.png")
        self.new_project_icon = self.get_icon(path="img/HomePage/NewProjectIcon.png", height=size/3, width=size/3)
        self.open_project_icon = self.get_icon(path="img/HomePage/OpenProjectIcon.png", height=size/3, width=size/3)
        self.help_icon = self.get_icon(path="img/HomePage/HelpIcon.png", height=size/3, width=size/3)

    def get_icon(self, path, height:int=60, width:int=60):
        """  
        icon_image = Image.open(path)
        resized_icon = icon_image.resize((height, width))
        return ImageTk.PhotoImage(resized_icon)
        """

        if type(path) == str:
            light_path, dark_path = path, path
        elif type(path) == tuple:
            light_path, dark_path = path


        return CTkImage(light_image=Image.open(light_path),
                            dark_image=Image.open(dark_path),
                            size=(height, width))

MAIN_ICON = CTkImage(light_image=Image.open("img/ServoSyncIconTransparent.png"),
                     dark_image=Image.open("img/ServoSyncIconTransparent.png"),
                     size=(450, 450))


def load_from_pickle(input_file):
    with open(input_file, 'rb') as file:
        loaded_obj = pickle.load(file)
    return loaded_obj

def write_on_pickle(obj, file_path):
    with open(file_path, 'wb') as file:
        pickle.dump(obj, file)


class RecentFileButton:

    def __init__(self, root, file_path, callback, *args, **kwargs) -> None:

        self.file_path = file_path

        self.button = CTkButton(master=root, text=file_path, command=lambda: callback(file_path), *args, **kwargs)
        self.font = self.button.cget("font")

        self.button.bind("<Enter>", lambda event: self.hover("e"))
        self.button.bind("<Leave>", lambda event: self.hover("l"))
    
    def hover(self, event):

        try:
            name, size = self.font
            if event == "e":
                self.button.configure(font=(name, size, 'bold'))
            else:
                self.button.configure(font=(name, size))
        except Exception as e:
            print(e)
    
    def grid(self, *args, **kwargs):
        self.button.grid(*args, **kwargs)