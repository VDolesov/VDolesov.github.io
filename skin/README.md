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
| Headings | Montserrat | Prata |
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
| Hero | stock photo | Schwarzwald cake under a light pool on cocoa |
| Section and product names | all caps | sentence case via CSS |
| Cart | Bitrix module | demo only: client-side cart and checkout (`cart.js`) |

## Install

1. Copy `skin.css` into the template, e.g. `/bitrix/templates/aspro_max/css/skin.css`.
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
python skin/build_site.py --stamp  # restamp skin version, photo series, hero files and copy into built pages
python skin/build_cart_data.py     # rebuild cart data (products, sections)
python skin/hero_choc.py           # rebuild hero-bg.jpg, hero-cake.webp, about.jpg
```

`build_site.py` crawls the live site by internal links (73 pages) and writes each page under its own URL. Links stay relative, template assets load from the original domain. Photo series, hero files and slide copy are set in `build_demo.py` (`SERIES`, `BANNER`, `BANNER_COPY`, `IMAGES`); `--stamp` applies them to already built pages.

## Photos

Series v9: every catalog item is a neural cutout placed on the same dark scene — cocoa ground, warm light from above, a pool of light on the table, a contact shadow. Ossetian pies shot at the bakery are composed on the same scene. Files live in `../assets/products/` and are named by product id: `747-v9.webp` (1024) and `747-v9-640.webp`.

Salads, ready meals and semi-finished products are re-plated: the food is masked out of its plastic tray and composed into a dark ceramic bowl or plate before it goes onto the scene (`build/plates.py` next to `photos_v9.py`).

On the live site upload them into the product cards; the file name is the element id. The demo swaps them in with a script.

## Hero

The slide is two images: a wide backdrop and a product on the right.

```
hero-bg.jpg      2400x1060   cocoa with a warm light pool on the right
hero-cake.webp   1308x880    Schwarzwald cake, transparent WebP, light pool and shadow baked in
```

Upload them into the banner element that currently holds `890366e70949176749ee46def14a193b.jpg` (backdrop) and `a76586772deb02b99d66c209bfda9c22.png` (product). Light and shadow are baked into the product image because the template moves the product as the viewport changes.

Slide copy used in the demo (set it in the slide settings):

```
label     Собственное производство
title     Прага. Шварцвальд. Сластёна.
text      Торты, пироги и десерты, которые мы печём сами. Заберите в одном из двух магазинов или закажите доставку по Саратову.
button    Выбрать торт
```

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

On the live site neither script is needed — Bitrix handles the cart and orders; the `ms-*` styles in `skin.css` do not interfere.

## Out of scope

The skin does not change markup, so it cannot change page content, block order or the product card composition. Layout inside existing elements is fair game: catalog grid, sticky header, buy button always visible.
