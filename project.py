import os
import time
import pickle
import threading
import tkinter as tk

from customtkinter import *
from tkinter import ttk, filedialog, messagebox, Menu

from scripts.colors import *
from scripts.utils import Icons
from scripts.editor import Editor
from scripts.controller import Controller, WiFiController
from scripts.audioPlayer import AudioPlayer
from scripts.tracks import FaderTrack, ButtonTrack, PanTiltTrack, CoupleTrack


class ProjectApp:

    def __init__(self, row:int = 0, column:int = 0):

        self.root = CTk()
        self.appearance = "dark"
        set_appearance_mode(self.appearance)
        self.menubar = Menu(self.root)
        self.root.config(menu=self.menubar)
        self.root.protocol("WM_DELETE_WINDOW", self.popup_exit)
        
        self.root.title("Servo Sync")
        
        self.root.iconbitmap("ServoSync.ico")

        self.controller = Controller()
        # self.controller = WiFiController()
        
        self.row, self.column, self.song_path = row, column, None
        self.occupied_pos = []
        self.COLUMNS = 4

        self.frame = CTkFrame(self.root, fg_color=self.root.cget("fg_color"))
        self.frame.grid(row = self.row, column=self.column, columnspan=self.COLUMNS)

        self.player = AudioPlayer()
        self.playing = False

        self.tracks = {}
        self.num_tracks = 0
        self.save_path = self.get_untitled_path()

        # Menu Bar
        self.menubar_init()

        # Icons
        self.icons = Icons()

        self.connected_btn = CTkButton(self.frame, 
                                         text="Disconnected",
                                         image=self.icons.disconnected_icon,
                                         corner_radius=10,
                                         fg_color=self.frame.cget("fg_color"), hover_color=BUTTON_HOVER_COLOR,
                                         command=self.controller.connect_to_arduino)
        self.connected_btn.grid(row=self.row, column=self.column, padx=5, pady=1, sticky="w")

        # Select Song Button
        self.select_song_btn = CTkButton(self.frame, 
                                         text="Select Song",
                                         image=self.icons.music_icon,
                                         corner_radius=10,
                                         fg_color=BUTTON_COLOR, hover_color=BUTTON_HOVER_COLOR,
                                         command=self.select_audio_file)
        self.select_song_btn.grid(row=self.row+1, column=self.column, padx=5, pady=1, sticky="w")

        # Song Title
        self.song_title_label = CTkLabel(self.frame, text="Choose a Song", width=80, font=("Arial", 16))
        self.song_title_label.grid(row=self.row, column=self.column+1, columnspan=2, pady=5)

        # Timestamp
        self.timestamp = " "
        self.timestamp_label = CTkLabel(self.frame, text=self.timestamp, width=10, font=("Arial", 50))
        self.timestamp_label.grid(row=self.row+1, column=self.column+1, columnspan=2, pady=1)

        # Play - Pause - Stop
        self.play_btn = CTkButton(self.frame, width=32, text="", fg_color=BUTTON_COLOR, hover_color=BUTTON_HOVER_COLOR, height=32,corner_radius=10, image=self.icons.play_icon, command=self.play_pause_callback)
        self.play_btn.grid(row=self.row+1, column=self.column+5, padx=10)
        self.stop_btn = CTkButton(self.frame, width=32, text="", fg_color=BUTTON_COLOR, hover_color=BUTTON_HOVER_COLOR, height=32,corner_radius=10, image=self.icons.stop_icon, command=self.stop_callback)
        self.stop_btn.grid(row=self.row+1, column=self.column+6, padx=10)
        self.rec_btn = CTkButton(self.frame, width=32, text="", fg_color=BUTTON_COLOR, hover_color=BUTTON_HOVER_COLOR, height=32,corner_radius=10, image=self.icons.rec_start_icon, command=self.rec_callback)
        self.rec_btn.grid(row=self.row+1, column=self.column+4, padx=10)
        self.rec = False

        s = self.player.get_length_seconds()
        if s:
            self.track_timeline = CTkSlider(self.frame, from_=0, to=s, button_color=BUTTON_COLOR, button_hover_color=BUTTON_HOVER_COLOR, orientation="horizontal", width=950)
        else:
            self.track_timeline = CTkSlider(self.frame, from_=0, to=1, orientation="horizontal", width=950)
        self.track_timeline.grid(row=self.row+2, column=self.column+1, columnspan=2, pady=10)
        
        self.update_status_thread = threading.Thread(target=self.update_status)
        self.update_status_thread.start()

        self.recorder_thread = None
        self.record_tape = None
        self.frame_rate = 0.1
        self.RC = 0
        self.editor = None

        self.root.mainloop()

    def menubar_init(self):
        self.file_menu = Menu(self.menubar)
        self.file_menu.add_command(label='Save', command=self.save)
        self.file_menu.add_command(label='Save As', command=self.save_as)
        self.file_menu.add_command(label='Open', command=self.open)
        self.file_menu.add_command(label='Open Preset from File', command=self.load_preset_from_file)
        
        self.menubar.add_cascade(label="File", menu=self.file_menu)

        self.track_menu = Menu(self.menubar)
        self.track_menu.add_command(label='Add Fader Track', command=lambda: self.add_track(type="fader"))
        self.track_menu.add_command(label='Add Button Track', command=lambda: self.add_track(type="button"))
        self.track_menu.add_command(label='Add Pan-Tilt Track', command=lambda: self.add_track(type="pantilt"))
        self.track_menu.add_command(label='Add Couple Track', command=lambda: self.add_track(type="couple"))
        self.menubar.add_cascade(label="Track", menu=self.track_menu)

        self.controller_menu = Menu(self.menubar)
        self.controller_menu.add_command(label='Try Reconnect', command= self.reconnect_controller)
        self.menubar.add_cascade(label="Controller", menu=self.controller_menu)

        self.aspect_menu = Menu(self.menubar)
        if self.appearance == "dark":
            self.aspect_menu.add_command(label="Change to Light Mode", command= self.change_theme)
        else:
            self.aspect_menu.add_command(label="Change to Dark Mode", command= self.change_theme)

        self.menubar.add_cascade(label="Aspect", menu=self.aspect_menu)
    
    def change_theme(self):
        if self.appearance == "dark":
            new_text = "Change to Dark Mode"
            self.appearance = "light"
            set_appearance_mode("light")
        else:
            new_text = "Change to Light Mode"
            self.appearance = "dark"
            set_appearance_mode("dark")
        
        self.menubar.entryconfig("Aspect", menu=self.aspect_menu.entryconfig(0, label=new_text))

    def reconnect_controller(self):
        self.controller.connect_to_arduino()
        if self.controller.connected:
            for servo in self.tracks.values():
                servo.update_available_servos(self.controller.get_servos_names())
        
    def update_status(self):
        while True:
            # Timestamp
            self.timestamp_label.configure(text=self.player.get_timestamp())

            # Track Timeline
            self.track_timeline.set(self.player.time)

            # Connected Arduino
            if self.controller.connected:
                text = "Connected"
                icon =  self.icons.connected_icon
            else:
                text = "Disconnected"
                icon =  self.icons.disconnected_icon
            self.connected_btn.configure(text=text, image=icon)

            # Editor
            try:
                if self.editor.is_open and self.playing:
                    window_size = self.editor.window_size
                    page = self.editor.page_num

                    min_v = window_size * page
                    max_v = min_v + window_size

                    rc_perc = self.RC / len(self.record_tape)

                    if rc_perc>= max_v:
                        self.editor.get_next_page()
                    elif rc_perc <= min_v:
                        self.editor.get_prev_page()
                    
                    self.editor.timeline.update_time_tracker(new_x=rc_perc, min_v=min_v, max_v=max_v)
                else:
                    if self.RC == 0:
                        self.editor.timeline.delete_tracker()

                    self.editor.timeline.RC = self.RC
                    
            except:
                pass

            time.sleep(0.25)
    
    def select_audio_file(self):
        song_path = filedialog.askopenfilename(title="Select a music file",
                                               filetypes=[("All files", "*.*")])
        
        self.load_audio_file(song_path=song_path)
        
    def load_audio_file(self, song_path):
        if song_path:
            self.song_path = os.path.abspath(song_path)
            self.song_title_label.configure(text=song_path.split("/")[-1])

            # Load file on player
            self.player.load_file(self.song_path)
            self.track_timeline.configure(to=self.player.get_length_seconds())

            # Add keyframes to record tape
            num_keyframes = int(round(self.player.get_length_seconds() / self.frame_rate, 0))
            self.record_tape = [{}] * num_keyframes

    def not_loaded_error(self):
        messagebox.showerror("No Music to Play", "Please, select an audio file you want to play")

    def get_free_coords(self, typ):

        if typ == "pantilt":
            rowspan, colspan= 2, 2
        else: 
            rowspan, colspan= 1, 1

        for i in range(3, 100):
            for j in range(self.COLUMNS):
                check, to_add = self.check_free_pos(i, j, rowspan, colspan)
                if check:
                    self.occupied_pos.extend(to_add)
                    return i, j
        return None, None

    def check_free_pos(self, i, j, rowspan, colspan):
        to_add = []
        for si in range(rowspan):
            for sj in range(colspan):
                pos = (i+si, j+sj)
                if pos in self.occupied_pos or pos[1] > self.COLUMNS-1:
                    return False, None
                to_add.append(pos)
        return True, to_add

    def add_track(self, type: str):
        """
        Args:
            type (str): fader, button, pantilt, couple
        """

        row, column = self.get_free_coords(type)
        self.num_tracks += 1

        print(row, column)
        if type == "fader":
            track = FaderTrack(self.root, row, column, self.num_tracks, self.controller, self.open_editor_callback)
        elif type == "button":
            track = ButtonTrack(self.root, row, column, self.num_tracks, self.controller, self.open_editor_callback)
        elif type == "pantilt":
            track = PanTiltTrack(self.root, row, column, self.num_tracks, self.controller, self.open_editor_callback)
        elif type == "couple":
            track = CoupleTrack(self.root, row, column, self.num_tracks, self.controller, self.open_editor_callback)

        self.tracks[track.uuid] = track
        print(self.occupied_pos)

    def save_tracks(self):
        self.tracks_status = {}
        for track in self.tracks.values():
            self.tracks_status[track.get_name()] = track.to_dict()
        
        return self.tracks_status

    def get_untitled_path(self):
        matching_files = [file for file in os.listdir("projects") if "untitled" in file]
        if len(matching_files) > 0:
            file_name = f"projects/untitled_{len(matching_files)}.pkl"
        else:
            file_name = "projects/untitled.pkl"
        return os.path.abspath(file_name)
        
    def save_as(self):

        file_path = filedialog.asksaveasfilename(
            title="Save As",
            defaultextension=".pkl",
            filetypes=[("ServoSync Files", "*.pkl"), ("All files", "*.*")]
        )
        self.save_path = os.path.abspath(file_path)
        self.save()
        return
        
    def save(self):
        
        if not self.save_path:
            self.save_path = self.get_untitled_path()
        
        save_dict = {"song_file_path": self.song_path,
                     "tracks": self.save_tracks(),
                     "tape": self.record_tape, 
                     "frame_rate": self.frame_rate,
                     "save_path": self.save_path,
                     "occupied_pos": self.occupied_pos,
                     }
        
        with open(self.save_path, 'wb') as file:
            pickle.dump(save_dict, file)

    def open(self):
        project_path = filedialog.askopenfilename()
        self.load_project(project_path=project_path)

    def play_pause_callback(self):
        if not self.song_path:
            self.not_loaded_error()
            return
        
        if not self.playing:
            self.playing = True
            self.player.play()
            self.recorder_thread = threading.Thread(target=self.recorder_thread_callback)
            self.recorder_thread.start()
            self.play_btn.configure(image=self.icons.pause_icon)

        else:
            self.playing = False
            if self.rec:
                self.rec = False
                self.rec_btn.configure(image=self.icons.rec_start_icon)
            self.player.pause()
            self.play_btn.configure(image=self.icons.play_icon)

    def stop_callback(self):
        self.RC = 0
        if not self.song_path:
            self.not_loaded_error()
            return

        self.playing = False
        if self.rec:
            self.rec = False
            self.rec_btn.configure(image=self.icons.rec_start_icon)
        self.play_btn.configure(image=self.icons.play_icon)
        self.player.stop()
    
    def rec_callback(self):
        if not self.song_path:
            self.not_loaded_error()
            return
        
        if not self.playing: 
            if self.rec:
                self.rec = False
                self.stop_callback()
                self.rec_btn.configure(image=self.icons.rec_start_icon)
            else:
                self.rec = True
                self.play_pause_callback()
                self.rec_btn.configure(image=self.icons.rec_stop_icon)

    def get_rec_tracks_status(self):
        rec_tracks = {}
        for track in self.tracks.values():
            if track.record:
                rec_tracks[track.uuid] = track.get_value()
        return rec_tracks

    def recorder_thread_callback(self):

        is_a_recording = self.rec

        while self.playing:

            it = time.time()
            
            if self.rec:
                status = self.get_rec_tracks_status()
                if not self.record_tape[self.RC]:
                    self.record_tape[self.RC] = status
                else:
                    self.record_tape[self.RC] = {**self.record_tape[self.RC], **status}
            
            else:
                for uuid, value in self.record_tape[self.RC].items():
                    self.tracks[uuid].move(value)
            
            self.RC += 1
            dt = time.time()-it
            time.sleep(self.frame_rate-dt)

        if is_a_recording:
            self.save()

    def load_project(self, project_path):

        with open(project_path, 'rb') as file:
            project_dict = pickle.load(file)

        # Name of window
        file_name = os.path.basename(project_path)
        self.root.title(f"Servo Sync - {file_name}")

        # Loading Song
        self.load_audio_file(project_dict["song_file_path"])

        # Other Variables
        self.record_tape = project_dict["tape"]
        self.frame_rate = project_dict["frame_rate"]
        self.save_path = project_dict["save_path"]
        self.occupied_pos = project_dict["occupied_pos"]

        # Tracks
        self.num_tracks = len(project_dict["tracks"])
        for i, track in project_dict["tracks"].items():
            uuid = track["uuid"]
            typ = track["type"]

            if typ == "BUTTON":
                self.tracks[uuid] = ButtonTrack(self.root, track["row"], track["column"], 0, self.controller, self.open_editor_callback)
            elif typ == "FADER":
                self.tracks[uuid] = FaderTrack(self.root, track["row"], track["column"], 0, self.controller, self.open_editor_callback)
            elif typ == "PANTILT":
                self.tracks[uuid] = PanTiltTrack(self.root, track["row"], track["column"], 0, self.controller, self.open_editor_callback)
            elif typ == "COUPLE":
                self.tracks[uuid] = CoupleTrack(self.root, track["row"], track["column"], 0, self.controller, self.open_editor_callback)

            self.tracks[uuid].load_track(track_dict=track)
        
    def open_editor_callback(self, track_uuid, index:int=None):
        self.editor = Editor(self.root, self.row+3, 
                             column=self.column, 
                             columnspan=self.COLUMNS, 
                             track_name=self.tracks[track_uuid].get_name(),
                             update_callback = self.update_edit_track)
        
        self.editor.load_editor(self.record_tape, track_uuid, index)
    
    def is_editor_open(self):
        if not self.editor:
            return False
        
        return self.editor.is_open

    def update_edit_track(self):

        uuid = self.editor.track_uuid
        new_tape = self.editor.tape

        idx = self.editor.index
        if idx is not None:
            for i in range(len(self.record_tape)):

                if uuid in self.record_tape[i]:
                    self.record_tape[i][uuid][idx] = new_tape[i][1]
                else:
                    a = [0, 0]
                    a[idx] = new_tape[i][1]
                    self.record_tape[i][uuid] = a
        else:
            for i in range(len(self.record_tape)):
                self.record_tape[i][uuid] = new_tape[i][1]
    
    def popup_exit(self):
        self.popup = CTkToplevel(self.root)
        self.popup.title("Save")

        width, height = 500, 100  # Set the height of the popup window

        # Calculate the x and y coordinates to center the popup
        x = (self.root.winfo_screenwidth() - width) // 2
        y = (self.root.winfo_screenheight() - height) // 2

        # Set the geometry of the popup window
        self.popup.geometry(f'{width}x{height}+{x}+{y}')
        
        # Add widgets to the popup frame
        label = CTkLabel(self.popup, text="Do you want to save the changes before closing?")
        label.grid(row=0, column=0, columnspan=3, padx=10, pady=10)

        yes_btn = CTkButton(self.popup, text="Save", fg_color=BUTTON_COLOR, hover_color=BUTTON_HOVER_COLOR, command=lambda: self.exit_callback("Y"))
        yes_btn.grid(row=1, column=2, padx=10, pady=10)

        no_btn = CTkButton(self.popup, text="Don't Save", fg_color=BUTTON_COLOR, hover_color=BUTTON_HOVER_COLOR, command=lambda: self.exit_callback("N"))
        no_btn.grid(row=1, column=1, padx=10, pady=10)

        cancel_btn = CTkButton(self.popup, text="Cancel", fg_color=BUTTON_COLOR, hover_color=BUTTON_HOVER_COLOR, command=lambda: self.exit_callback("C"))
        cancel_btn.grid(row=1, column=0, padx=10, pady=10)

    def exit_callback(self, value):

        if value == "Y":
            if "untitled" not in self.save_path:
                self.save()
            else:
                self.save_as()

        self.popup.destroy()

        if value == "N" or value == "Y":
            self.root.destroy()

    def load_preset_from_file(self, project_path):

        with open(project_path, 'rb') as file:
            project_dict = pickle.load(file)

        # Tracks
        self.num_tracks = len(project_dict["tracks"])
        for i, track in project_dict["tracks"].items():
            uuid = track["uuid"]
            typ = track["type"]

            if typ == "BUTTON":
                self.tracks[uuid] = ButtonTrack(self.root, track["row"], track["column"], 0, self.controller, self.open_editor_callback)
            elif typ == "FADER":
                self.tracks[uuid] = FaderTrack(self.root, track["row"], track["column"], 0, self.controller, self.open_editor_callback)
            elif typ == "PANTILT":
                self.tracks[uuid] = PanTiltTrack(self.root, track["row"], track["column"], 0, self.controller, self.open_editor_callback)
            elif typ == "COUPLE":
                self.tracks[uuid] = CoupleTrack(self.root, track["row"], track["column"], 0, self.controller, self.open_editor_callback)

            self.tracks[uuid].load_track(track_dict=track)

if __name__ == "__main__":
    pa = ProjectApp()