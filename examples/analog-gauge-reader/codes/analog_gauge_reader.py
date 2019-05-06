import cv2
import numpy as np


def dist_2_pts(x1, y1, x2, y2):
    return np.sqrt((x2 - x1)**2 + (y2 - y1)**2)


def draw_intervals(x, y, r, separation, img, job):
    interval = int(360 / separation)

    if job is 'major':
        ratio = float(0.8)
    else:
        ratio = float(0.9)

    text_offset_x = 10
    text_offset_y = 5

    p1 = np.zeros((interval, 2))
    p2 = np.zeros((interval, 2))
    p_text = np.zeros((interval, 2))

    for i in range(0, interval):
        for j in range(0, 2):
            if j % 2 == 0:
                p1[i][j] = x + ratio * r * np.cos(separation * i * 3.14 / 180)
            else:
                p1[i][j] = y + ratio * r * np.sin(separation * i * 3.14 / 180)

    for i in range(0, interval):
        for j in range(0, 2):
            if j % 2 == 0:
                p2[i][j] = x + r * np.cos(separation * i * 3.14 / 180)
                if job == 'major':
                    p_text[i][j] = x - text_offset_x + 1.1 * r * np.cos(separation * (
                                i + 9) * 3.14 / 180)
            else:
                p2[i][j] = y + r * np.sin(separation * i * 3.14 / 180)
                if job == 'major':
                    p_text[i][j] = y + text_offset_y + 1.1 * r * np.sin(separation * (
                                i + 9) * 3.14 / 180)

    # add the lines and labels to the image
    for i in range(0, interval):
        cv2.line(img, (int(p1[i][0]), int(p1[i][1])), (int(p2[i][0]), int(p2[i][1])), (0, 255, 0), 2)
        if job == 'major':
            cv2.putText(img, '%s' % (int(i * separation)), (int(p_text[i][0]), int(p_text[i][1])),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 69, 255), 1, cv2.LINE_AA)

    return img


def calibrate_gauge(gauge_number, file_type):
    img = cv2.imread('../images/gauge-%s.%s' % (gauge_number, file_type))
    height, width = img.shape[:2]
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # for testing, output gray image
    cv2.imwrite('../bw/gauge-%s-bw.%s' % (gauge_number, file_type), gray)

    # detect circles
    circles = cv2.HoughCircles(gray, cv2.HOUGH_GRADIENT, 1, 50,
                               np.array([]), 100, 50, int(height * 0.2), int(height * 0.4))

    circles = np.uint16(np.around(circles))
    for i in circles[0, :]:
        # draw the outer circle
        cv2.circle(img, (i[0], i[1]), i[2], (0, 255, 0), 2)
        # draw the center of the circle
        cv2.circle(img, (i[0], i[1]), 2, (0, 0, 255), 3)

    # for testing, output circles on image
    cv2.imwrite('../circles/gauge-%s-circles.%s' % (gauge_number, file_type), img)

    for c in circles[0, :]:
        x = c[0]
        y = c[1]
        r = c[2]
        separation_major = 10.0
        separation_minor = 5.0

        img = draw_intervals(x, y, r, separation_major, img, 'major')
        img = draw_intervals(x, y, r, separation_minor, img, 'minor')

    # store the image as a file
    cv2.imwrite('../calibration/gauge-%s-calibration.%s' % (gauge_number, file_type), img)

    print('gauge number: %s' % gauge_number)

    return circles


def get_current_value(img, min_angle, max_angle, min_value, max_value, x, y, r, gauge_number, file_type):

    print(x, y, r)
    gray2 = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    dst2 = cv2.adaptiveThreshold(gray2, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 11, 2)

    # for testing, show image after thresholding
    cv2.imwrite('../tempdst/gauge-%s-tempdst2.%s' % (gauge_number, file_type), dst2)

    # rho is set to 3 to detect more lines, easier to get more then filter them out later
    lines = cv2.HoughLinesP(image=dst2, rho=3, theta=np.pi / 180, threshold=100,
                            minLineLength=10, maxLineGap=0)

    # for testing purposes, show all found lines
    # for i in range(0, len(lines)):
    #     for x1, y1, x2, y2 in lines[i]:
    #         cv2.line(img, (x1, y1), (x2, y2), (0, 255, 0), 2)
    #         cv2.imwrite('gauge-%s-ALL-lines-test.%s' % (gauge_number, file_type), img)

    # remove all lines outside a given radius
    final_line_list = []

    # diff1LowerBound and diff1UpperBound determine how close the line should be from the center
    diff1LowerBound = 0.0
    diff1UpperBound = 0.25

    # diff2LowerBound and diff2UpperBound determine how far the line should be from the center
    diff2LowerBound = 0.4
    diff2UpperBound = 0.8

    for i in range(0, len(lines)):
        for x1, y1, x2, y2 in lines[i]:
            diff1 = dist_2_pts(x, y, x1, y1)
            diff2 = dist_2_pts(x, y, x2, y2)

            # set diff1 to be the smaller (closest to the center) of the two), makes the math easier
            if diff1 > diff2:
                temp = diff1
                diff1 = diff2
                diff2 = temp

            # check if line is within an acceptable range
            if diff1LowerBound * r <= diff1 <= diff1UpperBound * r:
                if diff2LowerBound * r <= diff2 <= diff2UpperBound * r:
                    final_line_list.append([x1, y1, x2, y2])

    # testing only, show all lines after filtering
    longest_line = -1;
    line_to_use = -1;
    for i in range(0, len(final_line_list)):
        img2 = img
        x1 = final_line_list[i][0]
        y1 = final_line_list[i][1]
        x2 = final_line_list[i][2]
        y2 = final_line_list[i][3]
        cv2.line(img2, (x1, y1), (x2, y2), (0, 255, 0), 2)
        cv2.imwrite('../lines/gauge-%s-lines-test-2.%s' % (gauge_number, file_type), img2)

        if dist_2_pts(x1, y1, x2, y2) > longest_line:
            longest_line = dist_2_pts(x1, y1, x2, y2)
            line_to_use = i

    if line_to_use >= 0:
        x1 = final_line_list[0][0]
        y1 = final_line_list[0][1]
        x2 = final_line_list[0][2]
        y2 = final_line_list[0][3]
        cv2.line(img, (x1, y1), (x2, y2), (255, 0, 0), 2)

    # for testing purposes, show the line overlaid on the original image
    cv2.imwrite('../lines/gauge-%s-lines-2.%s' % (gauge_number, file_type), img)

    # find the farthest point from the center to be what is used to determine the angle
    dist_pt_0 = dist_2_pts(x, y, x1, y1)
    dist_pt_1 = dist_2_pts(x, y, x2, y2)
    if dist_pt_0 > dist_pt_1:
        x_angle = x1 - x
        y_angle = y - y1
    else:
        x_angle = x2 - x
        y_angle = y - y2

    # take the arc tan of y/x to find the angle
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

    print("x: %s, y: %s" % (x_angle, y_angle))

    old_min = float(min_angle)
    old_max = float(max_angle)

    new_min = float(min_value)
    new_max = float(max_value)

    old_value = final_angle

    old_range = (old_max - old_min)
    new_range = (new_max - new_min)
    new_value = (((old_value - old_min) * new_range) / old_range) + new_min

    return new_value
