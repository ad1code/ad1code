#!/usr/bin/env python3
"""Genera las tarjetas fijas del perfil: assets/whoami.svg y assets/lenguajes.svg.

    python3 scripts/cards.py

`lenguajes.svg` sale de assets/lenguajes.json: bytes por lenguaje de los repos propios, sin forks
(el comando que lo actualiza está en SETUP.md). Solo biblioteca estándar.
"""

from __future__ import annotations

import html
import json
import math
import random
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ASSETS = ROOT / "assets"
MONO = "ui-monospace,SFMono-Regular,Menlo,Consolas,monospace"

# Colores del portfolio: fondo y terracota de adicodev, y el color de cada proyecto.
BG, PANEL, LINE = "#141414", "#1e1e1e", "#2e2b29"
TEXT, TEXT2, MUTED = "#edeae6", "#c9c4be", "#8f8983"
ACCENT, LIME, LILAC, TEAL, AMBER, BLUE = "#d97757", "#cdf34e", "#b39dff", "#3fd3c1", "#ffb000", "#9cdcfe"


def text(x: float, y: float, body: str, fill: str = TEXT, size: int = 16, weight: int = 400, anchor: str = "start") -> str:
    return (
        f'<text x="{x:g}" y="{y:g}" fill="{fill}" font-family="{MONO}" font-size="{size}" '
        f'font-weight="{weight}" text-anchor="{anchor}">{html.escape(body)}</text>'
    )


def window(w: int, h: int, title: str, label: str, desc: str) -> list[str]:
    """Marco común: ventana con sus tres botones y una línea de título."""
    return [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}" role="img" aria-labelledby="title desc">',
        f'<title id="title">{html.escape(label)}</title><desc id="desc">{html.escape(desc)}</desc>',
        f'<rect width="{w}" height="{h}" rx="18" fill="{BG}"/>',
        f'<rect x="9" y="9" width="{w - 18}" height="{h - 18}" rx="13" fill="none" stroke="{LINE}" stroke-width="1.5"/>',
        '<circle cx="35" cy="35" r="5" fill="#ff5f57"/><circle cx="54" cy="35" r="5" fill="#febc2e"/><circle cx="73" cy="35" r="5" fill="#28c840"/>',
        text(98, 40, title, MUTED, 14),
        f'<path d="M29 58H{w - 29}" stroke="{LINE}"/>',
    ]


def network() -> list[str]:
    """La red de «Mi historia» (36-8-6-3): un recorte de 6×6 píxeles entra y sale ojo, pelo o piel."""
    rng = random.Random(7)
    p: list[str] = []
    # Entrada: recorte de 6×6 píxeles en grises.
    gx, gy, cell = 672, 158, 10
    for r in range(6):
        for c in range(6):
            tone = rng.choice(("#2e2b29", "#5a544e", "#8f8983", "#c9c4be"))
            p.append(f'<rect x="{gx + c * cell}" y="{gy + r * cell}" width="{cell - 1}" height="{cell - 1}" fill="{tone}"/>')
    layers = [
        [(778, 136 + i * 20.5) for i in range(8)],
        [(838, 156 + i * 20.5) for i in range(6)],
        [(898, 180 + i * 28) for i in range(3)],
    ]
    tones = [ACCENT, LIME, LILAC, TEAL, AMBER, BLUE, TEXT2, ACCENT]
    entry = (gx + 6 * cell + 3, gy + 3 * cell)
    edges = [(entry, b, tones[i]) for i, b in enumerate(layers[0])]
    edges += [(a, b, tones[i]) for i, a in enumerate(layers[0]) for b in layers[1]]
    edges += [(a, b, tones[i]) for i, a in enumerate(layers[1]) for b in layers[2]]
    for k, (a, b, tone) in enumerate(edges):
        # Cada conexión late por su cuenta: la señal recorre la red sin fin.
        begin = rng.uniform(0, 3.2)
        p.append(
            f'<path d="M{a[0]:g} {a[1]:g}L{b[0]:g} {b[1]:g}" stroke="{tone}" stroke-width="1" opacity=".16">'
            f'<animate attributeName="opacity" dur="3.2s" begin="{begin:.2f}s" repeatCount="indefinite" '
            'keyTimes="0;.12;.3;1" values=".16;.75;.16;.16"/></path>'
            if k % 3 == 0
            else f'<path d="M{a[0]:g} {a[1]:g}L{b[0]:g} {b[1]:g}" stroke="{tone}" stroke-width="1" opacity=".16"/>'
        )
    for i, (x, y) in enumerate(layers[0]):
        p.append(f'<circle cx="{x:g}" cy="{y:g}" r="4.5" fill="{PANEL}" stroke="{tones[i]}" stroke-width="1.5"/>')
    for i, (x, y) in enumerate(layers[1]):
        p.append(f'<circle cx="{x:g}" cy="{y:g}" r="4.5" fill="{PANEL}" stroke="{tones[i]}" stroke-width="1.5"/>')
    # Salidas: se enciende una cada vez (ojo, pelo, piel).
    for i, ((x, y), tone) in enumerate(zip(layers[2], (LIME, LILAC, TEAL))):
        on = ["0"] * 3
        on[i] = "1"
        p.append(
            f'<circle cx="{x:g}" cy="{y:g}" r="6" fill="{PANEL}" stroke="{tone}" stroke-width="1.5"/>'
            f'<circle cx="{x:g}" cy="{y:g}" r="3.2" fill="{tone}" opacity="{on[0]}">'
            f'<animate attributeName="opacity" dur="6s" repeatCount="indefinite" calcMode="discrete" '
            f'keyTimes="0;.333;.666" values="{";".join(on)}"/></circle>'
        )
    return p


def whoami() -> str:
    w, h = 960, 390
    p = window(w, h, "ad1code  ·  perfil  ·  en línea", "Alberto Ramos, AI Engineer",
               "Tarjeta de terminal con el rol, la ubicación y los proyectos de Alberto Ramos, junto a una red neuronal pequeña.")
    p += [
        f'<rect x="29" y="78" width="594" height="283" rx="9" fill="{PANEL}" stroke="{LINE}" stroke-width="1.5"/>',
        text(48, 110, "❯ whoami", ACCENT, 19, 700),
        text(48, 140, "alberto_ramos", TEXT2, 17),
        text(196, 140, "—", MUTED, 17),
        text(220, 140, "AI Engineer · Fullstack", TEXT, 17, 700),
        f'<path d="M48 160H604" stroke="{LINE}"/>',
        text(48, 187, "base:", MUTED, 15), text(126, 187, "Madrid", TEXT2, 15),
        text(48, 211, "antes:", MUTED, 15), text(126, 211, "desarrollo web convencional", TEXT2, 15),
        text(48, 235, "ahora:", MUTED, 15), text(126, 235, "IA en productos", TEXT2, 15),
        text(48, 273, "❯ ls proyectos/", ACCENT, 19, 700),
    ]
    projects = [
        ("second-brain/", LIME, "clientes, proyectos y agenda con MCP"),
        ("gymtracker/", LILAC, "entreno y nutrición, sin anuncios"),
        ("validacion-facial/", TEAL, "antispoofing y caras hechas con IA"),
    ]
    for i, (name, tone, what) in enumerate(projects):
        y = 301 + i * 23
        p += [text(48, y, name, tone, 15), text(230, y, what, TEXT2, 15)]
    p += [
        f'<rect x="651" y="78" width="280" height="283" rx="9" fill="{PANEL}" stroke="{LINE}" stroke-width="1.5"/>',
        text(670, 108, "red.neuronal", ACCENT, 15, 700),
        text(912, 108, "36-8-6-3", MUTED, 12, anchor="end"),
        *network(),
        text(670, 322, "entrada 6×6 → ojo · pelo · piel", MUTED, 12),
        text(670, 342, "gris: no lo sabe, y lo dice", TEXT2, 12),
        "</svg>",
    ]
    return "".join(p)


def languages() -> str:
    data: dict[str, int] = json.loads((ASSETS / "lenguajes.json").read_text())
    total = sum(data.values())
    top = sorted(data.items(), key=lambda kv: -kv[1])[:6]
    shares = [(name, size / total) for name, size in top]
    tones = [ACCENT, LIME, LILAC, TEAL, AMBER, BLUE]

    w, h = 960, 360
    p = window(w, h, "ad1code  ·  lenguajes  ·  repos propios, sin forks", "Lenguajes de los repos de Alberto Ramos",
               "Radar y barras con el porcentaje de código por lenguaje: " + ", ".join(f"{n} {s:.0%}" for n, s in shares) + ".")

    # Radar. La raíz cuadrada evita que el lenguaje dominante aplaste al resto; la cifra exacta va en las barras.
    cx, cy, radius = 236, 208, 104
    biggest = shares[0][1]

    def at(i: int, r: float) -> tuple[float, float]:
        a = -math.pi / 2 + i * 2 * math.pi / len(shares)
        return cx + r * math.cos(a), cy + r * math.sin(a)

    def ring(r: float) -> str:
        return "M" + "L".join(f"{x:.1f} {y:.1f}" for x, y in (at(i, r) for i in range(len(shares)))) + "Z"

    for f in (0.25, 0.5, 0.75, 1):
        p.append(f'<path d="{ring(radius * f)}" fill="none" stroke="{LINE}"/>')
    for i, (name, _) in enumerate(shares):
        x, y = at(i, radius)
        lx, ly = at(i, radius + 16)
        anchor = "middle" if abs(lx - cx) < 8 else ("start" if lx > cx else "end")
        p += [f'<path d="M{cx} {cy}L{x:.1f} {y:.1f}" stroke="{LINE}"/>', text(lx, ly + 4, name, MUTED, 12, anchor=anchor)]
    shape = "M" + "L".join(
        f"{x:.1f} {y:.1f}" for x, y in (at(i, radius * math.sqrt(s / biggest)) for i, (_, s) in enumerate(shares))
    ) + "Z"
    p.append(f'<path d="{shape}" fill="{ACCENT}" fill-opacity=".22" stroke="{ACCENT}" stroke-width="2" stroke-linejoin="round"/>')
    for i, (_, s) in enumerate(shares):
        x, y = at(i, radius * math.sqrt(s / biggest))
        p.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="3.5" fill="{tones[i]}"/>')

    # Barras con el porcentaje real.
    x0, bar_w = 500, 280
    p.append(text(x0, 96, "❯ du --por-lenguaje", ACCENT, 17, 700))
    for i, (name, s) in enumerate(shares):
        y = 132 + i * 34
        p += [
            text(x0, y + 5, name, TEXT2, 14),
            f'<rect x="{x0 + 104}" y="{y - 6}" width="{bar_w}" height="12" rx="3" fill="{PANEL}" stroke="{LINE}"/>',
            f'<rect x="{x0 + 104}" y="{y - 6}" width="{max(4, bar_w * s / biggest):.0f}" height="12" rx="3" fill="{tones[i]}"/>',
            text(x0 + 104 + bar_w + 44, y + 5, f"{s:.1%}".replace(".", ","), MUTED, 13, anchor="end"),
        ]
    rest = 1 - sum(s for _, s in shares)
    p += [text(x0, 338, f"resto: {rest:.1%}".replace(".", ",") + f"  ·  {len(data)} lenguajes", MUTED, 12), "</svg>"]
    return "".join(p)


def main() -> None:
    for name, svg in (("whoami", whoami()), ("lenguajes", languages())):
        out = ASSETS / f"{name}.svg"
        out.write_text(svg, encoding="utf-8")
        print(f"{out.relative_to(ROOT)}  {out.stat().st_size / 1024:.1f} KB")


if __name__ == "__main__":
    main()
