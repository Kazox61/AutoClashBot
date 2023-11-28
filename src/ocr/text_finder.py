import numpy as np
import easyocr
from difflib import SequenceMatcher


def preprocess(image):
    # Define a threshold value for color closeness to white
    color_threshold = 10

    # Create a mask for white or near-white colors
    mask = np.logical_and.reduce(
        np.abs(image - [255, 255, 255]) < color_threshold, axis=-1)

    # Apply the mask to filter out non-white or near-white colors
    filtered_image = np.zeros_like(image)
    filtered_image[mask] = image[mask]
    return filtered_image


def convert_to_int(input: str) -> int:
    mapping = {' ': '', 'I': '1', 'O': '0', 'o': '0', 'z': '2', 'Z': '2'}
    for o, n in mapping.items():
        input = input.replace(o, n)
    return int(input)


class TextFinder:
    def __init__(self):
        self.reader = easyocr.Reader(lang_list=['en'])

    def find(self, image, text: str, conf: float = 0.9, paragraph=False):
        # processed = preprocess(image)
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

    def find_all(self, image, paragraph=False) -> dict[str, tuple[float, float]]:
        text = {}
        results = self.reader.readtext(image, paragraph=paragraph)
        for result in results:
            position = result[0]
            x_coords, y_coords = zip(*position)
            center_x = sum(x_coords) / len(x_coords)
            center_y = sum(y_coords) / len(y_coords)
            text[result[1]] = (center_x, center_y)
        return text
