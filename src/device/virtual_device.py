from device.device import Device
from ppadb.device import Device as AdbDevice

bluestacks_config_path = "C:/ProgramData/BlueStacks_nxt/bluestacks.conf"
adb_port_key = "bst.instance.Pie64.status.adb_port"

class VirtualDevice(Device):
	def __init__(self) -> None:
		super().__init__()
		self.read_adb_port()
	
	def create_adb_device(self) -> AdbDevice:
		self.adb_client.remote_connect("localhost", self.adb_port)
		self.abd_device = self.adb_client.device(f"localhost:{self.adb_port}")
		return self.abd_device

	def read_adb_port(self):
		with open(bluestacks_config_path, 'r') as file:
			lines = file.readlines()
			for line in lines:
				if not line.startswith(adb_port_key):
					continue
				self.adb_port = int(line.split('"')[1])
				print(self.adb_port)
				return