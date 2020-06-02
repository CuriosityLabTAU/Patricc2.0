from Tkinter import *
import Tkinter as tk
import os
from os import listdir
from os.path import isfile, join
import threading
import sys
import time
import subprocess
from flow import *
from PIL import Image, ImageTk


# block_player = play_block()
# time.sleep(1)


err = []


def run_script(script):
    x = subprocess.check_output(script.split(' '))
    err.append(x)
    return

scripts = {
    'roscore': 'roscore',
    'rfid': 'rosrun rosserial_python serial_node.py /dev/ttyACM0',
    'expose': 'python ./expose.py',
}


class SessionGUI(tk.Frame):
    def __init__(self, master=None):
        tk.Frame.__init__(self, master)
        self.grid()
        self.create_widgets()

        self.init_ok = False
        self.props_ok = False
        self.set_or_remove_props = 'set'

        self.flow = {}

    def create_widgets(self):

        self.option_add("*Font", "helvetica 34 bold")
        self.option_add("*Label.Font", "helvetica 20 bold")
        self.option_add("*Button.Font", "helvetica 30")

        self.frame_init = tk.LabelFrame(self, labelanchor='nw')
        self.frame_init.grid(column=0, row=0)
        self.button_init = tk.Button(self.frame_init, text='Prepare', command=self.init_session)
        self.button_init.grid(column=1, row=0)
        self.status_variable = StringVar(self)
        self.status_variable.set('Status')
        self.label_status = tk.Label(self.frame_init, textvariable=self.status_variable)
        self.label_status.grid(column=2, row=0)

        self.frame_session = tk.LabelFrame(self, labelanchor='nw', text='Session', width=500)
        self.frame_session.grid(column=0, row=1)
        self.label_session = tk.Label(self.frame_session, text='Session')
        self.label_session.grid(column=0, row=0)

        self.session_file_names = self.get_session_files()
        self.session_file_variable = StringVar(self)
        self.session_file_variable.set('')  # default value
        #OG
        self.text_load_session_file = OptionMenu(self.frame_session,
                                                 self.session_file_variable, *self.session_file_names,
                                                 command=self.update_session_list)
        self.text_load_session_file.grid(column=1, row=0)
        self.text_load_session_file.configure(state=DISABLED)
        #OG

        self.label_robot = tk.Label(self.frame_session, text='Robot:')
        self.label_robot.grid(column=0, row=1)
        self.robot_name_variable = StringVar(self)
        self.robot_name_variable.set('')
        self.label_robot_name = tk.Label(self.frame_session, textvariable=self.robot_name_variable)
        self.label_robot_name.grid(column=1, row=1)

        self.original = Image.open('./images/robot.png')
        self.resized = self.original.resize((100, 100), Image.ANTIALIAS)
        self.robot_image = ImageTk.PhotoImage(self.resized)
        self.label_robot_image = tk.Label(self.frame_session, image=self.robot_image, width=100, height=100)
        self.label_robot_image.grid(column=2, row=1)

        self.frame_props = tk.LabelFrame(self, labelanchor='nw', text='Props')
        self.frame_props.grid(column=0, row=2)
        self.label_props = tk.Label(self.frame_props, text='Props:')
        self.label_props.grid(column=0, row=0)
        self.props_name_variable = []
        self.label_props_name = []
        self.prop_image = []
        self.label_props_image = []
        self.prop_check_image = []
        self.label_props_check_image = []
        for p in range(5):
            self.props_name_variable.append(StringVar(self))
            self.props_name_variable[-1].set('')
            self.label_props_name.append(tk.Label(self.frame_props, textvariable=self.props_name_variable[-1]))
            self.label_props_name[-1].grid(column=p+1, row=0)
            self.prop_image.append(tk.PhotoImage(file='./images/jay.png'))
            self.label_props_image.append(tk.Label(self.frame_props, image=self.prop_image[-1], width=100, height=100))
            self.label_props_image[-1].grid(column=p+1, row=1)
            self.prop_check_image.append(tk.PhotoImage(file='./images/x.png'))
            self.label_props_check_image.append(tk.Label(self.frame_props,
                                                         image=self.prop_check_image[-1], width=50, height=50))
            self.label_props_check_image[-1].grid(column=p+1, row=2)
        self.button_check_props = tk.Button(self.frame_props, text='Refresh', command=self.refresh_props)
        self.button_check_props.grid(column=6, row=2)
        self.button_check_props.configure(state=DISABLED)


        self.frame_run = tk.LabelFrame(self, labelanchor='nw', text='Run session')
        self.frame_run.grid(column=0, row=3)
        self.button_run = tk.Button(self.frame_run, text='Run!', command=self.run_session)
        self.button_run.grid(column=0, row=0)
        self.button_run.configure(state=DISABLED)

        self.frame_finish = tk.LabelFrame(self, labelanchor='nw', text='Finish session')
        self.frame_finish.grid(column=0, row=4)
        self.button_finish = tk.Button(self.frame_finish, text='Finish!', command=self.finish_session)
        self.button_finish.grid(column=0, row=0)
        self.button_finish.configure(state=DISABLED)

        self.final_status_variable = StringVar()
        self.final_status_variable.set('Press Prepare!')
        self.label_final_status_init = tk.Label(self.frame_init, textvariable=self.final_status_variable)
        self.label_final_status_init.grid(column=0, row=0)

        self.label_final_status_run = tk.Label(self.frame_run, textvariable=self.final_status_variable)
        self.label_final_status_run.grid(column=1, row=0)

        self.label_final_status_finish = tk.Label(self.frame_finish, textvariable=self.final_status_variable)
        self.label_final_status_finish.grid(column=1, row=0)


    def init_session(self):
        for script in scripts.values():
            t = threading.Thread(target=run_script, args=(script,))
            t.start()
            threading._sleep(1.0)

        self.init_ok = len(err) == 0
        if self.init_ok:
            self.status_variable.set('OK')
            self.text_load_session_file.configure(state=NORMAL)
            self.session_file_names = self.get_session_files()
            self.session_file_variable.set(self.session_file_names[0])
            self.final_status_variable.set('Select the Appropriate Session!')
        else:
            self.status_variable.set('Check Motors!')

    def get_session_files(self):
        self.session_path = 'flow/'
        self.session_file_names = [f for f in listdir(self.session_path) if isfile(join(self.session_path, f)) and '.txt' in f]
        return self.session_file_names

    def update_session_list(self, event):
        FlowNode.block_player = play_block()
        FlowNode.block_player.base_path = './'
        time.sleep(1)
        self.load_session(self.session_path + self.session_file_variable.get())

    def load_session(self, file_name):
        self.final_status_variable.set('Switch Robot and Set Props!')
        self.robot_name_variable.set('Error')
        for p in range(5):
            self.props_name_variable[p].set('')
        try:
            self.flow = {}
            flow_sequence = open(file_name).read().split('\n')
            for step in flow_sequence:
                step_desc = step.split(',')
                # print(step_desc)
                if step_desc[0].lstrip() == 'robot':
                    self.flow['robot'] = step_desc[1].lstrip()
                    self.robot_name_variable.set(self.flow['robot'])
                    self.original = Image.open('./images/%s.png' % self.flow['robot'])
                    self.resized = self.original.resize((100, 100), Image.ANTIALIAS)
                    self.robot_image = ImageTk.PhotoImage(self.resized)
                    self.label_robot_image.configure(image=self.robot_image)
                    self.label_robot_image.image = self.robot_image
                elif step_desc[0].lstrip() == 'props':
                    self.flow['props'] = step_desc[1].lstrip().split(' ')
                    for i, prop_name in enumerate(self.flow['props']):
                        self.props_name_variable[i].set(prop_name.lstrip())
                        self.original = Image.open('./images/%s.jpg' % self.flow['props'][i])
                        self.resized = self.original.resize((100, 100), Image.ANTIALIAS)
                        self.prop_image[i] = ImageTk.PhotoImage(self.resized)
                        self.label_props_image[i].configure(image=self.prop_image[i])
                        self.label_props_image[i].image = self.prop_image[i]

            self.check_props()
        except:
            self.props_ok = False
            self.final_status_variable.set('Set the Appropriate Props!')
        self.check_run()
        self.button_check_props.configure(state=NORMAL)

    def refresh_props(self):
        if self.set_or_remove_props == 'set':
            self.check_props()
        else:
            self.check_remove_props()

    def check_props(self):
        found_props = FlowNode.block_player.rfids
        found_all = True
        for i in range(len(self.props_name_variable)):
            if self.props_name_variable[i].get() in found_props:
                #self.prop_check_image[i] = tk.PhotoImage(file='./images/v.png')

                self.original = Image.open('./images/v.png')
                self.resized = self.original.resize((50, 50), Image.ANTIALIAS)
                self.prop_check_image[i] = ImageTk.PhotoImage(self.resized)

            else:
                self.original = Image.open('./images/x.png')
                self.resized = self.original.resize((50, 50), Image.ANTIALIAS)
                self.prop_check_image[i] = ImageTk.PhotoImage(self.resized)
                found_all = False
            self.label_props_check_image[i].configure(image=self.prop_check_image[i])
            self.label_props_check_image[i].image = self.prop_check_image[i]
        self.props_ok = found_all
        if not self.props_ok:
            self.final_status_variable.set('Set the Appropriate Props!')
        self.check_run()

    def check_run(self):
        if self.init_ok and self.props_ok:
            self.button_run.configure(state=NORMAL)
            self.final_status_variable.set('Please, Start Recording Camera!')
        else:
            self.button_run.configure(state=DISABLED)

    def worker(self):
        os.system('rosbag record -a -o data/robot_puppet_ID001.bag')
        #os.system('rosbag record -a -x "/cam0/usb_cam/image_raw/compressed" "/cam0/usb_cam/image_raw/theora" -o data/physical_curiosity_big_experiment_' + str(subject_id) + '.bag')


    def run_session(self):
        flow = FlowNode()
        flow.base_path = './'
        flow.load(self.session_path + self.session_file_variable.get())

        t1 = threading.Thread(target=self.worker)
        t1.start()
        threading._sleep(2.5)

        flow.run()
        self.button_run.configure(state=DISABLED)
        self.final_status_variable.set('Please, Remove All Props!')
        self.set_or_remove_props = 'remove'
        self.check_remove_props()

    def check_remove_props(self):
        found_props = FlowNode.block_player.rfids
        remove_all = True
        for i in range(len(self.props_name_variable)):
            if self.props_name_variable[i].get() in found_props:
                self.prop_check_image[i] = tk.PhotoImage(file='./images/x.png')
                remove_all = False
            else:
                self.prop_check_image[i] = tk.PhotoImage(file='./images/v.png')
            self.label_props_check_image[i].configure(image=self.prop_check_image[i])
            self.label_props_check_image[i].image = self.prop_check_image[i]
        if not remove_all:
            self.final_status_variable.set('Please, Remove All Props!')
        else:
            self.button_finish.configure(state=NORMAL)
            self.final_status_variable.set('Please, STOP Recording Camera!')

    def finish_session(self):
        print('Go to sleep')


app = SessionGUI()
app.master.title('Curiosity Robotics: Session Controller')
app.master.geometry('900x1000')
app.mainloop()