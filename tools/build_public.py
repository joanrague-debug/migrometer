#!/usr/bin/env python3
"""Genera docs/index.html (web pública, solo lectura) a partir de panel/index.html.
Uso: python3 tools/build_public.py"""
import re, sys, os
HERE=os.path.dirname(os.path.abspath(__file__)); ROOT=os.path.dirname(HERE)
src = open(os.path.join(ROOT,'panel','index.html'), encoding='utf8').read()
h = src

def R(a, b, cnt=1):
    global h
    n = h.count(a)
    assert n == cnt, (n, a[:100])
    h = h.replace(a, b)

def cut(a, b, repl=''):
    global h
    i = h.index(a); j = h.index(b, i)
    h = h[:i] + repl + h[j:]

R('<title>Migrometer ES</title>', '<title>Migrometer ES Web</title>')
R('aria-label="Logotipo de Migrometer ES"', 'aria-label="Logotipo de Migrometer ES"')
R('<p>Llegadas irregulares a España · recuento diario a partir de noticias y balances oficiales</p>',
  '<p>Llegadas irregulares de personas migrantes a España · noticias y datos oficiales, siempre por separado y con sus fuentes</p>')
# Cabecera: sin exportar ni estado de base de datos
cut('    <div class="meta">', '  </div>\n</header>',
    '    <div class="meta">\n      <span class="pill ok" id="updPill"><i></i><span id="updAt">Cargando datos…</span></span>\n    </div>\n')
# Navegación interna
R('</header>\n', '''</header>
<nav class="pnav wrap" aria-label="Secciones">
  <a href="#h-day">Resumen</a><a href="#h-pop">Población</a><a href="#h-prof">Perfil</a><a href="#h-map">Mapa</a><a href="#h-off">Oficial y prensa</a><a href="#h-st">Estadísticas</a><a href="#h-med">Medios</a><a href="#h-log">Registro</a>
</nav>
''')
# Sin entrada de datos
cut('  <!-- 6. Entrada de noticias -->', '  <!-- 7. Registro -->')
R('<span class="sub">Toca un punto o una zona para filtrar</span>', '<span class="sub">Toca un punto o una zona para filtrar la página</span>')
# Pie: metodología, fuentes y aviso legal
i = h.index('  <footer>'); j = h.index('  </footer>', i) + len('  </footer>')
h = h[:i] + open(os.path.join(HERE,'public_footer.html'), encoding='utf8').read() + h[j:]
# Estilos extra
R('.prof{display:grid;gap:14px}', '''.prof{display:grid;gap:14px}
.brand .meta .pill{white-space:normal;height:auto;min-height:28px;padding:4px 11px;max-width:100%}
.pnav{display:flex;gap:6px;flex-wrap:wrap;padding-block:4px 0}
.pnav a{display:inline-flex;align-items:center;height:30px;padding:0 12px;border-radius:999px;background:var(--fill);color:var(--fg);font-size:13px;font-weight:500;text-decoration:none}
.pnav a:hover{background:var(--fill-2);text-decoration:none}
.section-h h2,footer h2{scroll-margin-top:130px}
.legal{display:grid;gap:4px;padding-top:28px;margin-top:10px;border-top:1px solid var(--line)}
.fold summary{cursor:pointer;font-size:12.5px;font-weight:600;color:var(--fg-3);padding:6px 0;list-style:none;display:inline-flex;align-items:center;gap:6px}
.fold summary::-webkit-details-marker{display:none}
.fold summary::before{content:"";width:6px;height:6px;border-right:1.5px solid currentColor;border-bottom:1.5px solid currentColor;transform:rotate(-45deg);transition:transform .15s}
.fold[open] summary::before{transform:rotate(45deg)}
.fold summary:hover{color:var(--fg-2)}
.fold-body{display:grid;gap:10px;padding:6px 0 12px 12px}
.fine{font-size:11.5px;color:var(--fg-3);margin:6px 0 0}
.legal h2,.legal h3{color:var(--fg)}
.legal h2{font-family:var(--font-display);font-size:22px;margin:0;letter-spacing:-.01em}
.legal h3{font-size:12.5px;margin:0 0 2px}
.legal p,.legal li{margin:0;color:var(--fg-3);font-size:12px;line-height:1.5;max-width:100ch}
.legal ul{margin:0;padding-left:18px;display:grid;gap:4px}
.legal .card{padding:18px 20px;display:grid;gap:12px}''')
# JS: solo lectura, sin almacenamiento en el dispositivo, datos desde data.json
R('function lsGet(k){try{return JSON.parse(localStorage.getItem(k)||"null");}catch(e){return null;}}', 'function lsGet(k){return null;}')
R('function lsSet(k,v){try{localStorage.setItem(k,JSON.stringify(v));}catch(e){}}', 'function lsSet(k,v){}')
R('events:[], official:null, mode:"loading", canWrite:true,', 'events:[], official:null, mode:"loading", canWrite:false,')
i = h.index('async function initStore(){'); j = h.index('\nasync function putEvent', i)
h = h[:i] + '''async function initStore(){
  renderAll();
  try{
    const r=await fetch("data.json",{cache:"no-store"}); if(!r.ok) throw new Error(String(r.status));
    const d=await r.json();
    S.events=Array.isArray(d.events)?d.events:[]; S.offReports=Array.isArray(d.official)?d.official:[]; S.official=null; S.meta=d; S.mode="public";
    const last=S.events.map(e=>e.date).sort().pop();
    if(last&&last<addDays(todayISO(),-6)) S.f.day=last;
  }catch(e){S.mode="error";}
  renderAll();
}''' + h[j:]
R('''function setPill(){''', '''function setPill(){
  const el=$("#updAt"); if(!el) return;
  if(S.mode==="public"){const u=S.meta&&S.meta.updatedAt; el.textContent="Datos actualizados: "+(u?new Date(u).toLocaleString("es-ES",{day:"numeric",month:"long",year:"numeric",hour:"2-digit",minute:"2-digit",timeZone:"Europe/Madrid"}):"sin fecha");}
  else if(S.mode==="error"){el.textContent="No se pudieron cargar los datos";$("#updPill").className="pill local";}
  else el.textContent="Cargando datos…";
  return;''')
R('''  $("#inputSection").hidden=!S.canWrite&&S.mode==="db";}''', '}')
cut('$("#refDate").value=todayISO();', 'window.matchMedia(')
R('initStore().then(initSample);', 'function renderDrafts(){}\ninitStore();')
HEAD = """<!doctype html>
<html lang="es">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<meta name="description" content="Llegadas irregulares de personas migrantes a España según la prensa y según el Ministerio del Interior, por separado y con sus fuentes.">
<style>:root{color-scheme:light;padding-top:env(safe-area-inset-top,0px);padding-bottom:env(safe-area-inset-bottom,0px)}body{margin:0;font:14px system-ui,-apple-system,sans-serif}img{max-width:100%}[hidden]{display:none!important}</style>
</head>
<body>
"""
out=os.path.join(ROOT,'docs','index.html')
open(out, 'w', encoding='utf8').write(HEAD + h + '\n</body>\n</html>\n')
print(out, len(h))
