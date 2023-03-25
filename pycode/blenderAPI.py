import bpy
import mathutils
import sys

# รับตัวแปร from command line argument
obj_path = sys.argv[-5]
output_path = sys.argv[-4]
Resolution = int(sys.argv[-3])
Cube_size = float(sys.argv[-2])
exportwith = sys.argv[-1]

bpy.ops.object.delete(use_global=False, confirm=False)

# Import OBJ file
bpy.ops.wm.obj_import(filepath=obj_path)
# รวม object
bpy.ops.object.join()

# convert to voxel with Block On
bpy.ops.object.block_on()

bpy.context.object.modifiers["Block On"]["Input_1"] = Resolution
bpy.context.object.modifiers["Block On"]["Input_2"] = Cube_size
bpy.context.object.modifiers["Block On"]["Input_4"] = Resolution

bpy.ops.object.modifier_move_to_index(modifier="Block On", index=0)

# Select the object to scale
obj = bpy.context.active_object

# Calculate the current size of the object
current_size = max(obj.dimensions)

# Set the desired size for the object
desired_size = 9.0

# Calculate the scale factor to bring the object to the desired size
scale_factor = desired_size / current_size

# Set the object's scale to the desired size
obj.scale = mathutils.Vector((scale_factor, scale_factor, scale_factor))

bpy.ops.object.convert(target='MESH')
bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY', center='MEDIAN')

# Set the desired location for the object
desired_location = mathutils.Vector((0, 0, 0))

# Set the object's location to the desired location
obj.location = desired_location

# bpy.ops.export_scene.obj(filepath="D:\\Project\\Blender-command\\Output\\tree.obj",path_mode="COPY")
if exportwith == 'OBJ':
    bpy.ops.export_scene.obj(filepath=output_path,path_mode="COPY")

if exportwith == 'STL':
    bpy.ops.export_mesh.stl(filepath=output_path)
    