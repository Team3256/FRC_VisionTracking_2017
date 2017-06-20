#!/bin/bash
exec 2> /tmp/rc.local.log
exec 1>&2
set -x
cd /home/ubuntu/Vision/FRC_VisionTracking_2017
python high_goal_tracking.py &
