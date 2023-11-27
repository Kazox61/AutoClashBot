from touch_input.touch_input import TouchInput


class AdbTouch(TouchInput):
    def init(self, adb_device):
        super().init(adb_device)

    def touch(self, x: int, y: int, duration: float):
        self._adb_device.input_swipe(x, y, x, y, int(duration * 1000))
