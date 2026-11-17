# Pompes Mixamo -> GLB : mains à plat (paume au sol, doigts vers l'avant), doigts tendus, corps posé au sol.
# Usage : python pompes_fix.py entree.fbx sortie.glb
import bpy, sys
from mathutils import Matrix, Vector
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.fbx(filepath=sys.argv[1], automatic_bone_orientation=False)
sc = bpy.context.scene
arm = [o for o in sc.objects if o.type == 'ARMATURE'][0]
arm.scale = (1, 1, 1); bpy.context.view_layer.update()
act = arm.animation_data.action
f0, f1 = int(act.frame_range[0]), int(act.frame_range[1]); sc.frame_start, sc.frame_end = f0, f1
P = 'mixamorig:'
AW = arm.matrix_world.to_3x3().normalized()

def repere(y, n):
    y = y.normalized(); n = (n - y * n.dot(y)).normalized(); x = y.cross(n)
    return Matrix((x, y, n)).transposed()  # colonnes : x, y, n

# Orientation de repos de chaque main : axe Y = le long de la main ; paume vers l'avant du modèle (-Y monde) en pose en T
cibles = {}
for c in ('Left', 'Right'):
    b = arm.data.bones[P + c + 'Hand']
    Rr = (AW @ b.matrix_local.to_3x3()).normalized()          # repos, en monde
    n_loc = Rr.transposed() @ Vector((0, -1, 0))               # normale de paume, dans le repère de l'os
    L = repere(Vector((0, 1, 0)), n_loc)
    # voulu : doigts vers l'avant (vers la tête), paume vers le sol
    sc.frame_set(f0); bpy.context.view_layer.update()
    tete = arm.matrix_world @ arm.pose.bones[P + 'Head'].head; pied = arm.matrix_world @ arm.pose.bones[P + 'LeftFoot'].head
    avant = Vector((tete.x - pied.x, tete.y - pied.y, 0)).normalized()
    Wd = repere(avant, Vector((0, 0, -1)))
    cibles[c] = Wd @ L.transposed()                            # rotation monde voulue pour l'os de la main

doigts = [b.name for b in arm.pose.bones if 'Thumb' in b.name or 'Index' in b.name]
mondeInv = arm.matrix_world.inverted()
for f in range(f0, f1 + 1):
    sc.frame_set(f); bpy.context.view_layer.update()
    for c in ('Left', 'Right'):
        pb = arm.pose.bones[P + c + 'Hand']
        tete_os = pb.matrix.translation.copy()
        R_arm = (mondeInv.to_3x3().normalized() @ cibles[c]).to_4x4()
        R_arm.translation = tete_os
        pb.matrix = R_arm; bpy.context.view_layer.update()
        pb.keyframe_insert('rotation_quaternion', frame=f)
    for n in doigts:
        pb = arm.pose.bones[n]; pb.rotation_quaternion = (1, 0, 0, 0); pb.keyframe_insert('rotation_quaternion', frame=f)

# Posé au sol : le point le plus bas du maillage, sur toute l'animation, va à z = 0
me = [o for o in sc.objects if o.type == 'MESH'][0]; zmin = 1e9
for f in range(f0, f1 + 1, 3):
    sc.frame_set(f); dg = bpy.context.evaluated_depsgraph_get(); ev = me.evaluated_get(dg); m = ev.to_mesh()
    zmin = min(zmin, min((me.matrix_world @ v.co).z for v in m.vertices)); ev.to_mesh_clear()
arm.location.z -= zmin
print('sol corrigé de', round(zmin, 4))
bpy.ops.export_scene.gltf(filepath=sys.argv[2], export_format='GLB', export_animations=True, export_skins=True, export_yup=True,
                          export_image_format='JPEG', export_image_quality=85, export_frame_range=True)
print('OK')
