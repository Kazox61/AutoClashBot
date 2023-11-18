from bot.find_red_lines import preprocess_image
from image.preprocessing import get_average_brightness
import cv2
import os


def test_images():
	if os.path.exists("output"):
		os.remove("output")
	os.mkdir("output")
	for i, image_name in enumerate(os.listdir("images")):
		image = cv2.imread(os.path.join("images", image_name))

		image = preprocess_image(image)

		# done testing
		cv2.imwrite(os.path.join("output",image_name), image)


if __name__ == "__main__":
	test_images()
