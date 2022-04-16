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

input_URI = "csi://1"
output_URI = ""
network = "ssd-mobilenet-v2"
overlay = "box,labels,conf"
threshold = 0.5
is_headless = [""]

class DetectionObject:
	def __init__(self, classID, confidence, left, top, right, bottom, width, height, area, center):
		self.classID = classID
		self.Width = width 
		self.Height = height 
		self.Area = area 
		self.Center = center
		self.Confidence = confidence 
		self.Left = left 
		self.Top = top 
		self.Right = right 
		self.Bottom = bottom 
################################

H_FOV = 62.2 #Horizontal FOV for RPi v2
V_FOV = 48.8 #Vertical FOV for RPi v2
RESOLUTION_H = 1280 #Horizontal Resolution
RESOLUTION_V = 720 #Vertical Resolution
IMAGE_CENTER = [RESOLUTION_H/2, RESOLUTION_V/2] #Center of the image
CLASSID = 44 #bottle

def calculate_angle(object):
	angle_of_a_pixel_h = H_FOV/RESOLUTION_H
	angle_of_a_pixel_v = V_FOV/RESOLUTION_V

	angle = None

	if object != None:
		angle = (IMAGE_CENTER[0] - object.Center[0])*angle_of_a_pixel_h #negative -> right hand, positive -> left hand
	
	return angle 

def filter_objects(detections):
	max_area_objects = [None, None]
	max_area = -1
	for detection in detections:
		if detection.Area>max_area and calculate_angle(detection)<=0:
			max_area_objects[0] = detection 
			max_area = detection.Area 
	max_area_s = -1
	for detection in detections:
		if detection.Area>max_area_s and max_area_objects[0] != None and detection.Area<max_area_objects[0].Area:
			max_area_objects[1] = detection
			max_area_s = detection.Area 
	return max_area_objects

def get_angle(detections):
	filtered_objects = filter_objects(detections)

	angle_nearest_object = calculate_angle(filtered_objects[0])

	return angle_nearest_object

def image_pub():
	pub = rospy.Publisher('/right_cam', Image, queue_size = 1)
	rospy.init_node('right_image_node', anonymous = False)
	rate = rospy.Rate(10)

	# create video output object 
	output = jetson.utils.videoOutput(output_URI, argv=sys.argv+is_headless)
		
	# load the object detection network
	net = jetson.inference.detectNet(network, sys.argv, threshold)

	# create video sources
	input = jetson.utils.videoSource(input_URI, argv=sys.argv)

	average_angle = 0.0
	time_steps = 10
	counter = 1

	# process frames until the user exits
    
	while True:
		
		# capture the next image
		img_right = input.Capture()

		# detect objects in the image (with overlay)
		detections = net.Detect(img_right, overlay=overlay)

		# print the detections
		# print("detected {:d} objects in  image".format(len(detections)))

		filtered_detections = []
		for detection in detections:
			if detection.ClassID == CLASSID:
				filtered_detections.append(detection)

		detections = filtered_detections

		angle = get_angle(detections)

		if angle!=None:
			average_angle+=angle
			counter+=1

		if counter%time_steps==0:
			average_angle /= float(time_steps)
			counter = 1
			print(str(average_angle)+" degrees")

		# render the image
		# output.Render(img_right)
		CV2imgRGBA = jetson.utils.cudaToNumpy(img_right, img_right.width, img_right.height, 4)
		frame_left = cv2.cvtColor(CV2imgRGBA, cv2.COLOR_RGBA2BGR)
		# print(frame_left)

		right_img_frame = Image()
		right_img_frame.header.stamp = rospy.Time.now()
		right_img_frame.height = img_right.height
		right_img_frame.width = img_right.width
		right_img_frame.encoding = "rgb8"
		right_img_frame.is_bigendian = False
		right_img_frame.step = 3*img_right.width
		right_img_frame.data = frame_left.tobytes()

		pub.publish(right_img_frame)

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
		input_URI = "csi://1"
		output_URI = ""
		network = "ssd-mobilenet-v2"
		overlay = "box,labels,conf"
		threshold = 0.5
		is_headless = [""]

		image_pub()
	except rospy.ROSInterruptException:
		pass