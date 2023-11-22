from core.android import Android
import time


start_center_x = 90
step = 66
row_y = 550

class CircularAttack:
	def __init__(self, android: Android) -> None:
		self._android = android

	def start(self):
		self._select_troop(0)
		max_x, max_y = self._android.device.get_screen_size()
		touch_cylce = [
			(max_x * 0.5, max_y * 0.05),
			(max_x * 0.25, max_y * 0.25),
			(max_x * 0.1, max_y * 0.5),
			(max_x * 0.25, max_y * 0.75),
			(max_x * 0.5, max_y * 0.9),
			(max_x * 0.75, max_y * 0.75),
			(max_x * 0.9, max_y * 0.5),
			(max_x * 0.75, max_y * 0.25),
		]
		touches = []
		touches.extend(touch_cylce)
		touches.extend(touch_cylce)
		touches.extend(touch_cylce)
		self._android.touch_input.swipe_along(touches, 0.5, 5, 1)
		time.sleep(1)
		self._select_troop(2)
		self._android.touch_input.touch(max_x * 0.5, max_y * 0.05)
		time.sleep(0.5)
		self._select_troop(3)
		self._android.touch_input.touch(max_x * 0.5, max_y * 0.05)
		time.sleep(0.5)
		self._select_troop(4)
		self._android.touch_input.touch(max_x * 0.5, max_y * 0.05)
		time.sleep(0.5)
		self._select_troop(5)
		self._android.touch_input.touch(max_x * 0.5, max_y * 0.05)
		time.sleep(5)
		self._select_troop(2)
		self._select_troop(3)
		self._select_troop(4)
		self._select_troop(5)


		

	def _select_troop(self, index):
		self._android.touch_input.touch(start_center_x + index * step, row_y)