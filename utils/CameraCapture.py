import cv2
import os

def CameraCapture(path_a:str, path_b:str):
    path_A = os.path.join(os.getcwd(), path_a)
    path_B = os.path.join(os.getcwd(), path_b)
    
    # Set-up capture object (Realsense Cam)
    cap = cv2.VideoCapture(1)
    
    # Interval between captures (ms) 
    capture_interval = int(1000 / 8)
    
    while True:
        # 960 Images
        number_images = 120 * 8
        
        # Capture and save images
        for i in range(number_images):
            # Capture Frame
            ret, frame = cap.read()
            
            # Filename for image
            filename = f'../{path_A}/image_{i}.jpg'

            # Save image
            cv2.imwrite(filename, frame)
            
            # Wait interval
            cv2.waitKey(capture_interval)
        
        # Prompt to repeat process
        repeat = input('Repeat process? (y/n)')
        if repeat.lower() != 'y':
            break
    
    cap.release()
    cv2.destroyAllWindows()
        