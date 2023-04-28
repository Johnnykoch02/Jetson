from globals import *
from Serial.VexCommunications import *
from Managers.GameObjects import *
from Managers.GameAnalysis import *
from Managers.VisionManager import *
from Managers.GameSteps import *
from Managers.GameTasks import *
from Managers.UpdateManager import *
from Classes.GameDecision import *
# import pyqtgraph as pg
# from PyQt5 import QtWidgets, QtCore
import cProfile
import pstats
import sys
import threading
import datetime

# from Testing.Visualize import *

# def visualization():
#     global objects
#     visualize_game_objects(objects.GetAll())

mag_cnt = 0
__mag_cnt_lck__ = threading.Lock()

get_mag_estimate = lambda game_data, task_manager: game_data.GetMagCnt() + sum (1 for action in task_manager.queued_actions if action.type == Actions.Type.LOAD_DISK )

def GameLogic(camera: Vision, tasks: TaskManager, analyzer: Analyzer, objects: ObjectManager, scheduler: UpdateManager, comms: Communications):
    t = time.time()
    # Beat the game
    while True:

        for object in camera.CollectObjects():
            objects.TraceObject(object)

        nt = time.time()
        dt = nt - t

        if DEBUG_VISUALIZE:
            pass # TODO: send data to Main Frame about the game state
            # for bot in objects.GetBots():
            #     update_robot_position_and_velocity(bot, dt)

        # buf = objects.SerializeForComs()
        # comms.SendRawBuffer(buf)

        analyzer.WaitForCompletion()

        # Task -> Actions -> Steps -> Directions
        # Reactive Program -> Reacts and responds its changing environment

        if tasks.AlmostFinished():
            decision = None
            if get_mag_estimate(objects, tasks) >= 3: # We decide to shoot the disks
                decision = Decision(objects.GetGoals()[GoalColor(CURRENT_TEAM_COLOR)], Actions.Type.SHOOT_DISK)
            frisbees = objects.GetFrisbees()
            closest_frisbee = min(frisbees, key= lambda obj: obj.distance)
            if closest_frisbee.distance < 2.5: # Pick up the closest frisbee
                decision = Decision(closest_frisbee, Actions.Type.LOAD_DISK)        
            else:
                decision = analyzer.FindBest(objects, tasks)
                
            if objects.GetCurrentTarget() != decision.GetTarget():
                objects.SetCurrentTarget(decision.GetTarget())
            action = Actions(decision.target, decision.target_type, kwargs=decision.kwargs)
            tasks.QueueTask(action)
        else:
            task = analyzer.TrackCompletion(objects, tasks.GetCurrentTask())
            if task.NeedsCorrection():
                tasks.Interupt()
                tasks.QueueTask(task.GetSteps())
        # t = nt

        # pr.disable()
        # ps = pstats.Stats(pr).sort_stats('cumtime')
        # ps.print_stats()
    # break

def Main() -> 0:
    global fcounter, comms, scheduler, objects, analyzer, builder, tasks, camera
    '''
        Callbacks
    '''
    fcounter = 1
    def SerialTestJetsonToV5( params ):
        pass

    def SerialTestV5ToJetson( params ):
        global fcounter
        print(f"Recieved: {fcounter}")
        for param in range(len(params)):
           print(params[param])
        fcounter += 1

    def UpdateMagCount( params ):
        global mag_cnt, __mag_cnt_lck__
        with __mag_cnt_lck__:
            mag_cnt = params[0]
            mg_copy = mag_cnt
        objects.SetMagCnt(mg_copy)
        
    def UpdatePos( params ):
        x = params[0]
        y = params[1]
        theta = params[2]
        position = Vec(x, y, 0)
        objects.UpdateRobot(position, theta)
        
    def OnTaskFinished( params ):
        tasks.OnTaskFinished(task_number=params[0])
    
    def NullUpdater( params ):
        comms.SendPacket("null_callback", (0))

    '''
    End Callbacks
    '''
    # global objects
    # Load serial Communications
    # camera = Vision(False)
    # camera.Start()
    # while True:
    #     camera.CollectObjects()
    comms = Communications()

    if DEBUG_MODE:
        sent = 1
        ctime = time.time()
        deltatime = 0
        ltime = ctime
        while(True):
            deltatime += (time.time() - ltime) * 1000
            ltime = time.time()
            #print(deltatime)
            if deltatime > 25:
                deltatime = 0
                b = comms.SendPacket("serial_test_jetson_to_v5", 3.14159, "Digits of PI:", "Today is the day we Win.")
                # print(f"Sent: {sent}")#, int((ltime - ctime) * 10) / 10, b)
                sent+=1
            time.sleep(0.005)
    # Create Scheduler
    scheduler = UpdateManager()
    #Init Game Object manager
    starting_vec = Vec(STARTING_POS[0], STARTING_POS[1], 0)
    objects = ObjectManager(starting_pos=starting_vec, starting_angle= STARTING_ANGLE, comms=comms)           
    # Init Game Analysis manager
    analyzer = Analyzer()

    # Init Task manager
    tasks = TaskManager(object_manager=objects)

    # Init Vision manager with reporting to Game Analysis
    # True for fake data
    camera = None # Vision(DEBUG_VISUALIZE)

    non_gui_thread = threading.Thread(target=GameLogic, args=(camera, tasks, analyzer, objects, scheduler, comms))

    # Register callbacks
    
    if DEBUG_MODE:
        comms.RegisterCallback("serial_test_v5_to_jetson", SerialTestV5ToJetson)
        comms.RegisterCallback("serial_test_jetson_to_v5", SerialTestJetsonToV5)
    else:
        comms.RegisterCallback("update_mag_count", UpdateMagCount)
        comms.RegisterCallback("task_finished", OnTaskFinished)
        comms.RegisterCallback("get_pos", UpdatePos)
    comms.Start()
    comms.WaitForTags()
    if comms.HasCallback("update_target_obj_dr_dtheta"):
        scheduler.ScheduledUpdate(objects.CommsUpdateTargetDrDth, 0.05)
    if comms.HasCallback("null_callback"):
        scheduler.ScheduledUpdate(NullUpdater, 0.01) # Ensures the brain Does not get held up on CIN
 
    
    # Start the non-GUI task in a separate thread
    non_gui_thread.start()

    if DEBUG_VISUALIZE:
        pass
        # app = QtWidgets.QApplication([])
        # visualize_game_objects(None)
        # timer = QtCore.QTimer()
        # timer.timeout.connect(visualization)
        # timer.start(50)
        # app.exec_()

    # GameLogic(camera, tasks, analyzer, scheduler, comms)

    return 0

if __name__ == '__main__':
    sys.exit(Main())