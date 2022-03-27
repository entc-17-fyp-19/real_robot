#!/usr/bin/env python3

import jetson.inference
import jetson.utils

# import argparse
import sys
import cv2

import rospy
from sensor_msgs.msg import Image
from cv_bridge import CvBridge, CvBridgeError
import numpy as np


# parse the command line

input_URI = "csi://0"
output_URI = ""
network = "ssd-mobilenet-v2"
overlay = "box,labels,conf"
threshold = 0.5
is_headless = [""]

bridge = CvBridge()

def image_pub():
	pub = rospy.Publisher('/left_cam', Image, queue_size = 1)
	rospy.init_node('left_image_node', anonymous = False)
	rate = rospy.Rate(10)

	# try:
	# 	opt = parser.parse_known_args()[0]
	# except:
	# 	print("")
	# 	parser.print_help()
	# 	sys.exit(0)

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
		#img_right = input_right.Capture()

		# print(img_left)

		# detect objects in the image (with overlay)
		detections = net.Detect(img_left, overlay=overlay)

		# print the detections
		print("detected {:d} objects in  image".format(len(detections)))

		for detection in detections:
			print(detection)

		# render the image
		#output.Render(img_left)
		CV2imgRGBA = jetson.utils.cudaToNumpy(img_left, img_left.width, img_left.height, 4)
		frame_left = cv2.cvtColor(CV2imgRGBA, cv2.COLOR_RGBA2BGR)
		# print(frame_left)

		# update the title bar
		output.SetStatus("{:s} | Network {:.0f} FPS".format(network, net.GetNetworkFPS()))

		# print out performance info
		# net.PrintProfilerTimes()

		# msg = bridge.cv2_to_imgmsg(frame_left, "bgr8")
		im = np.frombuffer(frame_left, dtype=np.uint8).reshape(img_left.height, img_left.width, -1)
		msg = bridge.cv2_to_imgmsg(im, "bgr8")
		# pub.publish(im)

		# exit on input/output EOS
		if not input.IsStreaming() or not output.IsStreaming(): # or rospy.is_shutdown()
			break

if __name__ == '__main__':
	try:
		# parser = argparse.ArgumentParser(description="Locate objects in a live camera stream using an object detection DNN.", 
		# 								formatter_class=argparse.RawTextHelpFormatter, epilog=jetson.inference.detectNet.Usage() +
		# 								jetson.utils.videoSource.Usage() + jetson.utils.videoOutput.Usage() + jetson.utils.logUsage())

		# parser.add_argument("input_URI", type=str, default="", nargs='?', help="URI of the input stream")
		# parser.add_argument("output_URI", type=str, default="", nargs='?', help="URI of the output stream")
		# parser.add_argument("--network", type=str, default="ssd-mobilenet-v2", help="pre-trained model to load (see below for options)")
		# parser.add_argument("--overlay", type=str, default="box,labels,conf", help="detection overlay flags (e.g. --overlay=box,labels,conf)\nvalid combinations are:  'box', 'labels', 'conf', 'none'")
		# parser.add_argument("--threshold", type=float, default=0.5, help="minimum detection threshold to use") 

		# is_headless = ["--headless"] if sys.argv[0].find('console.py') != -1 else [""]

		input_URI = "csi://1"
		output_URI = ""
		network = "ssd-mobilenet-v2"
		overlay = "box,labels,conf"
		threshold = 0.5
		is_headless = [""]

		image_pub()
	except rospy.ROSInterruptException:
		pass