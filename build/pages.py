# -*- coding: utf-8 -*-
"""Страницы витрины: главная, каталог, карточки товаров, корзина, оформление,
поиск, отложенные и текстовые разделы. Запускается из build/build_all.py.
"""
import json
import os

from build import (ADDRESS, DIALOGS, EMAIL, PHONE_MAIN, PHONE_MAIN_HREF,
                   PHONE_SECOND, PHONE_SECOND_HREF, SECTION_LEAD, SHOPS,
                   breadcrumbs, esc, money, page, page_hero, write)
from data import EXTRA, SECTIONS as SECTION_ROWS, pretty

HERE = os.path.dirname(os.path.abspath(__file__))

SECTIONS = [{"slug": s[0], "title": s[1], "short": s[2], "description": s[3]}
            for s in SECTION_ROWS]


def load_items():
    catalog = json.load(open(os.path.join(HERE, "catalog.json"), encoding="utf-8"))
    items = []
    for it in catalog["items"]:
        items.append({
            "id": it["id"], "section": it["section"],
            "name": pretty(it["name"], it["section"]),
            "price": it["price"], "unit": it["unit"] or "шт",
            "article": it["article"], "badge": (it["badges"] or [""])[0],
            "weight": it["weight"], "composition": it["composition"],
            "energy": it["energy"], "nutrition": it["nutrition"], "note": "",
        })
    for extra in EXTRA:
        row = dict(extra)
        row["badge"] = (row.pop("badges") or [""])[0]
        items.append(row)
    order = {s["slug"]: i for i, s in enumerate(SECTIONS)}
    items.sort(key=lambda x: (order.get(x["section"], 99), int(x["id"])))
    for it in items:
        it["url"] = f'/catalog/{it["section"]}/{it["id"]}/'
        it["image"] = f'/assets/products/{it["id"]}-v7.webp'
        it["availability"] = ("Предзаказ от 24 часов"
                              if it["section"] in ("torty", "pirogi")
                              else "Наличие уточнит менеджер")
    return items


# ------------------------------------------------------------ общие фрагменты

def catalog_toolbar(placeholder, chips=True):
    chip_html = ""
    if chips:
        buttons = "".join(
            f'<button class="filter-chip" type="button" data-filter="{s["slug"]}">{esc(s["short"])}</button>'
            for s in SECTIONS)
        chip_html = f"""      <div class="filter-row shell" aria-label="Фильтр разделов">
        <button class="filter-chip is-active" type="button" data-filter="all">Все</button>
{buttons}
      </div>
"""
    return f"""      <div class="catalog-toolbar shell">
        <label class="catalog-search">
          <span class="sr-only">Поиск по каталогу</span>
          <svg viewBox="0 0 24 24" aria-hidden="true"><circle cx="11" cy="11" r="7"/><path d="m16 16 5 5"/></svg>
          <input type="search" placeholder="{esc(placeholder)}" data-catalog-search>
        </label>
        <label class="catalog-sort">
          <span>Сортировка</span>
          <select data-catalog-sort>
            <option value="featured">Сначала популярные</option>
            <option value="price-asc">Сначала дешевле</option>
            <option value="price-desc">Сначала дороже</option>
            <option value="name">По названию</option>
          </select>
        </label>
      </div>

{chip_html}      <div class="catalog-status shell">
        <span data-catalog-count>0 товаров</span>
        <button type="button" data-clear-filters hidden>Сбросить фильтры</button>
      </div>
      <div class="product-grid shell" id="productGrid" aria-live="polite"></div>
      <div class="catalog__more shell">
        <button class="button button--outline" type="button" data-load-more>Показать ещё</button>
      </div>
"""


def section_tiles():
    tiles = []
    for i, s in enumerate(SECTIONS):
        dark = " category-tile--dark" if s["slug"] in ("pirozhnye_i_deserty", "polufabrikaty") else ""
        tiles.append(f"""        <a class="category-tile{dark} reveal" href="/catalog/{s['slug']}/">
          <span class="category-tile__number">{i + 1:02d}</span>
          <span class="category-tile__name">{esc(s['short'])}</span>
          <span class="category-tile__caption" data-section-count="{s['slug']}"></span>
        </a>""")
    return "\n".join(tiles)


DELIVERY_BLOCK = """    <section class="delivery" id="delivery" aria-labelledby="deliveryTitle">
      <div class="delivery__header shell reveal">
        <p class="eyebrow">От цеха до вашего стола</p>
        <h2 id="deliveryTitle">Доставляем<br><em>бережно</em></h2>
      </div>
      <div class="delivery__grid shell">
        <article class="delivery-card delivery-card--wide reveal">
          <span class="delivery-card__number">01</span>
          <svg viewBox="0 0 120 70" aria-hidden="true"><path d="M8 50h65V19H28L8 35v15Zm65-21h21l17 17v4H73V29ZM28 19v16H8M31 58a9 9 0 1 1-18 0 9 9 0 0 1 18 0Zm67 0a9 9 0 1 1-18 0 9 9 0 0 1 18 0Z"/></svg>
          <h3>На следующий день</h3>
          <p>Доставляем с 08:00 до 15:00. Оператор согласует точное время в течение двух часов после оформления заказа.</p>
        </article>
        <article class="delivery-card reveal"><span class="delivery-card__number">02</span><strong>800 ₽</strong><h3>Минимальный заказ</h3><p>Приём заявок ежедневно с 9:00 до 20:00, по субботам — с 9:00 до 12:00.</p></article>
        <article class="delivery-card reveal"><span class="delivery-card__number">03</span><strong>3 000 ₽</strong><h3>Бесплатная доставка</h3><p>В радиусе 3 км от центра — бесплатно, далее по Саратову — 150 ₽. От 3 000 ₽ доставка бесплатна.</p></article>
      </div>
      <div class="pickup-note shell reveal"><span>Самовывоз</span><p>""" + " · ".join(a for a, _ in SHOPS) + """</p></div>
    </section>
"""

CUSTOM_BLOCK = """    <section class="custom" id="custom" aria-labelledby="customTitle">
      <div class="custom__rings" aria-hidden="true"><i></i><i></i><i></i></div>
      <div class="custom__content shell reveal">
        <p class="eyebrow">Индивидуальный заказ</p>
        <h2 id="customTitle">Торт, которого<br>ещё <em>не существовало</em></h2>
        <p>Расскажите о поводе, любимом вкусе и количестве гостей. Мы уточним детали и предложим оформление.</p>
        <button class="button button--accent" type="button" data-open-custom>
          Обсудить торт
          <svg viewBox="0 0 24 24" aria-hidden="true"><path d="M5 12h14M14 7l5 5-5 5"/></svg>
        </button>
      </div>
      <div class="custom__cake reveal" aria-hidden="true">
        <div class="cake-sculpture"><span></span><span></span><span></span><span></span><i></i></div>
      </div>
    </section>
"""

FAQ_BLOCK = """    <section class="faq" id="faq" aria-labelledby="faqTitle">
      <div class="faq__intro shell reveal">
        <p class="eyebrow">Перед заказом</p>
        <h2 id="faqTitle">Важные<br><em>детали</em></h2>
        <p>Коротко о подтверждении, индивидуальных заказах и составе. Если ситуация особенная, лучше сразу рассказать о ней менеджеру.</p>
      </div>
      <div class="faq__list shell reveal">
        <details><summary>Когда заказ считается оформленным?<span aria-hidden="true"></span></summary><p>После заявки менеджер проверит наличие, согласует дату, время и итоговую стоимость. Заказ считается подтверждённым после разговора с менеджером.</p></details>
        <details><summary>За сколько заказывать праздничный торт?<span aria-hidden="true"></span></summary><p>Чем сложнее оформление и больше вес, тем раньше стоит обсудить заказ. Назовите дату, количество гостей и желаемый вкус — менеджер предложит доступный срок.</p></details>
        <details><summary>Можно ли изменить состав?<span aria-hidden="true"></span></summary><p>Пожелания можно указать в комментарии. Возможность замены ингредиентов зависит от рецептуры и подтверждается кондитером до оформления.</p></details>
        <details><summary>Как уточнить аллергены и хранение?<span aria-hidden="true"></span></summary><p>Сообщите менеджеру об аллергиях и ограничениях заранее. Точный состав, срок и температуру хранения конкретного изделия уточняйте при подтверждении заказа.</p></details>
      </div>
    </section>
"""


# -------------------------------------------------------------------- страницы

def build_home():
    main = f"""  <main id="main">
    <section class="hero" id="top" aria-labelledby="heroTitle">
      <div class="hero__media" aria-hidden="true"></div>
      <div class="hero__shade" aria-hidden="true"></div>
      <div class="hero__content shell">
        <p class="eyebrow hero__eyebrow">Кондитерская и кулинария · Саратов</p>
        <h1 id="heroTitle">Сладкое<br><em>искусство</em></h1>
        <p class="hero__description">Торты, пироги, свежая выпечка и готовая кулинария собственного производства. Доставка по Саратову и самовывоз из семи фирменных магазинов.</p>
        <div class="hero__actions">
          <a class="button button--light" href="#catalog">
            Перейти в каталог
            <svg viewBox="0 0 24 24" aria-hidden="true"><path d="M5 12h14M14 7l5 5-5 5"/></svg>
          </a>
          <button class="text-button" type="button" data-open-custom>Заказать особенный торт</button>
        </div>
      </div>
      <div class="hero__meta shell" aria-label="Преимущества">
        <div><strong data-total-count>50+</strong><span>позиций в каталоге</span></div>
        <div><strong>С 1998</strong><span>готовим в Саратове</span></div>
        <div><strong>7</strong><span>фирменных магазинов</span></div>
      </div>
      <a class="hero__scroll" href="#catalog" aria-label="Листать к каталогу"><span></span></a>
    </section>

    <section class="catalog" id="catalog" aria-labelledby="catalogTitle">
      <div class="catalog__heading shell reveal">
        <div>
          <p class="eyebrow">Полный ассортимент</p>
          <h2 id="catalogTitle">Каталог</h2>
        </div>
        <p>Ассортимент собственного производства. Наличие и ближайшую дату изготовления подтверждает менеджер после оформления.</p>
      </div>
{catalog_toolbar("Найти торт, пирог или десерт")}    </section>

    <section class="manifesto" aria-label="О качестве">
      <div class="manifesto__ticker" aria-hidden="true">
        <div>Слои · Текстуры · Время · Рецептура · Слои · Текстуры · Время · Рецептура ·</div>
      </div>
      <div class="manifesto__inner shell">
        <div class="manifesto__quote reveal">
          <span class="manifesto__index">01 / 04</span>
          <blockquote>«Вкус начинается не с украшения, а с точности каждого слоя»</blockquote>
        </div>
        <div class="manifesto__facts reveal">
          <article><span>01</span><h3>Своя рецептура</h3><p>Готовим на производстве в Саратове и контролируем каждый этап.</p></article>
          <article><span>02</span><h3>Свежий выпуск</h3><p>Не держим изделия неделями: формируем партии под текущий спрос.</p></article>
          <article><span>03</span><h3>Бережная доставка</h3><p>Фиксируем упаковку и доставляем по Саратову и Энгельсу.</p></article>
        </div>
      </div>
    </section>

{CUSTOM_BLOCK}
{DELIVERY_BLOCK}
{FAQ_BLOCK}  </main>
"""
    write("index.html", page(
        "Мир сладостей — кондитерская и кулинария в Саратове",
        "Торты, пироги, свежая выпечка и готовая кулинария собственного производства в Саратове. Доставка и самовывоз из семи фирменных магазинов.",
        "/", main, SECTIONS, "/"))


def build_catalog_index():
    main = f"""  <main id="main">
{page_hero(breadcrumbs(("Главная", "/"), ("Каталог", "/catalog/")), "Полный ассортимент", "Каталог",
           "Девять разделов собственного производства. Наличие и ближайшую дату изготовления подтверждает менеджер после оформления.")}
    <section class="collections" aria-label="Разделы каталога">
      <div class="section-rail shell-wide">
{section_tiles()}
      </div>
    </section>

    <section class="catalog" id="catalog" aria-label="Все товары" style="padding-top:80px">
{catalog_toolbar("Найти торт, пирог или десерт")}    </section>
  </main>
"""
    write("catalog/index.html", page(
        "Каталог — Мир сладостей",
        "Полный каталог изделий собственного производства: торты, пироги, выпечка, десерты, печенье, салаты, горячее, полуфабрикаты и напитки.",
        "/catalog/", main, SECTIONS, "/catalog/"))


def build_section(section, items):
    slug, title = section["slug"], section["title"]
    count = len([i for i in items if i["section"] == slug])
    links = ['      <div class="category-links shell" aria-label="Разделы каталога">',
             '        <a class="filter-chip" href="/catalog/">Весь каталог</a>']
    for s in SECTIONS:
        current = " is-current" if s["slug"] == slug else ""
        links.append(f'        <a class="filter-chip{current}" href="/catalog/{s["slug"]}/">{esc(s["short"])}</a>')
    links.append("      </div>")

    main = f"""  <main id="main">
{page_hero(breadcrumbs(("Главная", "/"), ("Каталог", "/catalog/"), (title, "")),
           f"Каталог · {count} позиций", esc(title), SECTION_LEAD.get(slug, ""))}
{chr(10).join(links)}

    <section class="catalog" id="catalog" aria-label="Товары раздела" style="padding-top:60px">
{catalog_toolbar(f"Найти в разделе «{title}»", chips=False)}    </section>
  </main>
"""
    write(f"catalog/{slug}/index.html", page(
        f"{title} — купить в Саратове | Мир сладостей",
        SECTION_LEAD.get(slug, title), f"/catalog/{slug}/", main, SECTIONS,
        f"/catalog/{slug}/", body_attrs=f' data-section="{slug}"'))


def build_product(item, items):
    section = next(s for s in SECTIONS if s["slug"] == item["section"])
    same = [i for i in items if i["section"] == item["section"] and i["id"] != item["id"]][:4]
    related = "".join(
        f"""          <a class="related-card" href="{i['url']}">
            <span class="related-card__image"><img src="{i['image'].replace('.webp', '-640.webp')}" alt="{esc(i['name'])}" width="640" height="640" loading="lazy" decoding="async"></span>
            <span class="related-card__name">{esc(i['name'])}</span>
            <span class="related-card__price">{money(i['price'])} <small>за {esc(i['unit'])}</small></span>
          </a>""" for i in same)

    specs = []
    if item["weight"]:
        specs.append(("Вес", item["weight"]))
    if item["composition"]:
        specs.append(("Состав", item["composition"]))
    if item["energy"]:
        specs.append(("Энергетическая ценность на 100 г", item["energy"]))
    if item["nutrition"]:
        specs.append(("Пищевая ценность на 100 г", item["nutrition"]))
    specs_html = "".join(
        f"<div><dt>{esc(k)}</dt><dd>{esc(v)}</dd></div>" for k, v in specs)
    badge_html = (f'<span class="product-page__badge">{esc(item["badge"])}</span>'
                  if item["badge"] else "")
    note = f'<p class="product-page__note">{esc(item["note"])}</p>' if item.get("note") else ""

    main = f"""  <main id="main">
    <section class="product-page" id="top">
      <div class="shell">
        {breadcrumbs(("Главная", "/"), ("Каталог", "/catalog/"),
                     (section["title"], f'/catalog/{section["slug"]}/'), (item["name"], ""))}
        <div class="product-layout">
          <div class="product-gallery">
            {badge_html}
            <img src="{item['image']}" srcset="{item['image'].replace('.webp', '-640.webp')} 640w, {item['image']} 1024w" sizes="(max-width: 900px) 92vw, 46vw" alt="{esc(item['name'])}" width="1024" height="1024" decoding="async">
          </div>
          <div class="product-info">
            <p class="eyebrow">{esc(section['title'])} · Арт. {esc(item['article'])}</p>
            <h1>{esc(item['name'])}</h1>
            {note}
            <div class="product-price"><strong>{money(item['price'])}</strong><span>за {esc(item['unit'])}</span></div>
            <p class="product-availability">{esc(item['availability'])}</p>

            <div class="product-actions">
              <div class="qty-control" data-qty-control>
                <button type="button" data-qty-minus aria-label="Меньше">−</button>
                <input type="number" min="1" max="99" value="1" data-qty-input aria-label="Количество">
                <button type="button" data-qty-plus aria-label="Больше">+</button>
              </div>
              <button class="button button--accent" type="button" data-add="{item['id']}" data-add-qty>В корзину</button>
              <button class="icon-button icon-button--fav" type="button" data-favorite="{item['id']}" aria-label="Отложить">
                <svg viewBox="0 0 24 24" aria-hidden="true"><path d="M20.8 4.6a5.4 5.4 0 0 0-7.6 0L12 5.8l-1.2-1.2a5.4 5.4 0 0 0-7.6 7.6L12 21l8.8-8.8a5.4 5.4 0 0 0 0-7.6Z"/></svg>
              </button>
            </div>
            <button class="text-button" type="button" data-open-callback>Купить в один клик</button>

            <ul class="product-perks">
              <li><strong>Самовывоз</strong>из семи фирменных магазинов — бесплатно</li>
              <li><strong>Доставка</strong>на следующий день, с 8:00 до 15:00</li>
              <li><strong>От 3 000 ₽</strong>доставка по Саратову бесплатно</li>
            </ul>
          </div>
        </div>

        <div class="product-details">
          <div class="product-specs">
            <h2>Характеристики</h2>
            <dl>{specs_html or "<div><dt>Уточняется</dt><dd>Состав и вес подтвердит менеджер при оформлении заказа.</dd></div>"}</dl>
            <p class="product-page__legal">Цена действительна для интернет-магазина и может отличаться от цен в розничных магазинах. Об аллергиях и пищевых ограничениях сообщите до оформления заказа.</p>
          </div>
          <aside class="product-side">
            <h3>Как купить</h3>
            <p>Добавьте товар в корзину и оформите заявку. Менеджер подтвердит наличие, итоговую стоимость и время получения.</p>
            <a class="arrow-link" href="/help/">Условия заказа <span>→</span></a>
            <h3>Оплата</h3>
            <p>Наличными, банковской картой или безналичным расчётом.</p>
            <a class="arrow-link" href="/help/payment/">Способы оплаты <span>→</span></a>
          </aside>
        </div>

        <section class="related" aria-labelledby="relatedTitle">
          <div class="section-heading">
            <h2 id="relatedTitle">Из этого же раздела</h2>
            <a class="arrow-link" href="/catalog/{section['slug']}/">Весь раздел <span>→</span></a>
          </div>
          <div class="related-grid">
{related}
          </div>
        </section>
      </div>
    </section>
  </main>
"""
    description = (item["note"] or
                   f'{item["name"]} — {money(item["price"])} за {item["unit"]}. '
                   f'{item["composition"][:110]}' if item["composition"] else item["name"])
    write(f"catalog/{item['section']}/{item['id']}/index.html", page(
        f'{item["name"]} — купить в Саратове | Мир сладостей',
        description, item["url"], main, SECTIONS, f'/catalog/{item["section"]}/'))


# ------------------------------------------------- корзина, оформление, поиск

def build_basket():
    main = f"""  <main id="main">
{page_hero(breadcrumbs(("Главная", "/"), ("Корзина", "")), "Ваш заказ", "Корзина",
           "Проверьте состав заказа. Итоговую стоимость и время получения подтверждает менеджер.")}
    <section class="basket-page">
      <div class="shell">
        <div class="basket-layout" data-basket-layout hidden>
          <div class="basket-list" data-basket-items></div>
          <aside class="basket-summary">
            <h2>Итого</h2>
            <div class="basket-summary__row"><span>Товары</span><strong data-basket-total>0 ₽</strong></div>
            <div class="basket-summary__row"><span>Доставка</span><span data-basket-delivery>—</span></div>
            <div class="cart-delivery-progress" data-delivery-progress>
              <div><span data-progress-label>До минимальной суммы заказа</span><strong data-progress-value>800 ₽</strong></div>
              <i><span data-progress-bar></span></i>
            </div>
            <a class="button button--accent" href="/order/" data-basket-checkout>Перейти к оформлению</a>
            <small>Минимальная сумма заказа — 800 ₽. Доставка по Саратову 150 ₽, от 3 000 ₽ бесплатно.</small>
          </aside>
        </div>
        <div class="basket-empty" data-basket-empty>
          <span>0</span>
          <h2>Корзина пуста</h2>
          <p>Загляните в каталог — там торты, пироги, выпечка и готовая кулинария собственного производства.</p>
          <a class="button button--outline" href="/catalog/">Перейти в каталог</a>
        </div>
      </div>
    </section>
  </main>
"""
    write("basket/index.html", page(
        "Корзина — Мир сладостей", "Состав вашего заказа в интернет-магазине «Мир сладостей».",
        "/basket/", main, SECTIONS, "/basket/"))


def build_order():
    pickup_options = "".join(f"<option>{esc(a)}</option>" for a, _ in SHOPS)
    main = f"""  <main id="main">
{page_hero(breadcrumbs(("Главная", "/"), ("Корзина", "/basket/"), ("Оформление", "")),
           "Оформление", "Получение<br><em>заказа</em>",
           "После заявки менеджер подтвердит наличие, итоговую стоимость и точное время получения.")}
    <section class="order-page">
      <div class="shell">
        <form class="order-form" data-order-form>
          <div class="order-form__fields">
            <h2>Контактные данные</h2>
            <div class="field-row">
              <label>Ваше имя<input name="name" required autocomplete="name" placeholder="Анна"></label>
              <label>Телефон<input name="phone" required inputmode="tel" autocomplete="tel" minlength="18" placeholder="+7 (900) 000-00-00"></label>
            </div>

            <h2>Получение</h2>
            <div class="field-row">
              <label>Способ<select name="delivery-method" data-delivery-method><option>Доставка</option><option>Самовывоз</option></select></label>
              <label>Желаемая дата<input name="date" required type="date"></label>
            </div>
            <label data-address-field>Адрес в Саратове<input name="address" autocomplete="street-address" placeholder="Улица, дом, квартира, подъезд"></label>
            <label data-pickup-field hidden>Пункт самовывоза<select name="pickup"><option value="">Выберите магазин</option>{pickup_options}</select></label>

            <h2>Оплата</h2>
            <label>Способ оплаты<select name="payment"><option>Банковской картой</option><option>Наличными при получении</option><option>Безналичный расчёт</option></select></label>
            <label>Комментарий<textarea name="comment" rows="3" placeholder="Желаемое время или детали заказа"></textarea></label>
            <label class="legal-check"><input type="checkbox" required><span>Согласен на обработку персональных данных для оформления заказа</span></label>
          </div>

          <aside class="order-form__summary">
            <h2>Ваш заказ</h2>
            <div class="order-summary" data-order-summary></div>
            <p class="cart-delivery-line" data-cart-delivery></p>
            <button class="button button--accent" type="submit">Подготовить заказ для менеджера</button>
            <p class="form-note">Заявка будет скопирована в буфер обмена. Для подтверждения позвоните <a href="tel:{PHONE_MAIN_HREF}">{PHONE_MAIN}</a>.</p>
          </aside>
        </form>
      </div>
    </section>
  </main>
"""
    write("order/index.html", page(
        "Оформление заказа — Мир сладостей", "Оформление заказа: доставка по Саратову или самовывоз из фирменных магазинов.",
        "/order/", main, SECTIONS, "/basket/"))


def build_search():
    main = f"""  <main id="main">
{page_hero(breadcrumbs(("Главная", "/"), ("Поиск", "")), "По каталогу", "Поиск",
           "Введите название изделия — например, «вишня», «слойка» или «осетинский».")}
    <section class="catalog" id="catalog" aria-label="Результаты поиска" style="padding-top:60px">
{catalog_toolbar("Название изделия", chips=False)}    </section>
  </main>
"""
    write("search/index.html", page(
        "Поиск по каталогу — Мир сладостей", "Поиск изделий в каталоге «Мир сладостей».",
        "/search/", main, SECTIONS, "/search/", body_attrs=' data-search-page'))


def build_favorites():
    main = f"""  <main id="main">
{page_hero(breadcrumbs(("Главная", "/"), ("Отложенные", "")), "Личная подборка", "Отложенные",
           "Товары, которые вы отметили сердечком. Список хранится в этом браузере.")}
    <section class="catalog" id="catalog" aria-label="Отложенные товары" style="padding-top:60px">
{catalog_toolbar("Найти среди отложенных", chips=False)}    </section>
  </main>
"""
    write("favorites/index.html", page(
        "Отложенные товары — Мир сладостей", "Отложенные позиции каталога «Мир сладостей».",
        "/favorites/", main, SECTIONS, "/favorites/", body_attrs=' data-favorites-page'))
