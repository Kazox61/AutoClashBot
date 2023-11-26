from core.android import Android
import time
from logger import Logger
from bot.fast_farm import FastFarm


class Bot:
	def __init__(self, android: Android):
		self._android = android
		self._fast_farm = FastFarm(android)

	def _start(self):
		Logger.info("Start Clash of Clans App")
		self._android.start_app()
		time.sleep(10)
		self._android.touch_input.zoom_out()

	def process(self):
		self._start()
		while True:
			self._loop()

	def _loop(self):
		self._fast_farm.loop()


