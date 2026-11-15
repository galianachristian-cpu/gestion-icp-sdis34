# Modélisation du Sergent-Chef / de la Sergente-Chef pour « Rame en direct »
# Régénérer : pip install bpy, puis python outils/sergent3d_blender.py h img/rame/sergent-h.glb apercu.png (f pour la Sergente-Chef)
# Usage : python sergent.py <h|f> <sortie.glb> <apercu.png>
import bpy, bmesh, sys, math
from mathutils import Vector

genre, SORTIE, APERCU = sys.argv[1], sys.argv[2], sys.argv[3]
F = genre == 'f'
bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene

def mat(nom, rgb):
    m = bpy.data.materials.get(nom) or bpy.data.materials.new(nom)
    m.diffuse_color = (*rgb, 1); m.use_nodes = True
    bsdf = m.node_tree.nodes.get('Principled BSDF'); bsdf.inputs['Base Color'].default_value = (*rgb, 1); bsdf.inputs['Roughness'].default_value = .6
    return m
def lin(h):  # couleur hexa sRGB -> linéaire
    c = [int(h[i:i+2], 16) / 255 for i in (0, 2, 4)]
    return tuple(x / 12.92 if x <= .04045 else ((x + .055) / 1.055) ** 2.4 for x in c)
M = {n: mat(n, lin(h)) for n, h in dict(peau='e8a57c', rouge='d92323', jaune='facc15', marine='1e2f57', noir='1a1a1a', blanc='ffffff',
         argent='d9dde3', **{'or': 'f2b52a'}, brun='5a3214', rose='f29a8f', levres='c2414b', cheveux='3b2416').items()}

# ---------- Squelette du corps (sert de base à la peau « Skin ») ----------
L = 1
ep = 0.23 if F else 0.29                  # demi-largeur d'épaules
P = {  # nom: (position, rayons x/y du « Skin »)
 'bassin': ((0, 0, 1.00), (0.17 if F else 0.16, 0.13)),
 'ventre': ((0, 0, 1.17), (0.17 if F else 0.19, 0.14 if F else 0.15)),
 'poitrine': ((0, 0, 1.36), (0.23 if F else 0.29, 0.17 if F else 0.21)),
 'cou': ((0, 0, 1.57), (0.08 if F else 0.1, 0.08 if F else 0.095)),
 'cou2': ((0, 0, 1.66), (0.07, 0.07)),
}
for s, c in ((1, 'G'), (-1, 'D')):
    sh = Vector((s * ep, 0, 1.50)); dv = Vector((s * math.sin(math.radians(40)), 0, -math.cos(math.radians(40))))
    el = sh + dv * 0.36; wr = el + dv * 0.33
    P['epaule' + c] = (tuple(sh), (0.11 if F else 0.14, 0.11 if F else 0.14))
    P['biceps' + c] = (tuple(sh + dv * 0.16), (0.085 if F else 0.12, 0.085 if F else 0.11))
    P['coude' + c] = (tuple(el), (0.065 if F else 0.08, 0.065 if F else 0.08))
    P['avbras' + c] = (tuple(el + dv * 0.12), (0.072 if F else 0.1, 0.068 if F else 0.09))
    P['poignet' + c] = (tuple(wr), (0.052 if F else 0.065, 0.048 if F else 0.06))
    hx = s * (0.12 if F else 0.12)
    P['hanche' + c] = ((hx, 0, 0.93), (0.12, 0.12))
    P['cuisse' + c] = ((hx, 0, 0.72), (0.115 if F else 0.13, 0.115 if F else 0.13))
    P['genou' + c] = ((hx, 0, 0.50), (0.075, 0.075))
    P['mollet' + c] = ((hx, 0.015, 0.33), (0.085 if F else 0.1, 0.085 if F else 0.1))
    P['cheville' + c] = ((hx, 0, 0.10), (0.055, 0.055))
noms = list(P)
aretes = [('bassin', 'ventre'), ('ventre', 'poitrine'), ('poitrine', 'cou'), ('cou', 'cou2')]
for c in 'GD':
    aretes += [('poitrine', 'epaule' + c), ('epaule' + c, 'biceps' + c), ('biceps' + c, 'coude' + c), ('coude' + c, 'avbras' + c), ('avbras' + c, 'poignet' + c),
               ('bassin', 'hanche' + c), ('hanche' + c, 'cuisse' + c), ('cuisse' + c, 'genou' + c), ('genou' + c, 'mollet' + c), ('mollet' + c, 'cheville' + c)]
me = bpy.data.meshes.new('corps'); me.from_pydata([P[n][0] for n in noms], [(noms.index(a), noms.index(b)) for a, b in aretes], [])
corps = bpy.data.objects.new('corps', me); scene.collection.objects.link(corps)
bpy.context.view_layer.objects.active = corps; corps.select_set(True)
skin = corps.modifiers.new('skin', 'SKIN'); skin.use_smooth_shade = True
for i, n in enumerate(noms):
    corps.data.skin_vertices[0].data[i].radius = P[n][1]
corps.data.skin_vertices[0].data[0].use_root = True
sub = corps.modifiers.new('sub', 'SUBSURF'); sub.levels = 2
bpy.ops.object.modifier_apply(modifier='skin'); bpy.ops.object.modifier_apply(modifier='sub')
bpy.ops.object.shade_smooth()

# Couleurs du corps : tee-shirt rouge à bande jaune, short bleu marine liseré rouge, poignets noirs, chaussettes noires
for m in ('peau', 'rouge', 'jaune', 'marine', 'noir'): corps.data.materials.append(M[m])
idx = {m: i for i, m in enumerate(('peau', 'rouge', 'jaune', 'marine', 'noir'))}
def proj(p, a, b):
    a, b = Vector(a), Vector(b); t = max(0, min(1, (p - a).dot(b - a) / (b - a).length_squared)); return t, (a + (b - a) * t - p).length
for poly in corps.data.polygons:
    p = poly.center; m = 'peau'
    bras = None
    for c in 'GD':
        t, d = proj(p, P['epaule' + c][0], P['poignet' + c][0])
        if d < 0.16 and abs(p.x) > ep * 0.75: bras = t
    if bras is not None:
        m = 'rouge' if bras < 0.28 else ('noir' if bras > 0.86 else 'peau')
    elif p.z > 1.05 and p.z < 1.56:
        m = 'jaune' if 1.33 < p.z < 1.41 else 'rouge'
    elif p.z >= 1.56: m = 'peau'
    elif p.z > 0.66: m = 'marine'
    elif p.z < 0.16: m = 'noir'
    poly.material_index = idx[m]

# ---------- Tête, visage, casque ----------
def objet(o, nom, matn, parent_os):
    o.name = nom; o.data.materials.clear(); o.data.materials.append(M[matn]); o['os'] = parent_os
    bpy.ops.object.shade_smooth(); return o
def sphere(nom, matn, loc, r, ech=(1, 1, 1), os_='tete', seg=28):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=seg, ring_count=seg // 2, radius=r, location=loc); o = bpy.context.object; o.scale = ech
    bpy.ops.object.transform_apply(scale=True); return objet(o, nom, matn, os_)
H = Vector((0, 0, 1.83))
sphere('crane', 'peau', H, 0.17, (1, 1.02, 1.05))
sphere('machoire', 'peau', H + Vector((0, -0.04, -0.08)), 0.13, (1.0 if not F else 0.9, 0.95, 0.8))
sphere('nez', 'peau', H + Vector((0, -0.172, -0.01)), 0.035)
for s in (1, -1):
    sphere('oeil', 'blanc', H + Vector((s * 0.058, -0.142, 0.025)), 0.032, (1, 0.6, 1.15))
    sphere('pupille', 'noir', H + Vector((s * 0.058, -0.162, 0.022)), 0.016, (1, 0.5, 1.2))
    bpy.ops.mesh.primitive_cube_add(size=1, location=H + Vector((s * 0.06, -0.15, 0.075))); o = bpy.context.object
    o.scale = (0.075, 0.03, 0.012 if F else 0.022); o.rotation_euler = (0, s * (0.22 if F else 0.38), 0); bpy.ops.object.transform_apply(scale=True, rotation=True)
    objet(o, 'sourcil', 'brun', 'tete')
    sphere('oreille', 'peau', H + Vector((s * 0.168, 0, 0)), 0.04, (0.5, 0.9, 1.2))
    if F: sphere('joue', 'rose', H + Vector((s * 0.085, -0.135, -0.035)), 0.03, (1, 0.4, 0.6))
# bouche : dents serrées (sourire déterminé)
if not F:
    bpy.ops.mesh.primitive_cube_add(size=1, location=H + Vector((0, -0.158, -0.085))); o = bpy.context.object; o.scale = (0.1, 0.02, 0.03); bpy.ops.object.transform_apply(scale=True)
    objet(o, 'dents', 'blanc', 'tete')
def tube(nom, matn, points, rayon, os_='tete'):
    cu = bpy.data.curves.new(nom, 'CURVE'); cu.dimensions = '3D'; cu.bevel_depth = rayon; cu.bevel_resolution = 4
    sp = cu.splines.new('NURBS'); sp.points.add(len(points) - 1)
    for i, p in enumerate(points): sp.points[i].co = (*p, 1)
    sp.use_endpoint_u = True; sp.order_u = 3
    o = bpy.data.objects.new(nom, cu); scene.collection.objects.link(o); bpy.context.view_layer.objects.active = o
    for x in bpy.context.selected_objects: x.select_set(False)
    o.select_set(True); bpy.ops.object.convert(target='MESH'); o = bpy.context.object
    return objet(o, nom, matn, os_)
if F:
    tube('sourire', 'levres', [H + Vector(v) for v in ((-0.055, -0.152, -0.07), (-0.02, -0.165, -0.088), (0.02, -0.165, -0.088), (0.055, -0.152, -0.07))], 0.012)
if not F:
    # moustache en guidon, pointes recourbées vers le haut
    for s in (1, -1):
        pts = [H + Vector(v) for v in ((0, -0.18, -0.045), (s * 0.05, -0.176, -0.058), (s * 0.095, -0.16, -0.062), (s * 0.128, -0.14, -0.04), (s * 0.135, -0.13, -0.005))]
        tube('moustache', 'brun', pts, 0.028)
        sphere('moustache_bout', 'brun', H + Vector((s * 0.135, -0.13, -0.005)), 0.028)
else:
    # queue de cheval avec élastique rouge
    sphere('chignon', 'cheveux', H + Vector((0, 0.19, -0.01)), 0.065)
    tube('queue', 'cheveux', [H + Vector(v) for v in ((0, 0.2, -0.01), (0, 0.29, -0.09), (0, 0.31, -0.22), (0, 0.27, -0.34))], 0.055)
    bpy.ops.mesh.primitive_torus_add(major_radius=0.05, minor_radius=0.015, location=H + Vector((0, 0.235, -0.03)), rotation=(math.radians(60), 0, 0))
    objet(bpy.context.object, 'elastique', 'rouge', 'tete')
    for s in (1, -1): sphere('meche', 'cheveux', H + Vector((s * 0.15, -0.06, 0.0)), 0.04, (0.6, 1, 1.6))
# casque : bombe argent, crête rouge, bord, visière dorée relevée, couvre-nuque noir
C = H + Vector((0, 0.005, 0.045))
bpy.ops.mesh.primitive_uv_sphere_add(segments=36, ring_count=18, radius=0.205, location=C); o = bpy.context.object
bm = bmesh.new(); bm.from_mesh(o.data); bmesh.ops.delete(bm, geom=[v for v in bm.verts if v.co.z < -0.002], context='VERTS'); bm.to_mesh(o.data); bm.free()
o.scale = (1, 1.1, 0.98); bpy.ops.object.transform_apply(scale=True); objet(o, 'casque', 'argent', 'tete')
tube('crete', 'rouge', [C + Vector((0, -0.226 * math.cos(a), 0.2 * math.sin(a))) for a in [math.radians(x) for x in range(10, 175, 20)]], 0.028)
bpy.ops.mesh.primitive_cylinder_add(vertices=40, radius=0.225, depth=0.02, location=C + Vector((0, 0, 0.005))); o = bpy.context.object; o.scale = (1, 1.1, 1); bpy.ops.object.transform_apply(scale=True)
objet(o, 'bord', 'argent', 'tete')
def arc(nom, matn, r, h, z, a0, a1, epai=0.012):
    bpy.ops.mesh.primitive_cylinder_add(vertices=48, radius=r, depth=h, location=C + Vector((0, 0, z)), end_fill_type='NOTHING'); o = bpy.context.object
    bm = bmesh.new(); bm.from_mesh(o.data)
    garde = lambda v: a0 <= math.degrees(math.atan2(v.co.x, -v.co.y)) <= a1
    bmesh.ops.delete(bm, geom=[v for v in bm.verts if not garde(v)], context='VERTS'); bm.to_mesh(o.data); bm.free()
    so = o.modifiers.new('ep', 'SOLIDIFY'); so.thickness = epai; bpy.context.view_layer.objects.active = o; bpy.ops.object.modifier_apply(modifier='ep')
    o.scale = (1, 1.1, 1); bpy.ops.object.transform_apply(scale=True); return objet(o, nom, matn, 'tete')
v = arc('visiere', 'or', 0.204, 0.055, 0.105, -55, 55, 0.014)
arc('nuque', 'noir', 0.215, 0.17, -0.07, 100, 260, 0.012)
bpy.ops.object.select_all(action='DESELECT')

# ---------- Mains (poings) et chaussures ----------
for s, c in ((1, 'G'), (-1, 'D')):
    w = Vector(P['poignet' + c][0]); el = Vector(P['coude' + c][0]); d = (w - el).normalized()
    sphere('main', 'peau', w + d * 0.07, 0.075 if not F else 0.065, (1, 0.9, 1.1), 'main' + c, 20)
    a = Vector(P['cheville' + c][0])
    for nom, matn, dz, sc in (('semelle', 'blanc', -0.07, (0.13, 0.29, 0.03)), ('chaussure', 'noir', -0.02, (0.13, 0.27, 0.09)), ('chaussure_bande', 'rouge', -0.01, (0.135, 0.18, 0.025))):
        bpy.ops.mesh.primitive_cube_add(size=1, location=a + Vector((0, -0.07, dz))); o = bpy.context.object; o.scale = sc
        bv = o.modifiers.new('bv', 'BEVEL'); bv.width = 0.02; bv.segments = 3; bpy.context.view_layer.objects.active = o; bpy.ops.object.modifier_apply(modifier='bv')
        bpy.ops.object.transform_apply(scale=True); objet(o, nom, matn, 'pied' + c)
bpy.ops.object.select_all(action='DESELECT')

# ---------- Armature (os nommés) ----------
arm = bpy.data.armatures.new('squelette'); rig = bpy.data.objects.new('squelette', arm); scene.collection.objects.link(rig)
bpy.context.view_layer.objects.active = rig; bpy.ops.object.mode_set(mode='EDIT')
eb = arm.edit_bones
def os_(nom, tete, queue, parent=None, connect=False):
    b = eb.new(nom); b.head = tete; b.tail = queue
    if parent: b.parent = eb[parent]; b.use_connect = connect
    return b
os_('bassin', (0, 0, 0.93), (0, 0, 1.08))
os_('dos', (0, 0, 1.08), (0, 0, 1.40), 'bassin', True)
os_('cou', (0, 0, 1.40), (0, 0, 1.66), 'dos', True)
os_('tete', (0, 0, 1.66), (0, 0, 2.0), 'cou', True)
for c in 'GD':
    os_('clavicule' + c, (0, 0, 1.45), P['epaule' + c][0], 'dos')
    os_('bras' + c, P['epaule' + c][0], P['coude' + c][0], 'clavicule' + c, True)
    os_('avbras' + c, P['coude' + c][0], P['poignet' + c][0], 'bras' + c, True)
    w = Vector(P['poignet' + c][0]); d = (w - Vector(P['coude' + c][0])).normalized()
    os_('main' + c, w, tuple(w + d * 0.12), 'avbras' + c, True)
    os_('hanche' + c, (0, 0, 0.93), P['hanche' + c][0], 'bassin')
    os_('cuisse' + c, P['hanche' + c][0], P['genou' + c][0], 'hanche' + c, True)
    os_('tibia' + c, P['genou' + c][0], P['cheville' + c][0], 'cuisse' + c, True)
    a = P['cheville' + c][0]; os_('pied' + c, a, (a[0], -0.2, a[2] - 0.05), 'tibia' + c, True)
bpy.ops.object.mode_set(mode='OBJECT')
# le corps suit le squelette (poids automatiques), les accessoires suivent un os entier
for o in scene.objects: o.select_set(False)
corps.select_set(True); rig.select_set(True); bpy.context.view_layer.objects.active = rig
bpy.ops.object.parent_set(type='ARMATURE_AUTO')
for o in list(scene.objects):
    if o.type == 'MESH' and 'os' in o:
        vg = o.vertex_groups.new(name=o['os']); vg.add(range(len(o.data.vertices)), 1.0, 'REPLACE')
        mo = o.modifiers.new('arm', 'ARMATURE'); mo.object = rig; o.parent = rig
# on fusionne les accessoires par matériau pour un fichier léger
bpy.ops.object.select_all(action='DESELECT')
acc = [o for o in scene.objects if o.type == 'MESH' and 'os' in o]
for o in acc: o.select_set(True)
bpy.context.view_layer.objects.active = acc[0]; bpy.ops.object.join(); bpy.context.object.name = 'accessoires'

bpy.ops.export_scene.gltf(filepath=SORTIE, export_format='GLB', export_skins=True, export_animations=False, export_yup=True, export_apply=False)

# ---------- Aperçu ----------
cam = bpy.data.objects.new('cam', bpy.data.cameras.new('cam')); scene.collection.objects.link(cam); scene.camera = cam
cam.location = (1.6, -3.4, 1.55); cam.rotation_euler = (math.radians(87), 0, math.radians(25)); cam.data.lens = 50
scene.render.engine = 'BLENDER_WORKBENCH'; scene.display.shading.light = 'STUDIO'; scene.display.shading.color_type = 'MATERIAL'
scene.display.shading.show_cavity = True; scene.display.shading.show_object_outline = True
scene.render.resolution_x = 700; scene.render.resolution_y = 900; scene.render.filepath = APERCU
scene.world = bpy.data.worlds.new('w'); scene.display.shading.background_type = 'VIEWPORT'
bpy.ops.render.render(write_still=True)
print('OK', SORTIE)
