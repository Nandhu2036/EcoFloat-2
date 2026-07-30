import math
import time

class PropSteeringController:
    """
    Proportional feedback yaw steering controller and GPS search patterns.
    Translates pixel errors into motor PWM duty offsets.
    """
    def __init__(self, kp=0.8, base_speed=60, center_x=320):
        self.kp = kp
        self.base_speed = base_speed
        self.center_x = center_x
        
        # Explorer Lawnmower configuration
        self.heading = 0.0  # Degrees
        self.lawnmower_dir = 1  # 1 = East, -1 = West
        self.last_turn_time = time.time()

    def get_steering_error(self, target_x):
        """
        Returns horizontal error: positive is target right, negative is left.
        """
        return target_x - self.center_x

    def compute_differential_speeds(self, target_x):
        """
        Calculates port and starboard throttle settings based on target offset.
        Outputs bounded within [0, 100]% duty speeds.
        """
        error = self.get_steering_error(target_x)
        correction = self.kp * error
        
        # Differential yaw adjustments
        port_speed = self.base_speed + correction
        starboard_speed = self.base_speed - correction
        
        # Enforce physical constraints
        port_speed = max(0, min(100, port_speed))
        starboard_speed = max(0, min(100, starboard_speed))
        
        return int(port_speed), int(starboard_speed)

    def get_explore_speeds(self):
        """
        Generates lawnmower grid pathing search speeds.
        Simulates search steering logic using heading adjustments.
        """
        now = time.time()
        # Every 12 seconds, simulate reaching a boundary and turning 90 degrees
        if now - self.last_turn_time > 12:
            print("[NAVIGATION] Boundary reached. Initiating grid lane shift.")
            self.lawnmower_dir *= -1
            self.last_turn_time = now
            # Swing motors to rotate catamaran
            if self.lawnmower_dir == 1:
                return 70, 30  # Pivot East
            else:
                return 30, 70  # Pivot West
        
        # Glide straight down the current lane
        return self.base_speed, self.base_speed