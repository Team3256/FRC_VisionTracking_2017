#!/bin/bash

v4l2-ctl -c exposure_auto=1 -c exposure_absolute=10 -d /dev/video1
python gear_lift_tracking.py
