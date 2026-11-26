#!/usr/bin/env python3
"""Genera la web pública de Migrometer (solo lectura) a partir del panel.
Salidas: public.html (contenido para el artefacto) y, con --docs DIR, DIR/index.html completo."""
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
PANEL = os.environ.get('MIGRO_PANEL', os.path.join(HERE, '..', 'panel', 'index.html'))
def rd(n): return open(os.path.join(HERE, n), encoding='utf8').read()
h = open(PANEL, encoding='utf8').read()

def R(a, b, cnt=1):
    global h
    n = h.count(a); assert n == cnt, (n, a[:100]); h = h.replace(a, b)
def cut(a, b, repl=''):
    global h
    i = h.index(a); j = h.index(b, i); h = h[:i] + repl + h[j:]

R('<title>Migrometer ES</title>', '<title>Migrometer</title>')
# Cabecera nueva (logotipo, menú) + portada; fuera la cabecera del panel
chrome = rd('public_chrome.html').replace('__LOGO_SYMBOL__', rd('logo_symbol.svg').strip())
cut('<header class="top wrap">', '<div class="bar">', chrome + '\n')
# Sin entrada de datos
cut('  <!-- 6. Entrada de noticias -->', '  <!-- 7. Registro -->')
R('<span class="sub">Toca un punto o una zona para filtrar</span>', '<span class="sub">Toca un punto o una zona para filtrar la página</span>')
# Pie: metodología y aviso legal plegados + barra de pestañas móvil
i = h.index('  <footer>'); j = h.index('  </footer>', i) + len('  </footer>')
h = h[:i] + rd('public_footer.html') + h[j:]
R('<div class="toast" id="toast" hidden></div>', '<div class="toast" id="toast" hidden></div>\n' + rd('public_tabbar.html'))
# Estilos: pie + tema público (al final para que manden)
R('</style>', '''.legal{display:grid;gap:4px;padding-top:28px;margin-top:10px;border-top:1px solid var(--line)}
.fold summary{cursor:pointer;font-size:12.5px;font-weight:600;color:var(--fg-3);padding:6px 0;list-style:none;display:inline-flex;align-items:center;gap:6px}
.fold summary::-webkit-details-marker{display:none}
.fold summary::before{content:"";width:6px;height:6px;border-right:1.5px solid currentColor;border-bottom:1.5px solid currentColor;transform:rotate(-45deg);transition:transform .15s}
.fold[open] summary::before{transform:rotate(45deg)}
.fold summary:hover{color:var(--fg-2)}
.fold-body{display:grid;gap:10px;padding:6px 0 12px 12px}
.fine{font-size:11.5px;color:var(--fg-3);margin:6px 0 0}
.legal h3{font-size:12.5px;margin:0 0 2px;color:var(--fg)}
.legal p,.legal li{margin:0;color:var(--fg-3);font-size:12px;line-height:1.5;max-width:100ch}
.legal ul{margin:0;padding-left:18px;display:grid;gap:4px}
''' + rd('public_theme.css') + '\n</style>')
# JS: solo lectura, sin almacenamiento, datos desde data.json
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
R('function setPill(){', '''function setPill(){
  const el=$("#updAt"); if(!el) return;
  if(S.mode==="public"){const u=S.meta&&S.meta.updatedAt; el.textContent="Datos actualizados: "+(u?new Date(u).toLocaleString("es-ES",{day:"numeric",month:"long",year:"numeric",hour:"2-digit",minute:"2-digit",timeZone:"Europe/Madrid"}):"sin fecha");}
  else if(S.mode==="error"){el.textContent="No se pudieron cargar los datos";$("#updPill").className="pill local";}
  else el.textContent="Cargando datos…";
  return;''')
R('''  $("#inputSection").hidden=!S.canWrite&&S.mode==="db";}''', '  renderHero();}')
cut('$("#refDate").value=todayISO();', 'window.matchMedia(')
R('initStore().then(initSample);', 'function renderDrafts(){}\n' + rd('public_extra.js') + '\nsetupChrome();\ninitStore();\nsetupVisits();')
open(os.path.join(HERE, 'public.html'), 'w', encoding='utf8').write(h)
print('public.html', len(h))
if '--docs' in sys.argv:
    out = sys.argv[sys.argv.index('--docs') + 1]
    head = '''<!doctype html>
<html lang="es">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<meta name="description" content="Llegadas irregulares de personas migrantes a España según la prensa y según el Ministerio del Interior, por separado y con sus fuentes.">
<meta name="theme-color" content="#111111">
<link rel="icon" href="favicon.svg" type="image/svg+xml">
<link rel="apple-touch-icon" href="apple-touch-icon.png">
<style>:root{color-scheme:light;padding-top:env(safe-area-inset-top,0px);padding-bottom:env(safe-area-inset-bottom,0px)}body{margin:0;font:14px system-ui,-apple-system,sans-serif}img{max-width:100%}[hidden]{display:none!important}</style>
</head>
<body>
'''
    open(os.path.join(out, 'index.html'), 'w', encoding='utf8').write(head + h + '\n</body>\n</html>\n')
    print(os.path.join(out, 'index.html'))
