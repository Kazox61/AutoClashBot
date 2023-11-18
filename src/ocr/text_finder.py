import numpy as np
import easyocr
import cv2

def preprocess(image):
	# Define a threshold value for color closeness to white
	color_threshold = 10

	# Create a mask for white or near-white colors
	mask = np.logical_and.reduce(np.abs(image - [255, 255, 255]) < color_threshold, axis=-1)

	# Apply the mask to filter out non-white or near-white colors
	filtered_image = np.zeros_like(image)
	filtered_image[mask] = image[mask]
	return filtered_image


class TextFinder:
	def __init__(self):
		self._reader = easyocr.Reader(lang_list=['en'])

	def find(self, image, text: str):
		processed = preprocess(image)
		results = self._reader.readtext(processed)

		for result in results:
			found_text = result[1]
			if text.lower() in found_text.lower():
				position = result[0]  # Position information is a list of points
				x_coords, y_coords = zip(*position)  # Separate x and y coordinates
				center_x = sum(x_coords) / len(x_coords)  # Calculate the average of x coordinates
				center_y = sum(y_coords) / len(y_coords)

				return center_x, center_y
		return None
