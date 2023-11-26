
from touch_input.touch_input import TouchInput

class Button:
	def __init__(self, position: tuple[int, int], touch_input: TouchInput) -> None:
		self.position = position
		self.touch_input = touch_input

	def press(self):
		self.touch_input.touch(self.position[0], self.position[1], 0.5)
		return True
