"""Render a Marp-style markdown deck to a print-quality PDF via weasyprint.

We do not call `marp-cli` (Node, not installed). Instead: strip the YAML
frontmatter, split on `\n---\n` slide separators, classify each slide
(cover / hero-band / section / closing), render each to HTML with the
`markdown` library, and stitch them into a landscape 16:9 PDF.

The CSS implements a small design system rather than the stock Marp dark
theme — named `@page` rules give the cover and closing slides a clean,
page-number-free surface while content slides pick up a subtle footer
with project name and page counter. Tables get a zebra treatment,
strong/em/code each have an assigned colour role, and the section
headers (written with Marp-style spaced letters, e.g. `T H E  C O S T`)
get an accent underline.

Usage:
    uv run --extra report python scripts/build_presentation.py \\
        --in presentation_en.md --out margin-optimizer-en.pdf
"""

from __future__ import annotations

import re
from pathlib import Path

import click
import markdown as md
from weasyprint import HTML

_FRONTMATTER = re.compile(r"^---\s*\n.*?\n---\s*\n", re.DOTALL)
_H1 = re.compile(r"^\s*#\s+(.+)$", re.MULTILINE)

_CSS = """
/* --- DESIGN TOKENS --------------------------------------------------- */
/*
 * ink:      #e6edf3    primary text
 * mute:     #94a3b8    secondary text
 * dim:      #475569    tertiary text / footer
 * base:     #0a0e14    page background
 * panel:    #141a22    cards / tables / code
 * line:     #1f2933    borders
 * amber:    #f59e0b    hero accent (strong)
 * cyan:     #60a5fa    highlight accent (em, links)
 * lime:     #84cc16    metric accent
 */

/* --- PAGE TEMPLATES -------------------------------------------------- */

@page {
    size: 297mm 167mm;                 /* 16:9 landscape */
    margin: 16mm 22mm 20mm;
    background: #0a0e14;

    @bottom-left {
        content: "MARGINOPTIMIZER  ·  B2B YIELD ENGINE";
        font-family: "Inter", "Helvetica Neue", Arial, sans-serif;
        font-size: 8pt;
        color: #475569;
        letter-spacing: 2.2pt;
    }
    @bottom-right {
        content: counter(page) "  /  " counter(pages);
        font-family: "JetBrains Mono", Menlo, monospace;
        font-size: 8.5pt;
        color: #94a3b8;
        letter-spacing: 1.2pt;
    }
}

@page cover {
    margin: 0;
    background: #0a0e14;
    @bottom-left { content: ""; }
    @bottom-right { content: ""; }
}
@page closing {
    margin: 0;
    background: #0a0e14;
    @bottom-left { content: ""; }
    @bottom-right { content: ""; }
}

/* --- GLOBAL ---------------------------------------------------------- */

html, body {
    font-family: "Inter", "Helvetica Neue", Arial, sans-serif;
    font-size: 13pt;
    line-height: 1.5;
    color: #e6edf3;
    background: #0a0e14;
    margin: 0;
    padding: 0;
    font-weight: 400;
}

strong { color: #f59e0b; font-weight: 600; }
em     { color: #60a5fa; font-style: normal; font-weight: 500; }

a { color: #60a5fa; text-decoration: none; }

/* --- SLIDE BASE ------------------------------------------------------ */

.slide {
    page-break-after: always;
    break-after: page;
    position: relative;
}
.slide:last-child { page-break-after: auto; }

/* --- SECTION (content) SLIDES --------------------------------------- */

.slide.section h1 {
    font-size: 26pt;
    font-weight: 700;
    letter-spacing: 1.8pt;
    color: #e6edf3;
    margin: 0 0 1mm;
    padding: 0 0 3.5mm;
    border-bottom: 0.4pt solid #1f2933;
    position: relative;
}
.slide.section h1::after {
    content: "";
    position: absolute;
    left: 0;
    bottom: -0.4pt;
    width: 22mm;
    height: 1.4pt;
    background: #f59e0b;
}
.slide.section h2 {
    font-size: 13pt;
    font-weight: 400;
    color: #94a3b8;
    letter-spacing: 0.3pt;
    margin: 0 0 8mm;
}

/* --- COVER SLIDE ----------------------------------------------------- */

.slide.cover { page: cover; padding: 24mm 22mm 20mm; }
.slide.cover h1 {
    font-size: 56pt;
    font-weight: 800;
    letter-spacing: -1.5pt;
    line-height: 1.05;
    color: #e6edf3;
    margin: 26mm 0 4mm;
}
.slide.cover h1::first-letter { color: #f59e0b; }
.slide.cover h2 {
    font-size: 18pt;
    font-weight: 400;
    color: #cbd5e1;
    letter-spacing: 0.2pt;
    margin: 0 0 2mm;
    max-width: 200mm;
}
.slide.cover h3 {
    font-size: 12.5pt;
    font-weight: 400;
    color: #60a5fa;
    text-transform: uppercase;
    letter-spacing: 3pt;
    margin: 6mm 0 0;
}
.slide.cover::before {
    content: "";
    position: absolute;
    top: 22mm;
    left: 22mm;
    width: 18mm;
    height: 1.6pt;
    background: #f59e0b;
}
.slide.cover::after {
    content: "CONFIDENTIAL  ·  2026";
    position: absolute;
    bottom: 14mm;
    left: 22mm;
    font-size: 8.5pt;
    letter-spacing: 2.5pt;
    color: #475569;
}

/* --- HERO BAND (metrics, no H1) ------------------------------------- */

.slide.band { padding-top: 28mm; }
.slide.band > p:first-of-type {
    text-transform: uppercase;
    letter-spacing: 3.5pt;
    font-size: 9.5pt;
    color: #60a5fa;
    margin: 0 0 6mm;
}
.slide.band ul {
    list-style: none;
    padding: 0;
    margin: 0;
    display: grid;
    grid-template-columns: 1fr 1fr;
    column-gap: 18mm;
    row-gap: 9mm;
}
.slide.band ul li {
    border-left: 1.4pt solid #f59e0b;
    padding: 1mm 0 1mm 6mm;
}
.slide.band ul li strong {
    display: block;
    font-size: 26pt;
    font-weight: 700;
    color: #e6edf3;
    letter-spacing: -0.5pt;
    line-height: 1.05;
    margin-bottom: 1.5mm;
}

/* --- CLOSING --------------------------------------------------------- */

.slide.closing {
    page: closing;
    padding: 0 22mm;
    text-align: left;
    display: block;
}
.slide.closing h1 {
    font-size: 48pt;
    font-weight: 800;
    letter-spacing: -1.2pt;
    color: #e6edf3;
    margin: 42mm 0 3mm;
}
.slide.closing h1::first-letter { color: #f59e0b; }
.slide.closing p {
    font-size: 15pt;
    color: #cbd5e1;
    margin: 0 0 12mm;
}
.slide.closing p strong { color: #f59e0b; font-weight: 500; }
.slide.closing p:last-of-type {
    font-size: 9pt;
    color: #475569;
    letter-spacing: 2.5pt;
    text-transform: uppercase;
    border-top: 0.4pt solid #1f2933;
    padding-top: 8mm;
    max-width: 120mm;
}

/* --- TYPOGRAPHY DETAILS --------------------------------------------- */

p { margin: 0 0 4mm; }

ul, ol { margin: 3mm 0 5mm 2mm; padding-left: 4mm; }
li { margin: 0 0 2.5mm; }
li::marker { color: #f59e0b; }

ol { padding-left: 6mm; }
ol > li { padding-left: 2mm; }

ul ul { margin: 2mm 0 2mm 0; }
ul ul li { margin: 0 0 1.5mm; color: #cbd5e1; font-size: 11.5pt; }
ul ul li::marker { color: #60a5fa; }

/* --- TABLES ---------------------------------------------------------- */

table {
    width: 100%;
    border-collapse: collapse;
    margin: 5mm 0 3mm;
    font-size: 11pt;
    background: #0d131a;
}
th {
    text-align: left;
    padding: 3mm 5mm;
    color: #60a5fa;
    font-weight: 600;
    letter-spacing: 0.4pt;
    text-transform: uppercase;
    font-size: 9.5pt;
    border-bottom: 1pt solid #1f2933;
}
td {
    padding: 2.6mm 5mm;
    color: #cbd5e1;
    border-bottom: 0.4pt solid #141a22;
    vertical-align: top;
}
tr:nth-child(even) td { background: #0f151c; }
td:first-child { color: #e6edf3; font-weight: 500; }
td strong, th strong { color: inherit; font-weight: 700; }

/* --- CODE ------------------------------------------------------------ */

code {
    font-family: "JetBrains Mono", Menlo, Consolas, monospace;
    font-size: 10.5pt;
    color: #f5d393;
    background: #141a22;
    padding: 0.6mm 1.8mm;
    border-radius: 1mm;
}
pre {
    background: #141a22;
    border-left: 2pt solid #f59e0b;
    padding: 4mm 5mm;
    font-size: 10pt;
    color: #e6edf3;
    margin: 4mm 0;
}
pre code { background: transparent; padding: 0; color: inherit; font-size: 10pt; }

/* --- BLOCKQUOTES ---------------------------------------------------- */

blockquote {
    border-left: 2pt solid #60a5fa;
    margin: 4mm 0;
    padding: 1mm 0 1mm 5mm;
    color: #cbd5e1;
    font-style: italic;
}

/* --- FIGURES & SVG GRAPHICS ----------------------------------------- */

figure { margin: 0; padding: 0; }
figure svg { display: block; width: 100%; height: auto; }

.slide.cover .cover-mark {
    position: absolute;
    right: 22mm;
    bottom: 22mm;
    width: 100mm;
    margin: 0;
    padding: 0;
    opacity: 0.98;
}

figure.chart, figure.flow, figure.diagram {
    margin: 4mm auto;
    text-align: center;
}
figure.chart    { max-width: 230mm; }
figure.flow     { max-width: 255mm; margin: 7mm auto 4mm; }
figure.diagram  { max-width: 255mm; margin: 3mm auto 5mm; }

/* When a band slide has a single figure, center it fully */
.slide.band figure.chart { margin-top: 6mm; }

/* Shrink tables slightly when they follow a diagram */
.slide.section figure + table { margin-top: 2mm; font-size: 10.5pt; }
.slide.section figure + table th { font-size: 9pt; padding: 2.4mm 5mm; }
.slide.section figure + table td { padding: 2.2mm 5mm; }
"""


def _strip_frontmatter(text: str) -> str:
    return _FRONTMATTER.sub("", text, count=1)


def _split_slides(body: str) -> list[str]:
    return [s.strip() for s in re.split(r"\n---\s*\n", body) if s.strip()]


def _classify(idx: int, total: int, slide_md: str) -> str:
    """Pick a slide class based on position + content shape.

    - cover:   first slide, H1 title present
    - closing: last slide, H1 title present (same pattern as cover but terminal)
    - band:    no H1 — treated as a hero metrics band
    - section: everything else (content with H1)
    """
    h1 = _H1.search(slide_md)
    if idx == 0 and h1:
        return "cover"
    if idx == total - 1 and h1:
        return "closing"
    if not h1:
        return "band"
    return "section"


def _render_slide(slide_md: str, slide_class: str) -> str:
    html = md.markdown(
        slide_md,
        extensions=["tables", "fenced_code", "attr_list", "sane_lists"],
        output_format="html5",
    )
    return f'<section class="slide {slide_class}">{html}</section>'


def _build_html(source: Path) -> str:
    text = source.read_text(encoding="utf-8")
    body = _strip_frontmatter(text)
    slides = _split_slides(body)
    rendered_parts = [
        _render_slide(s, _classify(i, len(slides), s)) for i, s in enumerate(slides)
    ]
    rendered = "\n".join(rendered_parts)
    return f"""<!doctype html>
<html lang="{source.stem[-2:]}"><head>
<meta charset="utf-8">
<title>{source.stem}</title>
<style>{_CSS}</style>
</head><body>{rendered}</body></html>"""


@click.command()
@click.option(
    "--in",
    "source",
    type=click.Path(exists=True, dir_okay=False, path_type=Path),
    required=True,
)
@click.option(
    "--out",
    "target",
    type=click.Path(dir_okay=False, path_type=Path),
    required=True,
)
def main(source: Path, target: Path) -> None:
    html = _build_html(source)
    HTML(string=html, base_url=str(source.parent)).write_pdf(target=str(target))
    click.echo(f"wrote {target} ({target.stat().st_size // 1024} KiB)")


if __name__ == "__main__":
    main()
