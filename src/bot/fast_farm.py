from core.android import Android
from bot.find_red_lines import get_red_lines
import math
from ocr.text_finder import TextFinder
from logger import Logger
from bot.utils.text_button import TextButton
from bot.utils.button import Button
from bot.attack_strategies.circular_attack import CircularAttack
from bot.dead_base_searcher import DeadBaseSearcher
import time

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
		#self._building_detector = YoloDetector()
		#self._collector_classifier = YoloDetector()
		self._attack_button = TextButton(self._text_finder, self._android.touch_input, "attack")
		self._find_match_button = TextButton(self._text_finder, self._android.touch_input, "match")
		self._next_opponent_button = TextButton(self._text_finder, self._android.touch_input, "next")
		self._train_panel_button = Button((33, 477), self._android.touch_input)
		self._quick_train_button = TextButton(self._text_finder, self._android.touch_input, "quick train")
		self._train_button = TextButton(self._text_finder, self._android.touch_input, "train", 0.6, paragraph=True)
		self._train_troops_button = TextButton(self._text_finder, self._android.touch_input, "train troops", paragraph=True)
		self._close_button = Button((755, 80), self._android.touch_input)

		self._dead_base_searcher = DeadBaseSearcher(self, self._android, self._text_finder)
		self._circular_attack = CircularAttack(self._android, self._text_finder)

	def _quick_train(self) -> None:
		self._train_panel_button.press()
		time.sleep(0.5)
		self._quick_train_button.try_press(self._android.get_screenshot())
		time.sleep(0.5)
		self._train_button.try_press(self._android.get_screenshot())
		time.sleep(1)
		self._close_button.press()
		time.sleep(0.5)

	def _is_army_ready(self) -> bool:
		self._train_panel_button.press()
		time.sleep(0.5)
		self._train_troops_button.try_press(self._android.get_screenshot())
		time.sleep(0.5)
		found_text = self._text_finder.find(self._android.get_screenshot(), "finish training", 0.8)
		time.sleep(0.5)
		self._close_button.press()
		time.sleep(0.5)
		return found_text is None

	def _get_troop_placement(self):
		image = self._android.get_screenshot()
		red_lines = get_red_lines(image)
		sorted_lines = sort_by_closest(red_lines)
		points = distribute_points_on_lines(sorted_lines, 10)
		return points

	def loop(self) -> None:
		self._quick_train()
		while not self._is_army_ready():
			self._quick_train()
			time.sleep(20)
		search_result = self._dead_base_searcher.search()
		Logger.info(f"Attacking base with {search_result}!")
		self._circular_attack.start()





