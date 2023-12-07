from core.android import Android
from logging import Logger
from cv.text_finder import TextFinder
from bot.attack_strategies.circular_attack import CircularAttack
from cv.yolo_detector import YoloDetector
from bot.dead_base_searcher import DeadBaseSearcher
import time
from config.buttons import Buttons
from bot.utils.button_touch import ButtonTouch
import os
from cv.extensions import template_matching
import cv2
from difflib import SequenceMatcher


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
        self.try_handle_daily_reward_screen()
        self.button_touch.try_press(Buttons.Close)
        time.sleep(0.5)
        if self.is_in_home_village():
            return
        self.android.stop_app()
        time.sleep(2)
        self.android.start_app()
        time.sleep(10)

    def try_handle_daily_reward_screen(self) -> None:
        is_daily_reward_screen = False
        all_text = self.text_finder.find_all(self.android.get_screenshot())
        for text, position in all_text.items():
            sm1 = SequenceMatcher(a=text.lower(), b='dailiy reward!')
            sm2 = SequenceMatcher(
                a=text.lower(), b='log in daily to collect rewards!')
            if sm1.ratio() > 0.7 or sm2.ratio() > 0.7:
                is_daily_reward_screen = True

        if not is_daily_reward_screen:
            return

        for text, position in all_text.items():
            sm = SequenceMatcher(a=text.lower(), b='claim')
            if sm.ratio() > 0.6:
                self.android.minitouch.touch(position[0], position[1])
                self.logger.info("Claimed daily reward")
                time.sleep(0.5)
                self.button_touch.try_press(Buttons.Close)
                break
        self.logger.warning(
            "Found daily reward screen, but can't find claim button!")

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
        self.logger.info(f"Activated Super Troop")
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

    def collect_resources(self) -> None:
        self.logger.debug("Collect Resources")
        max_x, max_y = self.android.bluestacks.get_screen_size()
        buildings = self.building_detector.predict(
            self.android.get_screenshot())
        collected_gold = False
        collected_elixir = False
        collected_dark_elixir = False
        for builing in buildings:
            if builing.name == 'Gold Mine' and not collected_gold:
                collected_gold = True
                self.android.minitouch.touch(max_x * 0.99, max_y * 0.5)
                time.sleep(0.5)
                self.android.minitouch.touch(builing.xywh[0], builing.xywh[1])
                time.sleep(0.5)
            if builing.name == 'Elixir Collector' and not collected_elixir:
                collected_elixir = True
                self.android.minitouch.touch(max_x * 0.99, max_y * 0.5)
                time.sleep(0.5)
                self.android.minitouch.touch(builing.xywh[0], builing.xywh[1])
                time.sleep(0.5)
            if builing.name == 'Dark Elixir Drill' and not collected_dark_elixir:
                collected_dark_elixir = True
                self.android.minitouch.touch(max_x * 0.99, max_y * 0.5)
                time.sleep(0.5)
                self.android.minitouch.touch(builing.xywh[0], builing.xywh[1])
                time.sleep(0.5)

            if collected_gold and collected_elixir and collected_dark_elixir:
                break

    def zoom_out(self) -> None:
        x, y = self.android.bluestacks.get_screen_size()
        center_y = y * 0.5
        self.android.minitouch.two_finger_swipe(
            (x*0.1, center_y), (x*0.45, center_y), (x*0.9, center_y), (x*0.55, center_y), 2, 5)
        time.sleep(0.5)
        self.android.minitouch.swipe_along([(int(x * 0.2), int(y * 0.2)),
                                            (int(x * 0.8), int(y * 0.8))])

    def run(self) -> None:
        while True:
            self.force_home_village()
            self.zoom_out()
            time.sleep(1)
            self.collect_resources()
            self.try_activate_super_troop()
            self.quick_train()
            if not self.is_army_ready():
                return
            self.logger.info("Army is ready. Start to search for dead base")
            search_result = self.dead_base_searcher.search()
            # is in a deadlock (not in clounds and no opponents)
            if search_result is None:
                self.android.stop_app()
                self.logger.warning(
                    "Not in clouds or has opponent. Stop searching. Force HomeVillage!")
                continue
            self.logger.info(f"Attacking base with {search_result}!")
            self.circular_attack.start()
