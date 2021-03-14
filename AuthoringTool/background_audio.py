import rospy
from std_msgs.msg import String
from pygame import mixer
import time
import numpy as np


class BackgroundAudio():
    def __init__(self):
        self.pub = rospy.Publisher ('skeleton_angles', String, queue_size=10)


    def start(self):
        #init a listener
        rospy.init_node('skeleton_angle')
        rospy.Subscriber("skeleton", Skeleton, self.callback)
        rospy.spin()

    def callback(self, data):
        positions = data.position

        pub_str = ''
        for s in self.skeleton_angles:
            pub_str += str(s) + ','
        self.pub.publish(pub_str[:-1])


background_audio = BackgroundAudio()
background_audio.start()

from pygame import mixer
import time
# Starting the mixer
mixer.init()

# Loading the song
mixer.music.load("aussom.mp3")

# Setting the volume
mixer.music.set_volume(0.7)

# Start playing the song
mixer.music.play()

# infinite loop
while True:

    time.sleep(2)
    mixer.music.play()