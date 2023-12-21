from core.android import Android
from cv.extensions import *
from bot.utils.line_extensions import get_red_lines
import time

start_center_x = 90
step = 66
row_y = 550


class BuilderBaseAttack:
    def __init__(self, android: Android) -> None:
        self.android = android

    def start(self):
        self.zoom_out()
        img = self.android.get_screenshot()
        img = filter_hue(img)

        cv2.imshow("Showcase", img)
        cv2.waitKey()
        cv2.destroyAllWindows()

        img = gray(img)
        img = blur(img)
        img = edges(img)
        img = dilate(img)
        img = erode(img)
        img = edges(img)

        slots = 7
        red_lines = get_red_lines(img)
        points = distribute_points_on_lines(red_lines, slots+1)

        self.select_troop(0)
        time.sleep(0.5)
        self.android.minitouch.touch(points[0][0], points[0][1])
        time.sleep(0.5)
        self.select_troop(1)
        time.sleep(0.5)
        for point in points[1:]:
            self.android.minitouch.touch(point[0], point[1])
            time.sleep(0.5)
        for i in range(slots):
            self.select_troop(i)
            time.sleep(0.5)

        time.sleep(3)
        self.android.stop_app()
        time.sleep(1)
        self.android.start_app()
        time.sleep(10)

    def zoom_out(self) -> None:
        self.android.zoom_out()
        time.sleep(0.5)
        max_x, max_y = self.android.bluestacks.get_screen_size()
        self.android.minitouch.swipe_along([(int(max_x * 0.4), int(max_y * 0.6)),
                                            (int(max_x * 0.9), int(max_y * 0.1))], 2, 10)
        time.sleep(0.5)

    def select_troop(self, index):
        self.android.minitouch.touch(start_center_x + index * step, row_y)
