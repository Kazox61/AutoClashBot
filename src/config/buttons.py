from enum import Enum
import os

root_dir = os.path.abspath(os.path.join(__file__, "../../../"))


class Buttons(Enum):
    Close = os.path.join(root_dir, "assets/buttons/close.png")
    StartAttack = (52, 547)
    FindAMatch = (605, 370)
    NextOpponent = (735, 470)
    Surrender = (56, 480)
    SurrenderOkay = (488, 363)
    ReturnHome = (400, 495)
    TrainAll = (31, 477)
    QuickTrain = (666, 84)
    TrainArmy1 = (716, 287)
    TrainTroops = (234, 88)
