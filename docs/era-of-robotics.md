# The late 1990s to early 2000s in robotics: what the "spirit" is

Status as of 2026-11-12. Research for the owner's guiding principle in `docs/electronics-concept.md` ("keep the spirit of that era of robotics"). The owner's own words: the spirit is loosely defined, but the current paradigm of hobbyist electronics is "very, very different", and characterising the spirit is worthwhile. **Sourcing:** items marked (SRC) come from pages found by web search (mostly secondary; the weakest, such as Wikipedia mirrors and vendor blogs, are noted); everything under "Synthesis" is my own reading and is not sourced. Dates that sources disagree on are marked. One low-quality mirror (cavac.at) contained text addressed to AI assistants; it was ignored and is not used here.

## 1. What existed (a timeline of the scene)

| When | What | Source |
|---|---|---|
| 1977 to 1985 | IEEE Spectrum announces the Amazing Micromouse Competition (1977, contest 1979); first World Micromouse Competition in Japan, 1985; clubs in schools from about 1990; 1991 world championship, 30 mice from 13 countries | IEEE Spectrum, Birmingham City University |
| 1986 to 1989 | Brooks's subsumption architecture (1986 paper, one source says 1985); Brooks and Flynn's memo on the Genghis hexapod (1989, other sources 1988 or 1991); "Fast, Cheap and Out of Control: A Robot Invasion of the Solar System" (1989), the idea that many small simple cheap robots could do more than one large one; Mark Tilden's first BEAM robot, Solaroller, at Waterloo on 10 November 1989 (a Solarbotics post) | Wikipedia, arXiv 0412056, a blog on the 1989 paper, Solarbotics |
| 1987 | Gordon McComb's *Robot Builder's Bonanza*, which Make credits with starting hobby robotics as a major maker category; over a million of his books in print | Make |
| 1990 to 1992 | All Japan Robot Sumo (1990; the contest is attributed to Hiroshi Nozawa, late 1980s); the first BASIC Stamp (Parallax, 1992); Marc Thorpe's 1992 radio-controlled vacuum experiments, the basis of Robot Wars; MIT's LEGO robot course 6.270 (Martin, Oberoi and Sargent credited in the 1992 Robot Builder's Guide; roots in LEGO/Logo) | Wikipedia, Parallax, a combat-robot book, MIT OCW |
| 1993 | Jones and Flynn, *Mobile Robots: Inspiration to Implementation* (A K Peters): the Rug Warrior, a Motorola 68HC11 robot using subsumption, source in C and 68HC11 assembler; sold later as a kit (a Rug Warrior Pro kit with a 2 MHz 68HC11 and 32 KB RAM was started in 2000) | Dr. Dobb's review, ASEE paper, a RobotShop post |
| 1990s | The Handy Board (Fred Martin, MIT): 68HC11, 32 KB battery-backed RAM, four motor outputs, Interactive C; licensed free of charge and built by several makers | Wikipedia, Martin's technical reference |
| 1995 to 1998 | Lynxmotion founded (1995), kits for a PC, a PIC or a BASIC Stamp; BASIC Stamp 2 (1995, PIC 16C57 inside); Parallax Board of Education (1997) and the Boe-Bot (sources say 1998; one says 2012 for the school programme) | Lynxmotion, Parallax, a PBASIC history |
| 1997 | Mars Pathfinder and Sojourner, which set a web-traffic record (over 200 million views from 4 to 8 July 1997); RoboCup and the nanorover task are of the same years | NASA |
| 1998 to 2000 | LEGO Mindstorms RCX: Hitachi H8, about 16 MHz, 32 KB RAM of which more than half held the firmware; reverse-engineered by individuals (Kekoa Proudfoot documented the internals, Dave Baum cracked the infrared protocol and wrote NQC, "Not Quite C"; legOS replaced the firmware; leJOS and TinyVM appear by 2000) | IEEE Spectrum, Orion Robots, Brown and Linux HOWTO pages |
| 2000 to 2003 | The CMUcam begins at Carnegie Mellon (2000); CMUcam1 (2002) tracked a colour blob at 17 frames per second; CMUcam2 (2003) added a frame buffer, servo control, windowing and video output | OpenMV legacy docs |
| 1997 to 2002 | **Teleoperated field robots, the nearest relatives of this rover's function:** NASA Ames Nomad (1997): video and data over 2.4 GHz spread-spectrum wireless Ethernet, with a separate low-bandwidth radio as a fallback that needs no line of sight; the MPRS Urban Robot: one 2.4 GHz Breezecom radio carried video (15 to 20 frames per second) and commands; DARPA's Tactical Mobile Robot programme: Urbie (JPL, Carnegie Mellon, USC) then iRobot's **PackBot** (DARPA approached iRobot in 1998; searched the World Trade Center in 2001; tracked, with flippers that rotate through 360 degrees and right it after a flip in seconds) | DTIC report ADA422028, Nomad FSR 1997 paper, Defense Media Network, NASA Spinoff |
| 2000 | An Electronic Design article lists the usual brains of toy, university and hobbyist robots: the Intel 8051, Motorola 68HC11, TI TM370 and Microchip PIC | Electronic Design |
| after the era | Wiring (Barragan, IVREA) then Arduino (Banzi and colleagues, mid-2000s), the AVR "breakout" board that became the industry standard; CMUcam3 (2007, ARM7), CMUcam4 (2012), Pixy (2014) | Blikstein 2013, OpenMV legacy docs |

## 2. A framework from the literature

Blikstein's 2013 history of physical computing (*Gears of Our Childhood*, found by search and read from the PDF) is the one source that tries to characterise the whole lineage. Its relevant claims:
- **Four generations:** (1) 1980s to early 1990s, LEGO/Logo and the MIT Media Lab programmable bricks; (2) the late 1990s, devices that extended these with new sensors and actuators and "programmable boards targeted to hobbyists and interaction designers"; (3) the early 2000s, devices built to broaden participation; and a later fourth wave.
- **Two models of board:** the **"Cricket model"** (the LEGO brick and the MIT Cricket: on-board motor drivers and batteries, an all-in-one that hides the inside of the microcontroller and exposes only function) and the **"breakout model"** (the BASIC Stamp, Wiring and the Arduino: the pins of the microcontroller exposed, circuits built outside on a breadboard). The Stamp was the first mass breakout board ("selling millions of units", the key hobbyist vendor until Arduino-like boards, language "more powerful but much harder to learn").
- **The intellectual root of the early generation was constructionism:** the devices were "things to think with", their designers wanted to give "powerful expressive tools" and make processes "visible and manipulable" ("beyond black boxes"), and were "not interested in turning children into engineering prodigies". The Programmable Brick was a computer small enough to be put in the thing it controlled (the ubiquitous-computing idea), with an LCD and buttons, running untethered once programmed.
- Later boards kept the pieces of this: the MetaCricket's daisy-chained bus devices, which Blikstein says foreshadowed the Arduino "shield". The Arduino added open source, "distributed expertise" and a barebones design.

## 3. Synthesis: what the spirit is (my reading, to be argued with)

1. **Scarcity was the medium.** An 8-bit part, kilobytes of memory, a clock of 2 to 16 MHz: the RCX gave a user under half of 32 KB, the Handy Board and Rug Warrior 32 KB. A design was what could be made to fit, so behaviours were few and each was understood.
2. **The board was the whole computer.** One self-contained controller, no operating system, programmed from a PC over a serial or infrared cable in a small language (Interactive C, NQC, PBASIC, C with 68HC11 assembler), then disconnected to run alone. The motor drivers were on the board in the Handy Board and Cricket pattern.
3. **Intelligence came from behaviour and from the body, not from computation.** Subsumption layers (the Rug Warrior: light-following overriding wandering), Genghis with its cognition removed, and at the extreme Tilden's BEAM (analog "nervous nets", no microcontroller, the Solar Engine; "to build smart machines one must first build a smart body", annealing into a gait). Robots were creatures.
4. **Small, cheap and many.** Brooks and Flynn's 1989 case for a swarm of small rovers instead of one large one is the same intellectual moment as the nanorover (my observation; no source ties the two).
5. **Few, simple sensors and mostly analog.** The Rug Warrior had three bump switches, two infrared emitters and one detector, shaft encoders, and two photo sensors; later hobby parts were the Sharp GP2D12 (a continuous analog distance voltage, easily fooled by materials) and the Devantech SRF04 (3 cm to 3 m ultrasonic; its designer said the Polaroid module's 10.7 m range was far more than a small robot needs). **A camera was an exotic luxury**, and the CMUcam made it a serial device that reported a tracked colour blob (17 frames per second for the first).
6. **Transparency was a value.** "Beyond black boxes" in the labs; in the hobby market the Stamp's PBASIC was "close to the hardware" with "nothing abstracted into libraries" (Parallax's own account); and a culture of taking products apart (Proudfoot opening the RCX, Baum cracking its protocol).
7. **Knowledge lived in books, clubs and contests, and in hand-built documentation.** McComb's book, Jones and Flynn's book (with the code), Martin's technical reference; contests as the organising event (6.270 every January, micromouse, sumo, the Trinity fire-fighting contest, Robot Wars). Each builder reinvented motor control and sensor reading.
8. **Mechanical work was improvised.** LEGO, hacked hobby servos, found and scratch-built chassis (the BEAM palm-sized robots; Lynxmotion kits aimed at a Stamp, a PIC or a PC).
9. **The purpose was understanding, not product.** The robot was a thing to think with (the constructionist root) or a contest entry; it was not meant to be a polished appliance. The nanorover project itself, a technology task about a very small rover, shares this.

## 4. What is different now (partly sourced, mostly mine)

| Era | Today |
|---|---|
| Scarcity (KB, MHz) shapes the design | Abundance (32-bit parts with MB of flash, radios built in, Linux boards, GPU vision for a few dollars) means the limit is attention, not memory |
| The board is the computer; you program it, it runs alone | Modules with libraries: you assemble breakouts and shields and call a driver; the Arduino "exposed the pins" and added shields and an open ecosystem (Blikstein; Mohomed and Dutta: low cost, open source, ease of use) |
| Behaviour and body | Perception and learning (a camera and a neural net are commodities); autonomy by software |
| A camera is a luxury (CMUcam: a blob) | A camera is the default sensor |
| Knowledge in books, clubs, contests; code in the book | Knowledge in forums, video, repositories; code by search; projects, not contests, as the unit (Electronic Design: the maker movement emerged "after the internet was in full swing, along with the open-source movement"; IEEE Spectrum: cheap PCs turned hobbyists into users, and Raspberry Pi and Arduino revived building) |
| Parts hard to get and expensive, but every part simple | Parts cheap and easy to get, but each part complex and closed (an ESP32 or a Pi is a black box in Blikstein's sense) |
| The robot is a thing to understand | The robot is a thing to ship, show or post |

## 5. What this means for the nanorover (revised on the owner's correction, 2026-11-12)

**The owner's correction: "the spirit shouldn't change how the rover functions fundamentally, just parts selection. This is still a teleoperated rover with a camera, like a PackBot (also a robot from the era in question)."** So the spirit is a rule for **choosing parts**, not for how the rover behaves. My earlier proposals of layered-behaviour autonomy, sensing built around the papers' sun detectors, and a BEAM-style solar trigger are **withdrawn**: they would change the function.

**PackBot as the functional anchor (SRC, thin):** a teleoperated, camera-carrying, self-righting robot from the same years and, through Urbie, from the same JPL-DARPA world as the nanorover. I found nothing on its electronics (onboard computer, camera, radio and operator unit are unverified). What the sources do show about teleoperated robots of the time is a **pattern of links**: a high-bandwidth channel for video (2.4 GHz spread-spectrum Ethernet or an analog link) and, in Nomad, a separate low-bandwidth radio that needs no line of sight; the MPRS robot used one radio for both. PC/104 (the stackable embedded-PC standard, from 1992) was the era's usual small x86 computer, but I found no source tying it to these robots.

**Parts-selection rules the spirit could give (mine, to be confirmed):**
1. **The controller is one small microcontroller board, no operating system, in the Handy Board manner** (motor drivers and I/O on the board), not a Linux board in the core of the rover.
2. **Simple, legible interfaces between parts** (serial, I2C, a few analog inputs and PWM, composite video if used), not opaque stacks.
3. **Parts with a lineage in the era** where the choice is otherwise equal (MIPS and PIC for the controller; an M12-lens camera module in the CMUcam manner; a simple radio).
4. **Documentation is part of the product** (already how the project works).

**What stays as before:** the rover's functions (driving, posing the struts, righting itself, solar charging, the camera) and the teleoperation by a person.

**Consequence for the camera and link (mine):** the camera is the operator's eyes, so it must deliver images or video, which weakens the case for the Pixy2 (a tracker). The era-faithful ways to get video to an operator are an analog (composite) camera with an analog video transmitter, or digital images over a modest radio; the first needs almost no processing in the rover (the controller only handles driving and commands), the second needs a module such as the OpenMV or Arducam to compress and buffer frames. Both fit the "two links" pattern above (video, plus a low-rate command and telemetry radio). Not researched further.

## Decided 2026-11-12
The owner first chose an analog route, then the same day reversed it: **digital video at a low bitrate over one modest digital radio, the headlamp for dim light** (details in `docs/electronics-concept.md`). Still to confirm: the four parts-only rules above.

## Sources
- [DTIC ADA422028, the MPRS Urban Robot](https://apps.dtic.mil/sti/pdfs/ADA422028.pdf); [Nomad, FSR 1997](https://vislab-ccom.unh.edu/~schwehr/papers/nomad-fsr97.pdf)
- [Defense Media Network, iRobot and PackBot](https://www.defensemedianetwork.com/stories/irobot-expands-and-enhances-robotic-systems/); [NASA Spinoff, public safety robots](https://spinoff.nasa.gov/node/10439)
- [Blikstein, Gears of Our Childhood (2013)](https://bba.tltlab.org/wp-content/uploads/2024/03/blikstein-gears-of-our-childhood-2013.pdf)
- [IEEE Spectrum, Mindstorms: Not Just a Kid's Toy](https://spectrum.ieee.org/mindstorms-not-just-a-kids-toy); [Orion Robots, the RCX inside and out](https://orionrobots.co.uk/2010/01/19/the-lego-rcx-inside-and-out.html)
- [Parallax milestones](https://www.parallax.com/?p=2434), [PBASIC article](https://www.parallax.com/?p=5631), [Boe-Bot origins](https://www.parallax.com/?p=35170)
- [Solarbotics, 20 years of BEAM](https://solarbotics.com/20-years-of-beam-technology/page/130)
- [Dr. Dobb's review of Jones and Flynn (1993)](https://archive.retro.co.za/CDROMs/DrDobbs/CD%20Release%2012/articles/1993/9312/9312n/9312n.htm); [ASEE paper on the Rug Warrior](https://peer.asee.org/11312.pdf)
- [MIT 6.270 history (OCW)](https://ocw.mit.edu/courses/6-270-autonomous-robot-design-competition-january-iap-2005/0f5f6dbbbb72c413625d74001553d68f_history.pdf)
- [IEEE Spectrum, the Amazing Micromouse Contest](https://spectrum.ieee.org/consumer-electronics/gadgets/the-amazing-micromouse-contest); [robot competitions (Wikipedia)](https://Www.Wikipedia.org/wiki/Robot_competition)
- [Make, Gordon McComb](https://makezine.com/article/maker-news/gordon-mccomb-father-of-hobby-robotics-has-passed-away/)
- [Genghis (Wikipedia)](https://en.wikipedia.org/wiki/Genghis_(robot)); [hexapod subsumption (arXiv)](https://arxiv.org/abs/cs/0412056)
- [History of Lynxmotion](https://www.lynxmotion.com/history/); [Electronic Design, embedded robots (2000)](https://www.electronicdesign.com/news/will-embedded-robots-become-erector-set-2000s)
- [CMUcam project (OpenMV legacy docs)](https://docs.openmv.io/dev/legacy/); [Handy Board (Wikipedia)](https://en.wikipedia.org/wiki/Handy_Board)
- [NASA, the Pathfinder web traffic record](https://www.nasa.gov/specials/pathfinder20/)
- [Sharp GP2D12 review](https://www.milesburton.com/w/index.php/Sharp_GP2D12_Infrared_Sensor_Review); [Devantech SRF04](https://www.robotshop.com/products/devantech-ultrasonic-range-finder-srf04)
- [IEEE Spectrum, the rise, fall and rise of electronics kits](https://spectrum.ieee.org/the-rise-fall-and-rise-of-electronics-kits); [Electronic Design, the maker movement](https://www.electronicdesign.com/technologies/embedded/article/55139227/electronic-design-formalization-of-the-maker-movement); [Mohomed and Dutta on makers](https://www.eecs.berkeley.edu/~prabal/pubs/papers/mohomed14makers.pdf)
