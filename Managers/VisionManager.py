from Classes.GameObject import *
from Managers.CameraManager import *
import cv2 as cv
import torch
from pathlib import Path
from Testing.Data import GenerateFakeData

from models.common import DetectMultiBackend
from models.experimental import attempt_load
from utils.general import non_max_suppression, scale_boxes
from utils.dataloaders import letterbox
from utils.torch_utils import select_device
from utils.plots import Annotator, colors, save_one_box

import os
import sys
import platform

FILE = Path(__file__).resolve()
ROOT = FILE.parents[0]  # YOLOv5 root directory
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))  # add ROOT to PATH
ROOT = Path(os.path.relpath(ROOT, Path.cwd()))  # relative

DEFAULT_SIZE = 480

def preprocess_image(image, img_size=DEFAULT_SIZE):
    img = letterbox(image, img_size, stride=32)[0]
    return torch.from_numpy(img).permute(2, 0, 1).unsqueeze(0).float().div(255.0)


class Vision:
    def __init__( self, generate_fake_data ) -> None:
        # if generate_fake_data:
        #     self.fake_data = GenerateFakeData()
        # else:
        #     self.fake_data = None
        self.camera = CameraManager()
        # Load the model
        weights = "E:/Jetson/best.pt" if platform.system() == "Windows" else "/home/robot/Jetson/best.pt"
        self.device = select_device('cpu') if platform.system() == "Windows" else select_device() # use 'cpu' if GPU is not available
        self.model = DetectMultiBackend(weights, device=self.device, dnn=False, data=ROOT / 'data/coco128.yaml', fp16=False)
        self.model.eval()

        if platform.system() == "Windows":
            cv.namedWindow("Labels")
    
    def Start(self):
        self.model.warmup(imgsz=(1 if self.model.pt or self.model.triton else 1, 3, *(DEFAULT_SIZE, DEFAULT_SIZE)))
        self.camera.Start()

    def CollectObjects( self ) -> list:

        dt = time.time()
        frame = self.camera.GetFrame()
        if frame is None:
            return None
        
        img = cv.resize(frame, (DEFAULT_SIZE, DEFAULT_SIZE), interpolation=cv.INTER_LINEAR)

        output_frame, detections = process_frame(img, self.model, self.device)
        print("Got Detection:", (time.time() - dt) * 1000, "ms")

        output_frame = cv2.cvtColor(output_frame, cv2.COLOR_RGB2BGR)

        if platform.system() == "Windows":
            # Display the frame with detections
            cv.imshow("Labels", output_frame)

            cv.waitKey(1)
            # return self.fake_data
        else:
            print(detections)


def preprocess_image(image, img_size=DEFAULT_SIZE):
    return torch.from_numpy(image).permute(2, 0, 1).unsqueeze(0).float().div(255.0)

def process_frame(frame, model, device, img_size=DEFAULT_SIZE, conf_thres=0.25, iou_thres=0.45):

    # Preprocess the frame
    input_tensor = preprocess_image(frame, img_size=img_size).to(device)
    
    # Perform the inference
    with torch.no_grad():
        pred = model(input_tensor, augment=False, visualize=False)[0]

    # Apply NMS
    pred = non_max_suppression(pred, conf_thres, iou_thres, None, False, 1000)

    # Process the detections
    detections = []
    annotator = Annotator(frame, line_width=3, example=str(model.names))
    for i, det in enumerate(pred):  # detections per image
        if len(det):
            det[:, :4] = scale_boxes(input_tensor.shape[2:], det[:, :4], frame.shape).round()
            for *xyxy, conf, cls in det:
                c = int(cls)
                label = f"{model.names[int(cls)]}: {conf:.2f}"
                annotator.box_label(xyxy, label, color=colors(c, True))
                # color = (0, 0, 255)
                # cv.rectangle(frame, (x1, y1), (x2, y2), color, 2)
                # cv.putText(frame, label, (x1, y1 - 5), cv.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 0), 2)
                
                detections.append((xyxy, conf, cls))
    return annotator.result(), detections