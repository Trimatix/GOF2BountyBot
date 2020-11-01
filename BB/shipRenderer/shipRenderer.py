"""Galaxy on Fire 2 ship skin renderer

EARLY UNFINISHED PROTOTYPE

Written by Trimatix
"""
from PIL import Image, ImageChops
import subprocess
import ntpath
# import sys
from typing import List
import os
import asyncio
from concurrent.futures import ThreadPoolExecutor

SCRIPT_PATH = os.path.dirname(os.path.realpath(__file__))
CWD = os.getcwd()

##### UTIL FUNCTIONS #####

def trim(im : Image) -> Image:
    """Crop image to content, written by neouyghur: https://stackoverflow.com/a/48605963/11754606

    :param Image im: The image to crop
    :return: im, with all surrounding empty space removed
    :rtype: Image
    """
    bg = Image.new(im.mode, im.size, im.getpixel((0,0)))
    diff = ImageChops.difference(im, bg)
    diff = ImageChops.add(diff, diff, 2.0, -100)
    bbox = diff.getbbox()
    if bbox:
        return im.crop(bbox)
    return im


def setRenderArgs(args : List[str]):
    """Pass arguments to the render via the arguments file

    :param List[str] args: List of arguments to write to file
    """
    with open(SCRIPT_PATH + os.sep + "render_vars","w") as f:
        for arg in args:
            f.write(arg + "\n")


def start_render():
    subprocess.call("blender -b \"" + SCRIPT_PATH + os.sep + "cube.blend\" -P \"" + SCRIPT_PATH + os.sep + "_render.py\"", shell=True)


async def renderShip(skinName : str, shipPath : str, shipModelName : str, textures : List[str], res_x : int, res_y : int): # TODO: Add 'useBaseTexture' argument. Pass to render_vars. If true, should bypass skinBase (for 'full' skins that don't use skinBase)
    """Render the given ship model with the specified skin layer(s).
    The resulting image is cropped to content and saved in shipPath + "/skins/" + skinName.jpg

    :param str skinName: The name of the skin being rendered. Depicts the name of the output file.
    :param str shipPath: Path to the bbShip being rendered. Must contain shipModelName
    :param str shipModelName: The name of the model file to render. Not a path. Must be contained within shipPath
    :param List[str] textures: List of paths to texture files to render the model with. The first element corresponds to the underlayer to render beneith the ship's base texture (foreground elements). All (currently 2) remaining textures are overlayed with respect to the ship's texture region masks.
    :param int res_x: The width in pixels of the render resolution. This is not the the width of the final image, as empty space around the rendered object is cropped out automatically.
    :param int res_y: The height in pixels of the render resolution. This is not the the height of the final image, as empty space around the rendered object is cropped out automatically.
    """
    # Generate render arguments
    current_model = shipPath + os.sep + shipModelName
    current_texes = [shipPath + os.sep + "skinBase.png"] + textures
    render_output_file = shipPath + os.sep + "skins" + os.sep + skinName + "-RENDER.png"
    texture_output_file = shipPath + os.sep + "skins" + os.sep + skinName + ".jpg"

    if res_x > 1920:
        raise ValueError("Attempted to render an image above 1080p (width=" + str(res_x) + ")")
    if res_y > 1080:
        raise ValueError("Attempted to render an image above 1080p (height=" + str(res_y) + ")")
    if res_x < 352:
        raise ValueError("Attempted to render an image below 240p (width=" + str(res_x) + ")")
    if res_y < 240:
        raise ValueError("Attempted to render an image below 240p (height=" + str(res_y) + ")")
    render_resolution = str(res_x) + "x" + str(res_y)

    # Pass the arguments to the renderer
    setRenderArgs([render_resolution, texture_output_file, render_output_file, current_model] + current_texes)
    # Render the requested model
    loop = asyncio.get_event_loop()
    await loop.run_in_executor(ThreadPoolExecutor(), start_render)

    # Load the newly rendered image
    bg = Image.open(render_output_file)
    # Crop it to content
    new_im = trim(bg)
    # Save it back to file
    new_im.save(render_output_file)
