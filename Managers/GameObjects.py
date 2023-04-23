from Classes.GameObject import *

class ObjectManager:
    def __init__(self) -> None:
        # int, GameObject
        self.frisbees = dict()
        self.enemies = dict()
        self.friendly = dict()
        self.goals = dict()
        self.rollers = dict()
        self.target = None

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
        if object.type == ObjectType.ROLLER:
            self.__Trace(self.rollers, object)
        

    def SetCurrentTarget( self, object: GameObject ) -> None:
        self.target = object
    def GetCurrentTarget( self ) -> GameObject:
        return self.target
    def SerializeForComs( self ) -> bytearray:
        pass
    def GetEnemies( self ) -> list[GameObject]:
        return self.enemies.values()
    def GetFriendly( self ) -> list[GameObject]:
        return self.friendly.values()
    def GetFrisbees( self ) -> list[GameObject]:
        return self.frisbees.values()
    def GetGoals( self ) -> dict[int, GameObject]:
        pass
    def GetBots( self ) -> list[GameObject]:
        return (self.enemies | self.friendly).values()
    def GetRollers( self ) -> list[GameObject]:
        return self.rollers.values()
    def GetAll( self ) -> list[GameObject]:
        return (self.enemies | self.friendly | self.frisbees | self.rollers).values()
