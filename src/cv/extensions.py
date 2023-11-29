from pyrect import Rect
import cv2
import numpy as np


def template_matching(img: np.ndarray, template: np.ndarray, threshold: float = 0.8) -> Rect | None:
    template = cv2.cvtColor(template.copy(), cv2.COLOR_BGR2GRAY)
    img = cv2.cvtColor(img.copy(), cv2.COLOR_BGR2GRAY)
    w, h = template.shape[::-1]
    res = cv2.matchTemplate(img, template, cv2.TM_CCOEFF_NORMED)
    loc = np.where(res >= threshold)
    points = list(zip(*loc[::-1]))

    if not points or len(points) <= 0:
        return None
    point = points[0]
    return Rect(int(point[0]), int(point[1]), int(w), int(h))
