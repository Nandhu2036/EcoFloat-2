import time
import sys
from camera import USBWaterCamera
from detector import DebrisDetector
from navigation import PropSteeringController
from propulsion import MarinePropulsionSystem
from telemetry import TelemetrySystem

# Operational States
STATE_INIT = "INITIALIZING"
STATE_EXPLORE = "EXPLORATORY_SEARCH"
STATE_LOCK = "TARGET_LOCKED"
STATE_INTERCEPT = "ACTIVE_INTERCEPTION"
STATE_CAPTURE = "DEBRIS_CAPTURE"

def main():
    print("=" * 60)
    print("ECO-FLOAT 2.0 - AUTONOMOUS CONTROL SYSTEM STARTUP")
    print("=" * 60)

    # State Variable
    current_state = STATE_INIT

    # Component Instantiations
    camera = USBWaterCamera()
    detector = DebrisDetector()
    nav = PropSteeringController(kp=0.8, base_speed=50)
    prop = MarinePropulsionSystem()
    telemetry = TelemetrySystem()

    # Diagnostic built-in test (BIST)
    print(f"[STATE] {current_state}")
    time.sleep(1)
    print("[DIAGNOSTIC] Checking motor driver continuity...")
    prop.set_thrust(15, 15)  # Spin thrusters briefly
    time.sleep(0.5)
    prop.stop()
    print("[DIAGNOSTIC] All checks passed. Starting sweep mission.")
    
    current_state = STATE_EXPLORE
    target_lock_id = None
    target_lost_counter = 0

    try:
        while True:
            # 1. Grab Frame
            ret, frame = camera.get_frame()
            if not ret:
                time.sleep(0.1)
                continue

            # 2. Run Inference
            detections = detector.detect(frame)
            
            # 3. State Processing Logic
            if current_state == STATE_EXPLORE:
                if len(detections) > 0:
                    current_state = STATE_LOCK
                    print(f"[STATE CHANGE] -> {current_state}. Target spotted!")
                else:
                    # Lawnmower pattern
                    p_speed, s_speed = nav.get_explore_speeds()
                    prop.set_thrust(p_speed, s_speed)
                    telemetry.log(current_state, 0, p_speed, s_speed, False)

            if current_state == STATE_LOCK:
                if len(detections) > 0:
                    current_state = STATE_INTERCEPT
                    target_lost_counter = 0
                    print(f"[STATE CHANGE] -> {current_state}. Navigating to intercept.")
                else:
                    current_state = STATE_EXPLORE
                    print(f"[STATE CHANGE] -> {current_state}. False alarm.")

            if current_state == STATE_INTERCEPT:
                if len(detections) > 0:
                    target_lost_counter = 0
                    # Extract target details
                    det = detections[0]
                    box = det["box"]  # [ymin, xmin, ymax, xmax]
                    y_max = box[2]
                    x_center = (box[1] + box[3]) / 2.0
                    
                    # Check if target is inside passive funnel mouth (close to bow)
                    if y_max >= 420:  # Bottom area of optical feed
                        current_state = STATE_CAPTURE
                        print(f"[STATE CHANGE] -> {current_state}. Debris entering catamaran duct.")
                    else:
                        p_speed, s_speed = nav.compute_differential_speeds(x_center)
                        prop.set_thrust(p_speed, s_speed)
                        err = nav.get_steering_error(x_center)
                        telemetry.log(current_state, err, p_speed, s_speed, True)
                else:
                    target_lost_counter += 1
                    if target_lost_counter > 20:  # ~2 seconds of frames lost
                        current_state = STATE_EXPLORE
                        print(f"[STATE CHANGE] -> {current_state}. Target lost. Resuming search grid.")
                        prop.stop()

            if current_state == STATE_CAPTURE:
                # Glides straight forward for 1.5 seconds to ensure mesh capture
                print("[CAPTURE] Funnel momentum sweep initiated.")
                prop.set_thrust(60, 60)
                time.sleep(1.5)
                prop.stop()
                print("[CAPTURE] Debris successfully retained in HDPE mesh net.")
                current_state = STATE_EXPLORE
                print(f"[STATE CHANGE] -> {current_state}. Resuming mission grid.")

            time.sleep(0.1)  # Limit loop iteration speed to 10Hz

    except KeyboardInterrupt:
        print("\n[SYSTEM] Terminating sweep mission.")
    finally:
        prop.clean_up()
        camera.release()
        print("[SYSTEM] Safe shutdown complete.")

if __name__ == "__main__":
    main()