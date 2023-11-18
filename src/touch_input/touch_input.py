from ppadb.device import Device as AdbDevice


class TouchInput:
	_adb_device: AdbDevice

	def init(self, adb_device):
		self._adb_device = adb_device

	def touch(self, x: int, y: int, duration: float):
		pass
