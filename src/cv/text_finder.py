import numpy as np
import easyocr
from difflib import SequenceMatcher


def convert_to_int(input: str) -> int:
    mapping = {' ': '', 'I': '1', 'O': '0', 'o': '0', 'z': '2', 'Z': '2'}
    for o, n in mapping.items():
        input = input.replace(o, n)
    return int(input)


class TextFinder:
    def __init__(self):
        self.reader = easyocr.Reader(lang_list=['en'])

    def find(self, image: np.ndarray, text: str, conf: float = 0.9, paragraph=False) -> tuple[int, int] | None:
        results = self.reader.readtext(image, paragraph=paragraph)
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

    def find_all(self, image: np.ndarray, paragraph=False) -> dict[str, tuple[float, float]]:
        text = {}
        results = self.reader.readtext(image, paragraph=paragraph)
        for result in results:
            position = result[0]
            x_coords, y_coords = zip(*position)
            center_x = sum(x_coords) / len(x_coords)
            center_y = sum(y_coords) / len(y_coords)
            text[result[1]] = (center_x, center_y)
        return text
