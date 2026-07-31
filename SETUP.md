# SETUP — repo de perfil `ad1code/ad1code`

Este repo existe por una única razón: GitHub renderiza el `README.md` de un repo
**público** que se llame igual que el usuario en la cabecera del perfil.
Si el repo pasa a privado o cambia de nombre, el perfil deja de mostrarlo.

---

## 1. Pendiente antes de publicar

- [x] **URL de LinkedIn** — puesta.
- [ ] Decidir si dejas el **email** en abierto. Los bots rastrean perfiles
      públicos; si prefieres que no, borra el badge "Escríbeme".
- [ ] **Sección de proyectos**: fuera por ahora. Solo se pueden enlazar repos
      públicos — un enlace a un repo privado da 404 a cualquiera que no seas tú.

---

## 2. El banner

Está en `img/header.jpg` (800 × 200 px, 32 KB).

Para cambiarlo, sustituye el archivo y ya. Dos avisos:

**Resolución.** El README se renderiza a unos 830 px de ancho, así que la imagen
se estira ligeramente por encima de su tamaño nativo. Se ve bien, pero en
pantallas retina se nota algo blanda. Si tienes el original (Figma, Canva),
expórtalo a **1600 × 400 px** y gana nitidez sin tocar nada más.

**Tema oscuro.** El banner tiene fondo gris claro, así que a quien tenga GitHub
en modo oscuro le aparece como una tarjeta clara. No queda mal y es lo que hace
media plataforma. Si quieres una versión oscura, exporta el mismo diseño con
fondo oscuro como `img/header-dark.jpg` y cambia en el README el `<img>` por:

```html
<picture>
  <source media="(prefers-color-scheme: dark)" srcset="img/header-dark.jpg">
  <img src="img/header.jpg" width="100%" alt="...">
</picture>
```

No merece la pena generar la versión oscura por software: los logos negros
(WordPress, Astro) desaparecen sobre fondo oscuro y hay que recolocarlos a mano.

### Reglas del formato

| Parámetro | Valor | Por qué |
|---|---|---|
| Ratio | 4:1 | Más alto empuja tu contenido fuera de la primera pantalla. |
| Tamaño ideal | 1600 × 400 px | El doble del ancho de render = nítido en retina. |
| Peso | < 500 KB | GitHub lo sirve por su proxy; los pesados tardan en aparecer. |
| Texto | ≥ 48 px sobre lienzo de 1600 | En móvil el banner baja a ~350 px de ancho. |

### Trampas

1. **Caché de Camo.** GitHub proxea y cachea las imágenes. Si corriges el banner
   con el mismo nombre puede seguir viéndose el viejo un rato. Solución:
   renómbralo (`header-v2.jpg`) y actualiza el `src`.
2. **Nada de CSS.** GitHub elimina `<style>`, `class` y scripts del Markdown.
   Solo sobreviven `align`, `width`, `height` y `srcset`. Todo el diseño va
   dentro de la imagen.
3. **Rutas relativas.** Usa `img/header.jpg`, no URLs de `github.com/.../blob/...`.
   Las de `blob` funcionan hoy porque GitHub las reescribe, pero se rompen si
   cambias el nombre de la rama.

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
