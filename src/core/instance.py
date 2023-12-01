from pymitter import EventEmitter
from threading import Thread
from bot.bot import Bot
from core.android import Android
from config.commands import Commands
import time
import cv2
from _logging import setup_logger, logging
import os


class Instance(Thread):
    def __init__(
        self,
        bluestacks_app_path: str,
        bluestacks_conf_path: str,
        bluestacks_sharedFolder_path: str,
        bluestacks_instance_name: str,
        minitouch_port: int,
        instance_index: int,
        instance_config: dict,
        event_emitter: EventEmitter,
    ) -> None:
        self.bluestacks_instance_name = bluestacks_instance_name
        self.logger = setup_logger(
            f"acb.{instance_index}.{self.bluestacks_instance_name}",
            os.path.join(
                __file__,
                f"../../../logs/{self.bluestacks_instance_name}.log"
            ),
            None,
            logging.DEBUG
        )
        self.bluestacks_app_path = bluestacks_app_path
        self.bluestacks_conf_path = bluestacks_conf_path
        self.bluestacks_sharedFolder_path = bluestacks_sharedFolder_path
        self.minitouch_port = minitouch_port
        self.instance_index = instance_index
        self.instance_config = instance_config
        self.event_emitter = event_emitter
        self.init_events()
        Thread.__init__(self)

    def run(self) -> None:
        time.sleep(self.instance_index * 10)
        self.android = Android(
            self.bluestacks_app_path,
            self.bluestacks_conf_path,
            self.bluestacks_sharedFolder_path,
            self.bluestacks_instance_name,
            self.minitouch_port
        )
        self.android.initialize()
        self.bot = Bot(self.logger, self.android)
        self.bot.run()

    def init_events(self) -> None:
        self.event_emitter.on(
            f"{self.instance_index}:{Commands.CloseInstance.value}",
            self.on_close_instance
        )
        self.event_emitter.on(
            f"{self.instance_index}:{Commands.Screenshot.value}",
            self.on_screenshot
        )

    def on_close_instance(self, _) -> None:
        print("Shutdown")

    def on_screenshot(self, path) -> None:
        screenshot = self.android.get_screenshot()
        cv2.imwrite(path, screenshot)
