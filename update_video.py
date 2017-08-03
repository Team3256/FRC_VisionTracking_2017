import cv2

def main():
	frame = cv2.imread("./frame.jpg", 1)
	hsv = cv2.imread("./hsv.jpg", 1)
	mask = cv2.imread("./mask.jpg", 1)
	cv2.imshow('mask', mask)
        cv2.imshow('HSV', hsv)
        cv2.imshow('frame',frame)	

if __name__ == '__main__':
	main()
