#!/usr/bin/env python3
"""Static site generator for Jack Albert Weddings.

Wraps every page in src/pages/ and every article in src/posts/ in the shared
layout (head, header, menu, footer, film modal) and writes plain HTML to site/.

    python3 build.py

Page files start with a front-matter block:

    ---
    title: Page title for the browser tab
    description: Meta description
    nav: films            (which nav item is current)
    hero: dark            (header starts transparent over a full-bleed hero)
    ---

Inside pages and articles, {{name}} expands to a snippet from SNIPPETS below,
and {{posts:N}} / {{posts:all}} renders journal cards.
"""
import html
import json
import re
from datetime import date
from pathlib import Path

ROOT = Path(__file__).parent
SRC = ROOT / "src"
OUT = ROOT / "site"
DOMAIN = "https://www.jackalbertweddings.ca"

BRAND = {
    "phone": "(613) 621-0458",
    "tel": "+16136210458",
    "email": "jack@jackalbertweddings.ca",
    "instagram": "https://www.instagram.com/jackalbertweddings/",
    "youtube": "https://www.youtube.com/@JackAlbertWeddings",
    "calendly": "https://calendly.com/jackalbertweddings/weddingcall",
    "google": "https://www.google.com/search?q=jack+albert+weddings#mpd=~17473429669530516849/customers/reviews",
    "formspree": "https://formspree.io/f/xaqgvyod",
    "pixel": "2142663756311688",
}

NAV = [
    ("films", "films.html", "Films"),
    ("experience", "experience.html", "Experience"),
    ("investment", "investment.html", "Investment"),
    ("about", "about.html", "About"),
    ("journal", "journal.html", "Journal"),
]

# ---------------------------------------------------------------- icons
ARROW = '<svg class="arrow" viewBox="0 0 18 10" fill="none" stroke="currentColor" stroke-width="1.1" aria-hidden="true"><path d="M0 5h17M13 1l4 4-4 4"/></svg>'
PLAY = '<svg viewBox="0 0 18 18" fill="currentColor" aria-hidden="true"><path d="M3 1.5v15L16 9z"/></svg>'
STAR = '<svg class="marquee__star" viewBox="0 0 20 20" fill="currentColor" aria-hidden="true"><path d="M10 0c.6 5.6 4.4 9.4 10 10-5.6.6-9.4 4.4-10 10-.6-5.6-4.4-9.4-10-10C5.6 9.4 9.4 5.6 10 0z"/></svg>'
IG = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.4" aria-hidden="true"><rect x="3" y="3" width="18" height="18" rx="5"/><circle cx="12" cy="12" r="4.2"/><circle cx="17.4" cy="6.6" r=".9" fill="currentColor" stroke="none"/></svg>'
YT = '<svg viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M23 7.2a3 3 0 0 0-2.1-2.1C19 4.6 12 4.6 12 4.6s-7 0-8.9.5A3 3 0 0 0 1 7.2 31 31 0 0 0 .5 12a31 31 0 0 0 .5 4.8 3 3 0 0 0 2.1 2.1c1.9.5 8.9.5 8.9.5s7 0 8.9-.5a3 3 0 0 0 2.1-2.1c.4-1.6.5-4.8.5-4.8s0-3.2-.5-4.8zM9.7 15V9l5.8 3-5.8 3z"/></svg>'
PHONE = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.4" aria-hidden="true"><path d="M5 3h4l2 5-2.5 1.5a11 11 0 0 0 6 6L16 13l5 2v4a2 2 0 0 1-2 2A17 17 0 0 1 3 5a2 2 0 0 1 2-2z"/></svg>'
MAIL = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.4" aria-hidden="true"><rect x="3" y="5" width="18" height="14" rx="1"/><path d="M3 6l9 7 9-7"/></svg>'
CLOSE = '<svg viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.2" aria-hidden="true"><path d="M1 1l14 14M15 1L1 15"/></svg>'

# ---------------------------------------------------------------- films
FILMS = {
    "shelby-bobby": dict(couple="Shelby &amp; Bobby", place="A Lakeside Wedding · Chapeau", yt="GLoy1N3UaAU",
                         img="preview-shelby-bobby.jpg", video="preview-shelby-bobby.mp4"),
    "bree-skyler": dict(couple="Bree &amp; Skyler", place="An Autumn Wedding · Golden Lake", yt="Lep5cu_MWEo",
                        img="preview-bree-skyler.jpg", video="preview-bree-skyler.mp4"),
    "lyndon-paige": dict(couple="Lyndon &amp; Paige", place="The Farmstead · Pembroke", yt="O0WLQU6qA5U",
                         img="preview-lyndon-paige.jpg", video="preview-lyndon-paige.mp4"),
    "shaughn-vanessa": dict(couple="Shaughn &amp; Vanessa", place="Toronto · Ontario", yt="KNO_ScRbNDs",
                            img="preview-shaughn-vanessa.jpg", video="preview-shaughn-vanessa.mp4"),
}


def film_tile(key, cls="", autoplay=False, img=None):
    f = FILMS[key]
    title = re.sub(r"&amp;", "&", f["couple"])
    poster = img or f["img"]
    if autoplay:
        vid = f'<video muted loop playsinline preload="none" data-loop data-src="assets/video/{f["video"]}" poster="assets/img/{poster}"></video>'
        attrs = ' film--autoplay'
        preview = ""
    else:
        vid = '<video muted loop playsinline preload="none"></video>'
        attrs = ""
        preview = f' data-preview="assets/video/{f["video"]}"'
    return f'''<a href="https://www.youtube.com/watch?v={f["yt"]}" class="film{attrs} {cls}" data-yt="{f["yt"]}" data-title="{title} — {re.sub("&amp;", "&", f["place"])}"{preview} aria-label="Play the {title} wedding film">
  <div class="film__media">
    <img src="assets/img/{poster}" alt="Still from {title}'s wedding film" loading="lazy" decoding="async">
    {vid}
    <span class="film__play">{PLAY}</span>
  </div>
  <div class="film__label">
    <div><div class="film__title">{f["couple"]}</div><div class="film__place">{f["place"]}</div></div>
    <span class="film__time">Watch film</span>
  </div>
</a>'''


REVIEWS = [
    ("He captured our day perfectly and somehow fit so many of the emotions, little moments, and memories from our wedding into one beautiful video. Every time we watch it, it feels like we get to relive the day all over again.", "Shelby &amp; Bobby"),
    ("Jack captured our whole day with so much care and talent. Watching the footage feels like reliving it, and the highlight film blew us away. 10/10 recommend.", "Theresa"),
    ("Jack was amazing to work with. He captured our favourite moments from the Wilno Church to our reception, and we couldn’t be happier. Highly recommend!", "Madison"),
    ("Jack was pleasant, professional, and knew exactly how to make our wedding video feel special. We got it back within weeks! 100% recommend.", "Ramona"),
]


def reviews_block():
    items = "\n".join(
        f'<figure class="review{" is-active" if i == 0 else ""}"><div class="stars" aria-label="Five stars">★★★★★</div>'
        f'<blockquote><p>“{q}”</p></blockquote><figcaption class="caps muted">{who} · Google Review</figcaption></figure>'
        for i, (q, who) in enumerate(REVIEWS))
    return f'''<div class="reviews" data-reviews>
  <div class="reviews__track" aria-live="polite">{items}</div>
  <div class="reviews__nav">
    <button class="reviews__arrow reviews__arrow--prev" type="button" aria-label="Previous review">{ARROW}</button>
    <div class="reviews__dots"></div>
    <button class="reviews__arrow reviews__arrow--next" type="button" aria-label="Next review">{ARROW}</button>
  </div>
</div>'''


def marquee(words):
    one = "".join(f'<span class="marquee__item">{w}{STAR}</span>' for w in words)
    return f'<div class="marquee" aria-hidden="true"><div class="marquee__track">{one}{one}</div></div>'


IG_IMAGES = ["reel-poster.jpg", "pembroke-kiss.jpg", "skyline-dance.jpg", "bree-portrait.jpg", "cake-detail.jpg", "champagne.jpg"]


def ig_band():
    tiles = "".join(f'<a href="{BRAND["instagram"]}" target="_blank" rel="noopener" aria-label="Jack Albert Weddings on Instagram"><img src="assets/img/{i}" alt="" loading="lazy" decoding="async"></a>' for i in IG_IMAGES)
    return f'''<section class="section section--tight" aria-labelledby="ig-title">
  <div class="container">
    <div class="section-head" style="margin-bottom:clamp(32px,4vw,56px)">
      <div class="reveal"><p class="eyebrow">On Instagram</p><h2 id="ig-title" class="display-md">Follow along <em class="accent">@jackalbertweddings</em></h2></div>
      <div class="reveal" data-delay="1"><p class="body-lg">Behind the scenes, new films and little moments from weddings across the Valley.</p><a class="link-line" href="{BRAND["instagram"]}" target="_blank" rel="noopener">Visit Instagram {ARROW}</a></div>
    </div>
  </div>
  <div class="ig-grid reveal">{tiles}</div>
</section>'''


def cta_band(title="Let’s capture <em>yours.</em>", text="Tell me your date and venue and I’ll let you know if I’m free, usually within 24 hours.", img="band-flowers.jpg", video="band-flowers.mp4"):
    return f'''<section class="cta-band" aria-labelledby="cta-title">
  <div class="cta-band__bg"><video muted loop playsinline preload="none" data-loop data-src="assets/video/{video}" poster="assets/img/{img}"></video></div>
  <div class="container">
    <p class="eyebrow reveal">Your day, on film</p>
    <h2 id="cta-title" class="display-lg reveal" data-delay="1" style="margin-bottom:28px">{title}</h2>
    <p class="reveal" data-delay="2">{text}</p>
    <div class="cta-band__actions reveal" data-delay="3">
      <a class="btn btn--light" href="contact.html">Check your date {ARROW}</a>
      <a class="btn btn--ghost-light" href="{BRAND["calendly"]}" target="_blank" rel="noopener">Book a quick call</a>
    </div>
  </div>
</section>'''


SNIPPETS = {
    "arrow": ARROW, "play": PLAY, "star": STAR, "ig": IG, "yt": YT,
    "phone": BRAND["phone"], "tel": BRAND["tel"], "email": BRAND["email"],
    "instagram": BRAND["instagram"], "youtube": BRAND["youtube"], "calendly": BRAND["calendly"],
    "google": BRAND["google"], "formspree": BRAND["formspree"],
    "reviews": reviews_block(),
    "ig_band": ig_band(),
    "cta_band": cta_band(),
    "marquee_places": marquee(["Ottawa Valley", "Golden Lake", "Pembroke", "Ottawa", "Kingston", "Petawawa", "Renfrew", "Arnprior", "Chapeau"]),
    "marquee_moments": marquee(["The vows", "The first look", "The speeches", "The last dance", "The quiet moments"]),
}
for k in FILMS:
    SNIPPETS["film:" + k] = film_tile(k)
    SNIPPETS["filmauto:" + k] = film_tile(k, autoplay=True)

# ---------------------------------------------------------------- journal
POST_IMAGES = {
    "wedding-videography-cost-ottawa-valley": "champagne.jpg",
    "is-a-wedding-video-worth-it": "bree-skyler-laugh.jpg",
    "do-you-need-videographer-and-photographer": "aisle-father.jpg",
    "questions-to-ask-wedding-videographer": "about-jack.jpg",
    "when-to-book-wedding-videographer": "preview-bree-skyler.jpg",
    "wedding-video-styles-explained": "s8-fs.jpg",
    "highlight-film-vs-full-film-raw-footage": "reel-poster.jpg",
    "how-long-to-get-wedding-video": "bride-window.jpg",
    "wedding-video-music-licensing": "skyline-dance.jpg",
    "wedding-day-timeline-for-video": "band-flowers.jpg",
    "best-wedding-venues-ottawa-valley": "pembroke-venue.jpg",
    "barn-and-farm-wedding-videography": "preview-lyndon-paige.jpg",
    "backyard-country-wedding-videography": "pembroke-aisle.jpg",
    "outdoor-wedding-rain-plan": "preview-shelby-bobby.jpg",
    "elopement-small-wedding-videography-ottawa-valley": "bree-portrait.jpg",
}
POST_ORDER = list(POST_IMAGES)


def load_posts():
    posts = {}
    for p in sorted((SRC / "posts").glob("*.json")):
        d = json.loads(p.read_text())
        d["img"] = POST_IMAGES.get(d["slug"], "hero-poster.jpg")
        d["cat"] = re.sub(r"[^a-z]+", "-", d["eyebrow"].lower()).strip("-")
        posts[d["slug"]] = d
    return [posts[s] for s in POST_ORDER if s in posts] + [p for s, p in posts.items() if s not in POST_ORDER]


def post_card(p, lead=False):
    excerpt = html.escape(p["description"])
    cls = "post-card post-card--lead" if lead else "post-card"
    title_tag = "h2" if lead else "h3"
    return f'''<article class="{cls} reveal" data-cat="{p["cat"]}">
  <a href="{p["slug"]}.html" class="frame-img post-card__img" tabindex="-1" aria-hidden="true"><img src="assets/img/{p["img"]}" alt="" loading="lazy" decoding="async"></a>
  <div>
    <div class="post-card__meta"><span>{html.escape(p["eyebrow"])}</span></div>
    <{title_tag} class="post-card__title"><a href="{p["slug"]}.html">{html.escape(p["title"])}</a></{title_tag}>
    <p class="post-card__excerpt">{excerpt}</p>
    <a class="link-line" href="{p["slug"]}.html">Read the guide {ARROW}</a>
  </div>
</article>'''


# ---------------------------------------------------------------- layout
def head(title, description, path, extra=""):
    canonical = DOMAIN + "/" + ("" if path == "index.html" else path)
    og_img = DOMAIN + "/assets/img/hero-poster.jpg"
    t = html.escape(title)
    d = html.escape(description)
    return f'''<!doctype html>
<html lang="en-CA">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{t}</title>
<meta name="description" content="{d}">
<link rel="canonical" href="{canonical}">
<meta name="theme-color" content="#13110e">
<meta property="og:type" content="website">
<meta property="og:site_name" content="Jack Albert Weddings">
<meta property="og:title" content="{t}">
<meta property="og:description" content="{d}">
<meta property="og:url" content="{canonical}">
<meta property="og:image" content="{og_img}">
<meta property="og:locale" content="en_CA">
<meta name="twitter:card" content="summary_large_image">
<link rel="icon" href="assets/img/favicon.svg" type="image/svg+xml">
<link rel="apple-touch-icon" href="assets/img/apple-touch-icon.png">
<link rel="manifest" href="site.webmanifest">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,300;0,400;0,500;1,300;1,400&family=Jost:wght@400;500&display=swap" rel="stylesheet">
<link rel="stylesheet" href="assets/css/site.css?v={VERSION}">
{extra}
<script>
!function(f,b,e,v,n,t,s){{if(f.fbq)return;n=f.fbq=function(){{n.callMethod?n.callMethod.apply(n,arguments):n.queue.push(arguments)}};if(!f._fbq)f._fbq=n;n.push=n;n.loaded=!0;n.version='2.0';n.queue=[];t=b.createElement(e);t.async=!0;t.src=v;s=b.getElementsByTagName(e)[0];s.parentNode.insertBefore(t,s)}}(window,document,'script','https://connect.facebook.net/en_US/fbevents.js');
fbq('init','{BRAND["pixel"]}');fbq('track','PageView');
</script>
</head>'''


def header(active, over_hero):
    links = "".join(
        f'<a class="nav__link" href="{href}"{" aria-current=\"page\"" if key == active else ""}>{label}</a>'
        for key, href, label in NAV)
    mlinks = "".join(
        f'<li><a href="{href}"><small>0{i + 1}</small>{label}</a></li>'
        for i, (key, href, label) in enumerate(NAV + [("contact", "contact.html", "Contact")]))
    cls = "site-header is-over-hero" if over_hero else "site-header"
    return f'''<a class="skip-link" href="#main">Skip to content</a>
<div class="curtain" aria-hidden="true"><div class="curtain__mark">Jack Albert<span>Wedding Films</span></div></div>
<header class="{cls}">
  <div class="container site-header__inner">
    <a class="logo" href="index.html" aria-label="Jack Albert Weddings, home">
      <span class="logo__name">Jack <em>Albert</em></span>
      <span class="logo__tag">Wedding Films</span>
    </a>
    <nav class="nav" aria-label="Primary">{links}<a class="btn header-cta" href="contact.html">Check your date</a></nav>
    <button class="menu-toggle" type="button" aria-expanded="false" aria-controls="mobile-menu" aria-label="Open menu"><span></span><span></span></button>
  </div>
</header>
<div class="mobile-menu" id="mobile-menu" aria-hidden="true">
  <ul class="mobile-menu__links">{mlinks}</ul>
  <div class="mobile-menu__foot">
    <div class="mobile-menu__contact">
      <a href="tel:{BRAND["tel"]}">{BRAND["phone"]}</a>
      <a href="mailto:{BRAND["email"]}">{BRAND["email"]}</a>
    </div>
    <a class="btn btn--light btn--block" href="contact.html">Check your date {ARROW}</a>
    <div class="socials"><a href="{BRAND["instagram"]}" target="_blank" rel="noopener" aria-label="Instagram">{IG}</a><a href="{BRAND["youtube"]}" target="_blank" rel="noopener" aria-label="YouTube">{YT}</a></div>
  </div>
</div>'''


def footer(show_cta=True):
    cta = f'''<div class="footer-cta">
      <h2 class="display-lg reveal">A film you’ll <em class="accent">watch forever.</em></h2>
      <div class="reveal" data-delay="1"><p>Dates for the coming seasons are booking now. Share a few details and I’ll reply within 24 hours.</p>
      <div class="actions"><a class="btn" href="contact.html">Check your date {ARROW}</a></div></div>
    </div>''' if show_cta else ""
    return f'''<footer class="site-footer">
  <div class="container">
    {cta}
    <div class="footer-grid">
      <div class="footer-col footer-brand">
        <a class="logo" href="index.html"><span class="logo__name">Jack <em>Albert</em></span><span class="logo__tag">Wedding Films</span></a>
        <p>Warm, cinematic wedding films from the Ottawa Valley, for couples close to home and wherever the day takes you.</p>
        <div class="socials"><a href="{BRAND["instagram"]}" target="_blank" rel="noopener" aria-label="Instagram">{IG}</a><a href="{BRAND["youtube"]}" target="_blank" rel="noopener" aria-label="YouTube">{YT}</a><a href="mailto:{BRAND["email"]}" aria-label="Email">{MAIL}</a><a href="tel:{BRAND["tel"]}" aria-label="Call">{PHONE}</a></div>
      </div>
      <div class="footer-col">
        <h4>Contact</h4>
        <ul>
          <li><a class="big" href="tel:{BRAND["tel"]}">{BRAND["phone"]}</a></li>
          <li><a href="mailto:{BRAND["email"]}">{BRAND["email"]}</a></li>
          <li><a href="{BRAND["calendly"]}" target="_blank" rel="noopener">Book a call</a></li>
          <li><a href="{BRAND["instagram"]}" target="_blank" rel="noopener">@jackalbertweddings</a></li>
        </ul>
      </div>
      <div class="footer-col">
        <h4>Explore</h4>
        <ul>
          <li><a href="films.html">Films</a></li>
          <li><a href="experience.html">The Experience</a></li>
          <li><a href="investment.html">Investment</a></li>
          <li><a href="about.html">About Jack</a></li>
          <li><a href="journal.html">Journal</a></li>
          <li><a href="contact.html">Contact</a></li>
        </ul>
      </div>
      <div class="footer-col">
        <h4>Service area</h4>
        <ul>
          <li><a href="pembroke-wedding-videographer.html">Pembroke &amp; Renfrew County</a></li>
          <li><a href="ottawa-wedding-videographer.html">Ottawa weddings</a></li>
          <li><a href="about.html#area">Kingston &amp; the Valley</a></li>
          <li><a href="contact.html">Further afield</a></li>
        </ul>
      </div>
    </div>
    <div class="footer-word" aria-hidden="true">Jack Albert</div>
    <div class="footer-bottom">
      <span>© <span data-year>{date.today().year}</span> Jack Albert Weddings · Ottawa Valley, Ontario</span>
      <span><a href="privacy.html">Privacy</a></span>
    </div>
  </div>
</footer>
<div class="mobile-cta" aria-label="Quick contact">
  <a class="btn" href="contact.html">Check your date</a>
  <a class="btn btn--icon" href="tel:{BRAND["tel"]}" aria-label="Call Jack">{PHONE}</a>
</div>
<div class="modal" id="film-modal" role="dialog" aria-modal="true" aria-label="Wedding film" aria-hidden="true">
  <span class="modal__title"></span>
  <button class="modal__close" type="button" aria-label="Close film">{CLOSE}</button>
  <div class="modal__frame"></div>
</div>
<script src="assets/js/site.js?v={VERSION}" defer></script>
</body>
</html>'''


SCHEMA = {
    "@context": "https://schema.org",
    "@type": "LocalBusiness",
    "name": "Jack Albert Weddings",
    "description": "Cinematic, documentary-style wedding videography in the Ottawa Valley, Ottawa, Kingston and beyond.",
    "url": DOMAIN + "/",
    "image": DOMAIN + "/assets/img/hero-poster.jpg",
    "telephone": "+1-613-621-0458",
    "email": BRAND["email"],
    "priceRange": "$1,950–$3,950+",
    "address": {"@type": "PostalAddress", "addressRegion": "ON", "addressCountry": "CA", "addressLocality": "Ottawa Valley"},
    "areaServed": ["Ottawa Valley", "Renfrew County", "Pembroke", "Petawawa", "Renfrew", "Arnprior", "Golden Lake", "Ottawa", "Kingston"],
    "sameAs": [BRAND["instagram"], BRAND["youtube"]],
}


def expand(text, posts):
    def rep(m):
        key = m.group(1)
        if key.startswith("posts:"):
            arg = key.split(":", 1)[1]
            if arg == "all":
                return "\n".join(post_card(p, lead=(i == 0)) for i, p in enumerate(posts))
            return "\n".join(post_card(p) for p in posts[: int(arg)])
        if key not in SNIPPETS:
            raise KeyError(f"Unknown snippet {{{{{key}}}}}")
        return SNIPPETS[key]
    return re.sub(r"\{\{([a-z0-9_:\-]+)\}\}", rep, text)


def parse(path):
    raw = path.read_text()
    m = re.match(r"---\n(.*?)\n---\n", raw, re.S)
    meta = dict(line.split(": ", 1) for line in m.group(1).splitlines() if line.strip())
    return meta, raw[m.end():]


def render(path, meta, body, posts):
    extra = meta.get("extra", "")
    if path == "index.html":
        extra += '\n<script type="application/ld+json">' + json.dumps(SCHEMA) + "</script>"
    out = head(meta["title"], meta["description"], path, extra)
    out += "\n<body>\n" + header(meta.get("nav", ""), meta.get("hero") == "dark")
    out += '\n<main id="main">\n' + expand(body, posts) + "\n</main>\n"
    # pages ending in the full-bleed CTA band don't need the footer CTA as well
    show_cta = meta.get("footer_cta", "yes") != "no" and "{{cta_band}}" not in body
    out += footer(show_cta)
    (OUT / path).write_text(out)


def article(p, posts):
    others = [x for x in posts if x["slug"] != p["slug"]]
    same = [x for x in others if x["cat"] == p["cat"]][:3]
    related = (same + [x for x in others if x not in same])[:3]
    schema = {
        "@context": "https://schema.org", "@type": "BlogPosting", "headline": p["title"],
        "description": p["description"], "author": {"@type": "Person", "name": "Jack Albert"},
        "image": f'{DOMAIN}/assets/img/{p["img"]}', "mainEntityOfPage": f'{DOMAIN}/{p["slug"]}.html',
        "publisher": {"@type": "Organization", "name": "Jack Albert Weddings"},
    }
    body = f'''<article>
  <header class="article-hero">
    <div class="container container--narrow">
      <nav class="breadcrumbs" aria-label="Breadcrumb"><a href="journal.html">Journal</a><span>/</span>{html.escape(p["eyebrow"])}</nav>
      <h1 class="display-md fade-in">{html.escape(p["title"])}</h1>
      <p class="article-meta">{html.escape(p["meta"])}</p>
    </div>
  </header>
  <div class="container"><div class="frame-img article-cover reveal-img"><img src="assets/img/{p["img"]}" alt="" decoding="async"></div></div>
  <div class="section" style="padding-top:clamp(56px,7vw,96px)">
    <div class="container container--text">
      <div class="prose">{p["body"]}</div>
      <aside class="article-cta">
        <h3>Thinking about a film for your day?</h3>
        <p>Tell me your date and venue and I’ll get back to you within 24 hours. No pressure, just a friendly chat.</p>
        <a class="btn" href="contact.html">Check your date {ARROW}</a>
      </aside>
      <div class="article-author">
        <img src="assets/img/about-jack.jpg" alt="Jack Albert filming with a gimbal" loading="lazy">
        <div><strong>Jack Albert</strong><span>Wedding filmmaker based in the Ottawa Valley</span></div>
      </div>
    </div>
  </div>
</article>
<section class="section section--paper2">
  <div class="container">
    <div class="section-head"><div><p class="eyebrow">Keep reading</p><h2 class="display-md">More from the <em>journal.</em></h2></div>
    <div><a class="link-line" href="journal.html">All guides {ARROW}</a></div></div>
    <div class="posts">{"".join(post_card(r) for r in related)}</div>
  </div>
</section>'''
    meta = {
        "title": p["seo_title"] or f'{p["title"]} | Jack Albert Weddings',
        "description": p["description"],
        "nav": "journal",
        "extra": '<script type="application/ld+json">' + json.dumps(schema) + "</script>",
    }
    render(p["slug"] + ".html", meta, body, posts)


def main():
    global VERSION
    VERSION = str(int((SRC / ".." / "site" / "assets" / "css" / "site.css").stat().st_mtime))
    posts = load_posts()
    pages = sorted((SRC / "pages").glob("*.html"))
    for page in pages:
        meta, body = parse(page)
        render(page.name, meta, body, posts)
    for p in posts:
        article(p, posts)
    # old journal URL -> new
    (OUT / "blog.html").write_text('<!doctype html><meta charset="utf-8"><title>Journal</title><link rel="canonical" href="'
                                   + DOMAIN + '/journal.html"><meta http-equiv="refresh" content="0; url=journal.html"><a href="journal.html">Journal</a>')
    urls = ["index.html"] + [p.name for p in pages if p.name not in ("index.html", "404.html")] + [p["slug"] + ".html" for p in posts]
    sm = "\n".join(f"  <url><loc>{DOMAIN}/{'' if u == 'index.html' else u}</loc></url>" for u in urls)
    (OUT / "sitemap.xml").write_text(f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n{sm}\n</urlset>\n')
    (OUT / "robots.txt").write_text(f"User-agent: *\nAllow: /\n\nSitemap: {DOMAIN}/sitemap.xml\n")
    print(f"Built {len(pages)} pages and {len(posts)} articles into {OUT}")


VERSION = "1"
if __name__ == "__main__":
    main()
