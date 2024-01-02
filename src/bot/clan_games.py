from cv.extensions import template_matching
from config.constants import TEMPLATE_DIR, ASSETS_DIR
import cv2
from core.android import Android
import time
from cv.yolo_detector import YoloDetector


clangames_template = cv2.imread(
    TEMPLATE_DIR.joinpath("clangames", "clangames.png").as_posix())
activate_tasks_templates = [cv2.imread(template_path) for template_path in list(TEMPLATE_DIR.joinpath(
    "clangames", "hv", "activate").iterdir())]
button_start_clangames = cv2.imread(
    TEMPLATE_DIR.joinpath("clangames", "button_start.png").as_posix())
icon_out_of_time = cv2.imread(TEMPLATE_DIR.joinpath(
    "clangames", "outoftime.png").as_posix())
button_trash = cv2.imread(
    TEMPLATE_DIR.joinpath("clangames", "button_trash.png").as_posix())
button_close = cv2.imread(
    TEMPLATE_DIR.joinpath("clangames", "button_close.png").as_posix())
icon_medal1 = cv2.imread(
    TEMPLATE_DIR.joinpath("clangames", "medalgrey1.png").as_posix())
icon_medal2 = cv2.imread(
    TEMPLATE_DIR.joinpath("clangames", "medalgrey2.png").as_posix())


class ClanGames:
    def __init__(self, android: Android) -> None:
        self.android = android
        self.clangames_detector = YoloDetector(ASSETS_DIR.joinpath(
            "or_models", "clangames_detector_model.pt").as_posix(), 0.8)

    def play_clan_games(self):
        img = self.android.get_screenshot()
        detections = self.clangames_detector.predict(img)
        if len(detections) < 1:
            return

        clangames_position = detections[0].xywh

        self.android.minitouch.touch(
            clangames_position[0], clangames_position[1])

        time.sleep(6)
        self.try_remove_out_of_time_challenge()

        is_activated = self.is_challenge_activated()
        print("Is activated", is_activated)
        if is_activated:
            self.close_clangames()
            return

        self.try_activate_challenge()
        self.close_clangames()

    def try_remove_out_of_time_challenge(self) -> bool:
        for _ in range(3):
            img = self.android.get_screenshot()
            result = template_matching(img, icon_out_of_time, 0.5)
            if result is None:
                continue
            self.android.minitouch.touch(result.centerx, result.centery)

            time.sleep(1)

            img = self.android.get_screenshot()
            result = template_matching(img, button_trash)

            if result is None:
                continue

            self.android.minitouch.touch(result.centerx, result.centery)
            time.sleep(3)
            return True

        return False

    def try_activate_challenge(self) -> bool:
        img = self.android.get_screenshot()
        for template in activate_tasks_templates:
            result = template_matching(img, template, 0.8)

            if result is None:
                continue

            self.android.minitouch.touch(result.centerx, result.centery)

            time.sleep(0.5)

            img = self.android.get_screenshot()
            result = template_matching(img, button_start_clangames)

            if result is None:
                print("Can't find button for starting clangames challenge")
                continue

            self.android.minitouch.touch(result.centerx, result.centery)
            return True
        print("Can't find any ClanGames challenge to activate")
        return False

    def is_challenge_activated(self) -> bool:
        img = self.android.get_screenshot()
        return template_matching(img, icon_medal1, 0.95) is not None

    def close_clangames(self) -> None:
        self.android.minitouch.touch(767, 67)
