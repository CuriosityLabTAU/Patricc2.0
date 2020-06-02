import rospy
from std_msgs.msg import String

rfids = [None for i in range(5)]
rfid_prev = [None for i in range(5)]
rfid_change = [None for i in range(5)]
is_rfid_change = False


class FlowRFID:

    def __init__(self):
        rospy.init_node('ros_flow')
        rospy.Subscriber('/rfid', String, self.callback)
        rospy.spin()


flow_rfid = FlowRFID()
