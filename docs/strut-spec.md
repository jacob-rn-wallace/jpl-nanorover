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
- **Mass:** about 27 g per strut in 6061 (an estimate), 109 g for four.
- **Track width:** the sources give none. With the wheel stack and collar outboard of the struts the overall width is 275.7 mm; the wheel's inboard end fits the photo (see `wheel-spec.md`), but the strut layout around it is a placeholder.
- **Not modelled:** the strut-pivot motors and bearings, the potentiometers, the wheel gearmotors, the real arm outline, strut stops.
