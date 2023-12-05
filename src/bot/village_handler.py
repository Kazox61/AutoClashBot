from core.android import Android
from logging import Logger
from bot.home_village import HomeVillage
from bot.village import Village
import time


class VillageHandler:
    def __init__(self, logger: Logger, android: Android, profile_names: list[str]):
        self.logger = logger
        self.android = android
        self.profile_names = profile_names

        self.villages: list[Village] = []
        for profile_name in profile_names:
            village = Village(profile_name, logger, android)
            self.villages.append(village)

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
        if len(self.villages) <= 1:
            return False

        self.current_account_index = (
            self.current_account_index + 1) % len(self.villages)
        self.switch_account(
            self.villages[self.current_account_index].profile_name)
        return True

    def run(self) -> None:
        self.current_account_index = 0
        self.active_village = self.villages[self.current_account_index]
        self.switch_account(self.active_village.profile_name)

        while True:
            self.active_village.run()
            switched = self.try_switch_next_account()
            if not switched:
                time.sleep(10)
