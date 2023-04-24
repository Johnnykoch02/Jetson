from Classes.GameDecision import *
from Classes.GameCorrection import *
from Managers.GameHasher import *
from Managers.GameObjects import *
from concurrent.futures import ThreadPoolExecutor
import time

class Analyzer:
    def __init__(self) -> None:
        self.__gameStartTime = time.time() * 1000
        self.__hasher = Hasher()
        pass
    # Finds the best decision
    # Add roller blocking
    
    def FindBest( self, game_data: ObjectManager ) -> Decision:
        hash_list = []
        
        bots = game_data.GetBots()
        frisbees = game_data.GetFrisbees()
        rollers = game_data.GetRollers()

        extra_data = {"bots": bots, "frisbees": frisbees, "rollers": rollers}

        # self.__hasher.rotate_velocity(2, 1)

        hashedFrisbees = self.__ThreadedHashing(frisbees, extra_data)
        hashedRollers = self.__ThreadedHashing(rollers, extra_data)

        hash_list.extend(hashedFrisbees)
        hash_list.extend(hashedRollers)

        return hash_list
    
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

