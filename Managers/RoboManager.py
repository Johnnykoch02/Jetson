from Serial.VexCommunications import *
from Managers.GameObjects import *
from Managers.GameAnalysis import *
from Managers.VisionManager import *
from Managers.GameSteps import *
from Managers.GameTasks import *

class RobotManager(object):
    def __init__(
    self, 
    debug_visulazation=False,                  
                 ):
        # Load serial Communications
        self.comms = Communications()
        self.comms.Init()
        self.comms.Start()
        # Init Game Object manager
        self.objects = ObjectManager()
        # Init Game Analysis manager
        self.analyzer = Analyzer()
        # Init Game Step Builder
        self.builder = StepBuilder()
        # Init Task manager
        self.tasks = TaskManager()
        # Init Vision manager with reporting to Game Analysis
        # True for fake data
        self.camera = Vision(debug_visulazation)
        
    def set_disk_obj_callback(self,):
        pass
    def get_disk_obj_callback(self,):
        pass
    def set_goal_obj_callback(self,):
        pass
    def get_goal_obj_callback(self,):
        pass
    def get_pos_callback(self,):
        pass
    def set_pos_callback(self,):
        pass
    
