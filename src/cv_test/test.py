import cv2
import numpy as np
from pathlib import Path
from lines import get_red_lines

fpath = Path.cwd().joinpath("bs")
ims = list(fpath.glob("*.png"))

images: list[np.ndarray] = []
for im in ims:
    img = cv2.imread(im.as_posix())
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


def contrast():
    img = current_img.copy()
    lab = cv2.cvtColor(img, cv2.COLOR_BGR2LAB)

    l_channel, a, b = cv2.split(lab)
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    cl = clahe.apply(l_channel)

    limg = cv2.merge((cl, a, b))
    enhanced_img = cv2.cvtColor(limg, cv2.COLOR_LAB2BGR)
    return enhanced_img


def erode():
    kernel = np.ones((5, 5), np.uint8)
    return cv2.erode(current_img, kernel)


def dilate():
    kernel = np.ones((5, 5), np.uint8)
    return cv2.dilate(current_img, kernel)


def filter_hue():
    hsv_image = cv2.cvtColor(current_img.copy(), cv2.COLOR_BGR2HSV)

    lower_bound = np.array([0, 128, 0])
    upper_bound = np.array([20, 255, 255])
    mask1 = cv2.inRange(hsv_image, lower_bound, upper_bound)

    lower_bound = np.array([170, 128, 0])
    upper_bound = np.array([179, 255, 255])
    mask2 = cv2.inRange(hsv_image, lower_bound, upper_bound)

    mask = cv2.bitwise_or(mask1, mask2, current_img)
    return cv2.bitwise_and(current_img, current_img, mask=mask)


def gray():
    gray = cv2.cvtColor(current_img, cv2.COLOR_BGR2GRAY)
    return gray


def threshold():
    _, th = cv2.threshold(current_img, 30, 255, cv2.THRESH_BINARY)
    return th


def blur():
    kernel_size = 5
    return cv2.GaussianBlur(current_img, (kernel_size, kernel_size), sigmaX=2, sigmaY=2)


def edges():
    return cv2.Canny(current_img, threshold1=30, threshold2=60)


def line():
    default = images[current_img_index].copy()
    lines = get_red_lines(current_img)
    for line in lines:
        x1, y1, x2, y2 = line
        cv2.line(default, (x1, y1), (x2, y2), (255, 0, 0), 5)
    return default


if __name__ == "__main__":
    while True:
        cv2.imshow("Showcase", current_img)
        key = cv2.waitKey()
        if key == ord("q"):
            break
        if key == ord("a"):
            change_image(-1)
        if key == ord("d"):
            change_image(1)
        if key == ord("1"):
            current_img = contrast()
        if key == ord("9"):
            current_img = erode()
        if key == ord("0"):
            current_img = dilate()
        if key == ord("2"):
            current_img = filter_hue()
        if key == ord("3"):
            current_img = gray()
        if key == ord("4"):
            current_img = blur()
        if key == ord("5"):
            current_img = edges()
        if key == ord("6"):
            current_img = line()
        if key == ord("7"):
            current_img = threshold()
        if key == ord("s"):
            cv2.imwrite(Path.cwd().joinpath(
                "output", f"image{current_img_index}.png").as_posix(), current_img)
    cv2.destroyAllWindows()
