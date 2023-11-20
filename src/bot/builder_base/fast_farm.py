from android import Android
from bot.find_red_lines import get_red_lines
import math
import time
from ocr.text_finder import TextFinder
from logger import Logger
from bot.utils.button import Button


def distance(x1, y1, x2, y2):
	return math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)


def point_on_line_segment(start, end, distance):
	x1, y1 = start
	x2, y2 = end

	length = math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)

	if length == 0:
		return None
	if length <= distance:
		return None
	x = x1 + (x2 - x1) * (distance / length)
	y = y1 + (y2 - y1) * (distance / length)

	return x, y


def distribute_points_on_lines(lines, total_points):
	total_length = sum(distance(x1, y1, x2, y2) for x1, y1, x2, y2 in lines)
	point_to_point_distance = total_length / total_points
	points = []
	length_remaining = point_to_point_distance
	for x1, y1, x2, y2 in lines:
		while True:
			point = point_on_line_segment((x1, y1), (x2, y2), length_remaining)
			if not point:
				length_remaining -= distance(x1, y1, x2, y2)
				break
			print("Found point")
			x1, y1 = point
			points.append(point)
			length_remaining = point_to_point_distance
		print("new line")

	return points


def sort_by_closest(lines):
	if len(lines) <= 1:
		return lines
	count = len(lines)
	for a in range(count - 1):
		min_index = a + 1
		min_distance = distance(lines[min_index][0], lines[min_index][1], lines[a][2], lines[a][3])
		for b in range(a + 1, count):
			dist1 = distance(lines[b][0], lines[b][1], lines[a][2], lines[a][3])
			dist2 = distance(lines[b][2], lines[b][3], lines[a][2], lines[a][3])
			if dist1 > min_distance and dist2 > min_distance:
				continue
			if dist2 < dist1:
				# switch start and endpoint
				x1, y1, x2, y2 = lines[b]
				lines[b] = [x2, y2, x1, y1]
			min_index = b
			min_distance = min(dist1, dist2)

		# change min_index with the a+1
		workspace = lines[a + 1]
		lines[a + 1] = lines[min_index]
		lines[min_index] = workspace
	return lines





class FastFarm:
	def __init__(self, android: Android):
		self._android: Android = android
		self._text_finder = TextFinder()
		self._attack_button = Button(self._text_finder, self._android.touch_input, "attack")
		self._find_match_button = Button(self._text_finder, self._android.touch_input, "match")
		self._next_opponent_button =Button(self._text_finder, self._android.touch_input, "next")

	def _get_troop_placement(self):
		image = self._android.get_screenshot()
		red_lines = get_red_lines(image)
		sorted_lines = sort_by_closest(red_lines)
		points = distribute_points_on_lines(sorted_lines, 10)
		return points

	def _find_attack(self):
		self._attack_button.try_press(self._android.get_screenshot())
		time.sleep(1)
		self._find_match_button.try_press(self._android.get_screenshot())
		time.sleep(2)
		self._next_opponent_button.try_press(self._android.get_screenshot())
	
	def _search_a_dead_base():
		pass

	def loop(self):
		self._find_attack()
		input()





