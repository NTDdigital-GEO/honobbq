# -*- coding: utf-8 -*-
"""Copy guard: block wording the 2026-10-23 audit found wrong, unverified or risky.

Scans visible text only (tags and URLs stripped), so the Toast URL slug "new-em"
or the 炎 character do not trip it. Add a rule here whenever a mistake is found,
so it can never be written back onto the site.
"""
import re, glob, html, os, sys

RULES = [  # (regex, why)
    (r"Hon[ōŌ]", "brand name standard is 'Hono Japanese BBQ' (client confirmed 2026-10-23)"),
    (r"75052", "wrong ZIP from the old Wix footer — the restaurant is 75252"),
    (r"\bsoft opening\b", "expired: opened ~2026-05-28"),
    (r"100\s*% American Wagyu", "unverified and contradicts the Japanese A5 in the Ruby tier"),
    (r"\bdrive[- ]?thru\b", "wrong Yelp attribute"),
    (r"\bNEW\s*-\s*EM\b", "internal Toast name"),
    (r"123 Yakiniku|ZIP: 12345|Pink Poppy", "Wix template leftovers"),
    (r"\b(best|#1|number one|world[- ]class|finest|the only)\b", "unsourced superlative (ads policy + GEO)"),
    (r"\bguarantee", "promise the business has not made"),
    (r"\[(N|NAME)\]", "unfilled placeholder from a PENDING item"),
]
problems, n = [], 0
for f in sorted(glob.glob("dist/**/*.html", recursive=True)):
    if "/_pending/" in f: continue            # internal review page quotes the questions on purpose
    n += 1
    s = open(f, encoding="utf-8").read()
    s = re.sub(r"<(script|style)[^>]*>.*?</\1>", " ", s, flags=re.S)
    attrs = " ".join(re.findall(r'(?:alt|content|title)="([^"]*)"', s))
    text = html.unescape(re.sub(r"<[^>]+>", " ", s)) + " " + html.unescape(attrs)
    for rx, why in RULES:
        for m in re.finditer(rx, text, re.I):
            ctx = text[max(0, m.start() - 40):m.end() + 40].replace("\n", " ")
            problems.append(f"{os.path.relpath(f, 'dist')}: «{m.group(0)}» — {why}\n      …{ctx.strip()}…")
if n == 0:
    print("✗ copy check scanned 0 files — run build.py first"); sys.exit(1)
if problems:
    print(f"✗ copy check: {len(problems)} problem(s) in {n} files"); [print("  ", p) for p in problems]; sys.exit(1)
print(f"✓ copy check: {n} files clean ({len(RULES)} rules)")
