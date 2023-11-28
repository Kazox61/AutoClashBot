import re
from adbutils import adb, AdbClient, AdbDevice
from pywinauto.application import Application
import time
from logging import getLogger


class Bluestacks:
    def __init__(
        self,
        app_path: str,
        config_path: str,
        bluestacks_display_name: str
    ) -> None:
        self.app_path = app_path
        self.config_path = config_path
        self.bluestacks_display_name = bluestacks_display_name

    def setup_name(self):
        with open(self.config_path, 'r') as file:
            text = file.read()
            self.installed_image_name = re.search(
                r"bst\.instance\.([^.]+)\.display_name=\"{}\"".format(
                    re.escape(self.bluestacks_display_name)),
                text
            ).group(1)

    def setup_adb_port(self):
        with open(self.config_path, 'r') as file:
            text = file.read()
            adb_port = re.search(
                r"bst\.instance\.{}\.status\.adb_port=\"(\d+)\"".format(
                    re.escape(self.installed_image_name)),
                text
            ).group(1)
            self.adb_port = int(adb_port)

    def start(self) -> (AdbClient, AdbDevice):
        self.setup_name()
        self.start_virtual_device()
        time.sleep(10)
        self.setup_adb_port()

        self.adb_client = adb
        serial_number = f"localhost:{self.adb_port}"
        self.adb_client.connect(serial_number)
        self.adb_device = self.adb_client.device(serial_number)
        return self.adb_client, self.adb_device

    def start_virtual_device(self) -> None:
        getLogger("acb.core").info(
            f"Starting Bluestacks:{self.installed_image_name}")
        self.application = Application().start(
            f"{self.app_path} --instance {self.installed_image_name}")

    def close_virtual_device(self) -> None:
        self.application.kill()

    def get_screen_size(self) -> None:
        output: str = self.adb_device.shell(
            'dumpsys window | grep cur= |tr -s " " | cut -d " " -f 4|cut -d "=" -f 2')
        screen_width, screen_height = output.strip().split("x")
        return int(screen_width), int(screen_height)
