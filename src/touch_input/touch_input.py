from adbutils import AdbDevice


class TouchInput:
    def init(self, adb_device: AdbDevice, device, instance_config: dict):
        self.adb_device = adb_device
        self.device = device
        self.screen_size: tuple[int, int] = self.device.get_screen_size()

    def touch(self, x: int, y: int, duration: float = 0.1, randomness: bool = True):
        pass

    def swipe_along(self, points, duration=1, steps_per_move=5, first_sleep_duration=0.1):
        pass

    def zoom_out(self):
        pass
