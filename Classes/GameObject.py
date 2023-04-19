
from enum import Enum
from Classes.Vector import *

class ObjectType(Enum):
    FRISBEE = 1
    ROLLER = 2
    HIGH_GOAL = 3
    LOW_GOAL = 4
    ENEMY_ROBOT = 5
    FRIENDLY_ROBOT = 6

class GameObject:
    def __init__(self) -> None:
        self.id = 0
        self.score = 0
        self.type = ObjectType.FRISBEE
        self.position = Vec(0,0,0)
        self.velocity = Vec(0,0,0)
    