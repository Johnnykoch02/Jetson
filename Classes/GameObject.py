
from enum import Enum
from Classes.Vector import *

class ObjectType(Enum):
    FRISBEE = 1
    HIGH_GOAL = 2
    LOW_GOAL = 3
    ENEMY_ROBOT = 4
    FRIENDLY_ROBOT = 5

class GameObject:
    def __init__(self, type, id=None, position=None, velocity=None):
        self.id = id
        self.score = 0
        self.type = type
        self.position = Vec(0,0,0) if position is None else position
        self.velocity = Vec(0,0,0) if velocity is None else velocity

class Frisbee(GameObject):
    def __init__(self, id, pos):
        super().__init__(ObjectType.FRISBEE, id, pos, Vec(0,0,0))
        
    def get_serialized(self):
        