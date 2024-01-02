from core.android import Android
from logging import Logger
from cv.extensions import template_matching
import cv2
from pathlib import Path
from bot.attack_strategies.smart_bh_attack import SmartBhAttack
import time
from bot.utils.button_touch import ButtonTouch
from config.buttons import Buttons
from cv.text_finder import TextFinder
import asyncio
from config.constants import TEMPLATE_DIR


template_ranking_icon = cv2.imread(
    TEMPLATE_DIR.joinpath("ranking_builder_base.png").as_posix())
template_elixir_cart_icon = cv2.imread(
    TEMPLATE_DIR.joinpath("elixir_cart_bh.png").as_posix())


class NightVillage:
    def __init__(self, logger: Logger, android: Android, text_finder: TextFinder) -> None:
        self.logger = logger
        self.android: Android = android
        self.smart_bh_attack = SmartBhAttack(android)
        self.button_touch = ButtonTouch(android)
        self.text_finder = text_finder

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
        time.sleep(1)

    def attack(self) -> None:
        self.start_search()
        self.zoom()
        self.smart_bh_attack.start()

    async def run(self) -> None:
        self.zoom()
        img = self.android.get_screenshot()
        elixir_cart_pos = template_matching(img, template_elixir_cart_icon)
        if elixir_cart_pos is not None:
            self.android.minitouch.touch(
                elixir_cart_pos.centerx, elixir_cart_pos.centery, randomness=False)
            time.sleep(1)
            self.android.minitouch.touch(605, 475)
            time.sleep(1)
            self.android.minitouch.touch(700, 100)
            time.sleep(1)

        for _ in range(5):
            self.attack()
            await asyncio.sleep(10)
        self.zoom()
        time.sleep(1)

    def zoom(self) -> None:
        x, y = self.android.bluestacks.get_screen_size()
        center_y = y * 0.5
        self.android.minitouch.two_finger_swipe(
            (x*0.1, center_y), (x*0.45, center_y), (x*0.9, center_y), (x*0.55, center_y), 2, 5)
        time.sleep(0.5)
        self.android.minitouch.swipe_along([(int(x * 0.9), int(y * 0.5)),
                                            (int(x * 0.1), int(y * 0.5))])
