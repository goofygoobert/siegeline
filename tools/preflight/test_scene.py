import bpy
bpy.ops.wm.read_factory_settings(use_empty=True)
s=bpy.context.scene
bpy.ops.mesh.primitive_uv_sphere_add(radius=1)
m=bpy.data.materials.new("toy"); m.use_nodes=True
m.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value=(0.9,0.4,0.1,1)
bpy.context.object.data.materials.append(m)
bpy.ops.object.light_add(type='SUN',location=(3,-3,5))
bpy.ops.object.camera_add(location=(0,-5,1.5),rotation=(1.35,0,0)); s.camera=bpy.context.object
s.render.film_transparent=True
