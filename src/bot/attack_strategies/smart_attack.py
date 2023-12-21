from core.android import Android
import time
from config.buttons import Buttons
from bot.utils.button_touch import ButtonTouch
from bot.utils.home_base import HomeBase
import math


start_center_x = 90
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


class SmartAttack:
    def __init__(self, android: Android) -> None:
        self.android = android
        self.button_touch = ButtonTouch(self.android)

    def start(self):
        img = self.android.get_screenshot()
        home_base = HomeBase()
        home_base.load(img)

        self.select_troop(0)
        top = home_base.top_building_position()
        red_lines = home_base.red_lines()
        points = points_on_lines(red_lines, 8)
        for coord in points:
            self.android.minitouch.touch(coord[0], coord[1], False)
            time.sleep(0.1)

        for i in range(2, 6):
            self.select_troop(i)
            time.sleep(0.5)
            self.android.minitouch.touch(top[0], top[1])
            time.sleep(0.5)

        self.select_troop(0)
        time.sleep(0.5)
        for coord in points:
            self.android.minitouch.touch(coord[0], coord[1], False)
            time.sleep(0.1)

        for i in range(2, 6):
            self.select_troop(i)
            time.sleep(0.5)

        self.select_troop(0)
        time.sleep(0.5)
        for coord in points:
            self.android.minitouch.touch(coord[0], coord[1], False)
            time.sleep(0.1)

        time.sleep(20)
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
