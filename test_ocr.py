import numpy as np
import easyocr
import cv2

reader = easyocr.Reader(lang_list=['en'])

img = cv2.imread("capture.png")

results = reader.readtext(img, paragraph=True)
print(results)
