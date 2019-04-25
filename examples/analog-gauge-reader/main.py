from cv2 import *
from datetime import datetime
import analog_gauge_reader as agr
import calibrationDAO as calDAO
import numpy as np


def take_picture():
    # initialize the camera
    cam = VideoCapture(0)   # 0 -> index of camera

    print("Press c to take picture...")

    while True:
        s, img = cam.read()

        if s:    # frame captured without any errors
            namedWindow("Gauge")
            imshow("Gauge", img)

        if waitKey(1) & 0xFF == ord('c'):
            cam.release()
            destroyWindow("Gauge")
            time = int(datetime.now().timestamp()*1000)
            filename = "images/gauge-" + str(time) + ".jpg"
            imwrite(filename, img)  # save image
            break

    return time


def calibrate_gauge_cam():
    gauge_number = take_picture()
    x, y, r = agr.calibrate_gauge(gauge_number, "jpg")

    if 'y' == input("Use this picture? (y/n): "):
        calibrate_gauge(x, y, r)
    else:
        calibrate_gauge_cam()


def calibrate_gauge_picture():
    gauge_number = input("Enter gauge number: ")
    x, y, r = agr.calibrate_gauge(gauge_number, "jpg")
    calibrate_gauge(x, y, r)


def calibrate_gauge(x, y, r):
    min_angle, max_angle, min_value, max_value, unit = get_calibration_values()
    name = input("Enter name for this gauge: ")
    calDAO.insert_new_gauge(name, min_angle, max_angle, min_value, max_value, unit)


def read_gauge_cam():
    gauge_number = take_picture()
    read_gauge(gauge_number)


def read_gauge_picture():
    gauge_number = input("Enter which gauge image you want to use: ")
    read_gauge(gauge_number)


def read_gauge(gauge_number):
    gauge_id = input("Enter which gauge calibration you want to use: ")
    cal_data = calDAO.retrieve_gauge_calibrations(gauge_id)
    x, y, r = agr.calibrate_gauge(gauge_number, "jpg")

    if cal_data != -1:
        min_angle = cal_data[0]
        max_angle = cal_data[1]
        min_value = cal_data[2]
        max_value = cal_data[3]
        units = cal_data[4]

        img = cv2.imread('images/gauge-%s.%s' % (gauge_number, "jpg"))
        val = agr.get_current_value(img, min_angle, max_angle, min_value, max_value, x, y, r, gauge_number, "jpg")
        print("Current reading: %s %s\n" % (val, units))
    else:
        print("An error occurred\n")


def get_calibration_values():
    # get user input on min, max, values, and units
    min_angle = input('Min angle (lowest possible angle of dial) - in degrees: ')  # the lowest possible angle
    max_angle = input('Max angle (highest possible angle) - in degrees: ')  # highest possible angle
    min_value = input('Min value: ')  # zero
    max_value = input('Max value: ')  # maximum reading of the gauge
    unit = input('Enter unit: ')

    return min_angle, max_angle, min_value, max_value, unit


def replace_colours():
    im = cv2.imread('images/gauge-13.jpg')
    # im[np.where((im != [0, 0, 0] and im != [255, 255, 255]).all(axis=2))] = [255, 255, 255]
    im[np.where(((im > [55, 55, 55]) & (im < [200, 200, 200])).all(axis=2))] = [255, 255, 255]
    cv2.imwrite('output.png', im)


if __name__ == "__main__":
    # print("At any point, enter q to quit...")
    # while True:
    #     user_choice = input("\n1. Calibrate Gauge (WebCam) \n2. Calibrate Gauge (Picture) \n3. Read Gauge Value "
    #                         "(WebCam) \n4. Read Gauge Value (Picture)\n\nSelect an option:")
    #     if user_choice == '1':
    #         calibrate_gauge_cam()
    #     elif user_choice == '2':
    #         calibrate_gauge_picture()
    #     elif user_choice == '3':
    #         read_gauge_cam()
    #     elif user_choice == '4':
    #         read_gauge_picture()
    #     elif user_choice == 'q':
    #         break

    replace_colours()
