# Wheels

Spec and design record for `hardware/wheel/wheel.py` (run after `hardware/body/body.py` and `hardware/strut/strut.py`).

The photo (`img840-340-hires.original.jpg`, kept in the private companion repository) shows a flat smooth aluminium disk on the outside with a shaft collar on its centre, over a stack of
saw-tooth discs like saw blades, each turned a little from the last so the teeth line up in helical ridges. I measured it by solving the camera
from the vanishing points of the cell edges (focal length about 3900 px), taking the top face as 140 mm, and projecting circles on the wheel axis
back onto the photo until they fit:
- **Smooth disk:** radius 27 mm. It is flat; the shading that looks like a cone is lathe finish. The collar centre sits 5 mm outboard of it.
- **Tooth tips:** radius about 29.5 mm, so the teeth stand about 2.5 mm proud of the disk. That makes the photographed wheel about 59 mm across
  the teeth, consistent with the "about 6 cm" prototype wheels in the sources.
- **Stack:** eight saw-tooth discs, 17 teeth each (about 21 degrees apart at the rim), and the whole stack reaches about 33 to 36 mm inboard of the disk.
  I counted the 17 from the teeth showing around the disk rim and the 8 from the steps along a ridge, so both can be off by one or so.
- **Helix:** best fit about 8 degrees of turn per disc going inboard, counterclockwise seen from outside (about 56 degrees over the stack). This is the least certain fit.
- **Scale to the published size:** every measured proportion is multiplied by 65 / 59 so the tooth diameter is the published 65 mm of MUSES-CN. The
  model's wheel is therefore 65 mm over the teeth, a 59.5 mm smooth disk, 34.6 mm wide to the disk face plus an 11 mm collar, 0.99 mm discs on a
  4.3 mm pitch, over an 11 mm core radius (an estimate: the wheel holds a gearmotor).
- **Fit check:** the photo's stack reaches inboard to where the strut ends, and that lands between the outer faces of the two strut layers (80 to 84 mm)
  at the 140 mm scale, which supports the strut layout and the 140 mm scale together.
- **Checks:** the wheels overlap nothing (casting, studs, struts, lid). Default stance: overall 261.7 mm wide by 191.9 mm long, wheel bottoms 32.1 mm below the box floor.
- **Mass:** about 98 g per wheel as solid aluminium with no motor, 392 g for four. With the box, plate, inserts, studs, struts and wheels the model comes to roughly 1.5 kg before any motor or electronics, against 1300 g for the original rover. That mass is the cast box's.
- **Caveats:** the photo is the early prototype, not the MUSES-CN wheel, so the proportions are borrowed; the 140 mm scale is an assumption (the quarter suggests the
  body could be somewhat smaller, 125 to 135 mm, in which case the true wheel is smaller and every photo measurement scales with it); tooth shape, disc spacing,
  the twist per disc, the core and the collar size are estimates. The scale and angles can be revised by editing the parameters at the top of `hardware/wheel/wheel.py`.
