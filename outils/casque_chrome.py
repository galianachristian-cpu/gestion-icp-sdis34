# Repeint le casque du Sergent-Chef en chrome dans la texture du modèle IA (pose en T).
# Usage : python casque_chrome.py modele.glb texture_sortie.png [apercu_masque.png]
import bpy, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=sys.argv[1])
m = [o for o in bpy.context.scene.objects if o.type == 'MESH'][0]
bpy.context.view_layer.objects.active = m; m.select_set(True)
bpy.ops.object.parent_clear(type='CLEAR_KEEP_TRANSFORM'); bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
img = [i for i in bpy.data.images if i.size[0] > 0][0]
Wt, Ht = img.size
px = np.array(img.pixels[:], dtype=np.float32).reshape(Ht, Wt, 4)[::-1, :, :3]   # haut de l'image en premier
V = np.array([v.co[:] for v in m.data.vertices]); zmin, zmax = V[:, 2].min(), V[:, 2].max(); H = zmax - zmin
tete = V[V[:, 2] > zmin + 0.80 * H]; cx, cy = np.median(tete[:, 0]), np.median(tete[:, 1])
uv = m.data.uv_layers.active.data
masque = Image.new('L', (Wt, Ht), 0); d = ImageDraw.Draw(masque)
for p in m.data.polygons:
    vs = V[list(p.vertices)]; z = (vs[:, 2].mean() - zmin) / H; r = np.hypot(vs[:, 0].mean() - cx, vs[:, 1].mean() - cy) / H
    # casque : le dessus de la tête, et le bord qui dépasse un peu plus bas
    # le visage (front, sourcils, nez) regarde vers l'avant (-y) et reste près de l'axe de la tête : on n'y touche pas
    visage = p.normal.y < -0.25 and z < 0.928 and r < 0.088
    if not visage and (z > 0.905 or (z > 0.865 and r > 0.075)):
        pts = [(uv[li].uv[0] * Wt, (1 - uv[li].uv[1]) * Ht) for li in p.loop_indices]
        d.polygon(pts, fill=255)
masque = masque.filter(ImageFilter.MaxFilter(5)).filter(ImageFilter.GaussianBlur(1.5))
M = np.asarray(masque, dtype=np.float32) / 255.0
# chrome : on garde la lumière (les reflets) mais on retire la couleur orange ; le noir reste noir
lum = px @ np.array([0.30, 0.55, 0.15], dtype=np.float32)
r, g, b = px[..., 0], px[..., 1], px[..., 2]
orange = np.clip((r - b) * 3.0, 0, 1) * (lum > 0.08)            # pixels chauds (orange, brun, doré)
l2 = np.clip((lum - 0.08) / 0.75, 0, 1); l2 = l2 ** 0.8           # plus de contraste, comme du métal poli
chrome = np.stack([0.20 + 0.78 * l2, 0.22 + 0.78 * l2, 0.26 + 0.76 * l2], -1)
a = (M * orange)[..., None]
out = px * (1 - a) + chrome * a
Image.fromarray((np.clip(out, 0, 1) * 255).astype(np.uint8)).save(sys.argv[2])
if len(sys.argv) > 3: Image.fromarray((M * orange * 255).astype(np.uint8)).save(sys.argv[3])
print('OK', Wt, Ht, 'pixels repeints', int((M * orange > 0.5).sum()))
