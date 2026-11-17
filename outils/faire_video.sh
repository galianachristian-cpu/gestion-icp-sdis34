#!/bin/bash
# Fabrique la vidéo (MP4), le GIF et le WebM d'un exercice à partir d'un GLB animé de l'atelier.
# Usage : outils/faire_video.sh exercice.glb nbImages dossierTravail nomSortie
# (le GLB doit être dans outils/tmp-anim/ ; le serveur local doit tourner sur le port 8123)
set -e
GLB=$1; N=$2; D=$3; NOM=$4
cd "$(dirname "$0")/.."
node outils/rendu_atelier.js "$GLB" "$N" "" "$D/img" >/dev/null
CROP=$(python3 - "$D/img" "$N" <<'EOF'
import sys
from PIL import Image, ImageChops
d,n=sys.argv[1],int(sys.argv[2]);x0=y0=9999;x1=y1=0
for i in range(n):
    im=Image.open(f'{d}/f{i:03d}.png').convert('RGB');bb=ImageChops.difference(im,Image.new('RGB',im.size,'white')).point(lambda v:255 if v>12 else 0).getbbox()
    if bb:x0=min(x0,bb[0]);y0=min(y0,bb[1]);x1=max(x1,bb[2]);y1=max(y1,bb[3])
W,H=im.size;m=24;x0=max(0,x0-m);y0=max(0,y0-m);x1=min(W,x1+m);y1=min(H,y1+m)
print(f'{(x1-x0)//2*2}:{(y1-y0)//2*2}:{x0}:{y0}')
EOF
)
V="crop=$CROP,scale=-2:420"
ffmpeg -v error -y -stream_loop 2 -framerate 26 -i "$D/img/f%03d.png" -vf "$V" -c:v libx264 -pix_fmt yuv420p "$D/$NOM.mp4"
ffmpeg -v error -y -framerate 26 -i "$D/img/f%03d.png" -vf "$V,split[a][b];[a]palettegen=max_colors=96[p];[b][p]paletteuse" -loop 0 "$D/$NOM.gif"
ffmpeg -v error -y -framerate 26 -i "$D/img/f%03d.png" -vf "$V" -c:v libvpx-vp9 -b:v 0 -crf 34 "$D/$NOM.webm"
echo "OK $CROP"
