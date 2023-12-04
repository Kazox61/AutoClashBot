from core.android import Android
import time
from logging import Logger
from bot.home_village import HomeVillage


class Bot:
    def __init__(self, logger: Logger, android: Android, profile_names: list[str]):
        self.logger = logger
        self.android = android
        self.profile_names = profile_names
        self.home_village = HomeVillage(self, self.logger, self.android)

    def run(self):
        self.current_account_index = 0
        self.switch_account(self.profile_names[self.current_account_index])
        while True:
            self.loop()

    def loop(self):
        self.home_village.loop()

    def switch_account(self, profile_name: str) -> None:
        self.logger.info(f"Switching account to {profile_name}")
        self.android.stop_app()
        time.sleep(2)
        self.logger.info(f"Pulling shared_prefs for {profile_name}")
        self.android.bluestacks.push_shared_prefs(profile_name)
        time.sleep(3)
        self.android.start_app()
        time.sleep(10)

    def try_switch_next_account(self) -> bool:
        if len(self.profile_names) <= 1:
            return False

        self.current_account_index = (
            self.current_account_index + 1) % len(self.profile_names)
        self.switch_account(self.profile_names[self.current_account_index])
        return True
