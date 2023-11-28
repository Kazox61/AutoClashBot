from core.bluestacks import Bluestacks
from core.minitouch import Minitouch
import numpy as np


package_name = "com.supercell.clashofclans"


class Android:
    def __init__(
        self,
        bluestacks_app_path: str,
        bluestacks_config_path: str,
        bluestacks_display_name: str,
        minitouch_port: int

    ) -> None:
        self.bluestacks = Bluestacks(
            bluestacks_app_path,
            bluestacks_config_path,
            bluestacks_display_name
        )
        self.minitouch = Minitouch(minitouch_port)

    def initialize(self):
        self.adb_client, self.adb_device = self.bluestacks.start()
        self.minitouch.setup(self.adb_device, self.bluestacks)

    def start_app(self):
        self.adb_device.shell(f"monkey -p {package_name} 1")

    def stop_app(self):
        self.adb_device.shell(f"am force-stop {package_name}")

    def get_screenshot(self) -> np.ndarray:
        pillow_image = self.adb_device.screenshot().convert("RGB")
        open_cv_image = np.array(pillow_image)
        open_cv_image = open_cv_image[:, :, ::-1].copy()
        return open_cv_image
