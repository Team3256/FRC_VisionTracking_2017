from __future__ import print_function
import subprocess

def start():
	popen = subprocess.Popen(["python", "/home/ubuntu/FRC_VisionTracking_2017/high_goal_tracking.py"], stderr=subprocess.PIPE, universal_newlines=True)
	for stdout_line in iter(popen.stderr.readline, ""):
		if "timeout" in stdout_line:
			popen.terminate()
		else:
			print(stdout_line)
	return_code = popen.wait()
	if return_code:
		print("process restarting")
		print(return_code)
		start()

start()