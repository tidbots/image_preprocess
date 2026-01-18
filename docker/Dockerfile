FROM ros:noetic-ros-base

ARG DEBIAN_FRONTEND=noninteractive

# ---- 基本ツール ----
RUN apt-get update && apt-get install -y \
    build-essential \
    git \
    python3-pip \
    python3-opencv \
    ros-noetic-cv-bridge \
    ros-noetic-image-transport \
    ros-noetic-camera-info-manager \
 && rm -rf /var/lib/apt/lists/*

# ---- catkin tools ----
RUN apt-get update && apt-get install -y \
    python3-catkin-tools \
 && rm -rf /var/lib/apt/lists/*

# ---- workspace ----
WORKDIR /catkin_ws
COPY src /catkin_ws/src

# ---- build ----
RUN /bin/bash -c "source /opt/ros/noetic/setup.bash && catkin_make"

# ---- entrypoint ----
COPY docker/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

ENV ROS_PACKAGE_PATH=/catkin_ws/src:${ROS_PACKAGE_PATH}
ENV YOLO_CONFIG_DIR=/tmp/Ultralytics

ENTRYPOINT ["/entrypoint.sh"]
CMD ["bash"]
