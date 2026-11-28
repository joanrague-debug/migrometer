/* ───────────── Web pública: portada, menú, pestañas y contador ───────────── */
/* Contador de visitas (GoatCounter). Escribe aquí el código de tu cuenta, p. ej. "migrometer". Vacío = contador oculto. */
const GC_CODE="migrometer";
function renderHero(){
  const r=range(); const [a,b]=rangeBounds();
  const evs=S.events.filter(e=>inRange(e,r)&&inGeo(e)&&!e._excluded);
  const pv=evs.reduce((s,e)=>s+(persons(e)||0),0);
  const past=S.f.day<todayISO(), EN=typeof LANG!=="undefined"&&LANG==="en";
  const upto=n=>EN?" · "+n+" days to "+dShort(S.f.day):" · "+n+" días hasta el "+dShort(S.f.day);
  const lab={dia:" · "+dShort(S.f.day),"7d":past?upto(7):" · últimos 7 días","30d":past?upto(30):" · últimos 30 días",anio:" · "+S.f.day.slice(0,4),todo:" · todo el registro"}[S.f.preset]||"";
  $("#heroK").textContent=lab+(scopeLabel()!=="Toda España"?" · "+scopeLabel():"");
  const n=$("#heroNum");
  if(evs.length){n.innerHTML=esc(fmt(pv));
    const days=[...new Set(evs.map(e=>e.date))].sort();
    $("#heroS").innerHTML='personas llegadas <b>según la prensa</b> del '+esc(dShort(days[0]))+' al '+esc(dShort(days[days.length-1]))+' · '+evs.length+(evs.length===1?' llegada registrada':' llegadas registradas')+' · '+sourcesOf(evs).length+' medios citados';
  }else{n.innerHTML='<em class="hero-empty">Sin datos reportados</em>';$("#heroS").textContent="No hay llegadas registradas en la prensa para estas fechas y zona.";}
  const o=officialFor(a,b,cmpScope().keys);
  if(o.v!=null){$("#hcO").textContent=fmt(o.v);$("#hcOs").textContent=(o.full?"Del ":"Solo del ")+dShort(o.covA)+" al "+dShort(o.covB)+" · Interior no se suma a la prensa";}
  else{const nv=o.near?periodVal(o.near,cmpScope().keys):null;$("#hcO").textContent=nv!=null?fmt(nv):"—";$("#hcOs").textContent=o.near?"Quincena más cercana, "+dShort(o.near.a)+" – "+dShort(o.near.b)+" · se muestra aparte":"Sin cifra oficial para estas fechas";}
  const eq=$("#heroEq");
  if(pv>0){const m=nearestMuni(pv);
    eq.querySelector(".nm").textContent=muniName(m);
    eq.querySelector(".mt").textContent=PROV[m[1].slice(0,2)]+" · "+fmt(m[0])+" habitantes · según la prensa";
  }else{eq.querySelector(".nm").textContent="—";eq.querySelector(".mt").textContent="Sin datos reportados para comparar";}
  if(pv>0){$("#hcS").textContent=euros(pv*SAN.nat)+" al año";$("#hcSs").textContent="Estimación: "+fmt(pv)+" personas × "+fmt(SAN.nat)+" € por habitante ("+SAN.year+")";}
  else{$("#hcS").textContent="—";$("#hcSs").textContent="Sin datos reportados";}
}
function setupChrome(){
  const tb=$("#tb"), btn=$("#tbMenu");
  const hero=document.getElementById("top");
  const onBand=()=>{const r=hero?hero.getBoundingClientRect():null;tb.classList.toggle("on-band",!!r&&r.bottom>tb.offsetHeight+40);};
  onBand(); window.addEventListener("scroll",onBand,{passive:true}); window.addEventListener("resize",onBand);
  const close=()=>{tb.classList.remove("open");document.documentElement.classList.remove("menu-open");btn.setAttribute("aria-expanded","false");btn.setAttribute("aria-label","Abrir el menú");};
  btn.onclick=()=>{const o=tb.classList.toggle("open");document.documentElement.classList.toggle("menu-open",o);btn.setAttribute("aria-expanded",String(o));btn.setAttribute("aria-label",o?"Cerrar el menú":"Abrir el menú");};
  document.querySelectorAll("#tbNav a").forEach(a=>a.addEventListener("click",close));
  const scrim=document.getElementById("tbScrim"); if(scrim) scrim.onclick=close;
  document.addEventListener("keydown",e=>{if(e.key==="Escape"&&tb.classList.contains("open")){close();btn.focus();}});
  const ids=["h-day","h-vel","h-sim","h-pop","h-san","h-prof","h-map","h-off","h-med","h-log"];
  if("IntersectionObserver" in window){
    const io=new IntersectionObserver(es=>{es.forEach(e=>{if(e.isIntersecting){const id=e.target.id;
      document.querySelectorAll("#tbNav a").forEach(a=>a.classList.toggle("on",a.getAttribute("href")==="#"+id));
      document.querySelectorAll("#tabbar a").forEach(a=>a.classList.toggle("on",a.dataset.t===id));}});},{rootMargin:"-30% 0px -60% 0px"});
    ids.forEach(id=>{const el=document.getElementById(id);if(el)io.observe(el);});
  }
}
/* Contador público de visitas: Abacus (sin registro ni correo; solo guarda un número).
   Cada carga de la página suma 1 al instante y la cifra se refresca cada minuto mientras la página está abierta.
   GoatCounter se mantiene aparte para las estadísticas y como respaldo si Abacus no responde. */
const VISITS_NS="migrometer-es", VISITS_KEY="visitas";
async function setupVisits(){
  const show=n=>{if(n==null||!isFinite(n))return false;$("#visitsN").textContent=fmt(n)+(n===1?" visita":" visitas");$("#visitsPill").hidden=false;return true;};
  const ab=async op=>{try{const r=await fetch("https://abacus.jasoncameron.dev/"+op+"/"+VISITS_NS+"/"+VISITS_KEY,{cache:"no-store"});if(!r.ok)return null;const d=await r.json();return typeof d.value==="number"?d.value:null;}catch(e){return null;}};
  if(GC_CODE&&/^[a-z0-9-]+$/.test(GC_CODE)){try{const s=document.createElement("script");s.async=true;s.src="https://gc.zgo.at/count.js";s.dataset.goatcounter="https://"+GC_CODE+".goatcounter.com/count";document.body.appendChild(s);}catch(e){}}
  const isLocal=/^(localhost|127\.|\[::1\])/.test(location.hostname)||location.protocol==="file:";
  let ok=show(await ab(isLocal?"get":"hit"));
  if(!ok&&GC_CODE){
    try{const r=await fetch("https://"+GC_CODE+".goatcounter.com/counter/TOTAL.json?start=2020-01-01",{cache:"no-store"});if(r.ok){const d=await r.json();ok=show(Number(String(d.count).replace(/[^\d]/g,""))||0);}}catch(e){}
  }
  if(ok) setInterval(async()=>{if(document.visibilityState!=="visible")return;show(await ab("get"));},60000);
}
