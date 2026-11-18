# Prépare le Sergent-Chef (modèle IA en pose en T) pour Mixamo : OBJ + MTL + texture PNG, pieds au sol, centré.
import bpy, sys, os
import numpy as np
from mathutils import Vector
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=sys.argv[1])
m = [o for o in bpy.context.scene.objects if o.type == 'MESH'][0]
for o in bpy.context.scene.objects: o.select_set(False)
m.select_set(True); bpy.context.view_layer.objects.active = m
bpy.ops.object.parent_clear(type='CLEAR_KEEP_TRANSFORM'); bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
V = np.array([v.co[:] for v in m.data.vertices])
d = Vector((-(V[:, 0].min() + V[:, 0].max()) / 2, -float(np.median(V[:, 1])), -V[:, 2].min()))
for v in m.data.vertices: v.co += d
m.name = 'SergentChef'
out = sys.argv[2]; os.makedirs(out, exist_ok=True)
for img in bpy.data.images:
    if img.size[0] > 0:
        img.filepath_raw = os.path.join(out, 'texture.png'); img.file_format = 'PNG'; img.save(); break
bpy.ops.wm.obj_export(filepath=os.path.join(out, 'SergentChef.obj'), export_selected_objects=True, export_materials=True,
                      path_mode='STRIP', forward_axis='NEGATIVE_Z', up_axis='Y')
print('OK', os.listdir(out))
