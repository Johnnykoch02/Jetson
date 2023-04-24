import socket
import numpy as np
import cv2
from PIL import Image
import threading
import asyncio
import time

class CameraManager:
    def __init__(self) -> None:
        self.server_ip = "192.168.1.92"
        self.server_port = 8798
        self.frame_width = int(1456 / 2)
        self.frame_height = int(1088 / 2)
        self.frame_size =  self.frame_width * self.frame_height * 4
        self.__managed_thread = asyncio.new_event_loop()
        self.__lock = threading.Lock()
        self.__lastframe = None
        self.__frame = None

    def __receive_frame(self, conn: socket.socket, frame_size: int):
        frame_data = b""
        bytes_received = 0
        
        while bytes_received < frame_size:
            data = conn.recv(frame_size - bytes_received)
            frame_data += data
            bytes_received += len(data)
        
        return frame_data
    
    def __ReadFrames(self):
        # cam = cv2.VideoCapture(0, cv2.CAP_DSHOW)
        # while True:
        #     _, self.__frame = cam.read()
        while True:
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                    sock.connect((self.server_ip, self.server_port))
                
                    try:
                        while True:
                            frame_data = self.__receive_frame(sock, self.frame_size)
                            frame = np.frombuffer(frame_data, dtype=np.uint8).reshape((self.frame_width,self.frame_height, 4))
                            frame = Image.frombytes('RGBA', (self.frame_width,self.frame_height), frame).convert('RGB')
                            frame = np.array(frame)
                            # frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
                            with self.__lock:
                                self.__frame = frame
                    except KeyboardInterrupt:
                        print("Closing connection...")
            except KeyboardInterrupt:
                print("Exiting safely")


    def __run_coroutine(self):
        asyncio.set_event_loop(self.__managed_thread)
        self.__managed_thread.run_until_complete(self.__ReadFrames())

    def GetFrame(self, wait: bool = False):
        with self.__lock:
            # if self.__lastframe != self.__frame:
            #     self.__lastframe = self.__frame
                return self.__frame
        # if wait:
        #     timeout = 5
        #     while timeout > 0:
        #         timeout -= 1
        #         time.sleep(0.1)
        #         with self.__lock:
        #             if self.__lastframe != self.__frame:
        #                 self.__lastframe = self.__frame
        #                 return self.__frame

        return None

    def Start(self):
        threading.Thread(target=self.__run_coroutine).start()
