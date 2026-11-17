# Fabrique une animation « maison » (position tenue + respiration) sur le squelette Mixamo du Sergent-Chef.
# Usage : python pose_maison.py squelette_mixamo.fbx exercice sortie.glb texture.png
# Exercices : gainage, gainage_lateral
import bpy, sys, math
from mathutils import Vector, Matrix
SRC, EX, OUT, TEX = sys.argv[1:5]
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.fbx(filepath=SRC, automatic_bone_orientation=False)
sc = bpy.context.scene
arm = [o for o in sc.objects if o.type == 'ARMATURE'][0]; arm.scale = (1, 1, 1)
me = [o for o in sc.objects if o.type == 'MESH'][0]
if arm.animation_data: arm.animation_data.action = None
for pb in arm.pose.bones: pb.rotation_mode = 'QUATERNION'; pb.rotation_quaternion = (1, 0, 0, 0); pb.location = (0, 0, 0)
bpy.context.view_layer.update()
P = 'mixamorig:'
def pb(n): return arm.pose.bones[P + n]
def W(n, queue=False):
    b = pb(n); return arm.matrix_world @ (b.tail if queue else b.head)

def viser(n, d, normale=None, garder=True):
    """Oriente l'os n vers la direction monde d (en gardant sa torsion de repos, ou en plaçant son axe Z vers 'normale')."""
    b = pb(n); bpy.context.view_layer.update()
    Mw = arm.matrix_world.to_3x3().normalized(); inv = Mw.inverted()
    d_a = (inv @ Vector(d)).normalized()
    R0 = b.bone.matrix_local.to_3x3()
    par = b.parent
    # rotation actuelle (armature) du repère de repos transporté par le parent
    if par: Rp = par.matrix.to_3x3() @ par.bone.matrix_local.to_3x3().inverted() @ R0
    else: Rp = R0
    y = Rp.col[1].normalized()
    q = y.rotation_difference(d_a); R = q.to_matrix() @ Rp
    if normale is not None:
        nz = (inv @ Vector(normale)); nz = (nz - d_a * nz.dot(d_a)).normalized()
        x = d_a.cross(nz); R = Matrix((x, d_a, nz)).transposed()
        # garder le sens de l'axe X de repos (évite une main retournée)
        if garder and R.col[0].dot(Rp.col[0]) < 0: R = Matrix((-x, d_a, -nz)).transposed()
    M = R.to_4x4(); M.translation = b.matrix.translation
    b.matrix = M; bpy.context.view_layer.update()

REPOS = {}   # orientation monde de chaque os dans la pose de repos (debout, face à -Y, gauche +X)
bpy.context.view_layer.update()
for b in arm.pose.bones: REPOS[b.name] = (arm.matrix_world @ b.matrix).to_3x3().normalized()

def orienter(n, haut, avant):
    """Tourne l'os n comme le corps entier : son « haut » devient 'haut', son « devant » devient 'avant' (repère monde)."""
    h = Vector(haut).normalized(); av = (Vector(avant) - h * Vector(avant).dot(h)).normalized(); g = h.cross(av)
    Q = Matrix((g, h, av)).transposed() @ Matrix(((1, 0, 0), (0, 0, 1), (0, -1, 0))).transposed().inverted()
    b = pb(n); bpy.context.view_layer.update()
    Mw = arm.matrix_world.to_3x3().normalized()
    R = Mw.inverted() @ Q @ REPOS[b.name]
    M = R.to_4x4(); M.translation = b.matrix.translation
    b.matrix = M; bpy.context.view_layer.update()

ANGLE = [0.08]   # inclinaison du corps (radians), ajustée au calage
def gainage(t):
    """Planche sur les avant-bras. t : phase de respiration 0..1."""
    r = math.sin(t * 2 * math.pi); a = ANGLE[0]
    corps = Vector((0, -math.cos(a), math.sin(a) + 0.012 * r)).normalized()   # du bassin vers la tête
    viser('Hips', corps)
    for n in ('Spine', 'Spine1', 'Spine2'): viser(n, corps)
    viser('Neck', Vector((0, -1, 0.42)).normalized()); viser('Head', Vector((0, -1, 0.55 + 0.02 * r)).normalized())   # tête dans l'alignement, regard vers le sol devant
    for c, s in (('Left', 1), ('Right', -1)):
        viser(c + 'Arm', Vector((s * 0.03, 0.06, -1)).normalized())                 # bras à la verticale, coude sous l'épaule
        viser(c + 'ForeArm', Vector((-s * 0.07, -1, 0)).normalized(), Vector((-s, 0, 0)), garder=False)            # avant-bras à plat, vers l'avant
        viser(c + 'Hand', Vector((-s * 0.04, -1, -0.03)).normalized(), Vector((-s, 0, 0)), garder=False)
        jambe = Vector((s * 0.03, math.cos(a), -math.sin(a))).normalized()
        viser(c + 'UpLeg', jambe); viser(c + 'Leg', jambe)
        viser(c + 'Foot', Vector((0, 0.45, -1)).normalized())                    # sur la pointe des pieds
        viser(c + 'ToeBase', Vector((0, 0.1, -1)).normalized())

def gainage_lateral(t):
    """Gainage latéral sur l'avant-bras droit, poitrine vers +X (vers la caméra), bras gauche tendu vers le ciel."""
    r = math.sin(t * 2 * math.pi); a = ANGLE[0]
    haut = Vector((0, -math.cos(a), math.sin(a))); avant = Vector((1, 0, 0))
    for n in ('Hips', 'Spine', 'Spine1', 'Spine2'): orienter(n, haut + Vector((0, 0, 0.012 * r)), avant)
    orienter('Neck', haut + Vector((0, 0, 0.05)), avant); orienter('Head', haut + Vector((0, 0, 0.08 + 0.02 * r)), avant + Vector((0, 0, -0.15)))
    viser('RightArm', Vector((0.04, 0, -1)).normalized())                                   # bras d'appui vertical, coude sous l'épaule
    viser('RightForeArm', Vector((1, -0.12, 0)).normalized(), Vector((0, -1, 0)), garder=False)   # avant-bras au sol, vers l'avant
    viser('RightHand', Vector((1, -0.08, -0.03)).normalized(), Vector((0, -1, 0)), garder=False)
    viser('LeftArm', Vector((0.03, -0.04, 1)).normalized())                                  # bras libre tendu vers le ciel
    viser('LeftForeArm', Vector((0.03, -0.04, 1)).normalized()); viser('LeftHand', Vector((0.02, -0.05, 1)).normalized())
    jambe = -haut
    for c, dz in (('Left', 0.0), ('Right', 0.0)):
        viser(c + 'UpLeg', jambe); viser(c + 'Leg', jambe)
        viser(c + 'Foot', (Vector((1, 0, 0)) * 0.9 + jambe * 0.42).normalized())          # pieds empilés, de profil
        viser(c + 'ToeBase', (Vector((1, 0, 0)) + jambe * 0.1).normalized())

def ecart_gainage(a):
    coude = (W('LeftForeArm') + W('RightForeArm')) / 2; orteil = (W('LeftToeBase', True) + W('RightToeBase', True)) / 2
    return (coude.z - 0.04) - orteil.z
def ecart_lateral(a):
    return (W('RightForeArm').z - 0.045) - (W('RightFoot').z - 0.06)

POSES = {'gainage': (gainage, ecart_gainage, 0.0, 0.3), 'gainage_lateral': (gainage_lateral, ecart_lateral, 0.2, 0.5)}
pose, mesure, A0, A1 = POSES[EX]

# Calage : on cherche l'inclinaison du corps qui pose l'appui (coudes) et les pieds à la même hauteur (sol)
def ecart(a):
    ANGLE[0] = a; pose(0); bpy.context.view_layer.update()
    return mesure(a)
a0, a1 = A0, A1; e0, e1 = ecart(a0), ecart(a1)
for _ in range(12):
    if abs(e1 - e0) < 1e-6: break
    a2 = a1 - e1 * (a1 - a0) / (e1 - e0); a0, e0 = a1, e1; a1, e1 = a2, ecart(a2)
ANGLE[0] = a1; print('angle du corps', round(math.degrees(a1), 1), 'écart', round(e1, 4))

N = 48; sc.frame_start, sc.frame_end = 1, N
for f in range(1, N + 1):
    sc.frame_set(f); pose((f - 1) / N); bpy.context.view_layer.update()
    for b in arm.pose.bones: b.keyframe_insert('rotation_quaternion', frame=f)
# posé au sol
zmin = 1e9
for f in range(1, N + 1, 6):
    sc.frame_set(f); dg = bpy.context.evaluated_depsgraph_get(); ev = me.evaluated_get(dg); m = ev.to_mesh()
    zmin = min(zmin, min((me.matrix_world @ v.co).z for v in m.vertices)); ev.to_mesh_clear()
arm.location.z -= zmin
nouv = bpy.data.images.load(TEX)
for mat in bpy.data.materials:
    if mat.use_nodes:
        for n in mat.node_tree.nodes:
            if n.type == 'TEX_IMAGE' and n.image and n.image.size[0] > 256 and n.image.colorspace_settings.name != 'Non-Color': n.image = nouv
bpy.ops.export_scene.gltf(filepath=OUT, export_format='GLB', export_animations=True, export_skins=True, export_yup=True,
                          export_image_format='JPEG', export_image_quality=85, export_frame_range=True)
print('OK', EX, 'sol', round(zmin, 3))
