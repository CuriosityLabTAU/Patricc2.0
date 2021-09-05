import pickle
import pygame
import time
import rospy
from dynamixel_hr_ros.msg import *
from std_msgs.msg import String
from std_msgs.msg import Int8
import numpy as np
from scipy.signal import *
import matplotlib.pyplot as plt
from copy import deepcopy
import csv
from scipy.interpolate import interp1d
from scipy.signal import butter, lfilter, filtfilt
import matplotlib.pyplot as plt
from datetime import datetime
from map_props import *
from copy import copy
import robot_parameters




class play_block():

    def __init__(self):

        self.base_path = '../'

        self.rfids = [None for i in range(5)]
        self.rfid_prev = [None for i in range(5)]
        self.rfid_change = [None for i in range(5)]
        self.is_rfid_change = False

        #self.publisher = rospy.Publisher('/dxl/command_position', CommandPosition, queue_size=10)
        self.motor_publisher = rospy.Publisher('/patricc_motion_control', CommandPosition, queue_size=10)
        self.game_activator = rospy.Publisher('/game_activation', String, queue_size=10)
        self.mode_publisher = rospy.Publisher('/patricc_activation_mode', String, queue_size=10)


        self.rifd_sub = rospy.Subscriber('/rfid', String, self.rfid_callback)
        self.world_sub = rospy.Subscriber('/world_action', String, self.world_callback)

        pygame.init()
        pygame.mixer.init()

        self.sound_filename = None
        self.sound_offset = 0.0
        self.lip_filename = None
        self.lip_offset = 0.0

        self.filename = None
        self.duration = 0.0

        self.lip_angle = []
        self.event_activation = 'off'
        self.rule = []
        self.rule_sign = []
        self.ros_event_occured = False
        self.world_action = 'none'
        self.world_event = 'none'
        self.world_event_old = 'none'
        self.world_action_time = datetime.now()
        self.world_action_timeout = 3
        self.world_animal = 'none'
        self.world_food = 'none'
        self.new_ros_event = 'false'

        self.motor_list = {'skeleton': [0, 1, 4, 5, 6, 7], 'head_pose': [2], 'lip': [3], 'full': [0, 1, 2, 3, 4, 5, 6, 7], 'full_idx': [1, 2, 3, 4, 5, 6, 7, 8]}
        self.robot_angle_range = robot_parameters.robot_angle_range
        self.sensor_angle_range = robot_parameters.sensor_angle_range
        self.robot_kinect_angles = robot_parameters.robot_kinect_angles
        self.robot_motors_no_mouth = robot_parameters.robot_motors_no_mouth
        self.robot_motor_mouth = robot_parameters.robot_motor_mouth
        self.motor_speed = robot_parameters.motor_speed

        rospy.init_node('block_player')
        #self.game_activator.publish('game_2')
        time.sleep(1)
        print 'open node'


    def test_motors(self):
        the_range = np.sin(np.linspace(0.0, 2.0 * np.pi, 200)) * 0.5 + 0.5
        dt = 1.0 / 30.0
        for j in range(the_range.shape[0]):
            new_command = CommandPosition()
            new_command.id = [i for i in range(1, 9)]
            new_command.angle = [self.robot_angle_range[i][0] + the_range[j] * (self.robot_angle_range[i][1] - self.robot_angle_range[i][0]) for i in range(8)]
            new_command.speed = self.motor_speed

            self.motor_publisher.publish(new_command)
            time.sleep(dt)

    def world_callback(self, data):
        #print 'event activation', self.event_activation
        msg = data.data
        print 'PLAY BLOCK: got message from world = ', msg
        msg_split = msg.split(',')
        #self.world_event_old = self.world_event
        self.world_action = msg_split[0]
        self.world_event = msg_split[0]
        #if self.world_event_old ==
        self.world_action_time = datetime.now()
        self.world_animal = msg_split[1]
        self.world_food = msg_split[2]
        #if self.world_event_old != self.world_event:
        self.new_ros_event  = 'true'



    def rfid_callback(self, data):
        msg = data.data
        for i in range(5):
            rfid = msg[i*8:(i+1)*8]
            if '---' in rfid:
                self.rfids[i] = None
            else:
                try:
                    self.rfids[i] = rfid_to_prop[rfid]
                except:
                    print(msg)
        #print self.rfids


    def update_rifd(self):
        self.is_rfid_change = False
        for i in range(5):
            if self.rfids[i] != self.rfid_prev[i]:
                self.rfid_change[i] = self.rfid_prev[i]
                self.is_rfid_change = True
            else:
                self.rfid_change[i] = None
        self.rfid_prev = deepcopy(self.rfids)
        return self.is_rfid_change

    # block things
    def load_block(self, block_filename = 'blocks/block_spider_1'):
        self.filename = block_filename
        #print 'block filename ', self.filename
        with open(self.filename, 'rb') as input:
            play_block = pickle.load(input)

        self.full_msg_list = self.clean_msg_list(play_block[1:])

        if not self.sound_filename:
            self.sound_filename = play_block[0][0]
            if self.sound_filename:
                self.sound_filename = self.base_path + self.sound_filename
                self.sound_offset = play_block[0][1]
            else:
                self.sound_offset = None
        self.load_files()

        if self.lip_angle:
            self.merge_lip_and_block()

        self.duration = (self.full_msg_list[-1][0] - self.full_msg_list[0][0]).total_seconds()
        #print('Block: duration:', self.duration, ' sound: ', self.sound_filename)

    def clean_msg_list(self, m_list):
        new_list = []
        new_list.append(m_list[0])
        for i in range(1, len(m_list)):
            if (m_list[i][0] - new_list[-1][0]).total_seconds() > 0.001:
                new_list.append(m_list[i])
        return new_list


    def merge_lip_and_block(self):
        lip_times = np.array([self.lip_angle[i][0] for i in range(len(self.lip_angle))])

        msg_list = self.full_msg_list
        new_msg_list = []
        first_item = msg_list[0]
        for iter in range(1, len(msg_list)):
            new_item = msg_list[iter]
            current_time = (new_item[0] - first_item[0]).total_seconds()
            lip_ind = np.argmin(abs(lip_times - current_time))

            current_angles = [new_item[2].angle[m] for m in range(8)]
            new_angle = self.map_angles(self.sensor_angle_range[self.motor_list['lip'][0]],
                                        self.robot_angle_range[self.motor_list['lip'][0]],
                                        self.lip_angle[lip_ind][1])
            current_angles[self.motor_list['lip'][0]] = new_angle

            new_command = CommandPosition()
            new_command.id = [i for i in range(1, 9)]
            new_command.angle = current_angles
            new_command.speed = new_item[2].speed

            new_msg_list.append([self.full_msg_list[iter][0], self.full_msg_list[1], new_command])
        self.full_msg_list = new_msg_list

    def play(self, msg_list=None, motor_commands=None, stop_on_sound=False):
        if msg_list is None:
            msg_list = self.full_msg_list
        first_item = msg_list[0]
        old_item = msg_list[0]
        is_playing = False
        real_output = []
        real_first_time = datetime.now()

        for iter in range(1, len(msg_list)):
            new_item = msg_list[iter]
            current_time = (new_item[0] - first_item[0]).total_seconds()

            real_current_time = (datetime.now() - real_first_time).total_seconds()
            dt = current_time - real_current_time

            if dt > 0.001:
                time.sleep(dt)

                new_speed = list(np.abs(np.array(new_item[2].angle) - np.array(old_item[2].angle)) / 2.0)

                old_item = new_item

                if motor_commands is not None:
                    new_item[2].angle = motor_commands[iter,1:]

                new_command = CommandPosition()
                new_command.id = [i for i in range(1, 9)]
                new_command.angle = new_item[2].angle

                new_command.speed = self.motor_speed
                self.motor_publisher.publish(new_command)

                real_output.append(new_command.angle)

                if self.sound_offset is not None:
                    if not is_playing and current_time >= self.sound_offset:
                        is_playing = True
                        pygame.mixer.music.play()
                        #print('playing')

                    if is_playing and stop_on_sound:
                        if not pygame.mixer.music.get_busy():
                            if float(iter) / float(len(msg_list)) > 0.80:
                                is_playing = False
                                break

        if is_playing:
            while pygame.mixer.music.get_busy():
                time.sleep(0.020)

        if self.sound_offset:
            pygame.mixer.music.stop()
            print('done playing!')
        np_real_output = np.array(real_output)


    def play_msg_list(self, msg_list, stop_on_sound=False):
        first_item = msg_list[0]
        old_item = msg_list[0]
        is_playing = False
        real_output = []
        real_first_time = datetime.now()

        for iter in range(1, len(msg_list)):
            new_item = msg_list[iter]
            current_time = (new_item[0] - first_item[0]).total_seconds()

            real_current_time = (datetime.now() - real_first_time).total_seconds()
            dt = current_time - real_current_time

            if dt > 0.001:
                time.sleep(dt)

                new_speed = list(np.abs(np.array(new_item[2].angle) - np.array(old_item[2].angle)) / 2.0)

                old_item = new_item

                new_command = CommandPosition()
                new_command.id = [i for i in range(1, 9)]
                new_command.angle = new_item[2].angle
                new_command.speed = self.motor_speed
                self.motor_publisher.publish(new_command)

                real_output.append(new_command.angle)

                if self.sound_offset is not None:
                    if not is_playing and current_time >= self.sound_offset:
                        is_playing = True
                        pygame.mixer.music.play()
                        #print('playing')

                    if is_playing and stop_on_sound:
                        if not pygame.mixer.music.get_busy():
                            if float(iter) / float(len(msg_list)) > 0.80:
                                is_playing = False
                                break

        if is_playing:
            while pygame.mixer.music.get_busy():
                time.sleep(0.020)

        if self.sound_offset:
            pygame.mixer.music.stop()
            print('done playing!')
        np_real_output = np.array(real_output)

    def play_motor_commands(self, motor_commands, stop_on_sound=False, play_sound='on', duration=500, activation="off", rule=[], rule_sign=[], lip='on', stop_at='block'):
        first_item = motor_commands[0, :]
        old_item = motor_commands[0, :]
        is_playing = False
        real_first_time = datetime.now()
        stopwatch_start = datetime.now()
        for iter in range(1, motor_commands.shape[0]):
            if (datetime.now()-stopwatch_start).total_seconds() > float(duration):
                pygame.mixer.music.stop()
                break
            if activation=="on":
                if self.check_prop_event(rule, rule_sign):
                    #a = self.check_prop_event(rule, rule_sign)
                    #print 'rule is ', a
                    pygame.mixer.music.stop()
                    break
                if self.ros_event_occured == True:
                    pygame.mixer.music.stop()
                    break


            new_item = motor_commands[iter, :]
            current_time = new_item[0] - first_item[0]

            real_current_time = (datetime.now() - real_first_time).total_seconds()
            dt = current_time - real_current_time

            if dt > 0.001:
                time.sleep(dt)
                old_item = new_item
                new_command = CommandPosition()
                new_command.id = [i for i in range(1, 9)]
                new_command.angle = new_item[1:]
                #This is the (ugly) change to make for the robot with the flipped arm
                #new_command.angle[4] = self.map_angles([4.1,0.9], [0.9,4.1], new_command.angle[4]) # flips angles of left arm
                #new_command.angle[6] = self.map_angles([1, 4.1], [4.1, 1], new_command.angle[6]) # flips angles of right arm
                ###
                if lip=='off':
                    new_command.angle[3] = 1.8
                new_command.speed = self.motor_speed
                self.motor_publisher.publish(new_command)

                if self.sound_offset is not None:
                    if not is_playing and current_time >= self.sound_offset:
                        is_playing = True
                        if play_sound=='on':
                            pygame.mixer.music.play()
                        #print('playing')
                if stop_at=='sound':
                    if pygame.mixer.music.get_busy()==False:
                        break
        if is_playing:
            while pygame.mixer.music.get_busy():
                time.sleep(0.020)

        if self.sound_offset:
            pygame.mixer.music.stop()
            print('done playing!')

    def convert_to_motor_commands(self, full_msg_list=None):
        if not full_msg_list:
            full_msg_list = self.full_msg_list
        motor_commands = np.zeros([len(full_msg_list), 9])
        first_item = full_msg_list[0]
        old_item = full_msg_list[0]
        for iter in range(0, len(full_msg_list)):
            new_item = full_msg_list[iter]
            motor_commands[iter, 0] = (new_item[0] - first_item[0]).total_seconds()
            motor_commands[iter, 1:] = np.array(new_item[2].angle)
        return motor_commands

    def edit(self, motor_commands):
        window_size = 40
        win = hann(window_size)
        temp_motor_commands = np.copy(motor_commands)
        for d in range(0, motor_commands.shape[1]):
            if d != 4:
                cutoff = 0.25
                order = 6
                b, a = butter(order, cutoff)#, btype='lowpass', analog=True)
                temp_motor_commands[:, d] = filtfilt(b, a,motor_commands[:, d])

        filtered_motor_commands = temp_motor_commands

        return filtered_motor_commands

    def play_editted(self, motor_commands=None, stop_on_sound=False, play_sound='on', duration=500, activation='off', rule=[], rule_sign=[], lip='on', stop_at='block'):
        if motor_commands is None:
            motor_commands = self.convert_to_motor_commands()
        filtered_motor_commands = self.edit(motor_commands)
        self.play_motor_commands(motor_commands=filtered_motor_commands, stop_on_sound=stop_on_sound, play_sound=play_sound, duration=duration, activation=activation, rule=rule, rule_sign=rule_sign, lip=lip, stop_at=stop_at)
        #print 'rule sign = ', self.rule_sign, 'rule = ', self.rule

    def load_files(self):
        self.lip_angle = []
        if self.lip_filename:
            with open(self.lip_filename, 'rb') as input:
                self.lip_reader = csv.reader(input)  # get all topics
                i = 0.0
                for row in self.lip_reader:
                    self.lip_angle.append((i, float(row[0])))
                    i += 1.0/30.0

        if self.sound_filename:
            with open(self.sound_filename, 'rb') as input:
                pygame.mixer.music.load(self.sound_filename)

    def play_sound(self, arg1=None, arg2=None):
        time.sleep(float(self.sound_offset))
        pygame.mixer.music.play()

    def play_lip(self, arg1=None, arg2=None):
        time.sleep(float(self.lip_offset))
        old_item = self.lip_angle[0]
        for iter in range(1, len(self.lip_angle)):
            new_item = self.lip_angle[iter]
            current_time = new_item[0]
            dt = (new_item[0] - old_item[0])
            time.sleep(dt)
            old_item = new_item
            self.publishers['/lip_angles'].publish(new_item[1])

    def play_sound_and_lip(self):

        try:
            self.play_sound()
            self.play_lip()
        except:
            self.load_files()
            self.play_sound()
            self.play_lip()

    def map_angles(self, kinect_range, robot_range, psi):
        new_angle = robot_range[0] + (psi - kinect_range[0]) * ((robot_range[1] - robot_range[0]) / (kinect_range[1] - kinect_range[0]))
        return new_angle

    # multi-blocks
    def stitch_blocks(self, block_before=None, block_after=None, motor_commands=None):
        if type(motor_commands) == type(None):
            motor_commands = self.convert_to_motor_commands()

        mouth_commands = copy(motor_commands[:, self.robot_motor_mouth])
        percent = 0.01
        window_size = 5
        win = hann(window_size)

        if block_before:
            if type(block_before) == str:
                with open(block_before, 'rb') as input:
                    play_block = pickle.load(input)
                motor_commands_before = self.convert_to_motor_commands(full_msg_list=play_block[1:])
            else:
                motor_commands_before = self.convert_to_motor_commands(full_msg_list=block_before.full_msg_list)
            n_end = int((1.0 - percent) * motor_commands_before.shape[0])
            n_begin = int(percent * motor_commands.shape[0])

            data = np.concatenate((motor_commands_before[n_end:, :], motor_commands[:n_begin + window_size, :]), axis=0)
            data[-n_begin:, 0] += data[-n_begin-1, 0]
            for d in range(data.shape[1]):
                data[:, d] = convolve(data[:, d], win, mode='same') / sum(win)
            relevant_data = data[-motor_commands[:n_begin, 1:].shape[0]-window_size:-window_size, 1:]
            motor_commands[:n_begin, 1:] = relevant_data

        if block_after:
            if type(block_after) == str:
                with open(block_after, 'rb') as input:
                    play_block = pickle.load(input)
                motor_commands_after = self.convert_to_motor_commands(full_msg_list=play_block[1:])
            else:
                motor_commands_after = self.convert_to_motor_commands(full_msg_list=block_after.full_msg_list)

            n_begin = int(percent * motor_commands_after.shape[0])
            n_end = int((1.0 - percent) * motor_commands.shape[0])

            data = np.concatenate((motor_commands[n_end - window_size:, :], motor_commands_after[:n_begin, :]), axis=0)
            data[-n_begin:, 0] += data[-n_begin-1, 0]
            for d in range(data.shape[1]):
                data[:, d] = convolve(data[:, d], win, mode='same') / sum(win)
            relevant_data = data[window_size:window_size + motor_commands[n_end:, 1:].shape[0], 1:]
            motor_commands[n_end:, 1:] = relevant_data

        motor_commands[:, self.robot_motor_mouth] = mouth_commands

        return motor_commands

    def cut_sub_block(self, start=0.0, end=-1.0):
        sub_block = play_block()
        sub_block.base_path = self.base_path
        sub_block.load_block(self.filename)

        if end < 0.0:
            end = self.duration

        if end < start:
            return None

        # go over current msg_list, and create new one
        sub_block.full_msg_list = []

        msg_list = self.full_msg_list
        first_item = msg_list[0]
        for iter in range(len(msg_list)):
            current_item = msg_list[iter]
            current_time = (current_item[0] - first_item[0]).total_seconds()
            if current_time >= start and current_time <= end:
                sub_block.full_msg_list.append(current_item)
            elif current_time > end:
                break
        sub_block.duration = (sub_block.full_msg_list[-1][0] - sub_block.full_msg_list[0][0]).total_seconds()

        return sub_block

    def check_prop_event(self, rule, rule_sign):
        #print 'event activation', self.event_activation
        detected_props = [x for x in self.rfids if x != None]
        prop_event_occured = False
        self.ros_event_occured = False
        #print 'the rule is:', rule, rule_sign
        if rule_sign=='is_on_console':
            if set(rule).issubset(set(detected_props))==True:
                prop_event_occured = True
            else:
                prop_event_occured = False
        elif rule_sign=='is_not_on_console':
            if set(rule).issubset(set(detected_props))==True:
                prop_event_occured = False
            else:
                prop_event_occured = True
        elif rule_sign == 'positive':
            if set(detected_props)==set(rule):
                prop_event_occured = True
            else:
                prop_event_occured = False
        elif rule_sign == 'negative':
            if set(detected_props)==set(rule):
                prop_event_occured = False
            else:
                prop_event_occured = True
        elif rule_sign == 'is_change':
            if set(detected_props)==set(rule):
                prop_event_occured = True
            else:
                prop_event_occured = False
        elif rule_sign == 'prop_on_position':
            try:
                self.rfids.index(rule[0])
                prop_pos = self.rfids.index(rule[0])
            except ValueError:
                prop_pos = 5
            #print 'debug new rule ', prop_pos, ' : ', rule[1]
            if prop_pos == rule[1]:
                prop_event_occured = True
            else:
                prop_event_occured = False
        elif rule_sign == 'ROS':
            print 'PLAY BLOCK: debug new rule ', self.world_event, ' : ', rule[0]
            if self.world_event == rule[0]:
                self.world_event = 'none'
                prop_event_occured = True
                self.ros_event_occured = True

            else:
                prop_event_occured = False
                self.ros_event_occured = False
        elif rule_sign == 'ROS_change':
            print "PLAY BLOCK: check ROS change rule"
            if self.new_ros_event == 'true':
                prop_event_occured = True
                self.ros_event_occured = True
                self.new_ros_event = 'false'
                print "PLAY BLOCK: ROS event changed"

            else:
                prop_event_occured = False
                self.ros_event_occured = False
        #print 'prop event check in play block = ', prop_event_occured
        return prop_event_occured

    def ros_publish(self, message):
        self.game_activator.publish(message)


    # behavioral filters
    def behavioral_filters(self, filtered_motor_commands):
        behavioral_motor_commands = np.copy(filtered_motor_commands)
        for d in range(filtered_motor_commands.shape[1]):
            # convert to velocity profile
            velocty_profiles = np.diff(filtered_motor_commands[:, d])

            # find zero velocity points
            v_zero = (np.diff(np.sign(np.diff(velocty_profiles))) > 0).nonzero()[0] + 1 # local min
            t_pose = np.where(np.abs(velocty_profiles[v_zero]) < 0.1)[0]

            behavioral_velocity_profile = np.copy(velocty_profiles)
            # apply filter (while maintaining area)
            for i in range(1, t_pose.shape[0]):
                t_pose_start = t_pose[i-1]
                t_pose_end = t_pose[i]
                duration_pose = v_zero[t_pose_end] - v_zero[t_pose_start]
                v_pose = velocty_profiles[v_zero[t_pose_start]:v_zero[t_pose_end]]
                area = np.sum(v_pose)

                # filter for up-down
                behavioral_pose = np.copy(v_pose)
                mid_duration = int(np.round(duration_pose/2.0))
                v_0 = v_pose[0]
                v_1 = v_pose[-1]
                max_v = (area - mid_duration * (v_0 + v_1)/2.02) / mid_duration

                first_half = behavioral_pose[:mid_duration].shape[0]
                second_half = behavioral_pose[mid_duration:].shape[0]
                behavioral_pose[:mid_duration] = np.linspace(v_pose[0], max_v, num=first_half)
                behavioral_pose[mid_duration:] = np.linspace(max_v, v_pose[-1], num=second_half)

                behavioral_velocity_profile[v_zero[t_pose_start]:v_zero[t_pose_end]] = behavioral_pose

            plt.plot(velocty_profiles)
            plt.title('area: %2.3f, num_points: %d' % (np.sum(velocty_profiles), velocty_profiles.shape[0]))
            #plt.show()
            plt.plot(behavioral_velocity_profile)
            plt.title('area: %2.3f, num_points: %d' % (np.sum(behavioral_velocity_profile), behavioral_velocity_profile.shape[0]))
            #plt.show()
            print('done')

            # find the positions
            for i in range(1, behavioral_velocity_profile.shape[0]):
                behavioral_motor_commands[i, d] = behavioral_motor_commands[i-1, d] + behavioral_velocity_profile[i] / 30.0

        return behavioral_motor_commands


