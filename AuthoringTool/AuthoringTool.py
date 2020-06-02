import os
import threading


def start_working():

    def run_roscore():
        os.system('roscore &')
        return

    def run_kinect():
        os.system('roslaunch skeleton_markers markers.launch')
        return

    def run_robot_angles():
        os.system('python ./skeleton_angles_for_puppet.py')
        return

    def run_expose():
        os.system('python ./expose.py')
        return

    def run_application():
        os.system('python ./ROS_recorder.py')

    def run_motion_control():
        os.system('python ./motion_control.py')
        return

    def run_rfid():
        os.system('rosrun rosserial_python serial_node.py /dev/ttyACM0')
        return


    the_threads = []

    the_threads.append(threading.Thread(target=run_roscore()))
    the_threads.append(threading.Thread(target=run_kinect))
    the_threads.append(threading.Thread(target=run_rfid))
    the_threads.append(threading.Thread(target=run_robot_angles))
    the_threads.append(threading.Thread(target=run_expose))
    the_threads.append(threading.Thread(target=run_motion_control))
    the_threads.append(threading.Thread(target=run_application))

    for t in the_threads:
        t.start()
        threading._sleep(1.0)

start_working()




