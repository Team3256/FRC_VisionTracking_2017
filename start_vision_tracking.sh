#!/bin/bash

#This lowers the camera exposure
v4l2-ctl -c exposure_auto=1 -c exposure_absolute=10 -d /dev/video1

#This starts up the vision tracking
python gear_lift_tracking.py
