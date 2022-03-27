#!/usr/bin/env python2
# license removed for brevity
import rospy
from std_msgs.msg import String
from visualization_msgs.msg import Marker
from geometry_msgs.msg import Point
from nav_msgs.msg import Odometry
import os

def odom_callback(msg):
    current_pos = Point()
    current_pos = msg.pose.pose.position
    point_list.append(current_pos)

def points_pub():

    global point_list
    point_list = []
    pub = rospy.Publisher('current_pos', Marker, queue_size = 100)
    rospy.Subscriber("/odom", Odometry, odom_callback)
    rospy.init_node('current_pos_visualizer', anonymous=True)
    rate = rospy.Rate(10) # 10hz 


    while not rospy.is_shutdown():
        odom_point = Marker()
       
        odom_point.header.frame_id = "/map"
        odom_point.header.stamp = rospy.Time.now()
        odom_point.ns = "current_robot_pos"
        odom_point.action = odom_point.ADD
        odom_point.pose.orientation.w = 1.0

        odom_point.id = 4

        odom_point.type = odom_point.POINTS

        odom_point.scale.x = 0.03
        odom_point.scale.y = 0.03

        # Points are green
        odom_point.color.g = 1.0
        odom_point.color.r = 1.0
        odom_point.color.a = 1.0

        # update point 
        odom_point.points = point_list

        pub.publish(odom_point)
        rate.sleep()

if __name__ == '__main__':
    try:
        points_pub()
    except rospy.ROSInterruptException:
        pass