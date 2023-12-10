import os
import tkinter as tk

from customtkinter import *

class Joystick:
    def __init__(self, root, row:int, column:int, size:int=300, rowspan:int=1, columnspan:int=1, pan_range:tuple=(0,180), tilt_range:tuple=(0,180), fg_color:str="green", btn_color:str="blue"):
        self.root = root

        # Min Max Values
        self.pan_min_label = CTkLabel(self.root, text="90", width=3)
        self.pan_max_label = 
        self.tilt_min_label = 
        self.tilt_max_label = 


        # Joystick 
        self.canvas = tk.Canvas(root, width=size, height=size, highlightthickness=0)
        self.canvas.grid(row=row, column=column, rowspan=rowspan, columnspan=columnspan)

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

        # Servo Motion
        self.pan_min, self.pan_max = pan_range
        self.tilt_min, self.tilt_max = tilt_range

    def move_joystick(self, event):
        # Calculate the new position of the joystick handle
        x = event.x
        y = event.y

        distance = ((x - self.center_x) ** 2 + (y - self.center_y) ** 2) ** 0.5

        os.system("clear")
        if distance <= self.radius:
            self.canvas.coords(self.handle, x - self.delta, y - self.delta, x + self.delta, y + self.delta)
            new_x, new_y = x, y
        else:
            # Normalize the vector to stay within the circular boundary
            scale_factor = self.radius / distance
            new_x = self.center_x + (x - self.center_x) * scale_factor
            new_y = self.center_y + (y - self.center_y) * scale_factor
            self.canvas.coords(self.handle, new_x - self.delta, new_y - self.delta, new_x + self.delta, new_y + self.delta)

        print(self.get_angles(new_x, new_y))

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




if __name__ == "__main__":
    root = tk.Tk()
    app = Joystick(root, 0, 0, 300)
    root.mainloop()