from pymitter import EventEmitter
from threading import Thread
from bot.village_handler import VillageHandler
from core.android import Android
from config.commands import Commands
import cv2
from _logging import setup_logger, logging
import os
from pathlib import Path
import asyncio
import time
from enum import Enum


class InstanceStatus(Enum):
    Closed = 0
    Starting = 1
    Running = 2
    Stopped = 3


class Instance(Thread):
    def __init__(
        self,
        bluestacks_app_path: Path,
        bluestacks_conf_path: Path,
        bluestacks_sharedFolder_path: Path,
        bluestacks_instance_name: str,
        minitouch_port: int,
        instance_index: int,
        instance_config: dict,
        event_emitter: EventEmitter,
    ) -> None:
        self.instance_status = InstanceStatus.Stopped
        self.bluestacks_instance_name = bluestacks_instance_name
        self.logger = setup_logger(
            f"acb.{instance_index}.{self.bluestacks_instance_name}",
            os.path.join(
                __file__,
                f"../../../logs/{self.bluestacks_instance_name}.log"
            ),
            None,
            logging.DEBUG
        )
        self.bluestacks_app_path = bluestacks_app_path
        self.bluestacks_conf_path = bluestacks_conf_path
        self.bluestacks_sharedFolder_path = bluestacks_sharedFolder_path
        self.minitouch_port = minitouch_port
        self.instance_index = instance_index
        self.instance_config = instance_config
        self.event_emitter = event_emitter
        self.init_events()
        Thread.__init__(self)

    def run(self) -> None:
        self.instance_status = InstanceStatus.Starting
        self.android = Android(
            self.bluestacks_app_path,
            self.bluestacks_conf_path,
            self.bluestacks_sharedFolder_path,
            self.bluestacks_instance_name,
            self.minitouch_port
        )
        self.android.initialize()
        self.village_handler = VillageHandler(self.logger,
                                              self.android,
                                              self.instance_config["profiles"]
                                              )

        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
        coroutine = self.village_handler.run()
        self.future = asyncio.run_coroutine_threadsafe(coroutine, self.loop)
        self.instance_status = InstanceStatus.Running
        self.loop.run_forever()

    def init_events(self) -> None:
        self.event_emitter.on(
            f"{self.instance_index}:{Commands.CloseInstance.value}",
            self.on_close_instance
        )
        self.event_emitter.on(
            f"{self.instance_index}:{Commands.RestartInstance.value}",
            self.on_restart_instance
        )
        self.event_emitter.on(
            f"{self.instance_index}:{Commands.StopInstance.value}",
            self.on_stop_instance
        )
        self.event_emitter.on(
            f"{self.instance_index}:{Commands.ResumeInstance.value}",
            self.on_resume_instance
        )
        self.event_emitter.on(
            f"{self.instance_index}:{Commands.Screenshot.value}",
            self.on_screenshot
        )
        self.event_emitter.on(
            f"{self.instance_index}:{Commands.PullSharedPrefs.value}",
            self.on_pull_shared_prefs
        )

    async def on_close_instance(self, _) -> None:
        if self.instance_status == InstanceStatus.Closed:
            return
        self.logger.info("Close Instance")
        self.future.cancel()
        try:
            await self.future.result()
        except Exception:
            self.android.kill()
            time.sleep(1)
            self.loop.stop()
            self.instance_status = InstanceStatus.Closed

    async def on_restart_instance(self, _) -> None:
        self.logger.info("Restart Instance")
        self.future.cancel()
        try:
            await self.future.result()
        except Exception:
            if self.instance_status != InstanceStatus.Closed:
                self.android.kill()
                time.sleep(1)
            self.instance_status = InstanceStatus.Starting
            self.android = Android(
                self.bluestacks_app_path,
                self.bluestacks_conf_path,
                self.bluestacks_sharedFolder_path,
                self.bluestacks_instance_name,
                self.minitouch_port
            )
            self.android.initialize()
            self.village_handler = VillageHandler(self.logger,
                                                  self.android,
                                                  self.instance_config["profiles"]
                                                  )
            coroutine = self.village_handler.run()
            self.future = asyncio.run_coroutine_threadsafe(
                coroutine, self.loop)
            self.instance_status = InstanceStatus.Running

    async def on_stop_instance(self, _) -> None:
        if self.instance_status == InstanceStatus.Closed and self.instance_status == InstanceStatus.Stopped:
            return
        self.logger.info("Stop Instance")
        self.future.cancel()
        try:
            await self.future.result()
        except Exception:
            self.instance_status = InstanceStatus.Stopped

    async def on_resume_instance(self, _) -> None:
        if self.instance_status != InstanceStatus.Stopped:
            return
        self.logger.info("Resume Instance")
        coroutine = self.village_handler.run()
        self.future = asyncio.run_coroutine_threadsafe(
            coroutine, self.loop)

    def on_screenshot(self, path: str) -> None:
        screenshot = self.android.get_screenshot()
        cv2.imwrite(path, screenshot)

    def on_pull_shared_prefs(self, profile_name: str) -> None:
        self.logger.info(f"Pushing shared_prefs for {profile_name}")
        self.android.bluestacks.pull_shared_prefs(profile_name)
