"""TMD pre-ship QA sweep for this listing page (see the tmd-site-deploy skill, section 5).

Checks page.html and index.html for: em/en dashes in copy, banned AI words, wrong phone,
wrong name form, both NMLS IDs, stale loan limits, JSON-LD validity, and an exact
character-for-character match between FAQPage schema and the visible FAQ.

Usage: python3 qa.py   (exits non-zero on any failure)
"""
import html
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
BANNED = r"\b(unveil|unlock|elevate|leverage|optimi[sz]e|streamline|seamless|comprehensive|crucial|robust|delve|tapestry|in today's world|in conclusion)\b"
STALE_LIMITS = ["806,500", "766,550", "1,209,750", "929,850", "524,225"]


def visible_text(src: str) -> str:
    s = re.sub(r"<style.*?</style>", " ", src, flags=re.S)
    s = re.sub(r"<script(?![^>]*ld\+json).*?</script>", " ", s, flags=re.S)
    s = re.sub(r"<!--.*?-->", " ", s, flags=re.S)
    return html.unescape(re.sub(r"<[^>]+>", " ", s))


def check(path: Path) -> list[str]:
    src = path.read_text(encoding="utf-8")
    text = visible_text(src)
    fails = []
    for ch, name in (("—", "em dash"), ("–", "en dash")):
        if ch in text:
            fails.append(f"{name} in copy: ...{text[max(0, text.index(ch) - 40):text.index(ch) + 40]!r}")
    for m in re.finditer(BANNED, text, flags=re.I):
        fails.append(f"banned word: {m.group(0)!r}")
    if "563.1469" in src or "563-1469" in src:
        fails.append("client-only 563 phone number present")
    if re.search(r"Eli O\.", src):
        fails.append('"Eli O." name form present')
    for nmls in ("1983384", "376205"):
        if nmls not in src:
            fails.append(f"NMLS {nmls} missing")
    if "Equal Housing Opportunity" not in src:
        fails.append("Equal Housing Opportunity missing")
    for lim in STALE_LIMITS:
        if lim in src:
            fails.append(f"stale loan limit {lim}")

    blocks = re.findall(r'<script type="application/ld\+json">(.*?)</script>', src, flags=re.S)
    if not blocks:
        fails.append("no JSON-LD")
    faq_schema = []
    for b in blocks:
        try:
            data = json.loads(b)
        except json.JSONDecodeError as e:
            fails.append(f"JSON-LD does not parse: {e}")
            continue
        for node in data.get("@graph", [data]):
            if node.get("@type") == "FAQPage":
                faq_schema = [(q["name"], q["acceptedAnswer"]["text"]) for q in node["mainEntity"]]
    faq_html = [
        (html.unescape(q), html.unescape(a))
        for q, a in re.findall(r'<details name="faq"[^>]*><summary>(.*?)</summary><p>(.*?)</p></details>', src, flags=re.S)
    ]
    if faq_schema != faq_html:
        fails.append(f"FAQ schema/visible mismatch ({len(faq_schema)} schema vs {len(faq_html)} visible)")
        for i, (s_, h_) in enumerate(zip(faq_schema, faq_html)):
            if s_ != h_:
                fails.append(f"  first difference at item {i + 1}: {s_[0]!r}")
                break
    title = re.search(r"<title>(.*?)</title>", src)
    if not title or len(title.group(1)) > 60:
        fails.append("title missing or over 60 characters")
    return fails


def main() -> int:
    bad = 0
    for name in ("page.html", "index.html"):
        p = HERE / name
        if not p.exists():
            print(f"SKIP {name} (not built)")
            continue
        fails = check(p)
        print(f"{'PASS' if not fails else 'FAIL'} {name}")
        for f in fails:
            print("   ", f)
        bad += len(fails)
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
