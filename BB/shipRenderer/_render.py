"""Galaxy on Fire 2 ship skin renderer

EARLY UNFINISHED PROTOTYPE

Written by Trimatix
"""
import bpy
import os
from math import radians
from PIL import Image, ImageOps
from pathlib import Path
from typing import List



##### CONFIG VARIABLES #####

# Determine the location of this script file. Used  for configuring script working paths below.
script_path = os.path.dirname(os.path.realpath(__file__))

# The camera's view distance. 5000 Should be plenty, but for larger models you may need to raise it. Tested with the Vossk Battlecruiser model.
CAM_CLIP = 5000
# Resolution of the render
# Moved to render_vars
# RES_X = 640
# RES_Y = 480
# Directory to save the final render in. The output file will have the same name as your model.
# Now disabled in favour of specifying the output dir via render_vars
# RENDER_OUTPUT_DIR = script_path + os.sep + "out"
# Working directory for the script. This is used for temporarily saving intermediate textures e.g between mask applications (TODO: Save the completed texture to a cache directory [the bbShipSkin dir])
RENDER_TEMP_DIR = script_path + os.sep + "temp"
# Path to the script's render variables file.
# Line 1:   Path to the model to render
# Line 2:   If rendering a single texture, the path to that texture. If rendering a base texture on top of another image, the path to the base texture.
# Line 3:   The path to the under-layer image if using one; the image to place underneith the base texture
# Line 4:   The path to the secondary texture region image if using one; This will be composited with respect to the secondary_mask.jpg found in the same directory as the model. This mask MUST exist in order for a passed secondary texture region image to be used.
# Line 4:   The path to the tertiary texture region image if using one; This will be composited with respect to the tertiary_mask.jpg found in the same directory as the model. This mask MUST exist in order for a passed tertiary texture region image to be used.
RENDER_ARGS_PATH = script_path + os.sep + "render_vars"



##### UTIL OBJECTS #####

class RenderArgs:
    """A data class representing arguments passed to the renderer.

    :var model_fullpath: The path to the model to render
    :vartype model_fullpath: str
    :var model_dir: Path to the directory containing the model
    :vartype model_dir: str
    :var model_filename: The name and file extension of the model file
    :vartype model_filename: str
    :var model_filename_noext: The name of the model file with no extension
    :vartype model_filename_noext: str
    :var base_texture_path: path to the base texture file containing the foreground features of the ship texture
    :vartype base_texture_path: str
    :var material: path to the material to render. It must be in model_dir, and called model_filename_noext + '.mtl'
    :vartype material: str
    :var texture_layers: A list of paths to texture files to mask and combine into the final ship texture
    :vartype texture_layers: List[str]
    :var has_textures: True if any textures were passed in texture_layers, False if texture_layers is empty
    :vartype has_textures: bool
    """

    def __init__(self, res_x : int, res_y : int, texture_output_file_path : str, render_output_file_path : str, model_path : str, base_texture_path : str, texture_layers : List[str]):
        """
        :param int res_x: The width in pixels of the render resolution.
        :param int res_y: The height in pixels of the render resolution.
        :param str texture_output_file_path: The path to save the final texture image to, including file name and extension
        :param str render_output_file_path: The path to render the output image to, including the file name and extension
        :param str model_path: The path to the model to render
        :param str base_texture_path: path to the base texture file containing the foreground features of the ship texture
        :param List[str] texture_layers: A list of paths to texture files to mask and combine into the final ship texture
        """
        self.res_x = res_x
        self.res_y = res_y
        self.texture_output_file_path = texture_output_file_path
        self.render_output_file_path = render_output_file_path
        self.model_fullpath = model_path
        self.model_dir = str(Path(self.model_fullpath).parent)
        self.model_filename = Path(self.model_fullpath).name
        self.model_filename_noext = Path(self.model_fullpath).stem
        self.base_texture_path = base_texture_path
        self.material = str(Path(self.model_fullpath).with_suffix(".mtl"))
        self.texture_layers = texture_layers
        self.has_textures = bool(texture_layers)


def getRenderArgs() -> RenderArgs:
    """Parse the arguments passed to the script via RENDER_ARGS_PATH, and return them in a RenderArgs object.

    :return: A RenderArgs object containing the passed renderer arguments
    :rtype: RenderArgs
    """
    args = []
    with open(RENDER_ARGS_PATH,"r") as f:
        for line in f.readlines():
            args.append(line.rstrip("\n"))
    return RenderArgs(int(args[0].split("x")[0]), int(args[0].split("x")[1]), args[1], args[2], args[3], args[4], args[5:] if len(args) > 5 else [])


def ensureImageMode(tex : Image, mode="RGBA") -> Image:
    """Ensure the passed image is in a given mode. If it is not, convert it.
    https://pillow.readthedocs.io/en/stable/handbook/concepts.html#concept-modes

    :param Image tex: The image whose mode to check
    :param str mode: The mode to ensure and convert to if needed
    :return: tex if it is of the given mode. tex converted to mode otherwise.
    :rtype: Image
    """
    return tex if tex.mode == mode else tex.convert(mode)



##### LOAD RENDERER ARGUMENTS #####

# Fetch renderer arguments
args = getRenderArgs()
# Load the images pointed to in args
if args.has_textures:
    # Load and combine the base texture and under layer
    workingTex = ensureImageMode(Image.open(args.texture_layers[0]))
    baseTex = ensureImageMode(Image.open(args.base_texture_path))
    workingTex = Image.alpha_composite(workingTex, baseTex)

    # For each layer number
    for layerData in [("secondary", 1), ("tertiary", 2)]:
        # Check that a corresponding texture was passed
        if len(args.texture_layers) > layerData[1]:
            # Check that a corresponding mask exists for the model
            try:
                mask = Image.open(args.model_dir + os.sep + layerData[0] + "_mask.jpg")
            except FileNotFoundError:
                print("WARNING: Attempted to render " + layerData[0] + " texture region for an model with no " + layerData[0] + "_mask: " + args.model_fullpath)
            else:
                # If both a texture and mask exist, load in the texture
                newTex = ensureImageMode(Image.open(args.texture_layers[layerData[1]]))
                # Load in the mask
                # Gimp and pillow use opposite shades to represent opacity in a mask, so invert the mask
                mask = ensureImageMode(ImageOps.invert(mask), "L")
                # Apply the texture with respect to the mask
                workingTex = Image.composite(workingTex, newTex, mask)

    # Save the completed ship texture to file
    # TODO: Change this to the cache (bbShipSkin) dir
    workingTex.save(RENDER_TEMP_DIR + os.sep + args.model_filename_noext + ".png")
    # Update the renderer arguments to point to the new texture
    args.base_texture_path = RENDER_TEMP_DIR + os.sep + args.model_filename_noext + ".png"

if args.texture_output_file_path.lower() not in ["", "none", "off"]:
    workingTex.convert("RGB").save(args.texture_output_file_path)
    


##### CONFIGURE THE SCENE #####

# Point the material at the requested texture
with open(args.material, "a") as f:
    f.write("map_Kd " + args.base_texture_path)

ctx = bpy.context
# import the model into blender's scene
bpy.ops.import_scene.obj(filepath=args.model_fullpath, axis_forward='-Z', axis_up='Y', filter_glob="*.obj;*.mtl")
# ensure nothing is currently selected, in case the camera is selected for some reason
bpy.ops.object.select_all(action='DESELECT')

# find the imported model in the scene
for obj in ctx.visible_objects:
    # Theoretically, nothing should be in the scene except for the model and the camera
    if obj.type != 'CAMERA':
        # Select the model
        obj.select_set(True)
        # Point the model in the correct direction
        obj.rotation_euler[0] = radians(0)
        # Set the camera view distance as configured earlier
        ctx.scene.camera.data.clip_end = CAM_CLIP



##### RENDER THE MODEL #####

# Set render resolution
ctx.scene.render.resolution_x = args.res_x
ctx.scene.render.resolution_y = args.res_y
ctx.scene.render.resolution_percentage = 100
# Set the renderer (eevee renders some strange perspective stuff...?)
ctx.scene.render.engine = 'CYCLES'
# Set the render output file
# ctx.scene.render.filepath = RENDER_OUTPUT_DIR + ("" if RENDER_OUTPUT_DIR.endswith(os.sep) else os.sep) + args.model_filename_noext
ctx.scene.render.filepath = args.render_output_file_path

# Move the camera so that the model fills the frame
bpy.ops.view3d.camera_to_view_selected()
# Zoom the camera back slightly to account for chromatic aberration
# If you remove chromatic aberration from the blender scene, either remove this line or set it to 50 (the default value)
bpy.data.cameras.values()[0].lens = 49
# Render the scene
bpy.ops.render.render(write_still=True)



##### CLEANUP #####

# Remove the material's pointer to the requested texture (will always be on the last line unless given an invalid material)
with open(args.material, "r") as f:
    lines = f.readlines()
with open(args.material, "w") as f:
    for line in lines[:-1]:
        f.write(line)

# If a temporary texture file was generated (the composition of the passed images), delete it
# TODO: Change this. Pass whether or not to delete the file as a boolean
if len(args.texture_layers) > 0:
    os.remove(args.base_texture_path)
