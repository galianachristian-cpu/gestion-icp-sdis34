// ===== SCÈNE DE NOËL : « Aidons le Père Noël à skier » =====
// Un paysage d'hiver animé (aurore boréale, lune, étoiles, montagnes, sapins, neige qui tombe) où le skieur avance
// le long de la piste selon le total du défi. Des gags passent de temps en temps (engins du centre déguisés, traîneau…).
// Canvas 2D (léger pour la télé de la salle). Usage : const s=SceneNoel(canvas,IMG,{dire:f}); s.avancer(pct); s.gag('fpt');
function SceneNoel(cv,IMG,opt){
  opt=opt||{};const g=cv.getContext('2d');let W=0,H=0,dpr=1,t0=performance.now(),pct=0,pctAff=0,vivant=true;
  const R=(()=>{let s=1234567;return()=>{s=(s*16807)%2147483647;return(s-1)/2147483646}})();   // hasard fixe : le décor ne bouge pas d'une fois à l'autre
  const etoiles=[...Array(140)].map(()=>({x:R(),y:R()*0.55,r:0.4+R()*1.3,p:R()*6}));
  const flocons=[...Array(170)].map(()=>({x:R(),y:R(),z:0.3+R()*0.7,p:R()*6}));
  // montagnes : deux chaînes (lointaine bleutée, proche plus claire), sommets enneigés
  const chaine=(n,base,amp)=>{const L=[];for(let i=0;i<=n;i++){const x=i/n;L.push([x,base-amp*(0.35+0.65*Math.abs(Math.sin(i*1.7+R()*2)))*(0.6+R()*0.5)])}return L};
  const loin=chaine(9,0.58,0.30),proche=chaine(7,0.66,0.22);
  const sapins=[...Array(26)].map((_,i)=>({x:R()*1.05-0.02,y:0.64+R()*0.06,s:0.55+R()*0.6})).sort((a,b)=>a.y-b.y);
  // la piste : une courbe du coin gauche jusqu'au village à droite
  const piste=u=>{const x=0.06+u*0.80,y=0.86-0.13*u+0.035*Math.sin(u*Math.PI*2.2);return[x,y]};
  const DECORS=[[0.25,'rennes',0.17],[0.5,'montagnes',0.20],[0.75,'sapins',0.16]];
  let filante=null;
  let gag=null,gagSuivant=opt.premierGag||14,bulle=null,feux=[],eclats=[];
  function taille(){const r=cv.getBoundingClientRect();dpr=Math.min(2,window.devicePixelRatio||1);W=Math.max(10,r.width);H=Math.max(10,r.height);cv.width=W*dpr;cv.height=H*dpr;g.setTransform(dpr,0,0,dpr,0,0)}
  const img=(n,x,y,h,o={})=>{const I=IMG[n];if(!I||!I.complete||!I.naturalWidth)return 0;const w=h*I.naturalWidth/I.naturalHeight;g.save();g.translate(x,y);if(o.rot)g.rotate(o.rot);if(o.flip)g.scale(-1,1);g.globalAlpha=o.a==null?1:o.a;
    if(o.ombre){g.shadowColor=o.ombre;g.shadowBlur=o.flou||18}g.drawImage(I,-w/2,-h,w,h);g.restore();return w};
  function ciel(t){
    const gr=g.createLinearGradient(0,0,0,H*0.7);gr.addColorStop(0,'#060b1f');gr.addColorStop(0.45,'#13265a');gr.addColorStop(1,'#5b7fc0');g.fillStyle=gr;g.fillRect(0,0,W,H);
    // aurore boréale : trois voiles qui ondulent
    g.save();g.globalCompositeOperation='lighter';
    [['rgba(60,255,170,',0.10,0.0],['rgba(80,200,255,',0.16,1.7],['rgba(170,110,255,',0.07,3.1]].forEach(([c,y0,ph],k)=>{
      for(let i=0;i<46;i++){const u=i/45,x=u*W,yy=H*(y0+0.07*Math.sin(u*5+t*0.25+ph)+0.03*Math.sin(u*13-t*0.4)),hh=H*(0.16+0.06*Math.sin(u*7+t*0.3+k));
        const a=0.13*(0.5+0.5*Math.sin(u*9+t*0.5+ph));const lg=g.createLinearGradient(0,yy,0,yy+hh);lg.addColorStop(0,c+'0)');lg.addColorStop(0.35,c+a+')');lg.addColorStop(1,c+'0)');
        g.fillStyle=lg;g.fillRect(x-W/90,yy,W/45+1,hh)}});
    g.restore();
    if(!filante&&Math.random()<0.004)filante={x:0.2+R()*0.6,y:0.05+R()*0.2,t:0};
    if(filante){filante.t+=0.016;const k=filante.t/0.9,x=(filante.x+k*0.25)*W,y=(filante.y+k*0.12)*H;const lg=g.createLinearGradient(x,y,x-W*0.08,y-H*0.04);lg.addColorStop(0,'rgba(255,255,255,'+(1-k)+')');lg.addColorStop(1,'rgba(255,255,255,0)');g.strokeStyle=lg;g.lineWidth=2;g.beginPath();g.moveTo(x,y);g.lineTo(x-W*0.08,y-H*0.04);g.stroke();if(k>=1)filante=null}
    etoiles.forEach(e=>{const a=0.35+0.65*Math.abs(Math.sin(t*1.3+e.p));g.fillStyle='rgba(255,255,255,'+a+')';g.beginPath();g.arc(e.x*W,e.y*H,e.r,0,7);g.fill()});
    // la lune et son halo
    const lx=W*0.86,ly=H*0.17,lr=H*0.065;const hl=g.createRadialGradient(lx,ly,lr*0.6,lx,ly,lr*4);hl.addColorStop(0,'rgba(255,250,220,.35)');hl.addColorStop(1,'rgba(255,250,220,0)');g.fillStyle=hl;g.fillRect(lx-lr*4,ly-lr*4,lr*8,lr*8);
    g.fillStyle='#fffbe8';g.beginPath();g.arc(lx,ly,lr,0,7);g.fill();g.fillStyle='rgba(200,195,170,.35)';[[-.3,-.2,.22],[.25,.15,.16],[.05,.35,.1]].forEach(([a,b,c])=>{g.beginPath();g.arc(lx+a*lr,ly+b*lr,c*lr,0,7);g.fill()});
  }
  function montagnes(){
    const tracer=(L,c1,c2,neige)=>{g.beginPath();g.moveTo(0,H);L.forEach(([x,y],i)=>{const px=x*W,py=y*H;if(!i)g.lineTo(px,py);else{const[x0,y0]=L[i-1];g.quadraticCurveTo((x0*W+px)/2,Math.min(y0,y)*H-H*0.02,px,py)}});g.lineTo(W,H);g.closePath();
      const gr=g.createLinearGradient(0,H*0.25,0,H*0.75);gr.addColorStop(0,c1);gr.addColorStop(1,c2);g.fillStyle=gr;g.fill();
      // neiges éternelles : un liseré clair sur les crêtes
      g.save();g.clip();g.strokeStyle=neige;g.lineWidth=H*0.035;g.lineJoin='round';g.beginPath();L.forEach(([x,y],i)=>{i?g.lineTo(x*W,y*H):g.moveTo(x*W,y*H)});g.stroke();g.restore()};
    tracer(loin,'#3b5a92','#22345e','rgba(235,242,255,.85)');
    tracer(proche,'#5f7fb5','#2f4676','rgba(245,250,255,.95)');
  }
  function sol(t){
    // grande pente enneigée, bleutée dans l'ombre
    g.beginPath();g.moveTo(0,H*0.70);g.bezierCurveTo(W*0.3,H*0.64,W*0.65,H*0.72,W,H*0.62);g.lineTo(W,H);g.lineTo(0,H);g.closePath();
    const gr=g.createLinearGradient(0,H*0.62,0,H);gr.addColorStop(0,'#eef4ff');gr.addColorStop(1,'#a9bfe6');g.fillStyle=gr;g.fill();
    // scintillements de la neige
    for(let i=0;i<60;i++){const x=(i*97.13%1)*W,y=H*(0.72+((i*53.7)%1)*0.26),a=Math.max(0,Math.sin(t*2+i*1.7));g.fillStyle='rgba(255,255,255,'+(a*0.9)+')';g.fillRect(x,y,1.6,1.6)}
    sapins.forEach(s=>img('sapins',s.x*W,s.y*H,H*0.12*s.s,{a:0.95}));
  }
  function trace(){
    // la piste (pointillés) et la partie déjà faite (trace bleutée bien marquée)
    const n=80;g.lineCap='round';
    g.setLineDash([H*0.012,H*0.016]);g.strokeStyle='rgba(90,120,170,.45)';g.lineWidth=H*0.007;g.beginPath();for(let i=0;i<=n;i++){const[x,y]=piste(i/n);i?g.lineTo(x*W,y*H):g.moveTo(x*W,y*H)}g.stroke();g.setLineDash([]);
    const u=Math.min(1,pctAff/100);g.strokeStyle='rgba(56,110,200,.55)';g.lineWidth=H*0.012;g.beginPath();for(let i=0;i<=n*u;i++){const[x,y]=piste(i/n);i?g.lineTo(x*W,y*H):g.moveTo(x*W,y*H)}g.stroke();
  }
  function decors(t){
    DECORS.forEach(([u,n,h])=>{const[x,y]=piste(u);const ok=pctAff/100>=u;img(n,x*W,y*H-H*0.02,H*h,{a:ok?1:0.55,ombre:ok?'rgba(255,230,120,.8)':null})});
    // le village d'arrivée : chalet illuminé, fumée de cheminée
    const[x,y]=piste(1);const hm=H*0.24;img('maison',x*W+W*0.04,y*H,hm,{ombre:'rgba(255,200,90,.9)',flou:28});
    for(let i=0;i<6;i++){const k=((t*0.25+i/6)%1);g.fillStyle='rgba(230,235,245,'+(0.5*(1-k))+')';g.beginPath();g.arc(x*W+W*0.065+Math.sin(t+i)*6*k,y*H-hm*0.9-k*H*0.12,H*0.012*(1+k*2),0,7);g.fill()}
  }
  function skieur(t){
    const u=Math.min(1,pctAff/100);let[x,y]=piste(Math.max(0.02,Math.min(0.97,u)));const fini=pctAff>=100;
    const h=H*0.22,saut=fini?Math.abs(Math.sin(t*3))*H*0.03:Math.sin(t*4)*H*0.004;
    // gerbe de neige derrière les skis
    if(!fini&&Math.random()<0.7)eclats.push({x:x*W-h*0.25,y:y*H,vx:-(40+Math.random()*60),vy:-(30+Math.random()*50),v:1});
    const n=fini?(IMG.traineau?'traineau':'arrivee'):(opt.skieur&&IMG[opt.skieur]?opt.skieur:'perenoel');
    if(fini&&IMG.traineau){img('traineau',x*W-W*0.06,y*H-saut-H*0.02,h*1.25)}else img(n,x*W,y*H-saut,fini?h*1.15:h,{rot:fini?0:-0.06});
  }
  function particules(dt){
    eclats=eclats.filter(p=>(p.v-=dt*1.6)>0);eclats.forEach(p=>{p.x+=p.vx*dt;p.y+=p.vy*dt;p.vy+=160*dt;g.fillStyle='rgba(255,255,255,'+p.v+')';g.beginPath();g.arc(p.x,p.y,2.2,0,7);g.fill()});
    feux=feux.filter(f=>(f.v-=dt*0.7)>0);feux.forEach(f=>{f.x+=f.vx*dt;f.y+=f.vy*dt;f.vy+=60*dt;g.fillStyle=f.c.replace('A',f.v);g.beginPath();g.arc(f.x,f.y,2.4,0,7);g.fill()});
  }
  function neige(dt,t){
    flocons.forEach(f=>{f.y+=dt*0.045*f.z;f.x+=dt*0.012*Math.sin(t*0.6+f.p)*f.z;if(f.y>1.02){f.y=-0.02;f.x=R()}
      g.fillStyle='rgba(255,255,255,'+(0.35+0.6*f.z)+')';g.beginPath();g.arc(((f.x%1)+1)%1*W,f.y*H,0.7+2.4*f.z,0,7);g.fill()});
  }
  // ----- les gags -----
  const GAGS={
    fpt:{dur:11,txt:"Le FPT a trouvé ses rennes. Plus besoin de gasoil !",dessin(k,t){const x=W*(1.15-1.4*k),y=H*0.80;const h=H*0.17;
      img('rennes',x-h*1.9,y+Math.sin(t*9)*3,h*0.9,{flip:true});const w=img('fpt',x,y,h,{flip:true});bonnetSur(x-w*0.3,y-h*0.93,h*0.16);g.strokeStyle='#7c2d12';g.lineWidth=2;g.beginPath();g.moveTo(x-w*0.5,y-h*0.35);g.lineTo(x-h*1.55,y-h*0.5);g.stroke()}},
    ccf:{dur:10,txt:"Le CCF s'est reconverti en chasse-neige. Ça mouille moins que les feux !",dessin(k,t){const x=W*(-0.25+1.45*k),y=H*0.88;const h=H*0.18;
      img('ccf',x,y+Math.sin(t*6)*2,h);for(let i=0;i<4;i++)eclats.push({x:x+h*0.95,y:y-h*0.35,vx:60+Math.random()*120,vy:-(80+Math.random()*90),v:1})}},
    vtu:{dur:9,txt:"Le VTU a mis les chaînes… et les skis. Personne ne sait pourquoi.",dessin(k,t){const x=W*(1.2-1.45*k),y=H*0.76;const h=H*0.14;
      img('vtu',x,y,h,{rot:Math.sin(t*5)*0.12,flip:true});g.fillStyle='#b91c1c';g.fillRect(x-h*1.2,y-2,h*2.4,4)}},
    traineau:{dur:11,txt:"Le Sergent-Chef et la Sergente-Chef font un tour de traîneau. Ils trichent : ils volent !",dessin(k,t){const x=W*(-0.2+1.4*k),y=H*(0.36+0.05*Math.sin(k*7));
      img('traineau',x,y,H*0.2,{ombre:'rgba(255,230,150,.9)',flou:24});
      if(Math.random()<0.8)feux.push({x:x-H*0.16,y:y-H*0.04,vx:-(20+Math.random()*30),vy:10+Math.random()*20,v:1,c:'rgba(255,230,150,A)'})}},
    brigade:{dur:14,txt:"La brigade de la forêt rentre d'intervention. Le loup n'a pas lâché son café.",dessin(k,t){const x=W*(-0.35+1.7*k),y=H*0.995+Math.abs(Math.sin(t*6))*-2;
      img('brigade',x,y,H*0.24);if(Math.random()<0.5)eclats.push({x:x-H*0.25,y:y,vx:-(20+Math.random()*40),vy:-(20+Math.random()*30),v:1})}},
    lutin:{dur:9,txt:"Le lutin pompier fait une reconnaissance… et arrose tout le monde de neige !",dessin(k,t){const a=k<0.12?k/0.12:k>0.88?(1-k)/0.12:1;const x=W*(0.06+0.16*a),y=H*0.99;
      img('lutin',x+H*0.2,y,H*0.3,{a});for(let i=0;i<5;i++)eclats.push({x:x+H*0.42,y:y-H*0.19,vx:120+Math.random()*160,vy:-(40+Math.random()*90),v:1})}},
    renne:{dur:9,txt:"Rudolph s'entraîne pour Noël. Il a encore du boulot…",dessin(k,t){const a=k<0.12?k/0.12:k>0.88?(1-k)/0.12:1;const x=W*(1.08-0.24*a),y=H*0.99+Math.sin(t*5)*2;
      img('renne',x,y,H*0.26,{a})}},
    bonhomme:{dur:8,txt:"Un bonhomme de neige en tenue d'intervention. Casque réglementaire !",dessin(k,t){const a=k<0.15?k/0.15:k>0.85?(1-k)/0.15:1;const x=W*0.30,y=H*(0.98-0.16*a);bonhommeNeige(x,y,H*0.2,t)}}
  };
  function bonnetSur(x,y,s){g.fillStyle='#dc2626';g.beginPath();g.moveTo(x-s,y);g.quadraticCurveTo(x,y-s*1.6,x+s*1.2,y-s*0.6);g.lineTo(x+s*0.8,y);g.fill();g.fillStyle='#fff';g.fillRect(x-s*1.1,y-s*0.15,s*2,s*0.35);g.beginPath();g.arc(x+s*1.2,y-s*0.6,s*0.3,0,7);g.fill()}
  function bonhommeNeige(x,y,h,t){const r1=h*0.26,r2=h*0.19,r3=h*0.14;g.fillStyle='#fff';g.strokeStyle='#b8c7e6';g.lineWidth=2;
    [[0,r1],[-(r1+r2*0.8),r2],[-(r1+r2*1.6+r3*0.7),r3]].forEach(([dy,r])=>{g.beginPath();g.arc(x,y-r1+dy,r,0,7);g.fill();g.stroke()});
    const ty=y-r1-(r1+r2*1.6+r3*0.7);g.fillStyle='#111';[-.35,.35].forEach(a=>{g.beginPath();g.arc(x+a*r3,ty-r3*0.2,r3*0.1,0,7);g.fill()});g.fillStyle='#f97316';g.beginPath();g.moveTo(x,ty);g.lineTo(x+r3*0.9,ty+r3*0.12);g.lineTo(x,ty+r3*0.22);g.fill();
    // casque de pompier chromé
    const cg=g.createLinearGradient(x-r3,ty-r3*1.5,x+r3,ty-r3*0.4);cg.addColorStop(0,'#f8fafc');cg.addColorStop(0.5,'#94a3b8');cg.addColorStop(1,'#e2e8f0');g.fillStyle=cg;g.beginPath();g.ellipse(x,ty-r3*0.55,r3*1.05,r3*0.85,0,Math.PI,0);g.fill();g.fillStyle='#1c1917';g.fillRect(x-r3*1.3,ty-r3*0.6,r3*2.6,r3*0.18);
    // un bras-branche qui salue
    g.strokeStyle='#7c4a1e';g.lineWidth=3;g.beginPath();const by=y-r1-(r1+r2*0.8);g.moveTo(x+r2*0.8,by);g.lineTo(x+r2*1.8,by-r2*(0.8+0.3*Math.sin(t*6)));g.stroke()}
  function lancerGag(n){const L=Object.keys(GAGS),k=n||L[Math.floor(Math.random()*L.length)];gag={n:k,t:0};if(opt.dire)opt.dire(GAGS[k].txt);bulle={txt:GAGS[k].txt,t:0}}
  function dessinerBulle(dt){if(!bulle||opt.dire)return;bulle.t+=dt;if(bulle.t>6){bulle=null;return}
    const a=Math.min(1,bulle.t*3,(6-bulle.t)*2),x=W*0.025,y=H*0.19,h=H*0.10;g.globalAlpha=a;img('sergent',x+h*0.5,y+h,h);
    g.font='700 '+Math.round(H*0.032)+'px Inter,system-ui,sans-serif';const w=Math.min(W*0.6,g.measureText(bulle.txt).width+H*0.05);
    g.save();g.shadowColor='rgba(0,0,0,.35)';g.shadowBlur=12;g.fillStyle='rgba(255,255,255,.96)';g.beginPath();g.roundRect(x+h*1.1,y+h*0.18,w,h*0.64,h*0.3);g.fill();g.restore();g.fillStyle='#111';g.fillText(bulle.txt,x+h*1.1+H*0.025,y+h*0.6,W*0.58);g.globalAlpha=1}
  function feuArtifice(){const x=W*(0.55+Math.random()*0.4),y=H*(0.12+Math.random()*0.25),c=['rgba(251,191,36,A)','rgba(244,63,94,A)','rgba(96,165,250,A)','rgba(74,222,128,A)'][Math.floor(Math.random()*4)];
    for(let i=0;i<40;i++){const a=i/40*6.283,v=40+Math.random()*70;feux.push({x,y,vx:Math.cos(a)*v,vy:Math.sin(a)*v,v:1,c})}}
  let avant=performance.now();
  function image(){if(!vivant)return;requestAnimationFrame(image);if(document.hidden)return;
    const now=performance.now(),dt=Math.min(0.1,(now-avant)/1000),t=(now-t0)/1000;avant=now;
    pctAff+=(pct-pctAff)*Math.min(1,dt*1.2);
    ciel(t);if(gag&&gag.n==='traineau'){const G=GAGS.traineau;gag.t+=dt;G.dessin(Math.min(1,gag.t/G.dur),t);if(gag.t>G.dur)gag=null}
    montagnes();sol(t);trace();decors(t);
    if(gag&&gag.n!=='traineau'){const G=GAGS[gag.n];gag.t+=dt;G.dessin(Math.min(1,gag.t/G.dur),t);if(gag.t>G.dur)gag=null}
    skieur(t);particules(dt);neige(dt,t);dessinerBulle(dt);
    if(pctAff>=99.5&&Math.random()<dt*0.9)feuArtifice();
    gagSuivant-=dt;if(gagSuivant<=0&&!gag){lancerGag();gagSuivant=opt.intervalle||32}
  }
  taille();addEventListener('resize',taille);requestAnimationFrame(image);
  return {avancer(p){pct=Math.max(0,p)},gag:lancerGag,arreter(){vivant=false},taille};
}
