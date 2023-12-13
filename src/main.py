from core.networking import ServerThread, event_emitter
from config.config import ConfigCore
from core.instance import Instance
from _logging import setup_logger, logging
import os
import re
from pathlib import Path
from config.commands import Commands
import time


def get_instance_names(conf_path) -> list[str]:
    with open(conf_path, 'r') as file:
        text = file.read()
        instance_names = re.findall(
            r"bst\.instance\.([^.]+)\.abi_list", text)
        return instance_names


def start_instance(index: int):
    instance_config = config['instances'][index]
    instance_name = instance_names[index]
    logger.info(f"Start Instance {index}, {instance_name}")
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
    instances.append(instance)


instances: list[Instance] = []
config = ConfigCore.get_config()

instance_names = get_instance_names(config['bluestacksConfPath'])

bluestacks_app_path = Path(config['bluestacksAppPath'])
bluestacks_conf_path = Path(config['bluestacksConfPath'])
bluestacks_sharedFolder_path = Path(config['bluestacksSharedFolderPath'])
minitouch_start_port = config['minitouchStartPort']


if __name__ == "__main__":
    logger = setup_logger(
        "acb.core",
        os.path.join(__file__, "../../logs/core.log"),
        None,
        logging.DEBUG
    )

    for i, instance in enumerate(config['instances']):
        event_emitter.on(
            f"{i}:{Commands.StartInstance.value}",
            lambda _: start_instance(i)
        )

    server = ServerThread("localhost", 9339)
    server.start()
    input()
