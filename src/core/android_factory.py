from core.android import Android
from logger import Logger
from touch_input.mini_touch import MiniTouch
from touch_input.adb_touch import AdbTouch
from device.physical_device import PhysicalDevice
from device.virtual_device import VirtualDevice


def build(instance_config) -> Android:
	if instance_config["touchInput"] == "MiniTouch":
		touch_input = MiniTouch()
	elif instance_config["touchInput"] == "AdbTouch":
		touch_input = AdbTouch()
	else:
		touch_input = AdbTouch()
		Logger.error(f"DeviceType '{instance_config['touchInput']}' doesn't exist.")

	if instance_config["deviceType"] == "PhysicalDevice":
		device = PhysicalDevice()
	else:
		device = VirtualDevice()

	return Android(touch_input, device)

