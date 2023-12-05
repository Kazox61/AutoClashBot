from core.bluestacks import Bluestacks
from core.minitouch import Minitouch
import numpy as np
import time
from pathlib import Path

package_name = "com.supercell.clashofclans"


class Android:
    def __init__(
        self,
        bluestacks_app_path: Path,
        bluestacks_conf_path: Path,
        bluestacks_sharedFolder_path: Path,
        bluestacks_instance_name: str,
        minitouch_port: int

    ) -> None:
        self.bluestacks = Bluestacks(
            bluestacks_app_path,
            bluestacks_conf_path,
            bluestacks_sharedFolder_path,
            bluestacks_instance_name
        )
        self.minitouch = Minitouch(minitouch_port)

    def initialize(self):
        self.adb_client, self.adb_device = self.bluestacks.start()
        self.minitouch.setup(self.adb_device, self.bluestacks)

    def start_app(self):
        self.adb_device.shell(f"monkey -p {package_name} 1")

    def stop_app(self):
        self.adb_device.shell(f"am force-stop {package_name}")

    def kill(self) -> None:
        self.minitouch.minitouch_client.close()
        self.bluestacks.application.kill()

    def get_screenshot(self) -> np.ndarray:
        pillow_image = self.adb_device.screenshot().convert("RGB")
        open_cv_image = np.array(pillow_image)
        open_cv_image = open_cv_image[:, :, ::-1].copy()
        return open_cv_image
