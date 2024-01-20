import uuid
import tkinter as tk
import math

from tkinter import ttk
from customtkinter import *

# from colors import *
# from controller import Controller

from scripts.controller import Controller
from scripts.colors import *

class TextVariable:
    def __init__(self, root, row:int, column:int, default_text:str, rowspan:int=1, columnspan:int=1, padx:int=5, pady:int=10, sticky:str=None, width:int=None, height:int=None, ext_callback = None):
        self.text = None
        self.ext_callback = None
        self.entry_var = tk.StringVar()
        self.entry_var.trace_add("write", self.on_text_change)

        self.entry = ttk.Entry(root, textvariable=self.entry_var, width=width, height=height)
        self.entry.insert(0, str(default_text))
        self.entry.grid(row=row, column=column, rowspan=rowspan, columnspan=columnspan, padx=padx, pady=pady, sticky=sticky)

        self.ext_callback = ext_callback

    def on_text_change(self, *args):
        try:
            self.text = int(self.entry_var.get())
            if self.ext_callback:
                self.ext_callback()

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

        self.frame = CTkFrame(root, width=500, height=500, border_color = BUTTON_COLOR, border_width=2)
        self.frame.grid(row = self.row, column=self.column, padx=10, pady=10)

        # Track Name
        self.track_name = TextVariable(root=self.frame, row=self.row, column=self.column, default_text=f"Track {track_num}", 
                                       columnspan=2, padx=5, sticky="w", width=14)

        # Editor Button
        self.editor_btn = CTkButton(self.frame, text="Editor", width=5, fg_color=BUTTON_COLOR, hover_color=BUTTON_HOVER_COLOR, command= lambda: open_editor_callback(self.uuid))
        self.editor_btn.grid(row = self.row, column=self.column+2, padx=5, pady=10)

        # Record Button
        self.record_btn = CTkButton(self.frame, text="R", width=2, command=self.record_btn_callback)
        self.record_btn.grid(row = self.row+1, column=self.column, padx=5, pady=10)
        self.record = False

        # Active Button
        self.active_btn = CTkButton(self.frame, text="A", width=2, fg_color = "green", command=self.active_btn_callback)
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
        self.rest_label = CTkLabel(self.frame, text="Rest", width=6)
        self.rest_label.grid(row = self.row+2, column=self.column, padx=10, pady=1)
        self.peak_label = CTkLabel(self.frame, text="Peak", width=6)
        self.peak_label.grid(row = self.row+2, column=self.column+1, padx=10, pady=1)

        self.rest_box = TextVariable(root=self.frame, row=self.row+3, column=self.column, default_text="0", padx=5, width=3)
        self.peak_box = TextVariable(root=self.frame, row=self.row+3, column=self.column+1, default_text="180", padx=5, width=3)

        # Button
        self.btn = CTkButton(self.frame, text="PRESS", fg_color = BUTTON_COLOR, hover=False, height=40, width=110)
        self.btn.grid(row = self.row+2, column=self.column+2, rowspan=2, columnspan=3, padx=10, pady=10)
        self.btn.bind("<ButtonPress-1>", lambda event: self.btn_press_callback())
        self.btn.bind("<ButtonRelease-1>", lambda event: self.btn_release_callback())

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
        self.btn.configure(fg_color = BUTTON_HOVER_COLOR)
        # Moving Servo
        self.move(self.btn_value)
        
    def btn_release_callback(self):
        if self.is_pressed:
            self.is_pressed = False
            self.btn_value = int(self.rest_box.get())
            self.btn.configure(fg_color = BUTTON_COLOR)
            self.move(self.btn_value)

    def move(self, angle):
        if self.controller.connected and self.active and self.selected_servo_pin:
            self.controller.move(servo_pin=self.selected_servo_pin, angle=angle)
        
    def record_btn_callback(self):
        if self.record:
            self.record_btn.configure(fg_color="gray")
            self.record = False
        else:
            self.record_btn.configure(fg_color="red")
            self.record = True
    
    def active_btn_callback(self):
        if self.active:
            self.active_btn.configure(fg_color="gray")
            self.active = False
        else:
            self.active_btn.configure(fg_color="green")
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

        self.track_name.set(track_dict["track_name"])

        self.selected_servo_name = track_dict["selected_servo_name"]
        self.selected_servo_pin = track_dict["selected_servo_pin"]
        if self.selected_servo_pin:
            self.servo_selector.set(self.selected_servo_name)


class FaderTrack:
    def __init__(self, root, row:int, column:int, track_num, controller, open_editor_callback) -> None:
        self.row, self.column = row, column
        self.uuid = uuid.uuid4()
        self.type = "FADER"

        self.frame = CTkFrame(root, width=1000, height=5000, border_color = BUTTON_COLOR, border_width=2)
        self.frame.grid(row = self.row, column=self.column, padx=10, pady=10)
        
        self.controller = controller
        self.rest_angle = 90

        # Track Name
        self.track_name = TextVariable(root=self.frame, row=self.row, column=self.column, default_text=f"Track {track_num}", 
                                       columnspan=3, padx=5, sticky="w", width=14)

        # Editor Button
        self.editor_btn = CTkButton(self.frame, text="Editor", width=5, fg_color=BUTTON_COLOR, hover_color=BUTTON_HOVER_COLOR, command= lambda: open_editor_callback(self.uuid))
        self.editor_btn.grid(row = self.row, column=self.column+2, padx=5, pady=10)

        # Record Button
        self.record_btn = CTkButton(self.frame, text="R", width=2, command=self.record_btn_callback)
        self.record_btn.grid(row = self.row+1, column=self.column, padx=5, pady=10)
        self.record = False

        # Active Button
        self.active_btn = CTkButton(self.frame, text="A", width=2, fg_color = "green", command=self.active_btn_callback)
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
        self.fader_label = CTkLabel(self.frame, text=str(self.rest_angle), width=3)
        self.fader_label.grid(row = self.row+2, column=self.column+2, padx=5, pady=10)
        self.fader = CTkSlider(self.frame, from_=0, to=180, orientation="horizontal", width=180, command=self.fader_callback)
        self.fader.grid(row = self.row+2, column=self.column, columnspan=2, padx=5, pady=10)
        self.fader.bind("<Button-1>", self.reset_callback)
        self.last_click_time = 0
        self.fader.set(self.rest_angle) 
        self.fader_value = self.rest_angle

    def reset_callback(self, event):
        # Check if the time difference between clicks is small enough to be considered a double-tap
        current_time = event.time
        time_diff = current_time - self.last_click_time
        self.last_click_time = current_time

        if 0 < time_diff < 500:
            self.move(self.rest_angle)
            self.fader_label.configure(text=str(self.rest_angle))
            self.fader.set(self.rest_angle) 
            self.fader_value = self.rest_angle
        

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
        self.fader_label.configure(text=str(int(float(value))))
        
    def move(self, angle):
        if self.controller.connected and self.active and self.selected_servo_pin:
            self.controller.move(servo_pin=self.selected_servo_pin, angle=angle)

    def record_btn_callback(self):
        if self.record:
            self.record_btn.configure(fg_color="gray")
            self.record = False
        else:
            self.record_btn.configure(fg_color="red")
            self.record = True
    
    def active_btn_callback(self):
        if self.active:
            self.active_btn.configure(fg_color="gray")
            self.active = False
        else:
            self.active_btn.configure(fg_color="green")
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

        self.track_name.set(track_dict["track_name"])

        self.selected_servo_name = track_dict["selected_servo_name"]
        self.selected_servo_pin = track_dict["selected_servo_pin"]
        if self.selected_servo_pin:
            self.servo_selector.set(self.selected_servo_name)


class PanTiltTrack:
    def __init__(self, root, row:int, column:int, track_num, controller, open_editor_callback) -> None:
        self.row, self.column = row, column
        self.type = "PANTILT"
        self.uuid = uuid.uuid4()

        self.frame = CTkFrame(root, width=1500, height=7500, border_color = BUTTON_COLOR, border_width=2)
        self.frame.grid(row = self.row, column=self.column, rowspan=2, columnspan=2, padx=10, pady=10)
        
        self.controller = controller

        # Track Name
        self.track_name = TextVariable(root=self.frame, row=self.row, column=self.column, default_text=f"Track {track_num}", 
                                       columnspan=3, padx=5, sticky="w", width=14)

        # Record Button
        self.record_btn = CTkButton(self.frame, text="R", width=2, command=self.record_btn_callback)
        self.record_btn.grid(row = self.row+1, column=self.column, padx=5, pady=10)
        self.record = False

        # Active Button
        self.active_btn = CTkButton(self.frame, text="A", width=2, fg_color = "green", command=self.active_btn_callback)
        self.active_btn.grid(row = self.row+1, column=self.column+1, padx=5, pady=10)
        self.active = True

        self.available_servos = self.controller.get_servos_names()

        # PAN Servo Selectors
        self.pan_uuid = uuid.uuid4()
        self.pan_servo_label = CTkLabel(self.frame, text="Pan Servo", width=3)
        self.pan_servo_label.grid(row = self.row+2, column=self.column, padx=5, pady=10)
        self.pan_servo_selector = ttk.Combobox(self.frame, values=self.available_servos, width=7)
        self.pan_servo_selector.grid(row = self.row+2, column=self.column+1, padx=5, pady=10)
        self.pan_servo_selector.bind("<<ComboboxSelected>>", lambda x: self.select_servo("PAN"))
        self.selected_pan_servo_pin = None
        self.selected_pan_servo_name = None

        self.pan_editor_btn = CTkButton(self.frame, text="Pan Editor", width=5, fg_color=BUTTON_COLOR, hover_color=BUTTON_HOVER_COLOR, command= lambda: open_editor_callback(self.uuid, index=0))
        self.pan_editor_btn.grid(row = self.row, column=self.column+2, padx=5, pady=10)

        # TILT Servo Selectors
        self.tilt_uuid = uuid.uuid4()
        self.tilt_servo_label = CTkLabel(self.frame, text="Tilt Servo", width=3)
        self.tilt_servo_label.grid(row = self.row+3, column=self.column, padx=5, pady=10)
        self.tilt_servo_selector = ttk.Combobox(self.frame, values=self.available_servos, width=7)
        self.tilt_servo_selector.grid(row = self.row+3, column=self.column+1, padx=5, pady=10)
        self.tilt_servo_selector.bind("<<ComboboxSelected>>", lambda x: self.select_servo("TILT"))
        self.selected_tilt_servo_pin = None
        self.selected_tilt_servo_name = None

        self.tilt_editor_btn = CTkButton(self.frame, text="Tilt Editor", width=5, fg_color=BUTTON_COLOR, hover_color=BUTTON_HOVER_COLOR, command= lambda: open_editor_callback(self.uuid, index=1))
        self.tilt_editor_btn.grid(row = self.row, column=self.column+3, padx=5, pady=10)

        # Joystick
        self.joystick = Joystick(root=self.frame, row=self.row+1, column=self.column+2, columnspan=2, move_callback=self.move, size=150, rowspan=3, fg_color="gray", btn_color=BUTTON_COLOR)


    def update_available_servos(self, servos_list):
        self.available_servos = servos_list

    def select_servo(self, typ):
        if typ == "PAN":
            name = self.pan_servo_selector.get()
            self.selected_pan_servo_name = name
            self.selected_pan_servo_pin = int(name.split("_")[1]) 
        elif typ == "TILT":
            name = self.tilt_servo_selector.get()
            self.selected_tilt_servo_name = name
            self.selected_tilt_servo_pin = int(name.split("_")[1]) 
        
    def move(self, value:list):
        pan_angle, tilt_angle = value
        if self.controller.connected and self.active and self.selected_tilt_servo_name and self.selected_pan_servo_name:
            self.controller.move(servo_pin=self.selected_tilt_servo_pin, angle=tilt_angle)
            self.controller.move(servo_pin=self.selected_pan_servo_pin, angle=pan_angle)

    def record_btn_callback(self):
        if self.record:
            self.record_btn.configure(fg_color="gray")
            self.record = False
        else:
            self.record_btn.configure(fg_color="red")
            self.record = True
    
    def active_btn_callback(self):
        if self.active:
            self.active_btn.configure(fg_color="gray")
            self.active = False
        else:
            self.active_btn.configure(fg_color="green")
            self.active = True
    
    def get_name(self):
        return self.track_name.get()

    def get_value(self):
        x, y = self.joystick.get_value()
        return [x, y]
    
    def to_dict(self):
        return {"row": self.row,
                "column": self.column, 
                "type": self.type,
                "uuid": self.uuid,
                "pan_uuid": self.pan_uuid, 
                "tilt_uuid": self.tilt_uuid, 
                "track_name": self.get_name(),
                "record": self.record, 
                "active": self.active, 
                "selected_pan_servo_pin": self.selected_pan_servo_pin,
                "selected_pan_servo_name": self.selected_pan_servo_name,
                "selected_tilt_servo_pin": self.selected_tilt_servo_pin,
                "selected_tilt_servo_name": self.selected_tilt_servo_name}

    def load_track(self, track_dict):
        self.uuid = track_dict["uuid"]
        self.pan_uuid = track_dict["pan_uuid"]
        self.tilt_uuid = track_dict["tilt_uuid"]

        self.record = not track_dict["record"]
        self.record_btn_callback()

        self.active = not track_dict["active"]
        self.active_btn_callback()

        self.selected_pan_servo_name = track_dict["selected_pan_servo_name"]
        self.selected_pan_servo_pin = track_dict["selected_pan_servo_pin"]
        if self.selected_pan_servo_pin:
            self.pan_servo_selector.set(self.selected_pan_servo_name)
        
        self.selected_tilt_servo_name = track_dict["selected_tilt_servo_name"]
        self.selected_tilt_servo_pin = track_dict["selected_tilt_servo_pin"]
        if self.selected_tilt_servo_pin:
            self.tilt_servo_selector.set(self.selected_tilt_servo_name)


class Joystick:
    def __init__(self, root, row:int, column:int, move_callback, size:int=300, rowspan:int=1, columnspan:int=1, pan_range:tuple=(0,180), tilt_range:tuple=(0,180), fg_color:str="green", btn_color:str="blue"):

        self.frame = CTkFrame(root, bg_color=root.cget("fg_color"))
        self.frame.grid(row = row, column=column, rowspan=rowspan, columnspan=columnspan, padx=10, pady=10)

        self.move_callback = move_callback

        # Min Max Values
        self.pan_min_label, self.pan_max_label, self.tilt_min_label, self.tilt_max_label = None, None, None, None
        self.pan_min_label = TextVariable(root=self.frame, row=row+1, column=column, default_text=f"{pan_range[0]}", padx=5, width=3, ext_callback=self.update_bounds)
        self.pan_max_label = TextVariable(root=self.frame, row=row+1, column=column+2, default_text=f"{pan_range[1]}", padx=5, width=3, ext_callback=self.update_bounds)
        self.tilt_min_label = TextVariable(root=self.frame, row=row+2, column=column+1, default_text=f"{tilt_range[0]}", padx=5, width=3, ext_callback=self.update_bounds)
        self.tilt_max_label = TextVariable(root=self.frame, row=row, column=column+1, default_text=f"{tilt_range[1]}", padx=5, width=3, ext_callback=self.update_bounds)

        self.pan_min, self.pan_max = pan_range
        self.tilt_min, self.tilt_max = tilt_range

        # Joystick 
        self.canvas = tk.Canvas(self.frame, width=size, height=size, highlightthickness=0)
        self.canvas.grid(row=row+1, column=column+1)

        self.size = size
        self.delta = size/20
        self.center_x, self.center_y, = size/2, size/2
        self.min_bound, self.max_bound = int(size*0.05), int(size*0.95)
        self.range = self.max_bound - self.min_bound
        self.radius = self.range / 2
        self.bg = self.canvas.create_oval(self.min_bound, self.min_bound, self.max_bound, self.max_bound, fill=fg_color, outline=btn_color)

        self.min_oval, self.max_oval = self.center_x - self.delta, self.center_x + self.delta
        self.handle = self.canvas.create_oval(self.min_oval, self.min_oval, self.max_oval, self.max_oval, fill=btn_color)

        self.canvas.bind("<B1-Motion>", self.move_joystick)
        self.canvas.bind("<Double-Button-1>", self.reset_position)

        self.x, self.y = self.get_angles(self.center_x, self.center_y)

    def update_bounds(self):
        if self.pan_min_label:
            self.pan_min = self.pan_min_label.get()

        if self.pan_max_label: 
            self.pan_max = self.pan_max_label.get()
            
        if self.tilt_min_label: 
            self.tilt_min = self.tilt_min_label.get()
            
        if self.tilt_max_label:
            self.tilt_max = self.tilt_max_label.get()

    def move_joystick(self, event):
        # Calculate the new position of the joystick handle
        x = event.x
        y = event.y

        distance = ((x - self.center_x) ** 2 + (y - self.center_y) ** 2) ** 0.5

        if distance <= self.radius:
            self.canvas.coords(self.handle, x - self.delta, y - self.delta, x + self.delta, y + self.delta)
            new_x, new_y = x, y
        else:
            # Normalize the vector to stay within the circular boundary
            scale_factor = self.radius / distance
            new_x = self.center_x + (x - self.center_x) * scale_factor
            new_y = self.center_y + (y - self.center_y) * scale_factor
            self.canvas.coords(self.handle, new_x - self.delta, new_y - self.delta, new_x + self.delta, new_y + self.delta)
        
        self.move_callback([new_x, new_y])
        self.x, self.y = self.get_angles(new_x, new_y)
        
    def get_perc_size(self, x, y):
        xp = round((x - self.center_x) / self.range, 2)
        yp = round((self.center_y - y) / self.range, 2)
        return xp, yp
    
    def get_angles(self, x, y):
        xp, yp = self.get_perc_size(x, y)
        x_angle = self.compute_angle(self.pan_min, self.pan_max, xp)
        y_angle = self.compute_angle(self.tilt_min, self.tilt_max, yp)
        return x_angle, y_angle

    def compute_angle(center, start, end, percentage_range):
        delta = end-start
        to_add = delta * percentage_range
        return int(start + delta/2 + to_add)
    
    def reset_position(self, event):
        self.canvas.coords(self.handle, self.min_oval, self.min_oval, self.max_oval, self.max_oval)
        new_x, new_y = self.get_angles(self.center_x, self.center_y)
        self.move_callback([new_x, new_y])

    def get_value(self):
        return self.x, self.y


class CoupleTrack:

    def __init__(self, root, row:int, column:int, track_num, controller, open_editor_callback) -> None:
        self.row, self.column = row, column
        self.uuid = uuid.uuid4()
        self.type = "COUPLE"

        self.frame = CTkFrame(root, width=1000, height=5000, border_color = BUTTON_COLOR, border_width=2)
        self.frame.grid(row = self.row, column=self.column, padx=10, pady=10)
        
        self.controller = controller
        self.rest_angle = 90

        # Track Name
        self.track_name = TextVariable(root=self.frame, row=self.row, column=self.column, default_text=f"Track {track_num}", 
                                       columnspan=4, padx=5, sticky="w", width=14)

        # Record Button
        self.record_btn = CTkButton(self.frame, text="R", width=2, command=self.record_btn_callback)
        self.record_btn.grid(row = self.row+1, column=self.column, padx=5, pady=10)
        self.record = False

        # Active Button
        self.active_btn = CTkButton(self.frame, text="A", width=2, fg_color = "green", command=self.active_btn_callback)
        self.active_btn.grid(row = self.row+1, column=self.column+1, padx=5, pady=10)
        self.active = True

        # Inverse Button
        self.inverse_btn = CTkButton(self.frame, text=" I ", width=4, fg_color = "orange", command=self.inverse_btn_callback)
        self.inverse_btn.grid(row = self.row+1, column=self.column+2, padx=5, pady=10)
        self.inverse = True
        self.inverse_btn.bind("<KeyPress-space>", self.set_inverse)
        self.inverse_btn.bind("<KeyRelease-space>", self.set_no_inverse)
        
        self.available_servos = self.controller.get_servos_names()

        # 1 Servo Selectors
        self.servo1_label = CTkLabel(self.frame, text="Servo 1", width=3)
        self.servo1_label.grid(row = self.row+2, column=self.column, padx=5, pady=10)
        self.servo1_selector = ttk.Combobox(self.frame, values=self.available_servos, width=7)
        self.servo1_selector.grid(row = self.row+2, column=self.column+1, columnspan=2, padx=5, pady=10)
        self.servo1_selector.bind("<<ComboboxSelected>>", lambda x: self.select_servo(1))
        self.selected_servo1_pin = None
        self.selected_servo1_name = None

        self.editor1_btn = CTkButton(self.frame, text="Editor 1", width=5, fg_color=BUTTON_COLOR, hover_color=BUTTON_HOVER_COLOR, command= lambda: open_editor_callback(self.uuid, index=0))
        self.editor1_btn.grid(row = self.row, column=self.column+3, padx=5, pady=10)

        # 2 Servo Selectors
        self.servo2_label = CTkLabel(self.frame, text="Servo 2", width=3)
        self.servo2_label.grid(row = self.row+3, column=self.column, padx=5, pady=10)
        self.servo2_selector = ttk.Combobox(self.frame, values=self.available_servos, width=7)
        self.servo2_selector.grid(row = self.row+3, column=self.column+1, columnspan=2, padx=5, pady=10)
        self.servo2_selector.bind("<<ComboboxSelected>>", lambda x: self.select_servo(2))
        self.selected_servo2_pin = None
        self.selected_servo2_name = None

        self.editor2_btn = CTkButton(self.frame, text="Editor 2", width=5, fg_color=BUTTON_COLOR, hover_color=BUTTON_HOVER_COLOR, command= lambda: open_editor_callback(self.uuid, index=1))
        self.editor2_btn.grid(row = self.row, column=self.column+4, padx=5, pady=10)

        # Eyes
        self.s1 = ServoAngle(self.frame, row=self.row+2, column=self.column+3, size=60)
        self.s2 = ServoAngle(self.frame, row=self.row+2, column=self.column+4, size=60)
        self.s1.draw_angle(self.rest_angle)
        self.s2.draw_angle(self.rest_angle)

        # Fader
        self.fader = CTkSlider(self.frame, from_=0, to=180, orientation="horizontal", width=180, command=self.fader_callback)
        self.fader.grid(row = self.row+3, column=self.column+3, columnspan=2, padx=5, pady=10)
        self.fader.bind("<Button-1>", self.reset_callback)
        self.last_click_time = 0
        self.fader.set(self.rest_angle) 
        self.fader_value = self.rest_angle

    def reset_callback(self, event):
        # Check if the time difference between clicks is small enough to be considered a double-tap
        current_time = event.time
        time_diff = current_time - self.last_click_time
        self.last_click_time = current_time

        if 0 < time_diff < 500:
            self.move([self.rest_angle]*2)
            self.s1.draw_angle(self.rest_angle)
            self.s2.draw_angle(self.rest_angle)
            self.fader.set(self.rest_angle) 
            self.fader_value = self.rest_angle
        
    def update_available_servos(self, servos_list):
        self.available_servos = servos_list

    def select_servo(self, num):
        if num == 1:
            name = self.servo1_selector.get()
            self.selected_servo1_name = name
            self.selected_servo1_pin = int(name.split("_")[1]) 
        elif num == 2:
            name = self.servo2_selector.get()
            self.selected_servo2_name = name
            self.selected_servo2_pin = int(name.split("_")[1]) 

    def fader_callback(self, value):
        angle = int(float(value))

        if self.inverse:
            angle1, angle2 = angle, 180-angle
        else:
            angle1, angle2 = angle, angle

        self.move([angle1, angle2])
        self.s1.draw_angle(angle1)
        self.s2.draw_angle(angle2)
        self.fader_value = angle
        
    def move(self, angles:list):
        angle1, angle2 = angles
        if self.controller.connected and self.active:
            if self.selected_servo1_pin:
                self.controller.move(servo_pin=self.selected_servo1_pin, angle=angle1)
            if self.selected_servo2_pin:
                self.controller.move(servo_pin=self.selected_servo2_pin, angle=angle2)

    def record_btn_callback(self):
        if self.record:
            self.record_btn.configure(fg_color="gray")
            self.record = False
        else:
            self.record_btn.configure(fg_color="red")
            self.record = True
    
    def active_btn_callback(self):
        if self.active:
            self.active_btn.configure(fg_color="gray")
            self.active = False
        else:
            self.active_btn.configure(fg_color="green")
            self.active = True

    def set_no_inverse(self):
        self.inverse_btn.configure(fg_color="gray")
        self.inverse = False
    
    def set_inverse(self):
        self.inverse_btn.configure(fg_color="orange")
        self.inverse = True

    def inverse_btn_callback(self):
        if self.inverse:
            self.set_no_inverse()
        else:
            self.set_inverse()
    
    def get_name(self):
        return self.track_name.get()

    def get_value(self):
        return [self.s1.angle, self.s2.angle]
    
    def to_dict(self):
        return {"row": self.row,
                "column": self.column, 
                "type": self.type,
                "uuid": self.uuid, 
                "track_name": self.get_name(), 
                "record": self.record, 
                "active": self.active,
                "inverse": self.inverse,
                "selected_servo1_pin": self.selected_servo1_pin,  
                "selected_servo2_pin": self.selected_servo2_pin,  
                "selected_servo1_name": self.selected_servo1_name,
                "selected_servo2_name": self.selected_servo2_name}

    def load_track(self, track_dict):
        self.uuid = track_dict["uuid"]

        self.record = not track_dict["record"]
        self.record_btn_callback()

        self.active = not track_dict["active"]
        self.active_btn_callback()

        self.inverse = not track_dict["inverse"]
        self.inverse_btn_callback()

        self.selected_servo1_name = track_dict["selected_servo1_name"]
        self.selected_servo2_name = track_dict["selected_servo2_name"]
        self.track_name.set(track_dict["track_name"])

        self.selected_servo1_name = track_dict["selected_servo1_name"]
        self.selected_servo1_pin = track_dict["selected_servo1_pin"]
        if self.selected_servo1_pin:
            self.servo1_selector.set(self.selected_servo1_name)

        self.selected_servo2_name = track_dict["selected_servo2_name"]
        self.selected_servo2_pin = track_dict["selected_servo2_pin"]
        if self.selected_servo2_pin:
            self.servo2_selector.set(self.selected_servo2_name)

class ServoAngle:

    def __init__(self, root, row, column, rowspan=1, columnspan=1, size=300, bg_color="white", fg_color="blue") -> None:
        
        self.root = root
        self.fg_color = fg_color
        self.size = size
        self.radius = size*0.8/2

        self.line = None
        self.angle = None

        width, height = size, size/2
        self.canvas = tk.Canvas(self.root, width=width, height=height, bg=bg_color)
        self.canvas.grid(row=row, column=column, rowspan=rowspan, columnspan=columnspan)

        # Draw the semicircle
        self.min, self.max = width*0.1, width*0.9
        self.xc, self.yc = size/2, size/2
        self.canvas.create_arc(self.min, self.min, self.max, self.max, start=0, extent=180, style=tk.CHORD, width=2, outline=fg_color)

    def draw_angle(self, angle):

        self.angle = angle
        if self.line: 
            self.canvas.delete(self.line)

        angle_rad = math.radians(180-angle)

        x1, y1 = self.xc, self.yc
        x2 = x1 + self.radius * math.cos(angle_rad)
        y2 = y1 - self.radius * math.sin(angle_rad)

        self.line = self.canvas.create_line(x1, y1, x2, y2, width=2, arrow=tk.LAST, fill=self.fg_color)
        

def open_editor():
    pass


if __name__ == "__main__":

    root = CTk()
    c = Controller(max_retry_number=1)
    set_appearance_mode("dark")

    b1 = PanTiltTrack(root=root, row=0, column=0, track_num=0, controller=c, open_editor_callback=open_editor)
    b2 = CoupleTrack(root, 0, 2, 1, controller=c, open_editor_callback=open_editor)
    b3 = ButtonTrack(root, 0, 3, 2, controller=c, open_editor_callback=open_editor)
    b2 = CoupleTrack(root, 1, 2, 1, controller=c, open_editor_callback=open_editor)
    b3 = ButtonTrack(root, 1, 3, 2, controller=c, open_editor_callback=open_editor)
    b2 = FaderTrack(root, 2, 0, 1, controller=c, open_editor_callback=open_editor)
    b3 = ButtonTrack(root, 2, 1, 2, controller=c, open_editor_callback=open_editor)
    b2 = FaderTrack(root, 2, 2, 1, controller=c, open_editor_callback=open_editor)
    b3 = ButtonTrack(root, 2, 3, 2, controller=c, open_editor_callback=open_editor)

    root.mainloop()