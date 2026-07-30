# Electronics & Power Subsystem

This document lists the wiring connections, power routing, and signal channels.

## 1. Wiring & Power Distribution Diagram
```
              +-------------------------------------+
              |    12V LiFePO4 / LiPo Battery       |
              +------------------+------------------+
                                 |
         +-----------------------+-----------------------+
         |                                               |
         v (12V High-Amp)                                v (12V Regulated)
+--------+--------+                             +--------+--------+
|  BTS7960 Motor  |                             | UBEC Buck Rail  |
|  Driver Stack   |                             |    (5V 3A)      |
+--------+--------+                             +--------+--------+
         | (PWM Input from Pi)                           |
         +<-----------------------+                      v (5V power)
         |                        |             +--------+--------+
         v                        |             |  Raspberry Pi 4 |
+--------+--------+               |             |  Microprocessor |
| Dual 775 DC     |               |             +--------+--------+
| Marine Motors   |               |                      ^
+-----------------+               |                      | (USB Video)
                                  +----------------------+ USB Camera
```

## 2. BTS7960 Driver Pins
- `RPWM` / `LPWM`: Connects to GPIO hardware PWM pins on the Raspberry Pi.
- `R_EN` / `L_EN`: Pull-up to 5V rail to enable H-bridge channels.
