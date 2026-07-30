import cv2
import time
import numpy as np

class USBWaterCamera:
    """
    Camera interface for capturing real-time surface video.
    Falls back to generating mock frames if no physical USB camera is connected.
    """
    def __init__(self, device_index=0, width=640, height=480):
        self.device_index = device_index
        self.width = width
        self.height = height
        self.cap = None
        self.is_mock = False
        self._init_camera()

    def _init_camera(self):
        self.cap = cv2.VideoCapture(self.device_index)
        if not self.cap or not self.cap.isOpened():
            print(f"[CAMERA] Warning: USB Camera at index {self.device_index} not found. Operating in MOCK mode.")
            self.is_mock = True
        else:
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.width)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.height)
            print(f"[CAMERA] Initialized USB Camera at index {self.device_index} ({self.width}x{self.height})")

    def get_frame(self):
        if self.is_mock:
            # Generate a mock green-blue water frame
            frame = np.zeros((self.height, self.width, 3), dtype=np.uint8)
            frame[:] = [100, 70, 30]  # Dark water color (BGR)
            return True, frame
        
        ret, frame = self.cap.read()
        if not ret:
            print("[CAMERA] Error reading frame from USB interface.")
            return False, None
        return True, frame

    def release(self):
        if self.cap and not self.is_mock:
            self.cap.release()
            print("[CAMERA] Released video device.")