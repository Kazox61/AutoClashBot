from touch_input.touch_input import TouchInput
from device.device import Device
from ppadb.client import Client as AdbClient
from ppadb.device import Device as AdbDevice


package_name = "com.supercell.clashofclans"


class Android:
	def __init__(self, touch_input: TouchInput, device: Device):
		self.touch_input = touch_input
		self.device = device
		self._adb_client: AdbClient = None
		self.adb_device: AdbDevice = None

	def init(self):
		self.device.stop_adb_server()
		self.device.start_adb_server()

		self._adb_client = self.device.create_adb_client()
		self.adb_device = self.device.create_adb_device()

		self.touch_input.init(self.adb_device)

	def start_app(self):
		self.adb_device.shell(f"monkey -p {package_name} 1")

	def stop_app(self):
		self.adb_device.shell(f"am force-stop {package_name}")
