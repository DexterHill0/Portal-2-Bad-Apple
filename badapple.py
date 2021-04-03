# imageio
# vmflib
# cv2

import argparse
import os
import subprocess
import shutil
import time
from pathlib import Path

import imageio
import cv2
import numpy as np

import vmf


args = None


# kinda like RLE for a numpy array
def get_groups(y, trigger_val, stopind_inclusive=True):
    y_ext = np.r_[False, y == trigger_val, False]
    idx = np.flatnonzero(y_ext[:-1] != y_ext[1:])

    return list(zip(idx[:-1:2], idx[1::2]-int(stopind_inclusive)))


def create_map():
    if(not os.path.exists(args.vid)):
        raise IOError("Cannot find video file!")

    map_folder = Path(args.p2) / \
        Path("portal2/maps/custom/")

    file = vmf.VMFFile(path=map_folder)

    events = []
    for x in range(0, args.w):
        for y in range(0, args.h):
            events.append(vmf.Event("OnUser1", "autoportal_%s" %
                                    vmf.EntityAutoPortal.portal_count, "SetActivatedState", "1", 0))
            p = vmf.EntityAutoPortal(
                name="autoportal_%s" % vmf.EntityAutoPortal.portal_count, origin=((x * 80) + 120, (y * 128) + 120, 5), colour="0")
            file.append(p)

    width = (args.w * 80) + 120
    height = (args.h * 128) + 120

    floor = vmf.Block(dimensions=(width, height, 16),
                      origin=(width / 2, height / 2, -8))
    file.append(floor)

    floor = vmf.Block(dimensions=(160, 160, 16),
                      origin=(320 + (floor.dim[0]/2), 0, 630))

    player = vmf.EntityPlayer(
        origin=(floor.origin[0] + 32, 0, 640), angles=(0, 180, 0))
    button = vmf.EntityButton(origin=(floor.origin[0] + 8, 0, 640),
                              events=[vmf.Event("OnPressed", "start_ba", "FireUser1")])

    file.append(floor)
    file.append(player)
    file.append(button)

    vid = imageio.get_reader(args.vid)
    fps = vid.get_meta_data(0).get("fps")

    if(args.f > fps):
        raise ValueError("FPS cannot be greater than %s" % fps)

    frame_count = 0
    delay = 0

    prev = []

    for frame in vid:
        if(frame_count >= (fps / args.f)):
            print("processing frame!")

            frame = cv2.resize(frame, dsize=(args.w, args.h),
                               interpolation=cv2.INTER_CUBIC)

            # video is black and white but is read as rgb so it has to be converted
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

            # make all values either 0 or 255 (black or white)
            new = np.where(frame.ravel() > 127, 255, 0)

            lows = get_groups(new, 0)
            highs = get_groups(new, 255)

            for l in lows:
                for i in range(l[0], l[1] + 1):
                    # big optimisation here: if the pixel has not changed colour since last frame, why add a new event, just keep it as it was
                    # went from about 3.1m events to 90k with this change
                    if(len(prev) == 0 or new[i] != prev[i]):
                        events.append(
                            vmf.Event("OnUser1", "autoportal_%s" % str(i), "SetActivatedState", "1", delay))

            for l in highs:
                for i in range(l[0], l[1] + 1):
                    if(len(prev) == 0 or new[i] != prev[i]):
                        events.append(
                            vmf.Event("OnUser1", "autoportal_%s" % str(i), "SetActivatedState", "0", delay))

            prev = new

            delay += (1 / args.f)
        frame_count += 1

    trigger = vmf.EntityScriptedSequence(
        name="start_ba", events=events)

    print("created scripted sequence entity with %s events!" % len(events))

    file.append(trigger)

    print("saving to file!")

    file.write_to_file(args.n + ".vmf")


def setup():
    global args

    parser = argparse.ArgumentParser(
        description="Creates Portal 2 map to play \"Bad Apple!!\"")

    parser.add_argument("--name", "-n", type=str,
                        help="Name of output file", dest="n", default=None)
    parser.add_argument("--video", "-vid", type=str,
                        help="Path to video", dest="vid", default=None)
    parser.add_argument("--portal2", "-p2", type=str,
                        help="Path to Portal 2 folder", dest="p2", default="C:\Program Files (x86)\Steam\steamapps\common\Portal 2")
    parser.add_argument("--width", "-w", type=int,
                        help="Width of output video", dest="w", default=100)
    parser.add_argument("--height", "-he", type=int,
                        help="Height of of output videp", dest="h", default=100)
    parser.add_argument("--frames", "-f", type=int,
                        help="Number of frames per second for output video", dest="f", default=10)

    args = parser.parse_args()


def main():
    setup()

    name = args.n + ".vmf"

    map_folder = Path(args.p2) / \
        Path("portal2/maps/custom/")

    if(not os.path.exists(args.p2)):
        raise IOError("Could not locate portal 2 folder!")

    map_folder.mkdir(parents=True, exist_ok=True)

    create_map()

    subprocess.Popen(["vbsp.exe", "-game", "../portal2/",
                      "../portal2/maps/custom/"+str(name)], cwd=Path(args.p2) / Path("bin/"), shell=True)


main()
