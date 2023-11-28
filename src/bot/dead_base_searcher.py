from core.android import Android
from object_detection.yolo_detector import YoloDetector, DetectorResult
from object_detection.yolo_classifier import YoloClassifier
from ocr.text_finder import TextFinder, convert_to_int
import time
from difflib import SequenceMatcher
from logging import Logger
from config.buttons import Buttons
from bot.utils.button_touch import ButtonTouch


class SearchResult:
    def __init__(self, duration: float, iterations: int, resources: [int, int, int]) -> None:
        self.duration = duration
        self.iterations = iterations
        self.resources = resources

    def __repr__(self) -> str:
        return f"Duration: {self.duration}secs, Iterations: {self.iterations}, Gold: {self.resources[0] if len(self.resources) > 0 else None}, Elixir: {self.resources[1]  if len(self.resources) > 1 else None}, Dark Elixir: {self.resources[2]  if len(self.resources) > 2 else None}"


class DeadBaseSearcher:
    def __init__(self, logger: Logger, android: Android, text_finder: TextFinder) -> None:
        self.logger = logger
        self.android = android
        self.text_finder = text_finder
        self.button_touch = ButtonTouch(self.android)
        self.building_detector = YoloDetector(
            "../object_detection/models/building_detector_model.pt", 0.7)
        self.collector_classifier = YoloClassifier(
            "../object_detection/models/collector_classifier_model.pt")

    def search(self) -> None:
        start_time = time.time()
        self.start_search()
        iterations = 0
        while True:
            iterations += 1
            time.sleep(8)
            try:
                img = self.android.get_screenshot()
                resources = self.find_available_loot(img)

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

    def find_available_loot(self, screen_shot) -> [int, int, int]:
        height, width, _ = screen_shot.shape
        cropped = screen_shot[0: int(height * 0.3), int(0):int(width * 0.3)]
        result = self.text_finder.find_all(cropped)
        values = [(key, value) for key, value in result.items()]

        loot = []
        loot_index = None
        for index, (key, coords) in enumerate(values):
            sm = SequenceMatcher(a="Available Loot", b=key)
            if sm.ratio() > 0.8:
                loot_index = index
                continue
            if not loot_index:
                continue
            if index == loot_index + 1:
                loot.append(convert_to_int(key))
            if index == loot_index + 2:
                loot.append(convert_to_int(key))
            if index == loot_index + 3:
                loot.append(convert_to_int(key))
        return loot

    def validate(self, image) -> int:
        results: list[DetectorResult] = self.building_detector.predict(image)
        val = 0
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
        return val
