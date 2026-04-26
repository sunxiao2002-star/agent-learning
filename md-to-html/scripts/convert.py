#!/usr/bin/env python3
"""
Markdown to HTML converter with beautiful preset styles.
Supports: minimal, academic, business, dark, elegant, magazine.
Usage:
    python convert.py input.md --style academic --output out.html
    python convert.py input.md --css custom.css --output out.html
"""
import argparse
import os
import sys
import re
import markdown
from pathlib import Path

PRESET_STYLES = {
    "minimal", "academic", "business", "dark", "elegant", "magazine"
}

KATEX_CSS = '<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/katex@0.16.9/dist/katex.min.css">'
KATEX_JS = '''
<script defer src="https://cdn.jsdelivr.net/npm/katex@0.16.9/dist/katex.min.js"></script>
<script defer src="https://cdn.jsdelivr.net/npm/katex@0.16.9/dist/contrib/auto-render.min.js"
    onload="renderMathInElement(document.body,{delimiters:[{left:'$$',right:'$$',display:true},{left:'$',right:'$',display:false}]});"></script>
'''

HLJS_CSS = '<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/styles/github.min.css">'
HLJS_CSS_DARK = '<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/styles/github-dark.min.css">'
HLJS_JS = '<script src="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/highlight.min.js"></script><script>hljs.highlightAll();</script>'


def load_preset_css(style: str) -> str:
    """Load built-in CSS for a preset style."""
    skill_dir = Path(__file__).parent.parent
    css_path = skill_dir / "assets" / "styles" / f"{style}.css"
    if css_path.exists():
        return css_path.read_text(encoding="utf-8")
    return ""


def detect_math(md_text: str) -> bool:
    """Detect if markdown contains LaTeX math."""
    return bool(re.search(r'\$\$.+?\$\$', md_text, re.DOTALL) or re.search(r'(?<!\$)\$(?!\$).+?\$', md_text, re.DOTALL))


def make_toc(html: str) -> str:
    """Generate a simple table of contents from h2/h3 headings."""
    headings = re.findall(r'<h([23]) id="([^"]+)">([^<]+)</h\1>', html)
    if not headings:
        return ""
    items = []
    for level, hid, title in headings:
        indent = "toc-h2" if level == "2" else "toc-h3"
        items.append(f'<a class="{indent}" href="#{hid}">{title}</a>')
    return '<nav id="toc"><div class="toc-title">目录</div>' + "\n".join(items) + "</nav>"


def convert(md_text: str, style: str = "minimal", title: str = "", custom_css: str = "", math: bool = False, toc: bool = False, no_highlight: bool = False) -> str:
    """Convert markdown text to a full HTML document."""
    md = markdown.Markdown(extensions=[
        "extra", "toc", "tables", "fenced_code", "nl2br", "sane_lists",
    ])

    body = md.convert(md_text)
    md.reset()

    resolved_title = title or "Document"
    has_math = math or detect_math(md_text)
    is_dark = style in ("dark",)

    preset_css = load_preset_css(style)
    hl_css = HLJS_CSS_DARK if is_dark else HLJS_CSS

    resources = [KATEX_CSS] if has_math else []
    if not no_highlight:
        resources.append(hl_css)

    toc_html = ""
    if toc:
        md2 = markdown.Markdown(extensions=["extra", "toc", "tables", "fenced_code", "nl2br", "sane_lists"])
        body_with_ids = md2.convert(md_text)
        toc_html = make_toc(body_with_ids)
        body = body_with_ids

    parts = [
        "<!DOCTYPE html>",
        '<html lang="zh-CN">',
        "<head>",
        '<meta charset="UTF-8">',
        '<meta name="viewport" content="width=device-width, initial-scale=1.0">',
        f'<title>{resolved_title}</title>',
        "\n".join(resources),
        "<style>",
        preset_css,
        custom_css,
        "</style>",
        "</head>",
        "<body>",
    ]

    if toc_html:
        parts.append(toc_html)

    parts.append('<main class="markdown-body">')
    parts.append(body)
    parts.append("</main>")

    if has_math:
        parts.append(KATEX_JS)
    if not no_highlight:
        parts.append(HLJS_JS)

    parts.append("</body></html>")
    return "\n".join(parts)


def main():
    parser = argparse.ArgumentParser(description="Convert Markdown to beautiful HTML")
    parser.add_argument("input", help="Input markdown file path")
    parser.add_argument("-o", "--output", help="Output HTML file path")
    parser.add_argument("--style", default="minimal", choices=sorted(PRESET_STYLES), help="Preset visual style")
    parser.add_argument("--title", default="", help="HTML document title")
    parser.add_argument("--css", default="", help="Path to custom CSS file to inject")
    parser.add_argument("--math", action="store_true", help="Enable KaTeX math rendering")
    parser.add_argument("--toc", action="store_true", help="Generate table of contents")
    parser.add_argument("--no-highlight", action="store_true", help="Disable syntax highlighting")
    args = parser.parse_args()

    if not os.path.exists(args.input):
        print(f"Error: File not found: {args.input}", file=sys.stderr)
        sys.exit(1)

    md_text = Path(args.input).read_text(encoding="utf-8")

    custom_css = ""
    if args.css:
        if not os.path.exists(args.css):
            print(f"Warning: CSS file not found: {args.css}", file=sys.stderr)
        else:
            custom_css = Path(args.css).read_text(encoding="utf-8")

    html = convert(
        md_text,
        style=args.style,
        title=args.title,
        custom_css=custom_css,
        math=args.math,
        toc=args.toc,
        no_highlight=args.no_highlight,
    )

    out_path = args.output or str(Path(args.input).with_suffix(".html"))
    Path(out_path).write_text(html, encoding="utf-8")
    print(f"Converted: {args.input} -> {out_path}")


if __name__ == "__main__":
    main()
