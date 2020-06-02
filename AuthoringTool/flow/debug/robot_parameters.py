import numpy as np

motor_list  = {'skeleton': [0, 1, 4, 5, 6, 7], 'head_pose': [2], 'lip': [3], 'full': [0, 1, 2, 3, 4, 5, 6, 7], 'full_idx': [1, 2, 3, 4, 5, 6, 7, 8]}
robot_angle_range = [[0.0, 5.0], #[1.1, 3.9],
                          [2.8, 1.6],
                          [2, 3.3], [1.8, 2.5], #[2.2, 2.5]#[1.8, 2.5], #[2.5, 3.5], #
                          [4.1, 0.9], [1.3, 3],
                          [1, 4.1], [2.5, 3.75]]
sensor_angle_range = [[-np.pi, np.pi], [0, np.pi/2],
                           [-0.2, 0.2], [0, 254],
                           [-np.pi/2, np.pi/2], [np.pi/2, 0],
                           [-np.pi/2, np.pi/2], [0, np.pi/2]]
#self.robot_kinect_angles = [0, 1, 0, 0, 2, 3, 4, 5] #these are the numbers that came from play_block.py
robot_motors_no_mouth = [0, 1, 2, 4, 5, 6, 7]
robot_motor_mouth = 4
motor_speed = [0.4, 0.4, 2, 7, 5, 5, 5, 5]
motor_speeds = motor_speed
robot_kinect_angles = [0, 1, 0, 0, 4, 5, 2, 3] # complete mirror, these are the numbers that came from motion_control.py

