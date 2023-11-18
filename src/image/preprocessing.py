import cv2
import numpy as np

red_line_colors = [(154, 65, 47), (149, 69, 76), (166, 40, 24), (94, 41, 57)]


def filter_red_lines(image):
	hsv_filter = create_hsv_filer(red_line_colors)
	apply_hsv_filter(image, hsv_filter)


def create_hsv_filer(rgb_colors):
	hsv_filter = []
	for rgb_color in rgb_colors:
		bgr_color = np.array([rgb_color[2], rgb_color[1], rgb_color[0]], dtype=np.uint8)
		hsv_color = cv2.cvtColor(np.array([[bgr_color]]), cv2.COLOR_BGR2HSV)[0][0]
		hsv_filter.append((
			np.array([hsv_color[0] - 10, hsv_color[1] - 40, hsv_color[2] - 40]),
			np.array([hsv_color[0] + 10, hsv_color[1] + 40, hsv_color[2] + 40])
		))
	return hsv_filter


def apply_hsv_filter(image, hsv_filter):
	hsv_image = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
	filtered_mask = np.zeros_like(hsv_image[:, :, 0], dtype=np.uint8)

	for hsv_range in hsv_filter:
		lower_threshold = hsv_range[0]
		upper_threshold = hsv_range[1]

		mask = cv2.inRange(hsv_image, lower_threshold, upper_threshold)
		filtered_mask = cv2.bitwise_or(filtered_mask, mask)

	filtered_image = cv2.bitwise_and(image, image, mask=filtered_mask)

	# Modify the input image with the filtered version
	image[:, :, :] = filtered_image[:, :, :]


# contrast from 0 to 3 where 1 is current and brightness from 0 to 100
def apply_contrast(image, contrast=1.0, brightness=0):
	cv2.convertScaleAbs(image, alpha=contrast, beta=brightness, dst=image)


def apply_threshold(image, threshold=127):
	cv2.threshold(image, threshold, 255, cv2.THRESH_BINARY, dst=image)


def get_average_brightness(image):
	gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
	average_brightness = np.mean(gray_image)
	return average_brightness
