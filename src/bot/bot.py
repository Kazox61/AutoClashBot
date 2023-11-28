from core.android import Android
import time
from logging import Logger
from bot.home_village import HomeVillage


class Bot:
    def __init__(self, logger: Logger, android: Android):
        self.logger = logger
        self.android = android
        self.home_village = HomeVillage(self.logger, self.android)

    def start(self):
        self.logger.info("Start Clash of Clans App")
        self.android.start_app()
        time.sleep(10)
        self.android.minitouch.zoom_out()

    def run(self):
        self.start()
        while True:
            self.loop()

    def loop(self):
        self.home_village.loop()
