import tkinter as tk
from tkinter import ttk, filedialog, messagebox, Menu
import pygame
import threading
import time
import os
import uuid
import pickle

from audioPlayer import AudioPlayer
from tkinter import PhotoImage, Menu
from datetime import datetime
from PIL import Image, ImageTk

from pyfirmata import Arduino, SERVO


class Servo:
    def __init__(self, pin, board) -> None:
        self.pin = pin
        self.servo = board.get_pin('d:{}:s'.format(self.pin))
        self.name = f"Servo_{pin}"
    
    def set_angle(self, angle):
        self.servo.write(angle)


class Controller:
    def __init__(self) -> None:
        
        # Connecting Arduinio
        self.connect_to_arduino()

        # Connecting Servos
        self.servos_init()

    def servos_init(self):
        self.servos = [None for i in range(8)]
        self.available_pins = list(range(8, 14))

        if self.connected:
            for i in self.available_pins:
                self.servos.append(Servo(i, self.board))

    def connect_to_arduino(self, max_retrials=5):
        print("Conntecting to Arduino Board:")
        for i in range(max_retrials):
            try:
                self.port = "/dev/cu.usbmodem14101" 
                self.board = Arduino(self.port)
                self.connected = True
                print(f"Trial {i+1} Succeded!")
                break
            except: 
                self.connected = False
                self.port, self.board = None, None
                print(f"Trial {i+1} Failed")
            time.sleep(1)

    def move(self, servo_pin, angle):
        self.servos[servo_pin].set_angle(angle)

    def get_servos_names(self):
        return [s.name for s in self.servos if s is not None]


class TrackTimeline:
    def __init__(self, frame, row, column, width = 900.0, height = 100.0, rowspan: int = None, columnspan: int = None):
        self.frame = frame
        self.row = row
        self.column = column
        self.rowspan = rowspan
        self.columnspan = columnspan
        self.RC = 0

        # Inizializzazione della variabile da tracciare
        self.variable_values = []  # Use a list to store multiple keyframes
        self.selected_keyframe = None  # To keep track of the selected keyframe
        self.drag_data = None  # To store data during dragging

        self.width = width
        self.height = height

        self.timeline_canvas = None
        self.delete_all_keyframes()
        
        # Creazione di un keyframe iniziale
        self.add_keyframe_at_position(0, 0.5)
        self.add_keyframe_at_position(1, 0.5)

        # Aggiorna la linea di interpolazione
        self.update_interpolation_line()

    def draw_time_tracker(self, normalized_x):

        real_x = normalized_x * self.width
        self.time_tracker = self.timeline_canvas.create_line(real_x, 0, real_x, self.height, fill="black", width=1)
    
    def update_time_tracker(self, new_x, window_size, page):
        self.RC = new_x
        self.timeline_canvas.delete(self.time_tracker)

        min_v = window_size * page
        max_v = min_v + window_size
        if new_x >= min_v and new_x <= max_v:
            normalized_x = new_x - min_v
            self.draw_time_tracker(normalized_x / window_size)

    def handle_click(self, event):
        # Cerca un keyframe cliccato
        item = self.timeline_canvas.find_withtag(tk.CURRENT)

        if item:
            # Se un keyframe è cliccato, inizia il trascinamento
            self.selected_keyframe = item[0]
            self.timeline_canvas.itemconfig(self.selected_keyframe, outline="red")

            # Memorizza la posizione del mouse durante il clic
            self.drag_data = {'x': event.x, 'y': event.y}
        else:
            # Se è cliccato uno spazio vuoto, aggiungi un nuovo keyframe
            self.add_keyframe(event)
    
    def handle_drag(self, event):
        # Se un keyframe è selezionato, trascinalo
        if self.selected_keyframe is not None:
            delta_x = event.x - self.drag_data['x']
            delta_y = event.y - self.drag_data['y']
            self.timeline_canvas.move(self.selected_keyframe, delta_x, delta_y)
            self.drag_data['x'] = event.x
            self.drag_data['y'] = event.y

            # Aggiorna il valore della variabile in base alla posizione del keyframe
            self.update_variable_value()

            # Aggiorna la linea di interpolazione
            self.update_interpolation_line()

    def handle_release(self, event):
        # Se un keyframe è stato rilasciato, termina il trascinamento
        if self.selected_keyframe is not None:
            self.timeline_canvas.itemconfig(self.selected_keyframe, outline="black")
            self.selected_keyframe = None

    def add_keyframe(self, event):
        # Calcola la posizione normalizzata in base all'evento di clic
        normalized_pos_x = event.x / self.width
        normalized_pos_y = event.y / self.height

        # Aggiungi un nuovo keyframe alla posizione cliccata
        self.add_keyframe_at_position(normalized_pos_x, normalized_pos_y)

        # Aggiorna la linea di interpolazione
        self.update_interpolation_line()

    def add_keyframe_at_position(self, normalized_pos_x, normalized_pos_y):
        # Aggiungi un keyframe cliccabile
        keyframe = self.timeline_canvas.create_oval(
            normalized_pos_x * self.width - 6, normalized_pos_y * self.height - 6,
            normalized_pos_x * self.width + 6, normalized_pos_y * self.height + 6,
            fill="red", outline="black", tags="keyframe"
        )

        # Memorizza la posizione normalizzata nel dizionario
        self.variable_values.append((normalized_pos_x, normalized_pos_y))

    def update_variable_value(self):
        # Aggiorna il valore della variabile in base alle posizioni dei keyframes sulla timeline
        self.variable_values = []

        keyframe_tags = self.timeline_canvas.find_withtag("keyframe")
        for i, keyframe_tag in enumerate(keyframe_tags):
            keyframe_pos = self.timeline_canvas.coords(keyframe_tag)
            normalized_pos_x = keyframe_pos[0] / self.width
            normalized_pos_y = keyframe_pos[1] / self.height
            self.variable_values.append((normalized_pos_x, normalized_pos_y))

    def update_interpolation_line(self):
        # Calcola i punti intermedi tra i keyframe e aggiorna la linea di interpolazione
        interpolation_points = []

        self.sorted_keyframes = sorted(self.variable_values, key=lambda k: k[0])

        for i in range(len(self.sorted_keyframes) - 1):
            x1, y1 = self.sorted_keyframes[i]
            x2, y2 = self.sorted_keyframes[i + 1]

            for t in range(0, 101, 10):  # 0, 10, ..., 100
                t /= self.height
                x = x1 + t * (x2 - x1)
                y = y1 + t * (y2 - y1)
                interpolation_points.extend([x * self.width, y * self.height])

        # Aggiorna la linea di interpolazione
        self.timeline_canvas.coords(self.line, *interpolation_points)

    def add_keyframe_from_gui(self, normalized_pos_x, normalized_pos_y):

        normalized_pos_y = 1 - normalized_pos_y

        if normalized_pos_y > 0.5:
            y = normalized_pos_y - 0.05
        else:
            y = normalized_pos_y + 0.05
        # Aggiungi un nuovo keyframe alla posizione cliccata
        self.add_keyframe_at_position(normalized_pos_x, y)

    def delete_all_keyframes(self):
        if self.timeline_canvas:
            self.timeline_canvas.delete(self.line)

        self.variable_values = []
        self.timeline_canvas = tk.Canvas(self.frame, width=self.width, height=self.height, background="white")
        self.timeline_canvas.grid(row=self.row, column=self.column, rowspan=self.rowspan, columnspan=self.columnspan, padx=5, pady=10)
  
        # Aggiungi la linea di tracciamento
        self.line = self.timeline_canvas.create_line(0, 50, self.width, 50, width=2, fill="blue")

        # Bind the canvas click and drag events
        self.timeline_canvas.bind("<Button-1>", self.handle_click)
        self.timeline_canvas.bind("<B1-Motion>", self.handle_drag)
        self.timeline_canvas.bind("<ButtonRelease-1>", self.handle_release)

        # Time Tracker
        self.draw_time_tracker(0)


class TextVariable:
    def __init__(self, root, row:int, column:int, default_text:str, rowspan:int=1, columnspan:int=1, padx:int=5, pady:int=10, sticky:str=None, width:int=None, height:int=None):
        self.text = None
        self.entry_var = tk.StringVar()
        self.entry_var.trace_add("write", self.on_text_change)

        self.entry = ttk.Entry(root, textvariable=self.entry_var, width=width, height=height)
        self.entry.insert(0, str(default_text))
        self.entry.grid(row=row, column=column, rowspan=rowspan, columnspan=columnspan, padx=padx, pady=pady, sticky=sticky)

    def on_text_change(self, *args):
        try:
            self.text = int(self.entry_var.get())
        except ValueError:
            self.text = self.entry_var.get()
    
    def get(self):
        return self.text
    
    def set(self, text):
        self.entry.delete(0, tk.END)
        self.entry.insert(0, str(text))


class ButtonTrack:
    def __init__(self, root, row:int, column:int, track_num: int, controller, open_editor_callback) -> None:
        self.row, self.column = row, column
        self.uuid = uuid.uuid4()
        self.type = "BUTTON"

        self.controller = controller

        self.frame = tk.Frame(root, padx=10, pady=10, borderwidth=0.5, relief="solid")
        self.frame.grid(row = self.row, column=self.column)

        # Track Name
        self.track_name = TextVariable(root=self.frame, row=self.row, column=self.column, default_text=f"Track {track_num}", 
                                       columnspan=3, padx=5, sticky="w", width=14)

        # Editor Button
        self.editor_btn = tk.Button(self.frame, text="Editor", command= lambda: open_editor_callback(self.uuid))
        self.editor_btn.grid(row = self.row, column=self.column+2, padx=5, pady=10)

        # Record Button
        self.record_btn = tk.Button(self.frame, text="R", command=self.record_btn_callback)
        self.record_btn.grid(row = self.row+1, column=self.column, padx=5, pady=10)
        self.record = False

        # Active Button
        self.active_btn = tk.Button(self.frame, text="A", fg = "green", command=self.active_btn_callback)
        self.active_btn.grid(row = self.row+1, column=self.column+1, padx=5, pady=10)
        self.active = True

        # Servo Selector
        self.available_servos = self.controller.get_servos_names()
        self.servo_selector = ttk.Combobox(self.frame, values=self.available_servos, width=7)
        self.servo_selector.grid(row = self.row+1, column=self.column+2, padx=5, pady=10)
        self.servo_selector.bind("<<ComboboxSelected>>", self.select_servo)
        self.selected_servo_pin = None
        self.selected_servo_name = None

        # Rest - Peak Values
        self.rest_label = tk.Label(self.frame, text="Rest", width=6)
        self.rest_label.grid(row = self.row+2, column=self.column, padx=10, pady=1)
        self.peak_label = tk.Label(self.frame, text="Peak", width=6)
        self.peak_label.grid(row = self.row+2, column=self.column+1, padx=10, pady=1)

        self.rest_box = TextVariable(root=self.frame, row=self.row+3, column=self.column, default_text="0", padx=5, width=3)
        self.peak_box = TextVariable(root=self.frame, row=self.row+3, column=self.column+1, default_text="180", padx=5, width=3)

        # Button
        self.btn = tk.Button(self.frame, text="PRESS", fg = "green", height=3, width=8)
        self.btn.grid(row = self.row+2, column=self.column+2, rowspan=2, columnspan=3, padx=10, pady=1)
        self.btn.bind("<ButtonPress>", lambda event: self.btn_press_callback())
        self.btn.bind("<ButtonRelease>", lambda event: self.btn_release_callback())

        self.btn_value = int(self.rest_box.get())
        self.is_pressed = False

    def update_available_servos(self, servos_list):
        self.available_servos = servos_list

    def select_servo(self, event):
        name = self.servo_selector.get()
        self.selected_servo_name = name
        self.selected_servo_pin = int(name.split("_")[1])
        
    def get_name(self):
        return self.track_name.get()
    
    def get_value(self):
        return self.btn_value
    
    def btn_press_callback(self):
        self.is_pressed = True
        self.btn_value = int(self.peak_box.get())
        # Moving Servo
        self.move(self.btn_value)
    
    def btn_release_callback(self):
        if self.is_pressed:
            self.is_pressed = False
            self.btn_value = int(self.rest_box.get())
            self.move(self.btn_value)

    def move(self, angle):
        if self.controller.connected and self.active and self.selected_servo_pin:
            self.controller.move(servo_pin=self.selected_servo_pin, angle=angle)
        
    def record_btn_callback(self):
        if self.record:
            self.record_btn.config(bg="red", fg="black")
            self.record = False
        else:
            self.record_btn.config(bg="grey", fg="red")
            self.record = True
    
    def active_btn_callback(self):
        if self.active:
            self.active_btn.config(bg="green", fg="black")
            self.active = False
        else:
            self.active_btn.config(bg="gray", fg="green")
            self.active = True
    
    def get_current_value(self):
        return self.btn_value

    def to_dict(self):
        return {"row": self.row,
                "column": self.column, 
                "type": self.type,
                "uuid": self.uuid, 
                "track_name": self.get_name(), 
                "record": self.record, 
                "active": self.active, 
                "selected_servo_pin": self.selected_servo_pin,  
                "selected_servo_name": self.selected_servo_name}

    def load_track(self, track_dict):
        self.uuid = track_dict["uuid"]

        self.record = not track_dict["record"]
        self.record_btn_callback()

        self.active = not track_dict["active"]
        self.active_btn_callback()

        self.selected_servo_name = track_dict["selected_servo_name"]
        self.track_name.set(track_dict["track_name"])

        self.selected_servo_pin = track_dict["selected_servo_pin"]
        if self.selected_servo_pin:
            self.servo_selector.set(f"Servo {self.selected_servo_pin}")


class FaderTrack:
    def __init__(self, root, row:int, column:int, track_num, controller, open_editor_callback) -> None:
        self.row, self.column = row, column
        self.uuid = uuid.uuid4()
        self.type = "FADER"

        self.frame = tk.Frame(root, padx=10, pady=24, borderwidth=0.5, relief="solid")
        self.frame.grid(row = self.row, column=self.column)
        

        self.controller = controller

        # Track Name
        self.track_name = TextVariable(root=self.frame, row=self.row, column=self.column, default_text=f"Track {track_num}", 
                                       columnspan=3, padx=5, sticky="w", width=14)

        # Editor Button
        self.editor_btn = tk.Button(self.frame, text="Editor", command= lambda: open_editor_callback(self.uuid))
        self.editor_btn.grid(row = self.row, column=self.column+2, padx=5, pady=10)

        # Record Button
        self.record_btn = tk.Button(self.frame, text="R", command=self.record_btn_callback)
        self.record_btn.grid(row = self.row+1, column=self.column, padx=5, pady=10)
        self.record = False

        # Active Button
        self.active_btn = tk.Button(self.frame, text="A", fg = "green", command=self.active_btn_callback)
        self.active_btn.grid(row = self.row+1, column=self.column+1, padx=5, pady=10)
        self.active = True

        # Servo Selector
        self.available_servos = self.controller.get_servos_names()
        self.servo_selector = ttk.Combobox(self.frame, values=self.available_servos, width=7)
        self.servo_selector.grid(row = self.row+1, column=self.column+2, padx=5, pady=10)
        self.servo_selector.bind("<<ComboboxSelected>>", self.select_servo)
        self.selected_servo_pin = None
        self.selected_servo_name = None

        # Fader
        self.fader_label = tk.Label(self.frame, text="90", width=3)
        self.fader_label.grid(row = self.row+2, column=self.column+2, padx=5, pady=10)

        self.fader = ttk.Scale(self.frame, from_=0, to=180, orient=tk.HORIZONTAL, length=180, command=self.fader_callback)
        self.fader.grid(row = self.row+2, column=self.column, columnspan=2, padx=5, pady=10)
        self.fader.set(90) 
        self.fader_value = 90


    def update_available_servos(self, servos_list):
        self.available_servos = servos_list

    def select_servo(self, event):
        name = self.servo_selector.get()
        self.selected_servo_name = name
        self.selected_servo_pin = int(name.split("_")[1])

    def fader_callback(self, value):
        angle = int(float(value))
        self.move(angle)

        self.fader_value = angle
        self.fader_label.config(text=str(int(float(value))))
        
    def move(self, angle):
        if self.controller.connected and self.active and self.selected_servo_pin:
            self.controller.move(servo_pin=self.selected_servo_pin, angle=angle)

    def record_btn_callback(self):
        if self.record:
            self.record_btn.config(bg="red", fg="black")
            self.record = False
        else:
            self.record_btn.config(bg="grey", fg="red")
            self.record = True
    
    def active_btn_callback(self):
        if self.active:
            self.active_btn.config(bg="green", fg="black")
            self.active = False
        else:
            self.active_btn.config(bg="gray", fg="green")
            self.active = True
    
    def get_name(self):
        return self.track_name.get()

    def get_value(self):
        return self.fader_value
    
    def to_dict(self):
        return {"row": self.row,
                "column": self.column, 
                "type": self.type,
                "uuid": self.uuid, 
                "track_name": self.get_name(), 
                "record": self.record, 
                "active": self.active, 
                "selected_servo_pin": self.selected_servo_pin,  
                "selected_servo_name": self.selected_servo_name}

    def load_track(self, track_dict):
        self.uuid = track_dict["uuid"]

        self.record = not track_dict["record"]
        self.record_btn_callback()

        self.active = not track_dict["active"]
        self.active_btn_callback()

        self.selected_servo_name = track_dict["selected_servo_name"]
        self.track_name.set(track_dict["track_name"])

        self.selected_servo_pin = track_dict["selected_servo_pin"]
        if self.selected_servo_pin:
            self.servo_selector.set(f"Servo {self.selected_servo_pin}")


class Icons:
    def __init__(self) -> None:
        self.play_icon = self.get_icon(path="img/play_icon.png")
        self.pause_icon = self.get_icon(path="img/pause_icon.png")
        self.stop_icon = self.get_icon(path="img/stop_icon.png")
        self.rec_start_icon = self.get_icon(path="img/rec_start.png")
        self.rec_stop_icon = self.get_icon(path="img/rec_stop.png")

    def get_icon(self, path, height:int=60, width:int=60):
        icon_image = Image.open(path)
        resized_icon = icon_image.resize((height, width))
        return ImageTk.PhotoImage(resized_icon)


class GUI:

    def __init__(self, row:int = 0, column:int = 0):

        self.root = tk.Tk()
        self.menubar = Menu(self.root)
        self.root.config(menu=self.menubar)

        self.controller = Controller()
        
        self.row, self.column, self.song_path = row, column, None
        self.COLUMNS = 4

        self.frame = tk.Frame(self.root, padx=10, pady=10)
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

        # Select Song Button
        self.select_song_btn = tk.Button(self.frame, text="Select Song", command=self.select_audio_file)
        self.select_song_btn.grid(row=self.row+1, column=self.column, padx=5, pady=10, sticky="w")

        # Song Title
        self.song_title_label = tk.Label(self.frame, text="Choose a Song", width=80, font=("Arial", 16))
        self.song_title_label.grid(row=self.row, column=self.column+1, pady=1)

        # Timestamp
        self.timestamp = " "
        self.timestamp_label = tk.Label(self.frame, text=self.timestamp, width=10, font=("Arial", 50))
        self.timestamp_label.grid(row=self.row+1, column=self.column+1, pady=1)

        # Play - Pause - Stop
        self.play_btn = tk.Button(self.frame, text="", image=self.icons.play_icon, command=self.play_pause_callback)
        self.play_btn.grid(row=self.row+1, column=self.column+5, padx=10)
        self.stop_btn = tk.Button(self.frame, text="", image=self.icons.stop_icon, command=self.stop_callback)
        self.stop_btn.grid(row=self.row+1, column=self.column+6, padx=10)
        self.rec_btn = tk.Button(self.frame, text="", image=self.icons.rec_start_icon, command=self.rec_callback)
        self.rec_btn.grid(row=self.row+1, column=self.column+4, padx=10)
        self.rec = False

        self.track_timeline = ttk.Scale(self.frame, from_=0, to=self.player.get_length_seconds(), orient="horizontal", length=950)
        self.track_timeline.grid(row=self.row+2, column=self.column+1, columnspan=2, pady=10)
        
        self.update_status_thread = threading.Thread(target=self.update_status)
        self.update_status_thread.start()

        self.recorder_thread = None
        self.record_tape = None
        self.frame_rate = 0.1
        self.RC = 0
        self.editor = None

        #self.load_project("projects/Jingle Bells.pkl")

        self.root.mainloop()

    def menubar_init(self):
        self.file_menu = Menu(self.menubar)
        self.file_menu.add_command(label='Save', command=self.save)
        self.file_menu.add_command(label='Save As', command=self.save_as)
        self.file_menu.add_command(label='Open', command=self.open)

        self.menubar.add_cascade(label="File", menu=self.file_menu)

        self.track_menu = Menu(self.menubar)
        self.track_menu.add_command(label='Add Fader Track', command=lambda: self.add_track(type="fader"))
        self.track_menu.add_command(label='Add Button Track', command=lambda: self.add_track(type="button"))
        self.menubar.add_cascade(label="Track", menu=self.track_menu)

        self.controller_menu = Menu(self.menubar)
        self.controller_menu.add_command(label='Try Reconnect', command= self.reconnect_controller)
        self.menubar.add_cascade(label="Controller", menu=self.controller_menu)

    def reconnect_controller(self):

        self.controller.connect_to_arduino()
        if self.controller.connected: 
            for servo in self.tracks.values():
                servo.update_available_servos(self.controller.get_servos_names())
        
    def update_status(self):
        while True:
            # Timestamp
            self.timestamp_label.config(text=self.player.get_timestamp())

            # Track Timeline
            self.track_timeline.set(self.player.time)

            try:
                if self.editor.is_open and self.playing:
                    window_size = self.editor.window_size
                    page = self.editor.page_num

                    min_v = window_size * page
                    max_v = min_v + window_size
                    if self.RC >= max_v:
                        self.editor.get_next_page()
                    elif self.RC <= min_v:
                        self.editor.get_prev_page()
                    self.editor.timeline.update_time_tracker(new_x=self.RC, window_size=window_size, page=page)

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
            self.song_title_label.config(text=song_path.split("/")[-1])

            # Load file on player
            self.player.load_file(self.song_path)
            self.track_timeline.configure(to=self.player.get_length_seconds())

            # Add keyframes to record tape
            num_keyframes = int(round(self.player.get_length_seconds() / self.frame_rate, 0))
            self.record_tape = [{}] * num_keyframes

    def not_loaded_error(self):
        messagebox.showerror("No Music to Play", "Please, select an audio file you want to play")

    def add_track(self, type: str):
        

        row = (self.num_tracks // self.COLUMNS) + 3 
        column = (self.num_tracks % self.COLUMNS)
        self.num_tracks += 1

        if type == "fader":
            track = FaderTrack(self.root, row, column, self.num_tracks, self.controller, self.open_editor_callback)
        elif type == "button":
            track = ButtonTrack(self.root, row, column, self.num_tracks, self.controller, self.open_editor_callback)
        self.tracks[track.uuid] = track

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
            self.play_btn.config(image=self.icons.pause_icon)

        else:
            self.playing = False
            if self.rec:
                self.rec = False
                self.rec_btn.config(image=self.icons.rec_start_icon)
            self.player.pause()
            self.play_btn.config(image=self.icons.play_icon)

    def stop_callback(self):
        self.RC = 0
        if not self.song_path:
            self.not_loaded_error()
            return

        self.playing = False
        if self.rec:
            self.rec = False
            self.rec_btn.config(image=self.icons.rec_start_icon)
        self.play_btn.config(image=self.icons.play_icon)
        self.player.stop()
    
    def rec_callback(self):
        if not self.song_path:
            self.not_loaded_error()
            return
        
        if not self.playing: 
            if self.rec:
                self.rec = False
                self.stop_callback()
                self.rec_btn.config(image=self.icons.rec_start_icon)
            else:
                self.rec = True
                self.play_pause_callback()
                self.rec_btn.config(image=self.icons.rec_stop_icon)

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

        # Loading Song
        self.load_audio_file(project_dict["song_file_path"])

        # Other Variables
        self.record_tape = project_dict["tape"]
        self.frame_rate = project_dict["frame_rate"]
        self.save_path = project_dict["save_path"]

        # Tracks
        self.num_tracks = len(project_dict["tracks"])
        for i, track in project_dict["tracks"].items():
            uuid = track["uuid"]
            typ = track["type"]

            if typ == "BUTTON":
                self.tracks[uuid] = ButtonTrack(self.root, track["row"], track["column"], 0, self.controller, self.open_editor_callback)
            elif typ == "FADER":
                self.tracks[uuid] = FaderTrack(self.root, track["row"], track["column"], 0, self.controller, self.open_editor_callback)

            self.tracks[uuid].load_track(track_dict=track)
        
    def open_editor_callback(self, track_uuid):
        self.editor = Editor(self.root, self.row+3, 
                             column=self.column, 
                             columnspan=self.COLUMNS, 
                             track_name=self.tracks[track_uuid].get_name())
        self.editor.load_editor(self.record_tape, track_uuid)
    
    def is_editor_open(self):
        if not self.editor:
            return False
        
        return self.editor.is_open


class Editor: 
    def __init__(self, root, row, column, columnspan, track_name) -> None:
        self.root, self.row, self.column = root, row, column

        self.window_size = 250
        self.is_open = True

        self.editor_frame = tk.Frame(self.root, padx=1, pady=1, borderwidth=0.5, relief="solid")
        self.editor_frame.grid(row = self.row, column=self.column, rowspan=5, columnspan=columnspan)

        self.timeline = TrackTimeline(self.editor_frame, self.row+2, self.column, width=1300, height=400, columnspan=20)
        self.tape = []

         # Exit Button
        self.exit_btn = tk.Button(self.editor_frame, text="X", command = self.close_editor)
        self.exit_btn.grid(row=self.row, column=self.column, padx=1, pady=1)

        # Track Name Label
        self.track_name_label = tk.Label(self.editor_frame, text=f"{track_name} Editor", font=("Arial", 20), width=50)
        self.track_name_label.grid(row = self.row, column=self.column+8, padx=1, pady=1, columnspan=2)

        # Zoom In - Out
        self.zoom_label = tk.Label(self.editor_frame, text="Zoom", width=4)
        self.zoom_label.grid(row = self.row, column=self.column+1, padx=1, pady=1, columnspan=2)
        self.zin_btn = tk.Button(self.editor_frame, text="+", command=lambda: self.zoom_callback("-"))
        self.zin_btn.grid(row = self.row+1, column=self.column+1, padx=1, pady=1)
        self.zout_btn = tk.Button(self.editor_frame, text="-", command=lambda: self.zoom_callback("+"))
        self.zout_btn.grid(row = self.row+1, column=self.column+2, padx=1, pady=1)

        # Page
        self.page_num, self.tot_pages_num = 0, 0
        self.page_label = tk.Label(self.editor_frame, text="", width=15)
        self.page_label.grid(row = self.row, column=self.column+18, padx=1, pady=1, columnspan=2)
        self.update_page_label()
        self.reward_btn = tk.Button(self.editor_frame, text="<<", command= self.get_prev_page)
        self.reward_btn.grid(row = self.row+1, column=self.column+18, padx=1, pady=1)
        self.forward_btn = tk.Button(self.editor_frame, text=">>", command= self.get_next_page)
        self.forward_btn.grid(row = self.row+1, column=self.column+19, padx=1, pady=1)
        
    def zoom_callback(self, param):

        if param == "+":
            self.window_size += 50
        elif param == "-":
            self.window_size -= 50
        
        self.show()

    def load_editor(self, record_tape, track_uuid):
        for i, d in enumerate(record_tape):
            try:
                self.tape.append(d[track_uuid])
            except:
                self.tape.append(0)
        
        self.tot_pages_num = int(len(self.tape)/self.window_size) + 1
        self.show()
        
    def show(self, min_w=None, max_w=None):
        self.timeline.delete_all_keyframes()

        if not (min_w or max_w):
            min_w, max_w = self.get_window_range()

        for i, value in enumerate(self.tape[min_w:max_w]):
            x, y = i / self.window_size, value / 180
            self.timeline.add_keyframe_from_gui(x, y)
        
        self.timeline.update_interpolation_line()

    def get_next_page(self):
        if self.page_num < self.tot_pages_num:
            self.page_num += 1
            unit = self.page_num*self.window_size
            self.show(unit, unit+self.window_size)
            self.update_page_label()

    def get_prev_page(self):
        if self.page_num > 0:
            self.page_num -= 1
            unit = self.page_num*self.window_size
            self.show(unit, unit+self.window_size)
            self.update_page_label()

    def get_window_range(self):

        margin = self.window_size/2
        len_tape = len(self.tape)
        rc = self.timeline.RC

        self.tot_pages_num = int(len(self.tape) / self.window_size) + 1
        self.page_num = rc // self.window_size
        self.update_page_label()

        if rc < margin:
            return (0, self.window_size)
        elif (len_tape - rc) < margin:
            return (len_tape - self.window_size, len_tape)
        else:
            return int(rc-margin), int(rc+margin)
    
    def update_page_label(self):
        self.page_label.config(text=f"Page {self.page_num+1} / {self.tot_pages_num+1}")

    def close_editor(self):
        self.editor_frame.destroy()
        self.is_open = False



if __name__ == "__main__":

    gui = GUI()
    
