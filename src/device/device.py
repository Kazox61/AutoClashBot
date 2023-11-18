import cv2
import numpy as np
import subprocess
from ppadb.client import Client as AdbClient
from ppadb.device import Device as AdbDevice


class Device:
	adb_device: AdbDevice

	def start_adb_server(self):
		subprocess.run("adb start-server", shell=True, capture_output=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

	def stop_adb_server(self):
		subprocess.run("adb kill-server", shell=True, capture_output=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

	def create_adb_client(self) -> AdbClient:
		self.adb_client = AdbClient(host="127.0.0.1", port=5037)
		return self.adb_client
	
	def create_adb_device(self) -> AdbDevice:
		self.abd_device = self.adb_client.devices()[0]
		return self.abd_device

	def get_screenshot(self):
		byte_array = self.adb_device.screencap()
		np_array = np.asarray(byte_array, dtype=np.uint8)
		return cv2.imdecode(np_array, cv2.IMREAD_COLOR)
