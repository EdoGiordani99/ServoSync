from customtkinter import *
from PIL import Image, ImageTk

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


