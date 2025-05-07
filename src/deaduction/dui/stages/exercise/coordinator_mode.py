from enum import IntEnum


class CoordinatorMode(IntEnum):
    Normal = 0
    History = 1  # Exercise launched in history version
    CompleteStatement = 2  # The context should be completed
    Test = 100
