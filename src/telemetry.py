import os
import json
import time

class TelemetrySystem:
    """
    Telemetry logger recording physical parameters (speeds, errors, locks, battery).
    Logs to a local JSON file under /data.
    """
    def __init__(self, log_dir="data"):
        self.log_dir = log_dir
        os.makedirs(self.log_dir, exist_ok=True)
        self.log_file = os.path.join(self.log_dir, "telemetry_history.json")

    def log(self, state, error, port_speed, starboard_speed, target_locked, battery_volt=11.8):
        data = {
            "timestamp": time.time(),
            "state": state,
            "steering_error": error,
            "port_pwm": port_speed,
            "starboard_pwm": starboard_speed,
            "target_locked": target_locked,
            "battery_voltage": battery_volt
        }
        
        try:
            # Load existing
            history = []
            if os.path.exists(self.log_file):
                with open(self.log_file, "r") as f:
                    try:
                        history = json.load(f)
                    except json.JSONDecodeError:
                        pass
            
            # Keep log history reasonable
            history.append(data)
            if len(history) > 1000:
                history = history[-1000:]
                
            with open(self.log_file, "w") as f:
                json.dump(history, f, indent=2)
        except Exception as e:
            print(f"[TELEMETRY] Logging error: {e}")