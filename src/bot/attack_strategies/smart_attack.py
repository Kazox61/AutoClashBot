from core.android import Android
import time
from config.buttons import Buttons
from bot.utils.button_touch import ButtonTouch
import cv2
import numpy as np
import math
import nanoid
from pathlib import Path

start_center_x = 90
step = 66
row_y = 550


def find_intersection(line1, line2):
    x1, y1, x2, y2 = line1
    x3, y3, x4, y4 = line2

    # Calculate slopes (m) and y-intercepts (b) for each line
    m1 = (y2 - y1) / (x2 - x1) if x2 - \
        x1 != 0 else float('inf')  # Avoid division by zero
    b1 = y1 - m1 * x1 if m1 != float('inf') else None

    m2 = (y4 - y3) / (x4 - x3) if x4 - \
        x3 != 0 else float('inf')  # Avoid division by zero
    b2 = y3 - m2 * x3 if m2 != float('inf') else None

    # Check for parallel lines (same slope)
    if m1 == m2:
        return None  # Lines are parallel, no intersection

    # Calculate intersection point
    if m1 == float('inf'):
        x_intersection = x1
        y_intersection = m2 * x_intersection + b2
    elif m2 == float('inf'):
        x_intersection = x3
        y_intersection = m1 * x_intersection + b1
    else:
        x_intersection = (b2 - b1) / (m1 - m2)
        y_intersection = m1 * x_intersection + b1

    return x_intersection, y_intersection


def distance(x1, y1, x2, y2):
    return math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)


def point_on_line_segment(start, end, distance):
    x1, y1 = start
    x2, y2 = end

    length = math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)

    if length == 0:
        return None
    if length <= distance:
        return None
    x = x1 + (x2 - x1) * (distance / length)
    y = y1 + (y2 - y1) * (distance / length)

    return x, y


def distribute_points_on_lines(lines, total_points):
    total_length = sum(distance(x1, y1, x2, y2) for x1, y1, x2, y2 in lines)
    point_to_point_distance = total_length / total_points
    points = []
    length_remaining = point_to_point_distance
    for x1, y1, x2, y2 in lines:
        while True:
            point = point_on_line_segment((x1, y1), (x2, y2), length_remaining)
            if not point:
                length_remaining -= distance(x1, y1, x2, y2)
                break
            x1, y1 = point
            points.append(point)
            length_remaining = point_to_point_distance

    return points


class SmartAttack:
    def __init__(self, android: Android) -> None:
        self.android = android
        self.button_touch = ButtonTouch(self.android)

    def preprocess(self) -> np.ndarray:
        imgs = self.android.bluestacks.multi_screenshot(10)
        base = imgs[0]
        others = imgs[1:]

        final = None

        for i, other in enumerate(others):
            diff = cv2.absdiff(base, other)

            gray = cv2.cvtColor(diff, cv2.COLOR_BGR2GRAY)
            _, th = cv2.threshold(gray, 10, 255, cv2.THRESH_BINARY)

            if i > 0:
                final = cv2.bitwise_or(final, th)
            else:
                final = th

        hsv_image = cv2.cvtColor(base, cv2.COLOR_BGR2HSV)
        lower_bound = np.array([0, 128, 0])
        upper_bound = np.array([20, 255, 255])
        mask1 = cv2.inRange(hsv_image, lower_bound, upper_bound)

        lower_bound = np.array([170, 128, 0])
        upper_bound = np.array([179, 255, 255])
        mask2 = cv2.inRange(hsv_image, lower_bound, upper_bound)

        mask = cv2.bitwise_or(mask1, mask2)
        result = cv2.bitwise_and(base, base, mask=mask)
        gray = cv2.cvtColor(result, cv2.COLOR_BGR2GRAY)

        add = cv2.bitwise_and(result, result, mask=final)
        gray = cv2.cvtColor(add, cv2.COLOR_BGR2GRAY)
        kernel_size = 5
        blur = cv2.GaussianBlur(
            gray, (kernel_size, kernel_size), sigmaX=2, sigmaY=2)
        _, result = cv2.threshold(blur, 20, 255, cv2.THRESH_BINARY)
        return result, base

    def find_corners(self, img: np.ndarray) -> list:
        image_center_x, image_center_y = self.android.bluestacks.get_screen_size()

        lines_found = cv2.HoughLinesP(img, 1, np.pi / 180,
                                      threshold=40, minLineLength=10, maxLineGap=15)

        lines = []
        for line in lines_found:
            x1, y1, x2, y2 = line[0]
            x_intersection = x1 + (image_center_y - y1) * (x2 - x1) / (y2 - y1)
            if x2 == x1:
                continue
            if y2 == y1:
                continue
            x_length = x2 - x1
            y_length = y2 - y1
            slope = y_length / x_length
            if abs(slope) > 0.8 or abs(slope) < 0.7:
                continue
            lines.append([[x1, y1, x2, y2], x_intersection, slope])

        negative_slope_negative_x = [None, image_center_x, None]
        negative_slope_positive_x = [None, image_center_x, None]
        positive_slope_negative_x = [None, image_center_x, None]
        positive_slope_positive_x = [None, image_center_x, None]
        for line in lines:
            l, x_intersection, slope = line
            if slope < 0:
                if x_intersection < negative_slope_negative_x[1]:
                    negative_slope_negative_x = line
                if x_intersection > negative_slope_positive_x[1]:
                    negative_slope_positive_x = line
            else:
                if x_intersection < positive_slope_negative_x[1]:
                    positive_slope_negative_x = line
                if x_intersection > positive_slope_positive_x[1]:
                    positive_slope_positive_x = line

        top = find_intersection(
            negative_slope_negative_x[0], positive_slope_positive_x[0])
        bottom = find_intersection(
            negative_slope_positive_x[0], positive_slope_negative_x[0])
        left = find_intersection(
            negative_slope_negative_x[0], positive_slope_negative_x[0])
        right = find_intersection(
            negative_slope_positive_x[0], positive_slope_positive_x[0])

        return top, bottom, left, right

    def start(self):
        log_attack_path = Path(__file__).joinpath(
            "..", "..", "..", "..", "logs", "attack")

        img, src_img = self.preprocess()

        cv2.imwrite(log_attack_path.joinpath(
            nanoid.generate()+".png").as_posix(), img)

        top, bottom, left, right = self.find_corners(img)

        lines = [
            [int(top[0]), int(top[1]), int(left[0]), int(left[1])],
            [int(left[0]), int(left[1]), int(bottom[0]), int(bottom[1])],
            [int(bottom[0]), int(bottom[1]), int(right[0]), int(right[1])],
            [int(right[0]), int(right[1]), int(top[0]), int(top[1])]
        ]

        points1 = distribute_points_on_lines(lines, 40)
        points2 = distribute_points_on_lines(lines, 40)

        for line in lines:
            x1, y1, x2, y2 = line
            cv2.line(src_img, (x1, y1), (x2, y2), (255, 0, 0), 5)

        cv2.imwrite(log_attack_path.joinpath(
            nanoid.generate()+".png").as_posix(), src_img)

        self.select_troop(0)
        for point in points1:
            self.android.minitouch.touch(point[0], point[1], False)

        for point in points2:
            self.android.minitouch.touch(point[0], point[1], False)

        time.sleep(1)
        self.select_troop(2)
        time.sleep(0.2)
        self.android.minitouch.touch(top[0], top[1])
        time.sleep(0.2)
        self.select_troop(3)
        time.sleep(0.2)
        self.android.minitouch.touch(top[0], top[1])
        time.sleep(0.2)
        self.select_troop(4)
        time.sleep(0.2)
        self.android.minitouch.touch(top[0], top[1])
        time.sleep(0.2)
        self.select_troop(5)
        time.sleep(0.2)
        self.android.minitouch.touch(top[0], top[1])
        time.sleep(10)
        self.leave_attack()

    def select_troop(self, index):
        self.android.minitouch.touch(start_center_x + index * step, row_y)

    def leave_attack(self):
        self.button_touch.try_press(Buttons.Surrender)
        time.sleep(1)
        self.button_touch.try_press(Buttons.SurrenderOkay)
        time.sleep(2)
        self.button_touch.try_press(Buttons.ReturnHome)
        time.sleep(5)
