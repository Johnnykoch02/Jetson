from Classes.GameDecision import *
from globals import *
from Classes.GameCorrection import *
from Managers.GameHasher import *
from Managers.GameObjects import *
from Managers.GameTasks import *
from concurrent.futures import ThreadPoolExecutor
import time
from typing import List, Dict, Tuple, Union
class Analyzer:
    def __init__(self) -> None:
        self.__gameStartTime = time.time() * 1000
        self.__hasher = None
        self.__Turned = False
        pass
    # Finds the best decision
    # Add roller blocking
    
    
    def FindBest( self, game_data: ObjectManager, task_manager: TaskManager ) -> Decision:
        hash_list = []
        if self.getMagEstimate(game_data, task_manager) >= 3: # We decide to shoot the disks
            return Decision(game_data.GetGoals()[GoalColor(CURRENT_TEAM_COLOR)], Actions.Type.SHOOT_DISK)
        
        frisbees = game_data.GetFrisbees()
        closest_frisbee = min(frisbees, key= lambda obj: obj.distance)
        if closest_frisbee.distance < 2.5: # Pick up the closest frisbee
            return Decision(closest_frisbee, Actions.Type.LOAD_DISK)        
        
        self.__hasher = Hasher(game_data)
        bots = game_data.GetBots()
        rollers = game_data.GetRollers()

        extra_data = {"bots": bots, "frisbees": frisbees, "rollers": rollers}

        # self.__hasher.rotate_velocity(2, 1)

        hashedFrisbees = self.__ThreadedHashing(frisbees, extra_data)
        hashedRollers = self.__ThreadedHashing(rollers, extra_data)

        hash_list.extend(hashedFrisbees)
        hash_list.extend(hashedRollers)
        
        hash_list = sorted(hash_list, key=lambda x: x[next(iter(x.keys()))]['score'], reverse=True)
        # We have a target object
        if hash_list:
            target_object = hash_list[0]['object']
            if target_object.type == ObjectType.FRISBEE:
                return Decision(target_object, Actions.Type.DRIVE_TO_OBJECT)
            elif target_object.type == ObjectType.ROLLER:
                return Decision (target_object, Actions.Type.CAPTURE_ROLLER, kwargs= {'power': 0.35})
        else:
            # if self.__Turned:
            #     return Decision(None, Actions.Type.DRIVE_TO_TARGET, kwargs= {'r': 3.5, 'theta': 0, 'reversed': START_REVERSED})
            # else:
                return Decision(None, Actions.Type.TURN_TO_ANGLE, kwargs= {'theta': 45, 'reversed': START_REVERSED})

    
    def __ThreadedHashing( self, objects: list, extra: dict) -> list:
        
        def __internal(item):
            return self.__hasher.HashGameObject(item, self.__GetDeltaTime(), extra)
        
        with ThreadPoolExecutor(max_workers=24) as executor:
            results = list(executor.map(__internal, objects))
        
        hash_list = list()

        for item, score in zip(objects, results):
            item.score = score
            hash_entry = {
                item.id: {
                    "score": score,
                    "object": item
                }
            }
            hash_list.append(hash_entry)

        return hash_list

    def __GetDeltaTime( self ) -> time:
        return (time.time() * 1000) - self.__gameStartTime
    def TrackCompletion( self, game_objects, task ) -> Correction:
        return Correction()
    def WaitForCompletion( self ):
        pass

