# JPL Nanorover (MUSES-CN and Precursor Prototypes): Annotated Bibliography and Verified Specifications

Prepared 2026-11-10 for a looks-like replica project. Citations use GitHub footnotes (`[^n]`); each footnote links to the source, and the full reference list is at the bottom.

## Summary

The best-documented, most replicable configuration is the **MUSES-CN flight-design rover** described by Wilcox and Jones (1999-2000): a 14 x 14 x 6 cm rectangular body, four 6.5 cm wheels on four independently posable struts (7 cm, pivot to axle) that pivot from hubs at the center of the two opposing 14 x 6 cm faces, solar cells on four of the six faces, and a listed mass of 1300 g.[^jones2000][^wilcox-kg]

- **The "~150 g nanorover" premise is not supported by any primary source I could verify.** JPL's "tens to hundreds of grams" wording describes a technology goal.[^tunstel] Every concrete vehicle figure found is roughly 1-2 kg.
- **Dimensions are internally consistent.** With 7 cm struts pivoting at the body center, a fully extended strut puts the axle at the 14 cm body's end face. Adding the 3.25 cm wheel radius at each end gives about 20.5 cm overall. This is my own derivation, not a published figure, but it matches JPL's "20 cm long" prototype caption.[^jpl-nano]
- **Biggest gaps:** wheel width, strut cross-section, hub and axle details, window and instrument-port placement, finish and color, and solar-cell layout dimensions are not published in any accessible text. These must be scaled from photographs.

## Three vehicles share the name "JPL Nanorover"

1. **Early research prototypes, c. 1996-1998.** Battery-powered, about 6 cm aluminum wheels with internal motors and helical cleats, about 20 cm long.[^weisbin][^tunstel]
2. **MUSES-CN flight design/prototype, c. 1999-2000.** 14 x 14 x 6 cm body, 6.5 cm wheels, 1300 g.[^jones2000]
3. **A possible two-wheeled prototype**, mentioned only in a 1998 MIT Technology Review article (unverified).[^techreview]

The Sojourner/Rocky lineage vehicles are conceptual ancestors only. The nanorover shares no chassis geometry with the rocker-bogie family.

## Confirmed specifications

**Verification levels:** *Full text* = read in the full source. *Indexed text* = the passage appeared verbatim in search-indexed text of an author-uploaded PDF, but the full PDF could not be opened. *Subagent-verified* = read in full by the research subagent only.

| Parameter | Value (paraphrased) | Vehicle | Source | Verification |
|---|---|---|---|---|
| Body size | 14 x 14 x 6 cm | MUSES-CN | [^jones2000], [^wilcox-kg], [^wilcox2000] | Indexed text, consistent across three papers |
| Mass (table) | 1300 g | MUSES-CN | [^jones2000] | Indexed text |
| Mass (narrative) | About 1 kg | MUSES-CN | [^wilcox-lpi] | Full text (abstract) |
| Mass (press) | A little more than 2.5 lb; cancelled over rising costs and weight; original budget $21 million | MUSES-CN | [^jplpress] | Subagent-verified |
| Wheel count | Four wheels on four posable struts | MUSES-CN, prototypes | [^tunstel], [^jones2000] | Full text (Tunstel); indexed (Jones/Wilcox) |
| Wheel diameter | 6.5 cm | MUSES-CN | [^jones2000], [^wilcox2000] | Indexed text |
| Wheel diameter | About 6 cm, aluminum, motor inside, helical cleats | 1997-98 prototype | [^weisbin], [^cassinis] | Full text |
| Strut length | 7 cm, pivot center to axle center | MUSES-CN | [^jones2000], [^wilcox-kg] | Indexed text |
| Strut mounting | Pairs from hubs at the center of the two opposing 14 x 6 cm faces | MUSES-CN | [^wilcox-kg] | Indexed text |
| Articulation | Four struts on a common pivot axis; same-side struts cannot pass; body can pitch about that axis (5 articulation DOF + 4 wheel DOF); potentiometers on struts, encoders on wheels | c. 1999 prototype | [^tunstel] | Full text |
| Overall length | 20 cm largest dimension; "30% the size of Sojourner" | Prototype | [^tunstel], [^jpl-nano], [^archive198] | Full text |
| Size (conflicting) | "Approximately 10 cm on a side" | "circa 1997" | [^jpl-gallery] | Full text; conflicts with others |
| Size (conflicting) | "6 inches square" | MUSES-CN (1999) | [^chronicle] | Full text |
| Motor mass | 10 g per motor with gearbox | MUSES-CN | [^wilcox2000] | Indexed text |
| Solar layout | Four of six faces | MUSES-CN | [^wilcox-kg], [^jones2000] | Indexed text |
| Solar layout | Top surface | Prototype | [^cassinis] | Full text |
| Power | 2.3 W at normal incidence | MUSES-CN | [^jones2000] | Indexed text |
| Speed | About 1.5 mm/s rolling; 10 cm/s hopping | MUSES-CN | [^jones2000] | Indexed text |
| Data rate | 4800 bit/s at 20 km to the orbiter-mounted rover equipment (OMRE) | MUSES-CN | [^jones2000] | Indexed text |
| Antenna | Right-hand circularly polarized square patch, offset-pin feed, high-k ceramic substrate | MUSES-CN | [^wilcox-kg] | Indexed text |
| Optics | Camera plus IR spectrometer; gimbaled mirror; filter wheel; 11.9 um detector pixel | MUSES-CN | [^jones2000] | Indexed text |
| Optics | CMOS APS camera with filter wheel and variable focus; 1-2.5 um near-IR spectrometer with scanned holographic grating; one gearmotor drives focus tube, filter wheel, and grating | Prototype | [^cassinis], [^weisbin] | Full text |
| APXS | At most 100 g and under 3 cubic inches (Pathfinder's weighed 570 g) | MUSES-CN | [^chronicle] | Full text |
| Electronics | Intel 8051 plus FPGA, radiation-hardened parts | Prototype | [^cassinis] | Full text |
| Power source | 500 g non-rechargeable lithium batteries | Prototype | [^weisbin], [^cassinis] | Full text |
| "Current nanorover" | 2 kg; 28 cm wide; stowed 28 cm long x 7 cm high; 25 cm operating height; 20 cm step; 1 m/s max | Labelled "current nanorover" in 1998 report | [^weisbin] | Subagent-verified; anomalous, see Caveats |
| Dust wiper | Electroactive-polymer wipers with graphite/epoxy blade baselined for the optical/IR window | MUSES-CN | [^barcohen] | Indexed text |

## Annotated bibliography

### A. Core MUSES-CN papers (highest priority)

1. **Wilcox & Jones (2000), IEEE Aerospace Conference.** Body size, 6.5 cm wheels, four posable struts, 10 g motors, self-righting concept, hopping, about 1 kg.[^wilcox2000] Available via IEEE Xplore (paywalled) or an author-uploaded ResearchGate copy. **Get this first.**
2. **Jones & Wilcox (2000), "The MUSES CN Rover and Asteroid Exploration Mission."** Contains the "Rover Characteristics" table (1300 g, 14 x 14 x 6 cm, 2.3 W, speeds, data rate), a prototype photo (Fig. 1), and OMRE structure and release mechanisms (Fig. 2).[^jones2000] The JPL repository record is metadata only.[^ntrs2000] The venue is unconfirmed.
3. **Wilcox & Jones, "A ~1 Kilogram Asteroid Exploration Rover."** Same table, plus strut mounting, antenna, and optics description.[^wilcox-kg] Venue unconfirmed (possibly the ICRA 2000 Workshop on Mobile Micro-Robots).
4. **Jones & Wilcox (1999), IAF-99-Q.5.03.** Likely repeats the rover and OMRE description.[^iaf99] **Numbers not verified.**
5. **Wilcox et al. (1997), i-SAIRAS '97, "Nanorover Technology and the MUSES-CN Mission."** The earliest MUSES-CN description.[^isairas97] **Not verified; no numbers extracted.**
6. **Wilcox (2000), LPI Mars workshop abstract.** About 1 kg, three instruments, self-righting, panels on four sides, camera can point straight up or down.[^wilcox-lpi] Low dimensional content.

### B. Precursor nanorover research (1996-1999)

7. **Weisbin (1998), NASA/CR-1998-208257.** Prototype description, 500 g lithium batteries, and Sojourner comparison data (13 cm wheels, 63 cm long, 45 cm wide).[^weisbin] Open PDF.
8. **Tunstel (1999), i-SAIRAS '99.** 20 cm largest dimension, strut/body articulation, solar panel placement, and figures of prototype poses and the self-righting sequence.[^tunstel] Open PDF. **Best open source for pose geometry.**
9. **Wilcox & Nasif (1998), NASA Tech Brief NPO-20057.** Pivot mechanism: per-wheel gearmotors at the strut ends, idler disk/pulley on the pivot axis, spring-loaded friction pivot. No dimensions in the text; the Technical Support Package figure (free login) shows the assembly.[^npo20057] **Best source for the hub look.**
10. **Wilcox et al. (1996), "Nanorovers for Planetary Exploration," AIAA Robotics Technology Forum.** Cited by Tunstel for the "several hundred grams" goal.[^tunstel] No online copy found. **Not verified.**
11. **Wilcox, Nasif & Welch, "A Nanorover for Mars," *Space Technology* 17(3/4).** Paywalled. **Not verified.**
12. **Weisbin, Lavery & Rodriguez (1997), *Autonomous Robots* 4.** Paywalled.[^weisbin-springer] An academia.edu summary claims a ~100 g nanorover.[^weisbin-academia] **That claim is not verified in the paper's own text.**
13. **Wilcox & Nguyen (1998), SAE 981695.** Mentions the "sub-1-Kg Nanorover."[^sae] Low dimensional value.
14. **Wilcox (2002), "Snow White and the 700 Dwarves."** Paywalled; cites the nanorover papers.[^snowwhite] Low priority.

### C. Instruments and subsystems

15. **Koppes (1999), University of Chicago Chronicle.** Economou's APXS limits and the "6 inches square" rover.[^chronicle]
16. **Bar-Cohen slides, NTRS 20010067234.** "Nanorover in action" photo and the dust-wiper window.[^barcohen]

### D. ISAS/JAXA side

17. **Kawaguchi et al. (2003), Acta Astronautica.** Spacecraft-level; cites Wilcox's i-SAIRAS '97 paper.[^kawaguchi] Rover-interface details **not verified.**
18. **Kawaguchi et al. (1998), ISTS 98-o-3-04V and IAA-L98-0505.** Cited by the JPL papers. Full text not located.

### E. Outreach and secondary

19. **NASA Space Place, "Make a Balloon-powered Nanorover!"** Says the real rover weighs 1 kg and is "a couple of inches high"; includes a prototype photo.[^spaceplace] Educational, not dimensional.
20. **Scigliano (1998), MIT Technology Review.** Source of the one-pound nanorover framing and the two-wheeled prototype mention.[^techreview] Journalism.
21. **Starek et al. (2015), Springer preprint.** Describes the Nanorover as "grapefruit-sized."[^starek] Secondary.
22. **ETHW oral history, Brian Wilcox.** Career context; no specs verified.[^ethw]

## Image and drawing sources

- **JPL Robotics Nano Rover task page and gallery.** High-res "Prototype of the nanorover, only 20cm long."[^jpl-nano] Gallery item "Nanorover (circa 1997)."[^jpl-gallery] Video "Nanorover Technology, 1997."[^jpl-video97] **Top photo source.**
- **NASA Solar System Exploration image IM_ID=198**, mirrored on the Internet Archive: caption gives 20 cm (8 in) length, camera, solar cells on all sides.[^archive198]
- **Archived JPL nanorover page** at the Univ. of Brescia minerobots archive: small GIFs, a pose-configuration diagram, and an optics-arrangement model.[^cassinis]
- **Tunstel 1999:** Fig. 1 (prototype with axes), Fig. 2 (strut/chassis configurations), Fig. 3 (self-righting sequence), Fig. 5 (fitness-case poses).[^tunstel]
- **NPO-20057 Technical Support Package:** schematic of the wheel, strut, idler pulley, and pivot assembly.[^npo20057]
- **Jones/Wilcox papers:** prototype photo, OMRE figure, optical subsystem figure.[^jones2000][^wilcox-kg]
- **Bar-Cohen slides:** photo plus simulated window with two side dust wipers.[^barcohen]
- **Stock photo (rights-managed):** "Nanorover prototype selected for the MUSES-CN asteroid mission."[^agefoto]
- **JPL press release 2000-110** on the cancellation; may include an image.[^jplpress]
- **NTRS 19990116393**, outreach compilation with a "Nanorover Technology Task" clip.[^ntrs-outreach]
- No museum holding of a nanorover was confirmed.

## Caveats and conflicts

- **Mass:** 1300 g (table) vs. about 1 kg (abstracts) vs. "a little more than 2 1/2 lbs" (press) vs. "one-pound" (Technology Review) vs. 2 kg (1998 report's "current nanorover") vs. "10kg" (JPL gallery caption, almost certainly a typo). An academia.edu summary claims 2.7 kg; per the research, the papers describe 2.7 kg as ISAS's allocation for the whole NASA payload (rover plus OMRE). The "10-100 g" phrasing is a program goal, not a vehicle mass.
- **Size:** 14 x 14 x 6 cm body vs. 20 cm overall length vs. "approximately 10cm on a side" vs. "6 inches square" vs. "a couple of inches high." The 20 cm and 14 cm figures are compatible if 20 cm means wheel-to-wheel length (my derivation).
- **"Current nanorover" spec list (2 kg, 28 cm wide, 1 m/s, 20 cm step):** inconsistent with a 6 cm-wheeled, 20 cm vehicle. Read by the subagent only; treat with caution.
- **Solar layout:** top only (prototype), four of six faces (MUSES-CN papers), all sides (NASA caption), most sides with primary on top (Tunstel). These likely reflect different iterations.
- **Speeds:** the papers give 1.5 mm/s rolling and 10 cm/s hopping; Space Place says 1 mm/s and 20 cm/s.[^spaceplace]
- **Wheel diameter:** about 6 cm (prototype) vs. 6.5 cm (MUSES-CN).
- **Patents:** none located. The Tech Brief says Caltech retained title, so one may exist.[^npo20057]
- **Verification limits:** the ResearchGate, academia.edu, and JPL repository PDFs blocked automated fetching. MUSES-CN figures come from indexed verbatim text, and the figures and table layouts in those papers were not inspected.

## Recommendations

1. **Obtain first:** the 2000 IEEE Aerospace paper, the Jones & Wilcox 2000 report, the NPO-20057 Technical Support Package, and the JPL Robotics high-res images.
2. **Then:** Tunstel 1999, Weisbin CR-1998-208257, and the i-SAIRAS '97 paper.
3. **Pick one iteration.** Use the MUSES-CN flight design (14 x 14 x 6 cm body, 6.5 cm wheels, 7 cm struts); it is the only one with a coherent dimension set.
4. **Scale unpublished details from photos,** using the 6.5 cm wheel or the 14 cm body edge as the reference.
5. **For certainty,** contact the JPL Robotics group (Brian Wilcox was the point of contact) or JPL Archives. No CAD or engineering drawings appear to be public.

## References

[^jones2000]: R. Jones and B. Wilcox, "The MUSES CN Rover and Asteroid Exploration Mission," 2000. [ResearchGate](https://www.researchgate.net/publication/277294262_The_MUSES_CN_Rover_and_Asteroid_Exploration_Mission); also [academia.edu](https://www.academia.edu/27965409/The_MUSES_CN_Rover_and_Asteroid_Exploration_Mission).
[^ntrs2000]: Same report, NTRS metadata record (no download): [NTRS 20210002434](https://ntrs.nasa.gov/citations/20210002434).
[^wilcox-kg]: B. H. Wilcox and R. M. Jones, "A ~1 Kilogram Asteroid Exploration Rover." [ResearchGate](https://www.researchgate.net/publication/237537971_A_-1_Kilogram_Asteroid_Exploration_Rover); [academia.edu](https://www.academia.edu/27965405/A_1_Kilogram_Asteroid_Exploration_Rover).
[^wilcox2000]: B. H. Wilcox and R. M. Jones, "The MUSES-CN nanorover mission and related technology," *2000 IEEE Aerospace Conference*, vol. 7, pp. 287-295. [DOI 10.1109/AERO.2000.879296](https://doi.org/10.1109/AERO.2000.879296); [ResearchGate copy](https://www.researchgate.net/publication/3869006_The_MUSES-CN_nanorover_mission_and_related_technology).
[^iaf99]: R. Jones and B. Wilcox, "NASA Participation in the ISAS MUSES C Asteroid Sample Return Mission," IAF-99-Q.5.03, 1999. [ResearchGate](https://www.researchgate.net/publication/2526731_NASA_Participation_in_the_ISAS_MUSES_C_Asteroid_Sample_Return_Mission).
[^isairas97]: B. Wilcox et al., "Nanorover Technology and the MUSES-CN Mission," i-SAIRAS '97. [NTRS 20060035115](https://ntrs.nasa.gov/search.jsp?R=20060035115).
[^wilcox-lpi]: B. H. Wilcox, "Nanorovers and Subsurface Explorers for Mars," LPI workshop abstract #6002, 2000. [NTRS 20010020531](https://ntrs.nasa.gov/search.jsp?R=20010020531).
[^weisbin]: C. R. Weisbin, *Rover and Telerobotics Technology Program: Accomplishments and Technology Transfer*, NASA/CR-1998-208257. [NTRS PDF](https://ntrs.nasa.gov/api/citations/19980201211/downloads/19980201211.pdf?attachment=true).
[^tunstel]: E. Tunstel, "Evolution of Autonomous Self-Righting Behaviors for Articulated Nanorovers," i-SAIRAS '99. [NTRS PDF](https://ntrs.nasa.gov/api/citations/20000064075/downloads/20000064075.pdf).
[^npo20057]: B. H. Wilcox and A. K. Nasif, "All-Terrain Vehicle With Self-Righting and Pose Control," NASA Tech Briefs NPO-20057, Feb 1998. [Tech Briefs](https://www.techbriefs.com/component/content/article/32108-npo20057).
[^weisbin-springer]: C. R. Weisbin, D. Lavery, G. Rodriguez, "Robotics Technology for Planetary Missions into the 21st Century," *Autonomous Robots* 4:159-173, 1997. [Springer](https://link.springer.com/article/10.1023/A:1008808730915).
[^weisbin-academia]: [academia.edu copy/summary](https://www.academia.edu/125518222/Robotics_technology_for_planetary_missions_into_the_21st_century) (source of the unverified ~100 g claim).
[^sae]: B. H. Wilcox and T. Nguyen, "Sojourner on Mars and Lessons Learned for Future Planetary Rovers," SAE 981695, 1998. [TRID record](https://trid.trb.org/view/1781636).
[^snowwhite]: B. H. Wilcox, "Snow White and the 700 Dwarves," 2002. [Springer chapter](https://link.springer.com/chapter/10.1007/978-94-017-2376-3_13).
[^chronicle]: S. Koppes, "From Mars to asteroids," *University of Chicago Chronicle*, Feb 4, 1999. [Article](http://chronicle.uchicago.edu/990204/economou.shtml).
[^barcohen]: Y. Bar-Cohen, "Electroactive Polymers as Artificial Muscles - Reality and Challenges" (slides). [NTRS PDF](https://ntrs.nasa.gov/api/citations/20010067234/downloads/20010067234.pdf).
[^kawaguchi]: J. Kawaguchi et al., "The MUSES-C mission for the sample and return," *Acta Astronautica* (2003). [ScienceDirect](https://www.sciencedirect.com/science/article/abs/pii/S0094576502001467).
[^spaceplace]: NASA Space Place, "Make a Balloon-powered Nanorover!" [Page](https://spaceplace.nasa.gov/nanorover/en/).
[^techreview]: E. Scigliano, "Honey, They've Shrunk the Rover," *MIT Technology Review*, Jan 1, 1998. [Article](https://www.technologyreview.com/1998/01/01/237105/honey-theyve-shrunk-the-rover/).
[^starek]: J. Starek et al., "Spacecraft Autonomy Challenges for Next-Generation Space Missions," Springer, 2015. [Preprint](http://stanford.edu/~pavone/papers/Starek.Acikmese.ea.Springer15.pdf).
[^ethw]: "Oral-History: Brian Wilcox," ETHW. [Page](https://ethw.org/Oral-History:Brian_Wilcox).
[^jpl-nano]: JPL Robotics, Nano Rover research task. [Page](https://www-robotics.jpl.nasa.gov/what-we-do/research-tasks/nano-rover/).
[^jpl-gallery]: JPL Robotics gallery, "Nanorover (circa 1997)." [Page](https://www-robotics.jpl.nasa.gov/gallery/nanorover-circa-1997).
[^jpl-video97]: JPL Robotics gallery, "Nanorover Technology, 1997." [Page](https://www-robotics.jpl.nasa.gov/gallery/nanorover-technology-1997).
[^archive198]: NASA Solar System Exploration image "Nanorover" (IM_ID=198), Internet Archive mirror. [archive.org](https://archive.org/details/SPD-SLRSY-198).
[^cassinis]: Archived JPL nanorover page, Univ. of Brescia minerobots archive. [Page](https://www.cassinis.it/Siti%20ex%20Uni/ARL/projects/minerobots_archive/ruote13.htm).
[^jplpress]: "NASA Cancels Miniature Rover for Joint Japan-U.S. Asteroid Mission," JPL release 2000-110, Nov 3, 2000. [JPL News](https://www.jpl.nasa.gov/news/nasa-cancels-miniature-rover-for-joint-japan-us-asteroid-mission/).
[^agefoto]: age fotostock GXC-S02252, "Nanorover prototype selected for the MUSES-CN asteroid mission." [Listing](https://www.agefotostock.com/age/en/details-photo/nanorover-prototype-selected-for-the-muses-cn-asteroid-mission-the-nanorover-technology-task-is-a-technology-development-effort-to-create-very-small-10-100s-of/GXC-S02252).
[^ntrs-outreach]: "Asteroids and Comets Outreach Compilation," JPL video AVC-1998-178. [NTRS 19990116393](https://ntrs.nasa.gov/search.jsp?R=19990116393).
