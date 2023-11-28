from device.device import Device
from adbutils import adb, AdbClient, AdbDevice
from pywinauto.application import Application
import time
from logging import getLogger

bluestacks_app_path = "C:/Program Files/BlueStacks_nxt/HD-PLAYER.exe"
bluestacks_config_path = "C:/ProgramData/BlueStacks_nxt/bluestacks.conf"


class VirtualDevice(Device):
    def __init__(self) -> None:
        super().__init__()

    def start_virtual_device(self):
        getLogger("acb.core").info(f"Starting Bluestacks:{self.instance_name}")
        self.application = Application().start(
            f"{bluestacks_app_path} --instance {self.instance_name}")

    def close_virtual_device(self):
        self.application.kill()

    def init(self, instance_config: dict) -> (AdbClient, AdbDevice):
        self.instance_name = instance_config["bluestacksInstance"]
        self.adb_port_key = f"bst.instance.{self.instance_name}.status.adb_port"
        self.start_virtual_device()
        time.sleep(10)
        self.read_adb_port()
        self.adb_client = adb
        serial_number = f"localhost:{self.adb_port}"
        self.adb_client.connect(serial_number)
        self.adb_device = self.adb_client.device(serial_number)
        return self.adb_client, self.adb_device

    def read_adb_port(self):
        with open(bluestacks_config_path, 'r') as file:
            lines = file.readlines()
            for line in lines:
                if not line.startswith(self.adb_port_key):
                    continue
                self.adb_port = int(line.split('"')[1])
                return
