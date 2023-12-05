from core.android import Android
from logging import Logger
from cv.extensions import template_matching
import cv2
from pathlib import Path
from bot.attack_strategies.builder_base_attack import BuilderBaseAttack
import time
from bot.utils.button_touch import ButtonTouch
from config.buttons import Buttons
from cv.text_finder import TextFinder

assets_path = Path(__file__).joinpath("..", "..", "..", "assets")
template_ranking_icon = cv2.imread(
    assets_path.joinpath("templates", "ranking_builder_base.png").as_posix())


class BuilderBase:
    def __init__(self, logger: Logger, android: Android) -> None:
        self.logger = logger
        self.android: Android = android
        self.builder_base_attack = BuilderBaseAttack(android)
        self.button_touch = ButtonTouch(android)
        self.text_finder = TextFinder()

    def is_in_builder_base(self) -> bool:
        img = self.android.get_screenshot()
        result = template_matching(img, template_ranking_icon)
        return result is not None

    def start_search(self) -> None:
        self.button_touch.try_press(Buttons.StartAttack)
        time.sleep(1)
        self.button_touch.try_press(Buttons.FindAMatch)
        img = self.android.get_screenshot()
        while self.text_finder.find(img, "searching for opponent", 0.5) is not None:
            img = self.android.get_screenshot()

    def attack(self) -> None:
        self.start_search()
        self.builder_base_attack.start()

    def run(self) -> None:
        self.zoom()
        for _ in range(5):
            self.attack()

    def zoom(self) -> None:
        self.android.zoom_out()
        time.sleep(0.5)
        max_x, max_y = self.android.bluestacks.get_screen_size()
        self.android.minitouch.swipe_along([(int(max_x * 0.5), int(max_y * 0.1)),
                                            (int(max_x * 0.5), int(max_y * 0.9))], 2, 10)
        time.sleep(0.5)
        self.android.minitouch.swipe_along([(int(max_x * 0.95), int(max_y * 0.5)),
                                            (int(max_x * 0.5), int(max_y * 0.5))], 1, 5)
        time.sleep(0.5)
