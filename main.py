import pyqtgraph as pg
import cProfile
import pstats
import sys
from PyQt5 import QtWidgets, QtCore
import threading
import time
DEBUG_VISUALIZE = True
from Testing.Visualize import *

def visualization():
    global objects
    visualize_game_objects(objects.GetAll())

def GameLogic(camera, tasks, analyzer):
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
        non_gui_thread = threading.Thread(target=GameLogic, args=(camera, tasks, analyzer))

        # Start the non-GUI task in a separate thread
        non_gui_thread.start()

        


def Main():
    global objects
    if DEBUG_VISUALIZE:
            app = QtWidgets.QApplication([])
            visualize_game_objects(None)
            timer = QtCore.QTimer()
            timer.timeout.connect(visualization)
            timer.start(50)
            app.exec_()

if __name__ == '__main__':
    sys.exit(Main())