from touch_input.touch_input import TouchInput
from logger import Logger
import socket
import time
from adbutils import AdbDevice, AdbConnection
import subprocess

minitouch_source_path = "../files/minitouch"
minitouch_destination_path = "/data/local/tmp"
minitouch_port = 12345


class MiniTouch(TouchInput):
	def __init__(self):
		self._minitouch_client: socket.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.default_pressure = 50

	def init(self, adb_device: AdbDevice, device):
		super().init(adb_device, device)

		if not self._has_mini_touch():
			self._install()

		self._start_server()

	def _has_mini_touch(self) -> bool:
		output = self.adb_device.shell(f"ls {minitouch_destination_path}")
		return "minitouch" in output

	def _install(self):
		self.adb_device.push(minitouch_source_path, minitouch_destination_path)
		self.adb_device.shell(f"chmod 755 {minitouch_destination_path}/minitouch")

	def _start_server(self):
		Logger.info("MiniTouch starting")

		self.adb_device.forward(f"tcp:{minitouch_port}", f"localabstract:minitouch_{minitouch_port}")
		self.minitouch_process = subprocess.Popen(
			f"{minitouch_destination_path}/minitouch -n minitouch_{minitouch_port} 2>&1",
			shell=True, stdout=subprocess.PIPE, 
			stderr=subprocess.PIPE, 
			start_new_session=True
		)
		time.sleep(1)
		Logger.info("MiniTouch Server started")

		self._minitouch_client.connect(("localhost", minitouch_port))
		self._minitouch_client.settimeout(2)
		header = b""

		while True:
			try:
				header += self._minitouch_client.recv(4096)
			except self._minitouch_client.timeout:
				Logger.error("minitouch header not recved")
				break
			if header.count(b'\n') >= 3:
				break
		header = header.decode()
		lines = header.splitlines()
		self.minitouch_version = lines[0][2:]
		minitouch_device_infos = lines[1].split(" ")
		self.max_contacts = int(minitouch_device_infos[1])
		self.max_x = int(minitouch_device_infos[2])
		self.max_y = int(minitouch_device_infos[3])
		self.max_pressure = int(minitouch_device_infos[4])
		self.pid = int(lines[2][2:])
		Logger.info(f"Minitouch Client started with Minitouch-Version: {self.minitouch_version}, Pid: {self.pid}, Max-Contacts: {self.max_contacts}, Max-X: {self.max_x}, Max-Y: {self.max_y}, Max-Pressure: {self.max_pressure}")

	def _send_minitouch_command(self, command: str):
		self._minitouch_client.sendall(command.encode())


	def _transform(self, x, y) -> (int, int):
		screen_x, screen_y = self.device.get_screen_size()
		return int(x / screen_x * self.max_x), int(y / screen_y * self.max_y)
	
	def touch(self, x: int, y: int, duration: float):
		x, y = self._transform(x, y)
		self._send_minitouch_command(f"d 0 {x} {y} {self.default_pressure}\n")
		self._send_minitouch_command("c\n")
		time.sleep(duration)
		self._send_minitouch_command("u 0\n")
		self._send_minitouch_command("c\n")

	def _swipe_move(self, start, end, duration=1, steps=5):
		sx, sy = start
		ex, ey = end
		step_x = (ex - sx) / steps
		step_y = (ey - sy) / steps
		step_duration = duration / steps
		for step in range(1, steps):
			self._send_minitouch_command(f"m 0 {int(sx + step * step_x)} {int(sy + step * step_y)} {self.default_pressure}\n")
			self._send_minitouch_command("c\n")
			time.sleep(step_duration)

	def swipe_along(self, points, duration=1, steps_per_move=5):
		for i in range(len(points)-1):
			start_point = points[i]
			end_point = points[i+1]
			sx, sy = self._transform(start_point[0], start_point[1])
			ex, ey = self._transform(end_point[0], end_point[1])
			if i == 0:
				self._send_minitouch_command(f"d 0 {sx} {sy} {self.default_pressure}\n")
				self._send_minitouch_command("c\n")
				time.sleep(0.1)
			self._swipe_move((sx, sy), (ex, ey), duration, steps_per_move)
		self._send_minitouch_command("u 0\n")
		self._send_minitouch_command("c\n")
	
	def zoom_out(self):
		self._zoom_out_horizontal(0.25)
		self._zoom_out_vertical(0.25)
		self._zoom_out_horizontal(0.75)
		self._zoom_out_vertical(0.75)
		max_x, max_y = self.device.get_screen_size()
		self.swipe_along([(int(max_x * 0.5), int(max_y * 0.2)), (int(max_x * 0.5), int(max_y * 0.8))])

	def _zoom_out_horizontal(self, pos_nx):
		steps = 5
		step_amount = self.max_y / (steps * 2)
		for step in range(steps):
			command_type = "d" if step == 0 else "m"
			self._send_minitouch_command(f"{command_type} 0 {int(self.max_x * pos_nx)} {int(step_amount * (step+1))} {self.default_pressure}\n")
			self._send_minitouch_command(f"{command_type} 1 {int(self.max_x * pos_nx)} {int(self.max_y - step_amount * (step+1))} {self.default_pressure}\n")
			self._send_minitouch_command("c\n")
			time.sleep(0.2)
		self._send_minitouch_command("u 0\n")
		self._send_minitouch_command("u 1\n")
		self._send_minitouch_command("c\n")

	def _zoom_out_vertical(self, pos_ny):
		steps = 5
		step_amount = self.max_x / (steps * 2)
		for step in range(steps):
			command_type = "d" if step == 0 else "m"
			self._send_minitouch_command(f"{command_type} 0 {int(step_amount * (step+1))} {int(self.max_y * pos_ny)} {self.default_pressure}\n")
			self._send_minitouch_command(f"{command_type} 1 {int(self.max_x - step_amount * (step+1))} {int(self.max_y * pos_ny)} {self.default_pressure}\n")
			self._send_minitouch_command("c\n")
			time.sleep(0.2)
		self._send_minitouch_command("u 0\n")
		self._send_minitouch_command("u 1\n")
		self._send_minitouch_command("c\n")
	

