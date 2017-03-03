#!/bin/bash

#This lowers the camera exposure
v4l2-ctl -c exposure_auto=1 -c exposure_absolute=30 -d /dev/video1 &

#This starts up the vision tracking and image sender
cd /home/ubuntu/FRC_VisionTracking_2017
python gear_lift_tracking.py &
python image_sender.py &
