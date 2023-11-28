from ultralytics import YOLO


class DetectorResult:
    cls: int
    conf: float
    name: str
    xyxy = list
    xywhn = list

    def __init__(self, cls: int, conf: float, name: str, xyxy: list, xyxyn: list, xywh: list, xywhn: list):
        self.cls = cls
        self.conf = conf
        self.name = name
        self.xyxy = xyxy
        self.xyxyn = xyxyn
        self.xywh = xywh
        self.xywhn = xywhn

    def __repr__(self):
        return f"cls: {self.cls} conf: {self.conf} name: {self.name}"


class YoloDetector:
    def __init__(self, model_path: str, min_conf: float):
        self.model = YOLO(model_path)
        self.min_conf = min_conf

    def predict(self, image_data) -> list[DetectorResult]:
        result = self.model.predict(
            source=image_data, verbose=False, conf=self.min_conf)[0]
        names = result.names
        boxes = result.boxes
        predict_results = []
        for conf, cls, xyxy, xyxyn, xywh, xywhn in zip(boxes.conf, boxes.cls, boxes.xyxy, boxes.xyxyn, boxes.xywh, boxes.xywhn):
            conf = round(conf.item(), 2)
            xyxy = xyxy.tolist()
            xyxyn = xyxyn.tolist()
            xywh = xywh.tolist()
            xywhn = xywhn.tolist()
            cls = int(cls.item())
            name = names[cls]
            predict_results.append(DetectorResult(
                cls, conf, name, xyxy, xyxyn, xywh, xywhn))
        return predict_results
