from core.android import Android
from ocr.text_finder import TextFinder
from logging import Logger
from bot.attack_strategies.circular_attack import CircularAttack
from bot.dead_base_searcher import DeadBaseSearcher
import time
from config.buttons import Buttons
from bot.utils.button_touch import ButtonTouch


class HomeVillage:
    def __init__(self, logger: Logger, android: Android):
        self.logger = logger
        self.android: Android = android
        self.text_finder = TextFinder()
        self.button_touch = ButtonTouch(self.android)

        self.dead_base_searcher = DeadBaseSearcher(
            self.logger,
            self.android,
            self.text_finder
        )
        self.circular_attack = CircularAttack(self.android)

    def is_in_home_village(self) -> bool:
        screenshot = self.android.get_screenshot()
        has_attack_text = self.text_finder.find(
            screenshot, "attack!", 0.6) is not None
        has_shop_text = self.text_finder.find(
            screenshot, "shop", 0.6) is not None
        return has_attack_text and has_shop_text

    def quick_train(self) -> None:
        self.button_touch.try_press(Buttons.TrainAll)
        time.sleep(0.5)
        self.button_touch.try_press(Buttons.QuickTrain)
        time.sleep(0.5)
        self.button_touch.try_press(Buttons.TrainArmy1)
        time.sleep(1)
        self.button_touch.try_press(Buttons.Close)
        time.sleep(0.5)

    def is_army_ready(self) -> bool:
        self.button_touch.try_press(Buttons.TrainAll)
        time.sleep(0.5)
        self.button_touch.try_press(Buttons.TrainTroops)
        time.sleep(0.5)
        found_text = self.text_finder.find(
            self.android.get_screenshot(), "finish training", 0.8)
        time.sleep(0.5)
        self.button_touch.try_press(Buttons.Close)
        time.sleep(0.5)
        return found_text is None

    def loop(self) -> None:
        self.quick_train()
        while not self.is_army_ready():
            self.quick_train()
            time.sleep(20)
        search_result = self.dead_base_searcher.search()
        self.logger.info(f"Attacking base with {search_result}!")
        self.circular_attack.start()
