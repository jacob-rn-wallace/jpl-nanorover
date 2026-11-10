# jpl-nanorover

Research toward an open, **looks-like replica** of the JPL nanorover, the small four-wheeled asteroid rover designed for the Japanese MUSES-C (Hayabusa) sample-return mission and cancelled by NASA in November 2000. "Looks-like" means visual and dimensional fidelity; it is not required to function.

> **Status: research only.** No CAD yet. Scale, materials, manufacturing method, CAD tool, articulation and the rover iteration to copy are all undecided.

## Target
The best-documented configuration is the MUSES-CN flight design: a 14 x 14 x 6 cm body, four 6.5 cm wheels on four posable 7 cm struts, solar cells on four of six faces, about 1 to 1.3 kg, and about 20 cm overall length. Wheel width, tread, strut cross-section, hub detail and finish are not published and must be scaled from photographs. Every figure is marked with how well it is sourced, and conflicting figures are listed.

## What's here
| Path | Contents |
|---|---|
| [`docs/jpl-nanorover-literature.md`](docs/jpl-nanorover-literature.md) | Annotated bibliography, specification table with verification levels, image sources and the list of conflicting figures |

## Contributing
Corrections with a primary source are the most valuable contribution, especially dimensions of the hub, wheel and struts, or engineering drawings. Contact with the JPL Robotics group or JPL Archives is the only known route to authoritative dimensions.

The source papers are kept in a separate private repository, `jpl-nanorover-private`, because they belong to their publishers.

## License model
- **Code** (scripts, tooling) is licensed under **Apache-2.0** (see [`LICENSE`](LICENSE)).
- **Hardware designs, mechanical documentation and bills of materials** are licensed under **CERN-OHL-S-2.0**, strongly reciprocal (see [`LICENSE-HARDWARE.txt`](LICENSE-HARDWARE.txt)).
- **Documentation** (the notes in `docs/`, READMEs) is licensed under **CC BY 4.0** (see [`LICENSE-DOCUMENTATION.txt`](LICENSE-DOCUMENTATION.txt)).

See [`NOTICE.md`](NOTICE.md) for third-party material. This is an independent hobby project, not affiliated with NASA, JPL or ISAS/JAXA.
