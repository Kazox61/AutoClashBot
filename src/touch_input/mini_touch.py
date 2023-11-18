from touch_input.touch_input import TouchInput
from logger import Logger
import socket
import time

minitouch_source_path = "../files/minitouch"
minitouch_destination_path = "/data/local/tmp"
minitouch_port = 12345


class MiniTouch(TouchInput):
	def __init__(self):
		self._minitouch_client: socket.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

	def init(self, adb_device):
		super().init(adb_device)

		if not self._has_mini_touch():
			self._push_minitouch()

		self._start_minitouch_server()

	def _has_mini_touch(self) -> bool:
		output = self._adb_device.shell(f"ls {minitouch_destination_path}")
		print(output)
		return "minitouch" in output

	def _push_minitouch(self):
		print("Push minitouch")
		self._adb_device.push(minitouch_source_path, minitouch_destination_path)

	def _start_minitouch_server(self):
		Logger.info("MiniTouch starting")
		#self._adb_device.shell(f"./{minitouch_destination_path}/minitouch > /dev/null 2>&1 &")
		Logger.info("MiniTouch started")
		self._adb_device.forward(f"tcp:{minitouch_port}", "minitouch")

		self._minitouch_client.connect(("127.0.0.1", minitouch_port))

	def _send_minitouch_command(self, command: str):
		self._minitouch_client.sendall(command.encode())

	def touch(self, x: int, y: int, duration: float):
		self._send_minitouch_command(f"d 0 {x} {y} 50\n")
		self._send_minitouch_command("c\n")
		time.sleep(duration)
		self._send_minitouch_command("u 0\n")
		self._send_minitouch_command("c\n")
