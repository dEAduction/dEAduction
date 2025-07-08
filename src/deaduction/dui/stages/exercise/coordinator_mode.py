from enum import IntEnum


class CoordinatorMode(IntEnum):
    Unknown = -1
    Normal = 0
    History = 1  # Exercise launched in history version
    CompleteStatement = 2  # The context should be completed
    Test = 100
