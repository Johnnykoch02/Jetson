from Classes.GameObject import *

class Decision:
    
    def __init__( self, target: GameObject, target_type, **kwargs) -> None:
        self.target = target
        self.target_type = target_type
        self.kwargs = kwargs
    def Getdecision( self ) -> GameObject:
        return self.target