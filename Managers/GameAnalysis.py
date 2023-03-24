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
        
        def wrap_hashing(frisbee):
            delta_time = self.__GetDeltaTime()
            return self.__hasher.HashGameObject(frisbee, delta_time, {"bots": bots, "frisbees": frisbees.values()})

        with ThreadPoolExecutor(max_workers=24) as executor:
            results = list(executor.map(wrap_hashing, frisbees.values()))

        self.__hasher.rotate_velocity(2, 1)

        for frisbee, score in zip(frisbees.values(), results):
            frisbee.score = score
            hash_entry = {
                frisbee.id: {
                    "score": score,
                    "object": frisbee
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

