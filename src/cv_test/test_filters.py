import cv2
import numpy as np
import os
from lines import get_red_lines

current_path = os.path.abspath(__file__)

images: list[np.ndarray] = []
for i in range(14):
    img = cv2.imread(os.path.join(os.path.dirname(
        current_path), f"images/test{i}.png"))
    images.append(img)

current_img = images[0].copy()
current_img_index = 0


def change_image(direction):
    global current_img_index
    global current_img

    current_img_index += direction
    current_img_index = current_img_index % len(images)
    if current_img_index < 0:
        current_img_index = len(images) - 1
    current_img = images[current_img_index].copy()


def horizontal_edge(img):
    kernel = np.array([[-1, 0, 1],
                       [-2, 0, 2],
                       [-1, 0, 1]])
    return cv2.filter2D(img, ddepth=-1, kernel=kernel)


def vertical_edge(img):
    kernel = np.array([[-1, -2, -1],
                       [0, 0, 0],
                       [1, 2, 1]])
    return cv2.filter2D(img, ddepth=-1, kernel=kernel)


def filter_border():
    global current_img
    h = horizontal_edge(current_img.copy())
    v = vertical_edge(current_img.copy())
    current_img = h + v


def filter_hue():
    global current_img
    hsv_image = cv2.cvtColor(current_img.copy(), cv2.COLOR_BGR2HSV)

    lower_bound = np.array([0, 128, 0])
    upper_bound = np.array([20, 255, 255])
    mask1 = cv2.inRange(hsv_image, lower_bound, upper_bound)

    lower_bound = np.array([170, 128, 0])
    upper_bound = np.array([179, 255, 255])
    mask2 = cv2.inRange(hsv_image, lower_bound, upper_bound)

    mask = cv2.bitwise_or(mask1, mask2, current_img)
    return cv2.bitwise_and(current_img, current_img, mask=mask)


def edges():
    current_img = filter_hue()
    gray = cv2.cvtColor(current_img, cv2.COLOR_BGR2GRAY)
    kernel_size = 5
    blur_gray = cv2.GaussianBlur(gray, (kernel_size, kernel_size), 0)
    return blur_gray


def line():
    global current_img
    default = current_img.copy()
    lines = get_red_lines(edges())
    for line in lines:
        x1, y1, x2, y2 = line
        cv2.line(default, (x1, y1), (x2, y2), (255, 0, 0), 5)
    return default


if __name__ == "__main__":
    while True:
        cv2.imshow("barcode", current_img)
        key = cv2.waitKey()
        if key == ord("q"):
            break
        if key == ord("a"):
            change_image(-1)
        if key == ord("d"):
            change_image(1)
        if key == ord("f"):
            filter_border()
        if key == ord("h"):
            current_img = filter_hue()
        if key == ord("p"):
            current_img = edges()
        if key == ord("m"):
            current_img = line()
    cv2.destroyAllWindows()
