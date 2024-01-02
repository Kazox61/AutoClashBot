from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from uvicorn import Config as uvicorn_Config
from uvicorn import Server
import asyncio
from pymitter import EventEmitter
from config.config import ConfigCore
from core.instance import Instance
from _logging import setup_logger, logging
import os
import re
from pathlib import Path
from tinydb import TinyDB, Query

db = TinyDB('../conf.json')


def append(key, value):
    def transform(doc: dict):
        obj: list = doc.get(key)
        if value in obj:
            obj.append(value)
    return transform


def remove(key, value):
    def transform(doc: dict):
        obj: list = doc.get(key)
        if value in obj:
            obj.remove(value)
    return transform


def get_instance_names(conf_path) -> list[str]:
    with open(conf_path, 'r') as file:
        text = file.read()
        instance_names = re.findall(
            r"bst\.instance\.([^.]+)\.abi_list", text)
        return instance_names


def create_instance_thread(index: int):
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
    instances[index] = instance


logger = setup_logger(
    "acb.core",
    os.path.join(__file__, "../../logs/core.log"),
    logging.DEBUG
)

loop = asyncio.get_event_loop()
event_emitter = EventEmitter()
app = FastAPI()
origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

clients: set[WebSocket] = set()
instances: dict[int, Instance] = {}
config = ConfigCore.get_config()

instance_names = get_instance_names(config['bluestacksConfPath'])

bluestacks_app_path = Path(config['bluestacksAppPath'])
bluestacks_conf_path = Path(config['bluestacksConfPath'])
bluestacks_sharedFolder_path = Path(config['bluestacksSharedFolderPath'])
minitouch_start_port = config['minitouchStartPort']


def broadcast_message(message):
    for client in clients:
        loop.create_task(client.send_json(message))


@app.get("/instance/{instance_number}/start")
async def start_instance(instance_number: int):
    create_instance_thread(instance_number)


@app.get("/instance/{instance_number}/close")
async def close_instance(instance_number: int):
    instance = instances.get(instance_number, None)
    if instance:
        task = instance.on_close_instance()
        instance.loop.create_task(task)


@app.get("/instance/{instance_number}/restart")
async def restart_instance(instance_number: int):
    instance = instances.get(instance_number, None)
    if instance:
        task = instance.on_restart_instance()
        instance.loop.create_task(task)


@app.get("/instance/{instance_number}/stop")
async def stop_instance(instance_number: int):
    instance = instances.get(instance_number, None)
    if instance:
        task = instance.on_stop_instance()
        instance.loop.create_task(task)


@app.get("/instance/{instance_number}/resume")
async def resume_instance(instance_number: int):
    instance = instances.get(instance_number, None)
    if instance:
        instance.on_resume_instance()


@app.get("/instance/{instance_number}/status")
async def get_instance_status(instance_number: int):
    instance = instances.get(instance_number, None)
    if instance:
        status = instance.instance_status.value
        return status
    else:
        return 0


@app.get("/instances")
async def get_instances():
    return instance_names


@app.post("/instances/{instance_number}/profiles/{profile_name}/add")
async def add_instance_profile(instance_number: int, profile_name: str):
    table = db.table('instances')
    Instance = Query()
    table.update(append("profiles", profile_name),
                 Instance.id == instance_number)
    broadcast_message({"type": "addProfileToInstance",
                      "instance_number": instance_number, "profile_name": profile_name})


@app.post("/instances/{instance_number}/profiles/{profile_name}/remove")
async def remove_instance_profile(instance_number: int, profile_name: str):
    table = db.table('instances')
    Instance = Query()
    table.update(remove("profiles", profile_name),
                 Instance.id == instance_number)


@app.get("/profiles")
async def get_profiles():
    profiles_table = db.table('profiles')
    return profiles_table.all()


@app.websocket("/updates")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    clients.add(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            await websocket.send_text(data)
    except WebSocketDisconnect:
        clients.remove(websocket)


create_instance_thread(0)
create_instance_thread(1)

if __name__ == "__main__":
    config = uvicorn_Config(app=app, loop="asyncio",
                            host="127.0.0.1", port=8000)
    server = Server(config)

    loop.create_task(server.serve())

    ###################################
    # just for quick testing
    create_instance_thread(0)
    # create_instance_thread(1)
    ####################################

    loop.run_forever()
