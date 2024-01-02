from core.android import Android
from logging import Logger
from cv.yolo_detector import YoloDetector
from cv.text_finder import TextFinder
from bot.home_village import HomeVillage
from bot.night_village import NightVillage
from pathlib import Path
import cv2
from cv.extensions import template_matching
import time


assets_path = Path(__file__).joinpath("..", "..", "..", "assets")
template_boat_switch = cv2.imread(
    assets_path.joinpath("templates", "boat_switch.png").as_posix())


class Village:
    def __init__(
        self,
        profile_name: str,
        logger: Logger,
        android: Android,
        building_detector: YoloDetector,
        text_finder: TextFinder,
    ) -> None:
        self.profile_name = profile_name
        self.logger = logger
        self.android: Android = android
        self.home_village = HomeVillage(
            self.logger, self.android, building_detector, text_finder)
        self.night_village = NightVillage(
            self.logger, self.android, text_finder)

    def try_switch_game_mode(self) -> bool:
        self.logger.debug("Try switching game mode")
        img = self.android.get_screenshot()
        result = template_matching(img, template_boat_switch)
        if result is None:
            self.logger.debug("Switching game mode failed")
            return False
        self.android.minitouch.touch(result.centerx, result.centery)
        time.sleep(1)
        self.logger.debug("Switching game mode was successfully")
        return True

    async def run(self) -> None:
        await self.home_village.run()
        # self.try_switch_game_mode()
        # await self.night_village.run()
        # self.try_switch_game_mode()
