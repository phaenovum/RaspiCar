""" raspicar_camera.py

SLW 01-23-2023
"""

import time
import cv2

class Camera:
    
    def __init__(self, width=800, height=600):
        # Calculate parameters
        self.width, self.height = width, height
        # Start video capture
        self.vid = cv2.VideoCapture(0)
        self.vid.set(cv2.CAP_PROP_FRAME_WIDTH, width)
        self.vid.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
        self.error = False
        
        
    def get_frame(self) -> numpy.ndarray:
        _, frame = self.vid.read()
        return frame
    
    
    def show_frame(self) -> bool:
        res, frame = self.vid.read()

        if not res:
            print("Video stream read errror")
            self.vid.release()
            self.error = True
            return False
            
        cv2.imshow("Frame", frame)
        key = cv2.waitKey(1)
        if key in (ord('q'), ord('Q'), 13, 27):
            return True
        else:
            return False
          
    
    def close(self):
        self.vid.release()
        cv2.destroyAllWindows()

#=================================================================================

duration = []

if __name__ == "__main__":
    cam = Camera()

    cnt = 0
    start_time = time.time()

    while True:
        if cam.show_frame():
            break
        cnt += 1

    end_time = time.time()
    cam.close()
    
    print(round(cnt / (end_time - start_time), 2), "frames per second")
        
