# -*- coding: utf-8 -*-
"""Build the Hono Japanese BBQ site into dist/.

    python3 build.py                     # preview build (noindex) for local checks
    SITE_URL=https://www.honobbq.com NOINDEX=0 python3 build.py   # production

Content lives in content/; this file is templates, schema and output.
"""
import os, re, json, shutil, hashlib, html
from content import PAGES, NAV, LEGACY, BIZ, PENDING, CONFIRMED
from content.facts import HOURS, TIERS, LUNCH
from content.pages import FAQ_GROUPS, faq_general

OUT = "dist"
TODAY = "2026-10-23"

# ── settings (environment variables; see README) ──
# Default is noindex. Forgetting to set it publishes a half-built site to Google,
# which is far worse than a preview that stays hidden a little too long.
NOINDEX = os.environ.get("NOINDEX", "1") != "0"
_SITE_FALLBACK = "https://example.invalid"
SITE = os.environ.get("SITE_URL", _SITE_FALLBACK).rstrip("/")
BASE = "/" + os.environ.get("BASE_PATH", "").strip("/") if os.environ.get("BASE_PATH", "").strip("/") else ""
if SITE == _SITE_FALLBACK and not NOINDEX:
    raise SystemExit("✗ NOINDEX=0 needs SITE_URL too, or canonical/sitemap/schema point at the wrong domain.\n"
                     "  e.g. SITE_URL=https://www.honobbq.com NOINDEX=0 python3 build.py")

# GTM only — GA4, Google Ads, Meta and TikTok tags live inside the container, so they
# are never installed twice. Empty until the container exists; dataLayer events fire anyway.
GTM_ID = os.environ.get("GTM_ID", "").strip()
GSC_VERIFY = os.environ.get("GSC_VERIFY", "").strip()
# Group-inquiry form (Web3Forms). The key lives in a repo secret, never in the code.
FORM_KEY = os.environ.get("FORM_ACCESS_KEY", "").strip()
FORM_ENDPOINT = "https://api.web3forms.com/submit"

def e(s): return html.escape(str(s), quote=True)
def absu(path): return SITE + BASE + path

def css_version():
    return hashlib.md5(open("assets/site.css", "rb").read()).hexdigest()[:8]
CSSV = css_version()
IMG = json.load(open("assets/img/_meta.json"))

def img_tag(slug, alt, sizes="(max-width:760px) 100vw, 50vw", eager=False, cls=""):
    """Responsive <img>. Landscape photos ship 800/1600, portrait 800/900."""
    files = sorted((k for k in IMG if re.fullmatch(rf"{slug}-\d+\.jpg", k)), key=lambda k: IMG[k][0])
    if not files: raise SystemExit(f"✗ no image files for {slug}")
    big = files[-1]; w, h = IMG[big]
    srcset = ", ".join(f"/assets/img/{f} {IMG[f][0]}w" for f in files)
    load = 'fetchpriority="high"' if eager else 'loading="lazy" decoding="async"'
    return (f'<img class="{cls}" src="/assets/img/{big}" srcset="{srcset}" sizes="{sizes}" '
            f'width="{w}" height="{h}" alt="{e(alt)}" {load}>')

def gtm_head():
    if not GTM_ID: return ""
    return ("<script>(function(w,d,s,l,i){w[l]=w[l]||[];w[l].push({'gtm.start':new Date().getTime(),event:'gtm.js'});"
            "var f=d.getElementsByTagName(s)[0],j=d.createElement(s),dl=l!='dataLayer'?'&l='+l:'';j.async=true;"
            "j.src='https://www.googletagmanager.com/gtm.js?id='+i+dl;f.parentNode.insertBefore(j,f);"
            f"}})(window,document,'script','dataLayer','{GTM_ID}');</script>")

def gtm_body():
    if not GTM_ID: return ""
    return (f'<noscript><iframe src="https://www.googletagmanager.com/ns.html?id={GTM_ID}" height="0" width="0" '
            'style="display:none;visibility:hidden"></iframe></noscript>')

# ── schema ──
RID = "/#restaurant"

def restaurant_node():
    return {
        "@type": "Restaurant", "@id": absu(RID), "name": BIZ["name"], "legalName": BIZ["legal_name"],
        "url": absu("/"), "telephone": BIZ["tel_schema"],
        "description": "All-you-can-eat Japanese BBQ (yakiniku) in North Dallas with wagyu, Japanese A5 wagyu, sushi, izakaya plates and a full bar.",
        "image": [absu("/assets/img/dining-room-1600.jpg"), absu("/assets/img/storefront-900.jpg")],
        "logo": absu("/assets/img/mark-512.png"),
        "servesCuisine": ["Japanese", "Yakiniku", "Japanese BBQ", "Sushi", "Izakaya"],
        "priceRange": "$$$",
        "address": {"@type": "PostalAddress", "streetAddress": BIZ["street"], "addressLocality": BIZ["city"],
                    "addressRegion": BIZ["region"], "postalCode": BIZ["zip"], "addressCountry": "US"},
        "geo": {"@type": "GeoCoordinates", "latitude": BIZ["lat"], "longitude": BIZ["lng"]},
        "hasMap": BIZ["maps"],
        "openingHoursSpecification": [{"@type": "OpeningHoursSpecification", "dayOfWeek": d, "opens": o, "closes": c}
                                      for _, d, o, c, _ in HOURS],
        "hasMenu": {"@id": absu("/menu/#menu")},
        "acceptsReservations": True,
        "potentialAction": [
            {"@type": "ReserveAction",
             "target": {"@type": "EntryPoint", "urlTemplate": BIZ["reserve"],
                        "actionPlatform": ["http://schema.org/DesktopWebPlatform", "http://schema.org/MobileWebPlatform"]},
             "result": {"@type": "FoodEstablishmentReservation", "name": "Reserve a table at Hono Japanese BBQ"}},
            {"@type": "OrderAction",
             "target": {"@type": "EntryPoint", "urlTemplate": BIZ["order"],
                        "actionPlatform": ["http://schema.org/DesktopWebPlatform", "http://schema.org/MobileWebPlatform"]},
             "deliveryMethod": "http://purl.org/goodrelations/v1#DeliveryModePickUp"},
        ],
        "amenityFeature": [{"@type": "LocationFeatureSpecification", "name": n, "value": True} for n in
                           ["Tabletop grill at every table", "Full bar", "Happy hour", "Takeout",
                            "Group dining (6+ guests, 110 minutes)", "Wheelchair accessible entrance"]
                           + (["Covered patio"] if "patio" in CONFIRMED else [])],
        # Deliberately no aggregateRating: Google does not allow a business to mark up its own reviews.
        "sameAs": [u for u in [BIZ["instagram"], BIZ["tiktok"], BIZ["yelp"], BIZ["facebook"]] if u],
    }

def menu_node():
    return {"@type": "Menu", "@id": absu("/menu/#menu"), "name": "Hono Japanese BBQ Menu", "url": absu("/menu/"),
            "inLanguage": "en-US",
            "hasMenuSection": [
                {"@type": "MenuSection", "name": "AYCE Dinner",
                 "description": "All-you-can-eat Japanese BBQ, priced per person. Each tier includes the tiers below it.",
                 "hasMenuItem": [{"@type": "MenuItem", "name": f'{t["name"]} Tier AYCE', "description": t["adds"],
                                  "offers": {"@type": "Offer", "price": str(t["price"]), "priceCurrency": "USD"}} for t in TIERS]},
                {"@type": "MenuSection", "name": "AYCE Lunch", "description": f'{LUNCH["days"]}, {LUNCH["time"]}.',
                 "hasMenuItem": [{"@type": "MenuItem", "name": "AYCE Lunch",
                                  "offers": {"@type": "Offer", "price": str(LUNCH["price"]), "priceCurrency": "USD"}}]}]}

def faq_node(pairs, url):
    return {"@type": "FAQPage", "@id": absu(url + "#faq"),
            "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in pairs]}

def build_schema(p):
    url = "/" + (p["slug"] + "/" if p["slug"] else "")
    page = {"@type": "WebPage", "@id": absu(url + "#webpage"), "url": absu(url), "name": p["title"],
            "description": p["desc"], "isPartOf": {"@id": absu("/#website")}, "about": {"@id": absu(RID)},
            "inLanguage": "en-US", "dateModified": TODAY}
    graph = [restaurant_node(),
             {"@type": "WebSite", "@id": absu("/#website"), "name": BIZ["name"], "url": absu("/"), "publisher": {"@id": absu(RID)}},
             page]
    if p.get("crumbs"):
        bc = [{"@type": "ListItem", "position": 1, "name": "Home", "item": absu("/")}] + [
            {"@type": "ListItem", "position": i + 2, "name": n, "item": absu(h)} for i, (n, h) in enumerate(p["crumbs"])]
        graph.append({"@type": "BreadcrumbList", "@id": absu(url + "#breadcrumb"), "itemListElement": bc})
        page["breadcrumb"] = {"@id": absu(url + "#breadcrumb")}
    if p["slug"] == "menu": graph.append(menu_node())
    if p["slug"] == "faq":
        graph.append(faq_node([qa for _, qs in faq_general() for qa in qs], url))
    if p["slug"] == "groups":
        graph.append(faq_node(FAQ_GROUPS, url))
        graph.append({"@type": "Service", "@id": absu("/groups/#service"), "name": "Group dining at Hono Japanese BBQ",
                      "serviceType": "Group dining", "provider": {"@id": absu(RID)},
                      "areaServed": {"@type": "City", "name": "Dallas"},
                      "description": "All-you-can-eat Japanese BBQ for groups of six or more, with 110 minutes of dining time.",
                      "hasOfferCatalog": {"@type": "OfferCatalog", "name": "Group AYCE tiers", "itemListElement": [
                          {"@type": "Offer", "name": f'{t["name"]} tier (per person)', "price": str(t["price"]), "priceCurrency": "USD"}
                          for t in TIERS]}})
    return json.dumps({"@context": "https://schema.org", "@graph": graph}, ensure_ascii=False, indent=1)

# ── page pieces ──
def header(cur):
    cur_attr = ' aria-current="page"'
    links = "".join(f'<a href="{h}"{cur_attr if h == cur else ""}>{e(t)}</a>' for h, t in NAV)
    return f'''<header class="top"><div class="wrap bar">
<a class="brand" href="/"><img src="/assets/img/logo-white.png" width="480" height="249" alt="Hono Japanese BBQ"></a>
<nav class="nav" aria-label="Main">{links}</nav>
<a class="btn btn-gold" data-track="reserve" data-place="header" href="{e(BIZ["reserve"])}">Reservations</a>
</div></header>'''

def crumbs(p):
    if not p.get("crumbs"): return ""
    items = '<a href="/">Home</a>' + "".join(f' <span aria-hidden="true">/</span> <a href="{h}">{e(n)}</a>' for n, h in p["crumbs"])
    return f'<nav class="crumb" aria-label="Breadcrumb">{items}</nav>'

def hero_h1(p):
    """Render the H1 as unbreakable phrases so lines break only where intended
    (e.g. "Japanese BBQ" and "in North Dallas" always stay together). The text is unchanged.
    In the photo hero each outer group is forced onto its own line; on plain page heads
    groups stay inline and only wrap between phrases when the screen is too narrow."""
    lines = p.get("h1_lines")
    if not lines: return e(p["h1"])
    if " ".join(w for line in lines for w in line) != p["h1"]:
        raise SystemExit(f"✗ h1_lines do not spell the H1 exactly: {p['h1']}")
    return " ".join('<span class="h1l">' + " ".join(f'<span class="nb">{e(w)}</span>' for w in line) + "</span>" for line in lines)

def hero(p):
    """Ad landing hero: proof, the H1 that echoes the ad, the offer, one primary CTA, then the address.
    Everything a paid visitor needs sits above the fold on a phone; Fogo's visual language is kept."""
    if p.get("hero"):
        f = p["hero"]
        if p.get("cta") == "plan":
            primary = '<a class="btn btn-p big" href="#plan">Plan a Group Dinner</a>'
        else:
            primary = f'<a class="btn btn-p big" data-track="reserve" data-place="hero" href="{e(BIZ["reserve"])}">Reserve a Table</a>'
        # each phrase is its own unbreakable span, so "D Magazine" or "from noon" never split across lines
        proof = ('<p class="proof">' + ' <i>·</i> '.join(f"<span>{e(x)}</span>" for x in p["proof"].split(" · ")) + "</p>") if p.get("proof") else ""
        offer = ('<ul class="offer">' + "".join(f"<li>{e(o)}</li>" for o in p["offer"]) + "</ul>") if p.get("offer") else ""
        return f'''<section class="hero">{img_tag(f["img"], f["alt"], sizes="100vw", eager=True, cls="hero-img")}
<div class="hero-in wrap">{proof}<h1>{hero_h1(p)}</h1>{offer}
<div class="cta-row center">{primary}<a class="btn btn-ghost big" href="tel:{BIZ["tel_href"]}">Call {e(BIZ["tel_display"])}</a></div>
<p class="hero-addr"><span>{e(BIZ["street"])}, {e(BIZ["city"])}</span> <i>·</i> <span>Open daily from noon</span></p></div></section>'''
    return f'<section class="pagehead"><div class="wrap">{crumbs(p)}<h1>{hero_h1(p)}</h1></div></section>'

def reserve_box():
    """Fogo's cream 'Reserve a Table' panel directly under the hero (home page)."""
    rows = "".join(f"<li><span>{e(l)}</span><b>{e(d)}</b></li>" for l, _, _, _, d in HOURS)
    return f'''<section class="resbox-wrap"><div class="wrap"><div class="resbox">
<div><h2>Reserve a Table</h2><p class="resplace">North Dallas, Texas · Preston &amp; Frankford</p>
<ul class="reshours">{rows}</ul></div>
<div class="resact"><a class="btn btn-p wide" data-track="reserve" data-place="resbox" href="{e(BIZ["reserve"])}">Book on Toast</a>
<a class="btn btn-line wide" href="tel:{BIZ["tel_href"]}">Call {e(BIZ["tel_display"])}</a>
<a class="btn btn-line wide" data-track="order" data-place="resbox" href="{e(BIZ["order"])}">Order Takeout</a></div>
</div></div></section>'''

def intro(p):
    """Answer block on white. Hero pages get their breadcrumb and brand line here (the H1 is in the hero)."""
    top = ""
    if p.get("hero"):
        kick = f'<p class="label">{e(p["kicker"])}</p>' if p.get("kicker") else ""
        top = crumbs(p) + kick
    return f'<section class="sec intro"><div class="wrap narrow">{top}<p class="answer">{p["answer"]}</p></div></section>'

def faq_list(pairs):
    return '<div class="faq">' + "".join(
        f'<details><summary>{e(q)}</summary><p>{e(a)}</p></details>' for q, a in pairs) + "</div>"

def form_html(title):
    status = "" if FORM_KEY else '<p class="formnote">Preview: this form is not connected to an inbox yet and will not send.</p>'
    return f'''<section class="sec" id="plan"><div class="wrap narrow"><h2>{e(title)}</h2>
<p>Tell us the date and the size of your group and we'll get back to you to confirm. Prefer to talk? Call
<a href="tel:{BIZ["tel_href"]}">{e(BIZ["tel_display"])}</a>.</p>{status}
<form id="groupForm" class="form" method="POST" action="{FORM_ENDPOINT}" novalidate>
<input type="hidden" name="access_key" value="{e(FORM_KEY)}">
<input type="hidden" name="subject" value="Group dining inquiry — honobbq.com">
<input type="hidden" name="from_name" value="Hono website">
<input type="hidden" name="ad_source" value=""><input type="hidden" name="click_id" value="">
<input type="hidden" name="landing_page" value="">
<input type="checkbox" name="botcheck" class="hp" tabindex="-1" autocomplete="off">
<label>Name*<input name="name" required autocomplete="name"></label>
<label>Phone*<input name="phone" type="tel" required autocomplete="tel"></label>
<label>Email<input name="email" type="email" autocomplete="email"></label>
<label>Date*<input name="date" type="date" required></label>
<label>Time<input name="time" type="time"></label>
<label>Party size*<input name="party_size" type="number" min="2" max="200" required></label>
<label>Tier<select name="tier"><option>Not sure yet</option><option>Gold — $49</option><option>Platinum — $65</option><option>Ruby — $79</option></select></label>
<label>Occasion<select name="occasion"><option>Birthday</option><option>Team dinner</option><option>Graduation</option><option>Family celebration</option><option>Other</option></select></label>
<label class="full">Notes<textarea name="notes" rows="3"></textarea></label>
<button class="btn btn-p full" type="submit">Send inquiry</button>
<p id="formStatus" class="formstatus full" hidden></p></form></div></section>'''

def block(b):
    kind = b[0]
    if kind == "raw": return f'<div class="wrap">{b[1]}</div>'
    if kind.startswith("section"):
        alt = " alt" if "alt" in kind else ""
        return f'<section class="sec{alt}"><div class="wrap"><h2>{e(b[1])}</h2>{b[2]}</div></section>'
    if kind == "split":
        f = b[3]
        return (f'<section class="sec"><div class="wrap split"><div><h2>{e(b[1])}</h2>{b[2]}</div>'
                f'<figure>{img_tag(f["img"], f["alt"])}</figure></div></section>')
    if kind == "form": return form_html(b[1])
    if kind == "faq": return f'<section class="sec"><div class="wrap narrow"><h2>{e(b[1])}</h2>{faq_list(b[2])}</div></section>'
    if kind == "faqgroups":
        return "".join(f'<section class="sec"><div class="wrap narrow"><h2>{e(g)}</h2>{faq_list(qs)}</div></section>' for g, qs in b[1])
    raise ValueError(kind)

def cta_band(p):
    return f'''<section class="band"><div class="wrap"><h2>{e(p.get("cta", "Gather around the flame"))}</h2>
<p>{e(BIZ["street"])}, {e(BIZ["city"])} · Open daily from noon</p>
<div class="cta-row center"><a class="btn btn-p" data-track="reserve" data-place="band" href="{e(BIZ["reserve"])}">Reserve a table</a>
<a class="btn btn-s" href="tel:{BIZ["tel_href"]}">Call {e(BIZ["tel_display"])}</a></div></div></section>'''

def related(p):
    if not p.get("related"): return ""
    return '<section class="sec"><div class="wrap"><div class="related">' + "".join(
        f'<a href="{h}">{e(t)}<span>{e(s)}</span></a>' for h, t, s in p["related"]) + "</div></div></section>"

def footer():
    hrs = "<br>".join(f"{e(l)}: {e(d)}" for l, _, _, _, d in HOURS)
    soc = "".join(f'<a href="{e(u)}" rel="noopener">{n}</a>' for n, u in
                  [("Instagram", BIZ["instagram"]), ("TikTok", BIZ["tiktok"]), ("Yelp", BIZ["yelp"]), ("Facebook", BIZ["facebook"])] if u)
    links = "".join(f'<a href="{h}">{e(t)}</a>' for h, t in NAV)
    return f'''<footer><div class="wrap fgrid">
<div><img src="/assets/img/logo-white.png" width="160" height="83" alt="Hono Japanese BBQ" loading="lazy">
<p>{e(BIZ["street"])}<br>{e(BIZ["city"])}, {e(BIZ["region"])} {e(BIZ["zip"])}<br>
<a href="tel:{BIZ["tel_href"]}">{e(BIZ["tel_display"])}</a></p></div>
<div><h3>Hours</h3><p>{hrs}</p></div>
<div><h3>Explore</h3><p class="flinks">{links}</p></div>
<div><h3>Follow</h3><p class="flinks">{soc}</p></div></div>
<div class="wrap legal">© 2026 {e(BIZ["name"])} · {e(BIZ["legal_name"])}</div></footer>
<nav class="mbar" aria-label="Quick actions">
<div class="mtxt"><b>Reserve a Table</b><span>North Dallas, Texas</span></div>
<a class="mcall" href="tel:{BIZ["tel_href"]}">Call</a>
<a class="mgo" data-track="reserve" data-place="mbar" href="{e(BIZ["reserve"])}">Book Now</a></nav>'''

SCRIPT = r"""<script>
(function(){window.dataLayer=window.dataLayer||[];
// Ad-source attribution: ads land with ?gclid=… but guests browse before acting, so
// keep the last ad click for 90 days and attach it to form submissions.
var AD=['gclid','wbraid','gbraid','fbclid','msclkid','ttclid'],UTM=['utm_source','utm_medium','utm_campaign','utm_term','utm_content'];
var KEY='hono_attr',DAYS=90;
function load(){try{var o=JSON.parse(localStorage.getItem(KEY)||'null');if(!o||!o.ts||(Date.now()-o.ts)/864e5>DAYS)return null;return o;}catch(x){return null;}}
function capture(){var q=new URLSearchParams(location.search),h={},f=false;AD.concat(UTM).forEach(function(k){var v=q.get(k);if(v){h[k]=v;f=true;}});
 if(f){h.ts=Date.now();h.landing=location.pathname;try{localStorage.setItem(KEY,JSON.stringify(h));}catch(x){}return h;}return load();}
function summary(a){if(!a)return 'Organic or direct';var s=a.utm_source||((a.gclid||a.wbraid||a.gbraid)?'Google Ads':(a.fbclid?'Meta Ads':(a.msclkid?'Microsoft Ads':(a.ttclid?'TikTok Ads':'Unknown'))));
 return [s,a.utm_campaign,a.utm_content,a.utm_term].filter(Boolean).join(' | ');}
function clickId(a){if(!a)return '';for(var i=0;i<AD.length;i++){if(a[AD[i]])return AD[i]+'='+a[AD[i]];}return '';}
var ATTR=capture();
// Outbound Toast links carry UTM so Toast's own reports show the website as the source.
document.querySelectorAll('a[data-track]').forEach(function(a){
 var t=a.getAttribute('data-track'),p=a.getAttribute('data-place')||'';
 if(t==='reserve'||t==='order'){try{var u=new URL(a.href);u.searchParams.set('utm_source','honobbq.com');u.searchParams.set('utm_medium','website');u.searchParams.set('utm_content',p);a.href=u.toString();}catch(x){}}
 a.addEventListener('click',function(){window.dataLayer.push({event:t+'_click',placement:p,page_path:location.pathname});});});
document.querySelectorAll('a[href^="tel:"]').forEach(function(a){a.addEventListener('click',function(){
 window.dataLayer.push({event:'call_click',page_path:location.pathname});});});
// Group inquiry form
var f=document.getElementById('groupForm');
if(f){var st=document.getElementById('formStatus'),b=f.querySelector('button[type=submit]'),HAS=__HAS_KEY__;
 function say(m,k){st.hidden=false;st.textContent=m;st.className='formstatus full '+(k||'');}
 f.addEventListener('submit',function(ev){ev.preventDefault();if(!f.reportValidity())return;
  if(!HAS){say('Preview only: this form is not connected yet. Please call (214) 484-7707.','warn');return;}
  f.querySelector('[name=ad_source]').value=summary(ATTR);f.querySelector('[name=click_id]').value=clickId(ATTR);
  f.querySelector('[name=landing_page]').value=(ATTR&&ATTR.landing)||location.pathname;
  b.disabled=true;var o=b.textContent;b.textContent='Sending…';
  fetch(f.action,{method:'POST',headers:{'Content-Type':'application/json','Accept':'application/json'},body:JSON.stringify(Object.fromEntries(new FormData(f).entries()))})
  .then(function(r){return r.json().catch(function(){return {success:r.ok};});})
  .then(function(j){if(j&&j.success){f.reset();say('Thank you! We received your inquiry and will be in touch to confirm.','ok');
     window.dataLayer.push({event:'group_inquiry',page_path:location.pathname});}
   else{say('Something went wrong. Please call (214) 484-7707.','err');}})
  .catch(function(){say('Something went wrong. Please call (214) 484-7707.','err');})
  .finally(function(){b.disabled=false;b.textContent=o;});});}
// The mobile action bar is position:fixed; pad the page by its measured height so it never covers the footer.
var mb=document.querySelector('.mbar');function fit(){document.body.style.paddingBottom=(mb&&getComputedStyle(mb).display!=='none')?mb.offsetHeight+'px':'';}
fit();addEventListener('resize',fit);addEventListener('orientationchange',fit);
})();
</script>"""

def head(title, desc, url, noindex=False, og_img="/assets/img/dining-room-1600.jpg"):
    gsc = f'<meta name="google-site-verification" content="{e(GSC_VERIFY)}">' if GSC_VERIFY else ""
    robots = '<meta name="robots" content="noindex">' if noindex else ""
    return f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{e(title)}</title>
<meta name="description" content="{e(desc)}">{robots}
<link rel="canonical" href="{absu(url)}">
<meta property="og:type" content="restaurant"><meta property="og:site_name" content="{e(BIZ["name"])}">
<meta property="og:title" content="{e(title)}"><meta property="og:description" content="{e(desc)}">
<meta property="og:url" content="{absu(url)}"><meta property="og:image" content="{absu(og_img)}">
<meta name="twitter:card" content="summary_large_image">
<meta name="theme-color" content="#111111">{gsc}
<link rel="icon" href="/assets/favicon-32.png" sizes="32x32"><link rel="apple-touch-icon" href="/assets/favicon-180.png">
<link rel="stylesheet" href="/assets/site.css?v={CSSV}">
{gtm_head()}</head>'''

def render(p):
    url = "/" + (p["slug"] + "/" if p["slug"] else "")
    og = f'/assets/img/{p["hero"]["img"]}-1600.jpg' if p.get("hero") and f'{p["hero"]["img"]}-1600.jpg' in IMG else "/assets/img/dining-room-1600.jpg"
    body = "".join(block(b) for b in p["blocks"])
    return (head(p["title"], p["desc"], url, og_img=og) + f'''
<body>{gtm_body()}
<a class="skip" href="#main">Skip to content</a>
{header(url)}
<main id="main">{hero(p)}{reserve_box() if p["slug"] == "" else ""}{intro(p)}
{body}{related(p)}{cta_band(p)}</main>
{footer()}
<script type="application/ld+json">
{build_schema(p)}
</script>
{SCRIPT.replace("__HAS_KEY__", "true" if FORM_KEY else "false")}
</body></html>''')

def apply_base(t):
    """Prefix root-relative href/src/srcset with BASE in exactly one place."""
    if BASE:
        t = re.sub(r'(href|src)="/(?!/)', r'\1="' + BASE + "/", t)
        def _ss(m):
            return 'srcset="' + ", ".join((BASE + c.strip()) if c.strip().startswith("/") and not c.strip().startswith("//")
                                          else c.strip() for c in m.group(1).split(",")) + '"'
        t = re.sub(r'srcset="([^"]+)"', _ss, t)
    if NOINDEX:
        t = t.replace("<head>", '<head>\n<meta name="robots" content="noindex,nofollow">', 1)
    return t

def write(rel, text):
    path = os.path.join(OUT, rel)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f: f.write(apply_base(text))

def legacy_page(target):
    # Ads may land on old Wix URLs with ?gclid=…; a bare meta refresh would drop it, so JS carries the query over.
    return f'''<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="robots" content="noindex"><meta name="x-legacy-redirect" content="{target}">
<link rel="canonical" href="{absu(target)}"><title>Moved — Hono Japanese BBQ</title>
<meta http-equiv="refresh" content="0; url={BASE}{target}">
<script>location.replace("{BASE}{target}"+location.search+location.hash);</script></head>
<body><p>This page moved to <a href="{target}">{target}</a>.</p></body></html>'''

def pending_page():
    rows = "".join(
        f'<tr><td><code>{k}</code></td><td>{"✅ " + e(CONFIRMED[k]) if k in CONFIRMED else "⏳ 待確認"}</td>'
        f'<td>{e(v["q"])}</td><td>{e(v["text"]) or "—"}</td></tr>' for k, v in PENDING.items())
    return f'''<!doctype html><html lang="zh-Hant"><head><meta charset="utf-8"><meta name="robots" content="noindex">
<meta name="viewport" content="width=device-width,initial-scale=1"><title>待確認清單 — 內部審稿</title>
<link rel="stylesheet" href="/assets/site.css?v={CSSV}"></head><body><main class="wrap" style="padding:40px 16px">
<h1 style="font-size:28px">待確認清單（內部，不會被收錄）</h1>
<p>以下說法目前<b>沒有查證來源</b>，所以不會出現在網站上。客人確認後，在 <code>content/facts.py</code> 的 CONFIRMED 加一行
「誰、哪天確認」，重新建置即可上線。</p>
<div class="tablewrap"><table class="kv"><tr><th>代號</th><th>狀態</th><th>要問客人</th><th>確認後會出現的文字</th></tr>{rows}</table></div>
</main></body></html>'''

def main():
    if os.path.isdir(OUT): shutil.rmtree(OUT)
    shutil.copytree("assets", os.path.join(OUT, "assets"))
    for p in PAGES:
        write(os.path.join(p["slug"], "index.html") if p["slug"] else "index.html", render(p))
    for old, new in LEGACY.items():
        write(os.path.join(old, "index.html"), legacy_page(new))
    write("_pending/index.html", pending_page())
    nf = PAGES[0] | {"slug": "", "title": "Page not found | Hono Japanese BBQ", "desc": "This page could not be found."}
    write("404.html", head(nf["title"], nf["desc"], "/404.html", noindex=True) + f'''
<body>{gtm_body()}{header("")}<main id="main"><section class="pagehead"><div class="wrap"><h1>Page not found</h1></div></section>
<section class="sec"><div class="wrap narrow"><p>The page you were looking for has moved. Here's where to go next:</p>
<div class="related"><a href="/menu/">Menu &amp; prices<span>AYCE tiers from $49</span></a><a href="/visit/">Visit<span>Hours and directions</span></a>
<a href="/groups/">Group dining<span>Parties of 6+</span></a></div></div></section></main>{footer()}
{SCRIPT.replace("__HAS_KEY__", "false")}</body></html>''')
    open(os.path.join(OUT, ".nojekyll"), "w").close()
    cname = os.environ.get("CNAME_DOMAIN", "").strip().removeprefix("https://").removeprefix("http://").strip("/")
    if cname:
        open(os.path.join(OUT, "CNAME"), "w").write(cname + "\n")
    with open(os.path.join(OUT, "robots.txt"), "w") as f:
        f.write("User-agent: *\nDisallow: /\n" if NOINDEX else f"User-agent: *\nAllow: /\nDisallow: /_pending/\n\nSitemap: {absu('/sitemap.xml')}\n")
    prio = {"": "1.0", "menu": "0.9", "groups": "0.8", "visit": "0.8"}
    urls = "".join(f'  <url><loc>{absu("/" + (p["slug"] + "/" if p["slug"] else ""))}</loc><lastmod>{TODAY}</lastmod>'
                   f'<priority>{prio.get(p["slug"], "0.6")}</priority></url>\n' for p in PAGES)
    with open(os.path.join(OUT, "sitemap.xml"), "w", encoding="utf-8") as f:
        f.write('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + urls + "</urlset>\n")
    pend = [k for k in PENDING if k not in CONFIRMED]
    print(f"✓ built {len(PAGES)} pages + 404 + {len(LEGACY)} legacy redirect(s) → {OUT}/  "
          f"[{'NOINDEX preview' if NOINDEX else 'INDEXABLE'} · site={SITE}{BASE or ''} · GTM={'on' if GTM_ID else 'off'} · "
          f"form={'connected' if FORM_KEY else 'not connected'} · pending={len(pend)}]")

if __name__ == "__main__":
    main()
