from core.bluestacks import Bluestacks
from core.minitouch import Minitouch
import numpy as np
import time

package_name = "com.supercell.clashofclans"


class Android:
    def __init__(
        self,
        bluestacks_app_path: str,
        bluestacks_conf_path: str,
        bluestacks_sharedFolder_path: str,
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

    def get_screenshot(self) -> np.ndarray:
        pillow_image = self.adb_device.screenshot().convert("RGB")
        open_cv_image = np.array(pillow_image)
        open_cv_image = open_cv_image[:, :, ::-1].copy()
        return open_cv_image

    def zoom_out(self) -> None:
        max_x, max_y = self.minitouch.screen_size
        left_finger_point_x, left_finger_point_y = self.minitouch.transform(
            max_x * 0.1, max_y * 0.5)

        self.minitouch.send_minitouch_command(
            f"d 1 {left_finger_point_x} {left_finger_point_y} {self.minitouch.default_pressure}\n")
        self.minitouch.send_minitouch_command("c\n")
        self.minitouch.swipe_along(
            [(max_x * 0.9, max_y * 0.5), (max_x * 0.2, max_y * 0.5)],
            3,
            20,
        )
        self.minitouch.send_minitouch_command("u 1\n")
        self.minitouch.send_minitouch_command("c\n")
        time.sleep(0.5)
        self.minitouch.swipe_along([(int(max_x * 0.2), int(max_y * 0.2)),
                                    (int(max_x * 0.8), int(max_y * 0.8))])
