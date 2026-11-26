#!/usr/bin/env python3
"""Migrometer · SEO/GEO estático.
Lee docs/data.json y escribe, sin inventar nada (solo cifras del propio data.json):
  - docs/index.html: bloques <!--SEO:JSONLD-->…<!--/SEO:JSONLD--> (head) y <!--SEO:FACTS-->…<!--/SEO:FACTS--> (texto visible)
  - docs/llms.txt, docs/sitemap.xml, docs/robots.txt
Uso: python3 tools/seo.py [carpeta_docs]   (por defecto ../docs respecto a este archivo)
Solo usa la biblioteca estándar de Python."""
import json, os, re, sys, unicodedata, html
from datetime import date, datetime, timedelta
from urllib.parse import urlparse

SITE = "https://migrometer.es/"
HERE = os.path.dirname(os.path.abspath(__file__))
DOCS = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, '..', 'docs')
MES = ["enero","febrero","marzo","abril","mayo","junio","julio","agosto","septiembre","octubre","noviembre","diciembre"]
CAN = {"el-hierro","la-palma","la-gomera","tenerife","gran-canaria","fuerteventura","lanzarote","canarias"}
BAL = {"formentera","ibiza","cabrera","mallorca","menorca","baleares"}
def group(z):
    return "canarias" if z in CAN else z if z in ("ceuta","melilla") else "peninsula"
def norm(s):
    return unicodedata.normalize("NFD", str(s or "").lower()).encode("ascii","ignore").decode()
def medium(s):
    s = str(s or "").strip(); i = s.find(" (")
    return s[:i].strip() if i > 0 else s
def nurl(u):
    try:
        p = urlparse(u or "")
        if not p.netloc: return ""
        return (re.sub(r"^www\.", "", p.netloc) + re.sub(r"/amp/?$|/$", "", p.path)).lower()
    except Exception: return ""
def fmt(n, dec=0):
    if n is None: return "—"
    neg = n < 0; n = abs(n)
    if dec:
        s = f"{round(n, dec):,.{dec}f}".replace(",", "X").replace(".", ",").replace("X", ".")
        s = re.sub(r",0+$", "", s)
    else:
        s = f"{round(n):,}".replace(",", ".")
    return ("−" if neg else "") + s
def dlong(d):
    y, m, dd = d.split("-"); return f"{int(dd)} de {MES[int(m)-1]} de {y}"
def dshort(d):
    y, m, dd = d.split("-"); return f"{int(dd)} de {MES[int(m)-1]}"
def pct(a, b):
    return None if not b else (a - b) / b * 100

def prep(events):
    for e in events:
        by = []
        for r in e.get("reports") or []:
            u, m = nurl(r.get("url")), norm(medium(r.get("source")))
            by = [x for x in by if not ((u and x[0] == u) or x[1] == m)]
            by.append((u, m, r))
        e["_reps"] = [x[2] for x in by]; e["_ex"] = False
    def cnts(e):
        out = []
        for r in e["_reps"]:
            try:
                v = float(r.get("count"))
                if v >= 0: out.append(v)
            except (TypeError, ValueError): pass
        return out
    srt = sorted(events, key=lambda e: (e.get("createdAt") or "", e.get("id") or ""))
    for i, e in enumerate(srt):
        if e["_ex"]: continue
        for f in srt[i+1:]:
            if f["_ex"] or f.get("date") != e.get("date") or group(f.get("zone")) != group(e.get("zone")): continue
            same = any(nurl(r.get("url")) and any(nurl(q.get("url")) == nurl(r.get("url")) and str(q.get("count")) == str(r.get("count")) for q in e["_reps"]) for r in f["_reps"])
            same2 = f.get("zone") == e.get("zone") and f["_reps"] and all(any(norm(medium(q.get("source"))) == norm(medium(r.get("source"))) and str(q.get("count")) == str(r.get("count")) for q in e["_reps"]) for r in f["_reps"])
            if same or same2: f["_ex"] = True
    for e in events:
        z = e.get("zone")
        if e["_ex"] or z not in ("canarias", "baleares"): continue
        isl = (CAN - {"canarias"}) if z == "canarias" else (BAL - {"baleares"})
        if any((not f["_ex"]) and f.get("date") == e.get("date") and f.get("zone") in isl for f in events): e["_ex"] = True
    for e in events:
        c = cnts(e); e["_p"] = None if e["_ex"] or not c else sum(c) / len(c)
    return events

def main():
    d = json.load(open(os.path.join(DOCS, "data.json"), encoding="utf8"))
    evs = prep(list(d.get("events") or []))
    off = sorted([o for o in d.get("official") or [] if o.get("to")], key=lambda o: o["to"])
    upd = d.get("updatedAt") or datetime.now().isoformat()
    upd_d = upd[:10]
    last = d.get("lastSweepDate") or (max((e["date"] for e in evs), default=upd_d))
    facts, faq = [], []
    # Oficial
    if off:
        o = off[-1]; yr = o["to"][:4]
        tv, tp = o["total"]["v"], o["total"].get("prev")
        rows = {r["key"]: r for r in o.get("rows", [])}
        def rv(*ks, f="v"):
            vs = [rows[k].get(f) for k in ks if k in rows]
            return sum(v for v in vs if v is not None) if vs and all(v is not None for v in vs) else None
        can, cp = rv("canarias"), rv("canarias", f="prev")
        ceu, mel = rv("ceuta_mar", "ceuta_tierra"), rv("melilla_mar", "melilla_tierra")
        pen, bal = rv("peninsula"), rv("baleares")
        p = pct(tv, tp)
        s1 = (f"Según el último informe quincenal del Ministerio del Interior, del 1 de enero al {dlong(o['to'])} llegaron de forma irregular a España "
              f"{fmt(tv)} personas" + (f", un {fmt(abs(p),1)} % {'más' if p >= 0 else 'menos'} que en el mismo periodo de {int(yr)-1} ({fmt(tp)})" if p is not None else "") + ".")
        parts = []
        if can is not None: parts.append(f"Canarias, {fmt(can)}" + (f" ({'+' if pct(can,cp)>=0 else '−'}{fmt(abs(pct(can,cp)),1)} %)" if cp else ""))
        if ceu is not None: parts.append(f"Ceuta, {fmt(ceu)} (por mar y por tierra)")
        if mel is not None: parts.append(f"Melilla, {fmt(mel)} (por mar y por tierra)")
        if pen is not None: parts.append(f"península, {fmt(pen)} por vía marítima")
        if bal is not None: parts.append(f"Baleares, {fmt(bal)}")
        s2 = ("Por zonas: " + "; ".join(parts) + ".") if parts else ""
        facts += [s1, s2]
        faq.append((f"¿Cuántos inmigrantes irregulares han llegado a España en {yr}?", s1 + " Interior publica el acumulado cada quincena; es una cifra provisional."))
        if can is not None:
            faq.append((f"¿Cuántas personas han llegado a Canarias en {yr}?", f"Según Interior, {fmt(can)} personas llegaron a Canarias por vía marítima del 1 de enero al {dlong(o['to'])}" + (f", frente a {fmt(cp)} en el mismo periodo de {int(yr)-1}." if cp else ".")))
        if ceu is not None and mel is not None:
            faq.append((f"¿Cuántas personas han entrado en Ceuta y Melilla en {yr}?", f"Según Interior, del 1 de enero al {dlong(o['to'])}: Ceuta, {fmt(ceu)} y Melilla, {fmt(mel)}, sumando las entradas por mar y por tierra."))
        off_src = (o.get("source") or "Ministerio del Interior", o.get("url") or "")
    else:
        off_src = None
    # Prensa: últimos 7 días con barrido
    b = last; a = (date.fromisoformat(b) - timedelta(days=6)).isoformat()
    wk = [e for e in evs if a <= e.get("date", "") <= b and e["_p"]]
    if wk:
        tot = sum(e["_p"] for e in wk)
        byd = {}
        for e in wk: byd[e["date"]] = byd.get(e["date"], 0) + e["_p"]
        top = max(byd.items(), key=lambda x: x[1])
        med = sorted({medium(r.get("source")) for e in wk for r in e["_reps"]})
        s3 = (f"Según las noticias de prensa y televisión registradas, del {dshort(a)} al {dlong(b)} llegaron {fmt(tot)} personas en {len(wk)} llegadas registradas; "
              f"el día con más llegadas fue el {dshort(top[0])} ({fmt(top[1])}). Medios citados: {', '.join(med[:8])}{' y otros' if len(med) > 8 else ''}.")
        facts.append(s3)
        faq.append(("¿Cuántos inmigrantes han llegado a España esta semana?", s3 + " Cuando varios medios dan cifras distintas para una misma llegada se usa la media, y cada noticia cuenta una sola vez."))
    faq.append(("¿De dónde salen los datos de Migrometer?", "De dos fuentes que se muestran por separado y nunca se suman: las noticias de televisiones, periódicos y agencias (cada cifra enlaza a su noticia) y los informes quincenales de inmigración irregular del Ministerio del Interior. La población de comparación es la del padrón del INE a 1 de enero de 2025."))
    faq.append(("¿Por qué no coinciden las cifras de prensa y las oficiales?", "Interior solo publica acumulados cada quincena y la prensa informa día a día de las llegadas que conoce; no todas las llegadas salen en las noticias y algunas cifras de prensa son provisionales. Por eso Migrometer las compara, pero no las mezcla."))
    facts = [f for f in facts if f]
    # Bloque visible
    esc = html.escape
    vis = ('<h2>Datos clave</h2><p class="kf-upd">Actualizado el ' + esc(dlong(upd_d)) + '.</p>' +
           ''.join('<p>' + esc(f) + '</p>' for f in facts) +
           '<h2>Preguntas frecuentes</h2>' +
           ''.join('<details><summary>' + esc(q) + '</summary><p>' + esc(a_) + '</p></details>' for q, a_ in faq))
    # JSON-LD
    first = min((e["date"] for e in evs), default=upd_d)
    years = sorted({e["date"][:4] for e in evs} | {o["to"][:4] for o in off})
    ld = [
        {"@context": "https://schema.org", "@type": "WebSite", "name": "Migrometer", "url": SITE, "inLanguage": "es-ES",
         "description": "Llegadas irregulares de personas migrantes a España, día a día, según la prensa y según el Ministerio del Interior, por separado y con sus fuentes."},
        {"@context": "https://schema.org", "@type": "Dataset", "name": "Migrometer · llegadas irregulares a España",
         "description": "Registro diario de llegadas irregulares a España (Canarias, Ceuta, Melilla, península y Baleares) recopilado de noticias de prensa y televisión, con cada cifra enlazada a su fuente, junto a los informes quincenales del Ministerio del Interior. Las dos fuentes se publican por separado y no se suman.",
         "url": SITE, "inLanguage": "es-ES", "isAccessibleForFree": True, "dateModified": upd,
         "keywords": ["inmigración irregular", "llegadas de migrantes", "pateras", "cayucos", "Canarias", "Ceuta", "Melilla", "España", "Ministerio del Interior"] + years,
         "creator": {"@type": "Organization", "name": "Migrometer", "url": SITE},
         "temporalCoverage": f"{min(first, off[0]['from'] if off else first)}/{last}",
         "spatialCoverage": {"@type": "Place", "name": "España", "geo": {"@type": "GeoShape", "box": "27.6 -18.2 43.8 4.4"}},
         "variableMeasured": ["Personas llegadas según la prensa", "Personas llegadas según el Ministerio del Interior", "Fallecidos y desaparecidos según la prensa"],
         "isBasedOn": [x for x in [off_src and off_src[1]] if x],
         "distribution": [{"@type": "DataDownload", "encodingFormat": "application/json", "contentUrl": SITE + "data.json"}]},
        {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a_}} for q, a_ in faq]},
    ]
    jl = '<script type="application/ld+json">' + json.dumps(ld, ensure_ascii=False).replace("</", "<\\/") + '</script>'
    p = os.path.join(DOCS, "index.html"); h = open(p, encoding="utf8").read()
    h2 = re.sub(r"<!--SEO:JSONLD-->.*?<!--/SEO:JSONLD-->", lambda m: "<!--SEO:JSONLD-->" + jl + "<!--/SEO:JSONLD-->", h, flags=re.S)
    h2 = re.sub(r"<!--SEO:FACTS-->.*?<!--/SEO:FACTS-->", lambda m: "<!--SEO:FACTS-->" + vis + "<!--/SEO:FACTS-->", h2, flags=re.S)
    h2 = re.sub(r'(<meta property="article:modified_time" content=")[^"]*(")', lambda m: m.group(1) + upd + m.group(2), h2)
    if h2 != h: open(p, "w", encoding="utf8").write(h2)
    # llms.txt
    llms = ["# Migrometer", "",
            "> Llegadas irregulares de personas migrantes a España, día a día: según la prensa (noticias de televisiones, periódicos y agencias, con enlace a cada noticia) y según los informes quincenales del Ministerio del Interior. Las dos fuentes se muestran por separado y nunca se suman. Sitio personal, informativo y sin ánimo de lucro.", "",
            f"Actualizado: {dlong(upd_d)}.", ""] + ["- " + f for f in facts] + ["",
            "## Datos", f"- [Datos completos en JSON]({SITE}data.json): llegadas según la prensa (con fuentes, medias y discrepancias) e informes oficiales de Interior.",
            f"- [Panel visual]({SITE}): resumen, mapa, ritmo semanal, equivalencia en población, coste sanitario de referencia, perfil demográfico y medios.", "",
            "## Método", "- No se inventan cifras; las aproximadas («unos», «casi», «más de») no cuentan como exactas.",
            "- Una llegada contada por varios medios es un solo registro; si las cifras difieren se usa la media aritmética.",
            "- Las cifras oficiales de cada quincena son la diferencia entre dos informes consecutivos de Interior.", "",
            "## Preguntas frecuentes"] + [f"- **{q}** {a_}" for q, a_ in faq] + [""]
    open(os.path.join(DOCS, "llms.txt"), "w", encoding="utf8").write("\n".join(llms))
    open(os.path.join(DOCS, "sitemap.xml"), "w", encoding="utf8").write(
        '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        f'  <url><loc>{SITE}</loc><lastmod>{upd_d}</lastmod><changefreq>daily</changefreq><priority>1.0</priority></url>\n'
        f'  <url><loc>{SITE}llms.txt</loc><lastmod>{upd_d}</lastmod><changefreq>daily</changefreq><priority>0.3</priority></url>\n</urlset>\n')
    open(os.path.join(DOCS, "robots.txt"), "w", encoding="utf8").write(
        "# Migrometer: contenido público e informativo. Se permite el acceso a buscadores y asistentes de IA.\nUser-agent: *\nAllow: /\n\n"
        f"Sitemap: {SITE}sitemap.xml\n")
    print("SEO actualizado:", upd, "·", len(facts), "datos ·", len(faq), "preguntas")

if __name__ == "__main__":
    main()
