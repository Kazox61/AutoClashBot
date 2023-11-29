from core.android import Android
from cv.text_finder import TextFinder
from logging import Logger
from bot.attack_strategies.circular_attack import CircularAttack
from cv.yolo_detector import YoloDetector
from bot.dead_base_searcher import DeadBaseSearcher
import time
from config.buttons import Buttons
from bot.utils.button_touch import ButtonTouch
import os
from cv.extensions import template_matching
import cv2


template_supertroop_lab_inactive = cv2.imread(os.path.join(
    __file__, "../../../assets/templates/supertroop_lab_inactive.png"))


class HomeVillage:
    def __init__(self, logger: Logger, android: Android):
        self.logger = logger
        self.android: Android = android
        self.building_detector = YoloDetector(
            os.path.join(__file__, "../../../assets/or_models/building_detector_model.pt"), 0.7)
        self.text_finder = TextFinder()
        self.button_touch = ButtonTouch(self.android)

        self.dead_base_searcher = DeadBaseSearcher(
            self.logger,
            self.android,
            self.building_detector,
            self.text_finder
        )
        self.circular_attack = CircularAttack(self.android)

    def is_in_home_village(self) -> bool:
        screenshot = self.android.get_screenshot()
        has_attack_text = self.text_finder.find(
            screenshot, "attack!", 0.6) is not None
        has_shop_text = self.text_finder.find(
            screenshot, "shop", 0.6) is not None
        if not has_attack_text or not has_shop_text:
            return False
        buildings = self.building_detector.predict(screenshot)
        return len(buildings) > 50

    def force_home_village(self) -> None:
        if self.is_in_home_village():
            return
        self.button_touch.try_press(Buttons.Close)
        time.sleep(0.5)
        if self.is_in_home_village():
            return
        self.android.stop_app()
        time.sleep(2)
        self.android.start_app()
        time.sleep(8)
        if self.is_in_home_village():
            return
        self.android.bluestacks.close_virtual_device()
        time.sleep(5)
        self.android.initialize()
        self.logger.info("Start Clash of Clans App")
        self.android.start_app()
        time.sleep(10)
        if self.is_in_home_village():
            return
        self.logger.error("Can't force to go to the HomeVillage")

    def try_activate_super_troop(self) -> bool:
        result = template_matching(self.android.get_screenshot(),
                                   template_supertroop_lab_inactive, 0.7)

        if result is None:
            return False

        super_barbs = (180, 330)
        activate = (580, 490)
        activate_confirm = (390, 410)
        close_button = (685, 116)
        self.android.minitouch.touch(result.centerx, result.centery)
        time.sleep(1)
        self.android.minitouch.touch(super_barbs[0], super_barbs[1])
        time.sleep(1)
        self.android.minitouch.touch(activate[0], activate[1])
        time.sleep(1)
        self.android.minitouch.touch(activate_confirm[0], activate_confirm[1])
        time.sleep(1)
        self.android.minitouch.touch(close_button[0], close_button[1])
        time.sleep(1)
        return True

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
        self.force_home_village()
        self.android.minitouch.zoom_out()
        time.sleep(1)
        self.try_activate_super_troop()
        self.quick_train()
        while not self.is_army_ready():
            self.quick_train()
            time.sleep(20)
        search_result = self.dead_base_searcher.search()
        self.logger.info(f"Attacking base with {search_result}!")
        self.circular_attack.start()
