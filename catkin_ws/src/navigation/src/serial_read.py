#!/usr/bin/env python

import serial

ser = serial.Serial("/dev/ttyACM0", 9600)

def read_line():
    data = ser.readline()
    if data:
        print(data)

def main():
    
    pass


if __name__ == '__main__':
    try:
        main()
    except rospy.ROSInterruptException:
        pass