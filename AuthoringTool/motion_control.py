#!/usr/bin/env python
#!/usr/bin/env python

import roslib; roslib.load_manifest("dynamixel_hr_ros")
import rospy
from std_msgs.msg import *
import json
from dynamixel_hr_ros.msg import *
from dxl import *
import logging
import time
import pygame
import numpy as np
import math
import csv
import itertools
# from affdex_msgs.msg import AffdexFrameInfo
from geometry_msgs.msg import PoseStamped
from flow.debug import robot_parameters

from threading import Timer


logging.basicConfig(level=logging.DEBUG)


class MotionControl:

    def __init__(self):

        self.motor_list  = robot_parameters.motor_list
        self.robot_angle_range = robot_parameters.robot_angle_range
        self.sensor_angle_range = robot_parameters.sensor_angle_range
        self.robot_kinect_angles = robot_parameters.robot_kinect_angles
        self.motor_speeds = robot_parameters.motor_speeds

        self.skeleton_angles = []
        self.robot_angles = np.zeros([8])
        for i, rar in enumerate(self.robot_angle_range):
            self.robot_angles[i] = np.mean(rar)
        self.robot_angles[1] = 2.8

        # print(self.robot_angles)


    def start(self):
        # init a listener to kinect angles
        rospy.init_node('motion_control')
        rospy.Subscriber("skeleton_angles", String, self.kinect_callback)
        rospy.Subscriber("head_pose", PoseStamped, self.head_pose_callback)
        rospy.Subscriber("lip_angles", String, self.lip_callback)
        enabler = rospy.Publisher("/dxl/enable", Bool, queue_size=10)
        self.commander = rospy.Publisher("/dxl/command_position", CommandPosition, queue_size=10)
        time.sleep(1)
        enabler.publish(True)
        time.sleep(1)
        rospy.spin()

    def head_pose_callback(self, data):
        head_angle = -data.pose.orientation.w

        self.robot_angles[self.motor_list['head_pose'][0]] = self.map_angles(self.sensor_angle_range[2],
                                                                          self.robot_angle_range[self.motor_list['head_pose'][0]],
                                                                          head_angle)
        self.move_motors()


    def lip_callback(self, data):
        # print ['lip angles : ', data]
        self.robot_angles[self.motor_list['lip'][0]] = self.map_angles(
            self.sensor_angle_range[self.motor_list['lip'][0]], self.robot_angle_range[self.motor_list['lip'][0]], float(data.data))
        self.move_motors()

    def kinect_callback(self, data):
        self.skeleton_angles = np.array([float(x) for x in data.data.split(',')])
        for motor in self.motor_list['skeleton']:
            try:
                self.robot_angles[motor] = self.map_angles(self.sensor_angle_range[motor], self.robot_angle_range[motor],
                                                           self.skeleton_angles[self.robot_kinect_angles[motor]])
            except:
                print('ERROR: motor ', motor, ' not connected!')
        # print self.skeleton_angles[2]
        self.move_motors()

    def move_motors(self, angles=None):
        command = CommandPosition()
        command.id = self.motor_list['full_idx']
        command.angle = self.robot_angles[self.motor_list['full']]
        print self.robot_angles[self.motor_list['full']]
        command.speed = self.motor_speeds
        # print(command)
        self.commander.publish(command)

    def map_angles(self, kinect_range, robot_range, psi):
        new_angle = robot_range[0] + (psi - kinect_range[0]) * ((robot_range[1] - robot_range[0]) / (kinect_range[1] - kinect_range[0]))
        return new_angle

# if __name__=="__main__":

motion_control = MotionControl()
motion_control.start()

logging.basicConfig(level=logging.DEBUG)

print "Listening for commands"


