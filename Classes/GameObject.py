
from enum import IntEnum
from Classes.Vector import *

class ObjectType(IntEnum):
    FRISBEE = 0
    ROLLER = 1
    RED_HIGH_GOAL = 2 # BRAIN thinks this is just a high goal
    BLUE_HIGH_GOAL = 3
    LOW_GOAL = 4
    ENEMY_ROBOT = 5
    FRIENDLY_ROBOT = 6
class RollerColor(IntEnum):
    RED = 0
    BLUE = 1
    NEUTRAL = 2
class GoalColor(IntEnum):
    RED = 0
    BLUE = 1
class GameObject:
    def __init__(self, pos:Vec, lifespan= 3, type=ObjectType.FRISBEE, **kwargs) -> None:
        self.id = 0
        self.score = 0
        self.type = type
        self.position = pos
        self.velocity = Vec(0,0,0)
        self.radial_distance = 0
        self.lifespan = lifespan
        self.updated = False
        self.ovo = 0
        self.vars = {}
        if self.type == ObjectType.FRISBEE:
            pass
        elif self.type == ObjectType.ROLLER:
            self.vars['color'] = kwargs['color'] if 'color' in kwargs else RollerColor.NEUTRAL
            self.vars['is_in_contact'] = False
        elif self.type == ObjectType.HIGH_GOAL:
            self.vars['valid'] = False
            self.vars['color'] = kwargs['color'] if 'color' in kwargs else GoalColor.RED
    def __getitem__(self, item):
        return self.vars[item] if item in self.vars.keys() else None
    def getVector2(self) :
        return Vector2(r=self.distance, theta=self.ovo)