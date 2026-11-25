# Migrometer ES

Llegadas irregulares de personas migrantes a España según la **prensa** (televisiones, periódicos y agencias) y según el **Ministerio del Interior**, mostradas siempre por separado y con sus fuentes.

## Estructura

```
docs/                 Web pública estática (lo que se publica en el dominio)
  index.html          Página de solo lectura, sin formularios ni almacenamiento en el dispositivo
  data.json           Datos que lee la página (se sustituye cada noche)
  .nojekyll           Evita el procesado de Jekyll en GitHub Pages
panel/index.html      Panel de trabajo con entrada de datos (funciona dentro de claude.ai: usa su base de datos)
tools/
  build_public.py     Genera docs/index.html a partir de panel/index.html
  public_footer.html  Metodología y aviso legal de la web pública
  munis.txt           629 municipios de referencia del padrón del INE (1/1/2025): población|código INE|nombre
  official-*.json     Informes quincenales de Interior cargados (copias de referencia)
  mapgen/             Generación del mapa vectorial (Natural Earth, dominio público)
```

## Formato de `docs/data.json`

```json
{
  "updatedAt": "2026-11-25T23:15:00+01:00",
  "lastSweepDate": "2026-11-25",
  "events":   [ { "id", "date", "time", "zone", "boatType", "sm", "notes", "reports": [ { "source", "url", "count", "boats", "note", "stats" } ], "createdAt" } ],
  "official": [ { "source", "url", "from", "to", "provisional", "total", "maritime", "land", "rows": [ { "key", "label", "group", "v", "prev" } ] } ]
}
```

## Reglas de los datos

- No se inventa ni se estima ninguna cifra; las aproximadas («casi», «unos», «más de», «al menos») no cuentan.
- Varios medios sobre la misma llegada son un solo evento: se usa la media y se avisa de la discrepancia.
- Una misma noticia nunca suma dos veces (un report por medio y evento; misma URL = misma noticia; los totales genéricos que solapan con el detalle por islas no se suman).
- Las cifras oficiales y las de prensa nunca se suman.

## Publicar con GitHub Pages y dominio propio

1. Sube este repositorio a GitHub.
2. En **Settings → Pages**: *Deploy from a branch*, rama `main`, carpeta `/docs`.
3. Crea `docs/CNAME` con tu dominio (una sola línea, p. ej. `migrometer.es`) y configura el DNS en tu registrador:
   - dominio raíz: registros `A` hacia las IP de GitHub Pages que indica la documentación de GitHub;
   - subdominio `www`: registro `CNAME` hacia `TU-USUARIO.github.io`.
4. Activa **Enforce HTTPS** cuando GitHub lo permita.

## Actualización diaria

Una tarea programada hace el barrido de noticias cada noche, guarda los datos en el panel y genera un `data.json` nuevo. Para que llegue al dominio, la tarea escribe `docs/data.json` en la copia local del repositorio y hace `git commit` + `git push` con las credenciales de git del propio ordenador.

## Fuentes y licencias

- Población: INE, Cifras oficiales de población de los municipios españoles a 1 de enero de 2025 (Revisión del Padrón municipal). Reutilización conforme a la Ley 37/2007, citando la fuente.
- Datos oficiales de llegadas: Ministerio del Interior, informes quincenales sobre inmigración irregular.
- Mapa base: Natural Earth (dominio público).
- Gráficos: Chart.js (licencia MIT), cargado desde jsDelivr.
