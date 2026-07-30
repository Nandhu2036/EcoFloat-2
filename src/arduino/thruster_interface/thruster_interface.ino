/**
 * ECO-FLOAT 2.0 - Low-level Thruster Control Sketch
 * Translates serial commands from the Raspberry Pi into PWM signals.
 */

#include <Servo.h>

// Pins
const int PIN_PORT_THRUSTER = 9;
const int PIN_STARBOARD_THRUSTER = 10;

// Servo instances for ESC control
Servo portEsc;
Servo starboardEsc;

void setup() {
  Serial.begin(115200);
  
  // Attach ESC pins
  portEsc.attach(PIN_PORT_THRUSTER);
  starboardEsc.attach(PIN_STARBOARD_THRUSTER);
  
  // Initialize ESC to neutral arm state (1500 microseconds)
  portEsc.writeMicroseconds(1500);
  starboardEsc.writeMicroseconds(1500);
  
  delay(2000); // Wait for ESC to arm
  Serial.println("[MCU] Esc thrusters armed and ready.");
}

void loop() {
  if (Serial.available() > 0) {
    String cmd = Serial.readStringUntil('\n');
    
    // Command format: "P1600 S1400" (port microsec, starboard microsec)
    if (cmd.startsWith("P") && cmd.indexOf(" S") > 0) {
      int sIndex = cmd.indexOf(" S");
      String portStr = cmd.substring(1, sIndex);
      String starStr = cmd.substring(sIndex + 2);
      
      int portVal = portStr.toInt();
      int starVal = starStr.toInt();
      
      // Bounded constraints (forward/reverse range)
      portVal = constrain(portVal, 1100, 1900);
      starVal = constrain(starVal, 1100, 1900);
      
      portEsc.writeMicroseconds(portVal);
      starboardEsc.writeMicroseconds(starVal);
      
      Serial.print("[MCU ACK] Port: ");
      Serial.print(portVal);
      Serial.print(" Starboard: ");
      Serial.println(starVal);
    }
  }
}