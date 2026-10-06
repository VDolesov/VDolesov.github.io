# Connecting the storefront to the backend

Notes for the developer who wires this markup to the backend of mirsladostey164.ru (1C-Bitrix, Aspro Max template).

The storefront is a set of static pages: HTML, one CSS set and one JS file. There is no bundler and no framework, so the pages open straight from disk. This is deliberate: plain markup is easier to move into a Bitrix template than a build pipeline.

## Key points

1. **URLs match the live site.** A catalog section is `/catalog/torty/`, a product is `/catalog/torty/747/`, where `747` is the infoblock element ID. Links, bookmarks and search positions are kept.
2. **Data lives in one file**, `products.js`. It is the only place the storefront reads products from; replace it with server data and the shop works.
3. **Nothing is sent to a server.** Forms build the request text and copy it to the clipboard. Every point that needs a server is listed below.

## Pages

| URL | Content | Bitrix component |
| --- | --- | --- |
| `/` | Home: showcase, catalog, delivery, FAQ | `catalog.section` or custom |
| `/catalog/` | All sections and the full list | `catalog.sections.list` |
| `/catalog/<section>/` | Section (9 of them, same slugs as now) | `catalog.section` |
| `/catalog/<section>/<id>/` | Product card | `catalog.element` |
| `/basket/` | Cart page | `sale.basket.basket` |
| `/order/` | Checkout | `sale.order.ajax` |
| `/search/` | Search, reads `?q=` | `search.page` |
| `/favorites/` | Saved products | `catalog.product.subscribe` or custom |
| `/personal/` | Account sign-in (placeholder) | `main.register`, `system.auth.form` |
| `/company/` + `reviews`, `vacancy`, `licenses`, `docs` | Company | static pages |
| `/help/` + `payment`, `delivery`, `warranty` | How to buy | static pages |
| `/sale/`, `/services/`, `/info/`, `/contacts/` | Offers, services, info, contacts | infoblocks |

73 pages in total, 44 of them product cards.

## Data format

`products.js` declares one global object:

```js
window.MS_DATA = {
  SECTIONS,
  SECTION_MAP,
  PRODUCTS,
  FEATURED_IDS,
  MIN_ORDER: 800, FREE_DELIVERY: 3000, DELIVERY_FEE: 150
};
```

`SECTIONS` holds slug, title, short title and description; `SECTION_MAP` is the same list keyed by slug; `FEATURED_IDS` is the "popular first" order.

A product:

```js
{
  id: "747",
  section: "torty",
  name: "Торт «Прага»",
  price: 1300,
  unit: "шт",
  article: "10007",
  badge: "Хит",
  weight: "1200 г",
  composition: "Мука пшеничная в/с, сахар-песок, …",
  energy: "391,55 ккал / 1369 кДж",
  nutrition: "Белков 6,0 г, жиров 20,77 г, углеводов 45,96 г",
  image: "/assets/products/747-v7.webp",
  url: "/catalog/torty/747/"
}
```

`id` is the infoblock element ID, `section` the section code, `price` a plain number, `badge` may be empty.

`sectionTitle`, `availability`, `description` and `url` are filled in at the end of `products.js`; when data comes from the server, repeat that logic or send the fields ready.

**Switching to server data:** render the same object from the PHP template or fetch it from a JSON endpoint and assign `window.MS_DATA` before `app.js` loads. Nothing else in the markup changes.

## Where a server is needed

| What | Where in code | Now | Needed |
| --- | --- | --- | --- |
| Checkout | `app.js`, `[data-order-form]` | text to clipboard | order creation, payment |
| Custom cake request | `[data-custom-form]` | same | e-mail or CRM |
| Call back | `[data-callback-form]` | notice only | request to a manager |
| Product review | `[data-review-form]` | notice only | moderation and output |
| Account sign-in | `[data-login-form]` | placeholder | authorization |
| Cart and favourites | `localStorage`, keys `mir-sladostey-cart-v3`, `-favorites-v3` | browser | server-side cart |
| Search | client-side filter | by name and composition | server search |
| Stock and prices | static `products.js` | catalog snapshot | live stock |

The markup does not need changes: every such point has a `data-` attribute to hook into.

## Keep when porting

- **Unit next to the price**: some items are sold by the kilogram, some by the piece; the card and the cart show it.
- **800 ₽ minimum order**: the checkout button stays disabled below it and shows how much to add.
- **Delivery**: 150 ₽ within Saratov, free from 3 000 ₽; the values live in `MS_DATA`.
- **Pre-order**: cakes and pies show "pre-order 24 hours ahead".

## Snapshot

This version is a static snapshot exported from history by `skin/export_version.py`; the scripts that generated it are retired. Product photos come from the sources in `build/`: `build/photos/` (site originals, 1100 px), `build/sources/studio/` (studio shots of the pies) and `build/sources/legacy/` (archive shots, 350 px, used where nothing else exists).

The strawberry cake has no photo in any source and shows a placeholder. Both kinds of vareniki share one shot, as on the live site.

## Not in this version

Left out on purpose, so as not to invent business rules: product comparison, coupons and discounts, newsletter, price and property filters, pagination (a "show more" button instead), online payment.
