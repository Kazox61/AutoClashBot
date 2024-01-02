from cv.yolo_detector import YoloDetector
from bot.base.coc_base import CoCBase

building_detector = YoloDetector(
    "../assets/or_models/building_bh_detector_model.pt", 0.8)


class BuilderBase(CoCBase):
    def __init__(self) -> None:
        super().__init__()
        self.building_detector = building_detector
