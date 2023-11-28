from core.android import Android
import time
from logging import Logger
from bot.fast_farm import FastFarm


class Bot:
    def __init__(self, logger: Logger, android: Android):
        self.logger = logger
        self.android = android
        self.fast_farm = FastFarm(self.logger, self.android)

    def start(self):
        self.logger.info("Start Clash of Clans App")
        self.android.start_app()
        time.sleep(10)
        self.android.touch_input.zoom_out()

    def run(self):
        self.start()
        while True:
            self.loop()

    def loop(self):
        self.fast_farm.loop()
