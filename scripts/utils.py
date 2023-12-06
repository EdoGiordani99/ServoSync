from PIL import Image, ImageTk


class Icons:
    def __init__(self) -> None:
        self.play_icon = self.get_icon(path="img/play_icon.png")
        self.pause_icon = self.get_icon(path="img/pause_icon.png")
        self.stop_icon = self.get_icon(path="img/stop_icon.png")
        self.rec_start_icon = self.get_icon(path="img/rec_start.png")
        self.rec_stop_icon = self.get_icon(path="img/rec_stop.png")
        self.music_icon = self.get_icon(path="img/music_icon.png", height=20, width=20)
        self.connected_icon = self.get_icon(path="img/connected_icon.png", height=20, width=20)
        self.disconnected_icon = self.get_icon(path="img/disconnected_icon.png", height=20, width=20)

    def get_icon(self, path, height:int=60, width:int=60):
        icon_image = Image.open(path)
        resized_icon = icon_image.resize((height, width))
        return ImageTk.PhotoImage(resized_icon)

