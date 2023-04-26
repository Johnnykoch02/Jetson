from typing import Literal, Union, TypeVar, Callable
from globals import *
from Classes.GameObject import *
from Classes.Vector import *
from collections import deque
from enum import IntEnum
from Serial.VexCommunications import Communications

class APICaller(object):
    class APICalls(IntEnum):
        GO_TO_POSITION = 0 #(DR DTHETA)
        TURN_TO_ANGLE = 1 #(DTHETA)
        SPIN_ROLLER = 2 
        TURNOFF_ROLLER = 3 
        SHOOT_DISK = 4
        LOAD_SHOOTER = 5 # ( ENSURE TARGET OBJECT SET )
        GO_TO_OBJECT = 6 
        SET_TARGET_OBJECT = 7 # (object type)
    TAG_MAP = dict({
            APICalls.GO_TO_POSITION: "go_to_pos_dr_dtheta",
            APICalls.TURN_TO_ANGLE: "turn_to_angle",
            APICalls.SPIN_ROLLER: "spin_roller",
            APICalls.TURNOFF_ROLLER: "turnoff_roller",
            APICalls.SHOOT_DISK: "shoot_disk",
            APICalls.LOAD_SHOOTER: "load_shooter",
            APICalls.GO_TO_OBJECT: "go_to_obj",
        })
        
    @staticmethod
    def GetAPITag(tag) -> Union(str, None):
            return APICaller.TAG_MAP.get(tag, None)

    def __init__(self, comms:Communications,):
        self.__comms__ = comms
    def MakeAPICall(self, method, *args) -> int:
        return self.__comms__.SendPacket(APICaller.GetAPITag(method), *args)
    def SendClearTasks( self ) -> int:
        self.__comms__.SendPacket("clear_tasks", 0)
    

class Actions:
    class Type(IntEnum):
        CAPTURE_ROLLER = 0 # [Drive in Forward Direction torwards Roller, Turn 180 Deg., Turn On Roller, Finish Driving until In Contact, Wait For Color Target, Send Stop Signal.]
        DRIVE_TO_TARGET = 1 # [Send over DrDtheta, wait for Task to Complete]
        LOAD_DISK = 2 # [Set Target Object, Go To Object, Wait For Task to Complete]
        SHOOT_DISK = 3 # [Set Target Object to Goal, Funnel Update Info (automatic), Wait For Task to Complete]
        TURN_TO_ANGLE = 4 # [Set Dtheta, Wait For Task to Complete]
        DRIVE_TO_OBJECT = 5 # Set Target Object, Go To Object, Wait For Task to Complete
    def __init__(self, target_object:GameObject, action_type:Type, **kwargs):
        self.vars = {}
        self.type = action_type
        self.isFinished = None # DEFAULT is None such that if a Task has a isFinished field, it will be used instead of the TaskManager.
        self.seq_indexes_finished = []
        self.seq_indexes_send_kills = []
        self.target_object = target_object
        if self.type == Actions.Type.CAPTURE_ROLLER:
            self.vars['color'] = RollerColor(CURRENT_TEAM_COLOR) # Capture Color
            self.vars['power'] = kwargs['power'] if 'power' in kwargs else 0.35 # as a Percentage of Max [-1: +1]
            self.vars['r'] = kwargs['r'] if 'r' in kwargs else 2.5 
            self.isFinished = lambda x: self.vars['color'] == x.target_object['color'] or x.target_object['is_in_contact']
            self.seq_indexes_finished.extend([4, 5])
        elif self.type == Actions.Type.DRIVE_TO_TARGET:
            self.vars['r'] = kwargs['r']
            self.vars['theta'] = kwargs['theta']
            self.vars['reversed'] = kwargs['reversed'] if 'reversed' in kwargs else False
            # self.isFinished = lambda x:  x
        elif self.type == Actions.Type.LOAD_DISK:
            pass # Needs Update Target Object
        elif self.type == Actions.Type.SHOOT_DISK:
            self.vars['color'] = GoalColor(CURRENT_TEAM_COLOR)
            # self.isFinished = lambda x:  x
        elif self.type == Actions.Type.TURN_TO_ANGLE:
            self.vars['theta'] = kwargs['theta']
            self.vars['reversed'] = kwargs['reversed'] if 'reversed' in kwargs else False
            # self.isFinished = lambda x:  x
        elif self.type == Actions.Type.DRIVE_TO_OBJECT:
            self.vars['reversed'] = kwargs['reversed'] if 'reversed' in kwargs else False
    def __getitem__(self, key):
        return self.vars[key] if key in self.vars else None

'''
    Takes in an Action and outputs a List of API Calls associated with that Action.
'''
class LogicBuilder(object):
    @staticmethod
    def GetAPICalls(action:Actions) -> tuple[list[APICaller.APICalls], list[object]]: 
        ''' 
        \ The Get API Calls Function returns a list of API Calls associated with an Action, with associated action arguments to pass to the API Caller. 
        This Function Relies:
            - Action is initialized properly.
            - The Target Object is initialized properly.
        '''
        if action.type == Actions.Type.CAPTURE_ROLLER:
            API_Calls = [
                APICaller.APICalls.SET_TARGET_OBJECT,  APICaller.APICalls.GO_TO_OBJECT,  APICaller.APICalls.TURN_TO_ANGLE, APICaller.APICalls.SPIN_ROLLER, APICaller.APICalls.GO_TO_POSITION, APICaller.APICalls.TURNOFF_ROLLER # Here We Send Kill of the Goto once in contact.
            ]
            API_Args = [
                (int(action.target_object.type)), (int(False)), (float(180), float(False)), (float(action['power'])), (int(action['r']), 0, int(True)), (0)
            ]
            return API_Calls, API_Args
        elif action.type == Actions.Type.DRIVE_TO_TARGET:
            API_Calls = [
                APICaller.APICalls.GO_TO_POSITION,
            ]
            API_Args = [
                (float(action['r']), float(action['theta']), int(action['reversed']))
            ]
        elif action.type == Actions.Type.LOAD_DISK:
            API_Calls = [
                 APICaller.APICalls.SET_TARGET_OBJECT, APICaller.APICalls.LOAD_SHOOTER,
            ]
            API_Args = [
                (int(action.target_object.type)), (0)
            ] 
        elif action.type == Actions.Type.SHOOT_DISK:
            API_Calls = [
                 APICaller.APICalls.SET_TARGET_OBJECT, APICaller.APICalls.SHOOT_DISK,
            ]
            API_Args = [
                (int(action.target_object.type)), (0)
            ]
        elif action.type == Actions.Type.TURN_TO_ANGLE:
            API_Calls = [
               APICaller.APICalls.TURN_TO_ANGLE,
            ]
            API_Args = [
                (float(action['theta']), float(action['reversed']))
            ]
        elif action.type == Actions.Type.DRIVE_TO_OBJECT:
            API_Calls = [
                APICaller.APICalls.SET_TARGET_OBJECT,  APICaller.APICalls.GO_TO_OBJECT,
            ]
            API_Args = [
                (int(action.target_object.type)), (int(action['reversed'])),
            ]
        

class TaskManager(object):
    class Task(object):
        def __init__(self, api_caller:APICaller, action: Actions):
            self.action = action
            self.__API_Calls, self.__API_Args = LogicBuilder.GetAPICalls(self.action)
            self.sequence_position = 0
            self.sequence_length = len(self.__API_Calls)
            self.__API__Caller = api_caller
            self.API_call_Sent = False
            self.target_object = action.target_object

        def update( self, task_finished ):
            if task_finished:
                self.sequence_position+=1
                self.API_call_Sent = False
            elif self.action.isFinished is not None and self.sequence_position in self.action.seq_indexes_finished and self.action.isFinished(self.action):
                self.__API__Caller.SendClearTasks()
                
            else:
                if not self.API_call_Sent:
                    self.__API__Caller.MakeAPICall(self.__API_Calls[self.sequence_position], *self.__API_Args[self.sequence_position])

            return True if self.sequence_position >= self.sequence_length else False
        
        def UpdateTargetObject( self, target_object:GameObject ):
            self.target_object = target_object
            self.action.target_object = target_object    
        
    def __init__(self, object_manager, comms:Communications,) -> None:
        self.object_manager = object_manager
        self.current_task_number = 0
        self.current_action = None
        self.current_task = None
        self.queued_actions = deque()
        self.__APICaller__ = APICaller(comms)
        self.__total_robot_tasks_completed = 0
        self.__update_task__ = False
        
    def Initialize( self ) -> None:
        pass
    
    def Update( self ) -> None:
        '''
            Some Actions may need an update if the majority of the Logic Takes place on the Jetson.
        '''
        if self.current_task.target_object != self.object_manager.GetCurrentTarget():
            self.current_task.UpdateTargetObject(self.object_manager.GetCurrentTarget())
        if self.current_task is not None:
            if self.current_task.update(self, self.__update_task__):
                self.__OnSequenceFinished()
            elif self.__update_task__:
              self.__update_task__ = False
        else:
            self.StartNextTask()
        
    def AlmostFinished( self ) -> bool:
        return self.current_task.sequence_position >= (self.current_task.sequence_length - 1)
    def QueueAction( self, action:Actions):
        self.queued_actions.append(action)
    def GetCurrentAction( self ) -> Actions:
        return self.current_action
    def Interupt( self ):
        pass
    def __OnSequenceFinished( self ):
        self.StartNextTask()
        
    def StartNextTask( self ):
        if len(self.queued_actions) > 0:
            self.current_action = self.queued_actions.popleft()
            self.current_task = TaskManager.Task(self.__APICaller__, self.current_action)
            self.current_task_number = 0
            self.__update_task__ = False
        
    def OnTaskFinished( self, task_number ):
        self.__update_task__ = True
        self.current_task_number+=1
        self.__total_robot_tasks_completed = task_number
        

