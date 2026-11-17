// Rend une animation de l'atelier (outils/atelier-mixamo.html) en images PNG, avec Playwright.
// Usage : node outils/rendu_atelier.js fichier.glb nbImages "options" dossierSortie
// (le serveur local doit servir le dépôt sur http://127.0.0.1:8123 ; fichier.glb dans outils/tmp-anim/)
const {chromium}=require('playwright');
(async()=>{const b=await chromium.launch({args:['--use-angle=swiftshader','--enable-unsafe-swiftshader','--ignore-gpu-blocklist']});
 const p=await b.newPage({viewport:{width:800,height:500}});const errs=[];p.on('pageerror',e=>errs.push(e.message));
 const [f,n,ext,dir]=process.argv.slice(2);require('fs').mkdirSync(dir,{recursive:true});
 await p.goto('http://127.0.0.1:8123/outils/atelier-mixamo.html?fige&'+ext+'&f=tmp-anim/'+f);await p.waitForFunction(()=>window.pret,{timeout:90000});
 console.log(JSON.stringify(await p.evaluate(()=>[window.duree,window.boite])));
 for(let i=0;i<+n;i++){await p.evaluate(t=>window.poserT(t),i/(+n));await p.screenshot({path:dir+'/f'+String(i).padStart(3,'0')+'.png'})}
 if(errs.length)console.log(JSON.stringify(errs));await b.close();})();
