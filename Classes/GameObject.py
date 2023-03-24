
from enum import Enum
from Classes.Vector import *

class ObjectType(Enum):
    FRISBEE = 1
    HIGH_GOAL = 2
    LOW_GOAL = 3
    ENEMY_ROBOT = 4
    FRIENDLY_ROBOT = 5

class GameObject:
    def __init__(self) -> None:
        self.id = 0
        self.score = 0
        self.type = ObjectType.FRISBEE
        self.position = Vec(0,0,0)
        self.velocity = Vec(0,0,0)
    