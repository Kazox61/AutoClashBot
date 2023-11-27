from core.net import ServerThread, event_emitter
from core.config import ConfigCore
from core.instance import Instance

if __name__ == "__main__":
    server = ServerThread("localhost", 9339)
    server.start()

    config = ConfigCore.get_config()
    for i, instance_config in enumerate(config):
        instance = Instance(event_emitter, i, instance_config)
        instance.start()
