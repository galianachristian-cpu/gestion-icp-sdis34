# Transfère une animation Mixamo d'un personnage à un autre (même squelette « mixamorig: »), puis exporte en GLB pour l'atelier.
# On recopie l'orientation de chaque os dans le monde (en tenant compte des poses de repos de chacun)
# et le déplacement du bassin, mis à l'échelle de la taille du personnage cible.
# Usage : python transfert_mixamo.py animation_source.fbx personnage_cible.fbx sortie.glb texture.png
# MAINS_A_PLAT=1 : pour les pompes, mains à plat au sol (même correction que mixamo_mains_a_plat.py)
import bpy, sys, os
from mathutils import Matrix, Vector
SRC, CIBLE, OUT, TEX = sys.argv[1:5]
bpy.ops.wm.read_factory_settings(use_empty=True)

def importer(f):
    avant = set(bpy.data.objects)
    bpy.ops.import_scene.fbx(filepath=f, automatic_bone_orientation=False)
    nouv = [o for o in bpy.data.objects if o not in avant]
    a = [o for o in nouv if o.type == 'ARMATURE'][0]; a.scale = (1, 1, 1)
    return a, [o for o in nouv if o.type == 'MESH']

T, mT = importer(CIBLE)
if T.animation_data: T.animation_data.action = None
for pb in T.pose.bones: pb.rotation_mode = 'QUATERNION'; pb.rotation_quaternion = (1, 0, 0, 0); pb.location = (0, 0, 0)
S, mS = importer(SRC)
for o in mS: bpy.data.objects.remove(o)          # le maillage source ne sert à rien (et ralentit)
sc = bpy.context.scene; bpy.context.view_layer.update()
act = S.animation_data.action; f0, f1 = int(act.frame_range[0]), int(act.frame_range[1]); sc.frame_start, sc.frame_end = f0, f1

nom = lambda n: n.split(':')[-1]
osS = {nom(b.name): b for b in S.pose.bones}
RS0 = {nom(b.name): (S.matrix_world.to_3x3() @ b.bone.matrix_local.to_3x3()).normalized() for b in S.pose.bones}
RT0 = {nom(b.name): (T.matrix_world.to_3x3() @ b.bone.matrix_local.to_3x3()).normalized() for b in T.pose.bones}
AT = T.matrix_world.to_3x3().normalized(); ATi = AT.inverted()
# échelle : hauteur du bassin au repos
hS = (S.matrix_world @ osS['Hips'].bone.head_local).z; hT = (T.matrix_world @ T.pose.bones[T.pose.bones[0].name].bone.head_local).z
k = hT / hS
print('échelle', round(k, 3), 'images', f0, f1)

ordre = list(T.pose.bones)   # les parents viennent avant les enfants
for f in range(f0, f1 + 1):
    sc.frame_set(f)
    Rarm = {}   # rotation (repère armature) déjà calculée pour chaque os cible
    for b in ordre:
        n = nom(b.name)
        if n not in osS: Rarm[b.name] = b.bone.matrix_local.to_3x3(); continue
        RSw = (S.matrix_world.to_3x3() @ osS[n].matrix.to_3x3()).normalized()
        RTw = RSw @ RS0[n].inverted() @ RT0[n]
        Rd = (ATi @ RTw).normalized(); Rarm[b.name] = Rd
        rest = b.bone.matrix_local.to_3x3()
        if b.parent:
            prest = b.parent.bone.matrix_local.to_3x3()
            base = Rarm[b.parent.name] @ prest.inverted() @ rest
        else:
            base = rest
        b.rotation_quaternion = (base.inverted() @ Rd).to_quaternion()
        if not b.parent:   # le bassin se déplace : position monde de la source, à l'échelle de la cible
            pS = S.matrix_world @ osS[n].head
            pd = ATi @ ((Vector((pS.x, pS.y, pS.z)) * k) - T.matrix_world.translation) - b.bone.head_local
            b.location = rest.inverted() @ pd
            b.keyframe_insert('location', frame=f)
        b.keyframe_insert('rotation_quaternion', frame=f)
bpy.data.objects.remove(S)
bpy.context.view_layer.update()
if os.environ.get('MAINS_A_PLAT'):
    P = 'mixamorig:'; AW = T.matrix_world.to_3x3().normalized()
    def repere(y, n):
        y = y.normalized(); n = (n - y * n.dot(y)).normalized(); return Matrix((y.cross(n), y, n)).transposed()
    sc.frame_set(f0); bpy.context.view_layer.update()
    tete = T.matrix_world @ T.pose.bones[P + 'Head'].head; pied = T.matrix_world @ T.pose.bones[P + 'LeftFoot'].head
    Wd = repere(Vector((tete.x - pied.x, tete.y - pied.y, 0)).normalized(), Vector((0, 0, -1)))
    cibles = {}
    for c in ('Left', 'Right'):
        Rr = (AW @ T.data.bones[P + c + 'Hand'].matrix_local.to_3x3()).normalized()
        cibles[c] = Wd @ repere(Vector((0, 1, 0)), Rr.transposed() @ Vector((0, -1, 0))).transposed()
    doigts = [b.name for b in T.pose.bones if 'Thumb' in b.name or 'Index' in b.name]
    for f in range(f0, f1 + 1):
        sc.frame_set(f); bpy.context.view_layer.update()
        for c in ('Left', 'Right'):
            pb = T.pose.bones[P + c + 'Hand']; M = (T.matrix_world.inverted().to_3x3().normalized() @ cibles[c]).to_4x4()
            M.translation = pb.matrix.translation.copy(); pb.matrix = M; bpy.context.view_layer.update()
            pb.keyframe_insert('rotation_quaternion', frame=f)
        for n in doigts:
            pb = T.pose.bones[n]; pb.rotation_quaternion = (1, 0, 0, 0); pb.keyframe_insert('rotation_quaternion', frame=f)
    print('mains à plat')
# posé au sol (sur tout le clip, comme mixamo_glb.py : les sauts restent des sauts)
me = mT[0]; zmin = 1e9
for f in range(f0, f1 + 1, 2):
    sc.frame_set(f); dg = bpy.context.evaluated_depsgraph_get(); ev = me.evaluated_get(dg); m = ev.to_mesh()
    zmin = min(zmin, min((me.matrix_world @ v.co).z for v in m.vertices)); ev.to_mesh_clear()
T.location.z -= zmin
nouv = bpy.data.images.load(TEX)
for mat in bpy.data.materials:
    if mat.use_nodes:
        for n in mat.node_tree.nodes:
            if n.type == 'TEX_IMAGE' and n.image and n.image.size[0] > 256 and n.image.colorspace_settings.name != 'Non-Color': n.image = nouv
bpy.ops.export_scene.gltf(filepath=OUT, export_format='GLB', export_animations=True, export_skins=True, export_yup=True,
                          export_image_format='JPEG', export_image_quality=85, export_frame_range=True)
print('OK', f1 - f0 + 1, 'images, sol', round(zmin, 3))
