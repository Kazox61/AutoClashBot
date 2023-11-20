from adbutils import adb, AdbClient, AdbDevice


class Device:
	def init(self) -> (AdbClient, AdbDevice):
		self.adb_client = adb
		self.adb_device = self.adb_client.device()
		return self.adb_client, self.adb_device

	def get_screen_size(self):
		output: str = self.adb_device.shell('dumpsys window | grep cur= |tr -s " " | cut -d " " -f 4|cut -d "=" -f 2')
		screen_width, screen_height = output.strip().split("x")
		return int(screen_width), int(screen_height)