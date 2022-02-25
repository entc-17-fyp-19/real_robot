execute_process(COMMAND "/home/fyp-19/fyp-real-bot/ros_part/catkin_ws/build/diff_drive/catkin_generated/python_distutils_install.sh" RESULT_VARIABLE res)

if(NOT res EQUAL 0)
  message(FATAL_ERROR "execute_process(/home/fyp-19/fyp-real-bot/ros_part/catkin_ws/build/diff_drive/catkin_generated/python_distutils_install.sh) returned error code ")
endif()
