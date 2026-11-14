"""Hand check of the strut motors' wiring (docs/mechanical-spec.md item 6): wire lengths, wrap slack and bends.

Run: python3 hardware/strut/cable_check.py   (plain python). Figures are from strut.py and hub.py (collar, groove, shaft cross holes, the stop gaps of item 7) and assumptions (ASM) noted.
Strut A's two wires leave the motor tail through a notch in the collar, run along the arm's inboard face (a free 4 mm channel against the body wall), wind round the pivot boss in a ring of free space
(r = 15 to 19 mm, between the boss's inboard face at |x| = 73.25 and the wall at about 70) and enter the body through a 2 mm hole in the wall 19 mm above the axis. Strut B's wires leave the same way,
run in a 1.5 x 1.0 mm groove on its plate's inboard face across its boss to the hollow inner shaft, enter its 3 mm bore through a cross hole (|x| = 81.75), run inboard inside the shaft to a second cross
hole (|x| = 52.25, in the 1.5 mm window between the horn adapter and the gear plane) and wind round the shaft there before running to the same kind of wall hole.
"""
import math

TRAVEL = 345.0                     # degrees of strut travel (item 7); the cable sits at mid-travel, so it winds half that each way
HALF = math.radians(TRAVEL / 2 + 10)   # plus a margin of 10 degrees
WIRE_OD = 0.6                      # mm, 30 AWG silicone-insulated (ASM); 32 AWG would be about 0.45
STRUT_L = 70.0                     # SRC strut.py
TIP_EXIT_R = STRUT_L - 12.0        # the notch through the collar's pivot side: 58 mm from the pivot axis
BOSS_R, B_BORE_R = 15.0, 2.5       # SRC strut.py (boss 30 mm), the 5 mm shaft's radius

# strut A
along_arm = TIP_EXIT_R - BOSS_R
ring_r = BOSS_R + 2.0              # the ring's radius to the wire, 2 mm clear of the boss
ring_wrap = ring_r * HALF
to_wall = 12.0                     # from the ring to the wall hole's outer end, through the 3 mm hole (ASM)
inside = 25.0                      # from the hole's inner end to the board (ASM)
a_len = along_arm + ring_wrap + to_wall + inside
# strut B
b_arm = TIP_EXIT_R - B_BORE_R
b_shaft = 81.75 - 52.25
shaft_wrap_r = 3.0                 # the wire winds round the 5 mm shaft in a 1.5 mm window
shaft_wrap = shaft_wrap_r * HALF
b_to_wall = math.hypot(60.0 - 52.25, 49.0 - 30.0)   # from the shaft's exit to the wall hole's inner end, z = 49 at |x| = 60
b_len = b_arm + b_shaft + shaft_wrap + b_to_wall + inside
print(f"strut A, per wire: along the arm {along_arm:.0f} mm, ring wrap {ring_wrap:.0f} mm, to and through the wall {to_wall:.0f} mm, inside {inside:.0f} mm: {a_len:.0f} mm")
print(f"strut B, per wire: along the arm and groove {b_arm:.0f} mm, inside the shaft {b_shaft:.1f} mm, wrap round the shaft {shaft_wrap:.0f} mm, to the wall hole {b_to_wall:.0f} mm, inside {inside:.0f} mm: {b_len:.0f} mm")
print(f"bend radii: the ring (A) {ring_r:.0f} mm = {ring_r / WIRE_OD:.0f} wire diameters; the shaft wrap (B) {shaft_wrap_r:.1f} mm = {shaft_wrap_r / WIRE_OD:.1f} wire diameters (the usual rule is at least 5, so 3.0 mm is the limit for a 0.6 mm wire, ASM)")
print(f"the 1.5 mm window holds two wires side by side ({2 * WIRE_OD:.1f} mm) in one layer; the wrap is {math.degrees(2 * HALF) / 360:.2f} turns in all (half each way from mid-travel), so one layer is enough")
print("groove 1.5 x 1.0 mm in a 3.0 mm plate leaves 2.0 mm; the shaft's wall (5 mm outside, 3 mm bore) is 1.0 mm, with a 1.0 mm and a 1.2 mm cross hole")
print("current: the wheel motor (Pololu 3068) draws 0.15 A free-running and about 0.15 to 0.7 A in use (docs/hardware-spec.md, section 6); stall is 1.5 A at 6 V (briefly, then the driver's current limit); 30 AWG silicone wire is good for about 0.9 A continuously in free air (ASM), so a stall is a burst, not a steady load")
