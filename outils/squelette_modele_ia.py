# Pose un squelette (mêmes noms d'os que sergent3d_blender.py) sur un modèle 3D généré par IA en pose en T.
# Exemple : python outils/squelette_modele_ia.py modele_hunyuan.glb img/rame/sergent-h.glb (modèle IA en pose en T, texturé)
# Usage : python rig_ia.py entree.glb sortie.glb
import bpy, bmesh, sys, math
import numpy as np
from mathutils import Vector

ENTREE, SORTIE = sys.argv[1], sys.argv[2]
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=ENTREE)
mesh = [o for o in bpy.context.scene.objects if o.type == 'MESH'][0]
# on applique toutes les transformations et on pose les pieds en z = 0, centré
for o in bpy.context.scene.objects: o.select_set(False)
mesh.select_set(True); bpy.context.view_layer.objects.active = mesh
bpy.ops.object.parent_clear(type='CLEAR_KEEP_TRANSFORM'); bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
V = np.array([v.co[:] for v in mesh.data.vertices])
zmin, zmax = V[:, 2].min(), V[:, 2].max()
dx = (V[:, 0].min() + V[:, 0].max()) / 2; dy = np.median(V[:, 1])
for v in mesh.data.vertices: v.co -= Vector((dx, dy, zmin))
V = np.array([v.co[:] for v in mesh.data.vertices]); H = V[:, 2].max(); X = V[:, 0].max()
print('hauteur', round(H, 3), 'envergure', round(2 * X, 3))

# ---------- mains de rameur : poings fermés, pouce rabattu, paumes vers le bas ----------
# Sur le modèle en T, la main est à plat dans le plan x-z, paume vers l'avant (-y), doigts vers l'extérieur.
def bras_z():
    b = V[np.abs(V[:, 0]) > 0.55 * X]; return float(np.median(b[:, 2])), float(np.median(b[:, 1]))
zb0, yb0 = bras_z()
ax = np.abs(V[:, 0]); sg = np.sign(V[:, 0])
main = ax > 0.74 * X
# repère de la main : jointure des doigts (début de la partie fine en y) et pointe
x0 = 0.875 * X; Lg = X - x0; y0 = float(np.median(V[main & (ax > x0), 1]))
pouce = main & (ax > 0.78 * X) & (ax < x0) & (V[:, 2] > zb0 + 0.04 * H)
doigts = main & (ax >= x0)
# 1) les doigts s'enroulent vers la paume (vers -y) : pliage en arc, ~190°
theta = 3.3; r = Lg / theta
d = ax[doigts] - x0; p = V[doigts, 1] - y0; R = r + p; phi = np.minimum(d / r, theta)
V[doigts, 0] = sg[doigts] * (x0 + R * np.sin(phi)); V[doigts, 1] = (y0 - r) + R * np.cos(phi)
# 2) le pouce se rabat devant les doigts (rotation autour de l'axe du bras)
cz = zb0 + 0.035 * H; a = np.radians(80)
dy = V[pouce, 1] - y0; dz = V[pouce, 2] - cz
V[pouce, 1] = y0 + dy * np.cos(a) - dz * np.sin(a); V[pouce, 2] = cz + dy * np.sin(a) + dz * np.cos(a)
# 3) pronation : l'avant-bras tourne pour que la paume regarde vers le bas (progressif depuis le coude)
coude = 0.5 * X; t = np.clip((ax - coude) / (0.8 * X - coude), 0, 1); t = t * t * (3 - 2 * t)
a = np.radians(90) * t; dy = V[:, 1] - yb0; dz = V[:, 2] - zb0
ny = yb0 + dy * np.cos(a) - dz * np.sin(a); nz = zb0 + dy * np.sin(a) + dz * np.cos(a)
V[:, 1] = np.where(ax > coude, ny, V[:, 1]); V[:, 2] = np.where(ax > coude, nz, V[:, 2])
for i, v in enumerate(mesh.data.vertices): v.co = Vector(V[i])
mesh.data.update()
print('mains : doigts', int(doigts.sum()), 'pouce', int(pouce.sum()))

# ---------- repères anatomiques mesurés sur le maillage ----------
bras = V[np.abs(V[:, 0]) > 0.55 * X]
zb = float(np.median(bras[:, 2])); yb = float(np.median(bras[:, 1]))
# torse : largeur juste sous les bras
tranche = V[(V[:, 2] > zb - 0.10 * H) & (V[:, 2] < zb - 0.06 * H)]
tor = tranche[np.abs(tranche[:, 0]) < 0.45 * X]
ep_x = float(np.percentile(np.abs(tor[:, 0]), 97)) * 0.92
# entrejambe : premier niveau (en montant) où la matière passe au centre
zc = None
for z in np.linspace(0.25 * H, 0.65 * H, 80):
    s = V[np.abs(V[:, 2] - z) < 0.006 * H]
    if len(s) and (np.abs(s[:, 0]) < 0.02 * X).any(): zc = z; break
zc = zc or 0.45 * H
hanche_z = zc + 0.05 * H
cuisses = V[(V[:, 2] > zc - 0.12 * H) & (V[:, 2] < zc - 0.06 * H)]
jx = float(np.median(np.abs(cuisses[:, 0])))
genou_z, cheville_z = 0.27 * H, 0.065 * H
cou_z = zb + 0.06 * H; tete_z = zb + 0.11 * H
poignet_x = 0.80 * X; coude_x = (ep_x + poignet_x) / 2
print('bras z', round(zb, 3), 'épaule x', round(ep_x, 3), 'entrejambe', round(zc, 3), 'jambes x', round(jx, 3))

# ---------- armature ----------
arm = bpy.data.armatures.new('squelette'); rig = bpy.data.objects.new('squelette', arm); bpy.context.scene.collection.objects.link(rig)
bpy.context.view_layer.objects.active = rig; bpy.ops.object.mode_set(mode='EDIT'); eb = arm.edit_bones
def os_(n, t, q, p=None, c=False):
    b = eb.new(n); b.head = t; b.tail = q
    if p: b.parent = eb[p]; b.use_connect = c
os_('bassin', (0, yb, hanche_z), (0, yb, hanche_z + 0.08 * H))
os_('dos', (0, yb, hanche_z + 0.08 * H), (0, yb, zb - 0.02 * H), 'bassin', True)
os_('cou', (0, yb, zb - 0.02 * H), (0, yb, tete_z), 'dos', True)
os_('tete', (0, yb, tete_z), (0, yb, H), 'cou', True)
for s, c in ((1, 'G'), (-1, 'D')):
    os_('clavicule' + c, (0, yb, zb - 0.01 * H), (s * ep_x, yb, zb), 'dos')
    os_('bras' + c, (s * ep_x, yb, zb), (s * coude_x, yb, zb), 'clavicule' + c, True)
    os_('avbras' + c, (s * coude_x, yb, zb), (s * poignet_x, yb, zb), 'bras' + c, True)
    os_('main' + c, (s * poignet_x, yb, zb), (s * X, yb, zb), 'avbras' + c, True)
    os_('hanche' + c, (0, yb, hanche_z), (s * jx, yb, hanche_z), 'bassin')
    os_('cuisse' + c, (s * jx, yb, hanche_z), (s * jx, yb, genou_z), 'hanche' + c, True)
    os_('tibia' + c, (s * jx, yb, genou_z), (s * jx, yb, cheville_z), 'cuisse' + c, True)
    os_('pied' + c, (s * jx, yb, cheville_z), (s * jx, yb - 0.09 * H, 0.01), 'tibia' + c, True)
segs = {b.name: (np.array(b.head[:]), np.array(b.tail[:])) for b in eb}
bpy.ops.object.mode_set(mode='OBJECT')

# ---------- poids : distance aux os, avec règles anatomiques (robuste sur un maillage d'IA) ----------
def dist_seg(P, a, b):
    ab = b - a; t = np.clip(((P - a) @ ab) / (ab @ ab), 0, 1); return np.linalg.norm(P - (a + t[:, None] * ab), axis=1)
noms = [n for n in segs if not n.startswith(('clavicule', 'hanche'))]
D = np.stack([dist_seg(V, *segs[n]) for n in noms], 1)
cote = np.where(V[:, 0] >= 0, 'G', 'D')
# un bras ne prend que les points du bon côté et au-delà de l'épaule ; une jambe ceux sous la hanche, du bon côté
for j, n in enumerate(noms):
    if n[:-1] in ('bras', 'avbras', 'main'):
        ok = (cote == n[-1]) & (np.abs(V[:, 0]) > ep_x * 0.78); D[~ok, j] = 9
    if n[:-1] in ('cuisse', 'tibia', 'pied'):
        ok = (cote == n[-1]) & (V[:, 2] < hanche_z + 0.02 * H); D[~ok, j] = 9
    if n in ('dos', 'cou', 'tete', 'bassin'):
        D[np.abs(V[:, 0]) > ep_x * 1.15, j] = 9
# cheveux longs (queue de cheval) : derrière la tête, au-dessus des épaules -> ils suivent la tête, jamais les bras
cheveux = (np.abs(V[:, 0]) < ep_x * 1.25) & (V[:, 1] > yb + 0.05 * H) & (V[:, 2] > zb - 0.03 * H)
for j, n in enumerate(noms):
    if n not in ('tete', 'cou'): D[cheveux, j] = 9
print('cheveux suivant la tête :', int(cheveux.sum()))
W = 1.0 / np.maximum(D, 1e-3) ** 6
W[D > 8] = 0
top = np.argsort(-W, 1)[:, :3]
for j, n in enumerate(noms): mesh.vertex_groups.new(name=n)
for i in range(len(V)):
    w = W[i, top[i]]; s = w.sum()
    if s <= 0: continue
    for k, j in enumerate(top[i]):
        if w[k] / s > 0.02: mesh.vertex_groups[noms[j]].add([i], float(w[k] / s), 'REPLACE')
mod = mesh.modifiers.new('arm', 'ARMATURE'); mod.object = rig; mesh.parent = rig
bpy.ops.export_scene.gltf(filepath=SORTIE, export_format='GLB', export_skins=True, export_animations=False, export_yup=True,
                          export_image_format='JPEG', export_image_quality=85)
print('OK', SORTIE)
