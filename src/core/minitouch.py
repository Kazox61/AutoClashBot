from logging import getLogger
import socket
import time
from core.bluestacks import Bluestacks
from adbutils import AdbDevice
import subprocess
from utils import add_screen_noise

minitouch_source_path = "../files/minitouch/x86/minitouch"
minitouch_destination_path = "/data/local/tmp"


class Minitouch:
    def __init__(self, minitouch_port: int):
        self.minitouch_port = minitouch_port
        self.minitouch_client: socket.socket = socket.socket(
            socket.AF_INET, socket.SOCK_STREAM)
        self.default_pressure = 50
        self.logger = getLogger("acb.core")

    def setup(self, adb_device: AdbDevice, bluestacks: Bluestacks):
        self.adb_device = adb_device
        self.bluestacks = bluestacks
        self.screen_size: tuple[int, int] = self.bluestacks.get_screen_size()
        if not self.has_mini_touch():
            self.install()

        self.start_server()

    def has_mini_touch(self) -> bool:
        output = self.adb_device.shell(f"ls {minitouch_destination_path}")
        return "minitouch" in output

    def install(self) -> None:
        self.logger.debug("Try to push Minitouch File to the Device.")
        self.adb_device.push(minitouch_source_path, minitouch_destination_path)
        self.adb_device.shell(
            f"chmod 755 {minitouch_destination_path}/minitouch")
        self.logger.debug("Minitouch File pushed to the Device.")

    def start_server(self) -> None:
        self.logger.info("MiniTouch starting")

        self.adb_device.forward(
            f"tcp:{self.minitouch_port}", f"localabstract:minitouch_{self.minitouch_port}")
        self.minitouch_process = subprocess.Popen(
            f"adb -s {self.adb_device.serial} shell {minitouch_destination_path}/minitouch -n minitouch_{self.minitouch_port} 2>&1",
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            start_new_session=True
        )
        time.sleep(1)
        self.logger.info("MiniTouch Server started")

        self.minitouch_client.connect(("localhost", self.minitouch_port))
        self.minitouch_client.settimeout(2)
        header = b""

        while True:
            try:
                header += self.minitouch_client.recv(4096)
            except self.minitouch_client.timeout:
                self.logger.error("minitouch header not recved")
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
        self.logger.info(
            f"Minitouch Client started with Minitouch-Version: {self.minitouch_version}, Pid: {self.pid}, Max-Contacts: {self.max_contacts}, Max-X: {self.max_x}, Max-Y: {self.max_y}, Max-Pressure: {self.max_pressure}")

    def send_minitouch_command(self, command: str) -> None:
        self.minitouch_client.sendall(command.encode())

    def transform(self, x, y, randomness: bool = True) -> (int, int):
        screen_x, screen_y = self.screen_size
        tx = int(x / screen_x * self.max_x)
        ty = int(y / screen_y * self.max_y)
        if randomness:
            tx, ty = add_screen_noise((tx, ty), (self.max_x, self.max_y))
        return tx, ty

    def touch(self, x: int, y: int, duration: float = 0.1, randomness: bool = True) -> None:
        x, y = self.transform(x, y, randomness)
        self.send_minitouch_command(f"d 0 {x} {y} {self.default_pressure}\n")
        self.send_minitouch_command("c\n")
        time.sleep(duration)
        self.send_minitouch_command("u 0\n")
        self.send_minitouch_command("c\n")

    def swipe_move(self, start, end, duration=1, steps=5) -> None:
        sx, sy = start
        ex, ey = end
        step_x = (ex - sx) / steps
        step_y = (ey - sy) / steps
        step_duration = duration / steps
        for step in range(1, steps):
            x, y = add_screen_noise(
                (sx + step * step_x, sy + step * step_y),
                (self.max_x, self.max_y)
            )
            self.send_minitouch_command(
                f"m 0 {x} {y} {self.default_pressure}\n")
            self.send_minitouch_command("c\n")
            time.sleep(step_duration)

    def swipe_along(self, points, duration=1, steps_per_move=5, first_sleep_duration=0.1) -> None:
        for i in range(len(points)-1):
            start_point = points[i]
            end_point = points[i+1]
            sx, sy = self.transform(start_point[0], start_point[1], False)
            ex, ey = self.transform(end_point[0], end_point[1], False)
            if i == 0:
                x, y = add_screen_noise((sx, sy), (self.max_x, self.max_y))
                self.send_minitouch_command(
                    f"d 0 {x} {y} {self.default_pressure}\n")
                self.send_minitouch_command("c\n")
                time.sleep(first_sleep_duration)
            self.swipe_move((sx, sy), (ex, ey), duration, steps_per_move)
        self.send_minitouch_command("u 0\n")
        self.send_minitouch_command("c\n")

    def zoom_out(self) -> None:
        self.zoom_out_horizontal(0.25)
        self.zoom_out_vertical(0.25)
        self.zoom_out_horizontal(0.75)
        self.zoom_out_vertical(0.75)
        max_x, max_y = self.screen_size
        self.swipe_along([(int(max_x * 0.5), int(max_y * 0.2)),
                         (int(max_x * 0.5), int(max_y * 0.8))])

    def zoom_out_horizontal(self, pos_nx) -> None:
        steps = 5
        step_amount = self.max_y / (steps * 2)
        for step in range(steps):
            command_type = "d" if step == 0 else "m"
            self.send_minitouch_command(
                f"{command_type} 0 {int(self.max_x * pos_nx)} {int(step_amount * (step+1))} {self.default_pressure}\n")
            self.send_minitouch_command(
                f"{command_type} 1 {int(self.max_x * pos_nx)} {int(self.max_y - step_amount * (step+1))} {self.default_pressure}\n")
            self.send_minitouch_command("c\n")
            time.sleep(0.2)
        self.send_minitouch_command("u 0\n")
        self.send_minitouch_command("u 1\n")
        self.send_minitouch_command("c\n")

    def zoom_out_vertical(self, pos_ny) -> None:
        steps = 5
        step_amount = self.max_x / (steps * 2)
        for step in range(steps):
            command_type = "d" if step == 0 else "m"
            self.send_minitouch_command(
                f"{command_type} 0 {int(step_amount * (step+1))} {int(self.max_y * pos_ny)} {self.default_pressure}\n")
            self.send_minitouch_command(
                f"{command_type} 1 {int(self.max_x - step_amount * (step+1))} {int(self.max_y * pos_ny)} {self.default_pressure}\n")
            self.send_minitouch_command("c\n")
            time.sleep(0.2)
        self.send_minitouch_command("u 0\n")
        self.send_minitouch_command("u 1\n")
        self.send_minitouch_command("c\n")
