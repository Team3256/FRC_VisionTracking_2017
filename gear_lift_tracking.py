#!/usr/bin/env python
import cv2
import numpy as np
import constants
import logging
from networktables import NetworkTables
import random
import Image
import time
import math

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
    cap = cv2.VideoCapture(-1)
    #Set camera values
    cap.set(3, constants.CAM_WIDTH)
    cap.set(4, constants.CAM_HEIGHT)
    cap.set(10, constants.CAM_BRIGHTNESS)
    #cap.set(15, constants.CAM_EXPOSURE)

    logging.basicConfig(level=logging.DEBUG)

    NetworkTables.setIPAddress(constants.ROBORIO_IP)
    NetworkTables.setClientMode()
    NetworkTables.initialize()
    nt = NetworkTables.getTable('SmartDashboard')
    start_time = time.time()
    while cap.isOpened():
        try:
            nt.putNumber('testing', random.randint(1, 100))
            #print nt.getNumber('gyro',0)
            #print nt.getNumber('dt',0)
            _,frame=cap.read()
            #frame = cv2.imread('/home/ubuntu/FRC_VisionTracking_2017/LED Peg/1ftH2ftD2Angle0Brightness.jpg')
            #converts bgr vals of image to hsv
            hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
            #Range for green light reflected off of the tape. Need to tune.
            lower_green = np.array(constants.LOWER_GREEN, dtype=np.uint8)
            upper_green = np.array(constants.UPPER_GREEN, dtype=np.uint8)

            #Threshold the HSV image to only get the green color.
            mask = cv2.inRange(hsv, lower_green, upper_green)
            #Gets contours of the thresholded image.
            contours_fullres, hierarchy = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_TC89_KCOS)
            contours_fullres = [x for x in contours_fullres if cv2.contourArea(x) >= constants.MIN_CONTOUR_AREA]
            contours = []
            for contour in contours_fullres:
                epsilon = 0.1*cv2.arcLength(contour, True)
                approx_contour = cv2.approxPolyDP(contour, epsilon, True)
                if len(approx_contour) == 4:
                    contours.append(approx_contour)
            #Draw the contours around detected object
            cv2.drawContours(frame, contours, -1, (0,0,255), 3)
            #Get centroid of tracked object.
            #Check to see if contours were found.
            if len(contours)>0:   
            #find largest contour
                cnt = max(contours, key=cv2.contourArea)

                i = 0
                while i < len(contours):
                    if np.array_equal(contours[i], cnt):
                        cv2.drawContours(frame, contours, i, (0, 255, 255), 3)
                        contours.pop(i)
                    i += 1

                #get center
                center = get_center(cnt)

                if contours != []:
                    # Find second largest contour
                    cnt2 = max(contours, key=cv2.contourArea)
                    i = 0
                    while i < len(contours):
                        if np.array_equal(contours[i], cnt2):
                            cv2.drawContours(frame, contours, i, (0, 255, 255), 3)
                        i += 1
                    center2 = get_center(cnt2)

                    center_x = int((center[0] + center2[0]) / 2)
                    center_y = int((center[1] + center2[1]) / 2)
                    # Midpoint between two centers
                    midpoint = (center_x, center_y)
                    cv2.circle(frame, midpoint, 5, (0, 255, 255), 2)
                    angle = get_offset_angle(center_x, center_y)
                    angleStr = str(round(angle[0], 2))
                    nt.putNumber('gyro', angle[0])
                    cv2.putText(frame, 'Angle: ' + angleStr, constants.TEXT_COORDINATE_1, cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
                    cv2.circle(frame, (144 + 12 * (len(angleStr) - 5), 4), 3, (0, 255, 255), 2)
                    cv2.putText(frame, 'Direction: ' + angle[1], constants.TEXT_COORDINATE_2, cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)

            if time.time() - start_time >= 1.0/constants.FPS:
                start_time = time.time()
                imgArray = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                jpg = Image.fromarray(imgArray)
                jpg = jpg.resize((480, 360))
                jpg.save('frame.jpg')
                start_time = time.time()

            #show image
            #cv2.imshow('frame',frame)
            #cv2.imshow('mask', mask)
            #cv2.imshow('HSV', hsv)

            #close if delay in camera feed is too long
            k = cv2.waitKey(20) & 0xFF
            if k == 27:
                break
        except Exception as e:
            print(e)
            continue

    #cv2.destroyAllWindows()

if __name__ == '__main__':
    #runs main
    main()

