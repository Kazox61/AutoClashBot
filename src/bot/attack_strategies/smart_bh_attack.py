from core.android import Android
import time
from bot.base.builder_base import BuilderBase
import math
import cv2

start_center_x = 82
step = 66
row_y = 550


def points_on_lines(red_lines: list, amount_on_line: int) -> list[tuple[int, int]]:
    points = []
    for line in red_lines:
        x1, y1, x2, y2 = line
        angle = math.atan2(y2 - y1, x2 - x1)
        x_length = x2 - x1
        y_length = y2 - y1
        length = math.sqrt(y_length * y_length + x_length * x_length)
        step = length / amount_on_line
        for i in range(amount_on_line):
            x = x1 + i * step * math.cos(angle)
            y = y1 + i * step * math.sin(angle)
            points.append((x, y))
    return points


class SmartBhAttack:
    def __init__(self, android: Android) -> None:
        self.android = android

    def start(self):
        img = self.android.get_screenshot()
        builder_base = BuilderBase()
        builder_base.load(img)

        red_lines = builder_base.red_lines()
        points = points_on_lines(red_lines, 2)
        print(points)
        for i, coord in enumerate(points):
            cv2.circle(img, (int(coord[0]), int(coord[1])), 3, (255, 0, 0), -1)
            self.select_troop(i)
            time.sleep(0.5)
            self.android.minitouch.touch(coord[0], coord[1], False)
            time.sleep(0.5)
        cv2.imwrite("testimg.png", img)

        for i in range(8):
            print("Activate Troop: ", i)
            self.select_troop(i)
            time.sleep(0.5)

        self.android.stop_app()
        self.android.start_app()

    def select_troop(self, index):
        self.android.minitouch.touch(start_center_x + index * step, row_y)
