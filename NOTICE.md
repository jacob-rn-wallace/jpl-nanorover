# Licensing and notices

jpl-nanorover uses the same split-license model as maha-rover. Unless otherwise noted, files are licensed according to the category they fall under.

| What | Licence | File |
|---|---|---|
| Code: tooling that is not itself a design (none yet) | Apache-2.0 | [`LICENSE`](LICENSE) |
| Hardware: the CAD scripts and their STEP output in `hardware/`, drawings, mechanical documentation (`docs/*-spec.md`), bill of materials | CERN-OHL-S-2.0 | [`LICENSE-HARDWARE.txt`](LICENSE-HARDWARE.txt) |
| Documentation: the notes, bibliography and measurements in `docs/`, READMEs | CC BY 4.0 | [`LICENSE-DOCUMENTATION.txt`](LICENSE-DOCUMENTATION.txt) |

## Third-party material
- The papers, reports and web pages cited in `docs/` belong to their authors and publishers. This repository records only
  numerical facts, short paraphrases and citations; it contains none of the papers or their figures.
- NASA and JPL imagery is generally reusable for reference, but each page's usage terms have not been checked. Check them before
  publishing anything derived from an image. The rights-managed age fotostock photo is for reference only.
- This is an independent hobby project. It is not affiliated with or endorsed by NASA, JPL, Caltech or ISAS/JAXA.
- **Hammond Manufacturing 1590Z090.** The body model starts from Hammond's STEP file for the 1590Z090 die-cast enclosure. That file is Hammond's, its terms
  of use have not been read, and it is **not in this repository**; the script reads it from the private companion repository. Output that contains its
  geometry (`hardware/body/out/body_hammond.step` and every assembly file) is git-ignored. What is published is the script, our own parts (lid plate,
  O-rings, thread inserts, hub studs, nuts, struts, wheels) and numerical dimensions of the casting read from Hammond's published drawing
  (https://www.hammfg.com/electronics/small-case/diecast/1590z). `docs/images/rover-preview.png` is a render that shows the casting's outer shape. "Hammond" and "1590Z090" are Hammond's names.
- **JPL photograph.** `docs/photo-measurements.md` and the wheel and solar-cell values are measured from JPL's gallery image "Nanorover (circa 1997)"
  (https://www-robotics.jpl.nasa.gov/gallery/nanorover-circa-1997/). The image is not in this repository, and its usage terms have not been checked.
