from Classes.GameObject import *

# Weights from 0-100 with -1 being infinite priority
hash_weights = {
    ObjectType.FRISBEE: {
        "time_weights": {
            # Auton
            15000: -1,
            # Start of match
            15001: 100,
            # Last 15 seconds
            105000 - 15000: 80,
            # Last 5 seconds
            105000 - 5000: 10,
            # End game
            105000: 0
        },
        # Applied in reverse to ourselves
        "direction_weights": {
            # Other robot facing within 5 degrees
            5: 5,
            # 15 degrees
            15: 50,
            # 45 degrees
            45: 80,
            # 180 degrees
            180: 100
        },
        # Applied in reverse to ourselves
        "distance_weights": {
            # Other robot under 10 cm
            10: 5,
            # Under 30 cm
            30: 25,
            # Under 50 cm
            50: 70,
            # Under 5 m
            500: 100
        },
        "score_weights": {
            # high goal weights
            ObjectType.HIGH_GOAL: 5,
            # enemy low goal weights
            ObjectType.LOW_GOAL: 1
        },
        "push_weights": {
            # Within 0 cm of our low goal (inside)
            0: 100,
            # Within 5 cm
            5: 50,
            # Within 15-500 cm
            15: 0,
            500: 0
        }
    }
}

class Hasher:
    def __init__(self) -> None:
        pass
    def GetTimeHash( self, deltatime ) -> float:
        weights = hash_weights[ObjectType.FRISBEE]
        time_weight = -2
        last_time = None
        for time in weights["time_weights"]:
            if time >= deltatime:
                diff = 0
                percentage = 0
                if last_time != None:
                    percentage = ((time - deltatime) + last_time) / time
                    diff = weights["time_weights"][last_time] - weights["time_weights"][time]    
                time_weight = weights["time_weights"][time] + (diff * percentage)
                break
            else:
                last_time = time
        return time_weight
    def HashFrisbee( self, object, deltatime, extra) -> float:
        time_weight = self.GetTimeHash(deltatime)
        #print(time_weight)
        return time_weight
    def HashGameObject( self, object: GameObject, deltatime: float, extra: list[GameObject] ) -> float:
        if object.type == ObjectType.FRISBEE:
            return self.HashFrisbee( object, deltatime, extra )