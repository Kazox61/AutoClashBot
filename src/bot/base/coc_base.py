from cv.yolo_detector import YoloDetector
import numpy as np


def intersection(line1, line2):
    x1, y1, x2, y2 = line1
    x3, y3, x4, y4 = line2

    m1 = (y2 - y1) / (x2 - x1) if x2 - x1 != 0 else float('inf')
    b1 = y1 - m1 * x1 if m1 != float('inf') else None

    m2 = (y4 - y3) / (x4 - x3) if x4 - x3 != 0 else float('inf')
    b2 = y3 - m2 * x3 if m2 != float('inf') else None

    if m1 == m2:
        return None

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


class CoCBase:
    building_detector: YoloDetector

    def __init__(self) -> None:
        pass

    def load(self, image: np.ndarray):
        self.image = image
        self.buildings = self.building_detector.predict(image)

    def outside_buildings(self):
        y, _, _ = self.image.shape
        x_min_pos = None
        x_max_pos = None
        x_min_neg = None
        x_max_neg = None
        slope = 0.75
        for builing in self.buildings:
            intercept_pos = builing.xywh[1] - slope * builing.xywh[0]
            x_pos = (y * 0.5 - intercept_pos) / slope
            intercept_neg = builing.xywh[1] + slope * builing.xywh[0]
            x_neg = (y * 0.5 - intercept_neg) / slope
            if x_min_pos is None:
                x_min_pos = (builing, x_pos)
            else:
                if x_pos < x_min_pos[1]:
                    x_min_pos = (builing, x_pos)
            if x_max_pos is None:
                x_max_pos = (builing, x_pos)
            else:
                if x_pos > x_max_pos[1]:
                    x_max_pos = (builing, x_pos)
            if x_min_neg is None:
                x_min_neg = (builing, x_neg)
            else:
                if x_neg < x_min_neg[1]:
                    x_min_neg = (builing, x_neg)
            if x_max_neg is None:
                x_max_neg = (builing, x_neg)
            else:
                if x_neg > x_max_neg[1]:
                    x_max_neg = (builing, x_neg)
        bottom_left_building = x_min_pos[0]
        top_right_building = x_max_pos[0]
        bottom_right_building = x_min_neg[0]
        top_left_building = x_max_neg[0]
        return [top_left_building, top_right_building, bottom_left_building, bottom_right_building]

    def top_building_position(self) -> tuple[int, int]:
        top_left_building, top_right_building, _, _ = self.outside_buildings()
        top_left = (top_left_building.xyxy[0], top_left_building.xyxy[1])
        top_right = (top_right_building.xyxy[2], top_right_building.xyxy[1])
        top = intersection([top_left[0], top_left[1], top_left[0]-4, top_left[1]+3],
                           [top_right[0], top_right[1], top_right[0]+4, top_right[1]+3])
        return top

    def red_lines(self):
        top_left_building, top_right_building, bottom_left_building, bottom_right_building = self.outside_buildings()
        top_left = (top_left_building.xyxy[0], top_left_building.xyxy[1])
        top_right = (top_right_building.xyxy[2], top_right_building.xyxy[1])
        bottom_left = (bottom_left_building.xyxy[0]-bottom_left_building.xywh[2]*0.2,
                       bottom_left_building.xyxy[3]+bottom_left_building.xywh[3]*0.2)
        bottom_right = (bottom_right_building.xyxy[2]+bottom_right_building.xywh[2]*0.2,
                        bottom_right_building.xyxy[3]+bottom_right_building.xywh[3]*0.2)
        top = intersection([top_left[0], top_left[1], top_left[0]-4, top_left[1]+3],
                           [top_right[0], top_right[1], top_right[0]+4, top_right[1]+3])
        left = intersection([top_left[0], top_left[1], top_left[0]-4, top_left[1]+3],
                            [bottom_left[0], bottom_left[1], bottom_left[0]+4, bottom_left[1]+3])
        right = intersection([top_right[0], top_right[1], top_right[0]+4, top_right[1]+3],
                             [bottom_right[0], bottom_right[1], bottom_right[0]-4, bottom_right[1]+3])
        bottom = intersection([bottom_left[0], bottom_left[1], bottom_left[0]+4, bottom_left[1]+3],
                              [bottom_right[0], bottom_right[1], bottom_right[0]-4, bottom_right[1]+3])
        return [
            (int(top[0]), int(top[1]), int(left[0]), int(left[1])),
            (int(top[0]), int(top[1]), int(right[0]), int(right[1])),
            (int(left[0]), int(left[1]), int(bottom[0]), int(bottom[1])),
            (int(right[0]), int(right[1]), int(bottom[0]), int(bottom[1]))
        ]

    def is_inactive(self) -> bool:
        pass

    def get_th_level(self) -> int:
        pass
