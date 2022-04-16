#!/usr/bin/env python
import rospy
import math
import numpy as np
from tf.transformations import euler_from_quaternion
from nav_msgs.msg import Odometry
from visualization_msgs.msg import Marker
from geometry_msgs.msg import Point
from std_msgs.msg import String

# define path coordinates
path_x = [0, 4.0]
path_y = [0, 5.0]

focus_point = 1

start_point = np.array([path_x[focus_point - 1], path_y[focus_point - 1]])
end_point = np.array([path_x[focus_point], path_y[focus_point]])

current_x = 0
current_y = 0

last_current_x = 0
last_current_y = 0
current_pos_list = []

heading_angle = 0
angle_path_to_head = 0
correction_omega = 1 # rotating about center


WHEEL_BASE = 0.54
WHEEL_RADIUS = 0.16
heading_vel = 0.05
CENTER_TO_WHEEL = 0.29

# At one end point
REACH_THRESHOLD = 0.1

# Thresholds to find temp location
L1 = 0.1
L1_min = L1
L1_increment = 0.05
TEMP_THRESHOLD = 0.15

# limits

max_omega = 3

pub_points = rospy.Publisher('/visualize_points', Marker, queue_size = 50)
pub_path = rospy.Publisher('/visualize_path', Marker, queue_size = 50)
pub_motor_values = rospy.Publisher('/motor_spd', String, queue_size = 30)

def degree_to_radian(degree):
    return (math.pi/180)*degree

def radian_to_degree(radian):
    return (180/math.pi)*radian

def tan(degree):
    return math.tan(math.radians(degree))

def cos(degree):
    return math.cos(math.radians(degree))

def sin(degree):
    return math.sin(math.radians(degree))

def cal_path_parameters():
    param = [0, 0, "N"] # [angle, intercept, "N"] or [m, y, "Y"] or [m, x, "X"]
    if ((end_point - start_point)[0] == 0):
        if((end_point - start_point)[1] >= 0):
            param[0] = 90
        else:
            param[0] = 270
        
        param[1] = start_point[0]
        param[2] = "X"
    elif ((end_point - start_point)[1] == 0):
        if((end_point - start_point)[0] >= 0):
            param[0] = 0
        else:
            param[0] = 180
        
        param[1] = start_point[1]
        param[2] = "Y"
    else:
        param[0] = radian_to_degree(math.atan((end_point[1] - start_point[1])/(end_point[0] - start_point[0])))
        param[1] = end_point[1] - tan(param[0])*end_point[0]
        param[2] = "N"
    
    # print(param)
    return param

def cal_perp_loc():
    perp_loc = [0, 0] # [x,y]
    orig_path = cal_path_parameters()

    if (orig_path[2] == 'Y'):
        perp_loc[0] = current_x
        perp_loc[1] = orig_path[1]
        return perp_loc
    
    elif (orig_path[2] == 'X'):
        perp_loc[0] = orig_path[1]
        perp_loc[1] = current_y
        return perp_loc
    
    perp_loc[0] = (current_y + (current_x/tan(orig_path[0])) - orig_path[1])/(tan(orig_path[0]) + 1/tan(orig_path[0]))
    perp_loc[1] = ((current_y + (current_x/tan(orig_path[0])) - orig_path[1])/(1 + 1/(tan(orig_path[0])**2))) + orig_path[1]
    
    return perp_loc

def cal_temp_end():
    global L1
    temp_end_point = [0, 0]
    
    perp_point = cal_perp_loc()
    orig_path = cal_path_parameters()
    d = math.sqrt((perp_point[0] - current_x)**2 + (perp_point[1] - current_y)**2)
    
    dis_to_end = math.sqrt((current_x - end_point[0])**2 + (current_y - end_point[1])**2)
    
    
    if (dis_to_end < L1):
        L1 = dis_to_end
    else:
        L1 = L1_min
    
    while (1):
        if (d < L1):
            l = math.sqrt(L1**2 - d**2)
            if (l >= TEMP_THRESHOLD):
                temp_end_point[0] = perp_point[0] + l * cos(orig_path[0])
                temp_end_point[1] = perp_point[1] + l * sin(orig_path[0])
                break
            else:
                L1 += L1_increment
                continue
        else:
            L1 += L1_increment
    
    return temp_end_point

def cal_arc_angle():
    global angle_path_to_head
    orig_path = cal_path_parameters()
    perp_point = cal_perp_loc()
    temp_end = cal_temp_end()
    
    if (temp_end == "OOC"):
        return "STOP"
    
    n2 = (heading_angle - orig_path[0])
    # print("heading_angle - " + str(heading_angle))
    # print("orig_path[0] - " + str(orig_path[0]))
    angle_path_to_head = n2
    d = math.sqrt((perp_point[0] - current_x)**2 + (perp_point[1] - current_y)**2)
    L_temp = math.sqrt((temp_end[0] - current_x)**2 + (temp_end[1] - current_y)**2)

    n1 = radian_to_degree(math.asin(d/L_temp))
    dis_to_end = math.sqrt((current_x - end_point[0])**2 + (current_y - end_point[1])**2)
    
    # print(dis_to_end)
    if(dis_to_end < REACH_THRESHOLD):
        return "STOP"
    else:
        cross_product = np.cross([current_x - temp_end[0], current_y - temp_end[1]], [perp_point[0] - temp_end[0], perp_point[1] - temp_end[1]])
        
        if (cross_product > 0):
            return n1 + n2
        else:
            return n2 - n1

def wheel_velocity():
    angle = cal_arc_angle()
    
    if angle == "STOP":
        return "REACHED"

    if (abs(angle_path_to_head) > 45):
        angle = math.atan(CENTER_TO_WHEEL/(WHEEL_BASE/2))
        dis = math.sqrt((WHEEL_BASE/2)**2 + CENTER_TO_WHEEL**2)

        if(angle_path_to_head > 0):
            left_motor_speed = (dis * correction_omega)*math.cos(angle)
            right_motor_speed = -1 * (dis * correction_omega)*math.cos(angle)
            print('left')
        else:
            left_motor_speed = -1 * (dis * correction_omega)*math.cos(angle)
            right_motor_speed = (dis * correction_omega)*math.cos(angle)
            print('right')            

    else:
        if (angle != 0):
            dis_from_center = L1/(2*(sin(angle)))
            if (angle > 0):
                dis_from_center = abs(dis_from_center)

            omega = heading_vel/dis_from_center

            if(dis_from_center > 0):
                left_angle = math.atan(CENTER_TO_WHEEL/(dis_from_center + WHEEL_BASE/2))
                right_angle = math.atan(CENTER_TO_WHEEL/(dis_from_center - WHEEL_BASE/2))

                left_dis = math.sqrt((dis_from_center + WHEEL_BASE/2)**2 + CENTER_TO_WHEEL**2)
                right_dis = math.sqrt((dis_from_center - WHEEL_BASE/2)**2 + CENTER_TO_WHEEL**2)

                left_motor_speed = (left_dis * omega * math.cos(left_angle))/WHEEL_RADIUS
                right_motor_speed = (right_dis * omega * math.cos(right_angle))/WHEEL_RADIUS
            else:
                dis_from_center = abs(dis_from_center)
                omega = -1 * omega

                left_angle = math.atan(CENTER_TO_WHEEL/(dis_from_center - WHEEL_BASE/2))
                right_angle = math.atan(CENTER_TO_WHEEL/(dis_from_center + WHEEL_BASE/2))

                left_dis = math.sqrt((dis_from_center - WHEEL_BASE/2)**2 + CENTER_TO_WHEEL**2)
                right_dis = math.sqrt((dis_from_center + WHEEL_BASE/2)**2 + CENTER_TO_WHEEL**2)

                left_motor_speed = (left_dis * omega * math.cos(left_angle))/WHEEL_RADIUS
                right_motor_speed = (right_dis * omega * math.cos(right_angle))/WHEEL_RADIUS
        else:
            left_motor_speed = heading_vel/WHEEL_RADIUS
            right_motor_speed = heading_vel/WHEEL_RADIUS

    print("Left - " + str(left_motor_speed) + ", Right - " + str(right_motor_speed))    
     
    if (left_motor_speed < 0):
        left_motor_speed = 0
    elif(left_motor_speed > 3):
        left_motor_speed = 3 

    if (right_motor_speed < 0):
        right_motor_speed = 0
    elif(right_motor_speed > 3):
        right_motor_speed = 3  
        
    
    
    return [left_motor_speed, right_motor_speed]

def odom_callback(msg):
    global heading_angle, current_x, current_y
    current_pos = Point()
    current_pos = msg.pose.pose.position
    current_x = current_pos.x
    current_y = current_pos.y
    orientation = msg.pose.pose.orientation
    (roll, pitch, yaw) = euler_from_quaternion([orientation.x, 
                                                orientation.y, 
                                                orientation.z,
                                                orientation.w])
    #

    heading_angle = radian_to_degree(yaw)
    # print(str(current_x) + " - " + str(current_y))
    # print(heading_angle)

def visualize_perp():
    global pub_path
    perp = cal_perp_loc()

    p = Point()
    p.x = float(perp[0])
    p.y = float(perp[1])
    p.z = 0

    c = Point()
    c.x = float(current_x)
    c.y = float(current_y)
    c.z = 0

    perp_line = Marker()
 
    perp_line.header.frame_id = "/map"
    perp_line.header.stamp = rospy.Time.now()
    perp_line.ns = "perpendicular_point"
    perp_line.action = perp_line.ADD
    perp_line.pose.orientation.w = 1.0

    perp_line.id = 10

    perp_line.type = perp_line.LINE_STRIP

    perp_line.scale.x = 0.05

    # perp_line is green
    perp_line.color.r = 1.0
    perp_line.color.a = 1.0

    perp_line.points = [p, c]

    pub_path.publish(perp_line)

def temp_point():
    global pub_path
    temp = cal_temp_end()

    p = Point()
    p.x = float(temp[0])
    p.y = float(temp[1])
    p.z = 0

    c = Point()
    c.x = float(current_x)
    c.y = float(current_y)
    c.z = 0

    temp_line = Marker()
 
    temp_line.header.frame_id = "/map"
    temp_line.header.stamp = rospy.Time.now()
    temp_line.ns = "temp_point"
    temp_line.action = temp_line.ADD
    temp_line.pose.orientation.w = 1.0

    temp_line.id = 11

    temp_line.type = temp_line.LINE_STRIP

    temp_line.scale.x = 0.05

    # temp_line is green
    temp_line.color.r = 1.0
    temp_line.color.g = 1.0
    temp_line.color.a = 1.0

    temp_line.points = [p, c]

    pub_path.publish(temp_line)

def current_pos():
    global pub_points, last_current_x, last_current_y,current_pos_list

    c = Point()
    c.x = float(current_x)
    c.y = float(current_y)
    c.z = 0

    current_point = Marker()
 
    current_point.header.frame_id = "/map"
    current_point.header.stamp = rospy.Time.now()
    current_point.ns = "current_point"
    current_point.action = current_point.ADD
    current_point.pose.orientation.w = 1.0

    current_point.id = 11

    current_point.type = current_point.POINTS

    current_point.scale.x = 0.05

    # current_point is green
    current_point.color.r = 0.5
    current_point.color.g = 0.5
    current_point.color.a = 1.0

    

    if (last_current_x != current_x or last_current_y != current_y):
        last_current_x = current_x
        last_current_y = current_y
        current_pos_list.append(c)
    
    current_point.points = current_pos_list
    pub_path.publish(current_point)

def visualize_path():
    point_list = []
    for i in range(len(path_x)):
        p = Point()
        p.x = float(path_x[i])
        p.y = float(path_y[i])
        p.z = 0
        
        point_list.append(p)

    travel_path = Marker()
    travel_points = Marker()
 
    travel_path.header.frame_id = travel_points.header.frame_id = "/map"
    travel_path.header.stamp = travel_points.header.stamp = rospy.Time.now()
    travel_path.ns = travel_points.ns = "travel_path_and_points"

    travel_path.action = travel_points.action = travel_path.ADD
    travel_path.pose.orientation.w = travel_points.pose.orientation.w = 1.0

    travel_path.id = 14
    travel_points.id = 15

    travel_path.type = travel_path.LINE_STRIP
    travel_points.type = travel_points.POINTS

    travel_path.scale.x = 0.05
    travel_path.scale.y = 0.05

    travel_points.scale.x = 0.05

    # travel_path is blue
    travel_path.color.b = 1.0
    travel_path.color.a = 1.0

    travel_points.color.g = 1.0
    travel_points.color.a = 1.0

    travel_path.points = travel_points.points = point_list

    pub_points.publish(travel_points)
    pub_path.publish(travel_path)


def control_motors():
    global focus_point
    motor_values = wheel_velocity()
    if (motor_values == "REACHED"):
        print("REACHED")
        if (focus_point != len(path_x)-1):
            focus_point += 1

        else:
            motor_values_str = "0+0"
            print("Finished navigation!")
    else:
        motor_values_str = str(motor_values[0]) + "+" + str(motor_values[1])
    
    pub_motor_values.publish(motor_values_str)

def main():
    
    rospy.init_node('navigation_algo', anonymous=True)
    rospy.Subscriber("/odom", Odometry, odom_callback)
    rate = rospy.Rate(2)

    
    while not rospy.is_shutdown():
        visualize_perp()
        temp_point()
        visualize_path()
        current_pos()
        control_motors()
        
        rate.sleep()

    # motor_timer = rospy.Timer(rospy.Duration(0.05), publish_imu)
    # rospy.spin()

if __name__ == '__main__':
    try:
        main()
    except rospy.ROSInterruptException:
        pass

