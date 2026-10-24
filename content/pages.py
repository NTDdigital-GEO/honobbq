# -*- coding: utf-8 -*-
"""Page content. Facts come from facts.py; this file holds structure and voice.

Structure follows Fogo de Chão's location site (location page, menus, group
dining page, FAQ), price cards follow Texas de Brazil, pricing rules and the
group page follow Chama Gaúcha, and the voice follows Uchi Dallas.
"""
from html import escape as e
from .facts import (BIZ, HOURS, LAST_SEATING, LAST_CALL, TIERS, ALL_TIERS_INCLUDE, LUNCH, LUNCH_DISCOUNT,
                    POLICIES, SAFETY, ALACARTE, A5_ALACARTE, HAPPY_HOUR, COCKTAILS, MOCKTAILS, WHISKY, SAKE,
                    BEER, WINE, PROOF, PENDING, REELS, ok)

JMGA = "https://www.jmga.or.jp/standard/beef/"
AWA = "https://wagyu.org/"

# ── small builders ───────────────────────────────────────────────
def ext(url, label):
    return f'<a class="ext" href="{e(url)}" rel="noopener" target="_blank">{e(label)}</a>'

def pend(key):
    """Text of an unverified claim, or '' until the client confirms it."""
    return PENDING[key]["text"] if ok(key) else ""

def btn(kind, label, cls="btn", place="body"):
    if kind == "reserve": return f'<a class="{cls} btn-p" data-track="reserve" data-place="{place}" href="{e(BIZ["reserve"])}">{e(label)}</a>'
    if kind == "order":   return f'<a class="{cls} btn-s" data-track="order" data-place="{place}" href="{e(BIZ["order"])}">{e(label)}</a>'
    if kind == "call":    return f'<a class="{cls} btn-s" href="tel:{BIZ["tel_href"]}">{e(label)}</a>'
    if kind == "map":     return f'<a class="{cls} btn-s" data-track="directions" data-place="{place}" href="{e(BIZ["maps"])}">{e(label)}</a>'
    raise ValueError(kind)

def ul(items, cls="list"):
    return f'<ul class="{cls}">' + "".join(f"<li>{e(i)}</li>" for i in items) + "</ul>"

def hours_table():
    rows = "".join(f"<tr><th>{e(lbl)}</th><td>{e(disp)}</td></tr>" for lbl, _, _, _, disp in HOURS)
    rows += f'<tr><th>AYCE lunch</th><td>{e(LUNCH["days"])}, {e(LUNCH["time"])}</td></tr>'
    rows += f'<tr><th>Happy hour</th><td>{" · ".join(e(w) for w in HAPPY_HOUR["when"])}</td></tr>'
    rows += f"<tr><th>Last seating · last call</th><td>{e(LAST_SEATING)} · {e(LAST_CALL)}</td></tr>"
    return f'<table class="kv">{rows}</table>'

def tier_cards(full=False):
    out = []
    for t in TIERS:
        body = ul(t["cuts"], "cuts") + (f'<p class="fine">{e(t["note"])}</p>' if t.get("note") else "") if full \
            else f'<p>{e(t["adds"])}</p>'
        out.append(f'''<article class="tier tier-{t["name"].lower()}">
<p class="tier-name">{e(t["name"])}</p>
<h3 class="tier-price">${t["price"]}<span> per person</span></h3>
<p class="tier-tag">{e(t["tagline"])}</p>{body}</article>''')
    return '<div class="tiers">' + "".join(out) + "</div>"

def hh_block():
    items = "".join(f"<li><span>{e(n)}</span><b>${p}</b></li>" for n, p in HAPPY_HOUR["items"])
    return f'<p class="when">{" · ".join(e(w) for w in HAPPY_HOUR["when"])}</p><ul class="pricelist">{items}</ul>'

def pricelist(rows):
    return '<ul class="pricelist">' + "".join(
        f'<li><span>{e(n)}{f"<small>{e(d)}</small>" if d else ""}</span><b>{e(str(p))}</b></li>' for n, p, d in rows) + "</ul>"

def policies_table():
    return '<table class="kv">' + "".join(f"<tr><th>{e(k)}</th><td>{e(v)}</td></tr>" for k, v in POLICIES) + "</table>"

def trust_strip():
    return (f'<div class="trust"><span>★ {PROOF["google_rating"]} on Google · {PROOF["google_reviews_floor"]} reviews</span>'
            f'<span>As featured in {ext(BIZ["dmag"], "D Magazine")}</span>'
            f'<span>Japanese A5 wagyu in our Ruby tier</span></div>')

def figure(slug, alt, caption=None, eager=False, mobile=None, lift=False):
    """mobile: a portrait image used below 760px (art direction). lift: brighten a dark interior photo."""
    return {"img": slug, "alt": alt, "caption": caption, "eager": eager, "mobile": mobile, "lift": lift}

def reels(tag=None):
    return [r for r in REELS if tag is None or r["tag"] == tag]

# ── FAQ (visible text and FAQPage schema are generated from the same tuples) ──
def faq_general():
    tiers = ", ".join(f'${t["price"]} ({t["name"]})' for t in TIERS)
    qs = [
        ("Pricing & tiers", [
            ("How much is all-you-can-eat at Hono Japanese BBQ?",
             f"Dinner AYCE is {tiers} per person. Each tier includes everything in the tiers below it. AYCE lunch is ${LUNCH['price']} per person, {LUNCH['days']}, {LUNCH['time']}."),
            ("What's the difference between Gold, Platinum and Ruby?",
             "Gold covers the wagyu essentials: wagyu beef belly, brisket, chuck roll and top blade, plus skirt steak and rib meat. Platinum adds steakhouse cuts such as filet mignon, ribeye, New York strip and picanha, plus lobster tail. Ruby adds Japanese A5 wagyu and a premium nigiri."),
            ("What does A5 mean?",
             "A5 is the top grade under the Japan Meat Grading Association's beef standard: A is the highest yield grade and 5 is the highest quality grade, which scores marbling, meat color, firmness and fat quality."),
            ("Is lunch cheaper than dinner?",
             f"Yes. AYCE lunch is ${LUNCH['price']} per person, {LUNCH['days']}, {LUNCH['time']}, with wagyu beef belly and brisket, sushi and ramen. {LUNCH_DISCOUNT}"),
        ]),
        ("Kids & groups", [
            ("Do kids pay full price?", 'Kids under 39 inches tall dine free. Kids from 39 to 51 inches pay 50% of the tier price.'),
            ("Does everyone at the table have to order the same tier?", "Yes. All guests at the table dine on the same AYCE tier."),
            ("Is gratuity included?", "Gratuity is added automatically for parties of five or more."),
            ("Do large groups get more time?", "Yes. Parties of six or more get 110 minutes of AYCE dining instead of 90."),
        ]),
        ("Dining rules", [
            ("Is there a time limit?", "AYCE dining is 90 minutes, or 110 minutes for parties of six or more. Final orders are taken 15 minutes before your dining time ends."),
            ("Is there a charge for leftovers?", "Uneaten AYCE items are charged at the à la carte price, and AYCE items can't be taken to go. Order a few plates at a time — you can always order more."),
            ("Can I order à la carte instead?", "Yes. Ramen, yakisoba, fried rice, hibachi, donburi, sushi and izakaya plates are available à la carte, and they're 20% off Monday to Thursday from 12 to 3 PM."),
            ("Can I bring outside food or drinks?", "Outside food and beverages are not permitted."),
        ]),
        ("Reservations, takeout & visiting", [
            ("Do you take reservations?", f"Yes. Reserve online through Toast or call {BIZ['tel_display']}. If your plans change, please cancel as soon as you know."),
            ("Do you offer takeout?", "Yes. Order online through Toast for pickup. All-you-can-eat is dine-in only."),
            ("What are your hours?", "Sunday to Thursday 12 PM to 11 PM, and Friday and Saturday 12 PM to 12 AM. Last seating is 60 minutes before close."),
            ("Where are you located?", f"{BIZ['street']}, {BIZ['city']}, {BIZ['region']} {BIZ['zip']}, near {BIZ['cross']} in {BIZ['area']}."),
            ("Is the restaurant wheelchair accessible?", "Yes. The entrance, parking, restroom and seating are wheelchair accessible."),
        ]),
        ("Drinks & dietary", [
            ("When is happy hour?", "Monday to Friday from 3 to 6 PM, and every day from 9 PM to close. Draft beer, frozen margaritas and well drinks are $5."),
            ("Do you have Japanese whisky and sake?", "Yes. The bar pours Japanese whisky from Suntory Toki to Yamazaki 18 and sake from nigori to Dassai 45 junmai daiginjo, plus signature cocktails like the Matcha-Tini."),
            ("Can you accommodate allergies or dietary restrictions?", "Please tell your server about any allergies or dietary restrictions before ordering. Our kitchen handles common allergens and cross-contact may occur. AYCE pricing applies regardless of dietary limitations."),
        ]),
    ]
    extra = []
    if ok("parking"):  extra.append(("Is there parking?", PENDING["parking"]["text"]))
    if ok("walkins"):  extra.append(("Do you take walk-ins?", PENDING["walkins"]["text"]))
    if ok("salad_bar"): extra.append(("Is the salad bar included?", PENDING["salad_bar"]["text"]))
    if extra: qs[3][1].extend(extra)
    return qs

FAQ_GROUPS = [
    ("How much time do large groups get?", "Parties of six or more get 110 minutes of AYCE dining, compared with 90 minutes for smaller parties."),
    ("Does the whole group have to choose the same tier?", "Yes. Everyone at the table dines on the same tier — Gold ($49), Platinum ($65) or Ruby ($79) per person."),
    ("Is gratuity added for groups?", "Yes. Gratuity is added automatically for parties of five or more."),
    ("How do kids in our group pay?", "Kids under 39 inches tall dine free, and kids from 39 to 51 inches pay half of the tier price."),
]

# ── pages ────────────────────────────────────────────────────────
inc = ALL_TIERS_INCLUDE

HOME = dict(
    slug="", nav="Home",
    title="Hono Japanese BBQ | AYCE Wagyu Yakiniku in North Dallas",
    desc="All-you-can-eat Japanese BBQ at Preston & Frankford. Dinner from $49, $29 weekday lunch, A5 wagyu, sushi and a full bar. Reserve on Toast.",
    h1="All-You-Can-Eat Japanese BBQ in North Dallas",
    # hero line breaks: each inner phrase never splits; each outer item starts a new line
    h1_lines=[["All-You-Can-Eat", "Japanese BBQ"], ["in North Dallas"]],
    hero=figure("fire-wide", "Wagyu flaring over the tabletop grill at Hono Japanese BBQ", eager=True, mobile="fire-tall"),
    kicker="Gather around the flame",
    proof=f'★ {PROOF["google_rating"]} on Google · {PROOF["google_reviews_floor"]} reviews · Featured in D Magazine',
    offer=[f'Wagyu AYCE from ${TIERS[0]["price"]}', f'${LUNCH["price"]} weekday lunch', "Happy hour daily 9 PM – close"],
    answer=(f"Hono Japanese BBQ is an all-you-can-eat yakiniku restaurant in North Dallas at {BIZ['street']}, near "
            f"Preston &amp; Frankford. Grill wagyu at your table with dinner tiers at $49, $65 and $79 per person — Ruby "
            f"adds Japanese A5 wagyu — plus sushi and izakaya plates. AYCE lunch is ${LUNCH['price']}, Monday–Thursday, "
            f"12–3 PM. Open daily from noon."),
    blocks=[
        ("raw", trust_strip()),
        ("section", "Choose Your Experience",
         tier_cards() + f'<p class="after">Every tier includes the full grill selection, kitchen specials and sushi. Kids under 39" dine free; 39–51" pay half. '
                        f'<a href="/menu/">See the full menu and what each tier includes →</a></p>'),
        ("split", f"Weekday AYCE Lunch — ${LUNCH['price']}",
         f"<p><b>{e(LUNCH['days'])}, {e(LUNCH['time'])}.</b> Wagyu beef belly, wagyu brisket, skirt steak, Duroc pork, chicken and seafood "
         f"for the grill, with sushi, ramen and kitchen favorites — ${LUNCH['price']} per person.</p><p>{e(LUNCH_DISCOUNT)}</p>"
         + btn("reserve", "Reserve lunch", place="home_lunch"),
         figure("table", "A full table of wagyu, pork belly, shrimp, ramen and sides around the grill at Hono Japanese BBQ")),
        ("split alt", "Happy Hour",
         hh_block() + '<p>Ask for the Matcha-Tini ($14) — vodka, matcha, Frangelico, Licor 43 and cream. '
                      '<a href="/drinks/">See the full bar menu →</a></p>',
         figure("cocktails", "A Matcha-Tini, a champagne-flute cocktail and an old fashioned on the bar at Hono Japanese BBQ")),
        ("section", "Guest Favorites",
         '<div class="cards3">'
         f'<article class="dish"><h3>Wagyu Beef Belly</h3><p>Thin, tender and quick on the grill. {e(pend("top_order"))}</p></article>'
         '<article class="dish"><h3>Wagyu Tartare</h3><p>Furikake-seasoned wagyu with crisp chips, one per guest on every dinner tier.</p></article>'
         '<article class="dish"><h3>Matcha-Tini</h3><p>The cocktail our Google reviewers keep mentioning: vodka, matcha, Frangelico, Licor 43 and cream.</p></article>'
         "</div>"),
        ("reels", "Follow the Flame @hono.bbq", reels()),
        ("split", "Groups & Celebrations",
         "<p>Birthdays, team dinners and family nights are better around a grill. Parties of six or more get 110 minutes "
         "of AYCE dining, and every table has its own grill.</p>"
         '<p><a class="btn btn-p" href="/groups/">Plan a group dinner</a></p>',
         figure("dining-room-tall", "Rows of booths with tabletop grills, ready for a group dinner", lift=True)),
        ("section", "Takeout",
         "<p>Ramen, donburi, sushi and izakaya favorites are ready for pickup. All-you-can-eat is dine-in only.</p>"
         + btn("order", "Order online", place="home_takeout")),
        ("section", "Hours & Location",
         f'<div class="two"><div>{hours_table()}</div><div><p class="addr">{e(BIZ["street"])}<br>{e(BIZ["city"])}, {e(BIZ["region"])} {e(BIZ["zip"])}<br>'
         f'Near {e(BIZ["cross"])}</p><p><a href="tel:{BIZ["tel_href"]}">{e(BIZ["tel_display"])}</a></p>'
         f'<div class="cta-row">{btn("map", "Get directions", place="home_location")}<a class="btn btn-s" href="/visit/">Visit info</a></div></div></div>'),
    ],
    related=[("/menu/", "Menu & prices", "Three AYCE tiers and lunch"), ("/faq/", "AYCE FAQ", "Kids, time limits, tiers"),
             ("/groups/", "Group dining", "Birthdays and team dinners")],
)

MENU = dict(
    slug="menu", nav="Menu",
    title="AYCE Yakiniku Menu & Prices | Hono Japanese BBQ Dallas",
    desc='Gold $49, Platinum $65, Ruby $79 with Japanese A5 wagyu. $29 AYCE lunch Mon–Thu. Kids under 39" eat free. Full menu and dining rules.',
    h1="Yakiniku Menu & All-You-Can-Eat Prices",
    # "All-You-Can-Eat Prices" is wider than a 320–375px screen, so it may split there (never overflow)
    h1_lines=[["Yakiniku Menu &"], ["All-You-Can-Eat", "Prices"]],
    crumbs=[("Menu", "/menu/")],
    answer=("All-you-can-eat dinner at Hono Japanese BBQ is $49 (Gold), $65 (Platinum) or $79 (Ruby) per person, and each tier "
            "includes the tiers below it. Every tier comes with the full grill selection, kitchen specials and sushi. AYCE lunch is "
            f"${LUNCH['price']}, Monday–Thursday 12–3 PM. Kids under 39 inches dine free; dining time is 90 minutes."),
    blocks=[
        ("section", "AYCE Dinner — from $49 per person", tier_cards(full=True)),
        ("section", "Included With Every Tier",
         '<div class="cols4">'
         f'<div><h3>For the grill</h3>{ul(inc["grill"])}</div>'
         f'<div><h3>From the kitchen</h3>{ul(inc["kitchen"])}</div>'
         f'<div><h3>Sushi</h3>{ul(inc["sushi"])}</div>'
         f'<div><h3>Sauces &amp; seasonings</h3>{ul(inc["sauces"])}</div></div>'
         + (f'<p class="after">{e(pend("salad_bar"))}</p>' if pend("salad_bar") else "")),
        ("section", f"AYCE Lunch — ${LUNCH['price']} per person",
         f'<p><b>{e(LUNCH["days"])}, {e(LUNCH["time"])}.</b></p><div class="cols3">'
         f'<div><h3>For the grill</h3>{ul(LUNCH["grill"])}</div><div><h3>Sushi</h3>{ul(LUNCH["sushi"])}</div>'
         f'<div><h3>From the kitchen</h3>{ul(LUNCH["kitchen"])}</div></div><p class="after">{e(LUNCH_DISCOUNT)}</p>'),
        ("section", "Pricing & Policies", policies_table() + '<p class="after"><a href="/faq/">More answers in the AYCE FAQ →</a></p>'),
        ("section", "What A5 Means",
         "<p>A5 is the top grade under the Japan Meat Grading Association's beef carcass standard: <b>A</b> is the highest yield grade "
         "and <b>5</b> is the highest quality grade, judged on marbling, meat color, firmness and texture, and fat quality "
         f"({ext(JMGA, 'JMGA grading standard, in Japanese')}). Our Gold and Platinum tiers feature wagyu cuts as well; "
         f"learn more about wagyu raised in the U.S. from the {ext(AWA, 'American Wagyu Association')}.</p>"),
        ("section", "Not Feeling Yakiniku? À La Carte",
         pricelist([(n, p, d) for n, d, p in ALACARTE])
         + "<h3>A5 Japanese wagyu à la carte</h3>" + pricelist([(n, f"${p}", "") for n, p in A5_ALACARTE])
         + f'<p class="after">{e(LUNCH_DISCOUNT)}</p>'),
        ("raw", f'<p class="fine center">{e(SAFETY)}</p>'),
    ],
    cta="Ready to grill?",
    related=[("/drinks/", "Drinks & happy hour", "$5 drafts and margaritas"), ("/faq/", "AYCE FAQ", "Everything about tiers and rules"),
             ("/groups/", "Group dining", "Parties of 6+ get 110 minutes")],
)

DRINKS = dict(
    slug="drinks", nav="Drinks",
    title="Drinks & Happy Hour | Hono Japanese BBQ Dallas",
    desc="Japanese whisky, sake, signature cocktails and the Matcha-Tini. Happy hour Mon–Fri 3–6 PM and daily 9 PM–close with $5 drafts and margaritas.",
    h1="Japanese Whisky, Sake, Cocktails & Happy Hour",
    h1_lines=[["Japanese Whisky,", "Sake, Cocktails"], ["& Happy Hour"]],
    crumbs=[("Drinks", "/drinks/")],
    answer=("The bar at Hono Japanese BBQ pours Japanese whisky from Suntory Toki to Yamazaki 18, sake from nigori to Dassai 45, "
            "and signature cocktails like the $14 Matcha-Tini. Happy hour runs Monday–Friday 3–6 PM and every day from 9 PM to "
            "close, with $5 draft beer, frozen margaritas and well drinks."),
    blocks=[
        ("split alt", "Happy Hour", hh_block(),
         figure("cocktails", "A Matcha-Tini, a champagne-flute cocktail and an old fashioned on the bar at Hono Japanese BBQ")),
        ("section", "Signature Cocktails", pricelist([(n, f"${p}", d) for n, p, d in COCKTAILS])),
        ("reels", "From the Bar on Instagram", reels("drinks")),
        ("section", "Mocktails", pricelist([(n, f"${p}", d) for n, p, d in MOCKTAILS])),
        ("section", "Japanese Whisky", pricelist([(n, f"${p}", "") for n, p in WHISKY])),
        ("section", "Sake", '<p class="fine">Glass / bottle</p>' + pricelist([(n, f"${p}", s) for n, s, p in SAKE])),
        ("section", "Beer", '<p class="fine">12 oz / 16 oz</p>' + pricelist([(n, f"${p}", "") for n, p in BEER])),
        ("section", "Wine", '<p class="fine">6 oz / bottle</p>' + pricelist([(n, f"${p}", "") for n, p in WINE])),
        ("raw", '<p class="fine center">Please drink responsibly. Guests must be 21 or older to order alcohol.</p>'),
    ],
    cta="Save a seat at the bar",
    related=[("/menu/", "Menu & prices", "AYCE tiers and lunch"), ("/visit/", "Hours & location", "Happy hour times"),
             ("/groups/", "Group dining", "Celebrate with a round")],
)

def groups_stats():
    third = pend("group_max").replace("up to ", "").replace("We can seat groups of ", "")
    s3 = (f'<div><b>{e(third)}</b><span>guests per reservation</span></div>' if third
          else '<div><b>Free</b><span>kids under 39" dine</span></div>')
    return ('<div class="stats"><div><b>6+</b><span>guests get 110 minutes</span></div>'
            '<div><b>$49</b><span>per person to start</span></div>' + s3 + "</div>")

GROUPS = dict(
    slug="groups", nav="Groups",
    title="Group Dining & Birthday Dinners | Hono Japanese BBQ Dallas",
    desc="All-you-can-eat Japanese BBQ for groups in North Dallas. Parties of 6+ get 110 minutes, tiers from $49 per person. Birthdays and team dinners.",
    h1="Group Dining & Celebrations in North Dallas",
    h1_lines=[["Group Dining", "& Celebrations"], ["in North Dallas"]],
    crumbs=[("Groups", "/groups/")],
    hero=figure("dining-room", "Dining room of booths with tabletop grills at Hono Japanese BBQ", eager=True, lift=True),
    kicker="Birthdays, team dinners, family nights", cta="plan",
    proof="Parties of 6+ get 110 minutes",
    offer=[f'Tiers from ${TIERS[0]["price"]} per person', 'Kids under 39" dine free', "Full bar · open until midnight Fri & Sat"],
    answer=("Hono Japanese BBQ hosts birthdays, team dinners and family celebrations in North Dallas. Parties of six or more get "
            "110 minutes of all-you-can-eat Japanese BBQ, everyone at the table dines on one tier — $49, $65 or $79 per person — "
            "and gratuity is added for parties of five or more. Kids under 39 inches dine free."),
    blocks=[
        ("raw", groups_stats()),
        ("section", "Gather Around the Flame",
         "<p>Some dinners are meant to be shared. Every table at Hono has its own grill, so the whole group cooks, passes plates "
         "and celebrates together — wagyu, sushi and a full bar included. Bring the birthday, the team, the graduation or the "
         f"family reunion. We'll keep the plates coming. {e(pend('group_contact'))}</p>"),
        ("section", "How Group Dining Works",
         '<div class="cards3">'
         '<article class="dish"><h3>One tier for the table</h3><p>Gold $49 · Platinum $65 · Ruby $79 per person. Everyone at the table dines on the same tier.</p></article>'
         '<article class="dish"><h3>More time for bigger parties</h3><p>Parties of six or more get 110 minutes of AYCE dining instead of 90.</p></article>'
         '<article class="dish"><h3>Easy math for organizers</h3><p>A party of 10 on Platinum is $650 before tax and gratuity. Kids under 39" dine free; 39–51" pay half.</p></article>'
         "</div>"),
        ("section", "Perfect For", ul(["Birthdays", "Team dinners and client entertaining", "Graduations",
                                       "Family celebrations", "Game-night groups"], "chips")),
        ("form", "Plan Your Group Dinner"),
        ("faq", "Group Dining FAQ", FAQ_GROUPS),
    ],
    related=[("/menu/", "Menu & prices", "What each tier includes"), ("/drinks/", "Drinks", "Sake, whisky and cocktails"),
             ("/visit/", "Visit", "Hours and directions")],
)

VISIT = dict(
    slug="visit", nav="Visit",
    title="Location, Hours & Parking | Hono Japanese BBQ Dallas",
    desc="18101 Preston Rd, Unit 302, Dallas, TX 75252 near Preston & Frankford. Open daily at noon, until midnight Fri–Sat. Call (214) 484-7707.",
    h1="Visit Hono: Location, Hours & Parking",
    h1_lines=[["Visit Hono:"], ["Location,", "Hours & Parking"]],
    crumbs=[("Visit", "/visit/")],
    answer=(f"Hono Japanese BBQ is at {BIZ['street']}, {BIZ['city']}, {BIZ['region']} {BIZ['zip']}, near {BIZ['cross']} in "
            "North Dallas. It is open Sunday–Thursday 12 PM–11 PM and Friday–Saturday 12 PM–12 AM, with last seating 60 minutes "
            "before close. Reserve on Toast or call (214) 484-7707."),
    blocks=[
        ("split", "Find Us",
         f'<p class="addr">{e(BIZ["name"])}<br>{e(BIZ["street"])}<br>{e(BIZ["city"])}, {e(BIZ["region"])} {e(BIZ["zip"])}</p>'
         f'<p>Near the intersection of {e(BIZ["cross"])} in {e(BIZ["area"])}. Look for the red 炎 sign.</p>'
         f'<p><a href="tel:{BIZ["tel_href"]}">{e(BIZ["tel_display"])}</a></p><div class="cta-row">{btn("map", "Get directions", place="visit")}</div>',
         figure("storefront", "Storefront of Hono Japanese BBQ with the red 炎 sign above the door", lift=True)),
        ("section", "Hours", hours_table()),
        ("section", "Parking & Accessibility",
         (f"<p>{e(pend('parking'))}</p>" if pend("parking") else "")
         + "<p>The entrance, parking, restroom and seating are wheelchair accessible.</p>"),
        ("section", "Reservations & Walk-ins",
         f"<p>Reserve online through Toast or call <a href=\"tel:{BIZ['tel_href']}\">{e(BIZ['tel_display'])}</a>. "
         f"{e(pend('walkins'))} If your plans change, please cancel your reservation as soon as you know. "
         'Planning for six or more? See <a href="/groups/">group dining</a>.</p>' + btn("reserve", "Reserve a table", place="visit")),
        ("split", "Good to Know",
         ul([x for x in ["Full bar with Japanese whisky and sake",
                         "Takeout for à la carte dishes through Toast",
                         'Kids under 39" dine AYCE free',
                         pend("patio"), pend("wifi")] if x]),
         figure("flame-sign", "The illuminated red 炎 flame sign on the building at Hono Japanese BBQ", lift=True)),
    ],
    related=[("/menu/", "Menu & prices", "AYCE tiers and lunch"), ("/groups/", "Group dining", "Parties of 6+"),
             ("/faq/", "FAQ", "Time limits, kids, takeout")],
)

ABOUT = dict(
    slug="about", nav="About",
    title="About Hono | Japanese BBQ & Wagyu in North Dallas",
    desc="Hono (炎) means flame. A North Dallas yakiniku and izakaya house built around wagyu, warm hospitality and gathering at the grill.",
    h1="About Hono: Gathering Around the Flame",
    h1_lines=[["About Hono:"], ["Gathering Around", "the Flame"]],
    crumbs=[("About", "/about/")],
    hero=figure("lattice-window", "Lattice windows, bonsai and warm lighting inside Hono Japanese BBQ", eager=True, lift=True),
    kicker="炎 means flame",
    proof=f'★ {PROOF["google_rating"]} on Google · {PROOF["google_reviews_floor"]} reviews · Featured in D Magazine',
    offer=["Wagyu yakiniku at your table", "Sushi & izakaya plates", "Full bar & happy hour"],
    answer=("Hono Japanese BBQ is a yakiniku and izakaya restaurant in North Dallas. Its name comes from 炎, the Japanese "
            "character for flame, and the idea that people everywhere gather around fire to cook, share stories and connect. "
            "Guests grill wagyu at their own table, with sushi, small plates and a full bar."),
    blocks=[
        ("section", "炎 Means Flame",
         "<p>Across the world, family, friends and even strangers gather around fire to cook, share stories and connect through "
         "the simple act of a shared meal. That is the idea behind Hono.</p>"
         "<p>Our focus is uncompromising ingredient quality, genuine hospitality and a room where meaningful connections can "
         "ignite — wagyu on the grill, small plates inspired by the spirit of yakiniku and izakaya, and a bar made for lingering. "
         "Whether you join us for a casual night or a special occasion, we believe how you dine matters as much as what you dine on.</p>"),
        ("split", "What People Are Saying",
         f'<p>In September 2026, {ext(BIZ["dmag"], "D Magazine")} taste-tested every meat on the menu. On Google, guests rate us '
         f'{PROOF["google_rating"]} stars across {PROOF["google_reviews_floor"]} reviews, and the things they mention most are the '
         "all-you-can-eat, the sushi, the salad bar and the matcha martini.</p>"
         + btn("reserve", "Reserve a table", place="about"),
         figure("flame-sign", "The red 炎 flame sign on the Hono Japanese BBQ building", lift=True)),
    ],
    related=[("/menu/", "Menu & prices", "Three AYCE tiers"), ("/visit/", "Visit", "Find the red 炎 sign"),
             ("/groups/", "Group dining", "Celebrate with us")],
)

FAQ = dict(
    slug="faq", nav="FAQ",
    title="AYCE FAQ: Prices, Kids, Time Limits | Hono Japanese BBQ",
    desc="Answers about Hono Japanese BBQ: AYCE tiers and prices, kids pricing, 90-minute dining time, gratuity, reservations, takeout and happy hour.",
    h1="All-You-Can-Eat FAQ",
    h1_lines=[["All-You-Can-Eat", "FAQ"]],
    crumbs=[("FAQ", "/faq/")],
    answer=("Quick answers about Hono Japanese BBQ: dinner AYCE is $49, $65 or $79 per person and lunch is $29 Monday–Thursday. "
            "Kids under 39 inches dine free, dining time is 90 minutes (110 for parties of six or more), the whole table orders "
            "one tier, and gratuity is added for parties of five or more."),
    blocks=[("faqgroups", faq_general())],
    related=[("/menu/", "Menu & prices", "See every tier"), ("/groups/", "Group dining", "Plan for 6+"),
             ("/visit/", "Visit", "Hours and directions")],
)

PAGES = [HOME, MENU, DRINKS, GROUPS, VISIT, ABOUT, FAQ]
NAV = [("/menu/", "Menu"), ("/drinks/", "Drinks"), ("/groups/", "Groups"), ("/visit/", "Visit"), ("/about/", "About"), ("/faq/", "FAQ")]
# Old Wix URLs that must keep working (someone else may link to them — ads, QR codes).
LEGACY = {"blank-3": "/visit/"}
