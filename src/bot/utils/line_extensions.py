import math

import numpy as np
import cv2
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
        slope_a = (ay2 - ay1) / (ax2 - ax1)
        for line_b in lines:
            bx1, by1, bx2, by2 = line_b
            slope_b = (by2 - by1) / (bx2 - bx1)
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
    lines = cv2.HoughLinesP(image, 1, np.pi / 180,
                            threshold=50, minLineLength=40, maxLineGap=10)

    processed_lines = []
    for line in lines:
        x1, y1, x2, y2 = line[0]
        x_length = x2 - x1
        y_length = y2 - y1
        slope = y_length / x_length
        if abs(slope) > 0.8 or abs(slope) < 0.7:
            continue
        processed_lines.append(line[0].tolist())

    processed_lines.sort(key=get_length, reverse=True)

    merged_lines = merge_lines(processed_lines)
    return sorted(merged_lines, key=get_length, reverse=True)


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
