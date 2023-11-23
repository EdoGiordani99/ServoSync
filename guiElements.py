import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import pygame
import threading
import time
import os

from audioPlayer import AudioPlayer
from tkinter import PhotoImage, Menu
from datetime import datetime
from PIL import Image, ImageTk

def seconds_to_timestamp(seconds):
    # Calculate hours, minutes, and seconds
    hours, remainder = divmod(int(seconds), 3600)
    minutes, seconds = divmod(remainder, 60)
    timestamp = "{:02d}:{:02d}:{:02d}".format(hours, minutes, seconds)
    return timestamp


class TrackTimeline:
    def __init__(self, frame, row, column, rowspan: int = None, columnspan: int = None):
        self.frame = frame

        # Inizializzazione della variabile da tracciare
        self.variable_values = []  # Use a list to store multiple keyframes
        self.selected_keyframe = None  # To keep track of the selected keyframe
        self.drag_data = None  # To store data during dragging

        self.width = 900.0
        self.height = 100.0

        # Creazione di un Canvas per la timeline
        self.timeline_canvas = tk.Canvas(frame, width=self.width, height=self.height, background="white")
        self.timeline_canvas.grid(row=row, column=column, rowspan=rowspan, columnspan=columnspan, padx=5, pady=10)

        # Aggiungi la linea di tracciamento
        self.line = self.timeline_canvas.create_line(0, 50, self.width, 50, width=2, fill="blue")

        # Bind the canvas click and drag events
        self.timeline_canvas.bind("<Button-1>", self.handle_click)
        self.timeline_canvas.bind("<B1-Motion>", self.handle_drag)
        self.timeline_canvas.bind("<ButtonRelease-1>", self.handle_release)

        # Initial scale factor
        self.scale_factor = 1.0

        # Creazione di un keyframe iniziale
        self.add_keyframe_at_position(0, 0.5)
        self.add_keyframe_at_position(1, 0.5)
        # self.add_keyframe_at_position(0.8, 0.8)

        # Aggiorna la linea di interpolazione
        self.update_interpolation_line()

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


class ButtonTrack:
    def __init__(self, root, row:int, column:int, track_num: int) -> None:
        self.row, self.column = row, column

        self.frame = tk.Frame(root, padx=10, pady=10, borderwidth=0.5, relief="solid")
        self.frame.grid(row = self.row, column=self.column)

        # Track Name
        self.track_name = TextVariable(root=self.frame, row=self.row, column=self.column, default_text=f"Track {track_num}", 
                                       columnspan=3, padx=5, sticky="w", width=14)

        # Record Button
        self.record_btn = tk.Button(self.frame, text="R", command=self.record_btn_callback)
        self.record_btn.grid(row = self.row+1, column=self.column, padx=5, pady=10)
        self.record = False

        # Active Button
        self.active_btn = tk.Button(self.frame, text="A", fg = "green", command=self.active_btn_callback)
        self.active_btn.grid(row = self.row+1, column=self.column+1, padx=5, pady=10)
        self.active = True

        # Servo Selector
        self.available_servos = ["Servo 1"]
        self.servo_selector = ttk.Combobox(self.frame, values=self.available_servos, width=5)
        self.servo_selector.grid(row = self.row+1, column=self.column+2, padx=5, pady=10)
        self.servo_selector.bind("<<ComboboxSelected>>", self.select_servo)
        self.selected_servo = True

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

        # Timeline
        self.timeline = TrackTimeline(self.frame, row=self.row, column=self.column+5, rowspan=3)

    def update_available_servos(self, servos_list):
        self.available_servos = servos_list

    def select_servo(self, event):
        self.selected_servo = self.servo_selector.get()

    def btn_press_callback(self):
        self.is_pressed = True
        self.btn_value = int(self.peak_box.get())

    def btn_release_callback(self):
        if self.is_pressed:
            self.is_pressed = False
            self.btn_value = int(self.rest_box.get())

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
    

class FaderTrack:
    def __init__(self, root, row:int, column:int, track_num) -> None:
        self.row, self.column = row, column

        self.frame = tk.Frame(root, padx=10, pady=10, borderwidth=0.5, relief="solid")
        self.frame.grid(row = self.row, column=self.column)

        # Track Name
        self.track_name = TextVariable(root=self.frame, row=self.row, column=self.column, default_text=f"Track {track_num}", 
                                       columnspan=3, padx=5, sticky="w", width=14)

        # Record Button
        self.record_btn = tk.Button(self.frame, text="R", command=self.record_btn_callback)
        self.record_btn.grid(row = self.row+1, column=self.column, padx=5, pady=10)
        self.record = False

        # Active Button
        self.active_btn = tk.Button(self.frame, text="A", fg = "green", command=self.active_btn_callback)
        self.active_btn.grid(row = self.row+1, column=self.column+1, padx=5, pady=10)
        self.active = True

        # Servo Selector
        self.available_servos = ["Servo 1"]
        self.servo_selector = ttk.Combobox(self.frame, values=self.available_servos, width=5)
        self.servo_selector.grid(row = self.row+1, column=self.column+2, padx=5, pady=10)
        self.servo_selector.bind("<<ComboboxSelected>>", self.select_servo)
        self.selected_servo = True

        # Fader
        self.fader_label = tk.Label(self.frame, text="90", width=3)
        self.fader_label.grid(row = self.row+2, column=self.column+2, padx=5, pady=10)

        self.fader = ttk.Scale(self.frame, from_=0, to=180, orient=tk.HORIZONTAL, length=200, command=self.fader_callback)
        self.fader.grid(row = self.row+2, column=self.column, columnspan=2, padx=5, pady=10)
        self.fader.set(90) 
        self.fader_value = 90

        # Timeline
        self.timeline = TrackTimeline(self.frame, row=self.row, column=self.column+5, rowspan=3)

    def update_available_servos(self, servos_list):
        self.available_servos = servos_list

    def select_servo(self, event):
        self.selected_servo = self.servo_selector.get()

    def fader_callback(self, value):
        self.fader_value = int(float(value))
        self.fader_label.config(text=str(int(float(value))))

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
        return self.fader_value


class MusicPlayer:

    def __init__(self, root, row:int, column:int):

        self.row, self.column, self.file_path = row, column, None

        self.frame = tk.Frame(root, padx=10, pady=10)
        self.frame.grid(row = self.row, column=self.column)

        self.player = AudioPlayer()
        self.playing = False

        # Icons
        self.play_icon = self.get_icon(path="img/play_icon.png")
        self.pause_icon = self.get_icon(path="img/pause_icon.png")
        self.stop_icon = self.get_icon(path="img/stop_icon.png")
        
        # Select Song Button
        self.select_song_btn = tk.Button(self.frame, text="Select Song", command=self.select_file)
        self.select_song_btn.grid(row=self.row+1, column=self.column, padx=5, pady=10, sticky="w")

        # Song Title
        self.song_title_label = tk.Label(self.frame, text="Choose a Song", width=80, font=("Arial", 16))
        self.song_title_label.grid(row=self.row, column=self.column+1, pady=1)

        # Timestamp
        self.timestamp = " "
        self.timestamp_label = tk.Label(self.frame, text=self.timestamp, width=10, font=("Arial", 50))
        self.timestamp_label.grid(row=self.row+1, column=self.column+1, pady=1)

        # Play - Pause - Stop
        self.play_btn = tk.Button(self.frame, text="", image=self.play_icon, command=self.play_pause)
        self.play_btn.grid(row=self.row+1, column=self.column+2, padx=10)
        self.stop_btn = tk.Button(self.frame, text="", image=self.stop_icon, command=self.stop)
        self.stop_btn.grid(row=self.row+1, column=self.column+3, padx=10)

        self.track_timeline = ttk.Scale(self.frame, from_=0, to=self.player.get_length(), orient="horizontal", length=950)
        self.track_timeline.grid(row=self.row+2, column=self.column+1, pady=10)
        
        self.frame.after(100, self.update_status)

    def get_icon(self, path, height:int=60, width:int=60):
        icon_image = Image.open(path)
        resized_icon = icon_image.resize((height, width))
        return ImageTk.PhotoImage(resized_icon)

    def select_file(self):
        file_path = filedialog.askopenfilename(title="Select a music file",
                                               filetypes=[("All files", "*.*")])
        if file_path:
            self.file_path = os.path.abspath(file_path)
            self.song_title_label.config(text=file_path.split("/")[-1])

            # Load file on player
            self.player.load_file(self.file_path)
            self.track_timeline.configure(to=self.player.get_length())

    def play_pause(self):
        if not self.file_path:
            messagebox.showerror("No Music to Play", "Please, select an audio file you want to play")
            return

        if not self.playing:
            self.playing = True
            self.player.play()
            self.play_btn.config(image=self.pause_icon)
        else:
            self.playing = False
            self.player.pause()
            self.play_btn.config(image=self.play_icon)

    def stop(self):
        self.playing = False
        self.play_btn.config(image=self.play_icon)
        self.player.stop()

    def update_status(self):
        self.timestamp_label.config(text=seconds_to_timestamp(self.player.time))
        self.track_timeline.set(self.player.time)
        self.frame.after(1, self.update_status)



if __name__ == "__main__":
    root = tk.Tk()

    mp = MusicPlayer(root=root, row=0, column=0)

    tracks = []
    for i in range(5):
        i += 1
        tracks.append(FaderTrack(root, (i*2)+3-1, 0, i*2-1))
        tracks.append(ButtonTrack(root, (i*2)+3, 0, i*2-2))

    root.mainloop()