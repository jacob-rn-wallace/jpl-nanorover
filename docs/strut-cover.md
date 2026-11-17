# Covering the strut's wire channel and the tube end (2026-11-17)

Owner's idea: split the arm into a 2 mm pocketed base and a 1 mm **skin on the inboard face**, so the wiring is hidden and the open end of the spindle tube (the square hole, the back of the gearmotor) is closed flush. Owner's conditions: investigate **screws plus a gasket**; **epoxy only if the part never has to be opened**, and in that case **rigid conductor rails instead of wires**. Numbers: `hardware/strut/cover_study.py` (plain python3). Tags as elsewhere: ASM assumption, ESTIMATE my arithmetic.

## What the geometry already gives us
- The tube starts at the collar's inboard face and the motor's tail is 4 mm inside it (`strut.py`: the motor is flush with the plate, the collar stands 4 mm proud). **A skin over the collar end therefore needs no change to the motor or the tube**: it closes a 4 mm pocket in front of the motor tail, where the leads can turn toward the notch and channel (this corrects my earlier remark that the motor would move 1 mm deeper).
- On strut B (outer) the inboard face of boss and plate are one flat plane, so one skin covers the whole arm. On strut A (inner) the pivot boss also stands 4 mm proud of the plate, and the arm faces the body wall at 3.25 mm: its inboard side is hardly visible. A skin on A is for parts commonality; B is where it matters.

## Option 1: screws and a gasket (serviceable; my recommendation)
- **Gasket:** a 0.5 mm silicone cord in a 0.65 x 0.40 mm groove cut in the base round the channel and the tip pocket (squeeze 20%, groove 76% full), with the skin landing on bare metal. The metal-to-metal stop sets the squeeze, so it does not depend on screw torque. A flat die-cut gasket under a 1 mm skin would depend on torque and is not recommended.
- **Screws:** M1.6 A2, about 19 per strut (two rows at 9 mm pitch beside the groove, six round the tip cap, three at the pivot), 76 for the rover, about 9 g. Thread engagement in the 2 mm base is 1.25 d, enough for a cover (it carries no structural load). Heads: a 1 mm skin is only just deep enough for a countersunk M1.6, so use low-head screws in shallow counterbores, or take the skin to 1.2 mm (the base stays at 2). The rows of small heads match the bezel's six screws and the lid cams' round heads.
- **Cost:** the skin is no longer part of the section. The arm's bending stiffness to a sideways knock falls to **32% of the monolithic 3 mm plate** (the two layers slide), which is a tip deflection of 0.20 mm against 0.06 mm for 5 N (ASM), and a root stress of 13 MPa (factor 21 on yield). Fine at this size, but it is a real loss of stiffness, and out-of-plane stiffness is the weak direction. The vertical (in-plane) strength that carries the wheel is unchanged.
- **Serviceable:** lift the skin, replace a motor lead, put it back with a new cord.

## Option 2: bonded skin with rigid rails (permanent)
- Bonded, the section acts as one: **97% of the monolithic stiffness** (0.07 mm, 7 MPa); no screws or gasket; the cleanest finish. The cost is that nothing inside can ever be repaired: a failed wheel motor means a new strut.
- **Rails:** a 0.8 mm FR-4 strip with two 1.0 mm traces fits a 3.0 x 1.0 mm channel, with solder pads at the motor end and the pivot end (the pivot end meets the hub shaft's cross hole, soldered once). Two ounce copper: 39 mohm out and back over 80 mm, 63 mV and 0.10 W at the motor's assumed stall current (1.6 A, ESTIMATE; **check the #3068's stall current against its datasheet**), ampacity 4 A (IPC-2221, 10 degree rise); one ounce also works (79 mohm, 2.4 A) but with less margin. The rail is also the insulator and the connection point; the motor's own leads are the only wire left, and it is short and inside the tube pocket.
- The motor can still be replaced if the **tube end** stays removable: bond the skin to the arm only, and close the 4 mm pocket with a small separate flush screwed cap (the cap makes the one exception to "never opened").

## Recommendation
**Option 1, with the cord gasket and low-head M1.6 screws, and the skin at 1.2 mm.** Reasons: the motors and leads are the part most likely to need service (the heat path through the bore is an untested estimate), the stiffness loss is acceptable, and a prototype that cannot be opened is a bad choice before anything has been measured. Revisit Option 2 once the drive has run for a long time; the rail channel is the same, so the base part does not change.

## Still open
1. How the stiffness changes if the skin's screws are added at the pivot boss (not modelled; slip is the worst case shown).
2. Whether anodising or a conformal coat is needed under the rails for isolation (a bare aluminium base touching a bare trace would short it; solder mask covers this).
3. The model: pocket, groove, tip pocket cap, skin parts and screw holes in `strut.py` are not drawn yet; the interference check and the renders must be re-run afterwards.
4. The motor's stall current and lead length (ESTIMATE).
