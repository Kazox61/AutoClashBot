import cv2
import numpy as np
from pathlib import Path
import math


def get_length(line):
    x1, y1, x2, y2 = line
    x_length = x2 - x1
    y_length = y2 - y1
    return math.sqrt(y_length * y_length + x_length * x_length)


def get_distance_point_to_line(point, line):
    x, y = point
    x1, y1, x2, y2 = line

    line_length = math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)

    if line_length == 0:
        return math.sqrt((x - x1) ** 2 + (y - y1) ** 2)

    t = max(0, min(1, ((x - x1) * (x2 - x1) + (y - y1)
            * (y2 - y1)) / (line_length ** 2)))

    projected_x = x1 + t * (x2 - x1)
    projected_y = y1 + t * (y2 - y1)

    distance = math.sqrt((x - projected_x) ** 2 + (y - projected_y) ** 2)
    return distance


def merge_lines(lines):
    for line_a in lines:
        ax1, ay1, ax2, ay2 = line_a
        try:
            slope_a = (ay2 - ay1) / (ax2 - ax1)
        except ZeroDivisionError:
            slope_a = 1000
        for line_b in lines:
            bx1, by1, bx2, by2 = line_b
            try:
                slope_b = (by2 - by1) / (bx2 - bx1)
            except ZeroDivisionError:
                slope_b = 1000
            if line_a == line_b:
                continue
            has_same_slope = abs(slope_b - slope_a) < 0.1
            if not has_same_slope:
                continue

            distance_bottom = get_distance_point_to_line((bx1, by1), line_a)
            distance_top = get_distance_point_to_line((bx2, by2), line_a)
            if abs(distance_bottom) > 10 and abs(distance_top) > 10:
                continue
            if slope_a > 0:
                if ay1 < by1:
                    x1 = ax1
                    y1 = ay1
                else:
                    x1 = bx1
                    y1 = by1

                if ay2 > by2:
                    x2 = ax2
                    y2 = ay2
                else:
                    x2 = bx2
                    y2 = by2
            else:
                if ay1 > by1:
                    x1 = ax1
                    y1 = ay1
                else:
                    x1 = bx1
                    y1 = by1

                if ay2 < by2:
                    x2 = ax2
                    y2 = ay2
                else:
                    x2 = bx2
                    y2 = by2

            lines.remove(line_a)
            lines.remove(line_b)
            lines.insert(0, [x1, y1, x2, y2])
            merge_lines(lines)
            return lines
    return lines


def get_red_lines(image):
    lines = cv2.HoughLinesP(result, 1, np.pi / 180,
                            threshold=40, minLineLength=10, maxLineGap=15)
    print(len(lines))
    # remove lines that don't have a slope of 0.75 or -0.75
    processed_lines = []
    for line in lines:
        x1, y1, x2, y2 = line[0]
        x_length = x2 - x1
        y_length = y2 - y1
        if x_length == 0:
            continue
        slope = y_length / x_length
        if abs(slope) > 0.8 or abs(slope) < 0.7:
            continue
        processed_lines.append(line[0].tolist())
    return processed_lines
    print(len(processed_lines))
    processed_lines.sort(key=get_length, reverse=True)

    merged_lines = merge_lines(processed_lines)
    print(len(merged_lines))
    return sorted(merged_lines, key=get_length, reverse=True)


def get_outside_lines(pre_lines):
    constant_y = 300
    constant_x = 400
    lines = []
    for line in pre_lines:
        x1, y1, x2, y2 = line
        x_intersection = x1 + (constant_y - y1) * (x2 - x1) / (y2 - y1)
        x_length = x2 - x1
        y_length = y2 - y1
        slope = y_length / x_length
        lines.append([line, x_intersection, slope])

    negative_slope_negative_x = [None, constant_x, None]
    negative_slope_positive_x = [None, constant_x, None]
    positive_slope_negative_x = [None, constant_x, None]
    positive_slope_positive_x = [None, constant_x, None]
    for line in lines:
        l, x_intersection, slope = line
        if slope < 0:
            if x_intersection < negative_slope_negative_x[1]:
                negative_slope_negative_x = line
            if x_intersection > negative_slope_positive_x[1]:
                negative_slope_positive_x = line
        else:
            print("slope positive", line)
            if x_intersection < positive_slope_negative_x[1]:
                print("FOUND")
                positive_slope_negative_x = line
            if x_intersection > positive_slope_positive_x[1]:
                positive_slope_positive_x = line
    return [negative_slope_negative_x[0], negative_slope_positive_x[0], positive_slope_negative_x[0], positive_slope_positive_x[0]]


fpath = Path.cwd().joinpath("diff")
ims = list(fpath.glob("*.png"))

imgs = [cv2.imread(i.as_posix()) for i in ims]
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

lines = get_outside_lines(get_red_lines(result))
print(len(lines))
for line in lines:
    x1, y1, x2, y2 = line
    cv2.line(base, (x1, y1), (x2, y2), (255, 0, 0), 5)

    cv2.imshow('Pixel Differences', base)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
