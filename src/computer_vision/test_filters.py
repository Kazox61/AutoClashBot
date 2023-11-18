import cv2
import numpy as np
import os

current_path = os.path.abspath(__file__)

images: list[np.ndarray] = []
for i in range(15):
    img = cv2.imread(os.path.join(os.path.dirname(current_path), f"images/test{i}.png"))
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
    kernel = np.array([[-1,0,1],
                       [-2,0,2],
                       [-1,0,1]])
    return cv2.filter2D(img, ddepth=-1, kernel=kernel)

def vertical_edge(img):
    kernel = np.array([[-1,-2,-1],
                       [0,0,0], 
                       [1,2,1]])
    return cv2.filter2D(img, ddepth=-1, kernel=kernel)

def filter_border():
    global current_img
    h = horizontal_edge(current_img.copy())
    v = vertical_edge(current_img.copy())
    current_img =  h + v


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
    cv2.destroyAllWindows()