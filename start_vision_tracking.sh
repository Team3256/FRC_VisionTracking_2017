#!/bin/bash
sleep 30
exec 2> /tmp/rc.local.log
exec 1>&2
set -x
cd /home/ubuntu/FRC_VisionTracking_2017
python start_vision.py &
