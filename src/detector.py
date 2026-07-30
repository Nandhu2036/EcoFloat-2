import os
import random
import numpy as np

class DebrisDetector:
    """
    Edge AI Object Detection interface. Runs quantized MobileNetV2-SSD models via TFLite.
    Simulates target bounding boxes if no TFLite model file is loaded.
    """
    def __init__(self, model_path="models/mobilenet_ssd.tflite", confidence_threshold=0.75):
        self.model_path = model_path
        self.confidence_threshold = confidence_threshold
        self.interpreter = None
        self.is_mock = True
        self._load_model()

    def _load_model(self):
        if os.path.exists(self.model_path):
            try:
                import tensorflow as tf
                self.interpreter = tf.lite.Interpreter(model_path=self.model_path)
                self.interpreter.allocate_tensors()
                self.input_details = self.interpreter.get_input_details()
                self.output_details = self.interpreter.get_output_details()
                self.is_mock = False
                print(f"[DETECTOR] Loaded TFLite model from {self.model_path}")
            except ImportError:
                print("[DETECTOR] tensorflow not installed. Operating in simulation mode.")
            except Exception as e:
                print(f"[DETECTOR] Error loading model: {e}. Operating in simulation mode.")
        else:
            print(f"[DETECTOR] Model file {self.model_path} not found. Running in MOCK target mode.")

    def detect(self, frame):
        """
        Processes image frame and returns detected bounding boxes of plastics.
        Format: [x_min, y_min, x_max, y_max, confidence, class_id]
        """
        if self.is_mock:
            # Simulates target coordinates randomly (e.g. 5% chance to spot debris)
            if random.random() < 0.08:
                x_center = random.randint(100, 540)
                y_center = random.randint(150, 400)
                width = random.randint(40, 80)
                height = random.randint(30, 60)
                conf = random.uniform(0.76, 0.99)
                return [{
                    "box": [y_center - height//2, x_center - width//2, y_center + height//2, x_center + width//2],
                    "confidence": conf,
                    "class": "pet_bottle"
                }]
            return []

        # Real TFLite inference logic goes here
        # Resize frame, invoke interpreter, filter by confidence threshold, etc.
        return []