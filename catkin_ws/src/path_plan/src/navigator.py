#!/usr/bin/env python
# license removed for brevity
import rospy
from geometry_msgs.msg import PoseStamped
from geometry_msgs.msg import Quaternion
from tf.transformations import quaternion_from_euler
from std_msgs.msg import Bool
import os

def robot_status_callback(data):
    reached_point = data.data
    print(reached_point)
def navigator():

    global reached_point
    reached_point = True
    initiated = False
    point_idx = 1
    seq = 0

    pub = rospy.Publisher('/move_base_simple/goal', PoseStamped, queue_size = 1)
    rospy.init_node('path_follower', anonymous=True)
    rospy.Subscriber("/goal_achieved", Bool, robot_status_callback)
    # rate = rospy.Rate(10) # 10hz
    
    point_list = []
    path_to_file = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "data/goal_pos.txt")
    data = open(path_to_file)
    for point in data.readlines():
        point_list.append(list(map(float, point.split(" "))))

    while not rospy.is_shutdown():
        
        if point_idx == len(point_list):
            rospy.loginfo("Finished following path!")
        
        elif reached_point == True:
            print("Hi")
            goal_point = PoseStamped()
            goal_point.header.seq = point_idx
            goal_point.header.frame_id = "/map"
            goal_point.header.stamp = rospy.Time.now()
            goal_point.pose.position.x = point_list[point_idx][0]
            goal_point.pose.position.y = point_list[point_idx][1]
            goal_point.pose.position.z = 0

            quat = quaternion_from_euler(0, 0, point_list[point_idx][2])

            goal_point.pose.orientation.x = quat[0]
            goal_point.pose.orientation.y = quat[1]
            goal_point.pose.orientation.z = quat[2]
            goal_point.pose.orientation.w = quat[3]

            pub = rospy.Publisher('/move_base_simple/goal', PoseStamped, queue_size = 1)

            while (pub.get_num_connections() <1):
                print("waiting")

            pub.publish(goal_point)

            point_idx +=1
            reached_point = False

        # rate.sleep()
        # rospy.spin()

if __name__ == '__main__':
    try:
        navigator()
    except rospy.ROSInterruptException:
        pass