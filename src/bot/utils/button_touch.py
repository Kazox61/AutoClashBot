from core.android import Android
from config.buttons import Buttons
import cv2
from image.extensions import template_matching


class ButtonTouch:
    def __init__(self, android: Android) -> None:
        self.android = android

    def try_press(self, button: Buttons) -> bool:
        value = button.value
        if type(value) == str:
            template = cv2.imread(value)
            img = self.android.get_screenshot()
            result = template_matching(img, template)
            if result is None:
                return False
            self.android.touch_input.touch(result.centerx, result.centery)
        elif type(value) == tuple:
            self.android.touch_input.touch(value[0], value[1])
            return True
        return False
