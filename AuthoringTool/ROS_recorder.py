from Tkinter import *
import Tkinter as tk
import rospy
from std_msgs.msg import String
from datetime import datetime
import pickle
import time
import thread
from dynamixel_hr_ros.msg import *
import csv
import pygame
from os import listdir
from os.path import isfile, join
from functools import partial


class Application(tk.Frame):
    def __init__(self, master=None):
        rospy.init_node('ros_recorder')

        self.rfids = [None for i in range(5)]
        self.rifd_sub = rospy.Subscriber('/rfid', String, self.rfid_callback)

        tk.Frame.__init__(self, master)
        self.grid()

        self.rec = False
        self.record_list = []
        self.filename = ''

        self.inter_block = []
        self.start_time = datetime.now()

        pygame.init()
        pygame.mixer.init()

        self.publishers = {
            '/skeleton_angles': rospy.Publisher('skeleton_angles', String, queue_size=10),
            # '/affdex_data': rospy.Publisher('affdex_data', AffdexFrameInfo,queue_size=10),
            '/lip_angles': rospy.Publisher('lip_angles', String, queue_size=10),
            '/dxl/command_position': rospy.Publisher('/dxl/command_position', CommandPosition, queue_size=10)
        }

        self.overide_motors = [0 for i in range(8)]
        self.created = False
        self.create_widgets()

    def get_path_name(self, sub_path):
        if 'home' in self.text_robot_name.get():
            return self.text_robot_name.get() + '/' + sub_path + '/'
        else:
            return sub_path + '/' + self.text_robot_name.get() + '/'

    def rfid_callback(self, data):
        msg = data.data
        for i in range(5):
            rfid = msg[i*8:(i+1)*8]
            if '----' in rfid:
                self.rfids[i] = None
            else:
                self.rfids[i] = rfid

            try:
                self.buttons_rfid[i].text = '%d, %s' % (i+1, self.rfids[i])
                self.buttons_rfid[i].refresh()
            except:
                pass
        if not self.created:
            self.create_widgets()

    def create_widgets(self):
        self.created = True

        self.frame_robot = tk.LabelFrame(self, labelanchor='nw', text='Robot')
        self.frame_robot.grid(column=0, row=0)
        self.label_robot_name = tk.Label(self.frame_robot, text='Name:')
        self.label_robot_name.grid(column=0, row=0)

        self.text_robot_name = tk.Entry(self.frame_robot, width=50)
        self.text_robot_name.insert(tk.END, '/home/gorengordon/PycharmProjects/run_general_robot_script/neo') #'hri_01')
        self.text_robot_name.grid(column=1, row=0)

        self.button_robot_set = tk.Button(self.frame_robot, text='set', command=self.set_robot)
        self.button_robot_set.grid(column=2, row=0)


        self.frame_record = tk.LabelFrame(self, labelanchor='n', text='RECORD ANIMATION BLOCK')
        self.frame_record.grid(column=0, row=1)

        self.label_saveas = tk.Label(self.frame_record, text='save as')
        self.label_saveas.grid(column=0, row=0)

        self.text_save_file = tk.Entry(self.frame_record, width=30)
        self.text_save_file.insert(tk.END, 'fuzzy_idle')
        self.text_save_file.grid(column=1, row=0)

        self.button_record = tk.Button(self.frame_record, text='record', command=self.start_record)
        self.button_record.grid(column=0, row=1)

        self.button_stop_rec = tk.Button(self.frame_record, text='stop', command=self.stop_record)
        self.button_stop_rec.grid(column=1, row=1)

        self.label_stop_after = tk.Label(self.frame_record, text='after: ')
        self.label_stop_after.grid(column=2, row=1)

        self.text_stop_after = tk.Entry(self.frame_record, width=12)
        self.text_stop_after.insert(tk.END, '0')
        self.text_stop_after.grid(column=3, row=1)

        self.button_replay_bag = tk.Button(self.frame_record, text='play sound & lip', command=self.play_sound_and_lip)
        self.button_replay_bag.grid(column=4, row=1)

        self.button_replay_block = tk.Button(self.frame_record, text='replay block', command=self.replay_block)
        self.button_replay_block.grid(column=5, row=1)

        self.button_replay_and_record_block = tk.Button(self.frame_record, text='replay & record block',
                                                        command=self.replay_and_record_block)
        self.button_replay_and_record_block.grid(column=4, row=2)


        self.radio_value = tk.IntVar()
        self.radio_bag = tk.Radiobutton(self.frame_record, text='bag only', variable=self.radio_value, value=1)
        self.radio_bag.grid(column=0, row=2)
        self.radio_block = tk.Radiobutton(self.frame_record, text='block', variable=self.radio_value, value=2)
        self.radio_block.grid(column=1, row=2)
        self.radio_mixed = tk.Radiobutton(self.frame_record, text='mixed', variable=self.radio_value, value=3)
        self.radio_mixed.grid(column=2, row=2)


        self.frame_lipsync = tk.LabelFrame(self, labelanchor='nw', text='LIP SYNC BLOCK')
        self.frame_lipsync.grid(column=0, row=2)
        col_ind = 0

        self.loadbag_value = IntVar()
        self.check_loadbag = tk.Checkbutton(self.frame_lipsync, variable=self.loadbag_value)
        self.check_loadbag.grid(column=col_ind, row=0)
        col_ind += 1
        self.label_loadbag = tk.Label(self.frame_lipsync, text='load bag')
        self.label_loadbag.grid(column=col_ind, row=0)
        col_ind += 1

        self.text_loadbag_file = tk.Entry(self.frame_lipsync, width=30)
        self.text_loadbag_file.insert(tk.END, 'bag_wheels_1')
        self.text_loadbag_file.grid(column=col_ind, row=0)
        col_ind += 1

        self.label_bag_offset = tk.Label(self.frame_lipsync, text='offset')
        self.label_bag_offset.grid(column=col_ind, row=0)
        col_ind += 1

        self.text_bag_offset = tk.Entry(self.frame_lipsync, width=20)
        self.text_bag_offset.insert(tk.END, '0.0')
        self.text_bag_offset.grid(column=col_ind, row=0)
        col_ind += 1

        col_ind = 0
        self.loadlip_value = IntVar()
        self.check_loadlip = tk.Checkbutton(self.frame_lipsync, variable=self.loadlip_value)
        self.check_loadlip.grid(column=col_ind, row=1)
        col_ind += 1

        self.label_loadlip = tk.Label(self.frame_lipsync, text='load lip')
        self.label_loadlip.grid(column=col_ind, row=1)
        col_ind += 1

        self.lip_file_names = ['fuzzy.csv']
        self.lip_file_variable = StringVar(self)
        self.lip_file_variable.set(self.lip_file_names[0]) # default value
        self.text_loadlip_file = OptionMenu(self.frame_lipsync, self.lip_file_variable, *self.lip_file_names)
        self.text_loadlip_file.grid(column=col_ind, row=1)
        col_ind += 1

        self.label_lip_offset = tk.Label(self.frame_lipsync, text='offset')
        self.label_lip_offset.grid(column=col_ind, row=1)
        col_ind += 1

        self.text_lip_offset = tk.Entry(self.frame_lipsync, width=50)
        self.text_lip_offset.insert(tk.END, '0.0')
        self.text_lip_offset.grid(column=col_ind, row=1)
        col_ind += 1

        col_ind = 0
        self.loadsound_value = IntVar()
        self.check_loadsound = tk.Checkbutton(self.frame_lipsync, variable=self.loadsound_value)
        self.check_loadsound.grid(column=col_ind, row=2)
        col_ind += 1

        self.label_loadsound = tk.Label(self.frame_lipsync, text='load sound')
        self.label_loadsound.grid(column=col_ind, row=2)
        col_ind += 1

        self.sound_file_names = ['fuzzy.mp3']
        self.sound_file_variable = StringVar(self)
        self.sound_file_variable.set(self.sound_file_names[0]) # default value
        self.text_loadsound_file = OptionMenu(self.frame_lipsync, self.sound_file_variable, *self.sound_file_names)
        self.text_loadsound_file.grid(column=col_ind, row=2)
        col_ind += 1
        
        self.label_sound_offset = tk.Label(self.frame_lipsync, text='offset')
        self.label_sound_offset.grid(column=col_ind, row=2)
        col_ind += 1
        
        self.text_sound_offset = tk.Entry(self.frame_lipsync, width=50)
        self.text_sound_offset.insert(tk.END, '0.0')
        self.text_sound_offset.grid(column=col_ind, row=2)
        col_ind += 1

        # control motors
        self.frame_motors = tk.LabelFrame(self, labelanchor='n', text='Motors')
        self.frame_motors.grid(column=0, row=3)
        self.label_motor = tk.Label(self.frame_motors, text='Motor:')
        self.label_motor.grid(column=0, row=0)

        self.motor_numbers = [str(i) for i in range(8)]
        self.motor_variable = StringVar(self)
        self.motor_variable.set(2) # default value
        self.text_motor = OptionMenu(self.frame_motors, self.motor_variable, *self.motor_numbers)
        self.text_motor.grid(column=1, row=0)

        self.button_set_motor = tk.Button(self.frame_motors, text='set motor', command=self.set_motor)
        self.button_set_motor.grid(column=2, row=0)

        # RIFD pointers
        self.frame_rfid = tk.LabelFrame(self, labelanchor='n', text='RFID')
        self.frame_rfid.grid(column=0, row=4)
        self.buttons_rfid = []
        for i in range(5):
            command_with_arg = partial(self.set_rfid, self.rfids[i])
            self.buttons_rfid.append(tk.Button(self.frame_rfid, text='%d,%s' % (i+1, self.rfids[i]),
                                               command=command_with_arg))
            self.buttons_rfid[-1].grid(column=i, row=1)


    def set_rfid(self, rfid):
        if self.radio_value.get() == 3: # mixed
            self.inter_block.append([(datetime.now() - self.start_time).total_seconds(), 'point', rfid])

    def set_motor(self):
        self.frame_motors.focus_set()
        self.frame_motors.bind('<Left>', self.left_key)
        self.frame_motors.bind('<Right>', self.right_key)
        self.overide_motors = [0 for i in range(8)]

    def left_key(self, event):
        self.overide_motors[int(self.motor_variable.get())] -= 0.05

    def right_key(self, event):
        self.overide_motors[int(self.motor_variable.get())] += 0.05

    def set_robot(self):
        # get all files in directory
        robot_sounds_path = self.get_path_name('sounds')

        self.sound_file_names = [f for f in listdir(robot_sounds_path) if isfile(join(robot_sounds_path, f)) and '.mp3' in f]
        if len(self.sound_file_names) > 0:
            self.sound_file_names.sort()
            self.text_loadsound_file.children['menu'].delete(0, "end")
            self.sound_file_variable.set(self.sound_file_names[0]) # default value
            for value in self.sound_file_names:
                self.text_loadsound_file.children['menu'].add_command(label=value,
                                                                    command=lambda v=value: self.set_general_file(v))

            self.lip_file_names = [f for f in listdir(robot_sounds_path) if isfile(join(robot_sounds_path, f)) and '.csv' in f]
            if len(self.lip_file_names) > 0:
                self.lip_file_names.sort()
                self.text_loadlip_file.children['menu'].delete(0, "end")
                self.lip_file_variable.set(self.lip_file_names[0]) # default value
                for value in self.lip_file_names:
                    self.text_loadlip_file.children['menu'].add_command(label=value,
                                                                        command=lambda v=value: self.set_general_file(v))

    def set_general_file(self, value):
        self.sound_file_variable.set(value[:-3] + 'mp3')
        self.lip_file_variable.set(value[:-3] + 'csv')
        self.text_save_file.delete(0, END)
        self.text_save_file.insert(END, value[:-4])

    def start_record(self):
        time.sleep(4)
        self.say_hello()
        time.sleep(2)

        self.record()
        if float(self.text_stop_after.get()) > 0.0:
            thread.start_new_thread(self.count_recording, (float(self.text_stop_after.get()), None))
        # if self.radio_value.get() == 2:  # block
        # self.play()

    def say_hello(self):
        pygame.mixer.music.load('sounds/fuzzy_hello.mp3')
        pygame.mixer.music.play()

    def count_recording(self, duration=0, *args):
        time.sleep(duration)
        self.stop_record()

    def stop_record(self):
        self.stop()

    def record(self):
        thread.start_new_thread(self.record_thread, (None, None))

    def record_thread(self, arg1=None, arg2=None):
        play_bag, play_lip, play_sound = self.load_files()

        if self.radio_value.get() == 3: # mixed
            self.inter_block = []
            self.start_time = datetime.now()

        self.rec_bag = []
        try:
            self.rec_bag.append((self.sound_filename,
                                 float(self.text_sound_offset.get()) - float(self.text_bag_offset.get())))
        except:
            self.rec_bag.append((None, None))

        self.rec = True

        if self.radio_value.get() == 1:       # bag only
            print(rospy.Subscriber('/skeleton_angles', String, self.callback))
            # print(rospy.Subscriber('/affdex_data', AffdexFrameInfo, self.callback))
        else:
            print(rospy.Subscriber('/dxl/command_position', CommandPosition, self.callback))

        if self.radio_value.get() > 1:  # block or mixed
            if play_sound:
                thread.start_new_thread(self.play_sound, (None, None))
            if play_lip:
                thread.start_new_thread(self.play_lip, (None, None))



    def play_sound(self, arg1=None, arg2=None):
        time.sleep(float(self.text_sound_offset.get()))
        pygame.mixer.music.play()

    def stop_recording_after_sound(self):
        while pygame.mixer.music.get_busy():
            time.sleep(0.020)
        self.stop()

    def play_lip(self, arg1=None, arg2=None):
        time.sleep(float(self.text_lip_offset.get()))
        if len(self.lip_angle) > 0:
            old_item = self.lip_angle[0]
            for iter in range(1, len(self.lip_angle)):
                new_item = self.lip_angle[iter]
                current_time = new_item[0]
                dt = (new_item[0] - old_item[0])
                time.sleep(dt)
                old_item = new_item
                self.publishers['/lip_angles'].publish(new_item[1])

    def play_sound_and_lip(self):
        self.load_files()
        self.play_sound()
        self.play_lip()

    def stop(self):
        if self.radio_value.get() == 2:  # block
            self.filename = self.get_path_name('blocks') + self.text_save_file.get()
        elif self.radio_value.get() == 1:
            self.filename = 'bags/' + self.text_save_file.get()
        elif self.radio_value.get() == 3:  # mixed
            inter_block_filename = self.get_path_name('blocks') + self.text_save_file.get() + '_inter_block'
            with open(inter_block_filename, 'w') as output:
                for ib in self.inter_block:
                    output.write('%2.3f,%s,%s\n' %(ib[0], ib[1], ib[2]))
            return

        self.rec = False

        if self.radio_value.get() != 3:  # recording something (not mixed)
            # save to file
            # shift all times to dt
            t0 = self.rec_bag[0][0]
            for item in self.rec_bag:
                try:
                    item = (item[0] - t0, item[1], item[2])
                except:
                    pass # first item is the sound

            # sort according to time (for multiple topics)
            with open(self.filename, 'wb') as output:
                pickle.dump(self.rec_bag, output, pickle.HIGHEST_PROTOCOL)
        print('done saving!')

    def callback(self, data):
        if self.rec:
            self.rec_bag.append((datetime.now(), data._connection_header['topic'], data))

    def play(self):
        thread.start_new_thread(self.play_block, (None, None))

    def load_files(self):
        play_bag = self.loadbag_value.get() == 1
        play_lip = self.loadlip_value.get() == 1
        play_sound = self.loadsound_value.get() == 1

        if play_bag:
            self.bag_filename = 'bags/' + self.text_loadbag_file.get()
        if play_lip:
            self.lip_filename = self.get_path_name('sounds') + self.lip_file_variable.get()
        if play_sound:
            self.sound_filename = self.get_path_name('sounds') + self.sound_file_variable.get()

        if play_bag:
            with open(self.bag_filename, 'rb') as input:
                self.play_bag = pickle.load(input)

        self.lip_angle = []
        if play_lip:
            with open(self.lip_filename, 'rb') as input:
                self.lip_reader = csv.reader(input)  # get all topics
                i = 0.0
                for row in self.lip_reader:
                    self.lip_angle.append((i, row[0]))
                    i += 1.0/30.0

        if play_sound:
            with open(self.sound_filename, 'rb') as input:
                pygame.mixer.music.load(self.sound_filename)
        return play_bag, play_lip, play_sound

    def replay_bag(self):
        play_bag, play_lip, play_sound = self.load_files()

        if play_sound:
            pygame.mixer.music.play()

        if play_bag:
            old_item = self.play_bag[0]
            for iter in range(1, len(self.play_bag)):
                new_item = self.play_bag[iter]
                current_time = new_item[0]
                dt = (new_item[0] - old_item[0]).total_seconds()
                time.sleep(dt)
                old_item = new_item
                self.publishers[new_item[1]].publish(new_item[2])


    def play_bag(self, arg1=None, arg2=None):
        try:
            self.filename = self.text_load_file.get()
            with open(self.filename, 'rb') as input:
                self.play_bag = pickle.load(input)

            # get all topics
            topic_list = set()
            for item in self.play_bag:
                topic_list.add(item[1])
            print(topic_list)

            publishers = {}
            for topic in topic_list:
                publishers[topic] = rospy.Publisher (topic, CommandPosition, queue_size=10)

            old_item = self.play_bag[0]
            publishers[old_item[1]].publish(old_item[2])
            for iter in range(1, len(self.play_bag)):
                new_item = self.play_bag[iter]
                dt = (new_item[0] - old_item[0]).total_seconds()
                time.sleep(dt)
                publishers[new_item[1]].publish(new_item[2])
                old_item = new_item
            print('done playing!')
        except:
            pass

    def replay_and_record_block(self):
        thread.start_new_thread(self.replay_and_record_thread, (None, None))

    def replay_and_record_thread(self, arg1=None, arg2=None):
        self.block_filename = self.get_path_name('blocks') + self.text_save_file.get()
        with open(self.block_filename, 'rb') as input:
            self.play_block = pickle.load(input)

        self.rec_bag = [self.play_block[0]]
        self.rec = True
        rospy.Subscriber('/dxl/command_position', CommandPosition, self.callback)

        self.sound_filename = self.play_block[0][0]
        if self.sound_filename:
            with open(self.sound_filename, 'rb') as input:
                pygame.mixer.music.load(self.sound_filename)
            sound_offset = self.play_block[0][1]
        else:
            if self.loadsound_value.get() == 1:
                self.sound_filename = self.get_path_name('sounds') + self.sound_file_variable.get()
                with open(self.sound_filename, 'rb') as input:
                    pygame.mixer.music.load(self.sound_filename)
                    self.rec_bag[0] = (self.sound_filename, 0.0)
            sound_offset = 0.0

        full_msg_list = self.play_block[1:]

        first_item = full_msg_list[0]
        old_item = full_msg_list[0]
        is_playing = False
        for iter in range(1, len(full_msg_list)):
            if not self.rec:
                break
            new_item = full_msg_list[iter]
            current_time = (new_item[0] - first_item[0]).total_seconds()
            dt = (new_item[0] - old_item[0]).total_seconds()
            time.sleep(dt)
            old_item = new_item

            new_command = CommandPosition()
            new_command.id = [i for i in range(1, 9)]
            new_command.angle = [new_item[2].angle[m] + self.overide_motors[m] for m in range(8)]
            new_command.speed = new_item[2].speed

            self.publishers[new_item[1]].publish(new_command)

            # self.publishers[new_item[1]].publish(new_item[2])

            if self.sound_filename:
                if not is_playing and current_time >= sound_offset:
                    is_playing = True
                    pygame.mixer.music.play()
                    print('playing')
        if self.sound_filename:
            pygame.mixer.music.stop()

        self.filename = self.get_path_name('blocks') + self.text_save_file.get() + '.new'
        self.rec = False

        t0 = self.rec_bag[0][0]
        for item in self.rec_bag:
            try:
                item = (item[0] - t0, item[1], item[2])
            except:
                pass # first item is the sound

        # sort according to time (for multiple topics)
        with open(self.filename, 'wb') as output:
            pickle.dump(self.rec_bag, output, pickle.HIGHEST_PROTOCOL)
        print('done saving!')

        print('done playing!')

    def replay_block(self):
        thread.start_new_thread(self.replay_block_thread, (None, None))

    def replay_block_thread(self, arg1=None, arg2=None):
        self.block_filename = self.get_path_name('blocks') + self.text_save_file.get()
        with open(self.block_filename, 'rb') as input:
            self.play_block = pickle.load(input)

        self.sound_filename = self.play_block[0][0]
        if self.sound_filename:
            with open(self.sound_filename, 'rb') as input:
                pygame.mixer.music.load(self.sound_filename)
            sound_offset = self.play_block[0][1]
        else:
            sound_offset = 0.0

        full_msg_list = self.play_block[1:]

        print('msg list:', len(full_msg_list))

        first_item = full_msg_list[0]
        old_item = full_msg_list[0]
        is_playing = False
        for iter in range(1, len(full_msg_list)):
            new_item = full_msg_list[iter]
            current_time = (new_item[0] - first_item[0]).total_seconds()
            dt = (new_item[0] - old_item[0]).total_seconds()
            time.sleep(dt)
            old_item = new_item

            new_command = CommandPosition()
            new_command.id = [i for i in range(1, 9)]
            new_command.angle = [new_item[2].angle[m] + self.overide_motors[m] for m in range(8)]
            new_command.speed = new_item[2].speed
            self.publishers[new_item[1]].publish(new_command)

            # self.publishers[new_item[1]].publish(new_item[2])

            if self.sound_filename:
                if not is_playing and current_time >= sound_offset:
                    is_playing = True
                    pygame.mixer.music.play()
                    print('playing')
        if self.sound_filename:
            pygame.mixer.music.stop()
            print('done playing!')


    def play_block(self, arg1=None, arg2=None):
        # try:
        play_bag, play_lip, play_sound = self.load_files()

        # create a full list
        start_time = datetime.now()
        end_bag = True
        bag_time = 0
        if play_bag:
            bag_iter = 0
            bag_item = self.play_bag[bag_iter]
            bag_start_time = bag_item[0]
            bag_time = (bag_item[0] - bag_start_time).total_seconds()
            end_bag = False

        end_lip = True
        lip_time = 0
        if play_lip:
            lip_iter = 0
            lip_item = self.lip_angle[lip_iter]
            lip_time = lip_item[0]
            end_lip = False

        full_msg_list = []
        if play_lip and not play_bag:
            for lip_item in self.lip_angle:
                full_msg_list.append((lip_item[0], '/lip_angles', str(lip_item[1])))
        elif play_bag and not play_lip:
            for bag_item in self.play_bag:
                full_msg_list.append(((bag_item[0] - bag_start_time).total_seconds(), bag_item[1], bag_item[2]))
        else:
            while not end_bag and not end_lip:
                try:
                    while bag_time > lip_time:
                        full_msg_list.append((lip_time, '/lip_angles', str(lip_item[1])))
                        lip_iter += 1
                        lip_item = self.lip_angle[lip_iter]
                        lip_time = lip_item[0]
                except:
                    end_lip = True
                try:
                    while bag_time <= lip_time:
                        full_msg_list.append((bag_time, bag_item[1], bag_item[2]))
                        bag_iter += 1
                        bag_item = self.play_bag[bag_iter]
                        bag_time = (bag_item[0] - bag_start_time).total_seconds()
                except:
                    end_bag = True

        print('full_msg_list', full_msg_list)

        if len(full_msg_list) > 0:
            first_item = full_msg_list[0]
            old_item = full_msg_list[0]
            is_playing = False
            for iter in range(1, len(full_msg_list)):
                if not self.rec:
                    break
                new_item = full_msg_list[iter]
                current_time = new_item[0] - first_item[0]
                dt = new_item[0] - old_item[0]
                time.sleep(dt)
                old_item = new_item

                if new_item[1] in ['/skeleton_angles', '/affdex_data']:
                    # if current time after bag offset --> publish
                    if current_time >= float(self.text_bag_offset.get()):
                        self.publishers[new_item[1]].publish(new_item[2])

                if new_item[1] in ['/lip_angles']:
                    if current_time >= float(self.text_lip_offset.get()):
                        self.publishers[new_item[1]].publish(new_item[2])

                if not is_playing and current_time >= float(self.text_sound_offset.get()):
                    is_playing = True
                    pygame.mixer.music.play()
                    print('playing')
            pygame.mixer.music.stop()
            print('done playing!')
        else:
            if play_sound:
                pygame.mixer.music.play()
                print('playing')

        # pygame.mixer.music.stop()
        # print('done playing!')
        # except:
        #     print('lots of errors')



app = Application()
app.master.title('Sample application')
app.mainloop()