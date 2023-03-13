from Serial.VexCommunications import *
from Managers.GameObjects import *
from Managers.GameAnalysis import *
from Managers.VisionManager import *
from Managers.GameSteps import *
from Managers.GameTasks import *
import sys

#comms = Communications()
#byte = comms.RegisterCallback("my_tag", callback)
#comms.Start()

def Main( args ) -> 0:
    # Load serial Communications
    comms = Communications()
    comms.Start()

    # Init Game Object manager
    objects = ObjectManager()

    # Init Game Analysis manager
    analyzer = Analyzer()

    # Init Game Step Builder
    builder = StepBuilder()

    # Init Task manager
    tasks = TaskManager()

    # Init Vision manager with reporting to Game Analysis
    cam = Vision()
    
    # Beat the game
    while True:
        for object in cam.CollectObjects():
            objects.TraceObject(object)

        analyzer.WaitForCompletion()

        if tasks.AlmostFinished():
            decision = analyzer.FindBest(objects)
            if objects.GetCurrentTarget() != decision.GetTarget():
                objects.SetCurrentTarget(decision.GetTarget())
                steps = builder.BuildSteps(decision)
                tasks.QueueTask(steps)
        else:
            task = analyzer.TrackCompletion(objects, tasks.GetCurrentTask())
            if task.NeedsCorrection():
                tasks.Interupt()
                tasks.QueueTask(task.GetSteps())


    return 0

if __name__ == '__main__':
    sys.exit(Main())