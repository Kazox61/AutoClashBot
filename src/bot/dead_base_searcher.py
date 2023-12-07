from core.android import Android
from cv.yolo_detector import YoloDetector, DetectorResult
from cv.yolo_classifier import YoloClassifier
from cv.text_finder import TextFinder
import time
from logging import Logger
from config.buttons import Buttons
from bot.utils.button_touch import ButtonTouch
import os


class SearchResult:
    def __init__(self, duration: float, iterations: int, resources: [int, int, int]) -> None:
        self.duration = duration
        self.iterations = iterations
        self.resources = resources

    def __repr__(self) -> str:
        return f"Duration: {self.duration}secs, Iterations: {self.iterations}, Gold: {self.resources[0] if len(self.resources) > 0 else None}, Elixir: {self.resources[1]  if len(self.resources) > 1 else None}, Dark Elixir: {self.resources[2]  if len(self.resources) > 2 else None}"


class DeadBaseSearcher:
    def __init__(
            self,
            logger: Logger,
            android: Android,
            building_detector: YoloDetector,
            text_finder: TextFinder
    ) -> None:
        self.logger = logger
        self.android = android
        self.building_detector = building_detector
        self.text_finder = text_finder
        self.button_touch = ButtonTouch(self.android)
        self.collector_classifier = YoloClassifier(
            os.path.join(__file__, "../../../assets/or_models/collector_classifier_model.pt"))

    def search(self) -> SearchResult | None:
        start_time = time.time()
        self.start_search()
        iterations = 0
        while True:
            iterations += 1
            time.sleep(4)
            try:
                img = self.android.get_screenshot()

                while self.text_finder.find(img, "searching for opponent", 0.5) is not None:
                    img = self.android.get_screenshot()

                # execute it twice because it s possible that screen switches from clouds to opponents and both text could not exist
                for _ in range(2):
                    img = self.android.get_screenshot()
                    height, width, _ = img.shape
                    cropped = img[0: int(height * 0.3),
                                  int(0):int(width * 0.3)]
                    available_loot_text_position = self.text_finder.find(
                        cropped, "available loot", 0.75)
                    if available_loot_text_position:
                        break

                if not available_loot_text_position:
                    # currently not in clounds and dont have a opponent => return
                    return None

                resources = self.find_available_loot(
                    cropped, available_loot_text_position)

                val = self.validate(img)
                if val >= 10:
                    break
            except Exception as e:
                resources = [None, None, None]
                self.logger.error(e)
            try:
                gold, elixir, dark_elexir = resources
            except:
                gold, elixir, dark_elexir = [None, None, None]
            self.logger.info(
                f"Found base with Gold: {gold}, Elixir: {elixir}, Dark Elixir: {dark_elexir}")
            self.button_touch.try_press(Buttons.NextOpponent)
        duration = time.time() - start_time
        return SearchResult(duration, iterations, resources)

    def start_search(self) -> None:
        self.button_touch.try_press(Buttons.StartAttack)
        time.sleep(1)
        self.button_touch.try_press(Buttons.FindAMatch)

    def find_available_loot(self, cropped_img, available_loot_text_position=None) -> tuple[int, int, int]:
        if available_loot_text_position is None:
            available_loot_text_position = self.text_finder.find(
                cropped_img, "available loot", 0.75)
        if available_loot_text_position is None:
            return None, None, None
        result = self.text_finder.find_all(
            cropped_img, allowlist='0123456789 ')
        values = [(key, value) for key, value in result.items()]

        loot = []
        for key, coords in values:
            if coords[1] > available_loot_text_position[1]:
                loot.append(int(key.replace(" ", "")))
        return loot[0] if len(loot) > 0 else None, loot[1] if len(loot) > 1 else None, loot[2] if len(loot) > 2 else None

    def validate(self, image) -> int:
        start_time = time.time()
        results: list[DetectorResult] = self.building_detector.predict(image)
        self.logger.debug(
            f"It took {time.time() - start_time} to predict the buildings")
        val = 0
        start_time = time.time()
        for result in results:
            if result.cls != 24:
                continue
            cropped = image[int(result.xyxy[1]): int(
                result.xyxy[3]), int(result.xyxy[0]):int(result.xyxy[2])]
            classifier_result = self.collector_classifier.predict(cropped)
            name, _ = classifier_result.best()
            if name == 'EmptyEC':
                val -= 2
            elif name == 'LowEC':
                val -= 1
            elif name == 'MiddleEC':
                val += 2
            elif name == 'MostlyEC' or name == 'FullEC':
                val += 3
        self.logger.debug(
            f"It took {time.time() - start_time} to classify the collectors")
        return val
