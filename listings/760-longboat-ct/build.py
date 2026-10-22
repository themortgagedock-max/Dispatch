"""Build index.html (a full, deployable document) from page.html (the artifact fragment).

page.html is the single source. It has no <!doctype>/<html>/<head>/<body> because the
claude.ai artifact host wraps it. This script wraps it the same way for Netlify,
Cloudflare Pages, or any static host, and adds the social/share meta tags.

Usage: python3 build.py
"""
from pathlib import Path

HERE = Path(__file__).resolve().parent
SRC = HERE / "page.html"
OUT = HERE / "index.html"

HEAD_EXTRA = """<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<meta name="theme-color" content="#0A1628">
<meta property="og:type" content="website">
<meta property="og:title" content="760 Longboat Ct, Longboat Key, FL 34228 | $840,000">
<meta property="og:description" content="A restored 1920 beach bungalow in the North End Village, with real post-sale taxes, flood and wind insurance ranges, and the all-in monthly cost.">
<meta name="twitter:card" content="summary">
<style>:root{padding-top:env(safe-area-inset-top,0px);padding-bottom:env(safe-area-inset-bottom,0px)}</style>
"""


def main() -> None:
    src = SRC.read_text(encoding="utf-8")
    split = src.index('<header class="bar"')
    head, body = src[:split], src[split:]
    doc = (
        "<!doctype html>\n<html lang=\"en\">\n<head>\n"
        + HEAD_EXTRA
        + head.strip()
        + "\n</head>\n<body>\n"
        + body.strip()
        + "\n</body>\n</html>\n"
    )
    OUT.write_text(doc, encoding="utf-8")
    print(f"wrote {OUT.name} ({len(doc):,} bytes)")


if __name__ == "__main__":
    main()
