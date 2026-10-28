#!/usr/bin/env python3
"""Build the JCH Auto Works static site.

    python3 build.py            -> writes ../dist (deploy this folder to Netlify)

Business facts live in site.json. Page copy lives below. Every page gets a unique
<title> (<= 60 chars) and meta description (<= 160 chars), canonical URL, Open Graph,
AutoBodyShop JSON-LD and (inner pages) BreadcrumbList JSON-LD.

PHOTOS: the two shop images are ILLUSTRATIVE (generated concepts), not JCH photos.
While site.json media.illustrative is true, every visible use carries an
"Illustrative image" label and no copy or alt text presents them as JCH's shop or work.
"""
import json, html, shutil, datetime, re
from pathlib import Path

SRC = Path(__file__).parent
DIST = SRC.parent / "dist"
S = json.loads((SRC / "site.json").read_text())
B, C = S["business"], S["claims"]
DOMAIN = B["domain"].rstrip("/")
TODAY = datetime.date.today().isoformat()
ILLUS = S["media"]["illustrative"]
e = html.escape

def show(key):
    return C.get(key, {}).get("show") and C[key].get("text")

# ---------------------------------------------------------------- icons
I = {
 "phone": '<path d="M5 3h3l2 5-2.5 1.5a11 11 0 0 0 5 5L14 12l5 2v3a2 2 0 0 1-2 2A15 15 0 0 1 3 5a2 2 0 0 1 2-2z"/>',
 "arrow": '<path d="M5 12h14M13 6l6 6-6 6"/>',
 "chev": '<path d="M6 9l6 6 6-6"/>',
 "menu": '<path d="M4 7h16M4 12h16M4 17h16"/>',
 "close": '<path d="M6 6l12 12M18 6L6 18"/>',
 "pin": '<path d="M12 21s-7-6.2-7-11.5A7 7 0 0 1 19 9.5C19 14.8 12 21 12 21z"/><circle cx="12" cy="9.5" r="2.5"/>',
 "shield": '<path d="M12 3l8 3v6c0 4.5-3.4 8.3-8 9-4.6-.7-8-4.5-8-9V6z"/><path d="M8.5 12l2.5 2.5 4.5-5"/>',
 "home": '<path d="M3 11l9-7 9 7"/><path d="M5 10v10h14V10"/><path d="M10 20v-5h4v5"/>',
 "badge": '<circle cx="12" cy="9" r="5"/><path d="M8.5 13l-1.5 8 5-3 5 3-1.5-8"/>',
 "clock": '<circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 2"/>',
 "doc": '<path d="M7 3h7l5 5v13H7z"/><path d="M14 3v5h5M10 13h6M10 17h6"/>',
 "car": '<path d="M3 13l2-5a2 2 0 0 1 2-1.3h10A2 2 0 0 1 19 8l2 5v4h-2"/><path d="M5 17H3v-4h18"/><circle cx="7" cy="17" r="2"/><circle cx="17" cy="17" r="2"/><path d="M9 17h6"/>',
 "spray": '<path d="M9 9h6v12H9z"/><path d="M10 9V6h4v3M12 6V4M17 4h.01M19 6h.01M17 8h.01M20 3h.01"/>',
 "dent": '<path d="M3 14c3 0 4-4 9-4s6 4 9 4"/><path d="M3 18h18"/><path d="M12 4v4M10 6l2 2 2-2"/>',
 "frame": '<path d="M5 4v16M19 4v16M5 8h14M5 16h14"/><circle cx="5" cy="12" r="1.5"/><circle cx="19" cy="12" r="1.5"/>',
 "glass": '<path d="M4 7c5-3 11-3 16 0l-2 10H6z"/><path d="M9 9l-1.5 5M13 9l-2 6"/>',
 "chip": '<rect x="7" y="7" width="10" height="10" rx="1.5"/><path d="M10 3v4M14 3v4M10 17v4M14 17v4M3 10h4M3 14h4M17 10h4M17 14h4"/>',
 "upload": '<path d="M12 16V4M7 9l5-5 5 5"/><path d="M4 16v4h16v-4"/>',
 "people": '<circle cx="9" cy="8" r="3.5"/><path d="M2.5 20a6.5 6.5 0 0 1 13 0"/><circle cx="17" cy="9" r="2.5"/><path d="M16 14.2a5 5 0 0 1 5.5 5.8"/>',
 "camera": '<path d="M4 8h3l2-3h6l2 3h3v11H4z"/><circle cx="12" cy="13" r="3.5"/>',
}
def icon(name, cls=""):
    return f'<svg class="{cls}" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">{I[name]}</svg>'

TEL = f'tel:{B["phoneE164"]}'
ADDR_LINE = f'{B["street"]}, {B["city"]}, {B["region"]} {B["postal"]}'
PANEL, BAY = "illustrative-technician-panel-prep", "illustrative-collision-repair-bay"
EXT = "jch-auto-works-shop-exterior-palmyra-ny"   # REAL photo of the shop
DIMS = {EXT: (1600, 800)}

def img(name, alt, eager=False, sizes="100vw"):
    load = 'fetchpriority="high"' if eager else 'loading="lazy" decoding="async"'
    return (f'<img src="img/{name}-1600.webp" srcset="img/{name}-800.webp 800w, img/{name}-1600.webp 1600w" '
            f'sizes="{sizes}" width="{DIMS.get(name, (1600, 900))[0]}" height="{DIMS.get(name, (1600, 900))[1]}" alt="{e(alt)}" {load}>')

def figure(name, alt, cls="", sizes="100vw", caption=""):
    """A visible photo. While images are illustrative, the label says so plainly."""
    label = caption if name == EXT else ("Illustrative image" if ILLUS else caption)
    cap = f'<figcaption>{e(label)}</figcaption>' if label else ""
    return f'<figure class="photo {cls}">{img(name, alt, sizes=sizes)}{cap}</figure>'

def btn(label, href, kind="", ic=None, track=""):
    i = icon(ic) if ic else ""
    t = f' data-track="{track}"' if track else ""
    return f'<a class="btn {kind}" href="{href}"{t}>{i}{e(label)}</a>'

# ---------------------------------------------------------------- services
SERVICES = [
 dict(slug="collision-repair", name="Collision Repair", ic="car", code="SVC 01", short="Front, rear and side impacts",
      blurb="Front, rear and side impacts, from first inspection to final check.",
      title="Collision Repair Shop in Palmyra, NY", desc="Collision repair in Palmyra, NY from a family-owned shop: 30+ years of auto body expertise, an I-CAR certified technician, free estimates and insurance help."),
 dict(slug="auto-body-paint", name="Auto Body & Paint", ic="spray", code="SVC 02", short="Bumpers, panels, refinishing",
      blurb="Bumper and panel repair, refinished and blended to match your car.",
      title="Auto Body & Paint Repair, Palmyra NY", desc="Bumper repair, body panel repair and paint refinishing in Palmyra, NY. Free estimates and a lifetime workmanship warranty from JCH Auto Works."),
 dict(slug="paintless-dent-repair", name="Paintless Dent Repair", ic="dent", code="SVC 03", short="Dents and dings, factory paint kept",
      blurb="Minor dents and dings removed without touching your factory paint.",
      title="Paintless Dent Repair, Palmyra NY", desc="Paintless dent repair near Palmyra and Wayne County, NY. Remove minor dents and dings while keeping your factory paint. Free estimates."),
 dict(slug="structural-repair", name="Structural Repair", ic="frame", code="SVC 04", short="The damage you can't see",
      blurb="Repairs to the hidden structure that protects you in a crash.",
      title="Structural & Frame Repair, Palmyra NY", desc="Structural collision repair near Palmyra, NY. Careful inspection and repair of hidden damage by an experienced, I-CAR certified team."),
 dict(slug="glass", name="Windshield & Glass", ic="glass", code="SVC 05", short="Handled with your repair",
      blurb="Windshield and glass replacement handled as part of your repair.",
      title="Windshield & Auto Glass, Palmyra NY", desc="Windshield and auto glass replacement in Palmyra, NY, coordinated with your collision repair by JCH Auto Works. Free estimates."),
 dict(slug="diagnostics-calibration", name="Diagnostics & Calibration", ic="chip", code="SVC 06", short="Scans and safety systems",
      blurb="Scans and the calibrations modern safety systems need after a crash.",
      title="Diagnostics & ADAS Calibration, Palmyra", desc="Post-collision diagnostic scans and driver-assistance (ADAS) calibration near Palmyra, NY. Ask JCH Auto Works what your vehicle needs."),
]
SVC = {s["slug"]: s for s in SERVICES}

# ---------------------------------------------------------------- chrome
NAV = [("insurance.html", "Insurance"), ("our-work.html", "Our Work"), ("about.html", "About"), ("fleet.html", "Fleet & Business"), ("faq.html", "FAQ"), ("contact.html", "Contact")]

def header(active):
    svc_links = "".join(f'<a href="{s["slug"]}.html">{e(s["name"])}<span>{e(s["short"])}</span></a>' for s in SERVICES)
    svc_links += '<a class="all" href="services.html">All services →</a>'
    cur = ' aria-current="page"'
    nav = "".join(f'<a href="{h}"{cur if h == active else ""}>{t}</a>' for h, t in NAV)
    dnav = "".join(f'<li><a href="{h}">{t}</a></li>' for h, t in NAV)
    dsvc = "".join(f'<li><a href="{s["slug"]}.html">{e(s["name"])}</a></li>' for s in SERVICES)
    return f'''<a class="skip" href="#main">Skip to content</a>
<div class="topbar"><div class="wrap">
  <span data-open-now><span class="dot"></span><span data-open-text>Mon–Fri 8:00 AM – 5:00 PM</span></span>
  <span>{e(ADDR_LINE)} · <a href="{TEL}" data-track="topbar">{B["phone"]}</a></span>
</div></div>
<header class="header" data-header><div class="wrap">
  <a class="brand" href="index.html" aria-label="{e(B["shortName"])} home"><img src="img/jch-auto-works-logo-320.webp" width="320" height="206" alt="JCH Auto Works LLC"></a>
  <nav class="nav" aria-label="Main">
    <div class="nav-group"><button type="button" aria-expanded="false" aria-controls="svc-menu"{" aria-current=\"page\"" if active == "services" else ""}>Services{icon("chev")}</button>
      <div class="menu" id="svc-menu">{svc_links}</div></div>
    {nav}
  </nav>
  <div class="header-cta">{btn(B["phone"], TEL, "btn--ghost", "phone", "header")}{btn("Free Estimate", "estimate.html", "", None, "header")}</div>
  <button class="burger" type="button" aria-expanded="false" aria-controls="drawer" aria-label="Open menu">{icon("menu")}</button>
</div></header>
<div class="drawer" id="drawer" hidden role="dialog" aria-modal="true" aria-label="Menu">
  <div class="drawer-head"><a href="index.html" class="brand"><img src="img/jch-auto-works-logo-320.webp" width="320" height="206" alt="JCH Auto Works home"></a><button class="burger" type="button" data-close aria-label="Close menu">{icon("close")}</button></div>
  <p class="drawer-status" data-open-now><span class="dot"></span><span data-open-text>Mon–Fri 8:00 AM – 5:00 PM</span></p>
  <nav aria-label="Mobile"><ul class="drawer-list">
    <li><a href="index.html">Home</a></li>
    <li><details><summary>Services{icon("chev")}</summary><ul class="drawer-sub">{dsvc}<li><a href="services.html">All services</a></li></ul></details></li>
    {dnav}</ul></nav>
  <div class="drawer-foot">{btn("Request a Free Estimate", "estimate.html", "", None, "drawer")}<a class="drawer-call" href="{TEL}" data-track="drawer">{icon("phone")}Call {B["phone"]}</a></div>
</div>'''

def footer(slug):
    svc = "".join(f'<li><a href="{s["slug"]}.html">{e(s["name"])}</a></li>' for s in SERVICES)
    hours = "".join(f'<li>{h["days"]}: {"Closed" if h.get("closed") else h["open"] + " – " + h["close"]}</li>' for h in B["hours"])
    reg = f'<p>{e(C["nysRegistered"]["text"])}{" #" + e(C["nysRegistered"]["facilityNumber"]) if C["nysRegistered"].get("facilityNumber") else ""}</p>' if show("nysRegistered") else ""
    bar = "" if slug == "estimate" else f'<div class="actionbar is-hidden" data-actionbar>{btn("Call", TEL, "btn--ghost", "phone", "actionbar")}{btn("Free Estimate", "estimate.html", "", None, "actionbar")}</div>'
    return f'''<footer class="footer"><div class="wrap">
  <div class="footer-grid">
    <div class="stack"><a class="brand" href="index.html"><img src="img/jch-auto-works-logo-320.webp" width="320" height="206" alt="JCH Auto Works LLC" loading="lazy"></a>
      <p>Family-owned collision repair on Route 21 in Palmyra, New York.</p>{reg}</div>
    <div><h2 class="fh">Services</h2><ul>{svc}</ul></div>
    <div><h2 class="fh">Help</h2><ul><li><a href="estimate.html">Request an estimate</a></li><li><a href="insurance.html">Insurance claims</a></li><li><a href="fleet.html">Fleet &amp; business</a></li><li><a href="our-work.html">Our work</a></li><li><a href="reviews.html">Reviews</a></li><li><a href="faq.html">FAQ</a></li></ul></div>
    <div><h2 class="fh">Visit</h2><ul>
      <li><a href="{B["mapsUrl"]}" target="_blank" rel="noopener" data-track="footer">{e(B["street"])}<br>{e(B["city"])}, {B["region"]} {B["postal"]}</a></li>
      <li><a href="{TEL}" data-track="footer">{B["phone"]}</a></li>
      <li><a href="mailto:{B["email"]}" data-track="footer">{B["email"]}</a></li>
      {hours}
      <li><a href="{B["facebook"]}" target="_blank" rel="noopener">Facebook</a></li></ul></div>
  </div>
  <div class="footer-bottom"><span>© {datetime.date.today().year} {e(B["name"])} · <a href="privacy.html">Privacy</a></span><span>Website by {e(S["credits"]["builtBy"])}</span></div>
</div></footer>
{bar}'''

def business_ld():
    return {
        "@context": "https://schema.org", "@type": "AutoBodyShop", "@id": DOMAIN + "/#business",
        "name": B["name"], "url": DOMAIN + "/", "telephone": B["phoneE164"], "email": B["email"],
        "image": DOMAIN + "/img/jch-auto-works-og.jpg", "logo": DOMAIN + "/img/jch-auto-works-logo-320.png",
        "address": {"@type": "PostalAddress", "streetAddress": B["street"], "addressLocality": B["city"], "addressRegion": B["region"], "postalCode": B["postal"], "addressCountry": "US"},
        "geo": {"@type": "GeoCoordinates", "latitude": B["geo"]["lat"], "longitude": B["geo"]["lng"]},
        "openingHoursSpecification": [{"@type": "OpeningHoursSpecification", "dayOfWeek": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"], "opens": "08:00", "closes": "17:00"}],
        "areaServed": [{"@type": "City", "name": "Palmyra, NY"}, {"@type": "AdministrativeArea", "name": "Wayne County, NY"}],
        "sameAs": [B["facebook"]],
        "makesOffer": [{"@type": "Offer", "itemOffered": {"@type": "Service", "name": s["name"]}} for s in SERVICES],
    }

def page(slug, title, desc, body, crumbs=None, extra_ld=None, active="", preload=None):
    canonical = DOMAIN + "/" + ("" if slug == "index" else slug)
    full_title = title if "JCH" in title else f"{title} | {B['shortName']}"
    assert len(full_title) <= 60, (slug, len(full_title), full_title)
    assert len(desc) <= 160, (slug, len(desc))
    lds = [business_ld()]
    if crumbs:
        lds.append({"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
            {"@type": "ListItem", "position": i + 1, "name": n, "item": DOMAIN + "/" + ("" if h == "index" else h)} for i, (n, h) in enumerate([("Home", "index")] + crumbs)]})
    if extra_ld: lds += extra_ld
    ld = "\n".join(f'<script type="application/ld+json">{json.dumps(x, ensure_ascii=False)}</script>' for x in lds)
    cfg = {"formsMode": S["integrations"]["formsMode"], "ga4Id": S["integrations"]["ga4Id"], "gtmId": S["integrations"]["gtmId"], "phone": B["phone"]}
    gsc = f'<meta name="google-site-verification" content="{e(S["integrations"]["searchConsoleToken"])}">\n' if S["integrations"]["searchConsoleToken"] else ""
    pre = f'<link rel="preload" as="image" href="img/{preload}-1600.webp" imagesrcset="img/{preload}-800.webp 800w, img/{preload}-1600.webp 1600w" imagesizes="100vw">\n' if preload else ""
    robots = '<meta name="robots" content="noindex">\n' if slug == "404" else ""
    return f'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{e(full_title)}</title>
<meta name="claude:viewport-fit-sides" content="cover">
<meta name="description" content="{e(desc)}">
{robots}<link rel="canonical" href="{canonical}">
<meta name="theme-color" content="#0d1218">
<meta property="og:type" content="website"><meta property="og:site_name" content="{e(B["name"])}">
<meta property="og:title" content="{e(full_title)}"><meta property="og:description" content="{e(desc)}">
<meta property="og:url" content="{canonical}"><meta property="og:image" content="{DOMAIN}/img/jch-auto-works-og.jpg">
<meta property="og:image:width" content="1200"><meta property="og:image:height" content="630">
<meta name="twitter:card" content="summary_large_image">
{gsc}<link rel="icon" href="img/favicon.png" type="image/png"><link rel="apple-touch-icon" href="img/apple-touch-icon.png">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Barlow+Condensed:wght@600;700&family=IBM+Plex+Mono:wght@500&family=Manrope:wght@400;500;600;700&display=swap">
{pre}<link rel="stylesheet" href="assets/style.css">
<script>window.JCH={json.dumps(cfg)};</script>
{ld}
</head>
<body>
{header(active)}
<main id="main">
{body}
</main>
{footer(slug)}
<script src="assets/app.js" defer></script>
</body>
</html>
'''

def page_hero(h1, lede, crumbs, bgimg=BAY, eyebrow=None, cta=True):
    items = ['<li><a href="index.html">Home</a></li>']
    for i, (n, h) in enumerate(crumbs):
        items.append(f'<li><a href="{h}.html">{e(n)}</a></li>' if i < len(crumbs) - 1 else f'<li><span aria-current="page">{e(n)}</span></li>')
    eb = f'<span class="eyebrow">{eyebrow}</span>' if eyebrow else ""
    bg = f'<div class="bg">{img(bgimg, "", eager=True)}</div>' if bgimg else ""
    ctas = f'<div class="btn-row" data-hero-cta>{btn("Request a Free Estimate", "estimate.html", "", None, "page-hero")}{btn("Call " + B["phone"], TEL, "btn--ghost", "phone", "page-hero")}</div>' if cta else ""
    tag = "<span class='hero-tag'>Illustrative image</span>" if (bgimg and bgimg != EXT and ILLUS) else ""
    return f'''<section class="page-hero">{bg}{tag}<div class="wrap">
<nav aria-label="Breadcrumb"><ol class="crumbs">{"".join(items)}</ol></nav>{eb}
<h1>{h1}</h1><p class="lede">{lede}</p>{ctas}</div></section>'''

def final_cta(h2="Let’s get you back to what matters."):
    hours = "<br>".join(f'{h["days"]}: {"Closed" if h.get("closed") else h["open"] + " – " + h["close"]}' for h in B["hours"])
    return f'''<section class="band final" aria-labelledby="final-h"><div class="bg">{img(EXT, "")}</div><div class="wrap">
<div class="final-grid">
  <div class="stack-lg"><span class="eyebrow">Palmyra, New York</span><h2 id="final-h">{h2}</h2>
  <p class="lede">Send photos for a head start, or bring the vehicle by for a free, no-obligation estimate.</p>
  <div class="btn-row">{btn("Request an Estimate", "estimate.html", "", None, "final")}{btn("Call Our Team", TEL, "btn--ghost", "phone", "final")}</div></div>
  <dl class="info-grid">
    <div><dt>Shop</dt><dd><a href="{B["mapsUrl"]}" target="_blank" rel="noopener" data-track="final">{e(B["street"])}<br>{e(B["city"])}, {B["region"]} {B["postal"]}</a><a class="textlink" href="{B["mapsUrl"]}" target="_blank" rel="noopener" data-track="final">Directions {icon("arrow")}</a></dd></div>
    <div><dt>Hours</dt><dd>{hours}</dd></div>
    <div><dt>Reach us</dt><dd><a href="{TEL}" data-track="final">{B["phone"]}</a><br><a href="mailto:{B["email"]}" data-track="final">{B["email"]}</a></dd></div>
  </dl>
</div></div></section>'''

def faq_block(items):
    return '<div class="faq">' + "".join(f'<details><summary>{e(q)}</summary><div class="a">{a}</div></details>' for q, a in items) + "</div>"

def faq_ld(items):
    return {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [
        {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": re.sub("<[^>]+>", "", a)}} for q, a in items]}

# ---------------------------------------------------------------- shared copy (claims as worded on the shop's own former site)
WARRANTY = "Our workmanship is warranted for as long as you own the vehicle. Parts carry the manufacturer’s warranty. If something isn’t right with our repair, bring it back and we’ll make it right."

FAQ_INS = [
 ("What should I do right after a collision?", "<p>Get to safety and call 911 if anyone is hurt. Exchange information, photograph the scene and every vehicle, and notify your insurer. In New York, a crash with injury, death, or property damage over $1,000 must be reported to the DMV on form MV-104 within 10 days. Then call us for the next step.</p>"),
 ("Do I have to use the shop my insurance company suggests?", "<p>No. New York law gives you the right to choose where your vehicle is repaired. Your insurer can recommend a shop, but the choice is yours.</p>"),
 ("Can you help with my insurance claim?", "<p>Yes. We work with all major insurance companies. We communicate with your provider and make sure the repair is documented according to their guidelines. Coverage decisions are between you and your insurer, and we keep you informed.</p>"),
 ("What if more damage is found after the repair starts?", "<p>It’s common. Removing damaged parts often reveals damage behind them. It gets documented, sent to your insurer for approval if a claim is involved, and discussed with you before any extra work.</p>"),
 ("How do I get an estimate?", "<p>Estimates are free with no obligation. Start online with photos, call, or stop by. Photo estimates are preliminary; the final estimate follows an in-person inspection.</p>"),
 ("My car isn’t drivable. What now?", f'<p>Call us at <a href="{TEL}">{B["phone"]}</a> and tell us where the vehicle is. Many policies include towing coverage, so check yours too. We’ll talk through how to get the vehicle here.</p>'),
 ("How does a rental car work during my repair?", "<p>Rental coverage depends on your policy or the at-fault driver’s insurer. Ask your adjuster what your claim includes. We keep you and the insurer updated so the rental lines up with the repair.</p>"),
]
FAQ_GENERAL = [
 ("What services do you offer?", "<p>Cosmetic and structural vehicle repair, bumper repair, paint repair, paintless dent removal, windshield and glass replacement, and vehicle diagnostics and calibration.</p>"),
 ("How long will my repair take?", "<p>It depends on the damage, the repairs needed and parts availability. We give you an estimated timeline after inspecting the vehicle, and we provide repair updates while your vehicle is at our facility.</p>"),
 ("How much will my repair cost?", "<p>Cost depends on the extent of the damage, the parts and materials needed, and the labor required. Your estimate is free, and we always provide transparent pricing information.</p>"),
 ("Do you warranty your repairs?", "<p>" + WARRANTY + "</p>"),
 ("What are your hours?", "<p>Monday through Friday, 8:00 AM to 5:00 PM. Closed Saturday and Sunday.</p>"),
 ("Where are you located?", f'<p>{e(ADDR_LINE)}. <a href="{B["mapsUrl"]}" target="_blank" rel="noopener">Get directions</a>.</p>'),
]

def aside(points=None, title="Talk to the shop"):
    pts = points or ["Free, no-obligation estimates", "Help with your insurance claim", "Lifetime workmanship warranty", "I-CAR certified technician"]
    return f'''<aside class="aside-card" aria-label="Get an estimate"><span class="eyebrow">Free estimate</span><h2 class="aside-h">{title}</h2>
<ul class="check">{"".join(f"<li>{e(p)}</li>" for p in pts)}</ul>
{btn("Request an Estimate", "estimate.html", "", None, "aside")}{btn("Call " + B["phone"], TEL, "btn--ghost", "phone", "aside")}
<p class="small">Mon–Fri, 8:00 AM – 5:00 PM</p></aside>'''

def related(exclude):
    return '<div class="related">' + "".join(f'<a class="chip" href="{s["slug"]}.html">{e(s["name"])}</a>' for s in SERVICES if s["slug"] != exclude) + '<a class="chip" href="insurance.html">Insurance help</a></div>'

def svc_cards(feature=True):
    out = ""
    for i, s in enumerate(SERVICES):
        if feature and i == 0:
            out += f'''<a class="svc svc--feature" href="{s["slug"]}.html"><div class="img">{img(BAY, "", sizes="(max-width: 640px) 100vw, 40vw")}{"<span class=tag>Illustrative image</span>" if ILLUS else ""}</div>
<div><div class="svc-top"><span class="code">{s["code"]}</span>{icon(s["ic"])}</div><div class="svc-body"><h3>{e(s["name"])}</h3><p>{e(s["blurb"])}</p><span class="more">Collision repair →</span></div></div></a>'''
        else:
            out += f'''<a class="svc" href="{s["slug"]}.html"><div class="svc-top"><span class="code">{s["code"]}</span>{icon(s["ic"])}</div><div class="svc-body"><h3>{e(s["name"])}</h3><p>{e(s["blurb"])}</p><span class="more">Learn more →</span></div></a>'''
    return out

# ---------------------------------------------------------------- HOME
def home():
    proof = [("30+ yrs", "auto body expertise"), ("I-CAR", "certified technician"), ("Lifetime", "workmanship warranty"), ("Free", "estimates")]
    proof_html = "".join(f"<div><b>{a}</b><span>{b}</span></div>" for a, b in proof)
    diff = [
      ("home", "Family owned", "You deal with the people who run the shop."),
      ("clock", "30+ years’ expertise", "Decades of knowing how vehicles go back together."),
      ("badge", "I-CAR certified", "Current training on today’s materials and methods."),
      ("doc", "Free estimates", "No charge, no obligation, explained line by line."),
      ("shield", "Insurance help", "We work with all major insurers and your adjuster."),
      ("badge", "Lifetime warranty", "On workmanship, for as long as you own the vehicle."),
    ]
    diff_html = "".join(f'<article><div class="ic">{icon(i)}</div><h3>{e(t)}</h3><p>{e(d)}</p></article>' for i, t, d in diff)
    steps = [
      ("Tell us what happened", "First contact", ["Call, stop by, or send photos online.", "Not drivable? Call and we’ll plan how to get it here."], "Tip: wide photos from all four corners help as much as close-ups."),
      ("Inspection & estimate", "Free", ["We inspect the vehicle and write a free estimate.", "We explain it line by line."], "Shop term: teardown. Removing damaged parts to see the full repair before work begins."),
      ("Repair plan & approval", "Insurance", ["We work with your adjuster and document the repair.", "In New York, the choice of repair shop is yours."], "Shop term: supplement. An added estimate sent to the insurer when hidden damage is found."),
      ("Repair & checks", "In the shop", ["Body, structural and paint work by an experienced, I-CAR certified team.", "You get repair updates along the way."], "Any scans or calibrations your vehicle needs are identified up front."),
      ("Back on the road", "Pickup", ["We walk you through the work that was done.", "Lifetime workmanship warranty while you own the vehicle."], "Parts carry the manufacturer’s warranty."),
    ]
    tabs = "".join(f'<button class="ro-tab" role="tab" id="ro-t{i}" aria-controls="ro-p{i}" aria-selected="{"true" if i == 0 else "false"}" tabindex="{0 if i == 0 else -1}"><span class="n">{i+1:02d}</span><span>{e(t)}</span></button>' for i, (t, *_ ) in enumerate(steps))
    panels = "".join(f'<div class="ro-panel" role="tabpanel" id="ro-p{i}" aria-labelledby="ro-t{i}"{"" if i == 0 else " hidden"}><span class="eyebrow">Step {i+1} · {e(k)}</span><h3>{e(t)}</h3><ul>{"".join("<li>" + e(x) + "</li>" for x in pts)}</ul><p class="term">{e(note)}</p></div>' for i, (t, k, pts, note) in enumerate(steps))
    reviews = S["reviews"]["items"]
    if reviews:
        rv = '<div class="quotes">' + "".join(f'<figure class="quote"><blockquote>“{e(r["text"])}”</blockquote><figcaption>{e(r["name"])} · {e(r.get("source", ""))}</figcaption></figure>' for r in reviews[:3]) + "</div>"
    else:
        rv = f'''<div class="empty"><h3>Repaired at JCH?</h3><p>Tell your neighbors how it went. It helps someone in Palmyra choose a shop with confidence.</p><div class="btn-row">{btn("Share on Facebook", B["facebook"], "btn--ghost", None, "reviews")}</div></div>'''
    body = f'''
<section class="hero" aria-labelledby="hero-h">
  <div class="hero-media">{img(PANEL, "", eager=True)}</div>
  <div class="wrap">
    <span class="eyebrow">Collision repair · Palmyra, NY</span>
    <h1 id="hero-h">When the unexpected happens, <em>experience matters.</em></h1>
    <p class="lede">Family-owned collision repair on Route 21, backed by more than 30 years of auto body expertise.</p>
    <div class="btn-row" data-hero-cta>{btn("Request a Free Estimate", "estimate.html", "", None, "hero")}{btn("Call JCH Auto Works", TEL, "btn--ghost", "phone", "hero")}</div>
    <div class="proof">{proof_html}</div>
  </div>
  {"<span class='hero-tag'>Illustrative image</span>" if ILLUS else ""}
</section>

<section class="band band--paper" aria-labelledby="moment-h"><div class="wrap split split--wide-left">
  <div class="stack-lg reveal"><span class="eyebrow">After an accident</span>
    <h2 id="moment-h" class="h-md">An accident changes your day. The right shop changes what happens next.</h2>
    <p class="lede">You need clear answers and someone to guide you through it. That’s where we start.</p></div>
  <ul class="worries reveal" aria-label="Common concerns after a collision">
    <li><b>Insurance</b><span>We work with all major insurers and handle the documentation.</span></li>
    <li><b>Cost</b><span>Free estimate, explained line by line.</span></li>
    <li><b>Updates</b><span>We keep you informed while your vehicle is here.</span></li>
    <li><b>Quality</b><span>Lifetime workmanship warranty while you own the vehicle.</span></li>
  </ul>
</div></section>

<section class="band" aria-labelledby="diff-h"><div class="wrap side-head">
  <div class="stack reveal"><span class="eyebrow">The JCH difference</span><h2 id="diff-h">Experienced hands. Honest work.</h2><a class="textlink" href="about.html">About the shop {icon("arrow")}</a></div>
  <div class="diff reveal">{diff_html}</div>
</div></section>

<section class="band band--paper" aria-labelledby="svc-h"><div class="wrap stack-lg">
  <div class="stack reveal"><span class="eyebrow">Services</span><h2 id="svc-h" class="h-md">Expert care for every stage of collision repair.</h2></div>
  <div class="svc-grid reveal">{svc_cards()}</div>
</div></section>

<section class="band band--mid" aria-labelledby="ro-h"><div class="wrap stack-lg">
  <div class="split reveal" style="align-items:end"><div class="stack"><span class="eyebrow">The repair journey</span><h2 id="ro-h">From first call to keys in hand.</h2></div>
  <p class="lede">A general outline. Every repair is different, and we’ll walk you through yours.</p></div>
  <div class="ro reveal" data-ro>
    <div class="ro-head"><span>Repair order · <b>{e(B["name"])}</b></span><span>{e(B["city"])}, {B["region"]}</span></div>
    <div class="ro-body"><div class="ro-tabs" role="tablist" aria-label="Repair steps" aria-orientation="vertical">{tabs}</div><div>{panels}</div></div>
  </div>
</div></section>

<section class="band band--paper" aria-labelledby="people-h"><div class="wrap split">
  {figure(EXT, "JCH Auto Works shop building at 904 State Route 21 in Palmyra, NY", "photo--wide reveal", "(max-width:900px) 100vw, 50vw", "904 State Route 21, Palmyra")}
  <div class="stack-lg reveal"><span class="eyebrow">The people behind the work</span>
  <h2 id="people-h" class="h-md">Real people. Real experience. A reputation built one repair at a time.</h2>
  <p>JCH Auto Works is family owned and operated. The shop is new to Route 21; the expertise behind it spans more than 30 years.</p>
  <p>When you call, you reach the people who will repair your vehicle.</p>
  <a class="textlink" href="about.html">Our story {icon("arrow")}</a></div>
</div></section>

<section class="band" aria-labelledby="rev-h"><div class="wrap split">
  <div class="stack reveal"><span class="eyebrow">Reviews</span><h2 id="rev-h">Ask around Palmyra.</h2>
  <p class="lede">The best measure of a body shop is what your neighbors say after the repair.</p></div>
  <div class="reveal">{rv}</div>
</div></section>

<section class="band band--paper" aria-labelledby="ins-h"><div class="wrap layout-aside">
  <div class="stack-lg"><div class="stack reveal"><span class="eyebrow">Insurance & collision guidance</span><h2 id="ins-h" class="h-md">Straight answers to common questions.</h2></div>
  {faq_block(FAQ_INS[:4])}
  <a class="textlink" href="insurance.html">How insurance claims work {icon("arrow")}</a></div>
  {aside(["We work with all major insurers", "We communicate with your adjuster", "Repairs documented to insurer guidelines", "Free estimate, no obligation"])}
</div></section>

<section class="band band--mid" aria-labelledby="fleet-h"><div class="wrap split">
  <div class="stack-lg reveal"><span class="eyebrow">Fleet & business</span><h2 id="fleet-h" class="h-md">For vehicles that earn a living.</h2>
  <p class="lede">When a work vehicle is down, the business feels it. Let’s talk about how we can help.</p>
  <div class="btn-row">{btn("Start a business inquiry", "fleet.html", "", None, "fleet-home")}</div></div>
  <ul class="fleet-list reveal">
    <li><b>Fleet operators</b><span>Vans, pickups and company cars.</span></li>
    <li><b>Local businesses</b><span>Work trucks and branded vehicles.</span></li>
    <li><b>Dealerships</b><span>Body, paint and dent work.</span></li>
    <li><b>Insurance professionals</b><span>A local shop for your clients.</span></li>
  </ul>
</div></section>
{final_cta()}'''
    return page("index", "JCH Auto Works | Auto Body & Collision Repair, Palmyra NY",
                "Family-owned collision repair in Palmyra, NY: 30+ years of auto body expertise, an I-CAR certified technician, free estimates and a lifetime warranty.",
                body, extra_ld=[faq_ld(FAQ_INS[:4])], preload=PANEL)

# ---------------------------------------------------------------- SERVICES HUB
def services_hub():
    body = f'''{page_hero("Our services.", "Six ways we get your vehicle back to pre-accident condition. Every estimate is free.", [("Services", "services")], PANEL, "Services")}
<section class="band band--paper"><div class="wrap stack-lg"><div class="svc-grid">{svc_cards()}</div>
<p class="lede">Not sure what you need? <a href="estimate.html">Send photos</a> and we’ll tell you.</p></div></section>
{final_cta()}'''
    il = {"@context": "https://schema.org", "@type": "ItemList", "itemListElement": [{"@type": "ListItem", "position": i + 1, "url": DOMAIN + "/" + s["slug"], "name": s["name"]} for i, s in enumerate(SERVICES)]}
    return page("services", "Collision & Auto Body Services, Palmyra NY", "Collision repair, auto body and paint, paintless dent repair, structural repair, glass, and diagnostics and calibration in Palmyra, NY.", body, crumbs=[("Services", "services")], extra_ld=[il], active="services", preload=PANEL)

# ---------------------------------------------------------------- SERVICE PAGES
SVC_COPY = {
"collision-repair": ("Collision repair, done right.",
 "A good repair is one you can’t see and never think about again.",
 [("What it covers", "<ul><li>Bumper covers and reinforcements</li><li>Fenders, doors, hoods, quarter panels, trunk lids</li><li>Lights, grilles, mirrors and trim</li><li>Structural damage behind the panels</li><li>Paint refinishing and blending</li></ul>"),
  ("Why experience matters", "<p>Modern vehicles use high-strength steel, aluminum and bonded joints. Knowing which parts can be repaired and which must be replaced is what separates a repair that looks fine from one that is right.</p><p>Our team brings more than 30 years of auto body expertise and an I-CAR certified technician.</p>"),
  ("Working with your insurance", '<p>We work with all major insurance companies, communicate with your provider, and document the repair to their guidelines. <a href="insurance.html">How claims work</a>.</p>')],
 [("Can you fix my car if insurance already wrote an estimate?", "<p>Yes. First estimates are often written before the vehicle is taken apart. We inspect it and work with the insurer on anything that was missed.</p>"), FAQ_INS[3], FAQ_GENERAL[1]]),
"auto-body-paint": ("Body and paint that blends in.",
 "Bumper scuffs, creased panels, scratches and chips, repaired and refinished to match.",
 [("Body repair", "<p>Damaged panels and bumpers are repaired or replaced, cracked bumper covers are repaired when that’s the right call, and panel gaps are restored so doors, hoods and trunks close properly.</p>"),
  ("Paint and refinishing", "<p>Factory colors vary from car to car. A good match starts with the paint code, is adjusted to your vehicle’s actual color, and is blended into neighboring panels so it disappears in sunlight.</p><ul><li>Scratch and chip repair</li><li>Bumper repair and refinishing</li><li>Panel refinishing and blending</li></ul>"),
  ("Backed for as long as you own it", "<p>" + WARRANTY + "</p>")],
 [("Will the new paint match?", "<p>That’s the goal of every refinish: matched to your car as it is today and blended so the repair can’t be picked out.</p>"), ("Can a cracked bumper be repaired?", "<p>It depends on where it’s damaged and whether the mounting tabs and sensors are intact. We’ll tell you which option is right and why.</p>"), FAQ_GENERAL[2]]),
"paintless-dent-repair": ("Dents out. Factory paint stays.",
 "We remove minor dents and dings without altering the original paint finish.",
 [("How it works", "<p>Specialized tools work the metal back into shape from behind the panel, or pull it from outside with glue tabs. The paint is never broken, so your factory finish stays intact.</p>"),
  ("What it can fix", "<ul><li>Parking-lot door dings</li><li>Small dents and creases with unbroken paint</li><li>Many hail dents</li></ul>"),
  ("When it isn’t the right repair", "<p>Cracked or chipped paint, stretched metal, or a dent on a sharp body line or panel edge usually calls for conventional body and paint work. We’ll give you an honest answer.</p>")],
 [("Is paintless dent repair cheaper?", "<p>Often, since there’s no paint or filler. Your estimate is free, so we can compare options.</p>"), ("Will the dent come back?", "<p>No. Once the metal is restored, it stays in shape.</p>"), FAQ_GENERAL[3]]),
"structural-repair": ("The repair you can’t see matters most.",
 "Your vehicle’s structure is engineered to protect you in a crash. After a collision, it needs a careful look.",
 [("Signs of structural damage", "<ul><li>Doors, hood or trunk that no longer line up</li><li>Uneven panel gaps</li><li>The vehicle pulls to one side</li><li>Uneven tire wear after the accident</li></ul><p>Moderate impacts can shift structure even when the outside looks lightly damaged.</p>"),
  ("Why it’s worth getting right", "<p>Structural repair affects how your vehicle protects you in the next accident. It’s where experience counts most. We’ll explain what we find before any work begins.</p>"),
  ("After the repair", '<p>Structural work can affect driver-assistance sensors and cameras. <a href="diagnostics-calibration.html">Scans and calibration</a> may be needed.</p>')],
 [("How do I know if my car has frame damage?", "<p>Often you can’t tell by looking. Misaligned panels and handling changes are clues; an inspection is the only way to know.</p>"), FAQ_INS[3], FAQ_GENERAL[3]]),
"glass": ("Windshield and glass, handled with your repair.",
 "Cracked windshields and broken glass are common in collisions. We take care of replacement so your repair is finished in one place.",
 [("Glass replacement", "<p>Windshield, door and rear glass. Call with your vehicle’s year, make and model and we’ll tell you what’s involved.</p>"),
  ("Why calibration may follow", '<p>Many newer vehicles mount lane-keeping and emergency-braking cameras on the windshield. After replacement, that camera may need recalibration. <a href="diagnostics-calibration.html">More on calibration</a>.</p>'),
  ("Insurance", "<p>Glass damage may fall under comprehensive or collision coverage, depending on what happened. Check with your insurer and we’ll help with the paperwork.</p>")],
 [("Does my windshield camera need calibration?", "<p>If your vehicle has a forward-facing driver-assistance camera, usually yes. We’ll tell you what yours requires.</p>"), FAQ_INS[2], FAQ_GENERAL[2]]),
"diagnostics-calibration": ("Modern cars need more than bodywork.",
 "Sensors, cameras and computers can all be affected by a collision and the repair that follows.",
 [("Diagnostic scans", "<p>A scan reads the codes stored in your vehicle’s computers. Before the repair, it can reveal damage you can’t see; after, it confirms systems are working.</p>"),
  ("ADAS calibration", "<p>Automatic emergency braking, lane-keeping, adaptive cruise and blind-spot monitoring rely on cameras and radar in bumpers, grilles, mirrors and windshields. After a repair, they may need calibration to aim correctly.</p>"),
  ("What we’ll tell you up front", "<p>Requirements depend on your make, model and the repairs performed. We identify the scans and calibrations your vehicle needs and explain how they’ll be completed before work begins.</p>")],
 [("Why scan if no warning lights are on?", "<p>Some faults are stored without lighting the dashboard, and some vehicle makers require scans after any collision repair.</p>"), ("Is calibration covered by insurance?", "<p>When it’s required as part of a covered repair, it’s normally part of the estimate. We document the requirement for your insurer.</p>"), FAQ_GENERAL[1]]),
}

def service_page(slug):
    s = SVC[slug]; h1, lede, sections, faqs = SVC_COPY[slug]
    blocks = "".join(f'<section class="prose-sec"><h2>{e(t)}</h2>{c}</section>' for t, c in sections)
    crumbs = [("Services", "services"), (s["name"], slug)]
    body = f'''{page_hero(e(h1), e(lede), crumbs, PANEL if slug in ("auto-body-paint", "paintless-dent-repair") else BAY, eyebrow=e(s["name"]) + " · Palmyra, NY")}
<section class="band band--paper"><div class="wrap layout-aside">
  <article class="prose">{blocks}
  <section class="prose-sec"><h2>Common questions</h2>{faq_block(faqs)}</section>
  <section class="prose-sec"><h2>Related services</h2>{related(slug)}</section></article>
  {aside()}
</div></section>
{final_cta()}'''
    svc_ld = {"@context": "https://schema.org", "@type": "Service", "name": s["name"], "serviceType": s["name"], "provider": {"@id": DOMAIN + "/#business"}, "areaServed": {"@type": "City", "name": "Palmyra, NY"}, "description": s["desc"]}
    return page(slug, s["title"], s["desc"], body, crumbs=crumbs, extra_ld=[svc_ld, faq_ld(faqs)], active="services", preload=PANEL if slug in ("auto-body-paint", "paintless-dent-repair") else BAY)

# ---------------------------------------------------------------- OTHER PAGES
def about():
    o = C["ownerName"]
    owner = ""
    if o.get("show") and o.get("text"):
        owner = f'<section class="band band--mid"><div class="wrap statement"><span class="eyebrow">From the owner</span><p class="owner-quote">{e(C["ownerMessage"]["text"]) if C.get("ownerMessage", {}).get("show") else ""}</p><p>{e(o["text"])}</p></div></section>'
    body = f'''{page_hero("A family shop with decades of experience.", "JCH Auto Works is a family-owned and operated auto body repair business on Route 21 in Palmyra, New York.", [("About", "about")], EXT, "About JCH", cta=False)}
<section class="band band--paper"><div class="wrap split">
  <div class="stack-lg reveal"><span class="eyebrow">Our story</span><h2 class="h-md">New sign. Experienced hands.</h2>
  <p class="lede">JCH Auto Works is a recently established business built on more than 30 years of auto body expertise.</p>
  <p>Honest estimates, real communication with customers and insurers, and repairs we stand behind for as long as you own the vehicle. And you deal with family, not a call center.</p></div>
  {figure(EXT, "JCH Auto Works shop building and service doors on State Route 21", "photo--wide reveal", "(max-width:900px) 100vw, 50vw", "Our shop on Route 21")}
</div></section>
{owner}
<section class="band"><div class="wrap side-head">
  <div class="stack reveal"><span class="eyebrow">How we work</span><h2>What we stand for.</h2></div>
  <div class="diff reveal">
    <article><div class="ic">{icon("people")}</div><h3>People first</h3><p>We listen, then explain your options plainly.</p></article>
    <article><div class="ic">{icon("badge")}</div><h3>Trained</h3><p>An I-CAR certified technician on staff.</p></article>
    <article><div class="ic">{icon("doc")}</div><h3>Transparent</h3><p>Free estimates and transparent pricing.</p></article>
    <article><div class="ic">{icon("shield")}</div><h3>Accountable</h3><p>Lifetime workmanship warranty.</p></article>
    <article><div class="ic">{icon("clock")}</div><h3>In touch</h3><p>Repair updates while your vehicle is here.</p></article>
    <article><div class="ic">{icon("home")}</div><h3>Local</h3><p>On Route 21 in Palmyra.</p></article>
  </div></div></section>
<section class="band band--paper band--tight" id="careers"><div class="wrap split">
  <div class="stack"><span class="eyebrow">Careers</span><h2 class="h-sm">Good body work takes good people.</h2></div>
  <div class="stack"><p>Experienced in collision repair, refinishing or estimating? We’re always glad to hear from skilled people who take pride in their work.</p>{btn("Contact the shop", "contact.html", "btn--ghost")}</div>
</div></section>
{final_cta()}'''
    return page("about", "About Our Family Body Shop in Palmyra", "Meet JCH Auto Works, a family-owned auto body shop in Palmyra, NY with more than 30 years of auto body expertise and an I-CAR certified technician.", body, crumbs=[("About", "about")], active="about.html", preload=EXT)

def insurance():
    steps = "".join(f'<li><b>{e(a)}</b><span>{e(b)}</span></li>' for a, b in [
      ("At the scene", "Get safe, call 911 if needed, photograph everything, exchange information."),
      ("Report the claim", "Call your insurer (or the at-fault driver’s) and get a claim number."),
      ("Choose your shop", "Tell the insurer you’d like JCH Auto Works. In New York, the choice is yours."),
      ("Inspection & estimate", "We inspect the vehicle, write the estimate and work with your adjuster."),
      ("Repair & updates", "Hidden damage is documented and approved; you get updates along the way.")])
    body = f'''{page_hero("Insurance claims, explained.", "We work with all major insurance companies and guide you from the first call to the final paperwork.", [("Insurance Assistance", "insurance")], BAY, "Insurance assistance")}
<section class="band band--paper"><div class="wrap layout-aside">
  <div class="stack-lg"><div class="stack"><span class="eyebrow">How it works</span><h2 class="h-md">Your claim, step by step.</h2></div>
  <ol class="steps">{steps}</ol>
  <p class="notice">Coverage, deductibles, rental and towing benefits are set by your policy; your adjuster can confirm what’s covered. General information, not legal or insurance advice.</p>
  <h2 class="h-sm">Common questions</h2>{faq_block(FAQ_INS)}</div>
  {aside(["We work with all major insurers", "We communicate with your adjuster", "Hidden damage documented and approved", "Free estimate, no obligation"])}
</div></section>
{final_cta()}'''
    return page("insurance", "Insurance Claim Help, Palmyra NY", "How collision insurance claims work in New York and how JCH Auto Works helps: we work with all major insurers and communicate with your adjuster.", body, crumbs=[("Insurance Assistance", "insurance")], extra_ld=[faq_ld(FAQ_INS)], active="insurance.html", preload=BAY)

def our_work():
    pairs = S["gallery"]["pairs"]
    if pairs:
        ba = "".join(f'''<div class="stack reveal"><div class="ba"><img src="{p["before"]}" alt="{e(p["vehicle"])} before repair" loading="lazy"><img class="after" src="{p["after"]}" alt="{e(p["vehicle"])} after repair" loading="lazy"><input type="range" min="0" max="100" value="50" aria-label="Compare before and after"><span class="handle"></span><span class="tag l">Before</span><span class="tag r">After</span></div><div class="ba-meta"><span><b>{e(p["vehicle"])}</b></span><span>{e(p["repair"])}</span></div><p>{e(p.get("note", ""))}</p></div>''' for p in pairs)
        content = f'<section class="band"><div class="wrap stack-lg"><div class="stack"><span class="eyebrow">Before & after</span><h2 class="h-md">Recent repairs.</h2></div><div class="ba-grid">{ba}</div></div></section>'
    else:
        content = f'''<section class="band band--paper"><div class="wrap">
  <div class="portfolio">
    <div class="stack-lg"><span class="eyebrow">Repair portfolio</span><h2 class="h-md">Coming soon.</h2>
    <p class="lede">We’re documenting completed repairs, with our customers’ permission, to share here.</p>
    <div class="btn-row">{btn("Get directions", B["mapsUrl"], "", "pin", "our-work")}{btn("Request an estimate", "estimate.html", "btn--ghost")}</div></div>
    <ul class="port-list">
      <li>{icon("camera")}<span><b>Before & after</b>Side-by-side comparisons from the same angle</span></li>
      <li>{icon("car")}<span><b>The vehicle</b>Make, model and the type of damage</span></li>
      <li>{icon("doc")}<span><b>The repair</b>What we did, in plain language</span></li>
    </ul>
  </div></div></section>'''
    body = f'''{page_hero("Our work.", "Completed JCH repairs, shown with our customers’ permission.", [("Our Work", "our-work")], EXT, "Repair portfolio")}
{content}
{final_cta()}'''
    return page("our-work", "Our Work & Repair Portfolio", "Completed collision repairs from JCH Auto Works in Palmyra, NY, shared with customers’ permission. Before-and-after projects are being added.", body, crumbs=[("Our Work", "our-work")], active="our-work.html", preload=EXT)

def reviews():
    items = S["reviews"]["items"]
    if items:
        inner = '<div class="quotes">' + "".join(f'<figure class="quote"><blockquote>“{e(r["text"])}”</blockquote><figcaption>{e(r["name"])} · {e(r.get("source", ""))} · {e(r.get("date", ""))}</figcaption></figure>' for r in items) + "</div>"
    else:
        g = S["reviews"]["googleReviewUrl"]
        gbtn = btn("Review us on Google", g, "", None, "reviews") if g else ""
        inner = f'''<div class="empty"><h2 class="h-sm">Your experience helps a neighbor.</h2>
<p class="lede">If we repaired your vehicle, we’d be grateful if you’d share how it went. Honest reviews help us improve and help other drivers choose with confidence.</p>
<div class="btn-row">{gbtn}{btn("Share on Facebook", B["facebook"], "btn--ghost", None, "reviews")}</div></div>'''
    body = f'''{page_hero("What customers say.", "Real feedback from real customers, shared with their permission.", [("Reviews", "reviews")], BAY, "Reviews", cta=False)}
<section class="band band--paper"><div class="wrap">{inner}</div></section>
{final_cta()}'''
    return page("reviews", "Customer Reviews", "Customer reviews of JCH Auto Works, a family-owned collision repair shop in Palmyra, NY. Share your experience to help other drivers.", body, crumbs=[("Reviews", "reviews")], preload=BAY)

def faq():
    body = f'''{page_hero("Questions, answered.", "Estimates, insurance, timing, warranty and what to do after an accident.", [("FAQ", "faq")], BAY, "FAQ", cta=False)}
<section class="band band--paper"><div class="wrap layout-aside">
  <div class="stack-lg"><h2 class="h-sm">About the shop</h2>{faq_block(FAQ_GENERAL)}<h2 class="h-sm">After an accident & insurance</h2>{faq_block(FAQ_INS)}</div>
  {aside()}
</div></section>
{final_cta()}'''
    return page("faq", "Collision Repair FAQ", "Answers to common collision repair questions: free estimates, New York insurance claims, repair time, cost, warranty and what to do after an accident.", body, crumbs=[("FAQ", "faq")], extra_ld=[faq_ld(FAQ_GENERAL + FAQ_INS)], active="faq.html", preload=BAY)

# ---------------------------------------------------------------- FORMS
def choice(name, value, label, kind="radio", req=None):
    r = ' data-req="group"' if req else ""
    return f'<label class="choice"><input type="{kind}" name="{name}" value="{e(value)}"{r}><span>{e(label)}</span></label>'

def result_block(title, body_txt):
    return f'''<div class="result" data-result hidden tabindex="-1" aria-live="polite">
<span class="eyebrow" data-result-eyebrow>Inquiry received</span><h2 data-result-title>{title}</h2><p data-result-body>{body_txt}</p>
<pre data-result-detail hidden></pre>
<p class="ref"></p><div class="btn-row">{btn("Call " + B["phone"], TEL, "", "phone", "form-result")}{btn("Back to home", "index.html", "btn--ghost")}</div></div>'''

def estimate():
    years = "".join(f'<option>{y}</option>' for y in range(datetime.date.today().year + 1, 1979, -1))
    makes = ["Acura","Audi","BMW","Buick","Cadillac","Chevrolet","Chrysler","Dodge","Ford","Genesis","GMC","Honda","Hyundai","Infiniti","Jeep","Kia","Lexus","Lincoln","Mazda","Mercedes-Benz","Mitsubishi","Nissan","Ram","Subaru","Tesla","Toyota","Volkswagen","Volvo","Other"]
    mk = "".join(f"<option>{m}</option>" for m in makes)
    dmg = "".join(choice("damage_type", v, v, "checkbox", req=(i == 0)) for i, v in enumerate(["Front", "Rear", "Driver side", "Passenger side", "Roof / hood", "Dent or ding", "Scratches / paint", "Glass", "Warning lights on", "Not sure"]))
    photo_inputs = "".join(f'<input type="file" name="photo{i}" hidden tabindex="-1" aria-hidden="true">' for i in range(1, 7))
    form = f'''<div class="form-shell" id="estimate-form">
<ol class="form-progress" aria-label="Progress"><li>1 · Vehicle</li><li>2 · Damage</li><li>3 · Insurance</li><li>4 · You</li></ol>
<form name="estimate" method="POST" action="/" data-netlify="true" netlify-honeypot="bot-field" enctype="multipart/form-data" data-jch-form novalidate>
<input type="hidden" name="form-name" value="estimate"><input type="hidden" name="reference" value="">
<p class="hp"><label>Leave this empty <input name="bot-field" tabindex="-1" autocomplete="off"></label></p>
{photo_inputs}
<div class="form-body">
  <fieldset data-step><legend>Your vehicle</legend>
    <div class="row-3">
      <div class="field"><label for="year">Year</label><select id="year" name="vehicle_year" data-req data-msg="Choose the model year."><option value="">Year</option>{years}</select></div>
      <div class="field"><label for="make">Make</label><select id="make" name="vehicle_make" data-req data-msg="Choose the make."><option value="">Make</option>{mk}</select></div>
      <div class="field"><label for="model">Model</label><input id="model" name="vehicle_model" type="text" autocomplete="off" placeholder="e.g. Grand Cherokee" data-req data-msg="Enter the model."></div>
    </div>
    <div class="field"><label for="vin">VIN <span class="opt">(optional)</span></label><input id="vin" name="vin" type="text" maxlength="17" autocapitalize="characters" spellcheck="false" placeholder="17 characters" class="mono"><span class="hint">On the driver-side dashboard by the windshield, the door jamb, or your insurance card.</span></div>
    <div class="field"><span class="label" id="drv">Is the vehicle drivable?</span><div class="choices" role="radiogroup" aria-labelledby="drv">{choice("drivable","Yes","Yes",req=True)}{choice("drivable","No","No")}{choice("drivable","Not sure","Not sure")}</div></div>
    <div data-show-if="drivable=No" class="notice">After you send this, call us at <a href="{TEL}">{B["phone"]}</a> and we’ll talk through getting the vehicle here. Many insurance policies include towing.</div>
  </fieldset>
  <fieldset data-step hidden><legend>The damage</legend>
    <div class="field"><span class="label" id="dmg">Where is the damage? <span class="opt">Pick all that apply</span></span><div class="choices" role="group" aria-labelledby="dmg">{dmg}</div></div>
    <div class="field"><label for="desc">What happened?</label><textarea id="desc" name="description" maxlength="1500" placeholder="A few words is fine, e.g. “Backed into a pole, rear bumper cracked.”" data-req data-msg="Tell us briefly what happened."></textarea></div>
    <div class="field"><span class="label">Photos <span class="opt">(optional, up to 6)</span></span>
      <div class="drop" role="button" tabindex="0" aria-describedby="photo-hint">{icon("upload")}<b>Add photos</b><span id="photo-hint" class="hint">Take or choose photos, or drag them here. A wide shot of each damaged side plus close-ups.</span></div>
      <input id="photo-picker" name="photo-picker" type="file" accept="image/*" multiple hidden>
      <p class="hint" data-photo-status aria-live="polite"></p><div class="thumbs"></div></div>
  </fieldset>
  <fieldset data-step hidden><legend>Insurance &amp; timing</legend>
    <div class="field"><span class="label" id="ins">Is insurance involved?</span><div class="choices" role="radiogroup" aria-labelledby="ins">{choice("insurance","Yes, my insurance","Yes, my insurance",req=True)}{choice("insurance","Yes, the other driver's","Yes, the other driver’s")}{choice("insurance","No, paying myself","No, I’ll pay myself")}{choice("insurance","Not sure yet","Not sure yet")}</div></div>
    <div data-show-if="insurance=Yes, my insurance|Yes, the other driver's" class="stack">
      <div class="row"><div class="field"><label for="carrier">Insurance company <span class="opt">(optional)</span></label><input id="carrier" name="insurance_company" type="text" placeholder="e.g. Progressive"></div>
      <div class="field"><span class="label" id="clm">Claim filed?</span><div class="choices" role="radiogroup" aria-labelledby="clm">{choice("claim_filed","Yes","Yes")}{choice("claim_filed","Not yet","Not yet")}</div></div></div>
      <p class="hint">No policy or claim numbers needed here. We’ll ask when we talk.</p></div>
    <div class="field narrow"><label for="date">Preferred drop-off day <span class="opt">(optional)</span></label><input id="date" name="preferred_date" type="date"><span class="hint">Mon–Fri. We’ll confirm a time.</span></div>
  </fieldset>
  <fieldset data-step hidden><legend>How to reach you</legend>
    <div class="field"><label for="name">Your name</label><input id="name" name="name" type="text" autocomplete="name" data-req data-msg="Enter your name."></div>
    <div class="row"><div class="field"><label for="phone">Phone</label><input id="phone" name="phone" type="tel" autocomplete="tel" inputmode="tel" placeholder="(315) 555-0142" data-req="phone"></div>
    <div class="field"><label for="email">Email</label><input id="email" name="email" type="email" autocomplete="email" placeholder="you@example.com" data-req="email"></div></div>
    <div class="field"><span class="label" id="pref">Best way to reach you</span><div class="choices" role="radiogroup" aria-labelledby="pref">{choice("contact_method","Call","Call",req=True)}{choice("contact_method","Text","Text")}{choice("contact_method","Email","Email")}</div></div>
    <p class="notice">This requests a preliminary estimate, not a final price. The final estimate is written after we inspect the vehicle in person.</p>
    <label class="consent field"><input type="checkbox" name="consent" value="yes" data-req="check" data-msg="Please agree so we can contact you about your estimate."><span>JCH Auto Works may contact me by phone, text or email about this estimate. <a href="privacy.html">Privacy</a></span></label>
    <div class="bar" hidden><i></i></div>
    <p class="err" data-send-error hidden tabindex="-1" role="alert"></p>
  </fieldset>
  <div class="form-nav"><button type="button" class="btn btn--ghost" data-prev>Back</button><button type="button" class="btn" data-next>Continue</button><button type="submit" class="btn" data-submit data-label="Send estimate request" hidden>Send estimate request</button></div>
</div></form>
{result_block("Thanks. We’ve got it.", "We’ll review your details and photos and reply during business hours, Mon–Fri 8 AM – 5 PM. Need us sooner? Call.")}
</div>'''
    body = f'''{page_hero("Request a free estimate.", "Four short steps. Add photos if you have them.", [("Request an Estimate", "estimate")], None, "Free · No obligation", cta=False)}
<section class="band band--paper band--form"><div class="wrap layout-aside">
  {form}
  <aside class="aside-card"><span class="eyebrow">What happens next</span><h2 class="aside-h">After you send this</h2>
  <ul class="check"><li>We review your details and photos.</li><li>We contact you to set up an in-person inspection.</li><li>You get a free written estimate.</li><li>If insurance is involved, we work with your adjuster.</li></ul>
  <p class="small">Prefer to talk? <a href="{TEL}" data-track="estimate-aside">{B["phone"]}</a></p></aside>
</div></section>'''
    return page("estimate", "Free Collision Repair Estimate, Palmyra NY", "Request a free, no-obligation collision repair estimate from JCH Auto Works in Palmyra, NY. Add damage photos and vehicle details in four short steps.", body, crumbs=[("Request an Estimate", "estimate")])

def fleet():
    needs = "".join(choice("service_needs", v, v, "checkbox", req=(i == 0)) for i, v in enumerate(["Collision repair", "Paint & refinishing", "Dent repair", "Glass", "Diagnostics & calibration", "Other"]))
    form = f'''<div class="form-shell" id="fleet-form">
<form name="fleet" method="POST" action="/" data-netlify="true" netlify-honeypot="bot-field" data-jch-form novalidate>
<input type="hidden" name="form-name" value="fleet"><input type="hidden" name="reference" value="">
<p class="hp"><label>Leave this empty <input name="bot-field" tabindex="-1" autocomplete="off"></label></p>
<div class="form-body"><fieldset><legend>Business inquiry</legend>
  <div class="row"><div class="field"><label for="f-org">Organization</label><input id="f-org" name="organization" type="text" autocomplete="organization" data-req data-msg="Enter your organization’s name."></div>
  <div class="field"><label for="f-type">Type</label><select id="f-type" name="org_type" data-req data-msg="Choose one."><option value="">Choose</option><option>Fleet operator</option><option>Local business</option><option>Dealership</option><option>Insurance professional</option><option>Other</option></select></div></div>
  <div class="row"><div class="field"><label for="f-name">Your name</label><input id="f-name" name="name" type="text" autocomplete="name" data-req data-msg="Enter your name."></div>
  <div class="field"><label for="f-role">Role <span class="opt">(optional)</span></label><input id="f-role" name="role" type="text" autocomplete="organization-title" placeholder="e.g. Fleet manager"></div></div>
  <div class="row"><div class="field"><label for="f-phone">Phone</label><input id="f-phone" name="phone" type="tel" autocomplete="tel" data-req="phone"></div>
  <div class="field"><label for="f-email">Email</label><input id="f-email" name="email" type="email" autocomplete="email" data-req="email"></div></div>
  <div class="field narrow"><label for="f-size">Number of vehicles <span class="opt">(approx.)</span></label><select id="f-size" name="fleet_size"><option value="">Choose</option><option>1–5</option><option>6–20</option><option>21–50</option><option>50+</option><option>Not applicable</option></select></div>
  <div class="field"><span class="label" id="f-needs">What do you need help with?</span><div class="choices" role="group" aria-labelledby="f-needs">{needs}</div></div>
  <div class="field"><label for="f-msg">Anything else? <span class="opt">(optional)</span></label><textarea id="f-msg" name="message" maxlength="2000" placeholder="Vehicle types, how repairs are handled today, what matters most."></textarea></div>
  <div class="field"><span class="label" id="f-fu">Preferred follow-up</span><div class="choices" role="radiogroup" aria-labelledby="f-fu">{choice("follow_up","Phone call","Phone call",req=True)}{choice("follow_up","Email","Email")}{choice("follow_up","Visit the shop","Visit the shop")}</div></div>
  <label class="consent field"><input type="checkbox" name="consent" value="yes" data-req="check" data-msg="Please agree so we can follow up."><span>JCH Auto Works may contact me about this inquiry. <a href="privacy.html">Privacy</a></span></label>
  <div class="bar" hidden><i></i></div><p class="err" data-send-error hidden tabindex="-1" role="alert"></p>
</fieldset>
<div class="form-nav"><span></span><button type="submit" class="btn" data-submit data-label="Send inquiry">Send inquiry</button></div></div></form>
{result_block("Thanks. We’ll be in touch.", "We’ll follow up the way you asked, during business hours.")}
</div>'''
    body = f'''{page_hero("Fleet & business collision repair.", "For fleets, local businesses, dealerships and insurance professionals near Palmyra.", [("Fleet & Business", "fleet")], EXT, "Commercial", cta=False)}
<section class="band"><div class="wrap split">
  <div class="stack-lg reveal"><span class="eyebrow">Why it matters</span><h2 class="h-md">Downtime costs you.</h2>
  <p class="lede">One experienced local shop you trust makes every repair simpler.</p></div>
  <ul class="check check--dark reveal"><li>One local point of contact</li><li>Free estimates and clear repair plans</li><li>Insurance coordination when a claim is involved</li><li>Repair updates while vehicles are here</li><li>Lifetime workmanship warranty</li></ul>
</div></section>
<section class="band band--paper band--form"><div class="wrap layout-aside">{form}
  <aside class="aside-card"><span class="eyebrow">Prefer to talk?</span><h2 class="aside-h">Call the shop</h2><p>We’re happy to talk through how we can support your vehicles.</p>{btn("Call " + B["phone"], TEL, "btn--ghost", "phone", "fleet-aside")}</aside>
</div></section>'''
    return page("fleet", "Fleet & Commercial Collision Repair", "Collision repair for fleets, local businesses, dealerships and insurance professionals near Palmyra, NY. Start a business inquiry with JCH Auto Works.", body, crumbs=[("Fleet & Business", "fleet")], active="fleet.html", preload=EXT)

def contact():
    hours = "".join(f'<li><b>{h["days"]}</b><span>{"Closed" if h.get("closed") else h["open"] + " – " + h["close"]}</span></li>' for h in B["hours"])
    area = ", ".join(S["serviceArea"]["nearby"])
    form = f'''<div class="form-shell"><form name="contact" method="POST" action="/" data-netlify="true" netlify-honeypot="bot-field" data-jch-form novalidate>
<input type="hidden" name="form-name" value="contact"><input type="hidden" name="reference" value="">
<p class="hp"><label>Leave this empty <input name="bot-field" tabindex="-1" autocomplete="off"></label></p>
<div class="form-body"><fieldset><legend>Send a message</legend>
  <div class="field"><label for="c-name">Name</label><input id="c-name" name="name" type="text" autocomplete="name" data-req data-msg="Enter your name."></div>
  <div class="row"><div class="field"><label for="c-phone">Phone</label><input id="c-phone" name="phone" type="tel" autocomplete="tel" data-req="phone"></div>
  <div class="field"><label for="c-email">Email</label><input id="c-email" name="email" type="email" autocomplete="email" data-req="email"></div></div>
  <div class="field"><label for="c-msg">Message</label><textarea id="c-msg" name="message" maxlength="2000" data-req data-msg="Enter a message."></textarea></div>
  <label class="consent field"><input type="checkbox" name="consent" value="yes" data-req="check" data-msg="Please agree so we can reply."><span>JCH Auto Works may contact me to reply. <a href="privacy.html">Privacy</a></span></label>
  <div class="bar" hidden><i></i></div><p class="err" data-send-error hidden tabindex="-1" role="alert"></p>
</fieldset><div class="form-nav"><span></span><button class="btn" type="submit" data-submit data-label="Send message">Send message</button></div></div></form>
{result_block("Message received.", "We’ll reply during business hours. For anything urgent, please call.")}</div>'''
    body = f'''{page_hero("Contact & directions.", "Call, email, send a message, or stop by during business hours.", [("Contact", "contact")], EXT, "Visit the shop", cta=False)}
<section class="band band--paper band--form"><div class="wrap layout-aside">
  {form}
  <aside class="aside-card"><span class="eyebrow">JCH Auto Works LLC</span><h2 class="aside-h">Visit us</h2>
    <p><strong>{e(B["street"])}</strong><br>{e(B["city"])}, {B["region"]} {B["postal"]}<br><span class="small">Mailing: {e(B["poBox"])}, {e(B["city"])}, {B["region"]} {B["postal"]}</span></p>
    {btn("Get directions", B["mapsUrl"], "", "pin", "contact")}
    <p><a href="{TEL}" data-track="contact"><strong>{B["phone"]}</strong></a><br><a href="mailto:{B["email"]}" data-track="contact">{B["email"]}</a></p>
    <ul class="hours">{hours}</ul>
    <p class="small">Customers often come to us from {e(area)}.</p>
  </aside>
</div></section>
<section class="band band--tight"><div class="wrap split">
  {figure(EXT, "JCH Auto Works building with 904 on the front, State Route 21, Palmyra NY", "photo--wide", "(max-width:900px) 100vw, 50vw", "Look for 904 on the building")}
  <div class="stack"><span class="eyebrow">Getting here</span><h2 class="h-sm">On Route 21 in Palmyra.</h2><p>Look for the gray building with “904” on the front, with parking right outside.</p>{btn("Get directions", B["mapsUrl"], "btn--ghost", "pin", "contact-photo")}</div>
</div></section>'''
    return page("contact", "Contact & Directions, Palmyra NY", f"Call JCH Auto Works at {B['phone']} or visit {ADDR_LINE}. Open Monday to Friday, 8 AM to 5 PM.", body, crumbs=[("Contact", "contact")], active="contact.html", preload=EXT)

def privacy():
    body = f'''{page_hero("Privacy.", "How we handle the information you send through this website.", [("Privacy", "privacy")], None, "Policy", cta=False)}
<section class="band band--paper"><div class="wrap prose narrow-prose">
<section class="prose-sec"><h2>What we collect</h2><p>What you enter in our forms: name, phone, email, vehicle details, a description of the damage, any photos you upload and, if you choose, your insurer’s name. We don’t ask for policy numbers, Social Security numbers or payment details here.</p></section>
<section class="prose-sec"><h2>How we use it</h2><p>Only to respond to your request, prepare your estimate and communicate about your repair. We don’t sell your information or share it with marketers.</p></section>
<section class="prose-sec"><h2>Where it’s stored</h2><p>Submissions are delivered to the shop’s email and stored with our website host’s form service. Inquiries that don’t become repairs are deleted after 12 months. Ask us to delete your information anytime at {e(B["email"])}.</p></section>
<section class="prose-sec"><h2>Analytics</h2><p>If analytics are enabled, we ask for consent first and use them only to see which pages are useful.</p></section>
<section class="prose-sec"><h2>Contact</h2><p>{e(B["name"])}, {e(ADDR_LINE)} · {B["phone"]} · {e(B["email"])}</p><p class="small">Last updated {datetime.date.today().strftime("%B %Y")}.</p></section>
</div></section>'''
    return page("privacy", "Privacy Policy", "How JCH Auto Works handles information submitted through its website forms.", body, crumbs=[("Privacy", "privacy")])

def notfound():
    body = f'''<section class="band"><div class="wrap stack-lg"><span class="eyebrow">404</span><h1 class="h-lg">This page took a detour.</h1><p class="lede">The page you’re looking for isn’t here.</p>
<div class="btn-row">{btn("Home", "index.html")}{btn("Request an estimate", "estimate.html", "btn--ghost")}</div></div></section>'''
    return page("404", "Page Not Found", "Page not found.", body)

# ---------------------------------------------------------------- write
def build():
    if DIST.exists(): shutil.rmtree(DIST)
    (DIST / "assets").mkdir(parents=True)
    shutil.copytree(SRC / "img", DIST / "img")
    for f in ("style.css", "app.js"): shutil.copy(SRC / "assets" / f, DIST / "assets" / f)
    pages = {"index": home(), "services": services_hub(), "about": about(), "insurance": insurance(), "our-work": our_work(), "reviews": reviews(),
             "estimate": estimate(), "fleet": fleet(), "faq": faq(), "contact": contact(), "privacy": privacy(), "404": notfound()}
    for s in SERVICES: pages[s["slug"]] = service_page(s["slug"])
    for k, v in pages.items(): (DIST / f"{k}.html").write_text(v)
    urls = [k for k in pages if k != "404"]
    (DIST / "sitemap.xml").write_text('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' +
        "".join(f'  <url><loc>{DOMAIN}/{"" if u == "index" else u}</loc><lastmod>{TODAY}</lastmod></url>\n' for u in urls) + "</urlset>\n")
    (DIST / "robots.txt").write_text(f"User-agent: *\nAllow: /\nSitemap: {DOMAIN}/sitemap.xml\n")
    (DIST / "_redirects").write_text("# Old URLs from the previous site\n/ccc-body-shop-careers  /about#careers  301\n/repair-authorization  /contact  301\n/home  /  301\n")
    print(f"Built {len(pages)} pages -> {DIST}")

if __name__ == "__main__":
    build()
