# Skin

A new look for mirsladostey164.ru without touching the template logic. The site stays on 1C-Bitrix with the Aspro Max template; the skin changes colours, type, backgrounds, cards and layout inside existing blocks. One stylesheet to install, one line to roll back.

Live demo: https://vdolesov.github.io/

## Direction

Near-black cocoa, caramel gold as the only accent, Prata for headings, Golos Text for copy, square corners.

| | Template | Skin |
| --- | --- | --- |
| Scheme | light | dark: ground `#120b08`, text `#f3e8d8` |
| Accent | `#f3103a` | `#d6a459`, hover `#e6b96f` |
| Headings | Montserrat | Prata, digits in Golos Text via a `unicode-range` face |
| Copy | Montserrat | Golos Text 16 px |
| Buttons | red, rounded | gold, square, spaced small caps |
| Product cards | white with a border | frameless, photo on a light cream scene, gold price |
| Labels | blue / green / purple | gold "hit", outlined "new", brown "recommended" |
| Header | plain | sticky, with a section strip under the logo row |
| Hero | stock photo | three full-bleed slides with copy on the dark left half |
| Home sections | 90×90 carousel | one row of square tiles with captions |
| Product page | 450 px photo | full-column photo, specs under the buy block |
| Names | all caps | sentence case |

## Install on the live site

1. Copy `skin.css` and the `fonts/` folder next to it into the template, e.g. `/bitrix/templates/aspro_max/css/skin.css` and `/bitrix/templates/aspro_max/css/fonts/`. Font paths in the stylesheet are relative.
2. Include it **last**, after the template styles:

   ```php
   $APPLICATION->SetAdditionalCSS(SITE_TEMPLATE_PATH . '/css/skin.css');
   ```

3. Clear the site cache: *Settings → Autocaching → Clear cache files*.

`motion.js` (reveal on scroll, hero parallax) is optional; include it after the template scripts. The other scripts exist only for the static demo: on the live site Bitrix handles the cart, search and forms.

## Build

```
python skin/build_skin.py                  # rebuild skin.css
python skin/build_site.py                  # crawl the live site and rebuild every page
python skin/build_site.py contacts/stores  # rebuild the given pages only
python skin/build_site.py --stamp          # re-apply skin version and content rules to built pages
python skin/build_cart_data.py             # rebuild cart-data.js from build/catalog.json
python skin/add_pies.py                    # Ossetian pie pages 801–803
python skin/hero_choc.py                   # rebuild the hero slides
```

`build_skin.py` collects every Aspro stylesheet the pages reference (cached in `skin/cache/`), rewrites each rule that uses the brand red with the gold accent and each rule of the light scheme dark, keeping the original selectors so the later file wins, then appends the manual layer: type, cards, header, hero, home blocks, product page, cart, drawer, forms.

`build_site.py` crawls the live site by internal links and writes each page under its own URL. Fetching needs a Russian IP: the live site does not answer foreign addresses. For every page it:

- inlines lazily loaded template blocks and swaps product photos for the series in `assets/products/`;
- clones the hero into three slides and applies the copy rules (`SLIDES`, `BANNER_COPY` in `build_demo.py`) and the "Important details" block (`FAQ`);
- serves template stylesheets from `vendor/css/` and self-hosted fonts from `skin/fonts/`, preloading the two above-the-fold faces; strips the Metrika counter, the session beacon and unused font links;
- removes blocks the demo does not use (`strip.py`): warranty, licenses, brands, services and blog pages and links, the footer help column, saved items, the home tizers and about block; the account page shows a demo note instead of the login form;
- aligns legal and order copy (`legal.py`): order acceptance, payment methods, refusal and quality questions, requisites, seller line in the footer, consent checkbox under reviews;
- names pages (`naming.py`): product and section names in sentence case with «» quotes, titles as «Name — Мир Сладостей», a description for every page, a heading and breadcrumbs on the store pages;
- links `skin.css` and the demo scripts with a content hash in the query string.

`--stamp` runs the same rules over already built pages without fetching anything, so it is the command to use after changing the skin, the scripts or the copy.

## Photos

Products use series v9: `{id}-v9.webp` (1024 px), `{id}-v9-640.webp` and `{id}-v9-2048.webp`. `python build/photos_light.py` renders them on the light cream scene of the July storefront: cutouts of the site originals (`build/photos/`), studio shots of the pies (`build/sources/studio/`), an archive shot where nothing else exists (`build/sources/legacy/`), plated salads and hot dishes (`build/plates.py`) and AI renders for the Ossetian pies and the strawberry cake (`build/sources/ai/`). Small sources are upscaled with FSRCNN x3 (`build/models/`). `python build/pies_ai.py` renders the contacts photo `assets/about.jpg`.

Upload the photos into the product cards on the live site; the file name is the element id.

## Hero

Three WebP slides, 2400×1060, subject on the right and the left half darkened for the copy: `hero-bg.webp`, `hero-2.webp`, `hero-3.webp`. `hero_choc.py` builds them from `assets/hero-noir.webp` and the AI renders in `build/sources/ai/` (`SLIDES` at the top of the script sets the source, grade, fit, vertical position and shift). The demo clones the template's single slide three times; on the live site these are three banner elements.

## Demo scripts

- `cart.js` — cart in localStorage: side drawer, `/basket/` page with the free delivery and minimum order bars, checkout form for pickup or delivery within Saratov, confirmation with an order number that can be sent by e-mail.
- `cart-data.js` — products, sections and photo ids, generated by `build_cart_data.py`.
- `nav.js` — the section strip under the logo row.
- `search.js` — header search over names, sections and composition.
- `demo.js` — template pop-up forms show a demo note with the phones, quick view opens the product page, one-time cookie notice.
- `motion.js` — reveal on scroll and the hero parallax, honouring `prefers-reduced-motion`.

## Caching

GitHub Pages serves everything with gzip and `max-age=600`; the skin and scripts carry a content hash, so a new build is picked up at once. Product cards use the 640 px photo with a 1024 px `srcset`, lazy loading and async decoding; the first hero slide is preloaded. Template scripts still load from mirsladostey164.ru.
