from Classes.GameObject import *
from typing import Dict

class ObjectManager:
    def __init__(self) -> None:
        # int, GameObject
        self.frisbees = dict()
        self.enemies = dict()
        self.friendly = dict()
        self.goals = dict()
        pass
    # Traces deteced objects to existing game objects
    def TraceObject( self, object: GameObject ) -> None:
        if object.type == ObjectType.FRISBEE:
            if object.id in self.frisbees.keys():
                self.frisbees.update({object.id: object})
            else:
                self.frisbees[object.id] = object               
        pass
    def SetCurrentTarget( self, object ):
        pass
    def GetCurrentTarget( self ) -> GameObject:
        pass
    def SerializeForComs( self ) -> bytearray:
        pass
    def GetEnemies( self ) -> Dict[int, GameObject]:
        pass
    def GetFriendly( self ) -> Dict[int, GameObject]:
        pass
    def GetFrisbees( self ) -> Dict[int, GameObject]:
        return self.frisbees
    def GetGoals( self ) -> Dict[int, GameObject]:
        pass
    def GetBots( self ) -> Dict[int, GameObject]:
        pass
