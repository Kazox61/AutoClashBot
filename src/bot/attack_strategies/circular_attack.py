from core.android import Android
import time
from config.buttons import Buttons
from bot.utils.button_touch import ButtonTouch

start_center_x = 90
step = 66
row_y = 550


class CircularAttack:
    def __init__(self, android: Android) -> None:
        self.android = android
        self.button_touch = ButtonTouch(self.android)

    def start(self):
        self.select_troop(0)
        max_x, max_y = self.android.bluestacks.get_screen_size()
        touch_cylce = [
            (max_x * 0.5, max_y * 0.05),
            (max_x * 0.25, max_y * 0.25),
            (max_x * 0.1, max_y * 0.5),
            (max_x * 0.25, max_y * 0.75),
            (max_x * 0.5, max_y * 0.9),
            (max_x * 0.75, max_y * 0.75),
            (max_x * 0.9, max_y * 0.5),
            (max_x * 0.75, max_y * 0.25),
        ]
        touches = []
        touches.extend(touch_cylce)
        touches.extend(touch_cylce)
        touches.extend(touch_cylce)
        self.android.minitouch.swipe_along(touches, 0.5, 5, 1)
        time.sleep(1)
        self.select_troop(2)
        self.android.minitouch.touch(max_x * 0.5, max_y * 0.05)
        time.sleep(0.5)
        self.select_troop(3)
        self.android.minitouch.touch(max_x * 0.5, max_y * 0.05)
        time.sleep(0.5)
        self.select_troop(4)
        self.android.minitouch.touch(max_x * 0.5, max_y * 0.05)
        time.sleep(0.5)
        self.select_troop(5)
        self.android.minitouch.touch(max_x * 0.5, max_y * 0.05)
        time.sleep(5)
        self.select_troop(2)
        self.select_troop(3)
        self.select_troop(4)
        self.select_troop(5)
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
