
from enum import Enum
from Classes.Vector import *

class ObjectType(Enum):
    FRISBEE = 1
    HIGH_GOAL = 2
    LOW_GOAL = 3
    ENEMY_ROBOT = 4
    FRIENDLY_ROBOT = 5

class GameObject:
    id = 0
    type = ObjectType.FRISBEE
    position = Vec(0,0,0)
    def __init__(self) -> None:
        pass
    