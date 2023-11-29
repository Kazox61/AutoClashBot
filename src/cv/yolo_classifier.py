from ultralytics import YOLO


class ClassifierResult:
    def __init__(self, result):
        self.result = result

    def __repr__(self):
        return f"names: {self.result.names} top1: {self.result.probs.top1}"

    def best(self) -> (str, int):
        index = self.result.probs.top1
        name = self.result.names.get(index)
        return name, index


class YoloClassifier:
    def __init__(self, model_path: str):
        self.model = YOLO(model_path)

    def predict(self, image) -> ClassifierResult:
        result = self.model.predict(source=image, verbose=False)[0]
        return ClassifierResult(result)
