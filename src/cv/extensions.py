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


def contrast(img):
    lab = cv2.cvtColor(img, cv2.COLOR_BGR2LAB)

    l_channel, a, b = cv2.split(lab)
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    cl = clahe.apply(l_channel)

    limg = cv2.merge((cl, a, b))
    enhanced_img = cv2.cvtColor(limg, cv2.COLOR_LAB2BGR)
    return enhanced_img


def erode(img):
    kernel = np.ones((5, 5), np.uint8)
    return cv2.erode(img, kernel)


def dilate(img):
    kernel = np.ones((5, 5), np.uint8)
    return cv2.dilate(img, kernel)


def filter_hue(img):
    hsv_image = cv2.cvtColor(img.copy(), cv2.COLOR_BGR2HSV)

    lower_bound = np.array([0, 128, 0])
    upper_bound = np.array([20, 255, 255])
    mask1 = cv2.inRange(hsv_image, lower_bound, upper_bound)

    lower_bound = np.array([170, 128, 0])
    upper_bound = np.array([179, 255, 255])
    mask2 = cv2.inRange(hsv_image, lower_bound, upper_bound)

    mask = cv2.bitwise_or(mask1, mask2, img)
    return cv2.bitwise_and(img, img, mask=mask)


def gray(img):
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    return gray


def threshold(img):
    _, th = cv2.threshold(img, 30, 255, cv2.THRESH_BINARY)
    return th


def blur(img):
    kernel_size = 5
    return cv2.GaussianBlur(img, (kernel_size, kernel_size), sigmaX=2, sigmaY=2)


def edges(img):
    return cv2.Canny(img, threshold1=30, threshold2=60)
