from Classes.GameObject import *
import cv2 as cv
import random

class Vision:
    def __init__( self ) -> None:
        # self.camera = cv.VideoCapture(0, cv.CAP_DSHOW)
        # cv.namedWindow("test")
        pass
    def CollectObjects( self ) -> list[GameObject]:
        fake_data = list[GameObject]()
        for i in range(20):
            obj = GameObject()
            obj.id = i
            obj.position = Vec(random.randrange(-50,50), random.randrange(-50,50), 0)
            obj.type = ObjectType.FRISBEE
            fake_data.append(obj)
        # ret, frame = self.camera.read()
        # if not ret:
        #     print("failed to grab frame")
        #     return
        # cv.imshow("test", frame)
        # cv.waitKey(1)
        return fake_data
