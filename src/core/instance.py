from pymitter import EventEmitter
from threading import Thread
from core import android_factory
from bot.bot import Bot
from config.commands import Commands
import time
import cv2
from _logging import setup_logger, logging
import os


class Instance(Thread):
    def __init__(self, event_emitter: EventEmitter, instance_index: int, instance_config: dict) -> None:
        self.logger = setup_logger(
            f"acb.{instance_config['bluestacksInstance']}",
            os.path.join(
                __file__,
                f"../../../logs/{instance_config['bluestacksInstance']}.log"
            ),
            None,
            logging.DEBUG
        )
        self.event_emitter = event_emitter
        self.instance_index = instance_index
        self.instance_config = instance_config
        self.init_events()
        Thread.__init__(self)

    def run(self) -> None:
        time.sleep(self.instance_index * 10)
        self.android = android_factory.build(self.instance_config)
        self.android.init(self.instance_config)
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
