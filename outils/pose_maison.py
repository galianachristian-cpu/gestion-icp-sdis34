# Fabrique une animation « maison » (position tenue + respiration) sur le squelette Mixamo du Sergent-Chef.
# Usage : python pose_maison.py squelette_mixamo.fbx exercice sortie.glb texture.png
# Exercices : gainage, gainage_lateral, chaise, pont_fessier, superman, hollow, fentes, mountain_climbers, montees_genoux, etire_quadri, etire_epaule, etire_ischios, etire_dos
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

def phase(t, monte=0.28, tient=0.55, descend=0.82):
    """Mouvement aller-retour avec pause en haut : 0 -> 1 (monte), 1 (tient), 1 -> 0 (descend), 0 (repos)."""
    lis = lambda x: x * x * (3 - 2 * x)
    if t < monte: return lis(t / monte)
    if t < tient: return 1.0
    if t < descend: return 1 - lis((t - tient) / (descend - tient))
    return 0.0

def chaise(t):
    """Chaise contre le mur : dos droit, cuisses à l'horizontale, genoux au-dessus des chevilles, bras tendus devant."""
    r = math.sin(t * 2 * math.pi)
    for n in ('Hips', 'Spine', 'Spine1', 'Spine2'): orienter(n, (0, 0.04, 1 + 0.01 * r), (0, -1, 0))
    orienter('Neck', (0, -0.05, 1), (0, -1, 0)); orienter('Head', (0, -0.02, 1), (0, -1, 0.05 * r))
    for c, s in (('Left', 1), ('Right', -1)):
        bras = Vector((s * 0.1, -1, 0.02 * r)).normalized()
        viser(c + 'Arm', bras); viser(c + 'ForeArm', bras); viser(c + 'Hand', bras)
        viser(c + 'UpLeg', Vector((s * 0.1, -1, 0)).normalized()); viser(c + 'Leg', Vector((0, 0.02, -1)).normalized())
        viser(c + 'Foot', Vector((0, -0.85, -0.5)).normalized()); viser(c + 'ToeBase', Vector((0, -1, -0.05)).normalized())

LEVE = [0.0]
def pont_fessier(t):
    """Pont fessier : sur le dos, genoux pliés, le bassin monte, tient 2 s, redescend.
    Le buste se lève avec le mouvement ; ANGLE = angle des cuisses, calé pour que les pieds restent à plat au sol."""
    a = 0.03 + 0.42 * LEVE[0]; b = ANGLE[0]
    for n in ('Hips', 'Spine', 'Spine1', 'Spine2'): orienter(n, (0, -math.cos(a), -math.sin(a)), (0, 0, 1))
    orienter('Neck', (0, -1, 0.25), (0, 0, 1)); orienter('Head', (0, -1, 0.05), (0, 0, 1))
    for c, s in (('Left', 1), ('Right', -1)):          # sur le dos, la gauche du personnage est vers -X
        bras = Vector((-s * 0.14, 1, -0.06)).normalized()
        viser(c + 'Arm', bras); viser(c + 'ForeArm', bras); viser(c + 'Hand', bras)
        viser(c + 'UpLeg', Vector((-s * 0.06, math.cos(b), math.sin(b))).normalized())
        viser(c + 'Leg', Vector((-s * 0.02, -0.15, -1)).normalized())
        viser(c + 'Foot', Vector((0, 1, -0.35)).normalized()); viser(c + 'ToeBase', Vector((0, 1, 0)).normalized())

def superman(t):
    """Superman : sur le ventre, bras et jambes se lèvent ensemble, tient 2 s, redescendent. Regard vers le sol."""
    l = LEVE[0]
    for n, k in (('Hips', 0.0), ('Spine', 0.1), ('Spine1', 0.22), ('Spine2', 0.32)): orienter(n, (0, -1, k * l), (0, 0, -1))
    orienter('Neck', (0, -1, 0.36 * l + 0.05), (0, 0, -1)); orienter('Head', (0, -1, 0.3 * l + 0.03), (0, 0, -1))
    for c, s in (('Left', 1), ('Right', -1)):
        bras = Vector((s * 0.16, -1, 0.04 + 0.4 * l)).normalized()
        viser(c + 'Arm', bras); viser(c + 'ForeArm', bras); viser(c + 'Hand', bras)
        viser(c + 'UpLeg', Vector((s * 0.05, 1, 0.03 + 0.24 * l)).normalized()); viser(c + 'Leg', Vector((s * 0.03, 1, 0.05 + 0.3 * l)).normalized())
        viser(c + 'Foot', Vector((0, 1, -0.3)).normalized()); viser(c + 'ToeBase', Vector((0, 1, -0.1)).normalized())

def hollow(t):
    """Hollow hold : sur le dos, bras et jambes tendus décollés du sol, le corps en banane, bas du dos collé au sol."""
    r = math.sin(t * 2 * math.pi)
    for n, k in (('Hips', 0.0), ('Spine', 0.12), ('Spine1', 0.26), ('Spine2', 0.38)): orienter(n, (0, -1, k + 0.01 * r), (0, 0, 1))
    orienter('Neck', (0, -1, 0.45), (0, 0, 1)); orienter('Head', (0, -1, 0.42), (0, 0, 1))
    for c, s in (('Left', 1), ('Right', -1)):
        bras = Vector((-s * 0.1, -1, 0.32 + 0.01 * r)).normalized()
        viser(c + 'Arm', bras); viser(c + 'ForeArm', bras); viser(c + 'Hand', bras)
        jambe = Vector((-s * 0.03, 1, 0.3 + 0.01 * r)).normalized()
        viser(c + 'UpLeg', jambe); viser(c + 'Leg', jambe)
        viser(c + 'Foot', Vector((0, 1, 0.05)).normalized()); viser(c + 'ToeBase', Vector((0, 1, 0.05)).normalized())

def ecart_pont(a):
    epaule = (W('LeftArm') + W('RightArm')) / 2; talon = (W('LeftFoot') + W('RightFoot')) / 2
    return (epaule.z - 0.07) - (talon.z - 0.08)

def main_a_plat(c, avant=(0, -1, 0)):
    """Main à plat au sol, doigts vers 'avant' (même méthode que mixamo_mains_a_plat.py)."""
    def rep(y, n):
        y = Vector(y).normalized(); n = Vector(n); n = (n - y * n.dot(y)).normalized(); return Matrix((y.cross(n), y, n)).transposed()
    Rr = REPOS[P + c + 'Hand']; L = rep((0, 1, 0), Rr.transposed() @ Vector((0, -1, 0)))
    b = pb(c + 'Hand'); bpy.context.view_layer.update()
    M = (arm.matrix_world.to_3x3().normalized().inverted() @ rep(avant, (0, 0, -1)) @ L.transposed()).to_4x4()
    M.translation = b.matrix.translation; b.matrix = M; bpy.context.view_layer.update()

def bras_balance(c, s, k):
    """Bras de course : coude plié à 90°, le bras se balance d'avant en arrière selon k (-1..1)."""
    a = 0.75 * k
    viser(c + 'Arm', Vector((s * 0.12, -math.sin(a), -math.cos(a))).normalized())
    viser(c + 'ForeArm', Vector((s * 0.05, -math.cos(a) * 0.9, math.sin(a) * 0.9 + 0.25)).normalized())
    viser(c + 'Hand', Vector((s * 0.05, -math.cos(a) * 0.9, math.sin(a) * 0.9 + 0.25)).normalized())

def debout(lean=0.0, r=0.0):
    for n in ('Hips', 'Spine', 'Spine1', 'Spine2'): orienter(n, (0, -lean, 1 + 0.01 * r), (0, -1, 0))
    orienter('Neck', (0, -lean * 0.5, 1), (0, -1, 0)); orienter('Head', (0, 0, 1), (0, -1, 0))

COTE = ['Left']
def fentes(t):
    """Fente avant alternée : un pas en avant, on descend genou arrière vers le sol, on remonte pieds joints, puis l'autre jambe.
    ANGLE = angle de la cuisse arrière, calé pour que les deux pieds restent au sol."""
    t2 = (t * 2) % 1; d = 0.5 - 0.5 * math.cos(2 * math.pi * t2); COTE[0] = 'Left' if t < 0.5 else 'Right'
    debout(0.06 * d)
    for c, s in (('Left', 1), ('Right', -1)):
        viser(c + 'Arm', Vector((s * 0.15, 0.03, -1)).normalized()); viser(c + 'ForeArm', Vector((s * 0.1, -0.15, -1)).normalized())
        viser(c + 'Hand', Vector((s * 0.1, -0.15, -1)).normalized())
        if c == COTE[0]:   # jambe avant
            th = 1.35 * d
            viser(c + 'UpLeg', Vector((s * 0.08, -math.sin(th), -math.cos(th))).normalized())
            viser(c + 'Leg', Vector((s * 0.04, 0.08 * d, -1)).normalized())
            viser(c + 'Foot', Vector((0, -0.85, -0.5)).normalized()); viser(c + 'ToeBase', Vector((0, -1, -0.05)).normalized())
        else:              # jambe arrière : genou qui descend vers le sol, sur la pointe du pied
            th = ANGLE[0] * d
            cuisse = Vector((s * 0.08, math.sin(th), -math.cos(th))).normalized()
            viser(c + 'UpLeg', cuisse)
            tibia = (cuisse * (1 - d) + Vector((0, 1, -0.35)).normalized() * d).normalized()
            viser(c + 'Leg', tibia)
            viser(c + 'Foot', (Vector((0, -0.85, -0.5)) * (1 - d) + Vector((0, -0.3, -1)) * d).normalized())
            viser(c + 'ToeBase', Vector((0, -1, -0.05)).normalized())
def ecart_fentes(a):
    av = COTE[0]; ar = 'Right' if av == 'Left' else 'Left'
    return W(ar + 'ToeBase', True).z - (W(av + 'Foot').z - 0.075)

GENOU = [0.0, 0.0]
def mountain_climbers(t):
    """Mountain climbers : planche bras tendus, on ramène un genou vers la poitrine puis l'autre, vite.
    ANGLE = inclinaison du corps, calée pour que les mains et le pied d'appui touchent le sol."""
    a = ANGLE[0]; ph = math.sin(2 * math.pi * t)
    GENOU[0], GENOU[1] = max(0.0, ph) ** 0.8, max(0.0, -ph) ** 0.8
    haut = Vector((0, -math.cos(a), math.sin(a)))
    for n in ('Hips', 'Spine', 'Spine1', 'Spine2'): orienter(n, haut, (0, 0, -1))
    orienter('Neck', haut + Vector((0, 0, 0.15)), (0, 0, -1)); orienter('Head', haut + Vector((0, 0, 0.2)), (0, 0, -1))
    for (c, s), g in zip((('Left', 1), ('Right', -1)), GENOU):
        bras = Vector((s * 0.06, -0.05, -1)).normalized()
        viser(c + 'Arm', bras); viser(c + 'ForeArm', bras); main_a_plat(c)
        jambe = -haut
        cuisse = (jambe * (1 - g) + Vector((s * 0.1, -0.88, -0.42)).normalized() * g).normalized()
        tibia = (jambe * (1 - g) + Vector((0, 0.95, -0.3)).normalized() * g).normalized()
        viser(c + 'UpLeg', cuisse); viser(c + 'Leg', tibia)
        viser(c + 'Foot', (Vector((0, 0.45, -1)).normalized() * (1 - g) + Vector((0, 1, 0.15)).normalized() * g).normalized())   # pied du genou ramené : pointe vers l'arrière
        viser(c + 'ToeBase', (Vector((0, 0.1, -1)) * (1 - g) + Vector((0, 1, 0.15)) * g).normalized())
def ecart_mc(a):
    appui = 'Right' if GENOU[0] >= GENOU[1] else 'Left'
    mains = (W('LeftHand') + W('RightHand')) / 2
    return (mains.z - 0.05) - W(appui + 'ToeBase', True).z

def montees_genoux(t):
    """Montées de genoux : course sur place, genou à hauteur de hanche, bras qui balancent."""
    ph = math.sin(2 * math.pi * t); kg, kd = max(0.0, ph), max(0.0, -ph)
    debout(0.04)
    for (c, s), k, kb in ((('Left', 1), kg, -ph), (('Right', -1), kd, ph)):
        th = 1.5 * k
        viser(c + 'UpLeg', Vector((s * 0.06, -math.sin(th), -math.cos(th))).normalized())
        viser(c + 'Leg', Vector((0, 0.15 * k + 0.02, -1)).normalized())
        viser(c + 'Foot', (Vector((0, -0.85, -0.5)) * (1 - k) + Vector((0, -0.5, -0.85)) * k).normalized())
        viser(c + 'ToeBase', Vector((0, -1, -0.05)).normalized())
        bras_balance(c, s, kb)

def etire_quadri(t):
    """Étirement des quadriceps debout : talon droit tenu contre la fesse, main gauche tendue pour l'équilibre, respiration lente."""
    r = math.sin(t * 2 * math.pi); debout(0.03, r)
    for c, s in (('Left', 1), ('Right', -1)):
        if c == 'Right':   # jambe pliée : genou vers le bas, talon vers la fesse
            viser(c + 'UpLeg', Vector((s * 0.05, 0.08, -1)).normalized()); viser(c + 'Leg', Vector((0, 0.35, 0.94)).normalized())
            viser(c + 'Foot', Vector((0, 0.9, 0.3)).normalized()); viser(c + 'ToeBase', Vector((0, 1, 0)).normalized())
            viser(c + 'Arm', Vector((s * 0.25, 0.35, -0.9)).normalized()); viser(c + 'ForeArm', Vector((s * 0.05, 0.85, -0.5)).normalized()); viser(c + 'Hand', Vector((0, 0.9, -0.4)).normalized())
        else:
            viser(c + 'UpLeg', Vector((s * 0.06, 0, -1)).normalized()); viser(c + 'Leg', Vector((s * 0.03, 0.02, -1)).normalized())
            viser(c + 'Foot', Vector((0, -0.85, -0.5)).normalized()); viser(c + 'ToeBase', Vector((0, -1, -0.05)).normalized())
            bras = Vector((s * 0.75, -0.35, 0.05 + 0.03 * r)).normalized(); viser(c + 'Arm', bras); viser(c + 'ForeArm', bras); viser(c + 'Hand', bras)

def etire_epaule(t):
    """Étirement de l'épaule : bras droit tendu en travers de la poitrine, tenu par l'avant-bras gauche ; on alterne à mi-temps."""
    r = math.sin(t * 2 * math.pi); debout(0.0, r); cote = 'Right' if t < 0.5 else 'Left'
    for c, s in (('Left', 1), ('Right', -1)):
        viser(c + 'UpLeg', Vector((s * 0.1, 0, -1)).normalized()); viser(c + 'Leg', Vector((s * 0.05, 0.02, -1)).normalized())
        viser(c + 'Foot', Vector((0, -0.85, -0.5)).normalized()); viser(c + 'ToeBase', Vector((0, -1, -0.05)).normalized())
        if c == cote:   # bras étiré : en travers, horizontal
            bras = Vector((-s * 0.9, -0.42, -0.05)).normalized(); viser(c + 'Arm', bras); viser(c + 'ForeArm', bras); viser(c + 'Hand', bras)
        else:           # bras qui tient : coude plié, avant-bras sous le bras étiré
            viser(c + 'Arm', Vector((s * 0.15, -0.35, -0.92)).normalized()); viser(c + 'ForeArm', Vector((-s * 0.85, -0.4, 0.35)).normalized()); viser(c + 'Hand', Vector((-s * 0.9, -0.3, 0.2)).normalized())

def etire_ischios(t):
    """Étirement des ischio-jambiers assis : jambes tendues devant, buste penché vers les pieds, mains vers les chevilles."""
    k = 0.5 - 0.5 * math.cos(2 * math.pi * t)      # on se penche, on revient doucement
    a = 0.55 + 0.45 * k                              # buste : de presque droit à bien penché
    for n, f in (('Hips', 0.5), ('Spine', 0.8), ('Spine1', 1.0), ('Spine2', 1.0)): orienter(n, (0, -math.sin(a * f), math.cos(a * f)), (0, -1, 0))
    orienter('Neck', (0, -math.sin(a), math.cos(a) + 0.3), (0, -1, 0)); orienter('Head', (0, -math.sin(a) - 0.2, math.cos(a) + 0.2), (0, -1, 0))
    for c, s in (('Left', 1), ('Right', -1)):
        jambe = Vector((s * 0.08, -1, 0)).normalized(); viser(c + 'UpLeg', jambe); viser(c + 'Leg', jambe)
        viser(c + 'Foot', Vector((0, -0.2, 1)).normalized()); viser(c + 'ToeBase', Vector((0, -0.5, 1)).normalized())
        bras = Vector((s * 0.12, -1, -0.25 - 0.3 * k)).normalized(); viser(c + 'Arm', bras); viser(c + 'ForeArm', bras); viser(c + 'Hand', bras)

def etire_dos(t):
    """Posture de l'enfant : à genoux, fesses sur les talons, bras tendus loin devant, front vers le sol."""
    r = math.sin(t * 2 * math.pi)
    for n, k in (('Hips', 0.0), ('Spine', 0.15), ('Spine1', 0.3), ('Spine2', 0.4)): orienter(n, (0, -1, -0.55 + k * 0.4 + 0.02 * r), (0, 0, -1))
    orienter('Neck', (0, -1, -0.5), (0, 0, -1)); orienter('Head', (0, -1, -0.6), (0, 0, -1))
    for c, s in (('Left', 1), ('Right', -1)):
        viser(c + 'UpLeg', Vector((s * 0.12, -0.55, -0.83)).normalized()); viser(c + 'Leg', Vector((0, 1, -0.05)).normalized())
        viser(c + 'Foot', Vector((0, 1, 0.2)).normalized()); viser(c + 'ToeBase', Vector((0, 1, 0.2)).normalized())
        bras = Vector((s * 0.15, -1, -0.12)).normalized(); viser(c + 'Arm', bras); viser(c + 'ForeArm', bras); viser(c + 'Hand', Vector((s * 0.1, -1, -0.15)).normalized(), Vector((0, 0, -1)), garder=False)

# nom : (pose, mesure de calage ou None, bornes de recherche, mouvement par image ou None)
POSES = {'gainage': (gainage, ecart_gainage, 0.0, 0.3, None), 'gainage_lateral': (gainage_lateral, ecart_lateral, 0.2, 0.5, None),
         'chaise': (chaise, None, 0, 0, None), 'pont_fessier': (pont_fessier, ecart_pont, 0.4, 1.0, phase),
         'superman': (superman, None, 0, 0, phase), 'hollow': (hollow, None, 0, 0, None),
         'fentes': (fentes, ecart_fentes, 0.3, 0.9, None), 'mountain_climbers': (mountain_climbers, ecart_mc, 0.1, 0.5, None),
         'montees_genoux': (montees_genoux, None, 0, 0, None),
         'etire_quadri': (etire_quadri, None, 0, 0, None), 'etire_epaule': (etire_epaule, None, 0, 0, None),
         'etire_ischios': (etire_ischios, None, 0, 0, None), 'etire_dos': (etire_dos, None, 0, 0, None)}
pose, mesure, A0, A1, mouvement = POSES[EX]

# Calage : on cherche l'inclinaison du corps qui pose l'appui et les pieds à la même hauteur (sol)
def ecart(a, t):
    ANGLE[0] = a; pose(t); bpy.context.view_layer.update()
    return mesure(a)
def caler(t):
    if not mesure: return
    a0, a1 = A0, A1; e0, e1 = ecart(a0, t), ecart(a1, t)
    for _ in range(14):
        if abs(e1 - e0) < 1e-7: break
        a2 = a1 - e1 * (a1 - a0) / (e1 - e0); a0, e0 = a1, e1; a1, e1 = a2, ecart(a2, t)
    ANGLE[0] = a1

def sol_mesh():
    dg = bpy.context.evaluated_depsgraph_get(); ev = me.evaluated_get(dg); m = ev.to_mesh()
    z = min((me.matrix_world @ v.co).z for v in m.vertices); ev.to_mesh_clear(); return z

N = 48; sc.frame_start, sc.frame_end = 1, N
for f in range(1, N + 1):
    t = (f - 1) / N; sc.frame_set(f)
    LEVE[0] = mouvement(t) if mouvement else 0.0
    caler(t); pose(t); arm.location.z = 0; bpy.context.view_layer.update()
    arm.location.z = -sol_mesh(); bpy.context.view_layer.update()          # toujours posé au sol, image par image
    for b in arm.pose.bones: b.keyframe_insert('rotation_quaternion', frame=f)
    arm.keyframe_insert('location', frame=f)
print('angle', round(math.degrees(ANGLE[0]), 1))
zmin = 0.0
if EX == 'chaise':   # le mur derrière le dos
    sc.frame_set(1); bpy.context.view_layer.update()
    dos = max((me.matrix_world @ v.co).y for v in me.evaluated_get(bpy.context.evaluated_depsgraph_get()).to_mesh().vertices
              if (me.matrix_world @ v.co).z > W('Spine').z)
    bpy.ops.mesh.primitive_cube_add(size=1, location=(0, dos + 0.03, 0.85)); mur = bpy.context.active_object
    mur.scale = (1.5, 0.06, 1.7); mur.name = 'mur'
    mm = bpy.data.materials.new('mur'); mm.use_nodes = True; mm.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value = (0.82, 0.78, 0.7, 1)
    mur.data.materials.append(mm)
nouv = bpy.data.images.load(TEX)
for mat in bpy.data.materials:
    if mat.use_nodes:
        for n in mat.node_tree.nodes:
            if n.type == 'TEX_IMAGE' and n.image and n.image.size[0] > 256 and n.image.colorspace_settings.name != 'Non-Color': n.image = nouv
bpy.ops.export_scene.gltf(filepath=OUT, export_format='GLB', export_animations=True, export_skins=True, export_yup=True,
                          export_image_format='JPEG', export_image_quality=85, export_frame_range=True)
print('OK', EX, 'sol', round(zmin, 3))
