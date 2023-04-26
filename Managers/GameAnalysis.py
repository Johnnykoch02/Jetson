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
        # actions = [
        #     Actions.Type.CAPTURE_ROLLER,
        #     Actions.Type.DRIVE_TO_OBJECT, 
        #     Actions.Type.LOAD_DISK, 
        #     Actions.Type.SHOOT_DISK, 
        #     Actions.Type.TURN_TO_ANGLE,
        #     Actions.Type.DRIVE_TO_OBJECT
        #            ]

        # def score_actions(frisbees: List[GameObject], rollers:List[GameObject], object_manager:ObjectManager, task_manager: TaskManager) -> List[Dict[str, Union[int, float]]]:
        #     dt = self.__GetDeltaTime()
        #     def CaptureRollerScore(frisbees: List[GameObject], rollers:List[GameObject], object_manager:ObjectManager, task_manager: TaskManager) -> List[Dict[str, Union[int, float]]]:
        #         kTime = 0.2
        #         kDistance = 0.3
        #         kOrientation = 0.3
        #         cost = lambda dt, distance, orientation, roller: (((55 - (dt/1000) / 55) + kTime) * ((distance*kDistance + orientation*kOrientation) / 12) + int(math.inf*int(roller['color']) == CURRENT_TEAM_COLOR)) # Feet
                
        #     def DriveToObjectScore(frisbees: List[GameObject], object_manager:ObjectManager, task_manager: TaskManager) -> List[Dict[str, Union[int, float]]]:
        #         kTime = 0.2
        #         kDistance = 0.3
        #         kOrientation = 0.3
        #         kNum0bjs = 0.68
        #         cost = lambda distance, orientation, dt, cnt_objs, : int((dt/1000)<45) * ((distance*kDistance + orientation*kOrientation) / 12) * kNum0bjs((3-cnt_objs)%4)
        #         for frisbee in frisbees:
        #             total_cost = cost()
        #         scored_items = for item.id: {
        #             "score": score,
        #             "object": item
        #         }  
     
        
        hash_list = sorted(hash_list, key=lambda x: x[next(iter(x.keys()))]['score'], reverse=True)
        target_object = hash_list[0]['object']
        if target_object.type == ObjectType.FRISBEE:
            return Decision(target_object, Actions.Type.DRIVE_TO_OBJECT)
        elif target_object.type == ObjectType.ROLLER:
            return Decision (target_object, Actions.Type.CAPTURE_ROLLER, kwargs= {'power': 0.35})
    
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

