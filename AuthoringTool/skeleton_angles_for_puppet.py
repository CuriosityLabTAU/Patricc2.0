import rospy
from std_msgs.msg import String
from skeleton_markers.msg import Skeleton
import numpy as np


class SkeletonAngles():
    def __init__(self):
        self.pub = rospy.Publisher ('skeleton_angles', String, queue_size=10)
        self.names = ['head', 'neck', 'torso', 'left_shoulder', 'left_elbow', 'left_hand',
                      'right_shoulder', 'right_elbow', 'right_hand',
                      'left_hip', 'left_knee', 'left_foot', 'right_hip', 'right_knee', 'right_foot']
        self.positions = {}
        for name in self.names:
            self.positions[name] = {'x': None, 'y': None, 'z': None}

        self.skeleton_angles = np.zeros([6])

    def start(self):
        #init a listener to kinect and
        rospy.init_node('skeleton_angle')
        rospy.Subscriber("skeleton", Skeleton, self.callback)
        rospy.spin()

    def callback(self, data):
        positions = data.position
        for name in self.names:
            self.positions[name]['x'] = positions[self.names.index(name)].x
            self.positions[name]['y'] = positions[self.names.index(name)].y
            self.positions[name]['z'] = positions[self.names.index(name)].z
        #build point vectors in the kinect frame
        left_shoulder_k =  np.array([self.positions["left_shoulder"]['x'], self.positions["left_shoulder"]['y'], self.positions["left_shoulder"]['z']])
        right_shoulder_k =  np.array([self.positions["right_shoulder"]['x'], self.positions["right_shoulder"]['y'], self.positions["right_shoulder"]['z']])
        left_elbow_k =  np.array([self.positions["left_elbow"]['x'], self.positions["left_elbow"]['y'], self.positions["left_elbow"]['z']])
        right_elbow_k =  np.array([self.positions["right_elbow"]['x'], self.positions["right_elbow"]['y'], self.positions["right_elbow"]['z']])
        left_hand_k =  np.array([self.positions["left_hand"]['x'], self.positions["left_hand"]['y'], self.positions["left_hand"]['z']])
        right_hand_k =  np.array([self.positions["right_hand"]['x'], self.positions["right_hand"]['y'], self.positions["right_hand"]['z']])
        left_hip_k =  np.array([self.positions["left_hip"]['x'], self.positions["left_hip"]['y'], self.positions["left_hip"]['z']])
        right_hip_k =  np.array([self.positions["right_hip"]['x'], self.positions["right_hip"]['y'], self.positions["right_hip"]['z']])



        y_k = np.array([0, 1, 0])
        x_k = np.array([1, 0, 0])
        z_k = np.array([0, 0, 1])

        #canonical base
        y_e = np.array([0, 1, 0])
        x_e = np.array([1, 0, 0])
        z_e = np.array([0, 0, 1])

        #convert from kinect frame to robot 0 frame
        A = np.array([[-1, 0, 0], [0, 1, 0], [0, 0, -1]])

        y_0 = np.dot(A, y_k)
        x_0 = np.dot(A, x_k)
        z_0 = np.dot(A, z_k)

        #frame 2 - frame of robot
        middle_shoulder = (left_shoulder_k + right_shoulder_k) / 2
        middle_hip = (left_hip_k + right_hip_k) / 2
        x_2_k = (left_shoulder_k - right_shoulder_k)/ np.linalg.norm(left_shoulder_k - right_shoulder_k)
        y_2_k = (middle_shoulder - middle_hip) / np.linalg.norm(middle_shoulder - middle_hip)
        x_2 = np.dot(A, x_2_k)
        y_2 = np.dot(A, y_2_k)
        z_2 = np.cross(x_2, y_2)

        #frame 1 - frame of robot after yaw and before pitch
        x_1 = x_2
        y_1 = y_0
        z_1 = np.cross(x_1, y_1)

        #robot yaw - phi
        x_1Px_e = np.dot(x_2_k, -x_e)
        x_1Pz_e = np.dot(x_2_k, z_e)
        phi = np.arctan2(x_1Pz_e, x_1Px_e)

        #robot pitch - theta
        y_2Pnz_e = np.dot(y_2_k, -z_e)
        y_2Py_e = np.dot(y_2_k, y_e)
        theta = np.arctan2(y_2Pnz_e, y_2Py_e)

        #arm angles
        x3_l_k = (left_elbow_k - left_shoulder_k) / np.linalg.norm(left_elbow_k - left_shoulder_k)
        x3_l = np.dot(A, x3_l_k)
        x3_lPx_2 = np.dot(x3_l, z_1)
        a_l = x3_l -x3_lPx_2 * x_2
        a_lPz_2 = np.dot(a_l, z_2)
        a_lPy_2 = np.dot(a_l, y_2)
        alpha_l = np.arctan2(a_lPy_2, a_lPz_2)

        x3_r_k = (right_elbow_k - right_shoulder_k) / np.linalg.norm(right_elbow_k - right_shoulder_k)
        x3_r = np.dot(A, x3_r_k)
        x3_rPx_2 = np.dot(x3_r, z_1)
        a_r = x3_r -x3_rPx_2 * x_2
        a_rPz_2 = np.dot(a_r, z_2)
        a_rPy_2 = np.dot(a_r, y_2)
        alpha_r = np.arctan2(a_rPy_2, a_rPz_2)

        x4_l_k = (left_hand_k - left_elbow_k) / np.linalg.norm(left_hand_k - left_elbow_k)
        x4_l = np.dot(A, x4_l_k)
        beta_l = np.arccos(np.dot(x4_l, x3_l))

        x4_r_k = (right_hand_k - right_elbow_k) / np.linalg.norm(right_hand_k - right_elbow_k)
        x4_r = np.dot(A, x4_r_k)
        beta_r = np.arccos(np.dot(x4_r, x3_r))

        self.skeleton_angles = [phi, theta, alpha_l, beta_l, alpha_r,  beta_r]

        pub_str = ''
        for s in self.skeleton_angles:
            pub_str += str(s) + ','
        self.pub.publish(pub_str[:-1])
        # print('====== skeleton_angles ====== published: ', pub_str[:-1])

skeleton_angles = SkeletonAngles()
skeleton_angles.start()