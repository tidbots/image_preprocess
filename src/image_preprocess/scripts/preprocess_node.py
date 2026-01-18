#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import rospy
import cv2
import numpy as np
from sensor_msgs.msg import Image
from cv_bridge import CvBridge


class ImagePreprocessNode:
    def __init__(self):
        rospy.init_node("image_preprocess_node")

        # ---- Parameters ----
        self.input_topic  = rospy.get_param("~input_topic",  "/camera/image_raw")
        self.output_topic = rospy.get_param("~output_topic", "/camera/image_preprocessed")

        # 明るさ評価
        self.dark_thresh   = rospy.get_param("~dark_thresh", 60)    # 暗い判定
        self.bright_thresh = rospy.get_param("~bright_thresh", 190) # 明るい判定

        # Gamma設定
        self.gamma_dark   = rospy.get_param("~gamma_dark",   0.6)  # 暗い → 明るく
        self.gamma_normal = rospy.get_param("~gamma_normal", 1.0)
        self.gamma_bright = rospy.get_param("~gamma_bright", 1.6)  # 白飛び抑制

        # CLAHE設定
        self.use_clahe   = rospy.get_param("~use_clahe", True)
        self.clahe_clip  = rospy.get_param("~clahe_clip", 2.0)
        self.clahe_grid  = rospy.get_param("~clahe_grid", 8)

        self.bridge = CvBridge()
        self.sub = rospy.Subscriber(self.input_topic, Image, self.cb, queue_size=1)
        self.pub = rospy.Publisher(self.output_topic, Image, queue_size=1)

        rospy.loginfo("Image preprocess node started")
        rospy.loginfo("Input : %s", self.input_topic)
        rospy.loginfo("Output: %s", self.output_topic)

    def estimate_brightness(self, bgr):
        gray = cv2.cvtColor(bgr, cv2.COLOR_BGR2GRAY)
        return np.mean(gray)

    def apply_gamma(self, img, gamma):
        inv = 1.0 / gamma
        table = np.array([(i / 255.0) ** inv * 255 for i in range(256)]).astype("uint8")
        return cv2.LUT(img, table)

    def apply_clahe(self, bgr):
        lab = cv2.cvtColor(bgr, cv2.COLOR_BGR2LAB)
        l, a, b = cv2.split(lab)
        clahe = cv2.createCLAHE(
            clipLimit=self.clahe_clip,
            tileGridSize=(self.clahe_grid, self.clahe_grid)
        )
        cl = clahe.apply(l)
        merged = cv2.merge((cl, a, b))
        return cv2.cvtColor(merged, cv2.COLOR_LAB2BGR)

    def cb(self, msg):
        try:
            img = self.bridge.imgmsg_to_cv2(msg, "bgr8")
        except Exception as e:
            rospy.logerr("cv_bridge error: %s", e)
            return

        brightness = self.estimate_brightness(img)

        # ---- Gamma selection ----
        if brightness < self.dark_thresh:
            gamma = self.gamma_dark
            state = "DARK"
        elif brightness > self.bright_thresh:
            gamma = self.gamma_bright
            state = "BRIGHT"
        else:
            gamma = self.gamma_normal
            state = "NORMAL"

        img = self.apply_gamma(img, gamma)

        if self.use_clahe:
            img = self.apply_clahe(img)

        rospy.logdebug("Brightness=%.1f State=%s Gamma=%.2f",
                       brightness, state, gamma)

        out = self.bridge.cv2_to_imgmsg(img, "bgr8")
        out.header = msg.header
        self.pub.publish(out)


if __name__ == "__main__":
    ImagePreprocessNode()
    rospy.spin()

