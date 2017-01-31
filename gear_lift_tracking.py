#!/usr/bin/env python

import cv2
import numpy as np
import constants

def get_center(contour):
    #get moments data from contour
    moments = cv2.moments(contour)
    #get center x and y value from image
    center = (0,0)

    if moments["m00"] > 0:
        center_x = int(moments["m10"]/moments["m00"])
        center_y = int(moments["m01"]/moments["m00"])
        #return a tuple with center coordinates
        center = (center_x, center_y)
    return center

def get_delta_x(x):
    #returns difference of X value of center of the tracked object to the targets X value
    return constants.TARGET_X-x

def get_delta_y(y):
    #returns difference of Y value of center of the tracked object to the targets Y value
    return constants.TARGET_Y-y

def get_offset_angle(center_x, center_y):
    delta_x = get_delta_x(center_x)
    tan_ratio = float(math.fabs(delta_x)/constants.DIST_CAM_TO_CENTER)
    angle_radians = math.atan(tan_ratio)
    degrees = float(angle_radians*constants.RADIAN_TO_DEGREE)
    if(delta_x<0):
        #direction = 1 #turn right
        direction = "right"
    else:
        #direction = 0 #turn left
        direction = "left"

    return (degrees, direction)

def main():
    cap = cv2.VideoCapture(0)

    #Set camera values
    cap.set(3, constants.CAM_WIDTH)
    cap.set(4, constants.CAM_HEIGHT)
    cap.set(10, constants.CAM_BRIGHTNESS)
    #cap.set(15, constants.CAM_EXPOSURE)

    #NetworkTable.setIPAddress('10.32.56.18')
    #NetworkTable.setClientMode()
    #NetworkTable.initialize()

    #nt = NetworkTable.getTable('SmartDashboard')

    while cap.isOpened():

        frame=cv2.imread("/home/ubuntu/Documents/Vision Images/LED Peg/1ftH5ftD0Angle0Brightness.jpg")
        #converts bgr vals of image to hsv
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        #Range for green light reflected off of the tape. Need to tune.
        lower_green = np.array(constants.LOWER_GREEN, dtype=np.uint8)
        upper_green = np.array(constants.UPPER_GREEN, dtype=np.uint8)

        #Threshold the HSV image to only get the green color.
        mask = cv2.inRange(hsv, lower_green, upper_green)
        #Gets contours of the thresholded image.
        contours, hierarchy = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_TC89_KCOS)
        #Draw the contours around detected object
        #cv2.drawContours(frame, contours, -1, (0,0,255), 3)

        #Get centroid of tracked object.
        #Check to see if contours were found.
        if len(contours)>0:
            #find largest contour
            cnt = max(contours, key=cv2.contourArea)	
	    
	    i = 0
	    while i < len(contours):
		if np.array_equal(contours[i], cnt):
			contours.pop(i)
		
		i += 1

	    # Find second largest contour
	    cnt2 = max(contours, key=cv2.contourArea)

            #get center
            center = get_center(cnt)
            cv2.circle(frame, center, 3, (0,0,255), 2)

	    center2 = get_center(cnt2)
	    cv2.circle(frame, center2, 3, (0, 0, 255), 2)

	    # Midpoint between two centers
	    midpoint = (int((center[0] + center2[0]) / 2), int((center[1] + center2[1]) / 2))
	    cv2.circle(frame, midpoint, 3, (0, 0, 255), 2)

        #show image
        cv2.imshow('frame',frame)
        cv2.imshow('mask', mask)
        cv2.imshow('HSV', hsv)

        #close if delay in camera feed is too long
        k = cv2.waitKey(1) & 0xFF
        if k == 27:
            break

    cv2.destroyAllWindows()

if __name__ == '__main__':
    #runs main
    main()
