#!/usr/bin/env python2
# license removed for brevity
import rospy
from geometry_msgs.msg import Pose
from geometry_msgs.msg import Quaternion
from tf.transformations import quaternion_from_euler
from std_msgs.msg import Bool
import os

reached_point = False
initiated = False
point_idx = 0

def robot_status_callback(data):
    reached_point = data.data

def navigator():
    pub = rospy.Publisher('follow_path', Pose, queue_size = 10)
    rospy.init_node('path_follower', anonymous=True)
    rospy.Subscriber("/goal_achieved", Bool, robot_status_callback)

    point_list = []
    path_to_file = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "data/goal_pos.txt")
    data = open(path_to_file)
    for point in data.readlines():
        point_list.append(list(map(float, point.split(" "))))

    while not rospy.is_shutdown():

        if reached_point == True:
            point_idx +=1
            reached_point = False

        if point_idx == len(point_list):
            rospy.loginfo("Finished following path")
        else:   
            point = Pose()
            point.position.x = point_list[point_idx][0]
            point.position.y = point_list[point_idx][1]
            point.position.z = 0

            point.orientation = quaternion_from_euler(0, 0, point_list[point_idx][2])
            pub.publish(point)

        rate.sleep()

if __name__ == '__main__':
    reached_point = False
    initiated = False
    point_idx = 0
    try:
        navigator()
    except rospy.ROSInterruptException:
        pass