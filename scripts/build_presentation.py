"""Render a Marp markdown deck to a print-quality PDF via weasyprint.

We do not call `marp-cli` (Node, not installed). Instead: strip the YAML
frontmatter, split on `\n---\n` slide separators, render each slide to
HTML with the `markdown` library, and stitch the slides into a single
document with a `@page` size and per-slide `page-break-after: always`.

Styling targets the `theme: dark` frontmatter intent — dark background,
light text, accent colour on strong/headings — but is not a pixel-perfect
Marp reproduction. It is a handout-grade PDF for sharing, not a stage
deck.

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

_CSS = """
@page {
    size: 297mm 167mm;  /* 16:9 landscape, ~ slide shape */
    margin: 14mm 18mm;
    background: #111418;
}

html, body {
    font-family: "Inter", "Helvetica Neue", Arial, sans-serif;
    color: #e8ecf1;
    background: #111418;
    line-height: 1.45;
    font-size: 14pt;
}

.slide {
    page-break-after: always;
    break-after: page;
    min-height: 100%;
}
.slide:last-child { page-break-after: auto; }

h1 { font-size: 34pt; color: #7dd3fc; margin: 0 0 8mm; letter-spacing: 1px; }
h2 { font-size: 22pt; color: #cbd5e1; margin: 0 0 4mm; font-weight: 500; }
h3 { font-size: 16pt; color: #94a3b8; margin: 0 0 6mm; font-weight: 400; }

strong { color: #fbbf24; }
em { color: #a5b4fc; font-style: normal; }

ul, ol { margin: 4mm 0 4mm 6mm; padding: 0; }
li { margin: 0 0 2mm; }

p { margin: 0 0 4mm; }

table {
    width: 100%;
    border-collapse: collapse;
    margin: 4mm 0;
    font-size: 12pt;
}
th, td {
    padding: 2.5mm 4mm;
    border-bottom: 0.5pt solid #2a3441;
    text-align: left;
    vertical-align: top;
}
th { color: #7dd3fc; font-weight: 600; }

code {
    font-family: "JetBrains Mono", "Menlo", monospace;
    background: #1e242c;
    color: #f5d393;
    padding: 0.5mm 1.5mm;
    border-radius: 1mm;
    font-size: 12pt;
}
pre {
    background: #1e242c;
    border-left: 2pt solid #7dd3fc;
    padding: 3mm 4mm;
    font-size: 11pt;
    overflow: hidden;
}
pre code { background: transparent; padding: 0; color: #e8ecf1; }

blockquote {
    border-left: 3pt solid #fbbf24;
    margin: 4mm 0;
    padding: 1mm 5mm;
    color: #cbd5e1;
    font-style: italic;
}

.pagenum {
    position: fixed;
    bottom: 6mm;
    right: 10mm;
    color: #475569;
    font-size: 9pt;
}
"""


def _split_slides(body: str) -> list[str]:
    """Break on a line containing only `---`, matching Marp's slide separator."""
    return [s.strip() for s in re.split(r"\n---\s*\n", body) if s.strip()]


def _render_slide(slide_md: str) -> str:
    html = md.markdown(
        slide_md,
        extensions=["tables", "fenced_code", "attr_list"],
        output_format="html5",
    )
    return f'<section class="slide">{html}</section>'


def _build_html(source: Path) -> str:
    text = source.read_text(encoding="utf-8")
    body = _FRONTMATTER.sub("", text, count=1)
    slides = _split_slides(body)
    rendered = "\n".join(_render_slide(s) for s in slides)
    return f"""<!doctype html>
<html><head><meta charset="utf-8"><title>{source.stem}</title>
<style>{_CSS}</style></head>
<body>{rendered}</body></html>"""


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
