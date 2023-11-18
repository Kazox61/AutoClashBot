from config import ConfigCore
from android import Android
from logger import Logger
from touch_input.mini_touch import MiniTouch
from touch_input.adb_touch import AdbTouch
from device.physical_device import PhysicalDevice
from device.virtual_device import VirtualDevice


def build() -> Android:
	config = ConfigCore.get_config()
	if config["touchInput"] == "MiniTouch":
		touch_input = MiniTouch()
	elif config["touchInput"] == "AdbTouch":
		touch_input = AdbTouch()
	else:
		touch_input = AdbTouch()
		Logger.error(f"DeviceType '{config['touchInput']}' doesn't exist.")

	if config["deviceType"] == "PhysicalDevice":
		device = PhysicalDevice()
	else:
		device = VirtualDevice()

	return Android(touch_input, device)

