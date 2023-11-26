from touch_input.touch_input import TouchInput
from device.device import Device
from adbutils import AdbClient, AdbDevice
import numpy as np


package_name = "com.supercell.clashofclans"

class Android:
	adb_client: AdbClient
	adb_device: AdbDevice
	def __init__(self, touch_input: TouchInput, device: Device):
		self.touch_input = touch_input
		self.device = device

	def init(self, instance_config: dict):
		self.adb_client, self.adb_device = self.device.init(instance_config)
		self.touch_input.init(self.adb_device, self.device, instance_config)

	def start_app(self):
		self.adb_device.shell(f"monkey -p {package_name} 1")

	def stop_app(self):
		self.adb_device.shell(f"am force-stop {package_name}")

	def get_screenshot(self) -> np.ndarray:
		pillow_image = self.adb_device.screenshot().convert("RGB")
		open_cv_image = np.array(pillow_image)
		open_cv_image = open_cv_image[:, :, ::-1].copy()
		return open_cv_image
