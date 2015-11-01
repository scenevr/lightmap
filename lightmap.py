# /Applications/Blender/blender.app/Contents/MacOS/blender --background --python lightmap.py

import os.path
import bpy
import json
import struct

def selectObject(name):
  bpy.ops.object.select_all(action='DESELECT')
  bpy.ops.object.select_pattern(pattern=name)
  bpy.context.scene.objects.active = bpy.data.objects[name]

# Use cycles
bpy.context.scene.render.engine = 'CYCLES'

path = '/Users/ben/Projects/scene/lightmap/'
voxelFilename = os.path.join(path, 'input.obj')
print(voxelFilename)

root = os.path.dirname(__file__)
file = open(os.path.join(root, 'colors.json'), 'r')
palette = json.loads(file.read())

bpy.ops.import_scene.obj(filepath = voxelFilename)

def setLampStrength(name, strength):
  bpy.data.objects[name].data.use_nodes = True
  bpy.data.lamps[name].node_tree.nodes.get('Emission').inputs[1].default_value = strength

# Move the sun
selectObject('Lamp')
bpy.context.object.data.type = 'SUN'
bpy.ops.transform.translate(value=(0,0,30))
setLampStrength('Lamp', 0.1)

# Create destination image
resolution = 1024
imageName = 'lightmap'
imageFilename = os.path.join(path, 'lightmapped.png')
objFilename = os.path.join(path, 'lightmapped.obj')
bpy.ops.image.new(name=imageName, width=resolution, height=resolution)
image = bpy.data.images[imageName]

def hex_to_rgb(rgb_str):    
  int_tuple = struct.unpack('BBB', bytes.fromhex(rgb_str))    
  return tuple([val/255 for val in int_tuple])  

def setEmission(nodes, color, strength):
  # clear all nodes to start clean
  for node in nodes:
      nodes.remove(node)

  # create emission node
  node_emission = nodes.new(type='ShaderNodeEmission')
  node_emission.inputs[0].default_value = color  # green RGBA
  node_emission.inputs[1].default_value = strength # strength
  node_emission.location = 0,0

  # create output node
  node_output = nodes.new(type='ShaderNodeOutputMaterial')   
  node_output.location = 400,0

  # link nodes
  links = mat.node_tree.links
  link = links.new(node_emission.outputs[0], node_output.inputs[0])

def setDiffuse(nodes, color):
  nodes.get('Diffuse BSDF').inputs[0].default_value = color

# Set the textures
for ob in bpy.data.objects:
  if ob.name.startswith('texture'):
    bpy.ops.object.select_all(action='DESELECT')
    ob.select = True
    bpy.context.scene.objects.active = ob

    print(ob.name)

    index = int(ob.name.replace("texture", "")) + 1
    color = hex_to_rgb(palette[index].replace('#','')) + tuple([1.0])

    # Set material
    mat = bpy.data.materials.new(ob.name)
    mat.use_nodes = True

    nodes = mat.node_tree.nodes

    if (index > 1):
      setEmission(nodes, color, 5.0)
    else:
      setDiffuse(nodes, color)

    lightmapNode = nodes.new(type='ShaderNodeTexImage')
    lightmapNode.image = image

    bpy.context.object.data.materials.append(mat)

# Merge geometry
bpy.ops.object.select_all(action='DESELECT')
for ob in bpy.data.objects:
  if ob.name.startswith('texture'):
    ob.select = True
    bpy.context.scene.objects.active = ob

bpy.ops.object.join()
voxelObject = bpy.context.scene.objects.active

# Create the uv mappings
bpy.ops.uv.lightmap_pack(PREF_CONTEXT = 'ALL_OBJECTS', PREF_IMG_PX_SIZE = resolution, PREF_MARGIN_DIV = 0.2)

# Bake
bpy.ops.object.bake(type='COMBINED')

# save the obj
bpy.ops.export_scene.obj(filepath=objFilename, use_selection=True, use_normals=True)

# save the image
image.file_format = 'PNG'
image.filepath_raw = imageFilename
image.save()
