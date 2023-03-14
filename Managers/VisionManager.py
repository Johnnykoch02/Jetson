import cv2 as cv

class Vision:
    def __init__( self ) -> None:
        self.camera = cv.VideoCapture(0, cv.CAP_DSHOW)
        cv.namedWindow("test")
        pass
    def CollectObjects( self ) -> list:
        ret, frame = self.camera.read()
        if not ret:
            print("failed to grab frame")
            return
        cv.imshow("test", frame)
        cv.waitKey(1)
        return {0}
