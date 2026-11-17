# Animation Mixamo (FBX) -> GLB pour l'atelier : à l'échelle, posé au sol, texture au casque chromé.
# Usage : python mixamo_glb.py entree.fbx sortie.glb texture.png
import bpy, sys
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.fbx(filepath=sys.argv[1], automatic_bone_orientation=False)
sc = bpy.context.scene
arm = [o for o in sc.objects if o.type == 'ARMATURE'][0]
arm.scale = (1, 1, 1); bpy.context.view_layer.update()
act = arm.animation_data.action
f0, f1 = int(act.frame_range[0]), int(act.frame_range[1]); sc.frame_start, sc.frame_end = f0, f1
me = [o for o in sc.objects if o.type == 'MESH'][0]; zmin = 1e9
for f in range(f0, f1 + 1, 2):
    sc.frame_set(f); dg = bpy.context.evaluated_depsgraph_get(); ev = me.evaluated_get(dg); m = ev.to_mesh()
    zmin = min(zmin, min((me.matrix_world @ v.co).z for v in m.vertices)); ev.to_mesh_clear()
arm.location.z -= zmin
nouv = bpy.data.images.load(sys.argv[3])
for mat in bpy.data.materials:
    if mat.use_nodes:
        for n in mat.node_tree.nodes:
            if n.type == 'TEX_IMAGE' and n.image and n.image.size[0] > 256 and n.image.colorspace_settings.name != 'Non-Color': n.image = nouv
bpy.ops.export_scene.gltf(filepath=sys.argv[2], export_format='GLB', export_animations=True, export_skins=True, export_yup=True,
                          export_image_format='JPEG', export_image_quality=85, export_frame_range=True)
print('OK', f1 - f0 + 1, 'images, sol', round(zmin, 3))
