from Classes.GameDecision import *
from Classes.GameCorrection import *
from Managers.GameHasher import *
from Managers.GameObjects import *
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
        
        for frisbee in frisbees.values():
            delta_time = self.__GetDeltaTime()
            hash = frisbee.id = { 
                "score": self.__hasher.HashGameObject(frisbee, delta_time, bots),
                "object": frisbee
            }
            print(hash)
            hash_list.append(hash)

        pass
    def __GetDeltaTime( self ) -> time:
        return (time.time() * 1000) - self.__gameStartTime
    def TrackCompletion( self, game_objects, task ) -> Correction:
        return Correction()
    def WaitForCompletion( self ):
        pass

