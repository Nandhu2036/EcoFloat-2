# Software tracking & Pathing Pipeline

This document details the algorithmic logic of the autonomous skimmer.

## 1. Video Processing & Inference
- Resolution: $640 \times 480$ pixels.
- Inference Engine: TensorFlow Lite C++ / Python interpreter.
- Model: Quantized MobileNetV2-SSD trained on Custom Debris Dataset (PET bottles, cups).
- Frame rate: ~10 FPS.

## 2. Navigational Control Logic
The tracking script computes the horizontal error $\Delta e$ from the target center $X_c$:
\[\Delta e = X_c - 320\]
Applying proportional correction, the target thruster speeds are defined as:
\[Speed_{port} = Base\_Speed + K_p \cdot \Delta e\]
\[Speed_{starboard} = Base\_Speed - K_p \cdot \Delta e\]
Where $K_p$ is set to $0.8$ after calibration testing.
