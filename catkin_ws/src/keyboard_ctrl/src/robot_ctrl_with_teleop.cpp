#include "ros/ros.h"
#include "geometry_msgs/Twist.h"
#include "std_msgs/Float64.h"
#include "std_msgs/Float32.h"
#include <cmath>

const double WHEEL_BASE = 0.5;

float left_motor_speed = 0; //rads-1
float right_motor_speed = 0; //rads-1

float rorate_center_to_veh_center = 1; // 1m
double omega_z = 0;



void cmd_vel_callback(const geometry_msgs::Twist& msg)
{
  omega_z = msg.angular.z;

  if(omega_z > 0){
    left_motor_speed = omega_z * (rorate_center_to_veh_center-WHEEL_BASE/2);
    right_motor_speed = omega_z * (rorate_center_to_veh_center+WHEEL_BASE/2);
  }else if(omega_z < 0){
    left_motor_speed = omega_z * (rorate_center_to_veh_center+WHEEL_BASE/2);
    right_motor_speed = omega_z * (rorate_center_to_veh_center-WHEEL_BASE/2);
  }else{
    left_motor_speed = msg.linear.x;
    right_motor_speed = msg.linear.x;
  }

  ROS_INFO_STREAM("left - " << left_motor_speed << ", right - " << right_motor_speed);
  
}


int main(int argc, char **argv)
{
  ros::init(argc, argv, "keyboard_ctrl_node");
  ros::NodeHandle n;

  ros::Subscriber sub_vel = n.subscribe("/cmd_vel", 100, cmd_vel_callback);
  
  ros::Publisher pub_front_LW = n.advertise<std_msgs::Float32>("/left_m_speed", 100);
  ros::Publisher pub_front_RW = n.advertise<std_msgs::Float32>("/right_m_speed", 100);

  ros::Rate rate(50);

  while (ros::ok())
  {
    std_msgs::Float32 left_msg;
    std_msgs::Float32 right_msg;

    left_msg.data = left_motor_speed;
    right_msg.data = right_motor_speed;

    pub_front_LW.publish(left_msg);
    pub_front_RW.publish(right_msg);

    ros::spinOnce();

    rate.sleep();
  }
  ros::spin();
  return 0;
}
