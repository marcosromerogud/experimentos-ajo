#!/usr/bin/env python3
"""
Extrae todos los enlaces de recursos (imagenes, pdf, svg, gif, etc.) de los
archivos HTML dentro de la carpeta bitacora/.

- Detecta URLs absolutas (https://www.viabcp.com/...) y relativas (/wcm/...).
- A las relativas les antepone el dominio https://www.viabcp.com.
- Decodifica entidades HTML (&amp; -> &).
- Deduplica y agrupa por extension.
- Genera un JSON con el resultado.

Uso:  python3 extraer_recursos.py
"""

import os
import re
import json
import html
from collections import defaultdict

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DOMINIO = "https://www.viabcp.com"
SALIDA = os.path.join(BASE_DIR, "enlaces-recursos.json")

# Extensiones que consideramos "recursos"
EXTENSIONES = ("png", "jpg", "jpeg", "gif", "svg", "webp", "pdf", "ico",
               "woff", "woff2", "mp4", "webm", "js")
EXT_RE = "|".join(EXTENSIONES)

# 1) URLs absolutas a viabcp (o cualquier http) que sean recurso por extension
RE_ABSOLUTA = re.compile(
    r'https?://[^\s"\'()<>]+?\.(?:' + EXT_RE + r')(?:\?[^\s"\'()<>]*)?',
    re.IGNORECASE,
)
# 2) Rutas relativas dentro de atributos src/href o url() que sean recurso por extension
RE_RELATIVA = re.compile(
    r'(?:(?:src|href)\s*=\s*["\']|url\(\s*["\']?)'
    r'(/[^\s"\'()<>]+?\.(?:' + EXT_RE + r')(?:\?[^\s"\'()<>]*)?)',
    re.IGNORECASE,
)
# 3) CATCH-ALL: cualquier ruta /wcm/(my)connect/... (abs o rel) TENGA O NO extension.
#    Asi no perdemos recursos servidos sin extension en la URL.
RE_WCM = re.compile(
    r'(?:https?://[^\s"\'()<>]*?)?/wcm/(?:my)?connect/[^\s"\'()<>]+',
    re.IGNORECASE,
)


def limpiar(url: str) -> str:
    url = html.unescape(url.strip())
    # quitar comillas o parentesis residuales al final
    url = url.rstrip('"\').,;')
    return url


# Dominios absolutos que SI aceptamos. Todo lo demas (gstatic, google, latam,
# yoando, cineplanet, w3.org, etc.) se ignora.
#   - cualquier subdominio de viabcp.com  (incl. www.mitarjetabcp.viabcp.com)
#   - cualquier host que contenga "preprodportal"
DOMINIOS_OK = re.compile(r'^https?://[^/]*(?:viabcp\.com|preprodportal)', re.IGNORECASE)


def dominio_permitido(url: str) -> bool:
    """True si es relativo (se volvera viabcp) o si su host esta permitido."""
    if url.startswith("/"):
        return True
    return bool(DOMINIOS_OK.match(url))


def normalizar(url: str) -> str:
    url = limpiar(url)
    if url.startswith("http"):
        return url
    if url.startswith("/"):
        return DOMINIO + url
    return DOMINIO + "/" + url


def extension_de(url: str) -> str:
    # se fija en el pathname (antes del ?) para no confundirse con la query
    ruta = url.split("?", 1)[0]
    m = re.search(r'\.(' + EXT_RE + r')$', ruta, re.IGNORECASE)
    return m.group(1).lower() if m else "sin-extension"


def main():
    archivos = []
    for raiz, _, ficheros in os.walk(BASE_DIR):
        for f in ficheros:
            if f.lower().endswith((".html", ".htm")):
                archivos.append(os.path.join(raiz, f))
    archivos.sort()

    # url -> set de archivos donde aparece
    ocurrencias = defaultdict(set)

    for ruta in archivos:
        rel = os.path.relpath(ruta, BASE_DIR)
        try:
            with open(ruta, encoding="utf-8", errors="ignore") as fh:
                contenido = fh.read()
        except Exception as e:
            print(f"  ! No se pudo leer {rel}: {e}")
            continue

        encontrados = set()
        crudos = set()
        for m in RE_ABSOLUTA.finditer(contenido):
            crudos.add(m.group(0))
        for m in RE_RELATIVA.finditer(contenido):
            crudos.add(m.group(1))
        for m in RE_WCM.finditer(contenido):
            crudos.add(m.group(0))
        for raw in crudos:
            raw = limpiar(raw)
            if dominio_permitido(raw):          # descarta absolutos de otros dominios
                encontrados.add(normalizar(raw))

        for u in encontrados:
            ocurrencias[u].add(rel)

    # Agrupar por extension
    por_extension = defaultdict(list)
    for url in sorted(ocurrencias):
        por_extension[extension_de(url)].append(url)

    resumen = {ext: len(v) for ext, v in sorted(por_extension.items())}

    # Un recurso queda "en duda" si NO vive en /wcm/ (p.ej. las fuentes .woff
    # de /ViaBCPThemeLight/). Son recursos del sitio pero no del gestor wcm.
    def en_duda(url: str) -> bool:
        return "/wcm/" not in url.lower()

    en_duda_urls = sorted(u for u in ocurrencias if en_duda(u))

    resultado = {
        "dominio_base": DOMINIO,
        "total_unicos": len(ocurrencias),
        "total_confiables": len(ocurrencias) - len(en_duda_urls),
        "total_en_duda": len(en_duda_urls),
        "resumen_por_extension": resumen,
        "por_extension": {ext: por_extension[ext] for ext in sorted(por_extension)},
        "en_duda": en_duda_urls,
        "recursos": [
            {
                "url": url,
                "extension": extension_de(url),
                "en_duda": en_duda(url),
                "archivos": sorted(ocurrencias[url]),
            }
            for url in sorted(ocurrencias)
        ],
    }

    with open(SALIDA, "w", encoding="utf-8") as fh:
        json.dump(resultado, fh, ensure_ascii=False, indent=2)

    print(f"Archivos HTML analizados: {len(archivos)}")
    print(f"Recursos unicos: {len(ocurrencias)}")
    print("Por extension:")
    for ext, n in resumen.items():
        print(f"  {ext:6} {n}")
    print(f"En duda (fuera de /wcm/): {len(en_duda_urls)}")
    print(f"\nJSON generado en: {SALIDA}")


if __name__ == "__main__":
    main()
