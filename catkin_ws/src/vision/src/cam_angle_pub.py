# #!/usr/bin/env python

# import rospy
# from std_msgs.msg import String

# pub = rospy.Publisher('/tree_angle', String, queue_size = 5)

# def angle_pub():
#     rospy.init_node('angle_pub_node', anonymous = False)
#     rospy.Subscriber("/left_cam_angle", Odometry, odom_callback)
#     rospy.Subscriber("/left_cam_angle", Odometry, odom_callback)
#     rate = rospy.Rate(2)
	


# if __name__ == '__main__':
# 	try:
# 		angle_pub()
# 	except rospy.ROSInterruptException:
# 		pass