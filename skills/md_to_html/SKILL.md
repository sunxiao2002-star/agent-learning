---
name: md-to-html
description: Convert Markdown documents to beautifully styled, standalone HTML pages with multiple preset themes and custom CSS support. Use when agent needs to (1) transform .md files into readable/presentable HTML, (2) generate styled documentation, reports, or articles from markdown, (3) create web-ready documents with a specific visual style, or (4) deploy markdown content as a static HTML page.
---

# Markdown to HTML Converter

Transform markdown into production-ready HTML with beautiful typography, responsive layouts, and optional features like syntax highlighting, math rendering, and table of contents.

## Quick Start

Run the conversion script:

```bash
python scripts/convert.py input.md --style minimal --output out.html
```

Or use the Python API directly:

```python
from scripts.convert import convert

html = convert(md_text, style="business", title="Report", toc=True, math=True)
```

## Preset Styles

Available built-in styles (located in `assets/styles/`):

| Style | Character | Best For |
|-------|-----------|----------|
| `minimal` | Clean, airy, card-based | General reading, blogs |
| `academic` | Formal, serif, justified | Papers, theses, research |
| `business` | Corporate, structured | Reports, memos, dashboards |
| `dark` | Night-mode, GitHub-like | Developer docs, long reading |
| `elegant` | Editorial, warm, refined | Magazines, portfolios, essays |
| `magazine` | Bold, high-contrast, modern | Articles, landing content |

### Selecting a Style

```bash
python scripts/convert.py input.md --style elegant --output report.html
```

Default style is `minimal` if not specified.

## CLI Options

| Flag | Description |
|------|-------------|
| `--style STYLE` | Preset style name |
| `--title TITLE` | HTML `<title>` and document heading |
| `--css FILE` | Path to custom CSS file (injected after preset) |
| `--math` | Enable KaTeX for LaTeX math (`$...$`, `$$...$$`) |
| `--toc` | Generate floating table of contents from H2/H3 |
| `--no-highlight` | Disable syntax highlighting |
| `-o, --output` | Output file path (default: same name with `.html`) |

## Custom CSS

Pass a custom CSS file to override or extend any preset:

```bash
python scripts/convert.py input.md --style minimal --css my-theme.css --output out.html
```

Custom CSS is injected after the preset CSS, so it can override any rule. Key selectors to target:

- `.markdown-body` -- main content container
- `h1, h2, h3` -- headings
- `blockquote` -- pull quotes / callouts
- `pre, code` -- code blocks
- `table, th, td` -- tables
- `#toc` -- floating table of contents

## Features

### Automatic Math Detection
If `--math` is set (or if LaTeX syntax is detected in the markdown), KaTeX CSS/JS is automatically included.

### Syntax Highlighting
Enabled by default via highlight.js. The `dark` style automatically uses the `github-dark` theme; others use `github`.

### Responsive Layout
All styles adapt to mobile, tablet, and desktop. The floating TOC hides on narrow viewports.

### Print-Friendly
Styles include `@media print` rules that remove backgrounds, shadows, and TOC for clean printing.

## File Structure

```
md-to-html/
├── SKILL.md
├── scripts/
│   └── convert.py          # Main converter script
└── assets/
    └── styles/
        ├── minimal.css
        ├── academic.css
        ├── business.css
        ├── dark.css
        ├── elegant.css
        └── magazine.css
```

## Dependencies

- `markdown` (Python package)

Install if missing: `pip install markdown`
