# Rovers smaller than the nanorover

A side question: in JPL's 1998 "Nanorover Technology Task" video (about 5:19 to 5:42) an animation shows Sojourner, the nanorover and a third rover about as much smaller than the nanorover as the nanorover is than Sojourner, followed by a shot labelled "Widget Board".
This page records what could be found about that idea. Nothing found uses a name like "picorover"; JPL's own wording, from the narration, is "an even smaller Nanorover".

## The narration (transcribed by the owner; I did not hear it)

> "The Nanorover technology task is also leading the way to the development of an even smaller Nanorover with a mass under 100 grams. The key development is JPL's Widget Board, which will enable these small, flight-qualifiable rovers."

So the third rover in the animation is the under-100 g goal vehicle of the nanorover task, and the Widget Board, shown in the next shot, is named as the enabling development.

## What the video shows (frames)

- **About 5:19 to 5:31:** a computer animation on an asteroid-like surface. Large, in front: a Sojourner-like rover with a gold-foil body, a solar panel and an antenna. Middle right: the nanorover, a flat box with a round cream window and a rectangular panel on its end face and banded cylindrical wheels. Front right: a much smaller rover, a box with a gold top and two round lenses or lights on the front, on a tiny leg and wheel assembly.
- **About 5:36 to 5:42:** a photograph of two small printed boards beside a ruler (about 3 inches of it visible; each board a little over 2 inches long), captioned "Widget Board".

## What the sources say

| Source | What it says | Bearing on a smaller rover |
|---|---|---|
| JPL Robotics, Nano Rover task page (https://www-robotics.jpl.nasa.gov/what-we-do/research-tasks/nano-rover/); the same text in Weisbin, NASA/CR-1998-208257 | The task's aim is "very small (10-100s of grams)", scientifically capable rovers. The first objective is a useful system "within a mass of a few hundred grams"; the second is to advance technologies for rovers "well under 100 grams". Electronics to work without a thermal enclosure from -125 C to +125 C. | The sub-100 g class is in the task's own goals: the 1.3 kg flight nanorover was the first step, not the aim. |
| Wilcox & Welch, "Embedded Control of a Miniature Science Rover for Planetary Exploration", draft preprint, May 1998 (NTRS 20060035824) | Abstract only: "A rover prototype has been integrated into a package of several hundred grams in mass", with embedded control for mobility and science instruments. | Suggests a rover of several hundred grams was built or at least integrated. Full text not found. |
| Powell, "Lilliput in Space", Discover, 1 March 1999 | Wilcox "is developing tiny rovers that weigh no more than a few ounces"; NASA is also pursuing robots "that could fit on a spoon". It gives the MUSES-CN rover as "six inches long ... 42 ounces". | The clearest public statement of a rover well below the nanorover. |
| IROS'97 Planetary Rover Workshop notes, M. Maimone (CMU), 1997 | MIT: "10-15 gram 'Hopette' rovers have been studied" (egg-shaped, weighted, spring-hopped, aimed by repositioning the payload), with CPUs and locomotion shown small enough, but not imaging and communications. | A parallel idea from another lab, described as a study. Not JPL. |
| Wilcox, "Nanorovers and Subsurface Explorers for Mars", LPI 2000 (NTRS 20010020531) | Defines nanorovers as "of order one kilogram or less". | Nothing smaller. |
| JPL Rocky 8 page (https://www-robotics.jpl.nasa.gov/how-we-do-it/systems/the-rocky-8-rover/) | "Widget" boards are 1 inch by 3 inch single-axis motion controllers with a small PIC microprocessor, distributed next to the actuators and linked by an I2C bus. | The widget board is a tiny distributed motor-control board. That fits a video line about enabling smaller rovers, but no source found ties it to the nanorover. |

Also found: Stern et al., "Extreme temperature (-170 C to +125 C) electronics for nanorover operation", IEEE Aerospace 2001, on the 1.3 kg, 1666 cm3 nanorover's 2.5 W control and data system; Weisbin's report also lists JPL microrobots for urban terrain, which are a different, human-portable class.

## What this suggests, and what is missing

- A rover in the 10 to 100 g class was a stated goal of the nanorover task from 1997 or earlier, and Wilcox spoke publicly about "a few ounces" in 1999. The narration confirms that the animated third rover is that goal vehicle ("an even smaller Nanorover", under 100 g), not a separate project, and that the Widget Board was the key enabling technology.
- No document found describes the animated vehicle or its design, or ties the Widget Board to the nanorover in writing. A few-hundred-gram prototype is mentioned only in an abstract.
- Two JPL pages on the widget-board family, "Distributed motor controller for flight" and its hardware gallery page (both at www-robotics.jpl.nasa.gov), were found but not read. A search snippet also points to a paper on the embedded control of a miniature science rover by Tunstel, Welch and Wilcox using an 80C51 microcontroller; that is unverified.
- Leads not yet followed: the full text of Wilcox & Welch (1998); Wilcox et al., "Nanorover Technology and the MUSES-CN Mission", i-SAIRAS '97 (NTRS 20060035115); Wilcox et al., "Nanorovers for Planetary Exploration", AIAA 1996; Wilcox, Nasif & Welch, "A Nanorover for Mars", Space Technology 17; the Wilcox oral history on ETHW (the page refused automatic fetching).
- A transcript of the video's narration would show exactly what was claimed at 5:19.
