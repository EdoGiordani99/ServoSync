#!/usr/bin/env python

import tkinter as tk
from tkinter import *
from tkinter import ttk

from gui_utils import *

import json
import rospy
import threading
import tkinter as tk
import time

from tkinter import *
from tkinter import ttk
from PIL import Image, ImageTk
from std_msgs.msg import String
from tkinter.messagebox import *
from time import strftime, localtime

from planner import PlanConverter, Planner
from PostaDatabaseClient import PostaSampleTray

class GUI:

    def __init__(self):

        os.chdir(os.path.abspath('/home/bicrobotics/ur5ws/src/sud2_moveit_config/scripts'))

        self.root = tk.Tk()
        self.root.title('SUD GUI')
        self.root.option_add("*TCombobox*Listbox*Font", subtitle_font)

        # Root Configuration
        self.root.geometry("2100x1100")
        self.root.configure(background=bg_color)

        self.style = ttk.Style()
        self.style.configure("Treeview", 
                             background=bg_color, 
                             foreground='white', 
                             fieldbackground=bg_light_color,
                             font=btn_font)
        

        # State memory
        self.last_state = {}
        self.last_moveit_error_timestamp = 0
        self.last_error_timestamp = 0
        self.plan_ongoing = False

        # GUI Publisher
        self.gui_pub = rospy.Publisher('sud_posta_commands', String, queue_size=10)
        rospy.init_node('gui', anonymous=True)
        rospy.loginfo("GUI Node Started")

        # State Subscriber
        rospy.Subscriber('sud_posta_state', String, self.state_callback)

        # ----------------------
        #       PAGE SWITCH
        # ----------------------

        self.pages = {'Home': 0, 
                      'ManualControl': 1,
                      'PlanControl':2, 
                      'GeneralControl': 3}

        self.page_frame = tk.Frame(self.root, bg=bg_color)
        self.page_frame.grid(row=0, column=0)

        self.manu_btn = tk.Button(self.page_frame, text='MANUAL\nCONTROL', font=btn_font, bg=bg_color, fg=btn_fg_color, command = lambda: self.select_page('ManualControl'))
        self.manu_btn.grid(row=0, column=0, pady=y_sm_pad, padx=x_sm_pad, sticky= tk.W + tk.E)

        self.plan_btn = tk.Button(self.page_frame, text='PLANNER\nCONTROL', font=btn_font, bg=bg_color, fg=btn_fg_color, command = lambda: self.select_page('PlanControl'))
        self.plan_btn.grid(row=1, column=0, pady=y_sm_pad, padx=x_sm_pad, sticky= tk.W + tk.E)

        self.general_btn = tk.Button(self.page_frame, text='GENERAL\nCONTROL', font=btn_font, bg=bg_color, fg=btn_fg_color, command = lambda: self.select_page('GeneralControl'))
        self.general_btn.grid(row=2, column=0, pady=y_sm_pad, padx=x_sm_pad, sticky= tk.W + tk.E)

        self.page_btn_list = [None, self.manu_btn, self.plan_btn, self.general_btn]

        self.time_start = time.time()


        # ----------------------
        #  MANUAL CONTROL PAGE 
        # ----------------------

        MANU_ROW = 1
        MANU_COL = 2

        self.manual_frame = tk.Frame(self.root, bg=bg_color, width=300, height=300)
        self.manual_frame.grid(row=0, column=2)

        # Drawers Section
        self.drawers_section = DrawersSection(self.manual_frame, self.gui_pub, row=MANU_ROW+1, col=MANU_COL+2)
        # Space Row
        self.space2 = YSpace(self.manual_frame, MANU_ROW+3)
        # Drawer Imaging Section
        self.go_to_drawer_imaging_btn = GoToDrawerImaging(self.manual_frame, self.gui_pub, row=MANU_ROW+4, col=MANU_COL+2)
        # Space Row
        self.space2 = YSpace(self.manual_frame, MANU_ROW+7)
        # Go To Section
        self.goto_section = GoToSection(self.manual_frame, self.gui_pub, row=MANU_ROW+8, col=MANU_COL+2)
        # Space Row
        self.space2 = YSpace(self.manual_frame, MANU_ROW+11)
        # Actions Section
        self.action_section = ActionSection(self.manual_frame, self.gui_pub, row=MANU_ROW+12, col=MANU_COL+2)
        # Space Row
        self.space2 = YSpace(self.manual_frame, MANU_ROW+18)

        # New Gripper Section
        GRIPPER_ROW = MANU_ROW+19
        GRIPPER_COL = MANU_COL+2
        self.gripperlabel = tk.Label(self.manual_frame, text = "Gripper", bg = bg_color, fg='white', pady=title_y_pad, font=title_font)
        self.gripperlabel.grid(row=GRIPPER_ROW, column=GRIPPER_COL, columnspan=2, padx=5, sticky= tk.W + tk.E)
        self.gripperbtn = GripperButton(self.manual_frame, self.gui_pub, row=GRIPPER_ROW+1, col=GRIPPER_COL)
        self.pouch_in_gripper = PouchInGripper(self.manual_frame, row=GRIPPER_ROW+1, col=GRIPPER_COL+1)
        self.gripper_aperture_setter = GripperApertureSetter(self.manual_frame, self.gui_pub, row=GRIPPER_ROW+4, col=GRIPPER_COL+1)

        self.pouch_in_coords = PickPouchInCoords(self.manual_frame, self.gui_pub, GRIPPER_ROW, GRIPPER_COL+3)

        # Bottom Right Margin
        self.middle_space = tk.Label(self.manual_frame, text = "", bg = bg_color, fg=bg_color, pady=title_y_pad, font=title_font)
        self.middle_space.grid(row=MANU_ROW+22, column=0, padx=5, sticky= tk.W + tk.E)

        # ----------------------
        #  PLAN CONTROL PAGE 
        # ----------------------

        PLAN_ROW = 1
        PLAN_COL = 2

        self.plan_frame = tk.Frame(self.root, bg=bg_color, width=300, height=300)
        self.plan_frame.grid(row=0, column=2)

        self.middle_space = tk.Label(self.plan_frame, text = ".", bg = bg_color, fg=bg_color, pady=title_y_pad, font=title_font)
        self.middle_space.grid(row=1, column=0, padx=5, sticky= tk.W + tk.E)

        # Plan Section
        self.plan_execution_status = ''
        self.plan_section = PlanSection(self.plan_frame, self.gui_pub, row=PLAN_ROW, col=PLAN_COL+2)

        self.execute = tk.Button(self.plan_frame, text='EXECUTE\nPLAN', font=btn_font, bg=btn_bg_color, fg=btn_fg_color, command=self.execute_plan)
        self.execute.grid(row=PLAN_ROW+14, column=PLAN_COL+2, rowspan=2, padx=x_sm_pad, pady= y_sm_pad, sticky= tk.W + tk.E)

        self.playpause = tk.Button(self.plan_frame, text='PAUSE\nPLAN', font=btn_font, bg=btn_bg_color, fg=btn_fg_color, command=self.play_pause_plan)
        self.playpause.grid(row=PLAN_ROW+14, column=PLAN_COL+3, rowspan=2, padx=x_sm_pad, pady= y_sm_pad, sticky= tk.W + tk.E)

        self.stop = tk.Button(self.plan_frame, text='STOP PLAN\nEXECUTION', font=btn_font, bg='red', fg=bg_color, command=self.stop_plan_execution)
        self.stop.grid(row=PLAN_ROW+14, column=PLAN_COL+4, rowspan=2, padx=x_sm_pad, pady= y_sm_pad, sticky= tk.W + tk.E)

        self.middle_space = tk.Label(self.plan_frame, text = ".", bg = bg_color, fg=bg_color, pady=title_y_pad, font=title_font)
        self.middle_space.grid(row=17, column=13, padx=5, sticky= tk.W + tk.E)
        self.middle_space = tk.Label(self.plan_frame, text = ".", bg = bg_color, fg=bg_color, pady=title_y_pad, font=title_font)
        self.middle_space.grid(row=18, column=13, padx=5, sticky= tk.W + tk.E)


        # ----------------------
        #  GENERAL CONTROL PAGE 
        # ----------------------

        GEN_ROW = 0
        GEN_COL = 2

        self.gen_frame = tk.Frame(self.root, bg=bg_color, width=300, height=300)
        self.gen_frame.grid(row=GEN_ROW, column=GEN_COL)

        self.middle_space = tk.Label(self.gen_frame, text = "..................", bg = bg_color, fg=bg_color, pady=title_y_pad, font=title_font)
        self.middle_space.grid(row=GEN_ROW+25, column=0, padx=5, sticky= tk.W + tk.E)
        self.middle_space = tk.Label(self.gen_frame, text = "..................", bg = bg_color, fg=bg_color, pady=title_y_pad, font=title_font)
        self.middle_space.grid(row=GEN_ROW+26, column=0, padx=5, sticky= tk.W + tk.E)

        self.genlabel = tk.Label(self.gen_frame, text = "General Section", bg = bg_color, fg='white', pady=0, font=title_font)
        self.genlabel.grid(row=GEN_ROW+2, column=GEN_COL, columnspan=6, padx=5, sticky= tk.W + tk.E)

        # Number of Pouch + Date Time
        self.pouches_display = PouchesDisplay(self.gen_frame, row=GEN_ROW+3, col=GEN_COL)
        self.time_display = TimeDisplay(self.gen_frame, row=GEN_ROW+3, col=GEN_COL+4)
        # Space Row
        self.space2 = YSpace(self.gen_frame, GEN_ROW+5)
        # Scale
        self.scale_disp = ScaleDisplay(self.gen_frame, self.gui_pub, row=GEN_ROW+6, col=GEN_COL)
        # Space Row
        self.space2 = YSpace(self.gen_frame, GEN_ROW+9)
        # Mark 10 Strength
        self.mark10_section = Mark10Section(self.gen_frame, self.gui_pub, row=GEN_ROW+10, col=GEN_COL)
        # Space Row
        self.space2 = YSpace(self.gen_frame, GEN_ROW+13)
        # General Section
        self.general_section = GeneralSection(self.gen_frame, self.gui_pub, row=GEN_ROW+14, col=GEN_COL)

        self.client_status = PostaClientStatus(self.gen_frame, row=GEN_ROW+20, col = GEN_COL)

        # Bottom Right Margin
        self.middle_space = tk.Label(self.gen_frame, text = "..................", bg = bg_color, fg=bg_color, pady=title_y_pad, font=title_font)
        self.middle_space.grid(row=GEN_ROW+25, column=13, padx=5, sticky= tk.W + tk.E)
        

        # ----------------------
        #  QUEUE SECTION SECTION 
        # ----------------------
        QUE_ROW = 0
        QUE_COL = 4
        self.middle_space = tk.Label(self.root, text = "....", bg = bg_color, fg=bg_color, pady=title_y_pad, font=title_font)
        self.middle_space.grid(row=QUE_ROW, column=QUE_COL-1, padx=5, sticky= tk.W + tk.E)

        self.queue_frame = tk.Frame(self.root, bg=bg_color, width=300, height=300)
        self.queue_frame.grid(row=0, column=QUE_COL)

        self.robot_queue = QueueList(self.queue_frame, self.gui_pub, title='Robot Queue', row=1, col=0, rowspan=4)
        self.scale_queue = QueueList(self.queue_frame, self.gui_pub, title='Scale Queue', row=6, col=0, rowspan=4)

        self.middle_space = tk.Label(self.queue_frame, text = "....", bg = bg_color, fg=bg_color, pady=title_y_pad, font=title_font)
        self.middle_space.grid(row=1, column=4, padx=5, sticky= tk.W + tk.E)

        self.mark10s_queue = QueueList(self.queue_frame, self.gui_pub, title='Mark10S Queue', row=1, col=5, rowspan=4)
        self.mark10t_queue = QueueList(self.queue_frame, self.gui_pub, title='Mark10T Queue', row=6, col=5, rowspan=4)

        self.middle_space = tk.Label(self.queue_frame, text = "....", bg = bg_color, fg=bg_color, pady=title_y_pad, font=title_font)
        self.middle_space.grid(row=12, column=4, padx=5, sticky= tk.W + tk.E)

        self.agents_queues = {'robot': self.robot_queue, 
                              'scale': self.scale_queue, 
                              'mark10s': self.mark10s_queue, 
                              'mark10t': self.mark10t_queue}

        #self.emergency_stop = StopBtn(self.queue_frame, self.gui_pub, row = 13, col=0, columnspan=20)

        self.emergency_stop = tk.Button(self.queue_frame, text='EMERGENCY\nSTOP', height=4, bg='red', fg='black', pady=y_sm_pad, font=title_font, anchor=CENTER, command=self.Stop)
        self.emergency_stop.grid(row=13, column=0, padx=x_lg_pad, pady=y_sm_pad, rowspan=4, columnspan=20, sticky= tk.W + tk.E)

        # ----------------------
        self.plan_frame.tkraise()
        self.change_page_idx('PlanControl')

        self.root.mainloop()


    #---------------------------
    #   STATE UPDATE METHODS
    #---------------------------

    def state_callback(self, data):
        """ 
        Updates the state of the GUI everytime a new_state is received. 
        To update GUI state, we only consider value that changed from 
        previous state. 
        """
        state_string = data.data

        global new_state
        new_state = json.loads(state_string)

        for k, v in new_state.items():
            
            if k == 'timestamp':  
                day_time = strftime('%Y-%m-%d\n%H:%M:%S', localtime(v))
                self.time_display.change_time(day_time)
                
            if k[:-2] == 'drawer':
                num = int(k.split('_')[1])
                self.drawers_section.open_close_drawer_num(num, v)

            elif k == 'gripper_aperture_mm':
                self.gripperbtn.button_state_callback(v)
                self.gripper_aperture_setter.change_value(v)

            elif k == 'number_of_detected_pouches':
                self.pouches_display.change_num_pouches(v)
            
            elif k == 'pouch_in_gripper':
                self.pouch_in_gripper.change_value(v)

            elif k == 'scale_weight':
                self.scale_disp.change_weight(v)
                scale_timestamp = new_state['scale_timestamp']
                day_time = strftime('%Y-%m-%d\n%H:%M:%S', localtime(scale_timestamp))
                self.scale_disp.change_time(day_time)
      
            elif k == 'posta_client_strength_online': 
                self.client_status.change_status(v)

            elif k == 'mark10S_instrument_ready':
                self.mark10_section.change_mark10_ready(v)
            
            elif k == 'mark10S_test_completed':
                self.mark10_section.change_test_status(v)
            
            elif k == 'mark10S_plate_distance':
                self.mark10_section.change_plate_distance(v)

            elif k == 'mark10S_plate_moving_up': 
                self.general_section.change_plate(v)

            elif k == 'moveit_trajectory_status':
                self.general_section.change_traj(v)

            elif k == 'robot':
                self.general_section.change_robot(v)

            elif k == 'error_msg':
                # if not self.plan_execution_status == 'ongoing':
                #     self.error_callback(v)
                self.error_callback(v)
            
            elif k == 'moveit_error_msg':
                if not self.plan_execution_status == 'ongoing':
                    self.moveit_error_callback(v)
            
            elif k == 'agents_status':
                self.update_agents_status(v)
            
            elif k[-11:] == 'action_list':
                agent, _, _ = k.split('_')
                v = json.loads(v)
                self.agents_queues[agent].update_table(v)
            
            elif k == 'undetected_pouches':
                self.undetected_pouches = json.loads(v)
                print('UPLOAD {}\t{}'.format(time.time(), self.undetected_pouches))


    def error_callback(self, error_msg):
        try:
            err_type, msg, timestamp = error_msg.data.split('|')
        except:
            pass
        try:
            err_type, msg, timestamp = error_msg.split('|')
        except:
            return

        if self.last_error_timestamp != timestamp and not self.plan_execution_status == 'ongoing':

            if err_type == 'ERROR':
                showerror(title=err_type, message=msg)
            elif err_type == 'WARNING':
                showwarning(title=err_type, message=msg)
            elif err_type == 'INFO':
                showinfo(title=err_type, message=msg)

            self.last_error_timestamp = timestamp


    def moveit_error_callback(self, error_msg):

        if error_msg is not None:
            err_type, msg, timestamp = error_msg.split('|')
            if self.last_moveit_error_timestamp != timestamp:
                showerror(title=err_type, message=msg)
                self.last_moveit_error_timestamp = timestamp


    def update_agents_status(self, agents_status):

        agents_status = json.loads(agents_status)

        # Agent status is a dictionary with:
        # {'robot' : ('PickNextPouch', 'ongoing', p1, p2), ...}

        for agent, act_stat in agents_status.items():

            action, status, p1, p2 = act_stat

            if action == None: 
                continue

            if action == 'OpenDrawer' or action == 'CloseDrawer':
                self.drawers_section.change_action_status(int(p1), status)
            
            elif action == 'GoToDrawerImaging':
                self.go_to_drawer_imaging_btn.change_action_status(int(p1), status)
            
            elif action == 'CloseGripper' or action == 'OpenGripper':
                self.gripperbtn.button_action_callback(status)

            elif action in self.action_section.available_actions:
                self.action_section.actions_btn_list[action].button_action_callback(status)

            elif action in self.general_section.available_actions:
                self.general_section.actions_btn_list[action].button_action_callback(status)
            
            elif action == 'GoTo':
                self.goto_section.button_action_callback(status)

            elif action == 'PickPouchInCoords':
                self.pouch_in_coords.button_action_callback(status)


    def parse_robot_action_status(self, msg):
        
        values = msg.split('|')

        ongoing = True if values[0] == 'True' else False
        action = values[1]

        p1, p2 = None, None

        if len(values) > 2:
            p1 = values[2]
        
        if len(values) > 3:
            p2 = values[3]
        
        return ongoing, action, p1, p2
    

    #---------------------------
    #       GUI METHODS
    #---------------------------

    def select_page(self, page_name):

        self.change_page_idx(page_name)
        
        if page_name == 'ManualControl':
            self.manual_frame.tkraise()
        elif page_name == 'PlanControl':
            self.plan_frame.tkraise()
        elif page_name == 'GeneralControl':
            self.gen_frame.tkraise()
    
    def change_page_idx(self, page_name):

        for btn in self.page_btn_list:
            if btn is not None:
                btn.configure(fg=btn_fg_color)
        
        idx = self.pages[page_name]
        self.page_btn_list[idx].configure(fg='white')

    def Stop(self):

        if self.plan_execution_status == 'ongoing':
            self.plan_execution_status = 'stop'
            self.gui_pub.publish('StopAll|all|start')
            self.plan_section.cmd_list = []
            self.plan_section.display_plan.clean_table()
        else:
            self.gui_pub.publish('StopAll|all|start')

    #---------------------------
    #      PLANNER METHODS
    #---------------------------

    def execute_plan(self):
        # Send commands split by split
        self.plan_execution_status = 'ongoing'
        self.gui_pub.publish('ExecutePlan|planner|start|{}'.format(self.plan_section.filepath))
        self.planner_thread = threading.Thread(target=self.NewPlannerThread)
        self.planner_thread.start()

    def stop_plan_execution(self):
        self.plan_execution_status = 'stop'
        self.gui_pub.publish('StopAll|all|start')
        self.gui_pub.publish('ExecutePlan|planner|stop|{}'.format(self.plan_section.filepath))
        self.plan_section.cmd_list = []
        self.plan_section.display_plan.clean_table()

    def play_pause_plan(self):
        if self.plan_execution_status == 'ongoing':
            self.plan_execution_status = 'pause'
            self.gui_pub.publish('StopAll|all|start')
            self.playpause.configure(text='RESUME\nPLAN')
        elif self.plan_execution_status == 'pause':
            self.plan_execution_status = 'ongoing'
            self.playpause.configure(text='PAUSE\nPLAN')

    def free_system(self, bypass = None):

        if self.plan_execution_status == 'pause':
            return False
        
        for agent, queue in self.agents_queues.items():

            if agent == bypass:
                continue
            else:
                if len(queue) != 0:
                    return False
        
        return True

    def NewPlannerThread(self):

        opened = self.drawers_section.is_drawer_open()

        if opened:
            showwarning(title='STARTING PLAN EXECUTION', message='Closing drawer {} before starting the plan execution'.format(opened))
            self.gui_pub.publish('CloseDrawer|robot|queue|{}'.format(opened))
        else:
            pass

        self.planner = Planner()
        self.converter = PlanConverter()
        self.plan_execution_status = 'ongoing'

        csv_path = self.plan_section.filepath
        #csv_path = 'PouchesTest.csv'
        self.gui_pub.publish('ExecutePlan|planner|start|{}'.format(csv_path))

        all_content = pd.read_csv(filepath_or_buffer=csv_path, header=0)

        priority_groups = self.planner.order_cv2_on_priority(all_content)

        ordered_groups = self.planner.order_priority_on_drawers(priority_groups)

        priority_drawers_content = self.planner.from_groups_to_content(ordered_groups)

        for priority, drawers_content in priority_drawers_content.items():

            for drawer_num, content_list in drawers_content.items():

                self.gui_pub.publish('OpenDrawer|robot|queue|{}'.format(drawer_num))

                rospy.sleep(1)

                while len(self.robot_queue) != 0:
                    rospy.sleep(0.5)

                detected_content_list = []
                undetected_content_list = []

                rospy.sleep(1)
                
                # Reading non detected pouches
                for pouch in content_list:
                    rowcol = [pouch.row, pouch.column]
                    if rowcol not in self.undetected_pouches:
                        detected_content_list.append(pouch)
                    else:
                        undetected_content_list.append(pouch)

                print([[pouch.row, pouch.column] for pouch in detected_content_list])
                print([[pouch.row, pouch.column] for pouch in undetected_content_list])

                drawer_plan = self.planner.generate_drawer_plan(content_list=detected_content_list, 
                                                        max_pouches_num=4,
                                                        drawer_num = drawer_num,
                                                        drawer_is_open=True, 
                                                        close_drawer=False, 
                                                        online=False,  
                                                        parallelize=self.plan_section.parallel)
                
                if drawer_plan:
                    drawer_cmd_list = self.converter.convert(drawer_plan, drawer_num=drawer_num)
                else:
                    self.gui_pub.publish('CloseDrawer|robot|queue|{}'.format(drawer_num))
                    break

                plan_to_execute = drawer_cmd_list[:]

                while (len(plan_to_execute) != 0 and 
                    (self.plan_execution_status == 'ongoing' or
                        self.plan_execution_status == 'pause')):
                    
                    if self.free_system():
                        self.plan_section.display_plan.update_table(plan_to_execute)
                        cmd_to_do = plan_to_execute.pop(0)

                        if type(cmd_to_do) == str:
                            self.gui_pub.publish(cmd_to_do)

                        elif type(cmd_to_do) == list:
                            
                            # the agent of the palallelized action
                            p_agent = cmd_to_do[0].split('|')[1]

                            # iterating through list
                            while (len(cmd_to_do) != 0 and 
                                (self.plan_execution_status == 'ongoing' or
                                self.plan_execution_status == 'pause')):
                                
                                # parallel action to execute
                                if self.free_system(bypass = p_agent):
                                    paction = cmd_to_do.pop(0)
                                    self.gui_pub.publish(paction)
                                rospy.sleep(0.5)

                    rospy.sleep(0.5)

                    self.plan_section.display_plan.update_table(plan_to_execute)

                    if self.plan_execution_status == 'stop':
                        break
                
                self.gui_pub.publish('CloseDrawer|robot|queue|{}'.format(drawer_num))

                if self.plan_execution_status == 'stop':
                    break
    

if __name__ == '__main__':

    try: 
        g = GUI()

        

    except rospy.ROSInterruptException:

        pass