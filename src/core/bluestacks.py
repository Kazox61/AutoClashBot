import re
from adbutils import adb, AdbClient, AdbDevice
from pywinauto.application import Application
import time
from logging import getLogger
import os
import cv2
from pathlib import Path
import numpy as np

remote_sharedFolder_path = "/mnt/windows/BstSharedFolder/"


class Bluestacks:
    def __init__(
        self,
        app_path: str,
        conf_path: str,
        sharedFolder_path: str,
        instance_name: str
    ) -> None:
        self.app_path = app_path
        self.conf_path = conf_path
        self.sharedFolder_path = Path(
            sharedFolder_path).joinpath(instance_name)
        self.remote_sharedFolder_path = Path(
            remote_sharedFolder_path).joinpath(instance_name)
        self.instance_name = instance_name

    def setup(self):
        os.makedirs(self.sharedFolder_path, exist_ok=True)
        self.set_config_value("fb_width", "800")
        self.set_config_value("fb_height", "600")
        self.set_config_value("dpi", "240")
        self.set_config_value("show_sidebar", "0")
        self.set_config_value("display_name", f"acb-{self.instance_name}")
        self.set_config_value("enable_fps_display", "1")
        self.set_config_value("google_login_popup_shown", "0")

    def start(self) -> (AdbClient, AdbDevice):
        self.setup()
        self.start_virtual_device()
        time.sleep(10)
        self.adb_port = self.get_config_value("status.adb_port")

        self.adb_client = adb
        serial_number = f"localhost:{self.adb_port}"
        self.adb_client.connect(serial_number)
        self.adb_device = self.adb_client.device(serial_number)
        return self.adb_client, self.adb_device

    def start_virtual_device(self) -> None:
        getLogger("acb.core").info(
            f"Starting Bluestacks:{self.instance_name}")
        self.application = Application().start(
            f"{self.app_path} --instance {self.instance_name}")

    def close_virtual_device(self) -> None:
        self.application.kill()

    def get_screen_size(self) -> None:
        output: str = self.adb_device.shell(
            'dumpsys window | grep cur= |tr -s " " | cut -d " " -f 4|cut -d "=" -f 2')
        screen_width, screen_height = output.strip().split("x")
        return int(screen_width), int(screen_height)

    def screenshot(self) -> np.ndarray:
        image_name = "img_temp.png"
        self.adb_device.shell(
            f"screencap -p > {self.remote_sharedFolder_path.joinpath(image_name).as_posix()}")
        image_path = self.sharedFolder_path.joinpath(image_name).as_posix()
        return cv2.imread(image_path)

    def set_config_value(self, key: str, value: str) -> None:
        with open(self.conf_path, 'r') as file:
            text = file.read()

        new_text = re.sub(
            r"bst\.instance\.{}\.{}=\"([^.]*)\"".format(
                re.escape(self.instance_name),
                re.escape(key)
            ),
            'bst.instance.{}.{}="{}"'.format(
                self.instance_name,
                key,
                value
            ),
            text,
            1
        )

        with open(self.conf_path, 'w') as file:
            file.write(new_text)

    def get_config_value(self, key: str) -> str:
        with open(self.conf_path, 'r') as file:
            text = file.read()
            return re.search(
                r"bst\.instance\.{}\.{}=\"([^.]*)\"".format(
                    re.escape(self.instance_name),
                    re.escape(key),
                ),
                text
            ).group(1)
