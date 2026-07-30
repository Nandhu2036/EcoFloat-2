# Design & Buoyancy Engineering Manual

This document details the hydrodynamic calculations and mechanical layout of the catamaran hull.

## 1. Buoyancy & Payload Model
- **Hull Material**: Fiberglass-reinforced shell with PETG internal support ribs.
- **Designed Weight Profile**:
  - Dry mass ($m_{dry}$): $6.0\text{ kg}$ (includes battery, thrusters, processor bay).
  - Designed payload limit ($m_{payload}$): $4.0\text{ kg}$ (collected plastics mesh weight).
  - Total operational mass ($M_{total}$): $10.0\text{ kg}$.
- **Displacement Draft**:
  At maximum $10\text{ kg}$ load, the required displaced water volume is:
  \[V_{disp} = \frac{M_{total}}{\rho_{water}} = \frac{10\text{ kg}}{1.0\text{ kg/Liter}} = 10.0\text{ Liters}\]
  The maximum twin-hull volume is $16.8\text{ Liters}$, placing the cruising draft at $59.5\%$ of hull height.

## 2. Metacentric Height ($GM$)
Spacing the two hulls by a center-to-center distance (beam width $B = 0.5\text{ m}$) provides a large transverse Moment of Inertia, guaranteeing a high metacentric height:
\[GM = KB + BM - KG\]
This geometry prevents roll oscillations when the collection net becomes unevenly loaded.
