import uuid
import tkinter as tk

from tkinter import ttk
from customtkinter import *

from colors import *
from controller import Controller

#from scripts.controller import Controller
#from scripts.colors import *

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

        self.frame = CTkFrame(root, width=1000, height=5000, border_color = BUTTON_COLOR, border_width=2)
        self.frame.grid(row = self.row, column=self.column, padx=10, pady=10)
        
        self.controller = controller

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
        self.fader_label = CTkLabel(self.frame, text="90", width=3)
        self.fader_label.grid(row = self.row+2, column=self.column+2, padx=5, pady=10)

        self.fader = CTkSlider(self.frame, from_=0, to=180, orientation="horizontal", width=180, command=self.fader_callback)
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

        self.selected_servo_name = track_dict["selected_servo_name"]
        self.track_name.set(track_dict["track_name"])

        self.selected_servo_pin = track_dict["selected_servo_pin"]
        if self.selected_servo_pin:
            self.servo_selector.set(f"Servo {self.selected_servo_pin}")


class PanTiltTrack:
    def __init__(self, root, row:int, column:int, track_num, controller, open_editor_callback) -> None:
        self.row, self.column = row, column
        self.type = "PANTILT"

        self.frame = CTkFrame(root, width=1500, height=7500, border_color = BUTTON_COLOR, border_width=2)
        self.frame.grid(row = self.row, column=self.column, rowspan=2, padx=10, pady=10)
        
        self.controller = controller

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

        self.available_servos = self.controller.get_servos_names()

        # PAN Servo Selectors
        self.pan_uuid = uuid.uuid4()
        self.pan_servo_label = CTkLabel(self.frame, text="Pan Servo", width=3)
        self.pan_servo_label.grid(row = self.row+2, column=self.column, padx=5, pady=10)
        self.pan_servo_selector = ttk.Combobox(self.frame, values=self.available_servos, width=7)
        self.pan_servo_selector.grid(row = self.row+2, column=self.column+1, padx=5, pady=10)
        self.pan_servo_selector.bind("<<ComboboxSelected>>", lambda: self.select_servo("PAN"))
        self.selected_pan_servo_pin = None
        self.selected_pan_servo_name = None

        # TILT Servo Selectors
        self.tilt_uuid = uuid.uuid4()
        self.tilt_servo_label = CTkLabel(self.frame, text="Tilt Servo", width=3)
        self.tilt_servo_label.grid(row = self.row+3, column=self.column, padx=5, pady=10)
        self.tilt_servo_selector = ttk.Combobox(self.frame, values=self.available_servos, width=7)
        self.tilt_servo_selector.grid(row = self.row+3, column=self.column+1, padx=5, pady=10)
        self.tilt_servo_selector.bind("<<ComboboxSelected>>", lambda: self.select_servo("TILT"))
        self.selected_tilt_servo_pin = None
        self.selected_tilt_servo_name = None

        # Joystick
        self.joystick = Joystick(root=self.frame, row=self.row+1, column=self.column+2, move_callback=self.move, size=150, rowspan=3, fg_color="gray", btn_color=BUTTON_COLOR)


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
        
    def move(self, pan_angle, tilt_angle):
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
        return {"pan": None, "tilt": None}
    
    def to_dict(self):
        return {"row": self.row,
                "column": self.column, 
                "type": self.type,
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

        self.record = not track_dict["record"]
        self.record_btn_callback()

        self.active = not track_dict["active"]
        self.active_btn_callback()

        self.selected_servo_name = track_dict["selected_servo_name"]
        self.track_name.set(track_dict["track_name"])

        self.selected_pan_servo_pin = track_dict["selected_pan_servo_pin"]
        if self.selected_pan_servo_pin:
            self.pan_servo_selector.set(f"Servo {self.selected_pan_servo_pin}")
        
        self.selected_tilt_servo_pin = track_dict["selected_tilt_servo_pin"]
        if self.selected_tilt_servo_pin:
            self.tilt_servo_selector.set(f"Servo {self.selected_tilt_servo_pin}")


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
        
        self.move_callback(new_x, new_y)
        
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
        self.move_callback(new_x, new_y)





def open_editor():
    pass


if __name__ == "__main__":

    root = CTk()
    c = Controller(max_retry_number=1)
    set_appearance_mode("dark")

    b1 = PanTiltTrack(root=root, row=0, column=0, track_num=0, controller=c, open_editor_callback=open_editor)
    b2 = FaderTrack(root, 0, 1, 1, controller=c, open_editor_callback=open_editor)
    b3 = ButtonTrack(root, 0, 2, 2, controller=c, open_editor_callback=open_editor)
    b2 = FaderTrack(root, 1, 1, 1, controller=c, open_editor_callback=open_editor)
    b3 = ButtonTrack(root, 1, 2, 2, controller=c, open_editor_callback=open_editor)

    root.mainloop()