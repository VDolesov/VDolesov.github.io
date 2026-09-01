# -*- coding: utf-8 -*-
"""Сборка статических страниц витрины.

Структура адресов повторяет mirsladostey164.ru — это нужно, чтобы вёрстку
можно было положить на существующий бэкенд без потери ссылок и позиций
в поиске. Данные берутся из build/catalog.json.
"""
import json
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
APP = os.path.dirname(HERE)
ASSETS_VERSION = "10"

PHONE_MAIN = "+7 (8452) 47-35-69"
PHONE_MAIN_HREF = "+78452473569"
PHONE_SECOND = "+7 (8452) 21-28-45"
PHONE_SECOND_HREF = "+78452212845"
EMAIL = "mirslad49@mail.ru"
ADDRESS = "г. Саратов, ул. Бахметьевская, 49"

SHOPS = [
    ("Бахметьевская, 49", "Производство и фирменный магазин"),
    ("Чернышевского, 144", "Фирменный магазин"),
    ("Советская, 30", "Фирменный магазин"),
    ("Большая Казачья, 17/39", "Фирменный магазин"),
    ("Тархова, 29А/1", "Фирменный магазин"),
    ("Одесская, 20А", "Фирменный магазин"),
    ("Приовражная, кольцо НИИ", "Фирменный магазин"),
]

SECTION_LEAD = {
    "torty": "Праздничные торты собственного производства. Предзаказ от 24 часов, оформление согласуем с кондитером.",
    "pirogi": "Домашние пироги с щедрой начинкой, включая коллекцию осетинских. Для семейного стола, офиса и праздника.",
    "vypechka": "Свежая выпечка из слоёного и дрожжевого теста. Выпускаем ежедневно.",
    "pirozhnye_i_deserty": "Порционные десерты с выразительной текстурой и аккуратной подачей.",
    "pechene": "Печенье собственной выпечки — к чаю, кофе и в подарочный набор.",
    "salaty": "Готовые салаты для домашнего обеда и праздничного стола. Небольшие партии.",
    "vtorye_blyuda": "Горячие блюда собственного производства. Остаётся разогреть и подать к столу.",
    "polufabrikaty": "Домашние полуфабрикаты для быстрого ужина — удобно хранить и легко приготовить.",
    "napitki": "Фруктово-ягодные напитки в удобном формате — к выпечке, обеду или праздничному заказу.",
}


# --------------------------------------------------------------------- утилиты

def esc(text):
    return (str(text).replace("&", "&amp;").replace("<", "&lt;")
            .replace(">", "&gt;").replace('"', "&quot;"))


def money(value):
    return f"{value:,}".replace(",", " ") + " ₽"


def write(path, content):
    full = os.path.join(APP, path)
    os.makedirs(os.path.dirname(full), exist_ok=True)
    with open(full, "w", encoding="utf-8", newline="\n") as f:
        f.write(content)


# ------------------------------------------------------------------- каркас

def head(title, description, canonical):
    v = ASSETS_VERSION
    return f"""<!doctype html>
<html lang="ru">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="theme-color" content="#100810">
  <meta name="description" content="{esc(description)}">
  <meta property="og:title" content="{esc(title)}">
  <meta property="og:description" content="{esc(description)}">
  <meta property="og:image" content="/assets/hero-noir-social.jpg">
  <link rel="canonical" href="https://mirsladostey164.ru{canonical}">
  <link rel="icon" href="/assets/logo-melnitsa.svg" type="image/svg+xml">
  <title>{esc(title)}</title>
  <link rel="stylesheet" href="/styles.css?v={v}">
  <link rel="stylesheet" href="/theme-noir.css?v={v}">
  <link rel="stylesheet" href="/pages.css?v={v}">
  <script src="/products.js?v={v}" defer></script>
  <script src="/app.js?v={v}" defer></script>
</head>"""


def nav_dropdown(title, href, items, active):
    """Пункт меню с выпадающим списком — как в верхнем меню оригинала."""
    links = "".join(
        f'<a href="{h}"{" class=&quot;is-current&quot;" if h == active else ""}>{esc(t)}</a>'
        for t, h in items)
    cls = " is-active" if active.startswith(href) else ""
    return f"""<div class="nav-group{cls}">
          <a class="nav-group__title" href="{href}">{esc(title)}<i aria-hidden="true"></i></a>
          <div class="nav-group__menu">{links}</div>
        </div>"""


def header(sections, active=""):
    catalog_items = [(s["title"], f'/catalog/{s["slug"]}/') for s in sections]
    company_items = [("О компании", "/company/"), ("Отзывы", "/company/reviews/"),
                     ("Вакансии", "/company/vacancy/"), ("Лицензии", "/company/licenses/"),
                     ("Документы", "/company/docs/")]
    help_items = [("Как купить", "/help/"), ("Условия оплаты", "/help/payment/"),
                  ("Условия доставки", "/help/delivery/"), ("Гарантия на товар", "/help/warranty/")]

    def link(title, href):
        cls = ' class="is-active"' if active == href else ""
        return f'<a href="{href}"{cls}>{esc(title)}</a>'

    mobile_sections = "".join(
        f'<a href="/catalog/{s["slug"]}/">{esc(s["title"])}</a>' for s in sections)

    return f"""  <a class="skip-link" href="#main">Перейти к содержимому</a>
  <div class="scroll-progress" aria-hidden="true"><i data-scroll-progress></i></div>

  <div class="service-line" aria-label="Информация о доставке">
    <span>Заказ от 800 ₽ · доставка по Саратову</span>
    <span class="service-line__dot" aria-hidden="true"></span>
    <span>Бесплатно от 3 000 ₽ · самовывоз из 7 магазинов</span>
    <a href="tel:{PHONE_MAIN_HREF}">{PHONE_MAIN}</a>
  </div>

  <header class="site-header" id="siteHeader">
    <a class="brand" href="/" aria-label="Мир сладостей — на главную">
      <span class="brand__mark brand__mark--mill" aria-hidden="true"></span>
      <span class="brand__text">Мир сладостей</span>
    </a>

    <nav class="desktop-nav" aria-label="Основная навигация">
      {nav_dropdown("Каталог", "/catalog/", catalog_items, active)}
      {link("Акции", "/sale/")}
      {link("Услуги", "/services/")}
      {nav_dropdown("Компания", "/company/", company_items, active)}
      {nav_dropdown("Как купить", "/help/", help_items, active)}
      {link("Контакты", "/contacts/")}
    </nav>

    <div class="header-actions">
      <a class="header-phone" href="tel:{PHONE_MAIN_HREF}">
        <span>{PHONE_MAIN}</span>
      </a>
      <a class="icon-link" href="/search/" aria-label="Поиск по каталогу">
        <svg viewBox="0 0 24 24" aria-hidden="true"><circle cx="11" cy="11" r="7"/><path d="m16 16 5 5"/></svg>
      </a>
      <a class="icon-link" href="/favorites/" aria-label="Отложенные товары">
        <svg viewBox="0 0 24 24" aria-hidden="true"><path d="M20.8 4.6a5.4 5.4 0 0 0-7.6 0L12 5.8l-1.2-1.2a5.4 5.4 0 0 0-7.6 7.6L12 21l8.8-8.8a5.4 5.4 0 0 0 0-7.6Z"/></svg>
        <span class="icon-link__count" data-favorites-count>0</span>
      </a>
      <button class="cart-button" type="button" data-open-cart aria-label="Открыть корзину" aria-controls="cartDrawer" aria-expanded="false">
        <svg viewBox="0 0 24 24" aria-hidden="true"><path d="M4 7h16l-1.4 13H5.4L4 7Zm4 0V5a4 4 0 0 1 8 0v2"/></svg>
        <span class="cart-button__count" data-cart-count>0</span>
      </button>
      <button class="menu-button" type="button" aria-expanded="false" aria-controls="mobileMenu" data-menu-toggle>
        <span class="sr-only">Открыть меню</span>
        <i></i><i></i>
      </button>
    </div>

    <nav class="mobile-menu" id="mobileMenu" aria-label="Мобильная навигация">
      <a href="/catalog/">Каталог</a>
      {mobile_sections}
      <a href="/sale/">Акции</a>
      <a href="/services/">Услуги</a>
      <a href="/company/">Компания</a>
      <a href="/help/">Как купить</a>
      <a href="/contacts/">Контакты</a>
      <a href="/personal/">Личный кабинет</a>
      <a href="tel:{PHONE_MAIN_HREF}">{PHONE_MAIN}</a>
    </nav>
  </header>
"""


def footer(sections):
    catalog_links = "".join(
        f'<a href="/catalog/{s["slug"]}/">{esc(s["title"])}</a>' for s in sections[:6])
    return f"""  <footer class="site-footer">
    <div class="site-footer__top shell">
      <a class="brand brand--footer" href="/">
        <span class="brand__mark brand__mark--mill" aria-hidden="true"></span>
        <span class="brand__text">Мир сладостей</span>
      </a>
      <p>Кондитерские изделия и кулинария<br>в Саратове и Энгельсе.</p>
      <div class="footer-phones">
        <a class="footer-phone" href="tel:{PHONE_MAIN_HREF}">{PHONE_MAIN}</a>
        <a href="tel:{PHONE_SECOND_HREF}">{PHONE_SECOND}</a>
      </div>
    </div>
    <div class="site-footer__grid shell">
      <div><h3>Каталог</h3>{catalog_links}<a href="/catalog/">Весь каталог</a></div>
      <div><h3>Покупателям</h3><a href="/help/">Как купить</a><a href="/help/payment/">Условия оплаты</a><a href="/help/delivery/">Условия доставки</a><a href="/help/warranty/">Гарантия на товар</a><a href="/basket/">Корзина</a></div>
      <div><h3>Компания</h3><a href="/company/">О компании</a><a href="/company/reviews/">Отзывы</a><a href="/company/vacancy/">Вакансии</a><a href="/company/licenses/">Лицензии</a><a href="/company/docs/">Документы</a></div>
      <div class="footer-note"><h3>Контакты</h3><p>{ADDRESS}</p><a href="mailto:{EMAIL}">{EMAIL}</a><p class="footer-note__hint">Наличие, состав и ближайшую дату изготовления подтвердит менеджер.</p></div>
    </div>
    <div class="site-footer__bottom shell">
      <span>© <span data-year></span> ООО «Мир сладостей»</span>
      <span>ИНН 6454104523 · ОГРН 1156451019867</span>
      <a href="#top">Наверх ↑</a>
    </div>
  </footer>
"""


DIALOGS = """  <div class="page-overlay" data-overlay></div>

  <aside class="cart-drawer" id="cartDrawer" aria-labelledby="cartTitle" aria-hidden="true" data-cart-drawer>
    <div class="drawer-head"><div><p class="eyebrow">Ваш заказ</p><h2 id="cartTitle">Корзина</h2></div><button class="icon-button" type="button" data-close-cart aria-label="Закрыть корзину">×</button></div>
    <div class="cart-delivery-progress" data-delivery-progress><div><span data-progress-label>До минимальной суммы заказа</span><strong data-progress-value>800 ₽</strong></div><i><span data-progress-bar></span></i></div>
    <div class="cart-items" data-cart-items></div>
    <div class="cart-empty" data-cart-empty><span>0</span><h3>Здесь пока пусто</h3><p>Добавьте что-нибудь к чаю — или к большому событию.</p><a class="button button--outline" href="/catalog/">Перейти в каталог</a></div>
    <div class="cart-footer" data-cart-footer hidden><div><span>Товары</span><strong data-cart-total>0 ₽</strong></div><p class="cart-delivery-line" data-cart-delivery></p><a class="button button--accent" href="/basket/">Перейти в корзину</a><small>Наличие, итоговую стоимость и время подтверждает менеджер.</small></div>
  </aside>

  <dialog class="product-dialog" data-product-dialog>
    <button class="dialog-close" type="button" data-close-dialog aria-label="Закрыть">×</button>
    <div class="product-dialog__image"><img src="" alt="" data-dialog-image><span data-dialog-category></span></div>
    <div class="product-dialog__content">
      <p class="eyebrow">Быстрый просмотр</p>
      <h2 data-dialog-name></h2>
      <p class="product-dialog__description" data-dialog-description></p>
      <div class="product-dialog__tags"><span>Свежая партия</span><span>Собственное производство</span></div>
      <div class="product-dialog__buy"><div><strong data-dialog-price></strong><span data-dialog-unit></span></div><label>Количество<input type="number" min="1" max="20" value="1" data-dialog-qty></label></div>
      <button class="button button--accent" type="button" data-dialog-add>Добавить в корзину</button>
      <a class="text-link" href="#" data-dialog-link>Открыть страницу товара →</a>
    </div>
  </dialog>

  <dialog class="form-dialog form-dialog--custom" data-custom-dialog>
    <button class="dialog-close" type="button" data-close-dialog aria-label="Закрыть">×</button>
    <div class="form-dialog__intro"><p class="eyebrow">Торт на заказ</p><h2>Расскажите о событии</h2><p>Менеджер свяжется, уточнит вкус, вес, оформление и рассчитает стоимость.</p></div>
    <form data-custom-form>
      <label>Ваше имя<input name="name" required autocomplete="name" placeholder="Алексей"></label>
      <label>Телефон<input name="phone" required inputmode="tel" autocomplete="tel" minlength="18" placeholder="+7 (900) 000-00-00"></label>
      <label>Дата события<input name="date" required type="date"></label>
      <label>Количество гостей<select name="guests"><option>До 10</option><option>10–20</option><option>20–40</option><option>Больше 40</option></select></label>
      <label class="form-dialog__wide">Пожелания<textarea name="idea" required rows="4" placeholder="Вкус, цвет, надпись, характер события"></textarea></label>
      <label class="form-dialog__wide">Ссылка на референс<input name="reference" type="url" placeholder="https://..."></label>
      <label class="legal-check form-dialog__wide"><input type="checkbox" required><span>Согласен на обработку персональных данных</span></label>
      <button class="button button--accent form-dialog__wide" type="submit">Подготовить заявку</button>
    </form>
  </dialog>

  <dialog class="form-dialog" data-callback-dialog>
    <button class="dialog-close" type="button" data-close-dialog aria-label="Закрыть">×</button>
    <div class="form-dialog__intro"><p class="eyebrow">Обратный звонок</p><h2>Перезвоним вам</h2><p>Оставьте телефон — менеджер свяжется в рабочее время.</p></div>
    <form data-callback-form>
      <label>Ваше имя<input name="name" required autocomplete="name" placeholder="Анна"></label>
      <label>Телефон<input name="phone" required inputmode="tel" autocomplete="tel" minlength="18" placeholder="+7 (900) 000-00-00"></label>
      <label class="form-dialog__wide">Вопрос<textarea name="question" rows="3" placeholder="Коротко о заказе"></textarea></label>
      <label class="legal-check form-dialog__wide"><input type="checkbox" required><span>Согласен на обработку персональных данных</span></label>
      <button class="button button--accent form-dialog__wide" type="submit">Отправить заявку</button>
    </form>
  </dialog>

  <div class="toast" role="status" aria-live="polite" data-toast></div>
"""


def page(title, description, canonical, main, sections, active="", body_attrs=""):
    return (head(title, description, canonical)
            + f'\n<body class="theme-noir"{body_attrs}>\n'
            + header(sections, active) + "\n" + main + "\n"
            + footer(sections) + "\n" + DIALOGS + "</body>\n</html>\n")


def breadcrumbs(*crumbs):
    parts = []
    for text, href in crumbs[:-1]:
        parts.append(f'<a href="{href}">{esc(text)}</a>')
        parts.append('<span aria-hidden="true">/</span>')
    parts.append(f"<span>{esc(crumbs[-1][0])}</span>")
    return '<nav class="breadcrumbs" aria-label="Хлебные крошки">' + "".join(parts) + "</nav>"


def page_hero(crumbs, eyebrow, title_html, lead=""):
    lead_html = f'\n        <p class="page-hero__lead">{lead}</p>' if lead else ""
    return f"""    <section class="page-hero" id="top">
      <div class="page-hero__media" aria-hidden="true"></div>
      <div class="page-hero__shade" aria-hidden="true"></div>
      <div class="shell">
        {crumbs}
        <p class="eyebrow page-hero__eyebrow">{esc(eyebrow)}</p>
        <h1>{title_html}</h1>{lead_html}
      </div>
    </section>
"""
