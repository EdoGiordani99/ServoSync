import tkinter as tk

from customtkinter import *
from tkinter import messagebox
from scipy.interpolate import interp1d

from scripts.colors import *
#from colors import *

def equidistant_points(original_points, M):
    x_values = [point[0] for point in original_points]
    y_values = [point[1] for point in original_points]

    # Create an interpolation function
    interp_func = interp1d(x_values, y_values, kind='linear', fill_value="extrapolate")

    # Determine the equidistant x-values
    x_min, x_max = min(x_values), max(x_values)
    equidistant_x_values = [x_min + i * (x_max - x_min) / (M - 1) for i in range(M)]

    # Evaluate the interpolation function at equidistant x-values
    equidistant_y_values = [interp_func(x) for x in equidistant_x_values]

    # Combine x and y values to get equidistant points
    equidistant_points = list(zip(equidistant_x_values, equidistant_y_values))

    return equidistant_points


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
        self.modified = False
        self.timeline_init()
        
        # Creazione di un keyframe iniziale
        self.add_keyframe_at_position(0, 0.5)
        self.add_keyframe_at_position(1, 0.5)

        # Aggiorna la linea di interpolazione
        self.update_interpolation_line()

    def delete_tracker(self):
        self.timeline_canvas.delete(self.time_tracker)
        
    def draw_time_tracker(self, normalized_x):
        x = normalized_x * self.width
        self.time_tracker = self.timeline_canvas.create_line(x, 0, x, self.height, fill="black", width=1)
    
    def update_time_tracker(self, new_x, min_v, max_v):
        self.RC = new_x
        self.delete_tracker()
            
        if new_x >= min_v and new_x <= max_v:
            normalized_x = (new_x - min_v) / (max_v - min_v)
            self.draw_time_tracker(normalized_x)

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
            self.modified = True
            delta_x = event.x - self.drag_data['x']
            delta_y = event.y - self.drag_data['y']
            self.timeline_canvas.move(self.selected_keyframe, delta_x, delta_y)
            #self.timeline_canvas.move(self.selected_keyframe, 0, delta_y)
            self.drag_data['x'] = event.x
            self.drag_data['y'] = event.y

            # Aggiorna il valore della variabile in base alla posizione del keyframe
            self.update_variable_value()

            # Aggiorna la linea di interpolazione
            self.update_interpolation_line()

    def handle_release(self, event):
        # Se un keyframe è stato rilasciato, termina il trascinamento
        if self.selected_keyframe is not None:
            self.timeline_canvas.itemconfig(self.selected_keyframe, outline=BUTTON_COLOR)
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
            fill=BUTTON_HOVER_COLOR, outline=BUTTON_COLOR, tags="keyframe"
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

        y = (normalized_pos_y + 0.05) * 0.90
                
        # Aggiungi un nuovo keyframe alla posizione cliccata
        self.add_keyframe_at_position(normalized_pos_x, y)

    def timeline_init(self):
        if self.timeline_canvas:
            self.timeline_canvas.delete(self.line)

        self.variable_values = []
        self.modified = False
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

    def get_all_keyframes(self):

        to_return = []
        dx = None
        
        for kf in self.sorted_keyframes:
            x, y = kf
            
            if not dx:
                if self.modified:
                    dx = 0 - x
                else:
                    dx = 0
            
            x = x + dx
            y = 1 - ((y/0.90)-0.05)
            
            to_return.append((x,y))

        return to_return


class KeyFrame:

    def __init__(self, real_x, real_y, original_length):

        self.real_x = real_x
        self.real_y = real_y
        self.original_length = original_length

        self.x = real_x / original_length
        self.y = round((real_y / 180), 3)


class Editor: 
    def __init__(self, root, row, column, columnspan, track_name, update_callback) -> None:
        self.root, self.row, self.column = root, row, column

        self.index = None
        self.tape = []
        self.track_uuid = None
        self.original_length = 1
        self.step = 0.01
        self.window_size = 0.1

        self.is_open = True
        self.update_callback = update_callback

        # Editor Frame
        self.editor_frame = CTkFrame(self.root)
        self.editor_frame.grid(row = self.row, column=self.column, rowspan=5, columnspan=columnspan, padx=5, pady=5)

        # Timeline
        self.timeline = TrackTimeline(self.editor_frame, self.row+2, self.column, width=1300, height=400, columnspan=6)
        
        # Exit Button
        self.exit_btn = CTkButton(self.editor_frame, text="X", fg_color="red", width=5, hover_color=BUTTON_HOVER_COLOR, command = self.close_editor)
        self.exit_btn.grid(row=self.row, column=self.column, padx=1, pady=1)

        # Track Name Label
        self.track_name = track_name
        self.track_name_label = CTkLabel(self.editor_frame, text=f"{track_name} Editor", font=("Arial", 20), width=50)
        self.track_name_label.grid(row = self.row, column=self.column+3, padx=1, pady=1, columnspan=1)

        # Zoom In - Out
        self.zoom_label = CTkLabel(self.editor_frame, text=f"Zoom: {int(self.window_size*100)} %", width=10)
        self.zoom_label.grid(row = self.row, column=self.column+1, padx=1, pady=1, columnspan=2)
        self.zin_btn = CTkButton(self.editor_frame, text=" + ", width=8, fg_color=BUTTON_COLOR, hover_color=BUTTON_HOVER_COLOR, command=lambda: self.zoom_callback("+"))
        self.zin_btn.grid(row = self.row+1, column=self.column+1, padx=1, pady=1)
        self.zout_btn = CTkButton(self.editor_frame, text=" - ", width=8, fg_color=BUTTON_COLOR, hover_color=BUTTON_HOVER_COLOR, command=lambda: self.zoom_callback("-"))
        self.zout_btn.grid(row = self.row+1, column=self.column+2, padx=1, pady=1)
        
        # Page
        self.page_num, self.tot_pages_num = 0, 0
        self.page_label = CTkLabel(self.editor_frame, text="", width=15)
        self.page_label.grid(row = self.row, column=self.column+4, padx=1, pady=1, columnspan=2)
        self.update_page_label()
        self.reward_btn = CTkButton(self.editor_frame, text="<<", width=5, fg_color=BUTTON_COLOR, hover_color=BUTTON_HOVER_COLOR, command= self.get_prev_page)
        self.reward_btn.grid(row = self.row+1, column=self.column+4, padx=1, pady=1)
        self.forward_btn = CTkButton(self.editor_frame, text=">>", width=5, fg_color=BUTTON_COLOR, hover_color=BUTTON_HOVER_COLOR, command= self.get_next_page)
        self.forward_btn.grid(row = self.row+1, column=self.column+5, padx=1, pady=1)

        self.min_v = self.page_num * self.window_size
        self.max_v = self.min_v + self.window_size

    def show(self, intenal:bool=False):

        self.timeline.timeline_init()
        if not intenal:
            self.min_v, self.max_v = self.get_window_range()
        self.update_page_label()

        already_added = [(None, None)]
        px, py = None, None

        for keyframe in self.tape:
            if keyframe.x >= self.min_v and keyframe.x <= self.max_v:
                
                normalized_x = (keyframe.x - self.min_v) / (self.max_v - self.min_v)
                self.timeline.add_keyframe_from_gui(normalized_x, keyframe.y)
                """
                normalized_x = (keyframe.x - self.min_v) / (self.max_v - self.min_v)
                if keyframe.y != py:
                    
                    if (normalized_x, keyframe.y) not in already_added:
                        self.timeline.add_keyframe_from_gui(normalized_x, keyframe.y)
                    
                    if (px, py) not in already_added:
                        self.timeline.add_keyframe_from_gui(px, py)
                
                px, py = normalized_x, keyframe.y
                """

        self.timeline.update_interpolation_line() 

    def update_page_label(self):
        self.page_label.configure(text=f"Page {self.page_num+1} / {self.tot_pages_num}")
    
    def zoom_callback(self, param):
        if self.timeline.RC == 0: 
            self.save_keyframes()

        if param == "-":
            if self.window_size <= (1 - self.step):
                self.window_size += self.step
        
        elif param == "+":
            if self.window_size >= 2*self.step:
                self.window_size -= self.step
        
        self.window_size = round(self.window_size, 2)
        self.tot_pages_num = int(1 / self.window_size) + 1
        self.zoom_label.configure(text=f"Zoom: {int(self.window_size*100)} %")

        self.show()
    
    def get_prev_page(self):
        if self.timeline.RC == 0: 
            self.save_keyframes()
        if self.page_num > 0:
            self.page_num -= 1

        self.min_v = self.page_num * self.window_size
        self.max_v = self.min_v + self.window_size
        
        self.show(intenal=True)

    def get_next_page(self):
        if self.timeline.RC == 0:
            self.save_keyframes()

        if self.page_num < self.tot_pages_num-1:
            self.page_num += 1

        self.min_v = self.page_num * self.window_size
        self.max_v = self.min_v + self.window_size

        self.show(intenal=True)
    
    def close_editor(self):
        self.save_keyframes()
        points = [(kf.real_x, kf.real_y) for kf in self.tape]
        self.tape = equidistant_points(points, self.original_length)
        result = messagebox.askyesno("Save Editor Changes", f"Do you want to save your changes for {self.track_name} track?")
        if result:
            self.update_callback()

        self.editor_frame.destroy()
        self.is_open = False

    def load_editor(self, record_tape:dict, track_uuid:str, index:int=None):

        self.tape = []
        self.track_uuid = track_uuid
        self.original_length = len(record_tape)
        self.index = index
        for i, d in enumerate(record_tape):
            try:
                if index is not None:
                    y = d[track_uuid][index]
                else:
                    y = d[track_uuid]
            except:
                    y = 0
            
            self.tape.append(KeyFrame(real_x=i, 
                                      real_y=y,
                                      original_length=len(record_tape)))
        
        self.tot_pages_num = int(1 / self.window_size)
        self.page_num = 0
        self.update_page_label()
        self.show()
        
    def get_window_range(self):

        if self.timeline.RC == 0: 
            min_v = self.page_num * self.window_size
            max_v = min_v + self.window_size
            return min_v, max_v
        
        else:
            margin = self.window_size / 2
            rc = self.timeline.RC
            rc_perc = round(rc / self.original_length, 4)

            self.page_num = int(rc_perc // self.window_size)

            if rc_perc < margin:
                return 0, self.window_size
            elif (1 - rc_perc) < margin:
                return (1.0 - self.window_size, 1.0)
            else:
                return rc_perc-margin, rc_perc+margin

    def save_keyframes(self):
        
        new_tape = []
        last_seen = 0

        for keyframe in self.tape:
            if keyframe.x < self.min_v:
                new_tape.append(keyframe)
                last_seen += 1
            else:
                break

        # Getting the new keyframes from timeline
        # kfft : keyframes from timeline
        kfft = self.timeline.get_all_keyframes()

        for x, y in kfft:
            
            real_x = (x * (self.max_v - self.min_v) + self.min_v) * self.original_length
            real_y = 180 * y

            # Correction if modify is done
            if self.timeline.modified:
                real_y = real_y - 3

            new_tape.append(KeyFrame(real_x=real_x, real_y=real_y, original_length=self.original_length))

        for keyframe in self.tape[last_seen:]:
            if keyframe.x > self.max_v:
                new_tape.append(keyframe)

        self.tape = new_tape


def update():
    pass

if __name__ == "__main__":

    root = CTk()
    set_appearance_mode("dark")
    e = Editor(root=root, row=0, column=0, columnspan=1, track_name="Edo", update_callback=update)

    root.mainloop()