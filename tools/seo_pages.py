#!/usr/bin/env python3
"""Migrometer · páginas de aterrizaje por búsqueda (hoy, Canarias, Ceuta, Melilla, Baleares, península).
Las genera seo.py cada noche a partir de docs/data.json. Solo usa cifras del propio data.json:
no inventa nada; donde no hay datos dice «Sin datos reportados»."""
import os, json, html
from datetime import date, timedelta

SITE = "https://migrometer.es/"
ZN = {"el-hierro": "El Hierro", "la-palma": "La Palma", "la-gomera": "La Gomera", "tenerife": "Tenerife", "gran-canaria": "Gran Canaria",
      "fuerteventura": "Fuerteventura", "lanzarote": "Lanzarote y La Graciosa", "canarias": "Canarias (isla sin precisar)",
      "ceuta": "Ceuta", "melilla": "Melilla", "almeria": "Almería", "alboran": "Isla de Alborán", "granada": "Granada (Motril)",
      "malaga": "Málaga", "cadiz": "Cádiz y Estrecho", "huelva": "Huelva", "murcia": "Región de Murcia", "alicante": "Alicante",
      "valencia": "Valencia y Castellón", "formentera": "Formentera", "ibiza": "Ibiza", "cabrera": "Cabrera", "mallorca": "Mallorca",
      "menorca": "Menorca", "baleares": "Baleares (isla sin precisar)", "otras": "Otras zonas, interior o aeropuertos"}
CAN = {"el-hierro", "la-palma", "la-gomera", "tenerife", "gran-canaria", "fuerteventura", "lanzarote", "canarias"}
BAL = {"formentera", "ibiza", "cabrera", "mallorca", "menorca", "baleares"}
PEN = {"almeria", "alboran", "granada", "malaga", "cadiz", "huelva", "murcia", "alicante", "valencia", "otras"}
esc = html.escape

PAGES = [
    {"slug": "hoy", "zones": None, "keys": None, "name": "España",
     "title": "Inmigrantes llegados hoy a España: pateras y cayucos · Migrometer",
     "h1": "Inmigrantes llegados hoy a España",
     "desc": "Cuántos inmigrantes han llegado hoy a España en pateras y cayucos: última jornada registrada, últimos 7 días y acumulado oficial del año, con las fuentes de cada cifra.",
     "panel": ""},
    {"slug": "canarias", "zones": CAN, "keys": ["canarias"], "name": "Canarias",
     "title": "Llegadas de cayucos a Canarias hoy: cifras día a día · Migrometer",
     "h1": "Llegadas de cayucos a Canarias hoy",
     "desc": "Cayucos y personas llegadas a Canarias, isla por isla (El Hierro, Tenerife, Gran Canaria, Lanzarote…): última llegada, últimos 7 días y datos oficiales del año, con fuentes.",
     "panel": "?zona=canarias"},
    {"slug": "ceuta", "zones": {"ceuta"}, "keys": ["ceuta_mar", "ceuta_tierra"], "name": "Ceuta",
     "title": "Inmigrantes llegados a Ceuta hoy: cifras del año · Migrometer",
     "h1": "Inmigrantes llegados a Ceuta",
     "desc": "Entradas irregulares en Ceuta por mar, a nado y por el espigón: última entrada registrada, últimos 7 días y acumulado oficial del año, con fuentes.",
     "panel": "?zona=ceuta"},
    {"slug": "melilla", "zones": {"melilla"}, "keys": ["melilla_mar", "melilla_tierra"], "name": "Melilla",
     "title": "Inmigrantes llegados a Melilla hoy: cifras del año · Migrometer",
     "h1": "Inmigrantes llegados a Melilla",
     "desc": "Entradas irregulares en Melilla por mar y por la valla: última entrada registrada, últimos 7 días y acumulado oficial del año, con fuentes.",
     "panel": "?zona=melilla"},
    {"slug": "baleares", "zones": BAL, "keys": ["baleares"], "name": "Baleares",
     "title": "Pateras llegadas a Baleares hoy: cifras día a día · Migrometer",
     "h1": "Pateras llegadas a Baleares",
     "desc": "Pateras y personas llegadas a Baleares (Formentera, Cabrera, Mallorca, Ibiza, Menorca): última llegada, últimos 7 días y datos oficiales del año, con fuentes.",
     "panel": "?zona=peninsula"},
    {"slug": "peninsula", "zones": PEN, "keys": ["peninsula"], "name": "la península",
     "title": "Pateras llegadas hoy a la península: Almería, Murcia, Alicante · Migrometer",
     "h1": "Pateras llegadas a la península",
     "desc": "Pateras llegadas a Almería, Granada, Málaga, Cádiz, Huelva, Murcia, Alicante y Valencia: última llegada, últimos 7 días y datos oficiales del año, con fuentes.",
     "panel": "?zona=peninsula"},
]

CSS = """:root{--bg:#F3F3F1;--surface:#fff;--fg:#111;--fg2:#56565C;--fg3:#8A8A90;--line:rgba(17,17,17,.08);--coral:#FF5A4E;--teal:#0E7C7B;--teal2:#2EC4B6}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--fg);font:15px/1.55 Inter,-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,Helvetica,Arial,sans-serif;-webkit-font-smoothing:antialiased}
a{color:var(--teal)}.wrap{max-width:1040px;margin:0 auto;padding:0 20px}
.top{background:radial-gradient(60% 120% at 100% 0%,rgba(255,90,78,.22),transparent 60%),radial-gradient(50% 120% at 0% 100%,rgba(46,196,182,.2),transparent 60%),#0B0C12;color:#fff;padding:18px 0 34px}
.nav{display:flex;align-items:center;gap:10px;flex-wrap:wrap}.brand{display:inline-flex;align-items:center;gap:10px;color:#fff;text-decoration:none;font-weight:800;font-size:19px;letter-spacing:-.03em}
.brand svg{width:32px;height:32px}.nav .links{margin-left:auto;display:flex;gap:4px;flex-wrap:wrap}.nav .links a{color:#fff;text-decoration:none;font-size:13.5px;font-weight:600;padding:6px 10px;border-radius:999px}.nav .links a:hover,.nav .links a.on{background:rgba(255,255,255,.14)}
.crumbs{font-size:12.5px;color:rgba(255,255,255,.7);margin:26px 0 6px}.crumbs a{color:rgba(255,255,255,.85)}
h1{font-size:clamp(30px,5vw,48px);line-height:1.05;letter-spacing:-.035em;margin:0 0 10px}.lead{margin:0;color:rgba(255,255,255,.86);font-size:16px;max-width:70ch}
.big{display:flex;flex-wrap:wrap;gap:12px;margin-top:22px}.stat{background:rgba(255,255,255,.08);border:1px solid rgba(255,255,255,.14);border-radius:18px;padding:14px 18px;min-width:180px;flex:1}
.stat b{display:block;font-size:30px;letter-spacing:-.03em;line-height:1.1}.stat small{color:rgba(255,255,255,.75);font-size:12.5px}.stat .k{font-size:11px;font-weight:700;letter-spacing:.08em;text-transform:uppercase;color:rgba(255,255,255,.65)}
.stat.off b{color:#5EEAD4}.stat.press b{color:#FF9A90}
main{padding:26px 0 40px;display:grid;gap:18px}main>*{min-width:0}td.d{white-space:nowrap}
@media (max-width:640px){th:nth-child(4),td:nth-child(4){display:none}td,th{padding:8px 6px}.top{padding-bottom:26px}.nav .links{margin-left:0;width:100%}}.card{background:var(--surface);border:1px solid var(--line);border-radius:20px;padding:20px 22px}
h2{font-size:20px;letter-spacing:-.02em;margin:0 0 10px}p{margin:0 0 8px}.muted{color:var(--fg3)}.small{font-size:12.5px;color:var(--fg2)}
table{width:100%;border-collapse:collapse;font-size:14px}th{font-size:11px;text-transform:uppercase;letter-spacing:.06em;color:var(--fg3);text-align:left;padding:8px;border-bottom:1px solid var(--line)}
td{padding:9px 8px;border-bottom:1px solid var(--line);vertical-align:top}td.n{text-align:right;font-weight:700;white-space:nowrap}tr:last-child td{border-bottom:0}.tw{overflow-x:auto}
.tag{display:inline-block;font-size:10.5px;font-weight:700;letter-spacing:.06em;text-transform:uppercase;padding:2px 7px;border-radius:999px;margin-right:6px;vertical-align:2px}
.tag.p{background:rgba(255,90,78,.12);color:#D8392E}.tag.o{background:var(--teal);color:#fff}.tag.a{background:rgba(255,159,10,.15);color:#B26A00}
details{border-top:1px solid var(--line);padding:10px 0}details:last-child{border-bottom:1px solid var(--line)}summary{cursor:pointer;font-weight:600}details p{margin-top:8px;color:var(--fg2)}
.cta{display:inline-flex;align-items:center;gap:8px;background:#111;color:#fff;text-decoration:none;font-weight:700;padding:12px 18px;border-radius:999px}.cta:hover{background:#000}
.zones{display:flex;flex-wrap:wrap;gap:8px}.zones a{background:var(--surface);border:1px solid var(--line);border-radius:999px;padding:7px 13px;text-decoration:none;color:var(--fg);font-weight:600;font-size:13.5px}
footer{padding:0 0 40px;color:var(--fg3);font-size:12px}
@media (prefers-color-scheme:dark){:root{--bg:#0B0B0D;--surface:#17171A;--fg:#F4F4F5;--fg2:#A6A6AD;--fg3:#7D7D85;--line:rgba(255,255,255,.08)}a{color:#2EC4B6}.cta{background:#fff;color:#111}}
"""


def fmt(n, dec=0):
    if n is None: return "—"
    neg = n < 0; n = abs(n)
    r = float(round(n)) if n >= 100 else round(n, 1)  # totales de personas: sin decimales
    i, _, dd = f"{r:.1f}".partition(".")
    i = f"{int(i):,}".replace(",", ".")
    s = i + ("," + dd if dd and dd != "0" else "")
    return ("−" if neg else "") + s


MES = ["enero", "febrero", "marzo", "abril", "mayo", "junio", "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre"]
DIAS = ["lunes", "martes", "miércoles", "jueves", "viernes", "sábado", "domingo"]
def dl(d): y, m, dd = d.split("-"); return f"{int(dd)} de {MES[int(m)-1]} de {y}"
def ds(d): y, m, dd = d.split("-"); return f"{int(dd)} de {MES[int(m)-1]}"
MS = ["ene","feb","mar","abr","may","jun","jul","ago","sep","oct","nov","dic"]
def dsh(d): y, m, dd = d.split("-"); return f"{int(dd)} {MS[int(m)-1]} {y}"
def dw(d): return DIAS[date.fromisoformat(d).weekday()] + " " + dl(d)
def medium(s): s = str(s or "").strip(); i = s.find(" ("); return s[:i].strip() if i > 0 else s


def build(docs, evs, off, upd, last, logo_svg):
    """evs: eventos ya preparados por seo.prep (con _p, _ex, _reps). Devuelve [(ruta, lastmod)]."""
    out = []
    latest = off[-1] if off else None
    for pg in PAGES:
        zs = pg["zones"]
        ze = [e for e in evs if (zs is None or e.get("zone") in zs) and e["_p"] is not None]
        ze.sort(key=lambda e: (e["date"], e.get("time") or ""), reverse=True)
        b = last; a7 = (date.fromisoformat(b) - timedelta(days=6)).isoformat()
        wk = [e for e in ze if a7 <= e["date"] <= b]
        tot7 = sum(e["_p"] for e in wk)
        today = [e for e in ze if e["date"] == b]
        yest = (date.fromisoformat(b) - timedelta(days=1)).isoformat()
        tday = sum(e["_p"] for e in today); yday = sum(e["_p"] for e in ze if e["date"] == yest)
        # Oficial
        ov = op = None; orep = None
        if latest:
            rows = {r["key"]: r for r in latest.get("rows", [])}
            if pg["keys"] is None:
                ov, op = latest["total"]["v"], latest["total"].get("prev")
            else:
                vs = [rows.get(k) for k in pg["keys"]]
                if all(vs):
                    ov = sum(r["v"] for r in vs); op = sum((r.get("prev") or 0) for r in vs) if all(r.get("prev") is not None for r in vs) else None
            orep = latest
        pct = ((ov - op) / op * 100) if (ov is not None and op) else None
        yr = latest["to"][:4] if latest else b[:4]
        # Por lugar (7 días)
        byz = {}
        for e in wk: byz[e["zone"]] = byz.get(e["zone"], 0) + e["_p"]
        # Textos
        name = pg["name"]
        if today:
            lead = f"Según la prensa, el {dw(b)} (último día revisado) llegaron {fmt(tday)} personas a {name if name != 'España' else 'España'} en {len(today)} {'llegada registrada' if len(today)==1 else 'llegadas registradas'}."
        else:
            lead = f"Sin llegadas registradas en la prensa el {dw(b)} (último día revisado) en {name}."
        if wk: lead += f" En los últimos 7 días, del {ds(a7)} al {ds(b)}: {fmt(tot7)} personas."
        stats = [
            ("press", "Último día revisado · prensa", fmt(tday) if today else "0", ds(b) + (" · sin llegadas registradas" if not today else f" · {len(today)} {'llegada' if len(today)==1 else 'llegadas'}")),
            ("press", "Últimos 7 días · prensa", fmt(tot7) if wk else "Sin datos", f"del {ds(a7)} al {ds(b)}"),
            ("off", f"Año {yr} · Interior", fmt(ov) if ov is not None else "Sin datos", (f"del 1 ene al {ds(orep['to'])}" + (f" · {'+' if pct>=0 else '−'}{fmt(abs(pct))} % vs {int(yr)-1}" if pct is not None else "")) if orep and ov is not None else "Sin cifra oficial"),
        ]
        # Tabla últimas llegadas
        rows_html = ""
        for e in ze[:15]:
            srcs = []
            for r in e["_reps"]:
                u = r.get("url") or ""
                nm = esc(medium(r.get("source")) or "Fuente")
                srcs.append(f'<a href="{esc(u)}" rel="nofollow noopener" target="_blank">{nm}</a>' if u.startswith("https://") else nm)
            boats = [r.get("boats") for r in e["_reps"] if isinstance(r.get("boats"), (int, float))]
            btype = e.get("boatType") or ""
            nb = (sum(boats) / len(boats)) if boats else None
            PL = {"cayuco": "cayucos", "patera": "pateras", "neumática": "neumáticas", "lancha": "lanchas", "embarcación": "embarcaciones", "otro": "otros"}
            if nb is not None and btype in PL and nb != 1: btype = PL[btype]
            bt = (fmt(nb) + " " if nb is not None and btype not in ("a nado", "valla terrestre") else "") + esc(btype)
            approx = ' <span class="tag a">aprox.</span>' if e.get("approx") else ""
            rows_html += (f'<tr><td class="d">{esc(dsh(e["date"]))}</td><td>{esc(ZN.get(e["zone"], e["zone"]))}</td>'
                          f'<td class="n">{"≈ " if e.get("approx") else ""}{fmt(e["_p"])}{approx}</td><td>{bt}</td><td>{", ".join(srcs)}</td></tr>')
        last_e = ze[0] if ze else None
        # FAQ
        faq = []
        if last_e:
            faq.append((f"¿Cuándo fue la última llegada registrada a {name}?",
                        f"El {dl(last_e['date'])}, en {ZN.get(last_e['zone'], last_e['zone'])}: {fmt(last_e['_p'])} personas según la prensa ({', '.join(sorted({medium(r.get('source')) for r in last_e['_reps']}))})."))
        faq.append((f"¿Cuántas personas han llegado a {name} en los últimos 7 días?",
                     (f"Según las noticias registradas, {fmt(tot7)} personas del {ds(a7)} al {dl(b)}." if wk else f"No hay llegadas registradas en la prensa del {ds(a7)} al {dl(b)}.")
                     + " Cuando varios medios dan cifras distintas para una misma llegada se usa la media."))
        if ov is not None:
            faq.append((f"¿Cuántas personas han llegado a {name} en {yr} según el Ministerio del Interior?",
                        f"{fmt(ov)} personas del 1 de enero al {dl(orep['to'])}" + (f", un {fmt(abs(pct))} % {'más' if pct>=0 else 'menos'} que en el mismo periodo de {int(yr)-1} ({fmt(op)})" if pct is not None else "") + ". Interior publica el acumulado cada quincena; es una cifra provisional."))
        faq.append(("¿Por qué no coinciden la prensa y los datos oficiales?",
                    "Interior publica acumulados cada quincena y la prensa informa día a día de las llegadas que conoce. Migrometer muestra las dos fuentes por separado y nunca las suma."))
        bylist = "".join(f'<tr><td>{esc(ZN.get(z, z))}</td><td class="n">{fmt(v)}</td></tr>' for z, v in sorted(byz.items(), key=lambda x: -x[1]))
        AC = ' aria-current="page"'
        links = "".join('<a href="' + SITE + p["slug"] + '/"' + (AC if p is pg else "") + '>' + esc(p["h1"].replace("Inmigrantes llegados hoy a España", "Hoy en España")) + '</a>' for p in PAGES)
        SHORT = {"hoy": "Hoy", "canarias": "Canarias", "ceuta": "Ceuta", "melilla": "Melilla", "baleares": "Baleares", "peninsula": "Península"}
        navl = "".join('<a href="' + SITE + p["slug"] + '/"' + (' class="on"' if p is pg else "") + '>' + esc(SHORT[p["slug"]]) + '</a>' for p in PAGES)
        ld = [{"@context": "https://schema.org", "@type": "WebPage", "name": pg["title"], "url": f"{SITE}{pg['slug']}/", "inLanguage": "es-ES", "dateModified": upd, "description": pg["desc"],
               "isPartOf": {"@type": "WebSite", "name": "Migrometer", "url": SITE}},
              {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
                  {"@type": "ListItem", "position": 1, "name": "Migrometer", "item": SITE},
                  {"@type": "ListItem", "position": 2, "name": pg["h1"], "item": f"{SITE}{pg['slug']}/"}]},
              {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": t}} for q, t in faq]}]
        ldj = json.dumps(ld, ensure_ascii=False).replace("</", "<\\/")
        page = f"""<!doctype html>
<html lang="es"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{esc(pg['title'])}</title>
<meta name="description" content="{esc(pg['desc'])}">
<link rel="canonical" href="{SITE}{pg['slug']}/">
<meta name="robots" content="index,follow,max-image-preview:large,max-snippet:-1">
<meta property="og:type" content="article"><meta property="og:site_name" content="Migrometer"><meta property="og:locale" content="es_ES">
<meta property="og:url" content="{SITE}{pg['slug']}/"><meta property="og:title" content="{esc(pg['title'])}"><meta property="og:description" content="{esc(pg['desc'])}">
<meta property="og:image" content="{SITE}og.png"><meta name="twitter:card" content="summary_large_image">
<meta property="article:modified_time" content="{esc(upd)}">
<meta name="theme-color" content="#0B0C12"><link rel="icon" href="../favicon.svg" type="image/svg+xml"><link rel="apple-touch-icon" href="../apple-touch-icon.png">
<script type="application/ld+json">{ldj}</script>
<style>{CSS}</style></head><body>
<header class="top"><div class="wrap">
<div class="nav"><a class="brand" href="{SITE}" aria-label="Migrometer, ir al panel">{logo_svg}<span>Migrometer</span></a>
<nav class="links" aria-label="Zonas">{navl}</nav></div>
<div class="crumbs"><a href="{SITE}">Migrometer</a> › {esc(pg['h1'])}</div>
<h1>{esc(pg['h1'])}</h1>
<p class="lead">{esc(lead)}</p>
<div class="big">{"".join(f'<div class="stat {c}"><span class="k">{esc(k)}</span><b>{esc(v)}</b><small>{esc(s)}</small></div>' for c, k, v, s in stats)}</div>
</div></header>
<main class="wrap">
<section class="card"><h2>Últimas llegadas registradas en {esc(name)}</h2>
{'<div class="tw"><table><thead><tr><th>Fecha</th><th>Lugar</th><th style="text-align:right">Personas</th><th>Embarcaciones</th><th>Fuentes</th></tr></thead><tbody>' + rows_html + '</tbody></table></div>' if rows_html else '<p class="muted">Sin datos reportados.</p>'}
<p class="small"><span class="tag p">Prensa</span>Cifras de noticias de televisiones, periódicos y agencias. Si varios medios difieren se usa la media; cada noticia cuenta una vez.</p></section>
{('<section class="card"><h2>Últimos 7 días por lugar</h2><div class="tw"><table><tbody>' + bylist + '</tbody></table></div></section>') if bylist else ''}
<section class="card"><h2>Datos oficiales de {yr}</h2>
{(f'<p><span class="tag o">Oficial</span>Según el último informe quincenal del Ministerio del Interior, del 1 de enero al {esc(dl(orep["to"]))} llegaron a {esc(name)} <b>{fmt(ov)}</b> personas' + (f', un {fmt(abs(pct))} % {"más" if pct>=0 else "menos"} que en el mismo periodo de {int(yr)-1} ({fmt(op)})' if pct is not None else '') + '.</p>' + (f'<p class="small">Fuente: <a href="{esc(orep.get("url",""))}" rel="nofollow noopener" target="_blank">Ministerio del Interior, informe quincenal a {esc(dl(orep["to"]))}</a>. Las cifras oficiales y las de prensa se muestran por separado y nunca se suman.</p>' if str(orep.get("url","")).startswith("https://") else '')) if ov is not None else '<p class="muted">Sin cifra oficial.</p>'}
</section>
<section class="card"><h2>Preguntas frecuentes</h2>{"".join(f'<details><summary>{esc(q)}</summary><p>{esc(t)}</p></details>' for q, t in faq)}</section>
<section><a class="cta" href="{SITE}{pg['panel']}">Ver el panel completo: mapa, ritmo y simulador →</a></section>
<section><h2>Otras zonas</h2><div class="zones">{links}</div></section>
</main>
<footer class="wrap">Actualizado el {esc(dl(upd[:10]))}. Datos de prensa con enlace a cada noticia y de los informes quincenales del Ministerio del Interior. Sitio personal, informativo y sin ánimo de lucro. <a href="{SITE}#metodologia">Metodología</a> · <a href="{SITE}#aviso-legal">Aviso legal</a></footer>
</body></html>
"""
        d = os.path.join(docs, pg["slug"]); os.makedirs(d, exist_ok=True)
        open(os.path.join(d, "index.html"), "w", encoding="utf8").write(page)
        out.append((f"{SITE}{pg['slug']}/", upd[:10]))
    return out
