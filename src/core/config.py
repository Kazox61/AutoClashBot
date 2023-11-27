import json
import os.path


class ConfigCore:
    config = {}

    @classmethod
    def load(cls):
        with open(os.path.join(__file__, '../../../configuration.json')) as fd:
            cls.config = json.load(fd)

    @classmethod
    def get_config(cls):
        if cls.config == {}:
            ConfigCore.load()
        return cls.config
