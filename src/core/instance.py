from pymitter import EventEmitter
from threading import Thread
from core import android_factory
from bot.bot import Bot
from core.events import Events
import time


class Instance(Thread):
    def __init__(self, event_emitter: EventEmitter, instance_index: int, instance_config: dict) -> None:
        self.event_emitter = event_emitter
        self.instance_index = instance_index
        self.instance_config = instance_config
        self.init_events()
        Thread.__init__(self)

    def run(self) -> None:
        android = android_factory.build(self.instance_config)
        android.init(self.instance_config)
        bot = Bot(android)
        bot.run()

    def init_events(self) -> None:
        self.event_emitter.on(
            f"{self.instance_index}:{Events.CloseInstance.value}", self.on_close_instance)

    def on_close_instance(self, _) -> None:
        print("Shutdown")
