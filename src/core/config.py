import json


class ConfigCore:
	config = {}

	@classmethod
	def load(cls):
		with open('../configuration.json') as fd:
			cls.config = json.load(fd)

	@classmethod
	def get_config(cls):
		if cls.config == {}:
			ConfigCore.load()
		return cls.config
