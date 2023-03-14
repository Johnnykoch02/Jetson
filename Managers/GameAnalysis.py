from Classes.GameDecision import *
from Classes.GameCorrection import *

class Analyzer:
    def __init__(self) -> None:
        pass
    # Finds the best decision
    def FindBest( self, game_data ) -> Decision:
        pass
    def TrackCompletion( self, game_objects, task ) -> Correction:
        return Correction()
    def WaitForCompletion( self ):
        pass

