/* ───────────── Idioma: español (original) / inglés ───────────── */
/* La web se escribe en español. En inglés, los números y fechas se formatean en inglés y
   los textos se traducen con el diccionario I18N_EN (frases completas o plantillas con {0}, {1}…
   donde van números y fechas). Lo que no está en el diccionario (nombres propios, notas
   originales de las noticias) se deja tal cual. La elección va en la URL (?lang=en): no se guarda nada. */
const MES_EN=["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"];
const MESL_EN=["January","February","March","April","May","June","July","August","September","October","November","December"];
const DIAS_EN=["Sunday","Monday","Tuesday","Wednesday","Thursday","Friday","Saturday"];
function fmt(n){
  if(n==null||isNaN(n)) return "—";
  const neg=n<0; n=Math.abs(n);
  const r=Math.round(n*10)/10;
  let [i,d]=String(r).split(".");
  i=i.replace(/\B(?=(\d{3})+(?!\d))/g,LANG==="en"?",":".");
  return (neg?"−":"")+i+(d&&d!=="0"?(LANG==="en"?".":",")+d:"");
}
function dShort(s){const d=parseISO(s);return LANG==="en"?MES_EN[d.getMonth()]+" "+d.getDate():d.getDate()+" "+MES[d.getMonth()];}
function dLong(s){const d=parseISO(s);return LANG==="en"?DIAS_EN[d.getDay()]+", "+MESL_EN[d.getMonth()]+" "+d.getDate()+", "+d.getFullYear():DIAS[d.getDay()]+" "+d.getDate()+" de "+MESL[d.getMonth()]+" de "+d.getFullYear();}
function euros(n,long){
  if(n==null||!isFinite(n)) return "—";
  const d1=x=>x.toLocaleString(LANG==="en"?"en-GB":"es-ES",{minimumFractionDigits:1,maximumFractionDigits:1});
  if(n>=1e9) return LANG==="en"?"€"+d1(Math.round(n/1e8)/10)+(long?" billion":"bn"):d1(Math.round(n/1e8)/10)+(long?" mil millones de €":" mil M€");
  if(n>=1e6) return LANG==="en"?"€"+d1(Math.round(n/1e5)/10)+(long?" million":"M"):d1(Math.round(n/1e5)/10)+(long?" millones de €":" M€");
  return LANG==="en"?"€"+fmt(Math.round(n)):fmt(Math.round(n))+" €";
}
const I18N_TOK=/(?:(?:Sunday|Monday|Tuesday|Wednesday|Thursday|Friday|Saturday), )?(?:January|February|March|April|May|June|July|August|September|October|November|December|Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec) \d{1,2}(?:, \d{4})?|€?[−+-]?\d(?:[\d.,]*\d)?(?:bn|M)?/g;
const I18N_MISS=new Set();
const I18N_PHR=[[/Guinea-Bisáu/g,"Guinea-Bissau"],[/Costa de Marfil/g,"Côte d'Ivoire"],[/Marruecos/g,"Morocco"],[/Argelia/g,"Algeria"],[/África subsahariana \(sin precisar\)/g,"Sub-Saharan Africa (unspecified)"],[/Magreb \(sin precisar\)/g,"Maghreb (unspecified)"],
  [/ y (\d+) más$/," and $1 more"],[/^(Ver|Ver todo)$/,"See all"],[/ \(cita a ([^)]+)\)/," (cites $1)"]];
const ES_ML=["enero","febrero","marzo","abril","mayo","junio","julio","agosto","septiembre","octubre","noviembre","diciembre"];
const ES_MS=["ene","feb","mar","abr","may","jun","jul","ago","sep","oct","nov","dic"];
function i18nPre(s){
  return s.replace(new RegExp("\\b(\\d{1,2}) de ("+ES_ML.join("|")+")(?: de (\\d{4}))?","g"),(_,d,m,y)=>MESL_EN[ES_ML.indexOf(m)]+" "+d+(y?", "+y:""))
    .replace(new RegExp("\\b("+ES_ML.join("|")+") de (\\d{4})","g"),(_,m,y)=>MESL_EN[ES_ML.indexOf(m)]+" "+y)
    .replace(new RegExp("\\b(\\d{1,2}) ("+ES_MS.join("|")+")\\b","g"),(_,d,m)=>MES_EN[ES_MS.indexOf(m)]+" "+d);
}
function i18nNum(t){
  if(/^\d{1,3}(\.\d{3})+$/.test(t)) return t.replace(/\./g,",");
  if(/^\d+,\d{1,2}$/.test(t)) return t.replace(",",".");
  return t;
}
function i18nOne(core){
  if(Object.prototype.hasOwnProperty.call(I18N_EN,core)) return I18N_EN[core];
  const pre=i18nPre(core);
  if(Object.prototype.hasOwnProperty.call(I18N_EN,pre)) return I18N_EN[pre];
  const toks=[]; const key=pre.replace(I18N_TOK,t=>{toks.push(t);return "{"+(toks.length-1)+"}";});
  if(toks.length&&Object.prototype.hasOwnProperty.call(I18N_EN,key)) return I18N_EN[key].replace(/\{(\d+)\}/g,(_,i)=>i18nNum(toks[+i]??""));
  return null;
}
function T(s){
  if(LANG!=="en"||s==null) return s;
  const str=String(s); const m=str.match(/^(\s*)([\s\S]*?)(\s*)$/); const core=m[2];
  if(!core||!/[A-Za-zÁÉÍÓÚÑáéíóúñ]/.test(core)) return str;
  let r=i18nOne(core);
  if(r==null&&core.includes(" · ")){const parts=core.split(" · ");const tp=parts.map(p=>i18nOne(p)??p);if(tp.some((x,i)=>x!==parts[i])) r=tp.join(" · ");}
  if(r==null){const mm=core.match(/^([^:]{1,60}): (.+)$/);if(mm){const a=i18nOne(mm[1])??mm[1],b=i18nOne(mm[2]);if(b!=null) r=a+": "+b;}}
  if(r==null){let p=core; I18N_PHR.forEach(([re,to])=>{p=p.replace(re,to);}); if(p!==core) r=p;}
  if(r==null){const key=x=>{let i=0;return i18nPre(x).replace(I18N_TOK,()=>"{"+(i++)+"}");};
    const add=x=>{if(i18nOne(x)==null&&/[a-záéíóúñ]{3}/.test(x)) I18N_MISS.add(key(x));};
    if(core.includes(" · ")) core.split(" · ").forEach(add); else {const mm=core.match(/^([^:]{1,60}): (.+)$/); if(mm){add(mm[1]);add(mm[2]);} else add(core);}
    return str;}
  return m[1]+r+m[3];
}
const I18N_ATTRS=["title","aria-label","placeholder","alt"];
function i18nNode(n){
  if(n.nodeType===3){const p=n.parentNode; if(!p||p.closest&&p.closest("script,style,[data-noi18n]"))return; const t=T(n.nodeValue); if(t!==n.nodeValue) n.nodeValue=t; return;}
  if(n.nodeType!==1||n.matches("script,style,[data-noi18n]")) return;
  I18N_ATTRS.forEach(a=>{const v=n.getAttribute(a); if(v){const t=T(v); if(t!==v) n.setAttribute(a,t);}});
  n.childNodes.forEach(i18nNode);
}
function setupLang(){
  const sel=document.getElementById("langSel");
  if(sel){sel.querySelectorAll("a").forEach(a=>{const on=a.dataset.l===LANG;a.classList.toggle("on",on);a.setAttribute("aria-current",on?"true":"false");
    const u=new URL(location.href); if(a.dataset.l==="en") u.searchParams.set("lang","en"); else u.searchParams.delete("lang"); a.href=u.pathname+u.search+u.hash;});}
  if(LANG!=="en") return;
  document.documentElement.lang="en";
  document.querySelectorAll(".kf-es").forEach(e=>e.hidden=true); document.querySelectorAll(".kf-en").forEach(e=>e.hidden=false);
  document.title="Migrometer · Irregular arrivals in Spain, day by day";
  if(window.Chart&&!window.Chart.__i18n){
    const C0=window.Chart;
    const tc=cfg=>{try{const d=cfg.data||{}; if(Array.isArray(d.labels)) d.labels=d.labels.map(x=>typeof x==="string"?T(x):x);
      (d.datasets||[]).forEach(ds=>{if(typeof ds.label==="string") ds.label=T(ds.label);});
      const cb=cfg.options&&cfg.options.plugins&&cfg.options.plugins.tooltip&&cfg.options.plugins.tooltip.callbacks;
      if(cb) ["label","title","afterLabel"].forEach(k=>{if(typeof cb[k]==="function"){const f=cb[k]; cb[k]=function(...a){const r=f.apply(this,a); return Array.isArray(r)?r.map(T):T(r);};}});}catch(e){} return cfg;};
    class TChart extends C0{constructor(el,cfg){super(el,tc(cfg));}}
    TChart.__i18n=true; window.Chart=TChart;
  }
  i18nNode(document.body);
  new MutationObserver(ms=>ms.forEach(m=>{if(m.type==="characterData") i18nNode(m.target); else m.addedNodes.forEach(i18nNode); if(m.type==="attributes") i18nNode(m.target);}))
    .observe(document.body,{subtree:true,childList:true,characterData:true,attributes:true,attributeFilter:I18N_ATTRS});
}
