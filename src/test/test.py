from bot.builder_base.fast_farm import distribute_points_on_lines, sort_by_closest
from bot.find_red_lines import get_red_lines
import cv2



if __name__ == "__main__":
	image = cv2.imread("abc7.png")
	red_lines = get_red_lines(image)
	print(red_lines)
	sorted_lines = sort_by_closest(red_lines)
	print(sorted_lines)
	points = distribute_points_on_lines(sorted_lines, 60)
	print(len(points))
	for point in points:
		cv2.circle(image, (int(point[0]), int(point[1])), 5, (0, 255, 255), -1)
	cv2.imshow("Point Drawing", image)
	cv2.waitKey(0)
	cv2.destroyAllWindows()

