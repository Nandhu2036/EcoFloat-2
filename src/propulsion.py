import time

class MarinePropulsionSystem:
    """
    Interface to send differential thruster commands to hardware PWM drivers (BTS7960).
    Falls back to mock console output on non-Pi platforms.
    """
    def __init__(self, pin_port=12, pin_starboard=13):
        self.pin_port = pin_port
        self.pin_starboard = pin_starboard
        self.is_raspberry_pi = False
        self._init_gpio()

    def _init_gpio(self):
        try:
            # Check if running on a Raspberry Pi
            with open("/proc/device-tree/model", "r") as f:
                model = f.read()
                if "Raspberry Pi" in model:
                    self.is_raspberry_pi = True
        except FileNotFoundError:
            pass

        if self.is_raspberry_pi:
            try:
                import RPi.GPIO as GPIO
                GPIO.setmode(GPIO.BCM)
                GPIO.setup(self.pin_port, GPIO.OUT)
                GPIO.setup(self.pin_starboard, GPIO.OUT)
                # Create PWM instances at 50Hz
                self.pwm_port = GPIO.PWM(self.pin_port, 50)
                self.pwm_starboard = GPIO.PWM(self.pin_starboard, 50)
                self.pwm_port.start(0)
                self.pwm_starboard.start(0)
                print(f"[PROPULSION] Initialized hardware PWM on GPIO {self.pin_port} and {self.pin_starboard}")
            except Exception as e:
                print(f"[PROPULSION] RPi.GPIO error: {e}. Falling back to MOCK propulsion.")
                self.is_raspberry_pi = False
        else:
            print("[PROPULSION] Non-Pi architecture. Simulated motor output active.")

    def set_thrust(self, port_percent, starboard_percent):
        """
        Command individual motor speeds (0-100% duty).
        """
        if self.is_raspberry_pi:
            self.pwm_port.ChangeDutyCycle(port_percent)
            self.pwm_starboard.ChangeDutyCycle(starboard_percent)
        else:
            # Simulated output
            pass

    def stop(self):
        self.set_thrust(0, 0)
        print("[PROPULSION] Thrusters deactivated (0% thrust).")

    def clean_up(self):
        self.stop()
        if self.is_raspberry_pi:
            import RPi.GPIO as GPIO
            self.pwm_port.stop()
            self.pwm_starboard.stop()
            GPIO.cleanup()
            print("[PROPULSION] GPIO channels released.")