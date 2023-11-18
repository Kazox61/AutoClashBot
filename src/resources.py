from logger import Logger
import android_factory
from bot.bot import Bot
import threading


def construct():
	Logger.init()
	Logger.info("Logger initialized. Logger can be used now")

	Logger.info("Start constructing Resources")

	android = android_factory.build()
	Logger.info("AndroidFactory built an instance of android")
	android.init()
	Logger.info("Android initialized")

	bot = Bot(android)
	thread = threading.Thread(target=bot.process)
	thread.start()

