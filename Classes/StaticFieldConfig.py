from Classes.GameObject import *
from Classes.Vector import *

game_objects_config = [
    {
        "pos": Vec(120, 120, 0),
        "type": ObjectType.HIGH_GOAL,
        "kwargs": {
            'color': GoalColor.RED
        }
    },
    {
        "pos": Vec(24, 24, 24),
        "type": ObjectType.HIGH_GOAL,
        "kwargs": {
            'color': GoalColor.BLUE
        }
    },
    {
        "pos": Vec(112, 0, 18),
        "type": ObjectType.ROLLER,
        "kwargs": {
            'color': RollerColor.NEUTRAL
        }
    },
    {
        "pos": Vec(144, 30, 18),
        "type": ObjectType.ROLLER,
        "kwargs": {
            'color': RollerColor.NEUTRAL
        }
    },
    {
        "pos": Vec(0, 112, 18),
        "type": ObjectType.ROLLER,
        "kwargs": {
            'color': RollerColor.NEUTRAL
        }
    },
    {
        "pos": Vec(30, 144, 18),
        "type": ObjectType.ROLLER,
        "kwargs": {
            'color': RollerColor.NEUTRAL
        }
    },
]