from enum import Enum


class Commands(Enum):
    StartInstance = 0
    CloseInstance = 1
    RestartInstance = 2
    StopInstance = 3
    ResumeInstance = 4
    Screenshot = 5
    PullSharedPrefs = 6
