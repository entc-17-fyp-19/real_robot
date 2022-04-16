#!/usr/bin/env python3

import jetson.inference
import jetson.utils

# import argparse
import sys
import cv2

import rospy
from sensor_msgs.msg import Image
# from cv_bridge import CvBridge, CvBridgeError
import numpy as np

# parse the command line

input_URI = "csi://0"
output_URI = ""
network = "ssd-mobilenet-v2"
overlay = "box,labels,conf"
threshold = 0.5
is_headless = [""]


def image_pub():
	pub = rospy.Publisher('/left_cam', Image, queue_size = 1)
	rospy.init_node('left_image_node', anonymous = False)
	rate = rospy.Rate(10)

	# create video output object 
	output = jetson.utils.videoOutput(output_URI, argv=sys.argv+is_headless)
		
	# load the object detection network
	net = jetson.inference.detectNet(network, sys.argv, threshold)

	# create video sources
	input = jetson.utils.videoSource(input_URI, argv=sys.argv)

	# process frames until the user exits
	while True:
		
		# capture the next image
		img_left = input.Capture()

		# detect objects in the image (with overlay)
		detections = net.Detect(img_left, overlay=overlay)

		# print the detections
		# print("detected {:d} objects in  image".format(len(detections)))

		# for detection in detections:
		# 	print(detection)

		# render the image
		# output.Render(img_left)
		CV2imgRGBA = jetson.utils.cudaToNumpy(img_left, img_left.width, img_left.height, 4)
		frame_left = cv2.cvtColor(CV2imgRGBA, cv2.COLOR_RGBA2BGR)
		# print(frame_left)

		left_img_frame = Image()
		left_img_frame.header.stamp = rospy.Time.now()
		left_img_frame.height = img_left.height
		left_img_frame.width = img_left.width
		left_img_frame.encoding = "rgb8"
		left_img_frame.is_bigendian = False
		left_img_frame.step = 3*img_left.width
		left_img_frame.data = frame_left.tobytes()

		pub.publish(left_img_frame)

		# update the title bar
		output.SetStatus("{:s} | Network {:.0f} FPS".format(network, net.GetNetworkFPS()))

		# print out performance info
		# net.PrintProfilerTimes()
		rate.sleep()
		# exit on input/output EOS
		if not input.IsStreaming() or not output.IsStreaming() or rospy.is_shutdown(): # or rospy.is_shutdown()
			break

if __name__ == '__main__':
	try:
		input_URI = "csi://0"
		output_URI = ""
		network = "ssd-mobilenet-v2"
		overlay = "box,labels,conf"
		threshold = 0.5
		is_headless = [""]

		image_pub()
	except rospy.ROSInterruptException:
		pass