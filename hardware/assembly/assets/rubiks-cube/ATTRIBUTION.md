# Rubik's Cube model (scale reference in the renders)

This work is based on "Rubik's Cube" (https://sketchfab.com/3d-models/rubiks-cube-688917bf6a064601aef28fdce328ad86) by BeyondDigital (https://sketchfab.com/BeyondDigital) licensed under CC-BY-4.0 (http://creativecommons.org/licenses/by/4.0/)

**Changes made (as the licence asks us to say):** the three baked textures (base colour, metallic-roughness, normal) were reduced from 4096 x 4096 to 2048 x 2048 pixels (the metallic-roughness map was also converted from a palette image to RGB) to keep the repository small; the mesh (`scene.gltf`, `scene.bin`) is unchanged. In `hardware/assembly/blender_render.py` the model is scaled to 57 mm on a side (the standard 3 x 3 x 3 cube; the page gives no real size), turned about the vertical and set on the ground beside the rover.

This directory is licensed CC BY 4.0, separately from the rest of the repository. The original files (full-resolution textures, Sketchfab's `license.txt`) are kept in the private companion repository.
