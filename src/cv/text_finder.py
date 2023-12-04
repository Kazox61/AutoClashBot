import numpy as np
import easyocr
from difflib import SequenceMatcher


class TextFinder:
    def __init__(self):
        self.reader = easyocr.Reader(lang_list=['en'])

    def find(self, image: np.ndarray, text: str, conf: float = 0.9, paragraph: bool = False, allowlist: str = None) -> tuple[int, int] | None:
        if allowlist is None:
            results = self.reader.readtext(image, paragraph=paragraph)
        else:
            results = self.reader.readtext(
                image, paragraph=paragraph, allowlist=allowlist, width_ths=2, x_ths=2)
        for result in results:
            found_text = result[1]
            sm = SequenceMatcher(a=text.lower(), b=found_text.lower())
            if sm.ratio() > conf:
                position = result[0]
                x_coords, y_coords = zip(*position)
                center_x = sum(x_coords) / len(x_coords)
                center_y = sum(y_coords) / len(y_coords)
                return center_x, center_y

        return None

    def find_all(self, image: np.ndarray, paragraph: bool = False, allowlist: str = None) -> dict[str, tuple[float, float]]:
        text = {}
        if allowlist is None:
            results = self.reader.readtext(image, paragraph=paragraph)
        else:
            results = self.reader.readtext(
                image, paragraph=paragraph, allowlist=allowlist, width_ths=1, x_ths=1)
        for result in results:
            position = result[0]
            x_coords, y_coords = zip(*position)
            center_x = sum(x_coords) / len(x_coords)
            center_y = sum(y_coords) / len(y_coords)
            text[result[1]] = (center_x, center_y)
        return text
