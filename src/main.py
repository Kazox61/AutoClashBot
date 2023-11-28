from core.networking import ServerThread, event_emitter
from config.config import ConfigCore
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
    bluestacks_app_path = config['bluestacksAppPath']
    bluestacks_config_path = config['bluestacksConfigPath']
    minitouch_start_port = config['minitouchStartPort']
    for index, instance_config in enumerate(config['instances']):
        minitouch_port = minitouch_start_port + index
        instance = Instance(
            bluestacks_app_path,
            bluestacks_config_path,
            minitouch_port,
            index,
            instance_config,
            event_emitter
        )
        instance.start()
