# Remplace la texture couleur d'un GLB ou FBX par une autre image, puis exporte en GLB.
import bpy,sys
bpy.ops.wm.read_factory_settings(use_empty=True)
src,tex,out=sys.argv[1],sys.argv[2],sys.argv[3]
if src.endswith('.fbx'):bpy.ops.import_scene.fbx(filepath=src)
else:bpy.ops.import_scene.gltf(filepath=src)
nouv=bpy.data.images.load(tex)
for m in bpy.data.materials:
    if not m.use_nodes:continue
    for n in m.node_tree.nodes:
        if n.type=='TEX_IMAGE' and n.image and n.image.size[0]>256 and n.image.colorspace_settings.name!='Non-Color':n.image=nouv
bpy.ops.export_scene.gltf(filepath=out,export_format='GLB',export_image_format='JPEG',export_image_quality=88)
print('OK')
