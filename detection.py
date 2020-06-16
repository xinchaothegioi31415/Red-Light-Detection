import cv2
import numpy as np
import matplotlib.path as mplPath
import time
from datetime import datetime
import os
import threading

import requests
# --------------------- GLOBAL --------------- #
poly_ne = np.array([[793,351],[920,466],[1102,420],[961,329]])
tl = (1106,100)
br = (1153,203)
cap = cv2.VideoCapture("test_video.mp4")
img_folder = "./image/"
# Plate Recognizer
regions = ['vn']
IS_FREE = True
ImageNode = []
#----------------------------------------------#

#---------------------- UTILS FUNCTION ---------------#
def pega_centro(x, y, w, h):
    x1 = int(w / 2)
    y1 = int(h / 2)
    cx = x + x1
    cy = y + y1
    return cx,cy
def inside_poly(pnts, poly):
    bbPath = mplPath.Path(poly)
    return bbPath.contains_point(pnts)




def detect_plate(path):
    with open(path, 'rb') as fp:
        response = requests.post(
            'https://api.platerecognizer.com/v1/plate-reader/',
            data=dict(regions=regions),  # Optional
            files=dict(upload=fp),
            headers={'Authorization': 'Token 11e12906b07074d87046cb0e3b530f55dd85a2c1'})
        result = response.json()['results']
        IS_FREE = True
        print(result)
#------------------------------------------------------#

ret, frame1 = cap.read()
ret, frame2 = cap.read()
while cap.isOpened():
    #Detect Red-light
    if frame1 is None or frame2 is None:
        break
    hsv_Frame = cv2.cvtColor(frame1[tl[1]:br[1], tl[0]:br[0]], cv2.COLOR_BGR2HSV)
    low_red = np.array([161, 155, 84], np.uint8)
    high_red = np.array([179, 255, 255], np.uint8)
    mask_red = cv2.inRange(hsv_Frame, low_red, high_red)
    coord=cv2.findNonZero(mask_red)
    #Detect moving
    try:
    	diff = cv2.absdiff(frame1, frame2)
    except:
    	print("error")
    gray = cv2.cvtColor(diff, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (5,5), 0)
    _, thresh = cv2.threshold(blur, 20, 255, cv2.THRESH_BINARY)
    dilated = cv2.dilate(thresh, None, iterations=3)
    contours, _ = cv2.findContours(dilated, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    if not(coord is None):
        poly = cv2.polylines(frame1, [poly_ne] ,True, (0, 0, 255),3)
        cv2.putText(frame1, "Status: {}".format('Den_do'), (10, 20), cv2.FONT_HERSHEY_SIMPLEX,
                    1, (0, 0, 255), 3)
        for contour in contours:
            (x, y, w, h) = cv2.boundingRect(contour)
            if cv2.contourArea(contour) < 10000:
                continue
            centro = pega_centro(x, y, w, h)
            x1, y1, w1, h1 = x, y, w, h
            circle_o = cv2.circle(frame1, centro, 4, (0, 0, 255), -1)
            rectangel = cv2.rectangle(frame1, (x, y), (x + w, y + h), (0, 255, 0), 2)
            if inside_poly(centro, poly_ne):
                
                cv2.imshow("crop", frame2[y1: y1 + h1, x1: x1 + w1])
                
                path = "%s%s_%s\\" % (img_folder, datetime.today().strftime("%Y_%m_%d"),int(time.time()))
                
                if not os.path.exists(path):
                    os.makedirs(path)
                
                #cv2.imwrite(path + "overview.png", frame1)
                
                cv2.imwrite(path + "detailed.png", frame2[y1: y1 + h1, x1: x1 + w1])
                #detect_plate(path + "detailed.png")
                ImageNode.append(path+"detailed.png")
    else:
    	cv2.putText(frame1, "Status: {}".format('Den_xanh'), (10, 20), cv2.FONT_HERSHEY_SIMPLEX,
                    1, (0, 255, 0), 3)
    print(ImageNode)
    if IS_FREE and len(ImageNode) > 0:
        IS_FREE = False
        thread = threading.Thread(target=detect_plate, args=(ImageNode.pop(0),))
        thread.start()
    cv2.imshow("feed", frame1)
    #cv2.imwrite("image.png", frame1)
    frame1 = frame2
    _, frame2 = cap.read()

    if cv2.waitKey(33) & 0xFF == ord("q"):
        break

cv2.destroyAllWindows()
cap.release()
