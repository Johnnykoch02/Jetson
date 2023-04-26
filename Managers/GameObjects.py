import time
from Classes.GameObject import *
from Serial.VexCommunications import Communications
from Classes.Vector import *
from typing import Dict, List
import math

def create_game_objects():
    from Classes.StaticFieldConfig import game_objects_config
    game_objects = []
    for obj_data in game_objects_config:
        game_objects.append(GameObject(obj_data['pos'], obj_data['type'], kwargs=obj_data.get('kwargs', {}), lifespan=math.inf))
    return game_objects

class ObjectManager:
    def __init__(self, starting_pos, starting_angle, comms: Communications) -> None:
        # int, GameObject
        self.frisbees = dict()
        self.enemies = dict()
        self.friendly = dict()
        self.goals = dict()
        self.rollers = dict()
        self.target = None
        self.comms = comms
        self.__mag_cnt = 0
        self.__my_robot__ = {
            'pos': starting_pos,
            'previous_pos': starting_pos,
            'velocity': Vec(0, 0, 0),
            'theta': starting_angle,
            'previous_theta': starting_angle,
            'angular_velocity': 0,
        }
        self.ctime = time.time()
        self.ltime = self.ctime
        self.object_memory = dict()    
        
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
    
    def UpdateRobot(self, pos:Vec, theta:float) -> None:
        self.ctime = time.time()
        previous_pos = self.my_robot['pos']
        new_velocity = (pos - previous_pos) / (self.ctime - self.ltime)
        previous_theta = self.my_robot['theta']
        angular_velocity = (theta - previous_theta) / (self.ctime - self.ltime)
        self.my_robot = {
            'pos': pos,
            'previous_pos': previous_pos,
            'velocity': new_velocity,
            'theta': theta,
            'previous_theta': previous_theta,
            'angular_velocity': angular_velocity,
        }
    def GetRobot( self ) -> Dict[str, any]:
        return self.__my_robot__

    def SetCurrentTarget( self, object: GameObject ) -> None:
        self.target = object
        self.CommsSetTarget()
    def GetCurrentTarget( self ) -> GameObject:
        return self.target
    def SerializeForComs( self ) -> bytearray:
        pass
    def GetEnemies( self ) -> list:
        return self.enemies.values()
    def GetFriendly( self ) -> list:
        return self.friendly.values()
    def GetFrisbees( self ) -> list:
        return self.frisbees.values()
    def GetGoals( self ) -> dict:
        return self.goals
    def GetBots( self ) -> list:
        return (self.enemies | self.friendly).values()
    def SetMagCnt( self, value: int ) -> None:
        self.__mag_cnt = value
    def GetMagCnt( self ) -> int:
        return self.__mag_cnt
    def GetRollers( self ) -> list:
        return self.rollers.values()
    def GetAll( self ) -> list:
        return (self.enemies | self.friendly | self.frisbees | self.rollers).values()
    def CommsSetTarget( self ) -> None:
        returnCode = self.comms.SendPacket("set_target_obj", max(int(self.target.type), 2))
    def reset_updated(self):
        for obj in self.GetAll():
            obj.updated = False
    def CommsUpdateTargetDrDth( self ) -> None:
        if self.target != None:
          if self.target.type == ObjectType.FRISBEE:
            self.comms.SendPacket("update_target_obj_dr_dtheta", self.target.r, self.target.ovo)
          if self.target.type == ObjectType.RED_HIGH_GOAL or self.target.type == ObjectType.BLUE_HIGH_GOAL:
            self.comms.SendPacket("update_target_obj_dr_dtheta", self.target.r, self.target.ovo, 0.0)
          if self.target.type == ObjectType.ROLLER: #TODO: DO SOME FANCY SHMANCY AUGMENTATION MATH HERE FOR OVO AND R
            self.comms.SendPacket("update_target_obj_dr_dtheta", self.target.r, self.target.ovo,  self.target['color'], self.target['is_in_contact']) 
    def PruneObjects( self ) -> None:
        for id, obj in self.frisbees.items():
            if not obj.updated:
                obj['lifespan'] -= 1
            if obj['lifespan'] <= 0:
                del self.frisbees[id] # What if is our target object?
            
    def ProcessImageData( self, image_data: List[List[float, float, ObjectType]]) -> None:
        '''
        DATA FORMAT: [d_r, -d_theta, object_type], 
        '''
        self.reset_updated()
        distance_threshold = 3.0 # Inches
        for (d_r, d_theta, object_type) in image_data:
            d_theta= -d_theta # <3
            if object_type == ObjectType.FRISBEE:
                d_Vector = Vector2(r=d_r, theta=d_theta)
                interp_pos = self.__my_robot__['pos'].toVector2() + d_Vector
                min_euclidian_distance, id = math.inf, -1
                for i, (id, obj) in enumerate(self.frisbees.items()):
                    obj_pos = obj.position.toVector2()
                    euclidean_distance = (interp_pos.x - obj_pos.x) ** 2 + (interp_pos.y - obj_pos.y) ** 2  
                    if euclidean_distance < min_euclidian_distance:
                        id, min_euclidian_distance = i, euclidean_distance
                if min_euclidian_distance < distance_threshold:
                    self.frisbees[id].updatePos(Vec(interp_pos.x, interp_pos.y, 0))
                    self.frisbees[id].lifespan = 3
                    self.frisbees[id].updated = True
                else:
                    self.frisbees[len(self.GetFrisbees())] = GameObject(Vec(interp_pos.x, interp_pos.y, 0), ObjectType.FRISBEE)
            if object_type == ObjectType.ROLLER:
                d_Vector = Vector2(r=d_r, theta=d_theta)
                interp_pos = self.__my_robot__['pos'].toVector2() + d_Vector
                min_euclidian_distance, id = math.inf, -1
                for i, (id, obj) in enumerate(self.rollers.items()):
                    obj_pos = obj.position.toVector2()
                    euclidean_distance = (interp_pos.x - obj_pos.x) ** 2 + (interp_pos.y - obj_pos.y) ** 2  
                    print('Euc. Delta on Roller:', euclidean_distance)
                    if euclidean_distance < min_euclidian_distance:
                        id, min_euclidian_distance = i, euclidean_distance
                if id != -1:
                    self.rollers[id]
                
        
        self.PruneObjects()