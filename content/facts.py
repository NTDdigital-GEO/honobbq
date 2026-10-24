# -*- coding: utf-8 -*-
"""Hono Japanese BBQ — every business fact the site states, in one place.

Each fact carries its source and the date it was checked (2026-10-23 audit,
see ../01-site-audit.html). Pages, schema and FAQ all read from here, so a
price or hours change is made once and propagates everywhere.

Rule from the audit: a claim no source supports is NOT published. It goes in
PENDING with the question to ask the client, and only renders once its key is
added to CONFIRMED (with who confirmed it and when).
"""

BIZ = dict(
    name="Hono Japanese BBQ",
    legal_name="HONO PRESTON INC.",          # client record; never used as a display name
    street="18101 Preston Rd, Unit 302",
    city="Dallas", region="TX", zip="75252",   # GBP + Toast + in-store menu agree; footer's 75052 was wrong
    area="North Dallas",
    cross="Preston Rd & Frankford Rd",
    lat=32.9986658, lng=-96.7992805,           # Google Maps place pin
    tel_display="(214) 484-7707", tel_href="+12144847707", tel_schema="+1-214-484-7707",
    # Toast links. NOTE: the slug still says "new-em" (internal name). After the
    # client renames the venue in Toast, re-copy both URLs from the Toast admin.
    reserve="https://tables.toasttab.com/restaurants/d145621b-b642-478e-a471-3224b925d0ed/findTime",
    order="https://toast.app/r/hono-japanese-bbq-new-em-18101-preston-road-unit-302/order",
    # CID taken from the GBP place URL (0x9c677f981f3d3d67); opened and checked 2026-10-23.
    maps="https://www.google.com/maps?cid=11270116883853819239",
    instagram="https://www.instagram.com/hono.bbq/",
    tiktok="https://www.tiktok.com/@hono_bbq",
    yelp="https://www.yelp.com/biz/hon%C5%8D-japanese-bbq-dallas",
    facebook="",                                # only a mobile share link is known — ask client for the page URL
    dmag="https://www.dmagazine.com/food-drink/2026/09/taste-testing-every-meat-at-north-dallas-hono-japanese-bbq/",
)

# Google Business Profile, Yelp and the in-store menu all agree (2026-10-23).
HOURS = [  # (label, days for schema, opens, closes-for-schema, display)
    ("Sunday – Thursday", ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday"], "12:00", "23:00", "12 PM – 11 PM"),
    ("Friday – Saturday", ["Friday", "Saturday"], "12:00", "23:59", "12 PM – 12 AM"),
]
LAST_SEATING = "60 minutes before close"   # in-store menu, AYCE policy panel
LAST_CALL = "30 minutes before close"

# ── AYCE (in-store dinner menu image, /menu, 2026-10-23; D Magazine 2026-09-12 corroborates $49/$65) ──
TIERS = [
    dict(name="Gold", price=49, tagline="The wagyu essentials",
         adds="Wagyu beef belly, wagyu brisket, wagyu chuck roll, wagyu top blade, skirt steak and rib meat.",
         cuts=["Wagyu beef belly", "Wagyu brisket", "Wagyu chuck roll", "Wagyu top blade", "Skirt steak", "Rib meat"]),
    dict(name="Platinum", price=65, tagline="Steakhouse cuts and lobster",
         adds="Everything in Gold, plus filet mignon, ribeye, New York strip, picanha, short rib, beef tongue, Kurobuta sausage, wagyu zabuton, wagyu bavette and lobster tail.",
         cuts=["Filet mignon*", "Ribeye", "New York strip", "Picanha", "Short rib", "Beef tongue",
               "Kurobuta sausage", "Wagyu zabuton*", "Wagyu bavette*", "Lobster tail*"],
         note="*One per guest."),
    dict(name="Ruby", price=79, tagline="Japanese A5 wagyu",
         adds="Everything in Platinum, plus Japanese A5 wagyu and a premium nigiri.",
         cuts=["Japanese A5 wagyu — top blade or zabuton*", "A5 wagyu caviar nigiri*", "A5 wagyu & uni nigiri*",
               "Scallop caviar nigiri*", "Scallop & uni nigiri*"],
         note="*Choose one A5 cut and one premium nigiri per guest."),
]
ALL_TIERS_INCLUDE = dict(
    grill=["Chicken breast", "Chicken thigh", "Beef sausage", "Shrimp", "Squid", "Duroc pork belly",
           "Duroc pork jowl", "Lamb chop (one per guest)"],
    kitchen=["Wagyu tartare (one per guest)", "Chawanmushi", "Wagyu donabe", "Harumaki", "Tempura shrimp",
             "Truffle fries", "Beef fried rice", "Takoyaki", "Tonkotsu ramen", "Shoyu ramen", "Chicken gyoza"],
    sushi=["Scallop sashimi (one per guest)", "Yellowtail nigiri", "Salmon nigiri", "Tuna nigiri",
           "Spicy salmon hand roll", "Spicy tuna hand roll", "Yellowtail hand roll", "Unagi hand roll",
           "Salmon crudo", "Yellowtail crudo"],
    sauces=["Garlic", "Yuzu", "Miso", "Oil & pepper", "Shichimi", "Ginger soy", "Negi", "Tare"],
)
LUNCH = dict(price=29, days="Monday – Thursday", time="12 – 3 PM",
             grill=["Wagyu beef belly", "Wagyu brisket", "Rib meat", "Skirt steak", "Beef sausage",
                    "Duroc pork jowl", "Duroc pork belly", "Chicken breast", "Chicken thigh", "Squid", "Shrimp"],
             sushi=["Tuna nigiri", "Salmon nigiri", "California roll", "Spicy tuna hand roll", "Spicy salmon hand roll"],
             kitchen=["Tempura shrimp", "Takoyaki", "Chicken gyoza", "Harumaki", "Truffle fries",
                      "Tonkotsu ramen", "Shoyu ramen"])
LUNCH_DISCOUNT = "À la carte (izakaya, entrées, sushi) is 20% off Monday – Thursday, 12 – 3 PM. AYCE lunch is not eligible."

POLICIES = [  # in-store menu "AYCE General Policy"
    ("Kids", 'Under 39" dine free · 39"–51" pay 50% of the tier price'),
    ("Dining time", "90 minutes · parties of 6+ get 110 minutes · final orders 15 minutes before time ends"),
    ("Same tier", "Everyone at the table dines on the same tier"),
    ("Gratuity", "Added automatically for parties of 5 or more"),
    ("Leftovers", "Uneaten AYCE items are charged at à la carte price · AYCE items can't be taken to go"),
    ("Over time", "Parties that go past their dining time may be charged up to 20% of the final bill"),
    ("Outside food", "Not permitted · no refunds"),
]
SAFETY = "Consuming raw or undercooked meats, seafood, or eggs may increase your risk of foodborne illness."

ALACARTE = [  # "Not Feeling Yakiniku?" menu image
    ("Ramen", "Tonkotsu or shoyu, with chashu pork, egg, bamboo and corn", "$15"),
    ("Yakisoba", "Veggie $13 · chicken $15 · wagyu beef $16 · shrimp $17", ""),
    ("Fried rice", "Veggie $13 · chicken $15 · wagyu beef $16 · shrimp $17", ""),
    ("Hibachi", "Chicken or shrimp $16 · ribeye or salmon $21, with white rice and veggies", ""),
    ("Sake don", "Salmon belly over furikake, ikura, negi, tare and rice", "$28"),
    ("Unagi don", "Seared eel over furikake, avocado, bonito, oshinko and rice", "$28"),
    ("Wagyu burger", "With truffle fries", "$15"),
    ("Sashimi (3) & nigiri (2)", "Bluefin tuna with gold leaf $14 · salmon $9 · yellowtail $10", ""),
    ("Classic rolls", "California $7 · spicy salmon, spicy tuna or spicy yellowtail $9", ""),
    ("Izakaya plates", "Edamame, gyoza, harumaki, truffle fries, miso soup, wagyu beef soup, kimchi", "from $3"),
]
A5_ALACARTE = [("A5 ribeye", 39), ("A5 filet mignon", 36), ("A5 New York strip", 28), ("A5 zabuton (2)", 21), ("A5 top blade (1)", 19)]

# ── Drinks (current /drinks embeds, 2026-10-23; two older embeds with lower prices are ignored) ──
HAPPY_HOUR = dict(when=["Monday – Friday, 3 – 6 PM", "Every day, 9 PM – close"],
                  items=[("12 oz draft beer", 5), ("Frozen margarita", 5), ("Well drinks", 5), ("Toki Highball", 7),
                         ("Yuzu No. 7", 7), ("Lychee Bloom", 9), ("Banana Daiquiri", 9)])
COCKTAILS = [
    ("Matcha-Tini", 14, "Vodka · matcha · Frangelico · Licor 43 · cream"),
    ("Old Meiji", 14, "Iwai whisky · Woodford rye · sakura · demerara"),
    ("Lychee Bloom", 13, "Fords gin · nigori sake · lychee liqueur · lemon"),
    ("Yuzu No. 7", 13, "Haku yuzu vodka · yuzu · prosecco"),
    ("Piña No Binchō", 13, "Herradura reposado · lime · ginger · charred pineapple"),
    ("Banana Daiquiri", 13, "Diplomático Planas rum · banana liqueur · pineapple · lime"),
    ("Toki Highball", 11, "Suntory Toki whisky · sparkling water · lemon peel"),
    ("Frozen Margarita", 11, "El Jimador · classic, strawberry, mango, lychee or yuzu"),
]
MOCKTAILS = [("Lychee Appletini", 8, "Lychee · apple · lemon"), ("Ginger Mojito", 8, "Ginger · lime · mint · soda"),
             ("Yuzu Chill", 8, "Yuzu lemonade slush"), ("Matcha Lemonade", 8, "Fresh lemonade · matcha float")]
WHISKY = [("Suntory Toki", 12), ("Akashi", 14), ("Iwai Tradition", 16), ("Nikka Coffey", 18),
          ("Hibiki Harmony", 21), ("Yamazaki 12 Year", 42), ("Yamazaki 18 Year (1 oz)", 78)]
SAKE = [("Sho Chiku Bai Nigori", "300 ml", "12 / 16"), ("Kikusui Funaguchi Honjozo Nama Genshu", "200 ml", "15"),
        ("Mio Sparkling", "300 ml", "21"), ("Dassai 45 Junmai Daiginjo", "300 ml", "29"),
        ("Kamitaka 'Octopus' Junmai", "720 ml", "15 / 57"), ("Onikoroshi 'Demon Slayer' Honjozo", "720 ml", "62"),
        ("Shonan 'Tidal Wave' Junmai Ginjo", "720 ml", "87"), ("Born Gold Muroka Junmai Daiginjo", "720 ml", "93")]
BEER = [("Asahi", "7 / 9"), ("Sapporo", "7 / 9"), ("Michelob Ultra", "6 / 8"), ("Rotating local draft", "7 / 9"),
        ("Kirin Ichiban (bottle)", "8"), ("Kirin Light (bottle)", "8"), ("Suntory -196 seltzer", "7"),
        ("Asahi 0.0 (non-alcoholic)", "7"), ("Athletic Brewing (non-alcoholic)", "8")]
WINE = [("Bollicini Prosecco", "10 / 34"), ("Placido Pinot Grigio", "11 / 35"), ("Peju Sauvignon Blanc", "18 / 64"),
        ("Alexander Valley Chardonnay", "15 / 54"), ("Torbreck Australian White Blend", "16 / 58"),
        ("Coppola Pinot Noir", "14 / 46"), ("Director's Cut Cabernet", "16 / 58"),
        ("Aska Bolgheri Rosso", "24 / 89"), ("Laurent-Perrier Champagne (bottle)", "121")]

# ── Instagram reels (@hono.bbq, captions are the restaurant's own; covers saved locally 2026-10-24) ──
# Titles are shortened from each reel's first caption line. Covers live in assets/img/ig-<code>-480.jpg
# because Instagram image URLs expire. Videos load only when a guest taps play (no IG widget weight).
REELS = [
    dict(code="DdICkYmgBBy", title="A night out at Hono", alt="Two guests toast with cocktails over wagyu on the grill", tag="night"),
    dict(code="Dd7FSw8udaR", title="Our fan-favorite Matcha-Tini", alt="A bartender holds up a frothy green Matcha-Tini", tag="drinks"),
    dict(code="DcWnvyMtdIZ", title="Drinks. Vibe. Food.", alt="Drinks, food and the dining room at Hono", tag="drinks"),
    dict(code="DeQBhzrxsaH", title="Wagyu + cocktails", alt="Unlimited wagyu paired with Japanese-inspired cocktails", tag="drinks"),
    dict(code="DdUsXuzBHoW", title="A fun night out with friends", alt="Friends gather around the grill at Hono", tag="night"),
    dict(code="DesSfEsS3Tu", title="Send this to your grill partner", alt="Japanese BBQ cooking at the table", tag="night"),
]

# ── Social proof (Google Business Profile, 2026-10-23) ──
PROOF = dict(google_rating="4.8", google_reviews_floor="600+",   # 604 on 2026-10-23; update when it passes 700
             review_topics=["all-you-can-eat", "sushi", "matcha martini", "salad bar", "wagyu tartare"])

# ── Unverified items: rendered ONLY when their key is in CONFIRMED ──
PENDING = {
    "parking":     dict(q="Is parking free, and where do guests park?",
                        text="Free parking in the shopping-center lot right outside our door."),
    "walkins":     dict(q="Do you accept walk-ins?",
                        text="Walk-ins are welcome; reservations are recommended on weekends."),
    "patio":       dict(q="Is there (covered) patio seating? Yelp lists it.",
                        text="Covered patio seating is available, weather permitting."),
    "salad_bar":   dict(q="Does AYCE include the salad bar, soup and dessert (fruit, soft-serve)? Reviews and D Magazine mention them; the menu does not.",
                        text="Every AYCE tier also includes our salad bar, soup and dessert."),
    "group_max":   dict(q="What is the largest party you can seat on one reservation? Private room or buyout?",
                        text="We can seat groups of up to [N] guests."),
    "group_contact": dict(q="Who handles group bookings (name)?",
                        text="Our group dining host, [NAME], will help you plan the night."),
    "top_order":   dict(q="Is wagyu beef belly the most-ordered item?",
                        text="It's the cut guests order first and order most."),
    "wifi":        dict(q="Free Wi-Fi for guests? (Yelp lists it)", text="Free guest Wi-Fi."),
    "facebook":    dict(q="What is the Facebook page URL (not a share link)?", text=""),
}
# key -> "who confirmed, when". Add a line here when the client answers, then rebuild.
CONFIRMED = {
}

def ok(key):
    return key in CONFIRMED
