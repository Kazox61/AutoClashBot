from core.net import ServerThread, event_emitter
from core.config import ConfigCore
from core.instance import Instance
from _logging import setup_logger, logging
import os

if __name__ == "__main__":
    logger = setup_logger(
        "acb.core",
        os.path.join(__file__, "../../logs/core.log"),
        None,
        logging.DEBUG
    )

    server = ServerThread("localhost", 9339)
    server.start()

    config = ConfigCore.get_config()
    for i, instance_config in enumerate(config):
        instance = Instance(event_emitter, i, instance_config)
        instance.start()
