# Hardware specification: what is chosen, what is working, what is open

Started 2026-11-13. Goal (owner, 2026-11-13): specify as much of the rover's own hardware as possible. Nothing is ordered, and purchasing is deferred indefinitely (owner), so every part here is a paper choice.

Tags: **owner** = decided by the owner; **working** = my recommendation, accepted by the owner as the working choice; **verified** = figure read from a datasheet or listing (source named); **assumed** = my estimate or memory, unchecked. The old placeholders in `hardware/body/layout.py` still carry assumed sizes and masses.

## 1. Chosen (owner or working)

| Subsystem | Part | Tag | Notes |
|---|---|---|---|
| Controller | Microchip PIC32MX250F128B | owner (family), figures assumed | about 20 mA at 40 MHz (family summary scaled by me, not the full datasheet table). |
| Radio | Digi XBee 3 802.15.4, non-PRO, U.FL (XB3-24AUM-J) | owner | 40 mA transmit at +8 dBm, 15 mA receive, 2 uA power-down (not from the full datasheet table). Not ordered. |
| Antenna | Taoglas WPC.25A.07.0150C patch, 25 x 25 x 5.5 mm | owner | Behind a flush 27 mm square RF window in the -y face. Not ordered. |
| Strut servos (4) | Feetech STS3215, 12 V variant (C018 or C047) | owner | 30 kg.cm stall (verified, [Core Electronics datasheet](https://core-electronics.com.au/attachments/uploads/sts3215-smart-servo-datasheet-translated.pdf)); 2.7 A stall and 180 mA no-load at 12 V; 45.2 x 24.7 x 35 mm; about 55 g; 12-bit magnetic encoder with position, load, current and temperature feedback ([listing](https://servodatabase.com/servo/feetech/sts3215)). Listings disagree on sub-model codes, so check the exact code at purchase. |
| Wheel motors (4) | Pololu #3068 gearmotor, 10 x 12 x 25 mm | owner | No encoder. See 2. |
| Solar cells | Anysolar IXOLAR: 6 x SM940K09L, 2 x SM401K08TF, 1 x SM531K08TFS per lid; four SM940K09L per end face | owner | Each part has Vmpp about 4.5 to 5 V (SM940K09L 5.02 V, 36.6 mA; SM531K08TFS 4.46 V, 205 mA; `docs/body-redesign.md`, preliminary datasheets). |
| Charger | **TI BQ25185**, 1-cell, 1 A linear charger with power path | working (2026-11-13) | See 3. |
| Wheel counting | **Back-EMF counting** | owner (2026-11-13) | See 2. |
| Battery cell | **1S LiPo, 1000 mAh, 25C class: Overlander SKU 2809** (retailer listings: 3.7 V, 25C constant and 50C burst; about 48 x 30 x 9 mm and 28.5 g, or 50 x 31 x 9 mm and 28 g) | working (2026-11-13) | See 4. Datasheet not retrieved (Overlander's pages returned 404); protection circuit not confirmed, so assume none. |
| Servo and wheel rail | **TI TPS61288** boost to about 7.4 V | working (2026-11-13) | See 4. |
| Logic rail | **TI TPS63802** buck-boost to 3.3 V | working (2026-11-13) | See 4. |

## 2. Wheel counting: back-EMF (owner, 2026-11-13)

The wheel motors carry no encoders, and there is no room for one in the 10 mm motor envelope, so wheel travel is counted from the motor's back-EMF.

- **Method (assumed, to be worked out):** the H-bridge briefly opens (a short coast gap each PWM period), the controller reads the motor terminal voltage, and the speed follows from it (EMF is proportional to speed). Counts come from integrating speed over time.
- **Consequences to model (assumed):** poor accuracy at low speed and near stall, a direction sign taken from the drive command, and drift from the motor constant changing with temperature and battery sag. This is odometry error the sim does not yet have (open item in the handover: wheel slip and scale errors). When the sim gets them, back-EMF counting should be a separate, larger error than an encoder would give.
- **Needs from hardware:** an ADC channel per motor (the PIC32MX250 has 10-bit ADC channels; the count needed is the open pin-allocation question) or a bridge with a sense output.
- **Era fit:** the period's hobby and academic robots (Handy Board class) counted wheels with cheap sensors or inferred speed from motor current. Back-EMF is in that spirit.

## 3. Charger: TI BQ25185 (working, 2026-11-13)

- **What it is (verified from TI's listings):** BQ25185 1-cell, 1 A standalone linear battery charger with power path, factory mode and battery-tracking VINDPM; input 3.0 to 18 V (25 V tolerant); charge current 5 mA to 1 A set by the ISET pin; input current limit 100, 500 or 1100 mA set by the ILIM/VSET pin; system output up to 3.125 A, regulated at 4.5 V; VINDPM tracks the battery with a 330 mV offset when VBAT is above 3.5 V ([TI datasheet](https://focus.ti.com/document-viewer/bq25185/datasheet), [product page](https://ti.com/product/BQ25185)).
- **Cell wiring (my proposal):** put all nine cell parts of both lids in parallel, one rail of about 4.5 to 5 V, behind a diode per lid so that a shaded lid does not load a lit one. The SM531K08TFS (4.46 V) will pull the 5.02 V parts down slightly; accepted.
- **Why this part (my reasoning):** the input voltage regulation backs the charger off in dim light instead of collapsing the cell voltage, which is a crude maximum-power-point control; a lid is about 3 W in full sun (about 0.6 A at 5 V, my estimate from the datasheet figures) and tens of mW indoors, inside the 1 A limit; it needs no inductor.
- **Rejected:** BQ25570 (output at most about 110 mA, built for a single small cell; [datasheet](https://cdn.sparkfun.com/assets/a/a/9/0/8/bq25570_Datasheet.pdf)); BQ24074 as the fallback (1.5 A; its input regulation threshold is not battery-tracking; [datasheet](https://www.ti.com/lit/gpn/bq24074)).
- **Not verified:** solar and MPPT behaviour in the full datasheet (SLUSF65), the package size (my "2 x 2 mm" was from memory), and the minimum useful input. A linear charger from 5 V to a 3.7 V battery wastes about a quarter of the power as heat (my arithmetic).

## 4. Battery sizing (`hardware/body/battery_sizing.py`, 2026-11-13)

**Correction to my earlier statement.** I said a 1S 500 mAh cell could not feed the servos because the STS3215 draws 2.7 A at 12 V, "about 9 A at the battery". That was the locked-rotor current, which the loads never need: the strut loads (172 mN.m to hold, 343 mN.m to push with a pair, `docs/drivetrain-spec.md`) are about 6 to 12% of the 2.94 N.m stall torque, so the servo current is about 0.16 to 0.32 A per servo (torque / 1.09 N.m per A, assuming linear torque and current, an assumption), and the battery supplies the winding loss, not V times that current. The firmware must still limit servo torque so that a jam cannot reach the stall current.

**Result (my model, assumed figures noted in the script):** battery-side load, before converter loss:

| Case | x1 load margin | x2 load margin (idle 30 mA) |
|---|---|---|
| Driving, struts holding (wheels, camera, controller, radio) | 1.6 to 4.2 W | 4.1 W |
| Posing one strut | 1.4 to 4.0 W | 4.1 W |
| Self-righting (one pair pushing, two holding) | 2.3 to 4.9 W | 7.5 W |

The range in the x1 column is the servo idle current, which the sources disagree on: 6 mA (Feetech datasheet, machine-translated; [servodatabase](https://servodatabase.com/servo/feetech/sts3215) 60 mA) or 30 mA ([DFRobot](https://www.dfrobot.com/product-2962.html)). **Four servos idling cost 0.3 W at 6 mA and 2.9 W at 60 mA, so the idle current, not the lifting, sets the running power.** It is the first thing to measure when hardware exists, and two firmware levers exist: torque off between moves (if the 345:1 gearing holds a pose unpowered, unverified) and a lower supply voltage.

**Options at the worst realistic case (self-right at x2 margin, idle 30 mA, 85% converters):**

| Option | Energy | Peak at the pack | C-rate | Driving hours |
|---|---|---|---|---|
| 1S 500 mAh, servos on 12 V boost | 1.85 Wh | 2.9 A | 5.9 C | 0.6 |
| 1S 1000 mAh, servos on 12 V boost | 3.70 Wh | 2.9 A | 2.9 C | 1.1 |
| 1S 1000 mAh, servos on 7.4 V boost | 3.70 Wh | 2.7 A | 2.7 C | 1.4 |
| 2S 500 mAh, servos straight off the pack | 3.70 Wh | 1.2 A | 2.4 C | 1.6 |

**Room (assumed 400 Wh/L pouch cell, from memory):** the placeholder bay (5 x 30 x 24 mm) holds about 1.4 Wh (390 mAh), too small; the whole 16 mm gap between the servo pairs (16 x 30 x 24 mm) holds about 4.6 Wh (1250 mAh at 3.7 V). The battery placeholder in `layout.py` should grow to that gap.

**Working recommendation (mine, awaiting the owner's word):**
- **1S, about 1000 mAh, 3C or better, filling the 16 mm gap**, in place of the 12 g, 500 mAh placeholder (about 20 g; to be settled when a real cell is chosen).
- **One boost converter to about 7.4 V for the servos and wheel drivers.** The STS3215's listed range is 4 to 14 V, so 12 V is not needed; at 7.4 V stall torque is about 1.8 N.m (my scaling, 2.6 times the largest need with margin) and speed about 60% of the 12 V figure (to be checked against the posing time).
- **A 3.3 V buck-boost for the logic** (a 1S pack falls to 3.0 V, too low for an LDO at 3.3 V).
- **The BQ25185 stays** as the charger (1S, 1 A), so the cell wiring in section 3 stands.
- **2S rejected for now:** it would halve the peak pack current and drop the servo boost, but the 5 V cell string cannot charge a 2S pack without a boost-charger, which is more parts than the one boost it saves.
- **Not checked:** the wheel motors' supply voltage (the docs give their no-load current at 6 V; they may run straight from the 1S pack or from the 7.4 V rail through PWM), and which 1S cell supplies 3C in this size.
**Picks (2026-11-13, working choices; figures are from TI's pages and retailer listings, not the full datasheets):**
- **Cell: Overlander SKU 2809, 1S 1000 mAh, 25C constant and 50C burst.** The 25C rating is far more than the 2.7 A (2.7C) worst case needs; the point is that a small cell of this kind exists at 1000 mAh with real discharge headroom. It lies in the 16 mm gap (10 x 51 x 31 mm box in `layout.py`, thickness along x), 28.5 g instead of the 12 g placeholder: **the body contents are now over the 386 g budget by 51 g** (was 35 g); the budget is deferred (owner). **Rejected:** the DNK602272 (74 x 22 x 6 mm, 16.7 g, 1000 mAh, with a protection circuit) because its sheet gives only 1C maximum continuous (1 A) and 3C for 10 ms, and its protection trips at 3 to 5 A ([DNK sheet](https://www.dnkpower.com/wp-content/uploads/2023/11/DNK602272-3.7V-1000mAh-Lipo-Battery-Specification.pdf)); our worst case is 2.7 A for self-righting and about 1.4 A at the unmargined load. A cell with a protection circuit and a higher rate is the thing to look for if a cell without protection is unwelcome. **Needed:** a protection circuit (over-discharge, over-current, short) on the power board; the cell is assumed to have none. Capacity check: 1.0 Ah at 3.7 V is 3.7 Wh, about 95 min of driving (`power_budget.py`, scenario D).
- **Servo and wheel rail: TPS61288** (TI, [product page](https://ti.com/product/TPS61288)): input 2.0 to 18 V with 2.4 V minimum start-up, output 4.5 to 18 V, 15 A peak switch current limit, 110 uA typical quiescent current into VOUT, 2.1 uA maximum shutdown current, PFM at light load, VQFN-HR about 3 x 2 mm (the page also says 2.5 x 3.0 mm), active. At 7.4 V and 1.2 A (8.9 W) the pack side carries about 3.5 A at 3.0 V and 85% (my arithmetic), inside the switch limit. **Not confirmed:** its load disconnect (the page does not mention one: with the converter off, the input still feeds the output through the inductor and diode path, so the servos need a load switch or the converter must be enabled only when moving, to be settled in the schematic) and its maximum output current. Rejected: TPS61022 and TPS61099 (output limited to 5.5 V; [TPS61022](https://ti.com/document-viewer/TPS61022/datasheet), [TPS61099](https://www.ti.com/product/tps61099)); TPS61093 (1.6 to 6 V input, up to 17 V output, but a small-current part and I did not confirm its current limit).
- **Logic rail: TPS63802** (TI, [datasheet](https://ti.com/lit/pdf/SLVSEU9)): 1.3 to 5.5 V input (1.8 V to start), 2 A at 3.3 V for inputs of 2.3 V and up, 11 uA quiescent current, 10-pin VSON-HR (3.0 x 2.0 mm by one page, 1.4 x 2.3 mm by another). A pack down to 3.0 V is inside its range. The 3.3 V load is about 0.3 to 0.45 A (controller, radio, camera, ToF; my sum), so 2 A is generous; **the alternative is the TPS63900** (400 mA at 3.3 V, 75 nA quiescent current, 2.5 x 2.5 mm; [page](https://www.ti.com.cn/lit/gpn/TPS63900)) if the keep-alive tier of `docs/body-redesign.md` wants a very-low-quiescent rail, with the 3.3 V loads that exceed 400 mA moved to a second converter.
- **Changed with the cell:** `power_budget.py` and the sim's `batteryWh` (1.85 to 3.70 Wh; 21 sim checks pass).

## 5. Still to specify (queue, in order)

1. Ranging sensor: **ST VL53L5CX** is the candidate (verified, [datasheet](https://cdn.sparkfun.com/assets/6/e/3/0/6/vl53l5cx-datasheet.pdf): 63 degree diagonal field, 6.4 x 3.0 x 1.5 mm, 15 Hz maximum at 8 x 8 and 60 Hz at 4 x 4; about 100 mA typical and 150 mA peak on the [Pololu carrier](https://www.pololu.com/product/3417), not the bare chip). Mount high on the camera end face (sim finding).
2. Inertial sensor: **TDK ICM-42688-P** is the candidate (verified, [TDK](https://invensense.tdk.com/products/icm-42688-p/): 2.8 mdps/rtHz gyro, 70 ug/rtHz accelerometer, 0.88 mA, 2.5 x 3 x 0.91 mm). The comparison with Bosch BMI270 and ST LSM6DSO rests on one secondary table that does not name the parts.
3. Battery cell, 7.4 V boost converter and 3.3 V buck-boost (recommendation in 4; part numbers still to find).
4. Wheel motor drivers (four small H-bridges, with the back-EMF sampling of 2) and the servo bus interface (half duplex).
5. Operator-side radio (a second XBee 3 on a USB board).
6. PIC32 pin and peripheral allocation (UART for the servo bus, UART for the radio, I2C for the sensors, PWM and ADC for the drivers).
7. Mechanical: wheel and spindle-tube retention, hub gear teeth and servo mounting, seals, O-rings and lid screws, wiring feedthroughs.
8. Optional: the Lighthouse receiver amplifier (needs the SM940K09L cell layout from Anysolar, `docs/positioning.md`).
