#!/usr/bin/env python2
# license removed for brevity
import rospy
from std_msgs.msg import String
from visualization_msgs.msg import Marker
from geometry_msgs.msg import Point
import os

def points_pub():
    pub = rospy.Publisher('visualize_path', Marker, queue_size = 100)
    rospy.init_node('path_visualizer', anonymous=True)
    rate = rospy.Rate(10) # 10hz

    point_list = []
    # os.path.join(os.path.dirname(os.getcwd()), "data/goal_pos.txt"
    path_to_file = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "data/goal_pos.txt")
    data = open(path_to_file)
    for point in data.readlines():
        x, y, Z_rot = point.split(" ")
        p = Point()
        p.x = float(x)
        p.y = float(y)
        p.z = 0
        point_list.append(p) 


    while not rospy.is_shutdown():
        points = Marker()
        line_strip = Marker()
        points.header.frame_id = line_strip.header.frame_id = "/map"
        points.header.stamp = line_strip.header.stamp = rospy.Time.now()
        points.ns = line_strip.ns = "points_and_lines"
        points.action = line_strip.action = points.ADD
        points.pose.orientation.w = line_strip.pose.orientation.w = 1.0

        points.id = 0
        line_strip.id = 1

        points.type = points.POINTS
        line_strip.type = line_strip.LINE_STRIP

        points.scale.x = 0.05
        points.scale.y = 0.05

        line_strip.scale.x = 0.05

        # Points are green
        points.color.g = 1.0
        points.color.a = 1.0

        # Line strip is blue
        line_strip.color.b = 1.0
        line_strip.color.a = 1.0

        points.points = line_strip.points = point_list

        pub.publish(points)
        pub.publish(line_strip)
        rate.sleep()

if __name__ == '__main__':
    try:
        points_pub()
    except rospy.ROSInterruptException:
        pass