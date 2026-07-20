# Contexto - Experimentos AJO

## Proyecto
Mailings HTML para Adobe Campaign (BCP - Crédito Hipotecario).

## Estructura de carpetas
- `mailings/` — fragmentos de email para Adobe Campaign (estilos inline, layout con tablas).
- `assets/` — iconos SVG usados en mailings.
- `landing/ajo/` — landing page completa de Crédito Hipotecario y script de experimento.
- `experimentos/csi/`, `experimentos/exp/` — experimentos A/B (control/piloto) para ViaBCP.
- `referencias/` — copias de páginas reales del sitio (campañas LATAM, legales TC) usadas como referencia.
- `herramientas/` — utilidades no relacionadas con BCP: extensión `target-qa-helper` y scripts de automatización de Mentimeter.
- `bitacora/` — histórico/archivo de experimentos y páginas capturadas (tc00xx, web/).
- `docs/` — este archivo de contexto.

## Archivos principales

### `mailings/ejemplo-vinetas.html`
Fragmento de email funcional con sección de 3 viñetas (ícono + texto).
- Contenido: Fondo MiVivienda, financiamiento hasta S/ 355,100, Bono de Buen Pagador
- Estilo: texto con negrita parcial (`font-weight:700`) + texto normal
- Íconos: círculo gris relleno

### `mailings/ejemplo-vinetas-me.html`
Nueva versión creada a partir de `ejemplo-vinetas.html` con diferente contenido.
- Contenido: 90% de financiamiento, alternativas de crédito, acompañamiento hipotecario
- Sin negritas
- Íconos: círculo con borde rosa (imágenes PNG diferentes)

## Problema detectado y resuelto

Al crear `ejemplo-vinetas-me.html` desde el original, se introdujeron atributos `class` incorrectos en las etiquetas `<img>`:

```html
<!-- MAL -->
<img alt src="..." style="width:72px;" class>
<img alt src="..." style="width:72px;" class="is-highlight">

<!-- BIEN -->
<img alt src="..." style="width:72px;">
```

**Causa:** El atributo `class="is-highlight"` podía estar activando estilos CSS del contexto de Adobe Campaign que rompían el layout.

**Solución:** Se quitaron todos los atributos `class` de las 3 imágenes en `ejemplo-vinetas-me.html`.

## Estructura HTML de las viñetas

Tabla de 3 columnas con `max-width:600px`, cada celda `<td>` con `width="168"` y `colspan="2"`:

```
[ícono]        [ícono]        [ícono]
 texto          texto          texto
```

## Notas
- Los estilos son inline (requerimiento de clientes de correo)
- Layout con tablas para compatibilidad con Outlook y otros clientes
- Imágenes alojadas en Adobe Campaign (`bcp-mid-stage13-res.adobe-campaign.com`)
- `line-height:0px` en `<td>` es un hack para evitar espacio extra bajo las imágenes
