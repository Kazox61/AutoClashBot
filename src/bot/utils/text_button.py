from ocr.text_finder import TextFinder
from touch_input.touch_input import TouchInput


class TextButton:
    def __init__(self, text_finder: TextFinder, touch_input: TouchInput, text: str, find_conf: float = 0.7, retries: int = 3, paragraph=False) -> None:
        self.text_finder = text_finder
        self.touch_input = touch_input
        self.text = text
        self.position = None
        self.find_conf = find_conf
        self.retries = retries
        self.paragraph = paragraph

    def try_press(self, current_screen) -> bool:
        tries = 0
        while self.position is None and tries < self.retries:
            self.position = self.text_finder.find(
                current_screen, self.text, self.find_conf, self.paragraph)
            tries += 1
        if self.position is None:
            return False
        self.touch_input.touch(self.position[0], self.position[1], 0.5)
        return True
