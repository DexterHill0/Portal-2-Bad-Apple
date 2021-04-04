# Portal-2-Bad-Apple

Must have Python 3 installed and the following libraries installed:

`opencv-python, imageio, numpy`

You must also have Portal 2 Authoring tools installed (for the VMF to BSP converter)

##### `badapple.py`

* `--video` / `-vid` The video file to be made into portals - should be completely black and white (i.e. black *or* white but no in between )
* `--width` / `-w` Width of output (in portals)
* `--height` / `-he` Height of output (in portals)
* `--frames` / `-f` FPS of output
* `--name` / `-n` Name of output map
* `--portal2` / `-p2` The path to your Portal 2 install

To open the map, enable the Portal 2 developer console and run `map custom/<name>`, `name` being the name your provided in the `name` argument. You *must* also run `r_portal_fastpath 0` to remove the 4 portal limit. I also recommend  `sv_cheats 1` with `noclip` so you can fly around.

It works by spawning in many `prop_portal` entities with unique names. It also creates a `scripted_sequence` entity with thousands of events with increasing delays to turn portals on and off at different times. Due to the limits of both the converter and Portal 2 I was only able to get a maximum output size of 26 x 26 before it broke (`no free edicts` in Portal 2 or a memory error in the converter)
