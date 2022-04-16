#!/usr/bin/env python3
import rospy
from std_msgs.msg import String, Int32, Float32


l_ticks_pub = rospy.Publisher('/lwheel_ticks', Int32, queue_size = 2)
r_ticks_pub = rospy.Publisher('/rwheel_ticks', Int32, queue_size = 2)
l_rate_pub = rospy.Publisher('/lwheel_rate', Float32, queue_size = 2)
r_rate_pub = rospy.Publisher('/rwheel_rate', Float32, queue_size = 2)

lwheel_ticks = 0
rwheel_ticks = 0
lwheel_rate = 0
rwheel_rate = 0

def wheel_data_callback_1(msg):
    global lwheel_ticks, rwheel_ticks, lwheel_rate, rwheel_rate
    data_set = msg.data.split("+")
    # print(data_set)
    lwheel_ticks = int(data_set[0])
    rwheel_ticks = int(data_set[1])
    lwheel_rate = float(data_set[2])
    rwheel_rate = float(data_set[3])


def main():
    rospy.init_node('process_data_node', anonymous=True)
    rospy.Subscriber("/wheel_data_1", String, wheel_data_callback_1)
    # rate = rospy.Rate(100)
    # rospy.spin()

    while not rospy.is_shutdown():
        l_ticks_pub.publish(lwheel_ticks)
        r_ticks_pub.publish(rwheel_ticks)
        l_rate_pub.publish(lwheel_rate)
        r_rate_pub.publish(rwheel_rate)

        # rate.sleep()

if __name__ == '__main__':
    try:
        main()
    except rospy.ROSInterruptException:
        pass