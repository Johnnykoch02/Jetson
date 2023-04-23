from Serial.VexCommunications import *
from Managers.GameObjects import *
from Managers.GameAnalysis import *
from Managers.VisionManager import *
from Managers.GameSteps import *
from Managers.GameTasks import *
import pyqtgraph as pg
from PyQt5 import QtWidgets, QtCore
import cProfile
import pstats
import sys
import threading

DEBUG_VISUALIZE = True
from Testing.Visualize import *

def visualization():
    global objects
    visualize_game_objects(objects.GetAll())

def GameLogic(camera: Vision, tasks: TaskManager, analyzer: Analyzer):
    t = time.time()
    # Beat the game
    while True:

        for object in camera.CollectObjects():
            objects.TraceObject(object)

        nt = time.time()
        dt = nt - t

        if DEBUG_VISUALIZE:

            for bot in objects.GetBots():
                update_robot_position_and_velocity(bot, dt)

        # buf = objects.SerializeForComs()
        # comms.SendRawBuffer(buf)

        # analyzer.WaitForCompletion()

        # Task -> Actions -> Steps -> Directions
        # Reactive Program -> Reacts and responds its changing environment

        if tasks.AlmostFinished():
            decision = analyzer.FindBest(objects)

            # if objects.GetCurrentTarget() != decision.GetTarget():
            #     objects.SetCurrentTarget(decision.GetTarget())
            #     steps = builder.BuildSteps(decision)
            #     tasks.QueueTask(steps)
        else:
            pass
            # task = analyzer.TrackCompletion(objects, tasks.GetCurrentTask())
            # if task.NeedsCorrection():
            #     tasks.Interupt()
            #     tasks.QueueTask(task.GetSteps())
        t = nt

        #pr.disable()
        #ps = pstats.Stats(pr).sort_stats('cumtime')
        #ps.print_stats()
        #break

fcounter = 1
def test_function( params ):
    global fcounter
    print(f"Recieved: {fcounter}")
    #for param in range(len(params)):
    #    print(params[param])
    fcounter += 1

def Main() -> 0:
    # global objects
    # Load serial Communications
    comms = Communications()
    comms.RegisterCallback("test_function", test_function)
    comms.Start()
    comms.WaitForTags()

    sent = 1
    ctime = time.time()
    deltatime = 0
    ltime = ctime
    while(True):
        deltatime += (time.time() - ltime) * 1000
        ltime = time.time()
        #print(deltatime)
        if deltatime > 10:
            deltatime = 0
            b = comms.SendPacket("TestFunction", 145, 541, "this is a long test string for testing sending string from the jetson to the v5 brain")
            print(f"Sent: {sent}")#, int((ltime - ctime) * 10) / 10, b)
            sent+=1
        time.sleep(0.005)

    # Init Game Object manager
    # objects = ObjectManager()

    # Init Game Analysis manager
    # analyzer = Analyzer()

    # Init Game Step Builder
    # builder = StepBuilder()

    # Init Task manager
    # tasks = TaskManager()

    # Init Vision manager with reporting to Game Analysis
    # True for fake data
    # camera = Vision(DEBUG_VISUALIZE)

    # non_gui_thread = threading.Thread(target=GameLogic, args=(camera, tasks, analyzer))

    # # Start the non-GUI task in a separate thread
    # non_gui_thread.start()

    # if DEBUG_VISUALIZE:
    #     app = QtWidgets.QApplication([])
    #     visualize_game_objects(None)
    #     timer = QtCore.QTimer()
    #     timer.timeout.connect(visualization)
    #     timer.start(50)
    #     app.exec_()

    # GameLogic(camera, tasks, analyzer)

    return 0

if __name__ == '__main__':
    sys.exit(Main())