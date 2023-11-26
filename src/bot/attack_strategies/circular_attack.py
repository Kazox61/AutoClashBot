from core.android import Android
import time
from bot.utils.text_button import TextButton

start_center_x = 90
step = 66
row_y = 550

class CircularAttack:
	def __init__(self, android: Android, text_finder) -> None:
		self._android = android
		self._leave_attack_end_battle_button = TextButton(text_finder, self._android.touch_input, "end battle")
		self._leave_attack_surrender_button = TextButton(text_finder, self._android.touch_input, "surrender")
		self._leave_attack_okay_button = TextButton(text_finder, self._android.touch_input, "okay")
		self._leave_attack_return_home_button = TextButton(text_finder, self._android.touch_input, "return home", 0.5)

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
		time.sleep(20)
		self._leave_attack()

	def _select_troop(self, index):
		self._android.touch_input.touch(start_center_x + index * step, row_y)

	def _leave_attack(self):
		success = self._leave_attack_surrender_button.try_press(self._android.get_screenshot())
		if not success:
			self._leave_attack_end_battle_button.try_press(self._android.get_screenshot())
		time.sleep(1)
		self._leave_attack_okay_button.try_press(self._android.get_screenshot())
		time.sleep(2)
		self._leave_attack_return_home_button.try_press(self._android.get_screenshot())
		time.sleep(5)