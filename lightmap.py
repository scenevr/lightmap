# /Applications/Blender/blender.app/Contents/MacOS/blender --background --python lightmap.py

import os.path
import bpy

def selectObject(name):
  bpy.ops.object.select_all(action='DESELECT')
  bpy.ops.object.select_pattern(pattern=name)
  bpy.context.scene.objects.active = bpy.data.objects[name]

# Use cycles
bpy.context.scene.render.engine = 'CYCLES'

path = '/Users/ben/Projects/scene/lightmap/'
voxelFilename = os.path.join(path, 'voxel.obj')
print(voxelFilename)

bpy.ops.import_scene.obj(filepath = voxelFilename)

# Create destination image
resolution = 1024
imageName = 'lightmap'
imageFilename = os.path.join(path, 'lightmapped.png')
objFilename = os.path.join(path, 'lightmapped.obj')
bpy.ops.image.new(name=imageName, width=resolution, height=resolution)
image = bpy.data.images[imageName]

# Create the uv mappings
selectObject('voxel')
bpy.ops.uv.lightmap_pack(PREF_CONTEXT = 'ALL_OBJECTS', PREF_IMG_PX_SIZE = resolution, PREF_MARGIN_DIV = 0.2)

# Set material
mat = bpy.data.materials.new('Orange')
mat.use_nodes = True

nodes = mat.node_tree.nodes
nodes.get('Diffuse BSDF').inputs[0].default_value=(0, 0.3, 1, 1)

lightmapNode = nodes.new(type='ShaderNodeTexImage')
lightmapNode.image = image

bpy.context.object.data.materials.append(mat)

# Move the sun
selectObject('Lamp')
bpy.context.object.data.type = 'SUN'
bpy.ops.transform.translate(value=(0,0,30))

selectObject('voxel')
bpy.ops.object.bake(type='COMBINED')

# save the obj
bpy.ops.export_scene.obj(filepath=objFilename, use_selection=True, use_normals=True)

# save the image
image.file_format = 'PNG'
image.filepath_raw = imageFilename
image.save()
