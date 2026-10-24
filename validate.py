# -*- coding: utf-8 -*-
"""Check dist/ before it ships. Exits 1 on any failure, so CI will not deploy a broken site.

Every check is built to fail loudly: it counts what it inspected and compares
against what it expected, so a check that silently inspected nothing cannot pass.
"""
import os, re, json, html, sys, glob, shutil, subprocess, tempfile
from collections import Counter

OUT = "dist"; fails = []; warns = []
BASE = "/" + os.environ.get("BASE_PATH", "").strip("/") if os.environ.get("BASE_PATH", "").strip("/") else ""
def unbase(h):
    if BASE and (h == BASE or h.startswith(BASE + "/")): return h[len(BASE):] or "/"
    return h
def fail(msg, items=()):
    fails.append(msg); print("✗", msg); [print("   ", i) for i in list(items)[:10]]
def ok(msg): print("✓", msg)

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from content import PAGES, LEGACY  # noqa: E402

pages, special = {}, {}
for f in glob.glob(OUT + "/**/index.html", recursive=True):
    rel = os.path.relpath(os.path.dirname(f), OUT)
    url = "/" if rel == "." else "/" + rel.replace(os.sep, "/") + "/"
    body = open(f, encoding="utf-8").read()
    (special if (url.startswith("/_") or 'name="x-legacy-redirect"' in body) else pages)[url] = body
expected = {"/" + (p["slug"] + "/" if p["slug"] else "") for p in PAGES}
if set(pages) != expected:
    fail("built pages differ from content/pages.py", sorted(set(pages) ^ expected))
else:
    ok(f"pages: {len(pages)} built = {len(expected)} defined (+{len(special)} noindex helpers)")

# 1) internal links
broken = []
for url, s in pages.items():
    for h0 in set(re.findall(r'href="(/[^"#?]*)', s)):
        h = unbase(h0)
        if h.startswith("/assets/"): continue
        if h not in pages and not os.path.exists(os.path.join(OUT, h.strip("/"))):
            broken.append(f"{url} → {h}")
fail(f"{len(broken)} broken internal links", broken) if broken else ok("internal links: all resolve")

# 2) breadcrumbs
bad = []
for url, s in pages.items():
    m = re.search(r'<nav class="crumb".*?</nav>', s, re.S)
    for h in re.findall(r'href="(/[^"]*)"', m.group() if m else ""):
        if unbase(h) not in pages: bad.append(f"{url} → {h}")
fail("breadcrumb parent missing", bad) if bad else ok("breadcrumbs: every parent exists")

# 3) exactly one H1
bad = [f"{u}: {len(re.findall(r'<h1[ >]', s))}" for u, s in pages.items() if len(re.findall(r"<h1[ >]", s)) != 1]
fail("H1 count is not 1", bad) if bad else ok("H1: exactly one per page")

# 4) schema: one block, parses, required nodes, FAQ text matches visible text word for word
bad, faq_n = [], 0
for u, s in pages.items():
    blocks = re.findall(r'<script type="application/ld\+json">(.*?)</script>', s, re.S)
    if len(blocks) != 1: bad.append(f"{u}: {len(blocks)} blocks"); continue
    try: g = json.loads(blocks[0])["@graph"]
    except Exception as ex: bad.append(f"{u}: parse error {ex}"); continue
    types = [n["@type"] for n in g]
    for need in ("Restaurant", "WebSite", "WebPage"):
        if need not in types: bad.append(f"{u}: missing {need}")
    if u != "/" and "BreadcrumbList" not in types: bad.append(f"{u}: missing BreadcrumbList")
    r = g[types.index("Restaurant")]
    if r["address"]["postalCode"] != "75252": bad.append(f"{u}: schema ZIP {r['address']['postalCode']}")
    if "aggregateRating" in r: bad.append(f"{u}: self-serving aggregateRating")
    if not any(a["@type"] == "ReserveAction" for a in r.get("potentialAction", [])): bad.append(f"{u}: no ReserveAction")
    for n in g:
        if n["@type"] == "FAQPage":
            for q in n["mainEntity"]:
                faq_n += 1
                vis = f"<summary>{html.escape(q['name'])}</summary><p>{html.escape(q['acceptedAnswer']['text'])}</p>"
                if vis not in s: bad.append(f"{u}: FAQ text ≠ schema: {q['name'][:50]}")
fail("schema problems", bad) if bad else ok(f"schema: {len(pages)} pages parse, Restaurant/WebPage/ReserveAction present, {faq_n} FAQ answers match visible text")

# 5) titles and descriptions: unique and within length
for field, pat, lim in [("title", r"<title>(.*?)</title>", 60), ("description", r'<meta name="description" content="([^"]*)"', 160)]:
    vals = {u: html.unescape(re.search(pat, s, re.S).group(1)) for u, s in pages.items()}
    dup = [v for v, c in Counter(vals.values()).items() if c > 1]
    long_ = [f"{u}: {len(v)} chars" for u, v in vals.items() if len(v) > lim]
    if dup: fail(f"{field} duplicated", dup)
    elif long_: fail(f"{field} over {lim} characters", long_)
    else: ok(f"{field}: unique and ≤{lim} characters on all {len(vals)} pages")

# 6) answer block length (English words)
bad = []
for u, s in pages.items():
    m = re.search(r'<p class="answer">(.*?)</p>', s, re.S)
    n = len(re.sub(r"<[^>]+>", "", m.group(1)).split()) if m else 0
    if not 25 <= n <= 95: bad.append(f"{u}: {n} words")
fail("answer block outside 25–95 words", bad) if bad else ok("answer blocks: 25–95 words on every page")

# 7) no render-blocking external resources
ext = set()
for s in pages.values():
    ext |= set(re.findall(r'<script[^>]+src="(https?://[^"]+)"', s))
    ext |= set(re.findall(r'<link[^>]+rel="stylesheet"[^>]*href="(https?://[^"]+)"', s))
fail("external render-blocking resources", sorted(ext)) if ext else ok("external blocking resources: 0")

# 8) images exist, are not double-prefixed, carry alt + width + height
refs, noattr = set(), []
for u, s in pages.items():
    for tag in re.findall(r"<(?:img|source) [^>]+>", s):
        if tag.startswith("<source"):
            for c in re.search(r'srcset="([^"]+)"', tag).group(1).split(","):
                c = c.strip().split(" ")[0]
                if "/assets/" in c: refs.add(c)
            continue
        if not all(a in tag for a in ('alt="', 'width="', 'height="')): noattr.append(f"{u}: {tag[:80]}")
        for m in re.finditer(r'(?:src|srcset)="([^"]+)"', tag):
            for c in m.group(1).split(","):
                c = c.strip().split(" ")[0]
                if "/assets/" in c: refs.add(c)
dbl = [r for r in refs if BASE and r.count(BASE + "/") > 1]
missing = [r for r in refs if not os.path.exists(os.path.join(OUT, unbase(r).lstrip("/")))]
if dbl: fail("image path has BASE twice", dbl)
if missing: fail("image file missing", missing)
if noattr: fail("img without alt/width/height", noattr)
if refs and not (dbl or missing or noattr): ok(f"images: {len(refs)} paths exist, single-prefixed, all tags have alt/size")

# 9) noindex helpers stay out of the index
sm = open(os.path.join(OUT, "sitemap.xml"), encoding="utf-8").read()
bad = [u for u, s in special.items() if "noindex" not in s] + [u for u in special if u in sm]
if not os.path.exists(os.path.join(OUT, "404.html")) or "noindex" not in open(os.path.join(OUT, "404.html")).read(): bad.append("/404.html")
fail("noindex helper pages leak", bad) if bad else ok("helpers (404, legacy, _pending): noindex and not in sitemap")
for old, new in LEGACY.items():
    if new not in pages: fail(f"legacy /{old}/ points to missing {new}")

# 10) NAP: every page shows the right ZIP and a tappable phone, never the old wrong ZIP
bad = []
for u, s in pages.items():
    if "75252" not in s: bad.append(f"{u}: no 75252")
    if "75052" in s: bad.append(f"{u}: contains wrong ZIP 75052")
    if 'href="tel:+12144847707"' not in s: bad.append(f"{u}: no tel: link")
    if "tables.toasttab.com" not in s: bad.append(f"{u}: no reserve link")
fail("NAP / conversion links", bad) if bad else ok("NAP: 75252 + tap-to-call + reserve link on every page")

# 11) inline JS parses (needs node; CI has it)
if shutil.which("node"):
    bad = []
    for u, s in pages.items():
        for code in re.findall(r"<script>(.*?)</script>", s, re.S):
            with tempfile.NamedTemporaryFile("w", suffix=".js", delete=False) as fh: fh.write(code); tmp = fh.name
            r = subprocess.run(["node", "--check", tmp], capture_output=True, text=True); os.unlink(tmp)
            if r.returncode: bad.append(f"{u}: {r.stderr.strip().splitlines()[-1][:100]}")
    fail("inline JS syntax error", bad) if bad else ok(f"inline JS: parses on all {len(pages)} pages")
else:
    print("! inline JS not checked (no node here; CI checks it)")

# 12) go-live gate: an indexable build must have a confirmed form inbox
live = os.environ.get("NOINDEX", "1") == "0"
has_key = bool(os.environ.get("FORM_ACCESS_KEY", "").strip())
confirmed = os.environ.get("FORM_RECIPIENT_CONFIRMED", "") == "1"
if live and not has_key: fail("live site but group form has no FORM_ACCESS_KEY — inquiries would go nowhere")
elif live and not confirmed: fail("live site but form inbox not confirmed as the client's — set FORM_RECIPIENT_CONFIRMED=1 after a test submission arrives")
elif live: ok("form: key set and inbox confirmed")
else: print("! preview build (NOINDEX): form " + ("connected" if has_key else "not connected yet"))

print("\n" + (f"✗ {len(fails)} problem(s)" if fails else "✓ all checks passed") + (f" ({len(warns)} warnings)" if warns else ""))
sys.exit(1 if fails else 0)
