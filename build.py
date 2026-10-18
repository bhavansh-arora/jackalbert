#!/usr/bin/env python3
"""Static site generator for Jack Albert Weddings.

Wraps every page in src/pages/ and every article in src/posts/ in the shared
layout (head, header, menu, footer, film modal) and writes plain HTML to the repo root.

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
OUT = ROOT  # built pages sit at the repo root so any host serves them directly
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
CHAT = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.4" aria-hidden="true"><path d="M4 5h16v11H9l-5 4z"/></svg>'
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
    return f'''<a href="https://www.youtube.com/watch?v={f["yt"]}" class="film{attrs} {cls}" data-cursor="Play" data-yt="{f["yt"]}" data-title="{title} — {re.sub("&amp;", "&", f["place"])}"{preview} aria-label="Play the {title} wedding film">
  <div class="film__media">
    <img src="assets/img/{poster}" alt="Still from {title}'s wedding film" loading="lazy" decoding="async">
    {vid}
    <span class="film__play"><span class="play-ring">{PLAY}</span></span>
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


def datecheck(src="site", label="Your date", button="Check my date"):
    return f'''<form class="datecheck" data-datecheck="{src}" action="contact.html" novalidate>
  <label for="dc-{src}">{label}</label>
  <input id="dc-{src}" type="date" name="date" required aria-describedby="dcm-{src}">
  <button class="btn btn--gold" type="submit">{button} {ARROW}</button>
</form>
<p class="datecheck__msg" id="dcm-{src}" aria-live="polite"></p>'''


def cta_band(title="", text="", img="band-flowers.jpg", video="band-flowers.mp4", src="cta"):
    return f'''<section class="cta-band invite-band" id="act-5" data-act="act-5" aria-labelledby="cta-title-{src}">
  <div class="cta-band__bg" data-speed="-60"><video muted loop playsinline preload="none" data-loop data-src="assets/video/{video}" poster="assets/img/{img}"></video></div>
  <div class="container">
    <div class="invite reveal">
      <div class="invite__seal">{mono("seal-" + src, "mono mono--seal")}</div>
      <div class="invite__inner">
        <p class="invite__kicker">Together with Jack Albert Wedding Films</p>
        <p class="invite__small">you are cordially invited</p>
        <h2 id="cta-title-{src}" class="invite__script">to check your date</h2>
        {ORNAMENT}
        <p class="invite__body">Share the day you’re planning and Jack will personally reply within twenty-four hours. No pressure, just a friendly hello.</p>
        <div class="invite__form light">{datecheck(src, "Your date", "Check my date")}</div>
        <p class="invite__rsvp">Kindly reply · <a href="sms:{BRAND["tel"]}">text {BRAND["phone"]}</a> · or <a href="{BRAND["calendly"]}" target="_blank" rel="noopener">book a 15-minute call</a></p>
      </div>
    </div>
  </div>
</section>'''


def google_badge():
    return f'''<a class="google-badge" href="{BRAND["google"]}" target="_blank" rel="noopener"><span class="g">G</span><strong>5.0</strong><span class="stars" aria-hidden="true">★★★★★</span><span>on Google</span></a>'''


QUIZ = [
    ("How much of the day do you want filmed?", [
        ("sweet-simple", "The essentials", "About 6 hours, getting ready through portraits"),
        ("classic-collection", "The full day", "About 10 hours, getting ready through the reception"),
        ("luxury-collection", "Every moment", "12+ hours, early prep to the last dance")]),
    ("What do you want to watch back?", [
        ("sweet-simple", "A short, cinematic highlight", "3 to 5 minutes you’ll rewatch on every anniversary"),
        ("classic-collection", "A full film and the big moments", "Ceremony, speeches and first dance, plus a letter-reading film"),
        ("luxury-collection", "Everything, kept in full", "The film plus all of your footage, raw and colour graded")]),
    ("Anything to share right away?", [
        ("sweet-simple", "Not needed", "We’re happy to wait for the film"),
        ("classic-collection", "A social teaser", "A short cinematic teaser to post"),
        ("luxury-collection", "Yes, and faster delivery", "A shorter version to share, with expedited editing available")]),
]


def quiz():
    steps = ""
    for qi, (q, opts) in enumerate(QUIZ):
        o = "".join(f'<button class="quiz__opt" type="button" data-v="{v}"><strong>{t}</strong><span>{d}</span></button>' for v, t, d in opts)
        steps += f'<div class="quiz__step"><h3 class="quiz__q">{q}</h3><div class="quiz__opts">{o}</div></div>'
    return f'''<div class="quiz" data-quiz>
  <div class="quiz__top"><span data-quiz-count>Question 1 of 3</span><span class="quiz__bar"><span></span></span></div>
  {steps}
  <div class="quiz__result" aria-live="polite">
    <div>
      <p class="eyebrow">Your best match</p>
      <h3 class="display-md" data-r-name>Classic Collection</h3>
      <p class="quiz__price" data-r-price></p>
      <p class="body-lg" data-r-why></p>
    </div>
    <div style="display:grid;gap:14px;justify-items:start">
      <a class="btn btn--gold magnetic" data-r-cta href="contact.html">Check my date with this {ARROW}</a>
      <a class="btn btn--ghost" href="{BRAND["calendly"]}" target="_blank" rel="noopener">Talk it through on a call</a>
      <button class="quiz__restart" type="button">Start over</button>
    </div>
  </div>
</div>'''


def hgallery():
    cards = ""
    for i, k in enumerate(FILMS):
        f = FILMS[k]
        cards += f'''<article class="hcard">{film_tile(k, autoplay=True)}
      <div class="hcard__info"><div><div class="hcard__num">0{i + 1} / 04</div><h3 class="hcard__title">{f["couple"]}</h3></div><div class="hcard__place">{f["place"]}</div></div></article>'''
    return f'''<section class="hgallery" aria-labelledby="hg-title">
  <div class="hgallery__pin">
    <div class="container hgallery__head">
      <div><p class="eyebrow">Selected Films</p><h2 id="hg-title" class="display-md" data-split>Real days, <em class="accent">kept forever.</em></h2></div>
      <div class="hgallery__nav"><span class="hgallery__count"><b data-hg-current>1</b> / 04</span><button type="button" data-hg="-1" aria-label="Previous film">{ARROW}</button><button type="button" data-hg="1" aria-label="Next film">{ARROW}</button></div>
    </div>
    <div class="hgallery__track" data-cursor="Drag">{cards}
      <div class="hcard hcard--end"><p class="eyebrow">There’s more</p><h3 class="display-sm" style="margin-bottom:24px">Every film is made for <em class="accent">one couple.</em> Yours is next.</h3><div class="actions"><a class="btn btn--gold magnetic" href="contact.html">Check your date {ARROW}</a><a class="link-line" href="films.html">All films {ARROW}</a></div></div>
    </div>
    <div class="hgallery__progress"><span></span></div>
  </div>
</section>'''


def reel():
    f = FILMS["shelby-bobby"]
    return f'''<section class="reel" aria-label="Showreel">
  <div class="reel__sticky">
    <span class="reel__word reel__word--l" aria-hidden="true">The</span>
    <button class="reel__frame" type="button" data-cursor="Play" data-yt="{f["yt"]}" data-title="Shelby &amp; Bobby — A Lakeside Wedding · Chapeau" aria-label="Play the featured film, Shelby and Bobby">
      <video muted loop playsinline preload="none" data-loop data-src="assets/video/reel.mp4" poster="assets/img/reel-poster.jpg"></video>
      <span class="reel__play"><span class="play-ring">{PLAY}</span><span class="caps">The featured film</span><span class="t">Shelby &amp; Bobby</span></span>
      <span class="reel__meta"><span>A Lakeside Wedding</span><span>Chapeau · Ottawa Valley</span></span>
    </button>
    <span class="reel__word reel__word--r" aria-hidden="true">Reel</span>
  </div>
</section>'''


SCROLLY = [
    ("bride-window.jpg", "A bride in her veil by a bright window", "Led by <em>light.</em>", "A strong eye for light and how to shape it, so every scene feels soft, warm and true to the moment, whether it’s a church at noon or a lakeshore at dusk."),
    ("aisle-father.jpg", "A father walking his daughter down the aisle", "Obsessed with <em>sound.</em>", "Your vows, your speeches, a parent’s laugh. Clean audio is what brings the day rushing back, so I’m close to obsessive about it."),
    ("bree-skyler-laugh.jpg", "A groom laughing as he sees his bride", "Mostly <em>invisible.</em>", "Calm, professional and in the background, catching real moments as they happen, with light direction only when it helps. The day stays yours."),
]


def scrolly():
    imgs = "".join(f'<div class="scrolly__img"><img src="assets/img/{i}" alt="{a}" loading="lazy"></div>' for i, a, _, _ in SCROLLY)
    steps = "".join(f'<div class="scrolly__step{" is-active" if n == 0 else ""}"><div class="frame-img"><img src="assets/img/{i}" alt="" loading="lazy"></div><p class="num">0{n + 1} — The Approach</p><h3>{h}</h3><p>{t}</p></div>' for n, (i, a, h, t) in enumerate(SCROLLY))
    return f'<div class="scrolly"><div class="scrolly__media">{imgs}<span class="scrolly__counter">01 / 03</span></div><div class="scrolly__steps">{steps}</div></div>'


STEPS = [
    ("Inquire", "Share your date, venue, and what matters most. You’ll get a quick text so you know it arrived, then a reply by email within 24 hours."),
    ("Connect", "A relaxed conversation to make sure we’re the right fit. Tell me about the two of you, your people, and the moments you can’t imagine missing."),
    ("Plan your story", "We shape the timeline and filming plan around your people and priorities, leaving buffer where it counts so nothing gets rushed."),
    ("Your wedding day", "Calm direction when it helps, with space for the real moments to unfold. I stay professional and mostly invisible."),
    ("Relive it", "Your finished film arrives in six to eight weeks, in a private 4K gallery that’s yours to download, keep and share."),
]


def timeline():
    st = "".join(f'<div class="tl-step reveal"><h3 class="tl-step__title"><small>0{i + 1}</small>{t}</h3><p>{d}</p></div>' for i, (t, d) in enumerate(STEPS))
    return f'<div class="timeline"><div class="timeline__line"><span></span></div>{st}</div>'


def film_index():
    rows = ""
    for i, k in enumerate(FILMS):
        f = FILMS[k]
        title = f["couple"].replace("&amp;", "&")
        rows += f'<button class="fi-row" type="button" data-cursor="Play" data-yt="{f["yt"]}" data-title="{title} — {f["place"]}" data-preview="assets/video/{f["video"]}"><span class="fi-row__num">0{i + 1}</span><span class="fi-row__title">{f["couple"]}</span><span class="fi-row__place">{f["place"]}</span><span class="fi-row__go">{PLAY}</span></button>'
    return f'<div class="film-index reveal">{rows}</div>'



# ---------------------------------------------------------------- concept: "The Wedding Film"
def mono(uid, cls="mono"):
    """JA monogram seal."""
    return (f'<svg class="{cls}" viewBox="0 0 100 100" aria-hidden="true">'
            f'<defs><path id="mt-{uid}" d="M50 50m-37 0a37 37 0 1 1 74 0a37 37 0 1 1-74 0"/></defs>'
            '<circle cx="50" cy="50" r="48" fill="none" stroke="currentColor" stroke-width=".7"/>'
            '<circle cx="50" cy="50" r="44.5" fill="none" stroke="currentColor" stroke-width=".35" stroke-dasharray=".6 1.6"/>'
            f'<text class="mono__ring"><textPath href="#mt-{uid}" startOffset="0">WEDDING FILMS · OTTAWA VALLEY · EST. JA ·</textPath></text>'
            '<text class="mono__j" x="41" y="62">J</text><text class="mono__a" x="51" y="62">A</text>'
            '<path d="M33 69h34" stroke="currentColor" stroke-width=".5"/></svg>')


def swash(word, kind="under"):
    """Hand-drawn gold stroke that draws on when its heading reveals."""
    if kind == "circle":
        path = '<path pathLength="1" d="M8 34C6 14 52 3 104 6s96 14 92 30-58 26-110 22S6 52 12 30"/>'
        vb = "0 0 210 60"
    else:
        path = '<path pathLength="1" d="M4 14C40 6 96 4 150 8c22 2 34 5 42 9M60 17c30-4 70-3 96 2"/>'
        vb = "0 0 200 24"
    return f'<span class="swash swash--{kind}">{word}<svg viewBox="{vb}" preserveAspectRatio="none" aria-hidden="true">{path}</svg></span>'


def filmedge(side, code="JA 5219"):
    marks = " · ".join(f"{code}  {n}{'A' if n % 2 else ''} ▸" for n in range(11, 23))
    return f'<div class="filmedge filmedge--{side}" aria-hidden="true"><span class="filmedge__holes"></span><span class="filmedge__code">{marks}</span></div>'


def act(n, title):
    return f'<p class="act reveal"><span class="act__n">Act {n}</span><span class="act__line"></span><span class="act__t">{title}</span></p>'


ACTS = [("I", "The Feeling", "act-1"), ("II", "The Films", "act-2"), ("III", "The Approach", "act-3"), ("IV", "Your Day", "act-4"), ("V", "The Invitation", "act-5")]


def actrail():
    items = "".join(f'<li><a href="#{a}" data-act-link="{a}"><span class="n">{n}</span><span class="t">{t}</span></a></li>' for n, t, a in ACTS)
    return f'<nav class="actrail" aria-label="Chapters"><ol>{items}</ol><span class="actrail__bar"><span></span></span></nav>'


SHEET = [
    ("bree-portrait.jpg", "circle"), ("bree-skyler-laugh.jpg", ""), ("cake-detail.jpg", ""), ("champagne.jpg", "star"),
    ("aisle-father.jpg", ""), ("bride-window.jpg", "circle"), ("skyline-dance.jpg", ""), ("pembroke-aisle.jpg", "x"),
    ("preview-lyndon-paige.jpg", ""), ("s8-fs.jpg", ""), ("pembroke-kiss.jpg", "circle"), ("reel-poster.jpg", ""),
]
MARKS = {
    "circle": '<svg class="grease" viewBox="0 0 100 70" preserveAspectRatio="none" aria-hidden="true"><path pathLength="1" d="M10 38C4 16 40 4 62 5s36 12 33 30-30 30-55 28S4 52 14 26"/></svg>',
    "x": '<svg class="grease" viewBox="0 0 100 70" preserveAspectRatio="none" aria-hidden="true"><path pathLength="1" d="M14 10L86 60M84 12L18 58"/></svg>',
    "star": '<svg class="grease grease--star" viewBox="0 0 40 40" aria-hidden="true"><path pathLength="1" d="M20 4l4 11 12 1-9 8 3 12-10-7-10 7 3-12-9-8 12-1z"/></svg>',
}


def contact_sheet(caption="Selects · Real weddings, real moments"):
    frames = ""
    for i, (img, mark) in enumerate(SHEET):
        n = 14 + i
        frames += (f'<figure class="cs__frame{" cs__frame--select" if mark == "circle" else ""}">'
                   f'<div class="cs__img"><img src="assets/img/{img}" alt="" loading="lazy" decoding="async"></div>'
                   f'<figcaption><span>{n}</span><span class="cs__arrow">▸</span><span>{n}A</span></figcaption>{MARKS.get(mark, "")}</figure>')
    return f'''<div class="cs reveal">
  <div class="cs__edge"><span>JA 5219</span><span>KODAK-STYLE PROOF · ROLL 07</span><span>◀ 24 ▸</span></div>
  <div class="cs__grid">{frames}</div>
  <div class="cs__edge cs__edge--b"><span>{caption}</span><span>JACK ALBERT WEDDING FILMS</span></div>
</div>'''


ORNAMENT = '<div class="ornament" aria-hidden="true"><span></span><svg viewBox="0 0 40 20"><path d="M20 2c2 5 6 8 12 8-6 0-10 3-12 8-2-5-6-8-12-8 6 0 10-3 12-8z"/></svg><span></span></div>'


# ---------------------------------------------------------------- studio components (v3)
def fs_slider():
    slides = titles = metas = bars = ""
    for i, (k, f) in enumerate(FILMS.items()):
        t = f["couple"].replace("&amp;", "&")
        act = " is-active" if i == 0 else ""
        slides += f'<div class="fs__slide{act}" data-slide data-img="assets/img/{f["img"]}" data-yt="{f["yt"]}" data-title="{t} — {f["place"]}"><img src="assets/img/{f["img"]}" alt="Still from {t}’s wedding film" loading="lazy"></div>'
        a, b = f["couple"].split(" &amp; ")
        titles += f'<h3 class="fs__title{act}"><span>{a}</span> <em>&amp;</em> <span>{b}</span></h3>'
        metas += f'<p class="fs__meta{act}">{f["place"]}</p>'
        bars += '<span role="button" tabindex="0" aria-label="Film ' + str(i + 1) + '"><i></i></span>'
    first = next(iter(FILMS.values()))
    return f'''<section class="fs" data-gl-slider tabindex="0" aria-label="Selected films">
  <div class="fs__stage" data-cursor="Drag">{slides}</div>
  <div class="fs__shade"></div>
  <div class="fs__ui">
    <div class="fs__top container"><p class="label label--light"><span>(03)</span><span>Selected films</span></p><span class="fs__count"><b data-fs-cur>01</b> / 0{len(FILMS)}</span></div>
    <div class="fs__mid container"><div class="fs__titles">{titles}</div></div>
    <div class="fs__bottom container">
      <div class="fs__metas">{metas}</div>
      <div class="fs__controls">
        <button class="fs__btn" type="button" data-fs="-1" aria-label="Previous film">{ARROW}</button>
        <button class="fs__play" type="button" data-fs-play data-yt="{first["yt"]}" data-title="Film">Play film {PLAY}</button>
        <button class="fs__btn" type="button" data-fs="1" aria-label="Next film">{ARROW}</button>
      </div>
    </div>
    <div class="fs__bars container">{bars}</div>
  </div>
</section>'''


STEPS_V3 = [
    ("Day 1", "Inquire", "Share your date, venue and what matters most. You’ll get a quick text so you know it arrived, then a reply by email within 24 hours.", "bree-portrait.jpg"),
    ("Within a week", "Connect", "A relaxed call to make sure we’re the right fit. Tell me about the two of you, your people, and the moments you can’t imagine missing.", "about-jack.jpg"),
    ("Weeks before", "Plan your story", "We shape the timeline and filming plan around your people and priorities, with buffer where it counts so nothing gets rushed.", "cake-detail.jpg"),
    ("The day", "Your wedding day", "Calm direction when it helps, with space for the real moments to unfold. One familiar face, mostly invisible.", "aisle-father.jpg"),
    ("6–8 weeks", "Relive it", "Your finished film arrives in a private 4K gallery, yours to download, keep and watch on every anniversary.", "reel-poster.jpg"),
]


def steps_stack():
    cards = ""
    for i, (tag, t, d, img) in enumerate(STEPS_V3):
        cards += f'''<article class="stack__card" style="--i:{i}">
      <div class="stack__text"><div class="stack__top"><span>Step 0{i + 1} / 0{len(STEPS_V3)}</span><span class="chip">{tag}</span></div><h3>{t}</h3><p>{d}</p></div>
      <div class="stack__img"><img src="assets/img/{img}" alt="" loading="lazy"></div>
    </article>'''
    return f'<div class="stack">{cards}</div>'


def review_cards():
    imgs = ["preview-shelby-bobby.jpg", "skyline-dance.jpg", "aisle-father.jpg", "bride-window.jpg"]
    cards = ""
    for (q, who), img in zip(REVIEWS, imgs):
        cards += f'''<figure class="rcard reveal"><div class="rcard__img"><img src="assets/img/{img}" alt="" loading="lazy"></div>
      <blockquote><p>“{q}”</p></blockquote><figcaption><span>{who}</span><span class="rcard__q" aria-hidden="true">“</span></figcaption></figure>'''
    return f'<div class="rcards">{cards}</div>'


HEROES = {
    # key: (scene label, eyebrow, title, sub, poster, video or None, buttons html, size)
    "films": ("Scene 02 · The Films", "The Films", 'Real days, <em class="gold-text">kept forever.</em>',
              "The work speaks louder than I can. Four weddings, four stories, each one made for one couple.",
              "reel-poster.jpg", "reel.mp4",
              f'<button class="btn btn--gold magnetic" type="button" data-yt="GLoy1N3UaAU" data-title="Shelby &amp; Bobby — A Lakeside Wedding · Chapeau">Play the featured film {PLAY}</button><a class="btn btn--ghost-light magnetic" href="#index-title">Browse all films</a>', ""),
    "experience": ("Scene 03 · The Experience", "The Experience", 'Calm, considered, <em class="gold-text">all about you.</em>',
                   "A relaxed, personal experience shaped around the people and moments that matter most to you, from first hello to the night you press play.",
                   "pembroke-aisle.jpg", "pembroke-aisle.mp4",
                   f'<a class="btn btn--gold magnetic" href="contact.html?src=experience">Check your date {ARROW}</a><a class="btn btn--ghost-light magnetic" href="#steps-title">How it works</a>', ""),
    "investment": ("Scene 04 · The Investment", "The Investment", 'Three collections, <em class="gold-text">one clear price.</em>',
                   "Clear, honest pricing from $1,950. Extra hours, raw footage and travel are quoted for your day, so there are never surprises.",
                   "band-flowers.jpg", "band-flowers.mp4",
                   f'<a class="btn btn--gold magnetic" href="#finder">Find my collection {ARROW}</a><a class="btn btn--ghost-light magnetic" href="#collections">See the collections</a>', ""),
    "about": ("Scene 05 · The Filmmaker", "About Me", 'Hi, I’m <em class="gold-text">Jack.</em>',
              "Wedding filmmaker, Ottawa Valley local, and the one person behind the camera at every wedding I film.",
              "bree-skyler-laugh.jpg", "preview-bree-skyler.mp4",
              f'<a class="btn btn--gold magnetic" href="contact.html?src=about">Check your date {ARROW}</a><a class="btn btn--ghost-light magnetic" href="#story-title">My story</a>', ""),
    "journal": ("Scene 06 · The Journal", "The Journal", 'Planning your <em class="gold-text">wedding film.</em>',
                "Honest guides for couples getting married in the Ottawa Valley, from what things cost to choosing a videographer and filming a country wedding.",
                "aisle-father.jpg", None,
                f'<a class="btn btn--gold magnetic" href="#articles">Read the guides {ARROW}</a>', ""),
    "contact": ("Scene 07 · Let’s Talk", "Let’s Talk", 'Tell me about <em class="gold-text">your day.</em>',
                "Four quick steps and I’ll let you know if your date is open, usually within 24 hours.",
                "pembroke-kiss.jpg", "pembroke-kiss.mp4",
                f'<a class="btn btn--gold magnetic" href="#inquiry">Start my inquiry {ARROW}</a><a class="btn btn--ghost-light magnetic" href="sms:{BRAND["tel"]}">Text Jack</a>', "short"),
    "ottawa": ("Ottawa · Ottawa Valley · Renfrew County", "Ottawa · Ottawa Valley", 'Ottawa wedding <em class="gold-text">videographer.</em>',
               "Cinematic, documentary-style wedding films for couples getting married in Ottawa and across the Valley.",
               "s8-fs.jpg", "s8-fs.mp4",
               f'<a class="btn btn--gold magnetic" href="contact.html?src=ottawa">Check your Ottawa date {ARROW}</a>', ""),
    "pembroke": ("Pembroke · Renfrew County", "Pembroke · Renfrew County", 'Pembroke wedding <em class="gold-text">videographer.</em>',
                 "Cinematic wedding films for couples getting married in Pembroke and across Renfrew County, from a filmmaker who’s from here.",
                 "pembroke-venue.jpg", "pembroke-venue.mp4",
                 f'<a class="btn btn--gold magnetic" href="contact.html?src=pembroke">Check your Pembroke date {ARROW}</a>', ""),
    "notfound": ("Scene 404 · Cut", "404", 'This scene <em class="gold-text">didn’t make the cut.</em>',
                 "The page you’re looking for has moved or no longer exists.",
                 "band-flowers.jpg", "band-flowers.mp4",
                 f'<a class="btn btn--gold magnetic" href="index.html">Back home {ARROW}</a><a class="btn btn--ghost-light magnetic" href="films.html">Watch the films</a>', "short"),
}


def page_hero(scene, eyebrow, title, sub, poster, video, buttons, size="", crumbs=""):
    vid = (f'<video muted loop playsinline autoplay preload="auto" poster="assets/img/{poster}" data-src-desktop="assets/video/{video}" data-src-mobile="assets/video/{video}" aria-hidden="true"></video>'
           if video else "")
    cls = "hero hero--page" + (" hero--short" if size == "short" else "")
    return f'''<section class="{cls}" data-hero aria-label="Introduction">
  <div class="hero__media"{' data-gl-video' if video else ''}><img src="assets/img/{poster}" alt="" fetchpriority="high">{vid}</div>
  <div class="hero__scrim"></div>
  <div class="letterbox letterbox--top"></div>
  <div class="letterbox letterbox--bottom"></div>
  {filmedge("l")}{filmedge("r", "JA 2027")}
  <div class="viewfinder" aria-hidden="true">
    <span class="vf-corner vf-corner--tl"></span><span class="vf-corner vf-corner--tr"></span>
    <span class="vf-corner vf-corner--bl"></span><span class="vf-corner vf-corner--br"></span>
    <div class="vf-tl"><span class="vf-rec">REC</span><span data-timecode>00:01:23:00</span></div>
    <div class="vf-tr"><span class="vf-hide-sm">{scene}</span><span class="vf-batt"></span></div>
  </div>
  <div class="hero__content hero__content--page">
    {crumbs}<p class="eyebrow hero__eyebrow">{eyebrow}</p>
    <h1 class="display-xl hero__title" data-split data-hero-split data-delay="300">{title}</h1>
    <p class="hero__sub">{sub}</p>
    <div class="hero__cta"><div class="actions">{buttons}</div></div>
  </div>
  <div class="scroll-cue" aria-hidden="true"><span class="scroll-cue__line"></span>Scroll</div>
</section>'''


MOSAIC = [
    ("skyline-dance.jpg", "A couple dancing in front of a city skyline", "tall", 50),
    ("cake-detail.jpg", "A couple cutting a cake decorated with butterflies", "", -30),
    ("bree-portrait.jpg", "A bride in a flower crown smiling softly", "", 70),
    ("champagne.jpg", "Guests lifting coupes from a champagne tower", "wide", -50),
    ("pembroke-aisle.jpg", "Flower girls walking down a garden aisle", "", 30),
    ("bride-window.jpg", "A bride in her veil by a bright window", "tall", -60),
]


def mosaic():
    tiles = "".join(f'<figure class="mosaic__item mosaic__item--{c or "std"} reveal-img"><img src="assets/img/{i}" alt="{a}" loading="lazy" data-speed="{sp}"></figure>' for i, a, c, sp in MOSAIC)
    return f'<div class="mosaic">{tiles}</div>'


INCLUDES = [
    ("M3 7h18v12H3zM8 7l2-3h4l2 3", "A cinematic film", "Shaped around how your day felt"),
    ("M12 3v4M5 9l3 2M19 9l-3 2M4 14h16M7 14l-1 6M17 14l1 6", "Drone footage", "Weather permitting, in every collection"),
    ("M4 5h16v14H4zM4 15l5-4 4 3 3-2 4 3", "Private 4K gallery", "Yours to download, keep and share"),
    ("M12 3a9 9 0 1 0 0 18 9 9 0 0 0 0-18zM12 7v5l3 2", "6–8 week delivery", "Expedited editing available"),
    ("M12 12a4 4 0 1 0 0-8 4 4 0 0 0 0 8zM4 21c1-4 4-6 8-6s7 2 8 6", "One filmmaker", "Jack, start to finish"),
]


def includes():
    items = "".join(f'<li class="includes__item reveal" data-delay="{n}"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.2" aria-hidden="true"><path d="{d}"/></svg><strong>{t}</strong><span>{x}</span></li>' for n, (d, t, x) in enumerate(INCLUDES))
    return f'<ul class="includes">{items}</ul>'


def quote_band(img, quote, who, video=None):
    vid = f'<video muted loop playsinline preload="none" data-loop data-src="assets/video/{video}" poster="assets/img/{img}"></video>' if video else f'<img src="assets/img/{img}" alt="" loading="lazy">'
    return f'''<section class="quote-band" aria-label="Review">
  <div class="quote-band__bg" data-speed="-70">{vid}</div>
  <div class="container container--narrow">
    <div class="quote-band__mark" aria-hidden="true">“</div>
    <blockquote><p data-split>{quote}</p></blockquote>
    <p class="cite reveal">★★★★★ &nbsp; {who} · Google Review</p>
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
    "datecheck_hero": datecheck("hero", "Your wedding date", "Check my date"),
    "datecheck_light": datecheck("page"),
    "google_badge": google_badge(),
    "quiz": quiz(),
    "hgallery": hgallery(),
    "reel": reel(),
    "scrolly": scrolly(),
    "timeline": timeline(),
    "film_index": film_index(),
    "marquee_places": marquee(["Ottawa Valley", "Golden Lake", "Pembroke", "Ottawa", "Kingston", "Petawawa", "Renfrew", "Arnprior", "Chapeau"]),
    "marquee_moments": marquee(["The vows", "The first look", "The speeches", "The last dance", "The quiet moments"]),
    "marquee_words": marquee(["Warm", "Cinematic", "Honest", "Timeless", "Yours"]),
}
SNIPPETS["mosaic"] = mosaic()
SNIPPETS["fs_slider"] = fs_slider()
SNIPPETS["steps_stack"] = steps_stack()
SNIPPETS["review_cards"] = review_cards()
SNIPPETS["contact_sheet"] = contact_sheet()
SNIPPETS["actrail"] = actrail()
SNIPPETS["ornament"] = ORNAMENT
SNIPPETS["mono"] = mono("page")
for _n, _t, _a in ACTS:
    SNIPPETS["act:" + _a] = act(_n, _t)
SNIPPETS["swash:felt"] = swash('<em class="gold-text">felt.</em>')
SNIPPETS["filmedges"] = filmedge("l") + filmedge("r", "JA 2027")
SNIPPETS["includes"] = includes()
SNIPPETS["quote:shelby"] = quote_band("preview-shelby-bobby.jpg", "Every time we watch it, it feels like we get to relive the day all over again.", "Shelby &amp; Bobby", "preview-shelby-bobby.mp4")
SNIPPETS["quote:theresa"] = quote_band("skyline-dance.jpg", "Watching the footage feels like reliving it, and the highlight film blew us away.", "Theresa")
SNIPPETS["quote:madison"] = quote_band("aisle-father.jpg", "He captured our favourite moments from the Wilno Church to our reception, and we couldn’t be happier.", "Madison")
SNIPPETS["quote:ramona"] = quote_band("bride-window.jpg", "He knew exactly how to make our wedding video feel special. We got it back within weeks!", "Ramona")
for k, v in HEROES.items():
    SNIPPETS["hero:" + k] = page_hero(*v)
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
<meta name="theme-color" content="#0b0a09">
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
<link href="https://fonts.googleapis.com/css2?family=Inter+Tight:wght@300;400;500;600&family=Instrument+Serif:ital@0;1&family=Geist+Mono:wght@400;500&family=Pinyon+Script&display=swap" rel="stylesheet">
<script>document.documentElement.classList.add("js");try{{if(sessionStorage.getItem("jaw-intro")==="1")document.documentElement.classList.add("no-loader")}}catch(e){{}}</script>
<link rel="stylesheet" href="assets/css/site.css?v={VERSION}">
{extra}
<script>
!function(f,b,e,v,n,t,s){{if(f.fbq)return;n=f.fbq=function(){{n.callMethod?n.callMethod.apply(n,arguments):n.queue.push(arguments)}};if(!f._fbq)f._fbq=n;n.push=n;n.loaded=!0;n.version='2.0';n.queue=[];t=b.createElement(e);t.async=!0;t.src=v;s=b.getElementsByTagName(e)[0];s.parentNode.insertBefore(t,s)}}(window,document,'script','https://connect.facebook.net/en_US/fbevents.js');
fbq('init','{BRAND["pixel"]}');fbq('track','PageView');
</script>
</head>'''


def header(active, over_hero):
    links = "".join(
        f'<a class="nav__link" href="{href}"{" aria-current=\"page\"" if key == active else ""}><span>{label}</span><span aria-hidden="true">{label}</span></a>'
        for key, href, label in NAV)
    mlinks = "".join(
        f'<li><a href="{href}">{label}<small>0{i + 1}</small></a></li>'
        for i, (key, href, label) in enumerate(NAV + [("contact", "contact.html", "Contact")]))
    cls = "site-header is-over-hero" if over_hero else "site-header"
    return f'''<a class="skip-link" href="#main">Skip to content</a>
<div class="loader" aria-hidden="true">
  <div class="pl__frame"><img src="assets/img/hero-poster.jpg" alt=""><img src="assets/img/bree-portrait.jpg" alt=""><img src="assets/img/champagne.jpg" alt=""><img src="assets/img/skyline-dance.jpg" alt=""><img src="assets/img/aisle-father.jpg" alt=""><img src="assets/img/cake-detail.jpg" alt=""><img src="assets/img/bride-window.jpg" alt=""><img src="assets/img/pembroke-kiss.jpg" alt=""><img src="assets/img/reel-poster.jpg" alt=""></div>
  <div class="pl__brand"><span>Jack Albert</span><em>wedding films</em></div>
  <div class="pl__meta">Ottawa Valley · Ontario<br>Est. for the moments you’ll feel again</div>
  <div class="pl__count"><span data-pl-count>0</span><sup>%</sup></div>
</div>
<div class="curtain" aria-hidden="true"><div class="curtain__mark">Jack Albert</div></div>
<div class="announce"><a href="contact.html?src=bar"><span class="dot"></span>Now booking 2027 &amp; 2028 weddings · Check your date {ARROW}</a></div>
<header class="{cls}">
  <div class="container site-header__inner">
    <a class="logo logo--seal" href="index.html" aria-label="Jack Albert Weddings, home">
      {mono("hdr", "mono mono--hdr")}
      <span class="logo__words"><span class="logo__name">Jack <em>Albert</em></span>
      <span class="logo__tag">Wedding Films</span></span>
    </a>
    <nav class="nav" aria-label="Primary">{links}<a class="btn btn--gold header-cta magnetic" href="contact.html">Check your date</a></nav>
    <button class="menu-toggle" type="button" aria-expanded="false" aria-controls="mobile-menu" aria-label="Open menu"><span></span><span></span></button>
  </div>
</header>
<div class="mobile-menu" id="mobile-menu" aria-hidden="true">
  <ul class="mobile-menu__links">{mlinks}</ul>
  <div class="mobile-menu__foot">
    <a class="btn btn--gold btn--block" href="contact.html">Check your date {ARROW}</a>
    <div class="mobile-menu__contact">
      <a class="btn btn--ghost-light" href="sms:{BRAND["tel"]}">Text Jack</a>
      <a class="btn btn--ghost-light" href="tel:{BRAND["tel"]}">Call {BRAND["phone"]}</a>
    </div>
    <div class="socials"><a href="{BRAND["instagram"]}" target="_blank" rel="noopener" aria-label="Instagram">{IG}</a><a href="{BRAND["youtube"]}" target="_blank" rel="noopener" aria-label="YouTube">{YT}</a><a href="mailto:{BRAND["email"]}" aria-label="Email">{MAIL}</a></div>
  </div>
</div>'''


def footer(show_cta=True):
    cta = f'''<div class="closer">
      <div class="closer__left">
        <p class="label"><span>(Fin)</span><span>Your story, next</span></p>
        <h2 class="display-xl closer__title" data-split>Let’s tell <em>your story.</em></h2>
        <p class="closer__sub">Dates for 2027 and 2028 are booking now. Share a few details and Jack replies within 24 hours.</p>
        <div class="closer__form">{datecheck("footer", "Your date", "Check my date")}</div>
      </div>
      <a class="closer__circle magnetic" href="contact.html?src=footer-circle" aria-label="Check your date">
        <span class="spin"><svg viewBox="0 0 120 120" aria-hidden="true"><defs><path id="cc" d="M60 60m-48 0a48 48 0 1 1 96 0a48 48 0 1 1-96 0"/></defs><text><textPath href="#cc">Check your date · Check your date · </textPath></text></svg></span>
        {ARROW}
      </a>
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
          <li><a href="sms:{BRAND["tel"]}">Text Jack</a></li>
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
    <div class="footer-name" aria-hidden="true">Jack Albert</div>
    <div class="footer-bottom">
      <span>© <span data-year>{date.today().year}</span> Jack Albert Weddings · Ottawa Valley, Ontario</span>
      <span><a href="privacy.html">Privacy</a></span>
    </div>
  </div>
</footer>
<a class="float-cta" href="contact.html?src=float" aria-label="Check your date">
  <span class="float-cta__bg"></span>
  <span class="spin"><svg class="ring" viewBox="0 0 110 110" aria-hidden="true"><defs><path id="fc" d="M55 55m-42 0a42 42 0 1 1 84 0a42 42 0 1 1-84 0"/></defs><text><textPath href="#fc">Check your date · Check your date · </textPath></text></svg></span>
  {ARROW}
</a>
<div class="mobile-cta" aria-label="Quick contact">
  <a class="btn btn--gold" href="contact.html?src=mobile-bar">Check your date</a>
  <a class="btn btn--icon" href="sms:{BRAND["tel"]}" aria-label="Text Jack">{CHAT}</a>
  <a class="btn btn--icon" href="tel:{BRAND["tel"]}" aria-label="Call Jack">{PHONE}</a>
</div>
<div class="modal" id="film-modal" role="dialog" aria-modal="true" aria-label="Wedding film" aria-hidden="true">
  <span class="modal__title"></span>
  <button class="modal__close" type="button" aria-label="Close film">{CLOSE}</button>
  <div class="modal__frame"></div>
  <div class="modal__after"><a class="btn btn--gold btn--sm" href="contact.html?src=film">Want a film like this? Check your date {ARROW}</a></div>
</div>
<div class="exit" id="exit-modal" role="dialog" aria-modal="true" aria-labelledby="exit-title" aria-hidden="true">
  <div class="exit__card">
    <button class="exit__close" type="button" aria-label="Close">{CLOSE}</button>
    <div class="exit__img"><img src="assets/img/reel-poster.jpg" alt="" loading="lazy"></div>
    <div class="exit__body">
      <p class="eyebrow" style="margin:0">Before you go</p>
      <h3 id="exit-title">Is your date <em style="color:#e2c393">still open?</em></h3>
      <p>Pop it in and I’ll personally confirm within 24 hours. No obligation.</p>
      {datecheck("exit", "Wedding date", "Check")}
      <p class="exit__alt">Rather talk? <a href="sms:{BRAND["tel"]}">Text Jack</a> or <a href="{BRAND["calendly"]}" target="_blank" rel="noopener">book a 15-min call</a>.</p>
    </div>
  </div>
</div>
<script src="assets/js/site.js?v={VERSION}" defer></script>
<script src="assets/js/gl.js?v={VERSION}" defer></script>
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
    out += f'\n<body data-cal-url="{BRAND["calendly"]}">\n' + header(meta.get("nav", ""), meta.get("hero") == "dark")
    out += '\n<main id="main">\n' + expand(body, posts) + "\n</main>\n"
    # pages ending in the full-bleed CTA band don't need the footer CTA as well
    # pages that end with the invitation band don't repeat the closing CTA
    show_cta = meta.get("footer_cta", "yes") != "no" and "{{cta_band}}" not in body
    out += footer(show_cta)
    out = out.replace(f'href="{BRAND["calendly"]}"', f'href="{BRAND["calendly"]}" data-calendly')
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
    # give each h2 an id so the sidebar can list it
    toc, n = [], [0]
    def _id(m):
        n[0] += 1
        hid = "s" + str(n[0])
        toc.append((hid, re.sub(r"<[^>]+>", "", m.group(1))))
        return f'<h2 id="{hid}">{m.group(1)}</h2>'
    prose = re.sub(r"<h2>(.*?)</h2>", _id, p["body"])
    toc_html = "".join(f'<li><a href="#{i}">{t}</a></li>' for i, t in toc)
    crumbs = f'<nav class="breadcrumbs hero__crumbs" aria-label="Breadcrumb"><a href="journal.html">Journal</a><span>/</span>{html.escape(p["eyebrow"])}</nav>'
    hero = page_hero("The Journal · " + html.escape(p["eyebrow"]), html.escape(p["meta"]), html.escape(p["title"]),
                     "", p["img"], None,
                     f'<a class="btn btn--gold magnetic" href="#read">Read the guide {ARROW}</a>', "short", crumbs)
    hero = hero.replace('class="display-xl hero__title"', 'class="display-lg hero__title"')
    body = f'''<div class="read-progress" aria-hidden="true"></div>
<article>
  {hero}
  <div class="section" id="read" style="padding-top:clamp(64px,8vw,110px)">
    <div class="container article-layout">
      <div class="article-main">
        <div class="prose">{prose}</div>
        <aside class="article-cta">
          <p class="eyebrow">Your day, on film</p>
          <h3>Thinking about a film for your day?</h3>
          <p>Pop in your date and I’ll let you know if I’m free within 24 hours. No pressure, just a friendly chat.</p>
          {datecheck("article")}
        </aside>
        <div class="article-author">
          <img src="assets/img/about-jack.jpg" alt="Jack Albert filming with a gimbal" loading="lazy">
          <div><strong>Jack Albert</strong><span>Wedding filmmaker based in the Ottawa Valley</span></div>
        </div>
      </div>
      <aside class="article-side" aria-label="On this page">
        <div class="article-side__inner">
          {"<p class='caps muted'>On this page</p><ol class='toc'>" + toc_html + "</ol>" if toc else ""}
          <div class="side-card">
            <div class="side-card__img"><img src="assets/img/reel-poster.jpg" alt="" loading="lazy"></div>
            <div class="side-card__body">
              <p class="caps" style="color:#e2c393;margin:0 0 8px">Is your date open?</p>
              <p class="side-card__t">Films from $1,950. Replies within 24 hours.</p>
              <a class="btn btn--gold btn--sm btn--block" href="contact.html?src=article-side">Check your date {ARROW}</a>
            </div>
          </div>
        </div>
      </aside>
    </div>
  </div>
</article>
<section class="section section--paper2">
  <div class="container">
    <div class="section-head"><div><p class="eyebrow">Keep reading</p><h2 class="display-md" data-split>More from <em class="accent">the journal.</em></h2></div>
    <div><a class="link-line" href="journal.html">All guides {ARROW}</a></div></div>
    <div class="posts">{"".join(post_card(r) for r in related)}</div>
  </div>
</section>'''
    meta = {
        "title": p["seo_title"] or f'{p["title"]} | Jack Albert Weddings',
        "description": p["description"],
        "nav": "journal",
        "hero": "dark",
        "extra": '<script type="application/ld+json">' + json.dumps(schema) + "</script>",
    }
    render(p["slug"] + ".html", meta, body, posts)


def main():
    global VERSION
    VERSION = str(int((OUT / "assets" / "css" / "site.css").stat().st_mtime))
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
