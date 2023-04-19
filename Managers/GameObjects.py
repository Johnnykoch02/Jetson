from Classes.GameObject import *

class ObjectManager:
    def __init__(self) -> None:
        # int, GameObject
        self.frisbees = dict()
        self.enemies = dict()
        self.friendly = dict()
        self.goals = dict()

    def __Trace( self, table: dict, obj: GameObject):
        if obj.id in table.keys():
            table.update({obj.id: obj})
        else:
            table[obj.id] = obj

    # Traces deteced objects to existing game objects
    def TraceObject( self, object: GameObject ) -> None:
        if object.type == ObjectType.FRISBEE:
            self.__Trace(self.frisbees, object)
        if object.type == ObjectType.ENEMY_ROBOT:
            self.__Trace(self.enemies, object)
        if object.type == ObjectType.FRIENDLY_ROBOT:
            self.__Trace(self.friendly, object)
        

    def SetCurrentTarget( self, object ):
        pass
    def GetCurrentTarget( self ) -> GameObject:
        pass
    def SerializeForComs( self ) -> bytearray:
        pass
    def GetEnemies( self ) -> dict[int, GameObject]:
        pass
    def GetFriendly( self ) -> dict[int, GameObject]:
        pass
    def GetFrisbees( self ) -> dict[int, GameObject]:
        return self.frisbees
    def GetGoals( self ) -> dict[int, GameObject]:
        pass
    def GetBots( self ) -> list[GameObject]:
        return (self.enemies | self.friendly).values()
    def GetAll( self ) -> list[GameObject]:
        return (self.enemies | self.friendly | self.frisbees).values()

