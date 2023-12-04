from core.networking import ServerThread, event_emitter
from config.config import ConfigCore
from core.instance import Instance
from _logging import setup_logger, logging
import os
import re
from pathlib import Path


def get_instance_names(conf_path) -> list[str]:
    with open(conf_path, 'r') as file:
        text = file.read()
        instance_names = re.findall(
            r"bst\.instance\.([^.]+)\.abi_list", text)
        return instance_names


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

    instance_names = get_instance_names(config['bluestacksConfPath'])

    bluestacks_app_path = Path(config['bluestacksAppPath'])
    bluestacks_conf_path = Path(config['bluestacksConfPath'])
    bluestacks_sharedFolder_path = Path(config['bluestacksSharedFolderPath'])
    minitouch_start_port = config['minitouchStartPort']

    for index, instance_config in enumerate(config['instances']):
        # just +1 because i don t want to use currently the first Instance, @TODO: Check if there are enough instances available
        instance_name = instance_names[index]
        minitouch_port = minitouch_start_port + index
        instance = Instance(
            bluestacks_app_path,
            bluestacks_conf_path,
            bluestacks_sharedFolder_path,
            instance_name,
            minitouch_port,
            index,
            instance_config,
            event_emitter
        )
        instance.start()
