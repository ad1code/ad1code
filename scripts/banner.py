#!/usr/bin/env python3
"""Genera el banner animado del perfil: assets/banner-dark.svg y assets/banner-light.svg.

    python3 scripts/banner.py [ruta-al-retrato] [carpeta-de-pegatinas]

El retrato (PNG o WebP sin fondo) se trama a 1 bit y se dibuja con puntos. Unas partículas
salen de él y forman, uno tras otro, los logos de LOGOS; después vuelven al retrato.
Todo es SVG con SMIL: GitHub pinta los SVG como imagen y no ejecuta JavaScript.

El retrato original no se guarda en este repo: se lee del portfolio. Requiere Pillow y numpy.
"""

from __future__ import annotations

import html
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageEnhance, ImageFilter, ImageOps

ROOT = Path(__file__).resolve().parent.parent
ASSETS = ROOT / "assets"
# El portfolio se espera clonado junto a este repo.
PORTFOLIO = ROOT.parent / "adicode-porfolio" / "public"
PORTRAIT = Path(sys.argv[1]) if len(sys.argv) > 1 else PORTFOLIO / "alberto-sin-fondo.webp"
STICKERS = Path(sys.argv[2]) if len(sys.argv) > 2 else ASSETS / "tech"

W, H = 1180, 610
MONO = "ui-monospace,SFMono-Regular,Menlo,Consolas,monospace"
SEED = 20260928

# Rejilla del retrato y su sitio dentro del marco izquierdo.
GRID_W, GRID_H = 300, 340
GRID_X, GRID_Y = 94, 162
# Recorte del retrato original (704×1097): cabeza y hombros.
CROP = (65, 0, 685, 703)
# Cara dentro de la rejilla: ahí se engancha el recuadro de detección, como en el hero.
FACE = (45, 52, 215, 302)
DETECT_LABEL = "Alberto Ramos · 0,97"

# Logos que forman las partículas, en orden, y el color de cada tramo.
LOGOS = ("claude", "python", "react", "docker")
LOGO_SIZE = 236
TRAVELLERS = 700
HOLD_PARTICLES = 3200
BANDS = 80

PORTRAIT_HOLD = 3.4
TRANSITION = 1.3
LOGO_HOLD = 3.0

# Sin clave `proyectos` con cifras: en la web los tickets tampoco llevan dato.
YAML_ROWS = [
    (0, "perfil", ""),
    (1, "nombre", "Alberto Ramos"),
    (1, "rol", "AI Engineer · Fullstack"),
    (1, "base", "Madrid"),
    (1, "foco", "producto con IA, puesto en producción"),
    (1, "origen", "desarrollo web convencional"),
    (0, "stack", ""),
    (1, "agentes", "Claude Code · MCP · n8n"),
    (1, "vision", "Python · PyTorch · OpenCV · FastAPI"),
    (1, "producto", "Next.js · React · TypeScript · PostgreSQL"),
    (1, "infra", "Docker · Linux"),
    (0, "proyectos", ""),
    (1, "second_brain", "clientes, proyectos y agenda, con Claude por MCP"),
    (1, "gymtracker", "entreno y nutrición; la uso en cada entreno"),
    (1, "validacion_facial", "antispoofing y caras generadas por IA"),
    (0, "contacto", ""),
    (1, "web", "adicodev.com"),
    (1, "linkedin", "/in/developer-ai-specialist"),
]

# Colores del portfolio (globals.css y themes.ts). `cycle`: retrato y, después, un color por logo.
THEMES = {
    "dark": {
        "bg": "#141414",
        "panel": "#181818",
        "panel2": "#1e1e1e",
        "line": "#2e2b29",
        "muted": "#8f8983",
        "text": "#edeae6",
        "accent": "#d97757",
        "ink": "#141414",
        "key": "#9cdcfe",
        "cycle": ["#d97757", "#d97757", "#cdf34e", "#b39dff", "#3fd3c1"],
    },
    "light": {
        "bg": "#efe9e1",
        "panel": "#f5f1eb",
        "panel2": "#faf7f3",
        "line": "#d6cdc1",
        "muted": "#8a7f74",
        "text": "#1d1a18",
        "accent": "#c4532f",
        "ink": "#ffffff",
        "key": "#2a6f97",
        "cycle": ["#c4532f", "#c4532f", "#5c7a00", "#6b4fd8", "#0f8f80"],
    },
}


def floyd_steinberg(gray: np.ndarray) -> np.ndarray:
    """Tramado de 1 bit en serpentina. True = píxel encendido."""
    work = gray.astype(np.float32) / 255.0
    out = np.zeros(work.shape, dtype=bool)
    h, w = work.shape
    for y in range(h):
        step = 1 if y % 2 == 0 else -1
        xs = range(w) if step == 1 else range(w - 1, -1, -1)
        for x in xs:
            old = work[y, x]
            new = 1.0 if old >= 0.5 else 0.0
            out[y, x] = new == 1.0
            err = old - new
            nx = x + step
            if 0 <= nx < w:
                work[y, nx] += err * 7 / 16
            if y + 1 < h:
                if 0 <= x - step < w:
                    work[y + 1, x - step] += err * 3 / 16
                work[y + 1, x] += err * 5 / 16
                if 0 <= nx < w:
                    work[y + 1, nx] += err * 1 / 16
    return out


def portrait_points(theme: str) -> np.ndarray:
    """Puntos del retrato en coordenadas del banner. En oscuro se dibujan las luces; en claro, las sombras."""
    crop = Image.open(PORTRAIT).convert("RGBA").crop(CROP).resize((GRID_W, GRID_H), Image.Resampling.LANCZOS)
    alpha = np.asarray(crop.getchannel("A")) > 20
    backdrop = Image.new("RGBA", crop.size, "black" if theme == "dark" else "white")
    backdrop.alpha_composite(crop)
    gray = ImageOps.autocontrast(ImageOps.grayscale(backdrop.convert("RGB")), cutoff=1)
    gray = ImageEnhance.Contrast(gray).enhance(1.3)
    if theme == "dark":
        # Sin esto la frente y la mejilla salen como una mancha lisa, sin trama.
        gray = ImageEnhance.Brightness(gray).enhance(0.74)
    gray = gray.filter(ImageFilter.UnsharpMask(radius=2, percent=150, threshold=1))
    bits = floyd_steinberg(np.asarray(gray))
    active = (bits if theme == "dark" else ~bits) & alpha
    ys, xs = np.where(active)
    return np.column_stack((GRID_X + xs, GRID_Y + ys)).astype(np.float32)


def logo_points(name: str) -> np.ndarray:
    """Silueta de un logo: los píxeles con color de su pegatina (sin el borde blanco ni la sombra)."""
    sticker = Image.open(STICKERS / f"{name}.webp").convert("RGBA").resize((LOGO_SIZE, LOGO_SIZE), Image.Resampling.LANCZOS)
    px = np.asarray(sticker).astype(np.int16)
    rgb = px[..., :3]
    saturated = (rgb.max(axis=2) - rgb.min(axis=2)) > 60
    ys, xs = np.where(saturated & (px[..., 3] > 200))
    if not len(xs):
        raise SystemExit(f"{name}: la pegatina no tiene píxeles de color")
    x0 = GRID_X + (GRID_W - LOGO_SIZE) / 2
    y0 = GRID_Y + (GRID_H - LOGO_SIZE) / 2
    return np.column_stack((x0 + xs, y0 + ys)).astype(np.float32)


def match(source: np.ndarray, target: np.ndarray, rng: np.random.Generator) -> np.ndarray:
    """Asigna a cada punto de origen el destino libre más cercano (voraz, sin scipy)."""
    dist = ((source[:, None, :] - target[None, :, :]) ** 2).sum(axis=2)
    ordered = np.empty_like(target)
    for i in rng.permutation(len(source)):
        j = int(np.argmin(dist[i]))
        ordered[i] = target[j]
        dist[:, j] = np.inf
    return ordered


def runs(points: np.ndarray) -> str:
    """Une los puntos contiguos de cada fila en tramos horizontales: menos peso."""
    cells = sorted({(int(y), int(x)) for x, y in np.rint(points)})
    out: list[str] = []
    i = 0
    while i < len(cells):
        y, x0 = cells[i]
        x1 = x0
        i += 1
        while i < len(cells) and cells[i][0] == y and cells[i][1] == x1 + 1:
            x1 = cells[i][1]
            i += 1
        out.append(f"M{x0} {y}h{x1 - x0 + 1}")
    return "".join(out)


def dots(points: np.ndarray) -> str:
    return "".join(f"M{x} {y}h1" for y, x in sorted({(int(y), int(x)) for x, y in np.rint(points)}))


def key(value: float) -> str:
    return f"{value:.4f}".rstrip("0").rstrip(".")


def render(theme: str) -> str:
    t = THEMES[theme]
    rng = np.random.default_rng(SEED)
    portrait = portrait_points(theme)
    n = min(TRAVELLERS, len(portrait))
    source = portrait[rng.choice(len(portrait), n, replace=False)]

    silhouettes = {name: logo_points(name) for name in LOGOS}
    targets: list[np.ndarray] = []
    current = source
    for points in silhouettes.values():
        current = match(current, points[rng.choice(len(points), n, replace=len(points) < n)], rng)
        targets.append(current)

    # Línea de tiempo del bucle: retrato, y por cada logo, viaje y pausa. Al final vuelve al retrato.
    times = [0.0, PORTRAIT_HOLD]
    frames = [source, source]
    for target in targets:
        times += [times[-1] + TRANSITION, times[-1] + TRANSITION + LOGO_HOLD]
        frames += [target, target]
    times.append(times[-1] + TRANSITION)
    frames.append(source)
    total = times[-1]
    key_times = ";".join(key(v / total) for v in times)
    loop = f'dur="{key(total)}s" repeatCount="indefinite" keyTimes="{key_times}"'
    colours = [t["cycle"][0], t["cycle"][0]]
    for colour in t["cycle"][1:]:
        colours += [colour, colour]
    colours.append(t["cycle"][0])
    colour_values = ";".join(colours)

    frame_x, frame_y, frame_w, frame_h = 35, 88, 418, 472
    p: list[str] = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" '
        'role="img" aria-labelledby="title desc">',
        '<title id="title">Alberto Ramos, AI Engineer</title>',
        '<desc id="desc">Ventana de editor con un retrato tramado cuyas partículas forman los logos de '
        "Claude, Python, React y Docker, junto a un archivo perfil.yml con su rol, stack y proyectos.</desc>",
        f'<defs><clipPath id="clip"><rect x="{frame_x + 14}" y="{frame_y + 36}" width="{frame_w - 28}" '
        f'height="{frame_h - 58}" rx="3"/></clipPath></defs>',
        f'<rect width="{W}" height="{H}" rx="18" fill="{t["bg"]}"/>',
        f'<rect x="13" y="13" width="{W - 26}" height="{H - 26}" rx="13" fill="{t["panel"]}" stroke="{t["line"]}"/>',
        f'<path d="M13 62H{W - 13}" stroke="{t["line"]}"/>',
        '<circle cx="38" cy="38" r="6" fill="#ff5f57"/><circle cx="59" cy="38" r="6" fill="#febc2e"/>'
        '<circle cx="80" cy="38" r="6" fill="#28c840"/>',
        f'<text x="{W // 2}" y="43" text-anchor="middle" fill="{t["muted"]}" font-family="{MONO}" '
        'font-size="13" letter-spacing=".4">adicodev_ — perfil.yml</text>',
        # Marco izquierdo: el retrato.
        f'<rect x="{frame_x}" y="{frame_y}" width="{frame_w}" height="{frame_h}" rx="6" fill="{t["panel2"]}" stroke="{t["line"]}"/>',
        f'<path d="M{frame_x} 124H{frame_x + frame_w}" stroke="{t["line"]}"/>',
        f'<text x="49" y="111" fill="{t["accent"]}" font-family="{MONO}" font-size="13" font-weight="700" '
        'letter-spacing="1.2">RETRATO.MAP</text>',
        f'<text x="438" y="111" text-anchor="end" fill="{t["muted"]}" font-family="{MONO}" font-size="11">'
        f"{GRID_W}×{GRID_H} / 1 BIT</text>",
        # El color del grupo cambia con cada logo: los hijos lo heredan.
        f'<g clip-path="url(#clip)" shape-rendering="crispEdges" stroke="{t["cycle"][0]}" fill="{t["cycle"][0]}">',
        f'<animate attributeName="stroke" {loop} values="{colour_values}"/>',
        f'<animate attributeName="fill" {loop} values="{colour_values}"/>',
    ]

    # Retrato denso, en bandas al azar: al empezar el viaje se desplazan un poco hacia el logo y se apagan.
    centre = targets[0].mean(axis=0)
    band_of = rng.integers(0, BANDS, size=len(portrait))
    jitter = rng.normal(0, 4, size=(BANDS, 2))
    still = len(frames) - 3
    for band in range(BANDS):
        pts = portrait[band_of == band]
        if not len(pts):
            continue
        dx, dy = (centre - pts.mean(axis=0)) * 0.18 + jitter[band]
        moves = ";".join(["0 0", "0 0", f"{dx:.0f} {dy:.0f}"] + ["0 0"] * still)
        fades = ";".join([".94", ".94", "0"] + ["0"] * (still - 1) + [".94"])
        p.append(
            f'<path d="{runs(pts)}" fill="none" opacity=".94">'
            f'<animateTransform attributeName="transform" type="translate" {loop} values="{moves}"/>'
            f'<animate attributeName="opacity" {loop} values="{fades}"/></path>'
        )

    # Partículas viajeras: un cuadrado por partícula, con su posición en cada parada.
    visible = ";".join(["0", "0"] + ["1"] * still + ["0"])
    for i in range(n):
        stops = ";".join(f"{f[i, 0]:.0f} {f[i, 1]:.0f}" for f in frames)
        p.append(
            '<path d="M-.7-.7h1.4v1.4h-1.4z" stroke="none" opacity="0">'
            f'<animateTransform attributeName="transform" type="translate" {loop} values="{stops}"/>'
            f'<animate attributeName="opacity" {loop} values="{visible}"/></path>'
        )

    # Al llegar, una nube más densa rellena la silueta mientras dura la pausa.
    for k, points in enumerate(silhouettes.values()):
        chosen = points[rng.choice(len(points), min(HOLD_PARTICLES, len(points)), replace=False)]
        shown = ["0"] * len(frames)
        shown[2 + 2 * k] = shown[3 + 2 * k] = ".85"
        p.append(
            f'<path d="{dots(chosen)}" fill="none" opacity="0">'
            f'<animate attributeName="opacity" {loop} values="{";".join(shown)}"/></path>'
        )
    p.append("</g>")

    # Recuadro de detección sobre la cara: entra al empezar cada vuelta y se va antes del viaje.
    fx0, fy0, fx1, fy1 = (GRID_X + FACE[0], GRID_Y + FACE[1], GRID_X + FACE[2], GRID_Y + FACE[3])
    cx, cy, hw, hh = (fx0 + fx1) / 2, (fy0 + fy1) / 2, (fx1 - fx0) / 2, (fy1 - fy0) / 2
    c = 22
    corners = (
        f"M{-hw} {-hh + c}V{-hh}H{-hw + c}M{hw - c} {-hh}H{hw}V{-hh + c}"
        f"M{hw} {hh - c}V{hh}H{hw - c}M{-hw + c} {hh}H{-hw}V{hh - c}"
    )
    label_w = len(DETECT_LABEL) * 7.3 + 16
    detect_times = ";".join(key(v / total) for v in (0, 0.4, PORTRAIT_HOLD - 0.4, PORTRAIT_HOLD - 0.1, total))
    p += [
        f'<g transform="translate({cx:.0f} {cy:.0f})"><g>',
        f'<animate attributeName="opacity" dur="{key(total)}s" repeatCount="indefinite" keyTimes="{detect_times}" values="0;1;1;0;0"/>',
        f'<animateTransform attributeName="transform" type="scale" dur="{key(total)}s" repeatCount="indefinite" '
        f'keyTimes="{detect_times}" values="1.14;1;1;1;1"/>',
        f'<path d="{corners}" fill="none" stroke="{t["accent"]}" stroke-width="2"/>',
        f'<rect x="{-hw:.0f}" y="{hh + 8:.0f}" width="{label_w:.0f}" height="22" rx="3" fill="{t["accent"]}"/>',
        f'<text x="{-hw + 8:.0f}" y="{hh + 23:.0f}" fill="{t["ink"]}" font-family="{MONO}" font-size="12" '
        f'font-weight="700">{html.escape(DETECT_LABEL)}</text>',
        "</g></g>",
        f'<text x="58" y="551" fill="{t["muted"]}" font-family="{MONO}" font-size="10">'
        f"PTS {len(portrait):05d} · FLOYD-STEINBERG</text>",
    ]

    # Marco derecho: perfil.yml.
    p += [
        f'<rect x="474" y="88" width="672" height="472" rx="6" fill="{t["panel2"]}" stroke="{t["line"]}"/>',
        f'<path d="M474 124H1146" stroke="{t["line"]}"/>',
        f'<text x="490" y="111" fill="{t["accent"]}" font-family="{MONO}" font-size="13" font-weight="700" '
        'letter-spacing=".5">perfil.yml</text>',
        f'<text x="574" y="111" fill="{t["muted"]}" font-family="{MONO}" font-size="11">[YAML]</text>',
        f'<rect x="1012" y="94" width="116" height="24" rx="12" fill="{t["accent"]}" fill-opacity=".14" stroke="{t["accent"]}"/>',
        f'<text x="1070" y="111" text-anchor="middle" fill="{t["accent"]}" font-family="{MONO}" font-size="13" '
        'font-weight="700">@ad1code</text>',
    ]
    y = 149.0
    step = 20.6
    for number, (indent, name, value) in enumerate(YAML_ROWS, 1):
        if indent == 0:
            body = f'<tspan fill="{t["accent"]}" font-weight="700">{html.escape(name)}:</tspan>'
        else:
            body = f'<tspan fill="{t["key"]}">{html.escape(name)}: </tspan><tspan fill="{t["text"]}">{html.escape(value)}</tspan>'
        p += [
            f'<text x="506" y="{y:.1f}" text-anchor="end" fill="{t["muted"]}" opacity=".5" font-family="{MONO}" font-size="13">{number}</text>',
            f'<text x="{525 + 17 * indent}" y="{y:.1f}" font-family="{MONO}" font-size="13">{body}</text>',
        ]
        y += step
    # Cursor parpadeante tras la última línea.
    last = YAML_ROWS[-1]
    cursor_x = 542 + (len(last[1]) + 2 + len(last[2])) * 7.83 + 3
    p.append(
        f'<rect x="{cursor_x:.0f}" y="{y - step - 11:.0f}" width="8" height="15" fill="{t["accent"]}">'
        '<animate attributeName="opacity" dur="1.1s" repeatCount="indefinite" keyTimes="0;.5;.5;1" values="1;1;0;0"/></rect>'
    )

    # Barra de estado, como la del editor.
    p += [
        f'<path d="M474 526H1146" stroke="{t["line"]}"/>',
        f'<rect x="485" y="533" width="62" height="20" rx="3" fill="{t["accent"]}"/>',
        f'<text x="516" y="547" text-anchor="middle" fill="{t["ink"]}" font-family="{MONO}" font-size="11" font-weight="700">main</text>',
        f'<text x="559" y="547" fill="{t["text"]}" font-family="{MONO}" font-size="12">perfil.yml</text>',
        f'<text x="1134" y="547" text-anchor="end" fill="{t["muted"]}" font-family="{MONO}" font-size="11">'
        f"UTF-8 · YAML · Ln {len(YAML_ROWS)}</text>",
        "</svg>",
    ]
    return "".join(p)


def main() -> None:
    ASSETS.mkdir(exist_ok=True)
    for theme in THEMES:
        out = ASSETS / f"banner-{theme}.svg"
        out.write_text(render(theme), encoding="utf-8")
        print(f"{out.relative_to(ROOT)}  {out.stat().st_size / 1024:.0f} KB")


if __name__ == "__main__":
    main()
