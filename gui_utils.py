#!/usr/bin/env python

import tkinter as tk

from tkinter import *
from tkinter import ttk, filedialog
from tkinter.messagebox import *
from tkinter.filedialog import askopenfile
import os

from planner import PlanConverter, Planner
from planner import *

# Colors

bg_color = '#111224'

bg_light_color = '#2e6585'

# Title'gripper_aperture_mm'
font = 'Arial'
title_color = 'white'

title_font = (font, 22)

title_y_pad = 10

subtitle_fg_color = 'white'

subtitle_font = (font, 16)


info_font = (font, 18)

num_pouch_font = (font, 30)

# Buttons

btn_font = (font, 14)


btn_bg_color = '#0F202A'


btn_fg_color = '#00C2C6'


btn_bg_bright = 'white'

btn_bg_bright = 'white'

# Padding


x_sm_pad = 5
y_sm_pad = 10
x_lg_pad = 10
y_lg_pad = 30


def value_check(v):

    try:
        # If the value is convertable to integer, convert it
        return int(v)
    except: 
        # If not, ignore and go ahead
        pass
    try:
        # If the value is convertable to float, convert it
        return float(v)
    except:
        if v == 'false': 
            return False
        elif v == 'true': 
            return True
        else:
            return str(v[1:-1])

def str_to_dict(s): 
    d = {}
    s = s[1:-1].split(", ")

    for item in s: 
        b = item.split(": ")
        key = b[0][1:-1]
        value = value_check(b[1])
        
        d[key] = value

    return d

def parse_command(command_string):

    if(len(command_string)>0):

        values = command_string.split('|')
        command = values[0]
        agent = values[1]
        startstop = values[2]
        parameter1 = None
        parameter2 = None
        if(len(values)>3):
            parameter1 = values[3]
            
        if(len(values)>4):
            parameter2 = values[4]
        return command, agent, startstop, parameter1, parameter2

class PostaClientStatus: 
    def __init__(self, frame, row=0, col=0):

        self.label = tk.Label(frame, text = "Posta Client: ", bg = bg_color, fg='white', pady=y_sm_pad, font=btn_font)
        self.label.grid(row=row, column=col, padx=x_lg_pad, sticky= tk.W + tk.E)

        self.status = tk.Label(frame, text = "Connecting", bg = bg_color, fg='yellow', pady=y_sm_pad, font=btn_font)
        self.status.grid(row=row, column=col+1, padx=x_lg_pad, sticky= tk.W + tk.E)

    def change_status(self, status):
        if status: 
            self.status.configure(text='Online', fg='green')
        else: 
            self.status.configure(text='Offline', fg='red')


class DrawerButton:
    """
    This button shows state of the drawer and can be used to execute the following actions: 
        - left click: executes action
        - left click: while action is executed: stops the action
        - right click: add the action to the queue
    """

    def __init__(self, frame, pub, num, col, row, state='CLOSED', agent='robot'):

        if state != 'CLOSED' and state != 'OPEN':
            raise KeyError('Button state can be only OPEN or CLOSED')

        text = 'DRAWER {0}\n{1}'.format(num, state)

        self.num = num
        self.pub = pub
        self.state = state
        self.agent = agent

        if self.state == 'OPEN': 
            self.color = 'GREEN'
        else: 
            self.color = 'RED'

        self.button = tk.Button(frame, text=text, font=btn_font, bg=btn_bg_color, fg=self.color)
        self.button.grid(row=row, column=col, padx=x_sm_pad, sticky= tk.W + tk.E)

        self.button.bind("<Button-1>", self.left_click)
        self.button.bind("<Button-2>", self.right_click)
        self.button.bind("<Button-3>", self.right_click)

        self.ongoing = False
    
    # Put in queue - Stop
    def left_click(self, e):

        cmd_name = self.get_action_name()

        if not self.ongoing:
            startstop = 'queue'
        else:
            startstop = 'stop'
        
        cmd_str = '{0}|{1}|{2}|{3}'.format(cmd_name, self.agent, startstop, self.num)
        self.pub.publish(cmd_str)

    # Execute Now
    def right_click(self, e):
        cmd_name = self.get_action_name()

        cmd_str = '{0}|{1}|{2}|{3}'.format(cmd_name, self.agent, 'start', self.num)
        self.pub.publish(cmd_str)

    def get_action_name(self):
        if self.state == 'OPEN':
            return 'CloseDrawer'
        else:
            return 'OpenDrawer'
        
    def button_state_callback(self, new_state):
        # Changes the state of the button when invoced
        if new_state == 'open':
            new_text = 'DRAWER {0}\nOPEN'.format(self.num)
            self.button.configure(text=new_text, fg='GREEN', bg=btn_bg_color)
            self.state = 'OPEN'
        else:
            new_text = 'DRAWER {0}\nCLOSED'.format(self.num)
            self.button.configure(text=new_text, fg='RED', bg=btn_bg_color)
            self.state = 'CLOSED'
        
        self.ongoing = False

    def button_action_callback(self, action_status):
        if action_status == 'ongoing':
            self.ongoing = True
            self.button.configure(bg=btn_bg_bright)
        else:
            self.ongoing = False
            self.button.configure(bg=btn_bg_color)


class DrawersSection:

    def __init__(self, frame, pub, row=1, col=0):

        self.label = tk.Label(frame, text = "Drawers Status", bg = bg_color, fg=title_color, pady=title_y_pad, font=title_font)
        self.label.grid(row=row, column=col, columnspan=6, padx=x_sm_pad, sticky= tk.W + tk.E)
        
        self.btn1 = DrawerButton(frame, pub, num=1, col=col, row=row+1)
        self.btn2 = DrawerButton(frame, pub, num=2, col=col+1, row=row+1)
        self.btn3 = DrawerButton(frame, pub, num=3, col=col+2, row=row+1)
        self.btn4 = DrawerButton(frame, pub, num=4, col=col+3, row=row+1)
        self.btn5 = DrawerButton(frame, pub, num=5, col=col+4, row=row+1)
        self.btn6 = DrawerButton(frame, pub, num=6, col=col+5, row=row+1)

        self.drawers_button_list = [self.btn1, self.btn2, self.btn3, self.btn4, self.btn5, self.btn6]
    
    def open_close_drawer_num(self, num, new_state):
        self.drawers_button_list[num-1].button_state_callback(new_state)
    
    def change_action_status(self, num, action_status):
        self.drawers_button_list[num-1].button_action_callback(action_status)
    
    def is_drawer_open(self):
        """
        Returns the number of the opened drawer. If all drawers are closed returns None
        """
        for i, d in enumerate(self.drawers_button_list):

            if d.state == 'OPEN':
                return i+1
        
        return None



class TimeDisplay:
    def __init__(self, frame, row=1, col=11):

        self.label = tk.Label(frame, text = "Date & Time", bg = bg_color, fg=title_color, pady=y_sm_pad, font=subtitle_font)
        self.label.config(anchor=CENTER)
        self.label.grid(row=row, column=col, padx=x_lg_pad, sticky= tk.W + tk.E)

        self.global_time = tk.Label(frame, text = "", bg = bg_color, fg=title_color, font=info_font)
        self.global_time.config(anchor=CENTER)
        self.global_time.grid(row=row+1, column=col, padx=x_lg_pad, sticky= tk.W + tk.E)

    def change_time(self, time):
        self.global_time.configure(text=time)


class PouchesDisplay:

    def __init__(self, frame, row=1, col=7):
        # Pouches Count
        self.label = tk.Label(frame, text = "Pouches Detected", bg = bg_color, fg=title_color, pady=y_sm_pad, font=subtitle_font, anchor=CENTER)
        self.label.grid(row=row, column=col, columnspan=3, padx=x_lg_pad, pady=y_sm_pad, sticky= tk.W + tk.E)
        
        self.pouches_count = tk.Label(frame, text = " ", bg = bg_color, fg='green', font=num_pouch_font, anchor=CENTER)
        self.pouches_count.grid(row=row+1, column=col, columnspan=3, padx=x_lg_pad, sticky= tk.W + tk.E)

    def change_num_pouches(self, num):
        if num > 10: 
            color = 'green'
        elif num > 3: 
            color = 'yellow'
        else: 
            color = 'red'
        self.pouches_count.configure(text=str(num), fg=color)


class DrawerImagingButton: 
    def __init__(self, frame, pub, num, agent, row, col):

        self.button = tk.Button(frame, text=str(num), font=btn_font, bg=btn_bg_color, fg=btn_fg_color)
        self.button.grid(row=row, column=col+num-1, rowspan=2, padx=x_sm_pad, sticky= tk.W + tk.E)

        self.button.bind("<Button-1>", self.left_click)
        self.button.bind("<Button-2>", self.right_click)
        self.button.bind("<Button-3>", self.right_click)

        self.pub = pub
        self.num = num
        self.agent = agent
        self.ongoing = False

        self.cmd_name = 'GoToDrawerImaging'
    
    def left_click(self, e):
        if not self.ongoing:
            startstop = 'queue'
        else:
            startstop = 'stop'
        
        cmd_str = '{0}|{1}|{2}|{3}'.format(self.cmd_name, self.agent, startstop, self.num)
        self.pub.publish(cmd_str)

    def right_click(self, e):
        cmd_str = '{0}|{1}|{2}|{3}'.format(self.cmd_name, self.agent, 'start', self.num)
        self.pub.publish(cmd_str)

    def button_action_callback(self, action_status):
        if action_status == 'ongoing':
            self.ongoing = True
            self.button.configure(bg=btn_bg_bright)
        else:
            self.ongoing = False
            self.button.configure(bg=btn_bg_color)


class GoToDrawerImaging: 
    def __init__(self, frame, pub, row, col):
        self.label = tk.Label(frame, text = "Go to Drawer Imaging", bg = bg_color, fg=title_color, pady=title_y_pad, font=title_font)
        self.label.grid(row=row, column=col, columnspan=6, padx=x_sm_pad, sticky= tk.W + tk.E)
        
        # di stands for drawer imaging
        self.di_1 = DrawerImagingButton(frame, pub, num=1, agent='robot', row=row+1, col=col)
        self.di_2 = DrawerImagingButton(frame, pub, num=2, agent='robot', row=row+1, col=col)
        self.di_3 = DrawerImagingButton(frame, pub, num=3, agent='robot', row=row+1, col=col)
        self.di_4 = DrawerImagingButton(frame, pub, num=4, agent='robot', row=row+1, col=col)
        self.di_5 = DrawerImagingButton(frame, pub, num=5, agent='robot', row=row+1, col=col)
        self.di_6 = DrawerImagingButton(frame, pub, num=6, agent='robot', row=row+1, col=col)

        self.di_list = [self.di_1, self.di_2, self.di_3, self.di_4, self.di_5, self.di_6]
    
    def change_action_status(self, num, action_status):
        self.di_list[num-1].button_action_callback(action_status)


class ScaleDisplay:

    def __init__(self, frame, pub, row=3, col=7, agent='scale'):

        self.pub = pub
        self.agent = agent

        # Scale Label
        self.label = tk.Label(frame, text = "Scale", bg = bg_color, fg='white', pady=title_y_pad, font=title_font)
        self.label.config(anchor=CENTER)
        self.label.grid(row=row, column=col, columnspan=5, padx=x_lg_pad, sticky= tk.W + tk.E)

        # Weight
        self.weight_lab = tk.Label(frame, text = "Weight", bg = bg_color, fg='white', pady=y_sm_pad, font=btn_font)
        self.weight_lab.config(anchor=CENTER)
        self.weight_lab.grid(row=row+1, column=col, columnspan=2, padx=x_lg_pad, sticky= tk.W + tk.E)

        self.scale_weight = tk.Label(frame, text = "--- g", bg = bg_color, fg='white', pady=y_sm_pad, font=title_font)
        self.scale_weight.config(anchor=CENTER)
        self.scale_weight.grid(row=row+2, column=col, columnspan=2, padx=x_lg_pad, sticky= tk.W + tk.E)

        # Weight Time Stamp
        self.weight_time_lab = tk.Label(frame, text = "Time Stamp", bg = bg_color, pady=y_sm_pad, fg='white', font=btn_font)
        self.weight_time_lab.config(anchor=CENTER)
        self.weight_time_lab.grid(row=row+1, column=col+2, columnspan=2, padx=x_lg_pad, sticky= tk.W + tk.E)

        self.weight_time = tk.Label(frame, text = "---", bg = bg_color, fg='white', pady=y_sm_pad, font=btn_font)
        self.weight_time.config(anchor=CENTER)
        self.weight_time.grid(row=row+2, column=col+2, columnspan=2, padx=x_lg_pad, sticky= tk.W + tk.E)

        # Reset Button
        self.reset_scale = tk.Button(frame, text="Reset", bg=btn_bg_color, fg=btn_fg_color, pady=y_sm_pad, font=btn_font, command=self.reset)
        self.reset_scale.grid(row=row+1, column=col+4, rowspan=2, padx=x_lg_pad, sticky= tk.W + tk.E)

    def reset(self):
        cmd_str = 'SetScaleToZero|{}|start'.format(self.agent)
        self.pub.publish(cmd_str)
        self.weight_time.configure(text='-----')

    def change_weight(self, value):
        self.scale_weight.configure(text=str(value)+' g')
    
    def change_time(self, time):
        self.weight_time.configure(text=str(time))


class GripperButton: 

    def __init__(self, frame, pub, row=4, col=1, agent='robot', state='OPEN'):

        if state != 'CLOSED' and state != 'OPEN':
            raise KeyError('Button state can be only OPEN or CLOSED')

        text = 'GRIPPER\n{0}'.format(state)
        self.state = state

        if self.state == 'OPEN': 
            self.color = 'GREEN'
        else: 
            self.color = 'RED'

        self.button = tk.Button(frame, text=text, font=btn_font, bg=btn_bg_color, fg=self.color)
        self.button.grid(row=row, column=col, padx=x_sm_pad, rowspan=2, sticky= tk.W + tk.E)

        self.button.bind("<Button-1>", self.left_click)
        self.button.bind("<Button-2>", self.right_click)
        self.button.bind("<Button-3>", self.right_click)
    
        self.pub = pub
        self.agent = agent
    
    def button_action(self, startstop):
        # If button is pressed, send the action to sud_posta_command
        if self.state == 'OPEN':
            cmd_str = 'CloseGripper|{}|{}'.format(self.agent, startstop)
            self.pub.publish(cmd_str)
        else:
            cmd_str = 'OpenGripper|{}|{}'.format(self.agent, startstop)
            self.pub.publish(cmd_str)

    def left_click(self, e):
        self.button_action('queue')

    def right_click(self, e):
        self.button_action('queue')

    def button_state_callback(self, new_gripper_aperture):
        # Changes the state of the button when invoced
        # When Gripper is open
        if new_gripper_aperture > 30:
            new_text = 'GRIPPER\nOPEN'
            self.button.configure(text=new_text, fg='GREEN')
            self.state = 'OPEN'
        else:
            new_text = 'GRIPPER\nCLOSED'
            self.button.configure(text=new_text, fg='RED')
            self.state = 'CLOSED'
    
    def button_action_callback(self, action_status):
        if action_status == 'ongoing':
            self.ongoing = True
            self.button.configure(bg=btn_bg_bright)
        else:
            self.ongoing = False
            self.button.configure(bg=btn_bg_color)


class GripperApertureSetter:
    def __init__(self, frame, pub, col=3, row=4, agent='robot'):
        
        self.pub = pub
        self.agent = agent

        self.title_label = tk.Label(frame, text = "Gripper Aperture", bg = bg_color, fg='white', font=subtitle_font)
        self.title_label.grid(row=row, column=col, columnspan=2, padx=x_sm_pad, pady = y_sm_pad, sticky= tk.W + tk.E)

        self.text_box = tk.Text(frame, bg = 'white', fg='black', font=btn_font, height=1, width=6)
        self.text_box.grid(row=row+1, column=col, padx=x_sm_pad)

        self.set_button = tk.Button(frame, text='Set', bg=btn_bg_color, fg=btn_fg_color, font=btn_font, command=self.button_action)
        self.set_button.grid(row=row+1, column=col+1, padx=x_sm_pad, sticky= tk.W + tk.E)
    
    def change_value(self, value):
        self.text_box.delete("1.0","end")
        self.text_box.insert(tk.END, str(value))
    
    def button_action(self):
        # If pressed, has to get the value from text box and SetGripperAperture
        new_value = self.text_box.get("1.0","end-1c")
        try:
            new_value = int(new_value)
            cmd_str = 'SetGripperApertureMM|{0}|queue|{1}'.format(self.agent, new_value)
            self.pub.publish(cmd_str)
        except:
            showerror('ERROR', 'Gripper Aperture Value\nnot admissible\n(need int number)')


class PouchInGripper:
    def __init__(self, frame, col=2, row=4):
        self.label = tk.Label(frame, text = "NO POUCH\nIN GRIPPER", bg = bg_color, fg='red', font=btn_font)
        self.label.grid(row=row, column=col, rowspan=2, padx=x_sm_pad, sticky= tk.W + tk.E)

    def change_value(self, value): 
        if value: 
            self.label.config(text='POUCH\nIN GRIPPER', fg='green')
        else:
            self.label.config(text='NO POUCH\nIN GRIPPER', fg='red')


class Mark10Section: 
    def __init__(self, frame, pub, row, col):
        self.pub = pub

        # Scale Label
        self.label = tk.Label(frame, text = "Mark 10", bg = bg_color, fg='white', pady=title_y_pad, font=title_font, anchor=CENTER)
        self.label.grid(row=row, column=col, columnspan=5, padx=x_lg_pad, sticky= tk.W + tk.E)

        # Instrument Ready
        self.ready_lab = tk.Label(frame, text = "Instrument Ready", bg = bg_color, fg='white', pady=y_sm_pad, font=subtitle_font, anchor=CENTER)
        self.ready_lab.grid(row=row+1, column=col, columnspan=2, padx=x_lg_pad, sticky= tk.W + tk.E)

        self.ready = tk.Label(frame, text = "", bg = bg_color, fg='white', pady=y_sm_pad, font=btn_font, anchor=CENTER)
        self.ready.grid(row=row+2, column=col, columnspan=2, padx=x_lg_pad, sticky= tk.W + tk.E)

        # Plate Distance
        self.plate_dist_lab = tk.Label(frame, text = "Plate Distance", bg = bg_color, fg='white', pady=y_sm_pad, font=subtitle_font)
        self.plate_dist_lab.config(anchor=CENTER)
        self.plate_dist_lab.grid(row=row+1, column=col+2, columnspan=2, padx=x_lg_pad, sticky= tk.W + tk.E)

        self.plate_dist = tk.Label(frame, text = "-1", bg = bg_color, fg='white', pady=y_sm_pad, font=btn_font)
        self.plate_dist.config(anchor=CENTER)
        self.plate_dist.grid(row=row+2, column=col+2, columnspan=2, padx=x_lg_pad, sticky= tk.W + tk.E)

        # Test Completed
        self.test_status_lab = tk.Label(frame, text = "Test Status", bg = bg_color, fg=subtitle_fg_color, pady=y_sm_pad, font=subtitle_font)
        self.test_status_lab.config(anchor=CENTER)
        self.test_status_lab.grid(row=row+1, column=col+4, columnspan=1, padx=x_lg_pad, sticky= tk.W + tk.E)

        self.test_status = tk.Label(frame, text = "   COMPLETED   ", bg = bg_color, fg='green', pady=y_sm_pad, font=btn_font)
        self.test_status.config(anchor=CENTER)
        self.test_status.grid(row=row+2, column=col+4, columnspan=1, padx=x_sm_pad, sticky= tk.W + tk.E)

        self.test_status_info = 'COMPLETED'

    
    def change_test_status(self, state):
        if state:
            self.test_status.configure(text='   COMPLETED   ', fg='green')
            self.test_status_info = 'COMPLETED'
        else: 
            self.test_status.configure(text='NOT COMPLETED', fg='red')
            self.test_status_info = 'NOT COMPLETED'

    def change_plate_distance(self, dist):
        self.plate_dist.configure(text=str(dist))

    def change_mark10_ready(self, state):

        if state: 
            self.ready.configure(text='READY', fg='green')
        else: 
            self.ready.configure(text='NOT READY', fg='red')


class ActionButton:

    def __init__(self, frame, pub, text, cmd_str, agent, col, row, p1 = None, p2 = None, rowspan=2):
        self.button = tk.Button(frame, text=text, font=btn_font, bg=btn_bg_color, fg=btn_fg_color)
        self.button.grid(row=row, column=col, rowspan=rowspan, padx=x_sm_pad, pady= y_sm_pad, sticky= tk.W + tk.E)

        self.button.bind("<Button-1>", self.left_click)
        self.button.bind("<Button-2>", self.right_click)
        self.button.bind("<Button-3>", self.right_click)

        self.p1 = p1
        self.p2 = p2

        self.cmd_str = cmd_str
        self.agent = agent
        self.pub = pub
        self.ongoing = False

    def left_click(self, e):
        if not self.ongoing:
            startstop = 'queue'
        else:
            startstop = 'stop'
        
        cmd_str = '{0}|{1}|{2}'.format(self.cmd_str, self.agent, startstop)

        if self.p1:
            cmd_str += '|{}'.format(self.p1)
            if self.p2:
                cmd_str += '|{}'.format(self.p2)

        self.pub.publish(cmd_str)

    def right_click(self, e):
        cmd_str = '{0}|{1}|{2}'.format(self.cmd_str, self.agent, 'start')
        self.pub.publish(cmd_str)
    
    def button_action_callback(self, action_status):
        if action_status == 'ongoing':
            self.ongoing = True
            self.button.configure(bg=btn_bg_bright)
        else:
            self.ongoing = False
            self.button.configure(bg=btn_bg_color)


class ActionSection: 
    def __init__(self, frame, pub, row=10, col=1):
        self.label = tk.Label(frame, text = "Actions", bg = bg_color, fg=title_color, pady=title_y_pad, font=title_font)
        self.label.grid(row=row, column=col, columnspan=6, padx=x_sm_pad, sticky= tk.W + tk.E)

        # Action Buttons
        self.pick_next_pouch = ActionButton(frame, pub, 'PICK NEXT\nPOUCH', cmd_str='PickNextPouch', agent='robot', row=row+1, col=col+0)
        self.put_pouch_on_scale = ActionButton(frame, pub, 'PUT POUCH\nON SCALE', cmd_str='PutPouchOnScale', agent='robot', row=row+1, col=col+1)
        self.pick_pouch_from_scale = ActionButton(frame, pub, 'PICK POUCH\nFROM SCALE', cmd_str='PickPouchFromScale', agent='robot', row=row+1, col=col+2)
        self.pouch_on_strenght = ActionButton(frame, pub, 'POUCH ON\nSTRENGHT', cmd_str='PutPouchOnStrengthPlate', agent='robot', row=row+1, col=col+3)
        self.dispose_sheet = ActionButton(frame, pub, 'DISPOSE\nSHEET', cmd_str='DisposePaperSheetFromStrength', agent='robot', row=row+1, col=col+4)
        self.put_pouch_on_tight = ActionButton(frame, pub, 'PUT POUCH\nON TIGHT', cmd_str='PutPouchOnTightPlate', agent='robot', row=row+1, col=col+5)

        self.pick_pouch_from_tight = ActionButton(frame, pub, 'PICK POUCH\nFROM TIGHT', cmd_str='PickPouchFromTightPlate', agent='robot', row=row+3, col=col+0)
        self.start_strength = ActionButton(frame, pub, 'START\nSTRENGTH', cmd_str='StartStrengthTest', agent='mark10s', p1='d4_r5_c6', p2 = 'BIC-01-0001-01#03', row=row+3, col=col+1)
        self.start_tight = ActionButton(frame, pub, 'START\nTIGHT', cmd_str='StartTightTest', agent='mark10t', p1='d4_r5_c6', p2 = 'BIC-01-0001-01#03', row=row+3, col=col+2)
        self.gotorest = ActionButton(frame, pub, 'GO TO\nREST', cmd_str='GoToRestPose', agent='robot', row=row+3, col=col+5)

        self.actions_btn_list = {'PickNextPouch': self.pick_next_pouch,
                                 'PutPouchOnScale': self.put_pouch_on_scale, 
                                 'PickPouchFromScale': self.pick_pouch_from_scale, 
                                 'PutPouchOnStrengthPlate': self.pouch_on_strenght,  
                                 'DisposePaperSheetFromStrength': self.dispose_sheet, 
                                 'StartStrengthTest': self.start_strength,
                                 'StartTightTest': self.start_tight,
                                 'GoToRestPose': self.gotorest, 
                                 'PickPouchFromTightPlate': self.pick_pouch_from_tight, 
                                 'PutPouchOnTight': self.put_pouch_on_tight}
        
        self.available_actions = [k for k in self.actions_btn_list.keys()]


class GeneralSection: 
    def __init__(self, frame, pub, row, col):

        self.pub = pub
        
        # General Label
        self.label = tk.Label(frame, text = "General Controls", bg = bg_color, fg=title_color, pady=title_y_pad, font=title_font, anchor=CENTER)
        self.label.grid(row=row, column=col, columnspan=5, padx=x_lg_pad, sticky= tk.W + tk.E)

        # Parameters
        self.robot_lab = tk.Label(frame, text = "Robot", bg = bg_color, fg=title_color, pady=y_sm_pad, font=btn_font, anchor=CENTER)
        self.robot_lab.grid(row=row+1, column=col, padx=x_lg_pad, sticky= tk.W + tk.E)

        self.plate_lab = tk.Label(frame, text = "Mark10 Plate", bg = bg_color, fg=title_color, pady=y_sm_pad, font=btn_font, anchor=CENTER)
        self.plate_lab.grid(row=row+2, column=col, padx=x_lg_pad, sticky= tk.W + tk.E)

        self.traj_lab = tk.Label(frame, text = "Trajectory",  bg = bg_color, fg=title_color, pady=y_sm_pad, font=btn_font, anchor=CENTER)
        self.traj_lab.grid(row=row+3, column=col, padx=x_lg_pad, sticky= tk.W + tk.E)

        # Values
        self.robot = tk.Label(frame, text = "", bg = bg_color, fg=title_color, pady=y_sm_pad, font=btn_font, anchor=CENTER)
        self.robot.grid(row=row+1, column=col+2, padx=x_lg_pad, sticky= tk.W + tk.E)

        self.plate = tk.Label(frame, text = "Not Moving", bg = bg_color, fg=title_color, pady=y_sm_pad, font=btn_font, anchor=CENTER)
        self.plate.grid(row=row+2, column=col+2, padx=x_lg_pad, sticky= tk.W + tk.E)

        self.traj= tk.Label(frame, text = "Ready",  bg = bg_color, fg=title_color, pady=y_sm_pad, font=btn_font, anchor=CENTER)
        self.traj.grid(row=row+3, column=col+2, padx=x_lg_pad, sticky= tk.W + tk.E)

        # Buttons
        self.reset_btn = ActionButton(frame, self.pub, text='RESET', cmd_str='Reset', agent='robot', row=row+1, col=col+4, rowspan=1)
        self.rest_btn = ActionButton(frame, self.pub, text='GO TO REST', cmd_str='GoToRestPose', agent='robot', row=row+2, col=col+4, rowspan=1)
        self.ping_btn = ActionButton(frame, self.pub, text='PING', cmd_str='Ping', agent='robot', row=row+3, col=col+4, rowspan=1)
        
        self.actions_btn_list = {'Reset': self.reset_btn,
                                 'GoToRestPose': self.rest_btn, 
                                 'Ping': self.ping_btn}
        self.available_actions = [k for k in self.actions_btn_list.keys()]

    def change_robot(self, v):
        
        if v == 'moving': 
            self.robot.configure(text='MOVING', fg='green')
        elif v == 'idle': 
            self.robot.configure(text='IDLE', fg='yellow')
        else: 
            self.robot.configure(text=v.upper(), fg='red')
    
    def change_plate(self, status): 

        if status: 
            self.plate.configure(text='MOVING', fg='green')
        else: 
            self.plate.configure(text='NOT MOVING', fg='red')

    def change_traj(self, v): 
        self.traj.configure(text=v)
    

class QueueList:

    def __init__(self, frame, pub, title, col, row, rowspan):
        
        self.label = tk.Label(frame, text = title, bg = bg_color, fg=title_color, pady=title_y_pad, font=title_font, anchor='w')
        self.label.grid(row=row, column=col, padx=x_sm_pad, pady=y_sm_pad, sticky= tk.W + tk.E)

        self.len_label = tk.Label(frame, text = '0', bg = bg_color, fg=title_color, pady=title_y_pad, font=title_font, anchor='e')
        self.len_label.grid(row=row, column=col+1, padx=x_sm_pad, pady=y_sm_pad, sticky= tk.W + tk.E)
        self.len = 0

        self.table = ttk.Treeview(frame, column=('Action', 'Status'), show='headings', height=y_sm_pad)
        
        self.table.column("# 1", anchor=CENTER, minwidth=0, width=300)
        self.table.heading("# 1", text="Action")
        self.table.column("# 2", anchor=CENTER, minwidth=0, width=100)
        self.table.heading("# 2", text="Status")

        self.table.grid(row=row+1, column=col, rowspan=rowspan, columnspan=2, padx=x_sm_pad, pady=y_sm_pad, sticky= tk.W + tk.E)
    
    def __len__(self):
        return self.len

    def update_table(self, action_list):
        self.clean_table()
        self.len = len(action_list)
        self.len_label.configure(text=str(self.len))
        for name, status, p1, p2 in action_list:
            if name == 'GoTo':
                self.table.insert('', 'end', values=('{} --> {}'.format(p1, p2), status))
            else:
                self.table.insert('', 'end', values=(name, status))

    def clean_table(self):
        for item in self.table.get_children():
            self.table.delete(item)


class GoToSection:

    def __init__(self, frame, pub, row, col):

        self.pub = pub

        # Go To Label
        self.label = tk.Label(frame, text = "Go To", bg = bg_color, fg='white', pady=title_y_pad, font=title_font, anchor=CENTER)
        self.label.grid(row=row, column=col, columnspan=6, padx=x_lg_pad, sticky= tk.W + tk.E)

        # From
        self.from_lab = tk.Label(frame, text = "From", bg = bg_color, fg='white', pady=y_sm_pad, font=subtitle_font, anchor=CENTER)
        self.from_lab.grid(row=row+1, column=col, padx=x_lg_pad, sticky= tk.W + tk.E)
        self.from_selection = StringVar()
        self.from_box = ttk.Combobox(frame, textvariable = self.from_selection, font=subtitle_font)
        self.from_box.grid(row=row+2, column=col, columnspan=2, padx=x_lg_pad, sticky= tk.W + tk.E)

        # To
        self.to_lab = tk.Label(frame, text = "To", bg = bg_color, fg='white', pady=y_sm_pad, font=subtitle_font, anchor=CENTER)
        self.to_lab.grid(row=row+1, column=col+2, padx=x_lg_pad, sticky= tk.W + tk.E)
        self.to_selection = StringVar()
        self.to_box = ttk.Combobox(frame, textvariable = self.to_selection, font=subtitle_font)
        self.to_box.grid(row=row+2, column=col+2, columnspan=2, padx=x_lg_pad, sticky= tk.W + tk.E)

        # Poses list
        self.poses = ['Near Strength', 'Above Scale', 'Imaging', '']
        self.from_box['values'] = self.poses
        self.to_box['values'] = self.poses

        # Button
        self.button = tk.Button(frame, text='GO TO', font=btn_font, bg=btn_bg_color, fg=btn_fg_color)
        self.button.grid(row=row+1, column=col+4, columnspan=2, rowspan=2, padx=x_sm_pad, pady= y_sm_pad, sticky= tk.W + tk.E)

        self.button.bind("<Button-1>", self.left_click)
        self.button.bind("<Button-2>", self.right_click)
        self.button.bind("<Button-3>", self.right_click)

        # Button
        self.swap_btn = tk.Button(frame, text='SWAP', font=btn_font, bg=btn_bg_color, fg=btn_fg_color)
        self.swap_btn.grid(row=row+2, column=col+4, columnspan=2, rowspan=2, padx=x_sm_pad, pady= y_sm_pad, sticky= tk.W + tk.E)
        self.swap_btn.bind("<Button-1>", self.swap)

        self.cmd_str = 'GoTo'
        self.agent = 'robot'
        self.pub = pub
        self.ongoing = False


    def left_click(self, e):
        if not self.ongoing:
            startstop = 'queue'
        else:
            startstop = 'stop'

        self.from_pos = self.from_selection.get()
        self.to_pos = self.to_selection.get()

        if self.to_pos == '':
            showerror(title='ERROR', message='MISSING DESTIANTION')

        elif self.from_pos == self.to_pos:
            showerror(title='ERROR', message='Initial and Final positions are the same!')

        else:
            cmd_str = '{0}|{1}|{2}|{3}|{4}'.format(self.cmd_str, self.agent, startstop, self.from_pos, self.to_pos)
            self.pub.publish(cmd_str)

    def right_click(self, e):

        from_pos = self.from_selection.get()
        to_pos = self.to_selection.get()

        cmd_str = '{0}|{1}|{2}|{3}|{4}'.format(self.cmd_str, self.agent, 'start', from_pos, to_pos)
        self.pub.publish(cmd_str)
    
    def button_action_callback(self, action_status):
        if action_status == 'ongoing':
            self.ongoing = True
            self.button.configure(bg=btn_bg_bright)
        else:
            self.ongoing = False
            self.button.configure(bg=btn_bg_color)

            from_pos = self.from_selection.get()
            to_pos = self.to_selection.get()

            
            #self.from_box.set('')
            #self.to_box.set('')

    def swap(self, e):
        self.from_pos = self.from_selection.get()
        self.to_pos = self.to_selection.get()
        """
        mem = self.from_pos
        self.from_pos = self.to_pos
        self.to_pos = mem
        """
        self.from_box.set(self.to_pos)
        self.to_box.set(self.from_pos)


class PlanDisplay:

    def __init__(self, frame, col, row, rowspan):
        
        self.table = ttk.Treeview(frame, column=('Action', 'Agent', 'P1', 'P2'), show='headings', height=y_lg_pad)
        
        self.table.column("# 1", anchor=W, minwidth=0, width=300)
        self.table.heading("# 1", text="Action")
        self.table.column("# 2", anchor=CENTER, minwidth=0, width=250)
        self.table.heading("# 2", text="Agent")
        self.table.column("# 3", anchor=CENTER, minwidth=0, width=150)
        self.table.heading("# 3", text="P1")
        self.table.column("# 4", anchor=CENTER, minwidth=0, width=150)
        self.table.heading("# 4", text="P2")

        self.table.grid(row=row, column=col, rowspan=rowspan, columnspan=6, padx=x_sm_pad, pady=y_sm_pad, sticky= tk.W + tk.E)

    def update_table(self, cmd_list):

        self.clean_table()

        for cmd_str in cmd_list:

            if type(cmd_str) == str:
                command, agent, _, parameter1, parameter2 = parse_command(cmd_str)
                self.table.insert('', 'end', values=('  '+command, agent, parameter1, parameter2))

            elif type(cmd_str) == list:
                for c in cmd_str:
                    if c:
                        command, agent, _, parameter1, parameter2 = parse_command(c)
                        self.table.insert('', 'end', values=('\t'+command, agent, parameter1, parameter2))

    def clean_table(self):
        for item in self.table.get_children():
            self.table.delete(item)


class StopBtn:
    def __init__(self, frame, pub, row, col, columnspan=15):
        self.pub = pub

        self.stop_btn = tk.Button(frame, text='EMERGENCY\nSTOP', height=4, bg='red', fg='black', pady=y_sm_pad, font=title_font, anchor=CENTER, command=self.stop)
        self.stop_btn.grid(row=row, column=col, padx=x_lg_pad, pady=y_sm_pad, rowspan=4, columnspan=columnspan, sticky= tk.W + tk.E)
    
    def stop(self):
        self.pub.publish('StopAll|all|start')


class YSpace:
    def __init__(self, frame, row):
        self.spacelab = tk.Label(frame, text = ".", bg = bg_color, fg=bg_color, pady=y_sm_pad, font=info_font)
        self.spacelab.grid(row=row, column=1, padx=5, sticky= tk.W + tk.E)


class PlanSection:

    def __init__(self, frame, pub, row, col):

        self.pub = pub

        self.online = False
        self.box_value = StringVar()
        self.parallel = True

        self.planner =  Planner()

        # Plan Section Label
        self.label = tk.Label(frame, text = "Plan Section", bg = bg_color, fg='white', pady=title_y_pad, font=title_font, anchor=CENTER)
        self.label.grid(row=row, column=col, columnspan=6, padx=x_lg_pad, sticky= tk.W + tk.E)

        self.on_off = tk.Button(frame, text='OFFLINE\nCOMPUTATION', font=btn_font, bg=btn_bg_color, fg='green', command=self.switch_on_off)
        self.on_off.grid(row=row+1, column=col, rowspan=2, padx=x_sm_pad, pady= y_sm_pad, sticky= tk.W + tk.E)

        self.par_seq = tk.Button(frame, text='PARALLEL\nPLAN', font=btn_font, bg=btn_bg_color, fg=btn_fg_color, command=self.switch_par_seq)
        self.par_seq.grid(row=row+1, column=col+2, rowspan=2, padx=x_sm_pad, pady= y_sm_pad, sticky= tk.W + tk.E)

        self.loadcsv = tk.Button(frame, text='GENERATE PLAN\nFROM FILE', font=btn_font, bg=btn_bg_color, fg=btn_fg_color, command= self.generate_plan_from_file)
        self.loadcsv.grid(row=row+1, column=col+5, rowspan=2, padx=x_sm_pad, pady= y_sm_pad, sticky= tk.W + tk.E)
        
        # Generated Plan Section
        self.gen_label = tk.Label(frame, text = "Generated Plan", bg = bg_color, fg='white', pady=title_y_pad, font=title_font, anchor=CENTER)
        self.gen_label.grid(row=row+4, column=col, columnspan=6, padx=x_lg_pad, sticky= tk.W + tk.E)

        self.display_plan = PlanDisplay(frame, col, row=row+5, rowspan=8)

        # Clear
        self.clean = tk.Button(frame, text='CLEAN\nPLAN', font=btn_font, bg=btn_bg_color,fg=btn_fg_color, command=self.clean_plan)
        self.clean.grid(row=row+14, column=col+5, rowspan=2, padx=x_sm_pad, pady= y_sm_pad, sticky= tk.W + tk.E)

        self.ongoing_action_num = 1


    def switch_on_off(self):
        if self.online:
            self.on_off.config(text='OFFLINE\nCOMPUTATION', fg='green')
            self.online = False
        else:
            self.on_off.config(text='ONLINE\nCOMPUTATION', fg='red')
            self.online = True

    def switch_par_seq(self):
        if self.parallel:
            self.par_seq.config(text='SEQUENTIAL\nPLAN', fg='green')
            self.parallel = False
        else:
            self.par_seq.config(text='PARALLEL\nPLAN', fg='green')
            self.parallel = True

    def generate_plan_from_file(self):

        home_path = os.path.abspath('bicrobotics')

        file = filedialog.askopenfile(mode='r', filetypes=[('csv files', '*.csv'), ('all files', '*.*')], initialdir = '/home/bicrobotics/Desktop')

        if file:
            showinfo(title='FILE UPLOAD', message='{} file uploaded correctly. You are now ready to run the tests'.format(file.name))
            self.filepath = os.path.abspath(file.name)

    def clean_plan(self):
        self.cmd_list = []
        self.display_plan.clean_table()


class PickPouchInCoords:

    def __init__(self, frame, pub, row=4, col=3):

        self.pub = pub

        self.gripperlabel = tk.Label(frame, text = "Pick Pouch in Coords", bg = bg_color, fg='white', pady=title_y_pad, font=title_font)
        self.gripperlabel.grid(row=row, column=col, columnspan=3, padx=5, sticky= tk.W + tk.E)

        self.row_label = tk.Label(frame, text = "Row", bg = bg_color, fg='white', font=subtitle_font)
        self.row_label.grid(row=row+2, column=col, columnspan=1, padx=x_sm_pad, pady = y_sm_pad, sticky= tk.W + tk.E)
        self.row_box = tk.Text(frame, bg = 'white', fg='black', font=btn_font, height=1, width=6)
        self.row_box.grid(row=row+1, column=col, padx=x_sm_pad)

        self.col_box = tk.Text(frame, bg = 'white', fg='black', font=btn_font, height=1, width=6)
        self.col_box.grid(row=row+1, column=col+1, padx=x_sm_pad)
        self.row_label = tk.Label(frame, text = "Col", bg = bg_color, fg='white', font=subtitle_font)
        self.row_label.grid(row=row+2, column=col+1, columnspan=1, padx=x_sm_pad, pady = y_sm_pad, sticky= tk.W + tk.E)

        self.button = tk.Button(frame, text='Pick Pouch', bg=btn_bg_color, fg=btn_fg_color, font=btn_font, command=self.button_action)
        self.button.grid(row=row+1, column=col+2, padx=x_sm_pad, sticky= tk.W + tk.E)

    
    def button_action(self):
        # If pressed, has to get the value from text box and SetGripperAperture
        str_row = self.row_box.get("1.0","end-1c")
        str_col = self.col_box.get("1.0","end-1c")

        try:
            row, col = int(str_row), int(str_col)
        except:
            showerror('ERROR', 'Row or / and column value\nnot admissible\n(need int number)')
            return

        if not (row<=8 and col<=10):
            showerror('ERROR', 'Row and column value\nmust be in range col(1-10), row(1-8)')
        else:
            cmd_str = 'PickPouchInCoords|robot|queue|d0_r{}_c{}'.format(row, col)
            self.pub.publish(cmd_str)
    
    
    def button_action_callback(self, action_status):
        if action_status == 'ongoing':
            self.ongoing = True
            self.button.configure(bg=btn_bg_bright)
        else:
            self.ongoing = False
            self.button.configure(bg=btn_bg_color)