#!/usr/bin/env node
/* Carte du code : sections, sous-sections et fonctions de index.html et rame.html, pour s'orienter sans relire tout le fichier.
   node outils/carte.cjs          → régénère docs/CARTE.md
   node outils/carte.cjs --check  → échoue si docs/CARTE.md n'est plus à jour (vérifié par GitHub à chaque envoi) */
const fs = require('fs'), path = require('path');
const ROOT = path.join(__dirname, '..'), OUT = path.join(ROOT, 'docs', 'CARTE.md'), FILES = ['index.html', 'rame.html'];
const SEC = /^\s*(?:\/\/|\/\*)\s*={3,}\s*(.+?)\s*={3,}\s*(?:\*\/)?\s*$/;          // ===== TITRE =====
const SUB = /^\s*(?:\/\/|\/\*)\s*-{3,}\s*(.+?)\s*-{3,}\s*(?:\*\/)?\s*$/;          // --- titre ---
const FN = /^\s{0,2}(?:async\s+)?function\s+([\w$]+)\s*\(|^\s{0,2}(?:const|let|var)\s+([\w$]+)\s*=\s*(?:async\s+)?(?:function\b|\([^)]*\)\s*=>|[\w$]+\s*=>)/;
function carteDe(file){
  const L = fs.readFileSync(path.join(ROOT, file), 'utf8').split('\n'), secs = [];
  let cur = { titre: 'Début du fichier (HTML, CSS, premiers scripts)', ligne: 1, subs: [], fns: [] }; secs.push(cur);
  L.forEach((l, i) => {
    let m = SEC.exec(l); if (m){ cur = { titre: m[1], ligne: i + 1, subs: [], fns: [] }; secs.push(cur); return; }
    m = SUB.exec(l); if (m){ cur.subs.push(m[1].slice(0, 110)); return; }
    m = FN.exec(l); if (m) cur.fns.push(m[1] || m[2]);
  });
  return secs.filter(s => s.subs.length || s.fns.length || s.ligne > 1);
}
function build(){
  let md = '# Carte du code\n\n_Générée par `node outils/carte.cjs`, ne pas modifier à la main. Numéros de ligne : début de chaque section._\n';
  FILES.forEach(f => { const S = carteDe(f), n = S.reduce((a, s) => a + s.fns.length, 0);
    md += `\n# ${f} : ${S.length} sections, ${n} fonctions\n\n` + S.map(s => `## ${s.titre} · ligne ${s.ligne}\n` + s.subs.map(x => `- ${x}\n`).join('') + (s.fns.length ? `\nFonctions : ${s.fns.map(x => '`' + x + '`').join(', ')}\n` : '')).join('\n'); });
  return md;
}
if (require.main === module){
  const md = build();
  if (process.argv.includes('--check')){
    if ((fs.existsSync(OUT) ? fs.readFileSync(OUT, 'utf8') : '') !== md){ console.error('docs/CARTE.md n’est plus à jour : lance « node outils/carte.cjs »'); process.exit(1); }
    console.log('Carte du code à jour');
  } else { fs.writeFileSync(OUT, md); console.log('docs/CARTE.md écrit'); }
}
module.exports = { build, OUT };
