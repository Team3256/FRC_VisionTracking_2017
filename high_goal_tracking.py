#!/usr/bin/env python
import os
import cv2
import numpy as np
import constants
import logging
import random
import time
import math
from networktables import NetworkTables

def solidity(contour):
    x,y,w,h = cv2.boundingRect(contour)
    return cv2.contourArea(contour)/(w*h)

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
	print center
        return center

def get_delta_x(x):
    #returns difference of X value of center of the tracked object to the targets X value
    return constants.TARGET_X-x

def get_offset_angle(center_x):
    delta_x = get_delta_x(center_x)
    x = (2.0*(center_x/640.0))-1
    deg = math.fabs(x) * 57.0 / 2.0; 
    if (delta_x<0):
	direction = "right"
    else:
	direction = "left"
    return (deg, direction)

'''
def get_offset_angle(center_x):
    delta_x = get_delta_x(center_x)
    tan_ratio = float(math.fabs(delta_x)/constants.FOCAL_LENGTH)
    angle_radians = math.atan(tan_ratio)
    degrees = float(angle_radians*constants.RADIAN_TO_DEGREE)
    if (delta_x<0):
	direction = "right"
    else:
	direction = "left"
    return (degrees, direction)
'''

def get_distance_from_cam(pixel_width):
    # Return distance from camera in inches
    return constants.GOAL_WIDTH * constants.FOCAL_LENGTH / pixel_width

def main():
    os.system('v4l2-ctl -c exposure_auto=1 -c exposure_absolute=1 -d /dev/video1')
    cap = cv2.VideoCapture(1)
    #Set camera values
    cap.set(cv2.cv.CV_CAP_PROP_FRAME_WIDTH, constants.CAM_WIDTH)
    cap.set(cv2.cv.CV_CAP_PROP_FRAME_HEIGHT, constants.CAM_HEIGHT)
    cap.set(cv2.cv.CV_CAP_PROP_BRIGHTNESS, constants.CAM_BRIGHTNESS)
    #cap.set(15, constants.CAM_EXPOSURE)

    logging.basicConfig(level=logging.DEBUG)

    NetworkTables.setIPAddress(constants.ROBORIO_IP)
    NetworkTables.setClientMode()
    NetworkTables.initialize()
    nt = NetworkTables.getTable('SmartDashboard')
    while cap.isOpened():
        try:
            #nt.putNumber('testing', random.randint(1, 100))
            #print nt.getNumber('gyro',0)
            #print nt.getNumber('dt',0)
            _,frame=cap.read()

            #kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3,3))
            #frame = cv2.morphologyEx(frame, cv2.MORPH_CLOSE, kernel)
            
            #frame = cv2.imread('C:\\Users\\Team 3256\\Desktop\\high goal tracking\\test pics\\j (33).jpg')
            #cv2.rectangle(frame, (0, 240), (640, 480), (0, 0, 0), 150)
            #converts bgr vals of image to hsv
            hsv = cv2.cvtColor(frame, cv2.COLOR_RGB2HSV)
            #Range for green light reflected off of the tape. Need to tune.
            lower_green = np.array(constants.LOWER_GREEN, dtype=np.uint8)
            upper_green = np.array(constants.UPPER_GREEN, dtype=np.uint8)

            #Threshold the HSV image to only get the green color.
            mask = cv2.inRange(hsv, lower_green, upper_green)
            #Gets contours of the thresholded image.
            contours, hierarchy = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            contours = [x for x in contours if cv2.contourArea(x) >= constants.MIN_CONTOUR_AREA and solidity(x) >= 0.4 and solidity(x) <= 1]
            #Draw the contours around detected object
            cv2.drawContours(frame, contours, -1, (0,0,255), 2)
            #Get centroid of tracked object.
            #Check to see if contours were found.
            if len(contours) > 0:   
            #find largest contour

                cnt = max(contours, key = cv2.contourArea)

                i = 0
                while i < len(contours):
                    if np.array_equal(contours[i], cnt):
                        cv2.drawContours(frame, contours, i, (0, 255, 255), 2)
                        contours.pop(i)
                    i += 1

                #get center
                center = get_center(cnt)
                cv2.circle(frame, center, 3, (0, 255, 255), 2)
                
                # Calculate the width of the contour in pixels
                leftmost = tuple(cnt[cnt[:,:,0].argmin()][0])
                rightmost = tuple(cnt[cnt[:,:,0].argmax()][0])
                pixel_width = rightmost[0] - leftmost[0]

                distance_away = get_distance_from_cam(pixel_width)
		distance_away = math.sqrt(distance_away**2 - (86-20)**2)
                nt.putNumber('vision_distance', distance_away)
                print 'distance: ' + str(distance_away)
		
		angle = get_offset_angle(center[0])
                nt.putNumber('vision_angle', angle[0] * (-1 if angle[1] == 'left' else 1));
                angleStr = str(round(angle[0], 2))
                print 'angle: ' + angleStr
		print time.time()
		print "\n"
                cv2.putText(frame, "Pixel Width: " + str(pixel_width), constants.TEXT_COORDINATE_3, cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
                cv2.putText(frame, "Distance: " + str(distance_away), constants.TEXT_COORDINATE_4, cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
                #nt.putNumber('gyro', angle[0])
                cv2.putText(frame, 'Angle: ' + angleStr, constants.TEXT_COORDINATE_1, cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
                cv2.circle(frame, (144 + 12 * (len(angleStr) - 5), 4), 3, (0, 255, 255), 2)
                cv2.putText(frame, 'Direction: ' + angle[1], constants.TEXT_COORDINATE_2, cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)



            #show image
            #cv2.imshow('mask', mask)
            #cv2.imshow('HSV', hsv)
            #cv2.imshow('frame',frame)
            cv2.imwrite('/home/ubuntu/FRC_VisionTracking_2017/frame.jpg', frame)
            cv2.imwrite('/home/ubuntu/FRC_VisionTracking_2017/mask.jpg', mask)
            cv2.imwrite('/home/ubuntu/FRC_VisionTracking_2017/hsv.jpg', hsv)

            #close if delay in camera feed is too long
            k = cv2.waitKey(30) & 0xFF
            if k == 27:
                break
        except Exception as e:
            print(e)
            continue
    cv2.destroyAllWindows()

if __name__ == '__main__':
    #runs main
    main()
