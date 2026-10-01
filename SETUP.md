# SETUP — repo de perfil `ad1code/ad1code`

Este repo existe por una única razón: GitHub renderiza el `README.md` de un repo
**público** que se llame igual que el usuario en la cabecera del perfil.
Si el repo pasa a privado o cambia de nombre, el perfil deja de mostrarlo.

---

## 1. Cómo está montado el perfil

El README casi no tiene Markdown: son piezas SVG que generan dos scripts de `scripts/`.
El planteamiento sigue el de [`macu-dev/macu-dev`](https://github.com/macu-dev/macu-dev)
(ventana de editor, retrato tramado, tarjeta `whoami`, tabla de stack). El código es propio:
su repo no tiene licencia, así que no se copia nada de él.

| Pieza | Archivo | La genera |
|---|---|---|
| Banner animado, claro y oscuro | `assets/banner-{dark,light}.svg` | `python3 scripts/banner.py` |
| Tarjeta `whoami` con la red neuronal | `assets/whoami.svg` | `python3 scripts/cards.py` |
| Lenguajes | `assets/lenguajes.svg` | `python3 scripts/cards.py` |
| Logos del stack | `assets/tech/*.webp` | Copia de las pegatinas del portfolio (`public/tech/sticker/`) |

Para cambiar un texto, un color o un logo se edita el script y se vuelve a ejecutar.
Los SVG no se tocan a mano.

`banner.py` necesita Pillow y numpy. `cards.py`, solo Python.

---

## 2. El banner

**Qué hace.** Trama el retrato a 1 bit (Floyd-Steinberg) y lo dibuja con puntos. 700 partículas
salen de él y forman los logos de `LOGOS` (Claude, Python, React y Docker), cada uno en el color
de un proyecto; después vuelven al retrato. Sobre la cara, el recuadro de detección del hero.

**De dónde sale el retrato.** De `adicode-porfolio/public/alberto-sin-fondo.webp`. El original
no se guarda en este repo, que es público. Con otra foto:
`python3 scripts/banner.py ruta/al/retrato.png`. Si cambia el encuadre, hay que ajustar `CROP`
(el recorte) y `FACE` (dónde cae el recuadro).

**Qué se edita:** `YAML_ROWS` (el texto de `perfil.yml`), `LOGOS` y `THEMES`.

### Trampas

1. **Sin JavaScript ni recursos externos.** GitHub pinta los SVG como imagen: no carga fuentes
   ni imágenes de fuera y no ejecuta scripts. La animación es SMIL (`<animate>`), y el texto usa
   la fuente monoespaciada del sistema.
2. **El primer fotograma tiene que valer solo.** La app móvil de GitHub puede no animar.
   Por eso el retrato ya está dibujado en el segundo 0.
3. **Peso.** Cada partícula lleva su recorrido escrito: el banner pesa entre 0,7 y 1 MB. Subir
   `TRAVELLERS` o añadir logos lo engorda rápido.
4. **Caché de Camo.** GitHub cachea las imágenes. Si regeneras el banner y sigue saliendo el
   viejo, renombra el archivo (`banner-dark.v2.svg`) y actualiza el README.
5. **Nada de CSS en el Markdown.** GitHub elimina `<style>`, `class` y scripts. Solo sobreviven
   `align`, `width`, `height` y `srcset`.

### Actualizar los lenguajes

`assets/lenguajes.json` son los bytes por lenguaje de los repos propios, privados incluidos y
sin forks. Se actualiza con:

```bash
gh api graphql -f query='{viewer{repositories(first:100,ownerAffiliations:OWNER,isFork:false){nodes{languages(first:10,orderBy:{field:SIZE,direction:DESC}){edges{size node{name}}}}}}}' \
  --jq '[.data.viewer.repositories.nodes[].languages.edges[]|{n:.node.name,s:.size}]|group_by(.n)|map({key:.[0].n,value:(map(.s)|add)})|from_entries' \
  > assets/lenguajes.json && python3 scripts/cards.py
```

### Pendiente

- Los proyectos no enlazan a ningún repo porque son privados: un enlace daría 404.
- El banner enlaza a adicodev.com, que sigue siendo el WordPress hasta que se despliegue el
  portfolio nuevo.

---

## 3. La serpiente de contribuciones

**De dónde sale:** de la GitHub Action [`Platane/snk`](https://github.com/Platane/snk).
No es un servicio en vivo ni una API. Funciona así:

1. La Action lee tu rejilla pública de contribuciones.
2. Genera un **SVG con la animación dentro** (SMIL + CSS, ambos permitidos por
   el sanitizador de SVG de GitHub — JavaScript no lo estaría).
3. Hace commit de ese SVG en una rama aparte del propio repo, `output`.
4. El README lo referencia con la URL cruda de esa rama.

Por eso la URL que viste (`.../edunavajas/output/github-contribution-grid-snake-dark.svg`)
apunta a **su** repo: cada uno aloja su propio SVG. Y por eso está en una rama
separada — así los commits automáticos cada 12 h no ensucian el historial de `main`.

**Ya está activa.** Quedó configurado así:

- Permisos de escritura para Actions (`Settings → Actions → General → Workflow
  permissions → Read and write`). Sin esto la Action falla al crear la rama.
- Primera ejecución lanzada a mano; a partir de ahí corre sola cada 12 h y en
  cada push a `main`.
- Los SVG viven en la rama `output` y el README ya los referencia.

Si algún día deja de aparecer, mira **Actions** en el repo: lo habitual es que
alguien haya devuelto los permisos del workflow a solo lectura.

### Otras animaciones del mismo estilo

| Qué hace | Proyecto |
|---|---|
| Serpiente comiéndose las contribuciones | `Platane/snk` |
| Gráfica de actividad animada | `Ashutosh00710/github-readme-activity-graph` |
| Tarjeta con las stats | `anuraghazra/github-readme-stats` |
| Banners con onda/gradiente por URL | `kyechan99/capsule-render` |
| Efecto máquina de escribir | `DenverCoder1/readme-typing-svg` |

Todos siguen el mismo principio: **un SVG animado**, generado por una Action que
lo commitea en tu repo, o servido por un endpoint externo. La diferencia importa:
lo generado por Action vive en tu repo y no se cae nunca; lo servido por un
endpoint externo depende de que ese Vercel siga en pie.

---

## 4. Tarjetas de stats — retiradas

Estaban puestas y se cayeron el mismo día. `github-readme-stats.vercel.app`
responde **503 DEPLOYMENT_PAUSED**: la instancia pública y compartida está
pausada en Vercel, así que las tarjetas salían rotas para todo el mundo.

Es el riesgo de cualquier badge servido por un endpoint de terceros. Si las
quieres de vuelta, la forma seria es desplegar tu propia instancia:

1. Fork de `anuraghazra/github-readme-stats`.
2. Importarlo en Vercel y añadir un `PAT_1` (token de GitHub, solo lectura).
3. Cambiar el dominio de las URLs por el de tu despliegue.

Así no dependes de que el Vercel de otro siga en pie.

Evita también `github-readme-streak-stats.herokuapp.com`: murió con el plan
gratuito de Heroku. Muchos READMEs lo siguen copiando y muestran imagen rota.
El dominio vivo de ese proyecto es `streak-stats.demolab.com`.

La serpiente no tiene este problema: su SVG vive en tu propia rama `output`.
