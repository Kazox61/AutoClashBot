import re
from adbutils import adb, AdbClient, AdbDevice
from pywinauto.application import Application
import time
from logging import getLogger
import os
import cv2
from pathlib import Path
import numpy as np

remote_sharedFolder_path = Path("/mnt/windows/BstSharedFolder")
shared_prefs_path = Path("/data/data/com.supercell.clashofclans/shared_prefs")


class Bluestacks:
    def __init__(
        self,
        app_path: Path,
        conf_path: Path,
        sharedFolder_path: Path,
        instance_name: str
    ) -> None:
        self.app_path = app_path
        self.conf_path = conf_path
        self.sharedFolder_path = sharedFolder_path
        self.instance_name = instance_name

    def setup(self):

        os.makedirs(self.sharedFolder_path.as_posix(), exist_ok=True)
        """
        self.set_global_config_values({
            "rooting": "1",
            "create_desktop_shortcuts": "0"
        })"""
        self.set_instance_config_values({
            "enable_root_access": "1",
            "fb_width": "800",
            "fb_height": "600",
            "dpi": "240",
            "show_sidebar": "0",
            "display_name": f"acb-{self.instance_name}",
            "enable_fps_display": "1",
            "google_login_popup_shown": "0"
        })

    def start(self) -> (AdbClient, AdbDevice):
        self.setup()
        self.start_virtual_device()
        time.sleep(10)
        self.adb_port = self.get_config_value("status.adb_port")

        self.adb_client = adb
        serial_number = f"localhost:{self.adb_port}"
        self.adb_client.disconnect(serial_number)
        time.sleep(1)
        self.adb_client.connect(serial_number)
        self.adb_device = self.adb_client.device(serial_number)
        self.adb_device.root()
        time.sleep(4)
        return self.adb_client, self.adb_device

    def start_virtual_device(self) -> None:
        getLogger("acb.core").info(
            f"Starting Bluestacks:{self.instance_name}")
        self.application = Application().start(
            f"{self.app_path.as_posix()} --instance {self.instance_name}")

    def get_screen_size(self) -> tuple[int, int]:
        output: str = self.adb_device.shell(
            'dumpsys window | grep cur= |tr -s " " | cut -d " " -f 4|cut -d "=" -f 2')
        screen_width, screen_height = output.strip().split("x")
        return int(screen_width), int(screen_height)

    def set_global_config_values(self, config_values: dict) -> None:
        with open(self.conf_path.as_posix(), 'r') as file:
            text = file.read()

        for key, value in config_values.items():
            text = re.sub(
                r"bst\.{}=\"([^.]*)\"".format(
                    re.escape(key)
                ),
                'bst.{}="{}"'.format(
                    key,
                    value
                ),
                text,
                1
            )

        with open(self.conf_path.as_posix(), 'w') as file:
            file.write(text)

    def set_instance_config_values(self, config_values: dict) -> None:
        with open(self.conf_path.as_posix(), 'r') as file:
            text = file.read()

        for key, value in config_values.items():
            text = re.sub(
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

        with open(self.conf_path.as_posix(), 'w') as file:
            file.write(text)

    def get_config_value(self, key: str) -> str:
        with open(self.conf_path.as_posix(), 'r') as file:
            text = file.read()
            return re.search(
                r"bst\.instance\.{}\.{}=\"([^.]*)\"".format(
                    re.escape(self.instance_name),
                    re.escape(key),
                ),
                text
            ).group(1)

    def pull_shared_prefs(self, profile_name: str) -> None:
        os.makedirs(self.sharedFolder_path.joinpath("acb_profiles").joinpath(
            profile_name).as_posix(), exist_ok=True)
        remote_profile_path = remote_sharedFolder_path.joinpath("acb_profiles").joinpath(
            profile_name).joinpath("shared_prefs")
        self.adb_device.shell(["su",
                               "-c",
                               f"cp -r {shared_prefs_path.as_posix()} {remote_profile_path.as_posix()}"
                               ])

    def push_shared_prefs(self, profile_name: str) -> None:
        remote_profile_path = remote_sharedFolder_path.joinpath("acb_profiles").joinpath(
            profile_name).joinpath("shared_prefs")
        self.adb_device.shell(["su",
                               "-c",
                               f"cp -r {remote_profile_path.as_posix()+'/.'} {shared_prefs_path.as_posix()}"
                               ])
