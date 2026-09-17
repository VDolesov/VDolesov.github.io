# Skin for the live site

A new look for mirsladostey164.ru without touching markup or logic. The site stays on 1C-Bitrix with the Aspro Max template; only the visual layer changes — colours, type, backgrounds, cards, layout inside existing blocks.

One file to install, one line to roll back.

Live demo: https://vdolesov.github.io/ — the whole site with the skin: home, every catalog section and product, cart, contacts, company and help pages.

## Direction

Near-black cocoa, caramel gold as the only accent, Prata for headings, Golos Text for copy, square corners, no frames.

| | Before | After |
| --- | --- | --- |
| Scheme | light | dark: ground `#120b08`, text `#f3e8d8` |
| Accent | `#f3103a` | `#d6a459`, hover `#e6b96f` |
| Headings | Montserrat | Prata, digits in Golos Text via a `unicode-range` face |
| Copy | Montserrat | Golos Text 16 px |
| Buttons | red, rounded, white caption | gold, square, dark spaced small caps |
| Product cards | white with border | frameless, photo on a dark scene, gold price |
| Product photos | on white | series v9 — cutout on a dark scene matching the page |
| Labels | blue / green / purple | gold "hit", outlined "new", brown "recommended" |
| Logo | dark red | gold |
| Home sections | 90×90 carousel | one row of square tiles with captions |
| Home hits | four narrow cards | four frameless cards, tabs in Prata |
| About block | text + video block | gold-framed band with a production photo |
| Header | plain | sticky, plus a section navigation strip (`nav.js`) |
| Product page | 450 px photo, narrow specs column | full-column photo, specs under the buy block |
| Hero | stock photo | three full-bleed slides (cakes, pies, cakes to order), copy on the dark left half |
| Section and product names | all caps | sentence case via CSS |
| Cart | Bitrix module | demo only: client-side cart and checkout (`cart.js`) |

## Install

1. Copy `skin.css` and the `fonts` folder next to it into the template, e.g. `/bitrix/templates/aspro_max/css/skin.css` and `/bitrix/templates/aspro_max/css/fonts/golos-text-latin.woff2` (the digits face, referenced relatively).
2. Include it **last**, after the template styles:

   ```php
   $APPLICATION->SetAdditionalCSS(SITE_TEMPLATE_PATH . '/css/skin.css');
   ```

   or in `<head>`:

   ```html
   <link rel="stylesheet" href="/bitrix/templates/aspro_max/css/skin.css">
   ```

3. Clear the site cache: *Settings → Autocaching → Clear cache files*.

Order matters: the skin must load after the template CSS.

## How it is built

`build_skin.py` fetches every Aspro CSS bundle the pages reference (template, page, default, component bundles; cached in `skin/cache/`) and makes two passes:

1. every rule using the brand red is rewritten with the gold accent;
2. every rule of the light scheme — dark text, white fills, light borders and shadows — is rewritten dark, keeping the original selectors so specificity matches and the later file wins.

A manual layer follows: type, cards, header, grid, hero, home blocks, cart; the final block is the direction itself.

```
python skin/build_skin.py          # rebuild skin.css
python skin/build_site.py          # crawl the live site and rebuild all pages
python skin/build_site.py contacts/stores company/agreement   # rebuild only the given pages
python skin/build_site.py --stamp  # restamp skin version, photo series, hero files and copy into built pages
python skin/build_cart_data.py     # rebuild cart data (products, sections)
python skin/hero_choc.py           # rebuild hero-bg.jpg
```

`build_site.py` crawls the live site by internal links (81 pages) and writes each page under its own URL. Links stay relative, template assets load from the original domain. Links the demo cannot serve are aliased (`ALIAS`: the account page to `/auth/`, the two policy pages under `/company/`), the Metrika counter is stripped so demo visits do not land in the live site's statistics. Photo series, hero files and slide copy are set in `build_demo.py` (`SERIES`, `BANNER`, `BANNER_COPY`, `IMAGES`); `--stamp` applies them to already built pages.

## Photos

Series v9: every catalog item is a neural cutout placed on the same dark scene — cocoa ground, warm light from above, a pool of light on the table, a contact shadow. Before placing, `natural()` in `build/photos_v9.py` calms the source shots (the originals are over-sharpened and over-saturated): halos softened, saturation pulled down with extra weight on oranges, highlights rolled off, blacks lifted a touch. `python build/photos_v9.py` rebuilds the whole series and dispatches plated items and AI renders itself. The three Ossetian pies (801–803), the strawberry cake (752, no photo on the live site) and the about-block photo are AI-generated (FLUX, raw renders in `build/sources/ai/`, composed by `build/pies_ai.py`) and graded onto the same scene. Files live in `../assets/products/` and are named by product id: `747-v9.webp` (1024) and `747-v9-640.webp`.

Salads, ready meals and semi-finished products are re-plated: the food is masked out of its plastic tray and composed into a dark ceramic bowl or plate before it goes onto the scene (`build/plates.py` next to `photos_v9.py`).

On the live site upload them into the product cards; the file name is the element id. The demo swaps them into the built pages at build time (`swap_photos` in `build_demo.py`), so no white originals flash before the dark ones.

## Hero

Three slides, each one full-bleed photo (2400x1060) with the subject on the right and the left half darkened for the copy: `hero-bg.jpg` (cherry chocolate cake), `hero-2.jpg` (meat pie), `hero-3.jpg` (chocolate layer cake with berries and a cut slice). `skin/hero_choc.py` builds them from `assets/hero-noir.webp` and the AI renders in `build/sources/ai/` (`SLIDES` at the top of the script; the last value is the photo height as a fraction of the canvas, the rest is filled by extending the photo edges so wide renders keep the whole subject inside the cropped 1920px view). The template's product image on the right is hidden by the skin (`td.img`).

The demo clones the template's single slide three times at build time (`SLIDES` in `build_demo.py` — file, label, title, text, button, link) and switches the theme's slider settings to fade / 8 s in `demo.js`; on phones the slideshow is off and slides swipe. On the live site these are three banner elements plus the theme's "big banner" settings.

## Home sections

The template renders sections as an Owl carousel with 90×90 images. The skin lays it out as one row of square tiles (nine on desktop, four on tablet, three on phone), captions under the photos, arrows hidden. The carousel script keeps running; only its layout is overridden.

Section images on the site are 90×90 and will look soft on 140–215 px tiles — upload larger images (800 px+) or raise the preview size in the component settings. The demo uses one product photo per section:

```
torty                749   pirogi   801   vypechka        746
pirozhnye_i_deserty  757   pechene  753   salaty          765
vtorye_blyuda        770   polufabrikaty 760   napitki    763
```

## Product page

- gallery fills its column and is squared; thumbnails are 84 px squares;
- columns split 54 / 46 in favour of the photo;
- price and buy block on top, specs below through a gold line;
- specs are two columns with hairlines; on phones the label moves above the value;
- bottom tabs are spaced small caps, the active one underlined in gold;
- empty ratings, the duplicate side block and the empty "you may also like" block are hidden.

## Demo cart

The demo is static, so the cart lives in the browser: `cart.js` intercepts the template's "add to cart" buttons, keeps the cart in localStorage, renders `/basket/` (list, quantities, total, checkout form, confirmation with an order number) and offers to send the order by e-mail. Product data is `cart-data.js`, generated from `build/catalog.json`. `nav.js` adds the section navigation strip under the header from the same data.

`motion.js` adds the reveal-on-scroll animation (IntersectionObserver, honours `prefers-reduced-motion`) and the hero parallax: on pointer devices from 768px up it moves each slide's photo into its own layer (`.ms-hero-par` from `data-bg`), shifts photo and copy in opposite directions after the mouse, adds a warm light spot under the cursor and a slow 18s zoom on the active slide; the hover and hero entrance animations are pure CSS in `skin.css`. Favourites (the heart on cards) live in localStorage next to the cart and show up as a «Отложенные» list on `/basket/#delayed`.

`search.js` answers the header search (`/catalog/?q=` and `/search/?q=`) from the same product data: name, section and composition, with a crude Russian stem. `demo.js` catches the template's popup forms (call back, subscribe, question, account, quick view): quick view opens the product page, the rest show a note with the phones instead of a request the static demo cannot send.

On the live site none of these scripts is needed — Bitrix handles the cart, favourites, orders, search and forms; `motion.js` is the one optional extra (drop it next to `skin.css` and include it after the template scripts). The `ms-*` styles in `skin.css` do not interfere.

## Weight and caching

Pages are served by GitHub Pages: gzip, `Cache-Control: max-age=600`; `skin.css` and the scripts carry a content hash in the query string, so a new build is picked up at once and an unchanged one stays cached. Product cards use the 640 px variant with a 1024 px `srcset` for retina, `loading="lazy"` and `decoding="async"`; the first hero image is preloaded. The demo sets no cookies of its own (cart and favourites are in localStorage); the Metrika counter and the Bitrix session beacon are stripped so demo visits do not reach the live site's statistics. Template CSS/JS still come from mirsladostey164.ru with that server's caching.

## Out of scope

The skin does not change markup, so it cannot change page content, block order or the product card composition. Layout inside existing elements is fair game: catalog grid, sticky header, buy button always visible.
