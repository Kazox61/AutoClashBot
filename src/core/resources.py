from core.config import ConfigCore
from logger import Logger
from core import android_factory
from bot.bot import Bot
import threading


def construct():
	Logger.init()
	Logger.info("Logger initialized. Logger can be used now")

	Logger.info("Start constructing Resources")
	config = ConfigCore.get_config()
	for instance_config in config:
		android = android_factory.build(instance_config)
		Logger.info("AndroidFactory built an instance of android")
		android.init(instance_config)
		Logger.info("Android initialized")

		bot = Bot(android)
		thread = threading.Thread(target=bot.process)
		thread.start()

