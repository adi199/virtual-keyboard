import cv2
#import pickle
import numpy as np
import pyautogui as gui
import requests as res
#import urllib.request as urllib

url = "http://192.168.43.1:8080/video"

cam = cv2.VideoCapture('test.mp4')
if (cam.isOpened() == False):
    print("File cannot be opened");

#hsv_lower = np.array([t[0], t[1], t[2]])
#hsv_upper = np.array([t[3], t[4], t[5]])
width = cam.get(cv2.CAP_PROP_FRAME_WIDTH)
height = cam.get(cv2.CAP_PROP_FRAME_HEIGHT)
max_keys_in_a_row = 10
key_width = int(width/max_keys_in_a_row)


def get_keys():

    row1_key_width = key_width * 10            # width of first row of keys
    row2_key_width = key_width * 9            # width of second row
    row3_key_width = key_width * 7            # width of third row
    row4_key_width = key_width * 5            # width of spacebar
    row_keys = []

    # for the first row
    x1, y1 = 0, int((height - key_width * 4) / 2)
    x2, y2 = key_width + x1, key_width + y1
    c1, c2 = x1, y1
    c = 0
    keys = "qwertyuiop"
    for i in range(len(keys)):
        row_keys.append([keys[c], (x1, y1), (x2, y2), (int((x2+x1)/2) - 5, int((y2+y1)/2) + 10)])
        x1 += key_width
        x2 += key_width
        c += 1
    x1, y1 = c1, c2

    # for second row
    x1, y1 = int((row1_key_width - row2_key_width) / 2) + x1, y1 + key_width
    x2, y2 = key_width + x1, key_width + y1
    c1, c2 = x1, y1
    c = 0
    keys = "asdfghjkl"
    for i in range(len(keys)):
        row_keys.append([keys[c], (x1, y1), (x2, y2), (int((x2+x1)/2) - 5, int((y2+y1)/2) + 10)])
        x1 += key_width
        x2 += key_width
        c += 1
    x1, y1 = c1, c2

    # for third row
    x1, y1 = int((row2_key_width - row3_key_width) / 2) + x1, y1 + key_width
    x2, y2 = key_width + x1, key_width + y1
    c1, c2 = x1, y1
    c = 0
    keys = "zxcvbnm"
    for i in range(len(keys)):
        row_keys.append([keys[c], (x1, y1), (x2, y2), (int((x2+x1)/2) - 5, int((y2+y1)/2) + 10)])
        x1 += key_width
        x2 += key_width
        c += 1
    x1, y1 = c1, c2

    x1, y1 = int((row3_key_width - row4_key_width) / 2) + x1, y1 + key_width
    x2, y2 = 5 * key_width + x1, key_width + y1
    c1, c2 = x1, y1
    c = 0
    keys = " "
    for i in range(len(keys)):
        row_keys.append([keys[c], (x1, y1), (x2, y2), (int((x2+x1)/2) - 5, int((y2+y1)/2) + 10)])
        x1 += key_width
        x2 += key_width
        c += 1
    x1, y1 = c1, c2

    return row_keys


def do_keypress(img, center, row_keys_points):
    for row in row_keys_points:
        arr1 = list(np.int0(np.array(center) >= np.array(row[1])))
        arr2 = list(np.int0(np.array(center) <= np.array(row[2])))
        if arr1 == [1, 1] and arr2 == [1, 1]:
            gui.press(row[0])
            cv2.fillConvexPoly(img, np.array([np.array(row[1]), \
                                                np.array([row[1][0], row[2][1]]), \
                                                np.array(row[2]), \
                                                np.array([row[2][0], row[1][1]])]), \
                                                (255, 0, 0))
    return img


def main():
    row_keys_points = get_keys()
    new_area, old_area = 0, 0
    c, c2 = 0, 0

    flag_keypress = False
    while True:
        ret,img = cam.read()
        if ret!=True:
            break
        #img_res = res.get(url)
        #img_arr = np.array(bytearray(img_res.content),dtype = np.uint8)
        #img = cv2.imdecode(img_arr,5)
        frame = img;
        img = cv2.flip(img, 1)
        imgHSV = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        mask = cv2.inRange(imgHSV,(0, 30, 60, 0),(20, 150, 255, 0))#(30, 110, 40, 0),(85, 255, 255, 0))
        blur = cv2.medianBlur(mask, 15)
        blur = cv2.GaussianBlur(blur , (5,5), 0)
        thresh = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY+cv2.THRESH_OTSU)[1]
        contours = cv2.findContours(thresh.copy(), cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)[1]

        if len(contours) > 0:
            cnt = max(contours, key = cv2.contourArea)

            if cv2.contourArea(cnt) > 350:

                rect = cv2.minAreaRect(cnt)
                center = list(rect[0])
                box = cv2.boxPoints(rect)
                box = np.int0(box)
                cv2.circle(img, tuple(np.int0(center)), 2, (0, 255, 0), 2)
                cv2.drawContours(img,[box],0,(0,0,255),2)

                new_area = cv2.contourArea(cnt)
                new_center = np.int0(center)
                if c == 0:
                    old_area = new_area
                c += 1
                diff_area = 0
                if c > 3:
                    diff_area = new_area - old_area
                    c = 0
                if c2 == 0:
                    old_center = new_center
                c2 += 1
                diff_center = np.array([0, 0])
                if c2 > 5:
                    diff_center = new_center - old_center
                    c2 = 0

                # setting some thresholds
                center_threshold = 10
                area_threshold = 200
                if abs(diff_center[0]) < center_threshold or abs(diff_center[1]) < center_threshold:
                    print(diff_area)
                    if diff_area > area_threshold and flag_keypress == False:
                        img = do_keypress(img, new_center, row_keys_points)
                        flag_keypress = True
                    elif diff_area < -(area_threshold) and flag_keypress == True:
                        flag_keypress = False
            else:
                flag_keypress = False
        else:
            flag_keypress = False

        for key in row_keys_points:
            cv2.putText(img, key[0], key[3], cv2.FONT_HERSHEY_DUPLEX, 1, (0, 255, 0))
            cv2.rectangle(img, key[1], key[2], (0, 255, 0), thickness = 2)

        '''hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        lower_red = np.array([30,150,50])
        upper_red = np.array([255,255,180])
        mask = cv2.inRange(hsv, lower_red, upper_red)
        res = cv2.bitwise_and(frame,frame, mask= mask)
        cv2.imshow('Original',frame)
        edges = cv2.Canny(frame,100,200)
        cv2.imshow('Edges',edges)'''

        cv2.imshow("img", img)
        #cv2.imshow("thresholds",thresh)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cam.release()
    cv2.destroyAllWindows()

main()
