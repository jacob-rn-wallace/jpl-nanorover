# Struts

Spec and design record for `hardware/strut/strut.py` (run after `hardware/body/body.py`).

Four struts, two per side on the stud's axle stub. The sources give two numbers: **70 mm from the pivot
centre to the wheel axle centre**, and **65 mm wheels**. Everything else here is a placeholder choice.
- **Layers (|x| from the body centre):** stud flange face 72.25; inboard strut A boss 73.25 to 80.25 (7 mm); outboard strut B boss 81.25 to
  88.25; the stud's axle stub ends at 92.25, leaving 4 mm for a retainer. Each boss is 30 mm across with a 12.1 mm bore on the 12 mm axle.
- **Arms:** 3 mm plate, tapering from the 30 mm boss to an 18 mm axle boss, 70.00 mm between centres. Plate A is flush with the outer face of
  boss A and plate B with the inner face of boss B, 1 mm apart. Each arm carries a 6 mm wheel-axle stub out to the wheel plane.
- **Wheel envelopes:** the script uses plain 65 mm cylinders, 44.6 mm wide (inner face to the cone apex), for its pose checks (they overlap only their own axle stubs); `hardware/wheel/wheel.py` models the real wheel.
- **Stance:** the default pose has the arms 25 degrees below horizontal, a choice and not a sourced figure. The wheel bottoms are then at
  z = -32.1 (the box floor is 32 mm above the ground), axle spacing 126.9 mm and overall length 191.9 mm. With the arms
  horizontal the overall length is 205 mm, which fits JPL's "only 20cm long" caption.
- **Passing:** the script finds interference between strut A and strut B only when they point the same way (12 of 144 sampled angle
  pairs, all at equal angles), because each strut's wheel-axle stub crosses the other's layer at the tip. So the struts cannot swap
  places, which matches Tunstel's note that same-side struts cannot pass each other. That comes out of this layout; it is not a measured
  feature of the original.
- **Clearances:** no overlap between the struts and the casting, stud or nut at the default pose. The wheel envelopes overlap only their own axle stubs.
- **Mass:** about 27 g per strut in 6061 with the 6 mm axle stub (`TIP_MODE = "axle"`), 109 g for four; **22 g each, 89 g for four in the default `TIP_MODE = "motor"`** (no stub, a bore for the motor).
- **Track width:** the sources give none. With the wheel stack and collar outboard of the struts the overall width is 275.7 mm; the wheel's inboard end fits the photo (see `wheel-spec.md`), but the strut layout around it is a placeholder.
- **Tip mode (layout C, 2026-11-11).** `strut.py` has `TIP_MODE`: `"motor"` (default) replaces the 6 mm axle stub with a 10.1 mm bore through the tip boss and plate (4 mm of wall left in the 18 mm tip boss) and builds the wheel motor as its own part, `out/wheel_motors.step`: a 10 mm x 44.9 mm cylinder (maxon ECX SPEED 10 M 25.1 mm + GPX 10 A 4-stage 19.8 mm, 20.2 g each) plus a 3 mm output shaft (**diameter assumed**, not read from the catalogue) running to the wheel's collar. The front face sits as far toward the cone apex as the cone's inner radius allows less a 3 mm pad (assumed), so the tail ends at |x| = 79.45, 9.5 mm from the body face and 5.8 mm inboard of the wheel's inner face. `"axle"` keeps the earlier model. The same-hub check now includes the motors: it still finds interference only at the 12 equal-angle pairs (both wheels and motors in the same place, which cannot happen); one strut's motor against the other strut alone gives 0 (`hardware/drivetrain/motor_clearance.py`, for pads of 0, 3 and 6 mm). The cone constants in `strut.py` (`CONE_T`, `CONE_H`, `CONE_R`) are copies of the thin wheel in `wheel.py`; keep them in step.
- **Not modelled:** the strut-pivot motors and bearings, the potentiometers, how the wheel motor is fixed in the tip bore, the real arm outline, strut stops.
