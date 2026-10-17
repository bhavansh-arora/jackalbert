# Jack Albert Weddings — Website

A multi-page, mobile-first website for **Jack Albert Weddings**, an Ottawa Valley wedding filmmaker.
It is a plain static site: no framework, no build step needed to host it.

The built site lives at the **repo root** (`index.html` and friends), so any static host works with no settings: GitHub Pages (Settings → Pages → Deploy from branch `main`, folder `/ (root)`), Cloudflare Pages, Netlify, Vercel or cPanel.

## Pages

| Page | File |
| --- | --- |
| Home | `index.html` |
| Films | `films.html` |
| The Experience | `experience.html` |
| Investment & FAQ | `investment.html` |
| About | `about.html` |
| Journal (15 articles, filterable) | `journal.html` + one file per article |
| Contact / inquiry form | `contact.html` |
| Ottawa & Pembroke pages (SEO) | `ottawa-wedding-videographer.html`, `pembroke-wedding-videographer.html` |
| Privacy, 404 | `privacy.html`, `404.html` |

All article and location URLs match the current live site, so existing Google rankings carry over.
`blog.html` redirects to `journal.html`. `sitemap.xml` and `robots.txt` are generated.

## Design & motion

- Dark cinematic palette (espresso black, champagne gold, ivory) with film grain and ivory "breather" sections.
- Film-leader countdown intro (first visit), letterbox bars opening over the hero, camera-viewfinder overlay with live timecode.
- Showreel that grows to full screen as it passes through, swipe/drag film carousel with arrows, scroll-story with sticky images, word-by-word text reveals, gold timeline that fills as you scroll.
- Custom cursor ("Play" on films), magnetic buttons, 3D-tilt pricing cards, scroll-reactive marquees, page-to-page wipe transitions. Scrolling is fully native: no scroll-jacking or pinned sections.
- Everything respects reduced-motion settings; phones get swipe galleries and simpler scenes.

## Conversion features

- **Date checker** in the hero, CTA band, articles and exit prompt: gives an instant note about the chosen date, then opens the inquiry form with the date pre-filled.
- **Collection quiz** (3 questions) recommends a collection and links to the form with it pre-selected.
- **4-step inquiry form** with progress bar, validation and a locally saved draft; posts to the existing Formspree endpoint (`xaqgvyod`) and records the entry point (hero, quiz, film, exit, ...). The thank-you screen offers a Calendly call straight away.
- **Calendly** opens as an on-page popup; **Text Jack** / **Call** buttons; floating "Check your date" button (desktop) and sticky bar (mobile); announcement bar; "Want a film like this?" button under every film.
- **Exit-intent prompt** once per session (desktop: cursor leaves the window; mobile: after reading most of a page).
- **Meta Pixel** (`2142663756311688`) events: PageView, ViewContent (film plays), InitiateCheckout (form start/date check), CustomizeProduct (quiz), Schedule (Calendly), Contact (call/text/email), Lead (inquiry sent).

## Also included

All article and location URLs match the current live site, so existing Google rankings carry over. `blog.html` redirects to `journal.html`. SEO titles, descriptions, canonical URLs, Open Graph tags, LocalBusiness and BlogPosting schema, `sitemap.xml` and `robots.txt` are generated.

## Editing

Pages live in `src/pages/`, articles in `src/posts/` (JSON), and the shared header, footer, films, reviews, quiz questions and contact details are at the top of `build.py`. The announcement bar text (Now booking 2027 & 2028 weddings) is in `header()`. After editing, run:

```sh
python3 build.py
```

Styles are in `assets/css/site.css` (colour and type tokens at the top; `.section--ivory` switches a section to the light theme) and behaviour is in `assets/js/site.js`.

To preview locally: `python3 -m http.server 8000`, then open http://localhost:8000.
