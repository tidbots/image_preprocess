cmake_minimum_required(VERSION 3.0.2)
project(image_preprocess)

find_package(catkin REQUIRED COMPONENTS
  rospy
  sensor_msgs
  cv_bridge
  image_transport
)

catkin_package()

catkin_install_python(PROGRAMS
  scripts/preprocess_node.py
  DESTINATION ${CATKIN_PACKAGE_BIN_DESTINATION}
)

