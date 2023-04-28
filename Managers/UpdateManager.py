import time
import json
import asyncio
import threading
from Serial.VexCommunications import Communications

class UpdateManager(object):
    class ScheduledUpdate(object):
        def __init__(self, call_func, frequency= 0.5):
            self._callfunc = call_func
            self.sum_time = 0
            frequency = frequency
    def __init__(self):
        self.ScheduledUpdates = []
        self.__update_th = threading.Thread(target=self.__update)
        
    def ScheduleUpdate( self, call_func, frequency= 0.5):
        self.ScheduledUpdates.append( UpdateManager.ScheduledUpdate(call_func, frequency))
    def StartUpdates( self ):
        self.__update_th.start()
        
    def __update(self):
        # do something init wise
        ct = time.time()
        dt = 0
        lt = ct
        while True:
            dt = (time.time() - lt)
            lt = time.time()
            for update in self.ScheduledUpdates:
                update.sum_time += dt
                if update.sum_time >= update.frequency:
                    update._callfunc()
                    update.sum_time = 0
            time.sleep(0.1)
            
                
            
