from core.android import Android
from logging import Logger
from bot.home_village import HomeVillage
from bot.builder_base import BuilderBase
from pathlib import Path
import cv2
from cv.extensions import template_matching
import time


assets_path = Path(__file__).joinpath("..", "..", "..", "assets")
template_boat_switch = cv2.imread(
    assets_path.joinpath("templates", "boat_switch.png").as_posix())


class Village:
    def __init__(self, profile_name, logger: Logger, android: Android) -> None:
        self.profile_name = profile_name
        self.logger = logger
        self.android: Android = android
        self.home_village = HomeVillage(self.logger, self.android)
        self.builder_base = BuilderBase(self.logger, self.android)

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

    def run(self) -> None:
        self.home_village.run()
