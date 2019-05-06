import cv2
import numpy as np
from codes import calibrationDAO as calDAO
import time


def avg_circles(circles, b):
    avg_x = 0
    avg_y = 0
    avg_r = 0
    for i in range(b):
        # optional - average for multiple circles (can happen when a gauge is at a slight angle)
        avg_x = avg_x + circles[0][i][0]
        avg_y = avg_y + circles[0][i][1]
        avg_r = avg_r + circles[0][i][2]
    avg_x = int(avg_x/b)
    avg_y = int(avg_y/b)
    avg_r = int(avg_r/b)
    return avg_x, avg_y, avg_r


def dist_2_pts(x1, y1, x2, y2):
    return np.sqrt((x2 - x1)**2 + (y2 - y1)**2)


def detect_circle(frame):
    height, width = frame.shape[:2]
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)  # convert to gray
    circles = cv2.HoughCircles(gray, cv2.HOUGH_GRADIENT, 1, 50,
                               np.array([]), 100, 50, int(height * 0.2), int(height * 0.4))

    if circles is not None and len(circles.shape) == 3:
        a, b, c = circles.shape
        x, y, r = avg_circles(circles, b)

        cv2.circle(frame, (x, y), r, (0, 0, 255), 3, cv2.LINE_AA)
        cv2.circle(frame, (x, y), 2, (0, 255, 0), 3, cv2.LINE_AA)

        get_dial_angle(frame, x, y, r)


def get_dial_angle(frame, x, y, r):
    final_line_list = []

    diff1LowerBound = 0.0  # 0.15
    diff1UpperBound = 0.25  # 0.25

    diff2LowerBound = 0.6  # 0.5
    diff2UpperBound = 1.0  # 1.0

    gray2 = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    _,dst2 = cv2.threshold(gray2, 100, 255, cv2.THRESH_BINARY_INV)
    dst2 = cv2.GaussianBlur(dst2, (5, 5), 0)

    lines = cv2.HoughLinesP(image=dst2, rho=3, theta=np.pi / 180, threshold=100,
                            minLineLength=r*0.6, maxLineGap=0)

    if lines is not None:
        for i in range(0, len(lines)):
            for x1, y1, x2, y2 in lines[i]:
                diff1 = dist_2_pts(x, y, x1, y1)
                diff2 = dist_2_pts(x, y, x2, y2)

                if diff1 > diff2:
                    temp = diff1
                    diff1 = diff2
                    diff2 = temp

                if (((diff1<diff1UpperBound*r) and (diff1>diff1LowerBound*r) and (diff2<diff2UpperBound*r)) and (diff2>diff2LowerBound*r)):
                    final_line_list.append([x1, y1, x2, y2])

    if len(final_line_list) != 0:
        x1 = final_line_list[0][0]
        y1 = final_line_list[0][1]
        x2 = final_line_list[0][2]
        y2 = final_line_list[0][3]
        cv2.line(frame, (x1, y1), (x2, y2), (255, 0, 0), 2)

        cv2.imshow("lines", frame)

        get_current_reading(x, y, x1, y1, x2, y2, frame)


def get_current_reading(x, y, x1, y1, x2, y2, frame):
    dist_pt_0 = dist_2_pts(x, y, x1, y1)
    dist_pt_1 = dist_2_pts(x, y, x2, y2)

    if dist_pt_0 > dist_pt_1:
        x_angle = x1 - x
        y_angle = y - y1
    else:
        x_angle = x2 - x
        y_angle = y - y2

    res = np.arctan(np.divide(float(y_angle), float(x_angle)))
    res = np.rad2deg(res)
    if x_angle > 0:
        if y_angle > 0:  # in quadrant I
            final_angle = 270 - res
        else:  # in quadrant IV
            final_angle = 270 - res
    else:
        if y_angle > 0:  # in quadrant II
            final_angle = 90 - res
        else:  # in quadrant III
            final_angle = 90 - res

    cal_data = calDAO.retrieve_gauge_calibrations("gr004")

    if cal_data != -1:
        min_angle = cal_data[0]
        max_angle = cal_data[1]
        min_value = cal_data[2]
        max_value = cal_data[3]
        units = cal_data[4]

        old_min = float(min_angle)
        old_max = float(max_angle)

        new_min = float(min_value)
        new_max = float(max_value)

        old_value = final_angle

        old_range = (old_max - old_min)
        new_range = (new_max - new_min)
        new_value = (((old_value - old_min) * new_range) / old_range) + new_min

        cv2.putText(frame, '%s' % new_value, (100,100),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 69, 255), 1, cv2.LINE_AA)
    else:
        print("An error occurred\n")


def main():
    cap = cv2.VideoCapture(0)

    while True:
        _, frame = cap.read()
        detect_circle(frame)

        cv2.imshow("Frame", frame)

        key = cv2.waitKey(1)
        if key == 27:
            break

        time.sleep(0.1)

    cap.release()
    cv2.destroyAllWindows()
