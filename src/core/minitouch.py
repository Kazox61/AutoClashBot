from logging import Logger
from core import instance
import socket
import time
from core.bluestacks import Bluestacks
from adbutils import AdbDevice
import subprocess
from utils import add_screen_noise


class MotionEvent:
    def getcmd(self, transform=None) -> str:
        raise NotImplementedError


class DownEvent(MotionEvent):
    def __init__(self, coordinates: tuple[int, int], contact: int = 0, pressure: int = 50) -> None:
        super().__init__()
        self.coordinates = coordinates
        self.contact = contact
        self.pressure = pressure

    def getcmd(self) -> str:
        x, y = self.coordinates
        return f"d {self.contact} {x} {y} {self.pressure}\nc\n"


class UpEvent(MotionEvent):
    def __init__(self, contact: int = 0) -> None:
        super().__init__()
        self.contact = contact

    def getcmd(self, transform=None) -> str:
        return f"u {self.contact}\nc\n"


class MoveEvent(MotionEvent):
    def __init__(self, coordinates: tuple[int, int], contact: int = 0, pressure: int = 50) -> None:
        super().__init__()
        self.coordinates = coordinates
        self.contact = contact
        self.pressure = pressure

    def getcmd(self) -> str:
        x, y = self.coordinates
        return f"m {self.contact} {x} {y} {self.pressure}\nc\n"


class SleepEvent(MotionEvent):
    def __init__(self, seconds) -> None:
        super().__init__()
        self.seconds = seconds

    def getcmd(self, transform=None) -> str:
        return None


minitouch_source_path = "../files/minitouch/x86/minitouch"
minitouch_destination_path = "/data/local/tmp"


class Minitouch:
    def __init__(self, minitouch_port: int):
        self.minitouch_port = minitouch_port
        self.minitouch_client: socket.socket = socket.socket(
            socket.AF_INET, socket.SOCK_STREAM)
        self.default_pressure = 50
        self.logger = instance.thread_storage.logger

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
        self.logger.info(
            f"MiniTouch Server started on Port {self.minitouch_port}")

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

    def perform(self, motion_events: list[MotionEvent], interval: float = 0.0) -> None:
        for event in motion_events:
            if isinstance(event, SleepEvent):
                time.sleep(event.seconds)
            else:
                cmd = event.getcmd()
                self.send_minitouch_command(cmd)
                time.sleep(interval)

    def touch(self, x: int, y: int, duration: float = 0.1, contact: int = 0, randomness: bool = True) -> None:
        x, y = self.transform(x, y, randomness)
        events = [
            DownEvent((x, y), contact, self.default_pressure),
            SleepEvent(duration),
            UpEvent()
        ]
        self.perform(events)

    def __swipe_move(self, start, end, duration=1, steps=5) -> list[MotionEvent]:
        sx, sy = start
        ex, ey = end
        step_x = (ex - sx) / steps
        step_y = (ey - sy) / steps
        step_duration = duration / steps
        events = []
        for step in range(1, steps):
            x, y = add_screen_noise(
                (sx + step * step_x, sy + step * step_y),
                (self.max_x, self.max_y)
            )
            events.append(MoveEvent((x, y), pressure=self.default_pressure))
            events.append(SleepEvent(step_duration))
        x, y = add_screen_noise(
            (ex, ey),
            (self.max_x, self.max_y)
        )
        events.append(MoveEvent((x, y), pressure=self.default_pressure))
        events.append(SleepEvent(step_duration))
        return events

    def swipe_along(self, points, duration=1, steps_per_move=5, first_sleep_duration=0.1) -> None:
        sxy = self.transform(points[0][0], points[0][1])
        events = [DownEvent(
            sxy, pressure=self.default_pressure), SleepEvent(first_sleep_duration)]
        for point in points[1:]:
            # randomnes is False, because noise will be added in swipe_move
            exy = self.transform(point[0], point[1], False)
            events.extend(self.__swipe_move(sxy,
                                            exy, duration=duration, steps=steps_per_move))
            sxy = exy

        events.append(UpEvent())
        self.perform(events)

    def two_finger_swipe(
            self,
            start_finger1,
            end_finger1,
            start_finger2,
            end_finger2,
            duration=1,
            steps=5
    ) -> None:
        sxy1 = self.transform(start_finger1[0], start_finger1[1], False)
        exy1 = self.transform(end_finger1[0], end_finger1[1], False)
        sxy2 = self.transform(start_finger2[0], start_finger2[1], False)
        exy2 = self.transform(end_finger2[0], end_finger2[1], False)

        events = [DownEvent(sxy1, 0, self.default_pressure),
                  DownEvent(sxy2, 1, self.default_pressure)]

        sx1, sy1 = sxy1
        sx2, sy2 = sxy2
        ex1, ey1 = exy1
        ex2, ey2 = exy2

        step_x1 = (ex1 - sx1) / steps
        step_x2 = (ex2 - sx2) / steps
        step_y1 = (ey1 - sy1) / steps
        step_y2 = (ey2 - sy2) / steps
        step_duration = duration / steps
        for step in range(1, steps+1):
            x1, y1 = add_screen_noise(
                (sx1 + step * step_x1, sy1 + step * step_y1),
                (self.max_x, self.max_y)
            )
            x2, y2 = add_screen_noise(
                (sx2 + step * step_x2, sy2 + step * step_y2),
                (self.max_x, self.max_y)
            )
            events.append(MoveEvent((x1, y1), 0, self.default_pressure))
            events.append(MoveEvent((x2, y2), 1, self.default_pressure))
            events.append(SleepEvent(step_duration))
        x1, y1 = add_screen_noise(
            (ex1, ey1),
            (self.max_x, self.max_y)
        )
        x2, y2 = add_screen_noise(
            (ex2, ey2),
            (self.max_x, self.max_y)
        )
        events.append(UpEvent(0))
        events.append(UpEvent(1))
        self.perform(events)
