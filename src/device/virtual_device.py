from device.device import Device
from adbutils import adb, AdbClient, AdbDevice

bluestacks_config_path = "C:/ProgramData/BlueStacks_nxt/bluestacks.conf"
adb_port_key = "bst.instance.Pie64.status.adb_port"

class VirtualDevice(Device):
	def __init__(self) -> None:
		super().__init__()
		self.read_adb_port()

	def init(self) -> (AdbClient, AdbDevice):
		self.adb_client = adb
		serial_number = f"localhost:{self.adb_port}"
		self.adb_client.connect(serial_number)
		self.adb_device = self.adb_client.device(serial_number)
		return self.adb_client, self.adb_device

	def read_adb_port(self):
		with open(bluestacks_config_path, 'r') as file:
			lines = file.readlines()
			for line in lines:
				if not line.startswith(adb_port_key):
					continue
				self.adb_port = int(line.split('"')[1])
				return