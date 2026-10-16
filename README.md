# Jack Albert Weddings — Website

A multi-page, mobile-first website for **Jack Albert Weddings**, an Ottawa Valley wedding filmmaker.
It is a plain static site: no framework, no build step needed to host it.

**Deploy the `site/` folder** to any static host (Cloudflare Pages, Netlify, Vercel, GitHub Pages, cPanel).

## Pages

| Page | File |
| --- | --- |
| Home | `site/index.html` |
| Films | `site/films.html` |
| The Experience | `site/experience.html` |
| Investment & FAQ | `site/investment.html` |
| About | `site/about.html` |
| Journal (15 articles, filterable) | `site/journal.html` + one file per article |
| Contact / inquiry form | `site/contact.html` |
| Ottawa & Pembroke pages (SEO) | `site/ottawa-wedding-videographer.html`, `site/pembroke-wedding-videographer.html` |
| Privacy, 404 | `site/privacy.html`, `site/404.html` |

All article and location URLs match the current live site, so existing Google rankings carry over.
`blog.html` redirects to `journal.html`. `sitemap.xml` and `robots.txt` are generated.

## What's wired up

- **Inquiry form** posts to the existing Formspree endpoint (`xaqgvyod`) with an in-page thank-you state. Links like `contact.html?collection=classic-collection` preselect a collection.
- **Calendly** "book a call" link, **click-to-call** `(613) 621-0458`, email, Instagram and YouTube.
- **Films** open in a privacy-enhanced YouTube lightbox; previews play on hover (desktop) and autoplay muted when on screen.
- **Meta Pixel** (`2142663756311688`) is kept, and a `Lead` event fires on a successful inquiry.
- **SEO**: per-page titles and descriptions, canonical URLs, Open Graph tags, LocalBusiness and BlogPosting schema.
- **Mobile**: full-screen menu, sticky "Check your date" and call bar, a separate lighter hero video for phones, and support for reduced motion.

## Editing

Pages live in `src/pages/`, articles in `src/posts/` (JSON), and the shared header, footer, films, reviews and contact details are at the top of `build.py`. After editing, run:

```sh
python3 build.py
```

Styles are in `site/assets/css/site.css` (colour and type tokens at the top) and behaviour is in `site/assets/js/site.js`.

To preview locally: `cd site && python3 -m http.server 8000`, then open http://localhost:8000.
