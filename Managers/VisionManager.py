from Classes.GameObject import *
import cv2 as cv
import random
from Testing.Data import GenerateFakeData

class Vision:
    def __init__( self, generate_fake_data ) -> None:
        if generate_fake_data:
            self.fake_data = GenerateFakeData()
        else:
            self.fake_data = None
        # self.camera = cv.VideoCapture(0, cv.CAP_DSHOW)
        # cv.namedWindow("test")
        pass
    def CollectObjects( self ) -> list[GameObject]:
        # ret, frame = self.camera.read()
        # if not ret:
        #     print("failed to grab frame")
        #     return
        # cv.imshow("test", frame)
        # cv.waitKey(1)
        return self.fake_data
