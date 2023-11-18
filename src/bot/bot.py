from android import Android
import time
from logger import Logger
from bot.builder_base.fast_farm import FastFarm


class Bot:
	def __init__(self, android: Android):
		self._android = android
		self._fast_farm = FastFarm(android)

	def process(self):
		Logger.info("Start Clash of Clans App")
		self._android.start_app()
		time.sleep(10)

	def _loop(self):
		self._fast_farm.loop()


