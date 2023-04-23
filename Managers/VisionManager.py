from Classes.GameObject import *
import cv2 as cv
import torch
from pathlib import Path
import numpy as np
from Testing.Data import GenerateFakeData

def preprocess_image(image, img_size=640):
    h, w, _ = image.shape
    ratio = min(img_size / h, img_size / w)
    resized_image = cv.resize(image, (int(w * ratio), int(h * ratio)), interpolation=cv.INTER_LINEAR)
    new_image = np.full((img_size, img_size, 3), 114, dtype=np.uint8)
    new_image[: int(h * ratio), : int(w * ratio)] = resized_image
    return torch.from_numpy(new_image).permute(2, 0, 1).unsqueeze(0).float().div(255.0)

def draw_boxes(image, results, names, colors=None):
    for *xyxy, conf, cls in results:
        x1, y1, x2, y2 = map(int, xyxy)
        label = f"{names[int(cls)]}: {conf:.2f}"
        if colors is None:
            color = (255, 0, 0)
        else:
            color = colors[int(cls) % len(colors)]
        cv.rectangle(image, (x1, y1), (x2, y2), color, 2)
        cv.putText(image, label, (x1, y1 - 5), cv.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
    return image

class Vision:
    def __init__( self, generate_fake_data ) -> None:
        if generate_fake_data:
            self.fake_data = GenerateFakeData()
        else:
            self.fake_data = None
        self.camera = cv.VideoCapture(0, cv.CAP_DSHOW)
        # Load the model
        self.model = torch.hub.load('ultralytics/yolov5', 'custom', path="Z:/Model/Training/yolov5/runs/train/exp/weights/best.pt")
        cv.namedWindow("test")
        pass
    
    def CollectObjects( self ) -> list[GameObject]:
        ret, frame = self.camera.read()
        if not ret:
            print("failed to grab frame")
            return {}
        input_tensor = preprocess_image(frame)
        # Perform the inference
        with torch.no_grad():
            results = self.model(input_tensor)[0].cpu().numpy()
        # Filter the results with a confidence threshold (0.25 in this example)
        results = results[results[:, 4] > 0.25]

        # Draw the bounding boxes and labels on the image
        output_image = draw_boxes(frame, results, self.model.names)
        cv.imshow("test", output_image)
        cv.waitKey(1)
        return self.fake_data
