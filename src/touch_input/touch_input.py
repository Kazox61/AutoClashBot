from adbutils import AdbDevice

class TouchInput:
	def init(self, adb_device: AdbDevice, device):
		self.adb_device = adb_device
		self.device = device

	def touch(self, x: int, y: int, duration: float):
		pass

	def zoom_out(self):
		pass
