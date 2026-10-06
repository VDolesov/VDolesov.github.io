import html
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
APP = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(APP, "build"))
from data import EXTRA, pretty

BRAND = "Мир Сладостей"
CATALOG = json.load(open(os.path.join(APP, "build", "catalog.json"), encoding="utf-8"))
SECTIONS = {s["slug"]: s["title"] for s in CATALOG["sections"]}
PRODUCTS = {i["id"]: dict(i, title=pretty(i["name"], i["section"])) for i in CATALOG["items"]}
PRODUCTS.update({i["id"]: dict(i, title=i["name"]) for i in EXTRA})

SECTION_TEXT = {
    "torty": "Праздничные торты собственного производства в Саратове: бисквит, крем, свежие ягоды. Предзаказ от 24 часов.",
    "pirogi": "Пироги с мясом, рыбой, капустой и ягодами, осетинские пироги и караваи собственной выпечки в Саратове.",
    "vypechka": "Свежая выпечка из слоёного и дрожжевого теста: слойки, самса, струдели. Выпекаем каждый день.",
    "pirozhnye_i_deserty": "Порционные пирожные и десерты собственного производства — к чаю и на праздничный стол.",
    "pechene": "Печенье собственной выпечки — к чаю, кофе и в подарок.",
    "salaty": "Готовые салаты для домашнего обеда и праздничного стола, небольшими партиями.",
    "vtorye_blyuda": "Горячие блюда собственного производства: остаётся разогреть и подать к столу.",
    "polufabrikaty": "Домашние пельмени, манты и вареники ручной лепки для быстрого ужина.",
    "napitki": "Морсы и компоты собственного производства — к выпечке, обеду и празднику.",
}

PAGE_TEXT = {
    "/": "Торты, пироги, выпечка и кулинария собственного производства в Саратове. Семь фирменных магазинов, "
         "самовывоз и доставка по городу.",
    "/catalog/": "Каталог «Мир Сладостей»: торты, пироги, выпечка, десерты, печенье, салаты, горячее, "
                 "полуфабрикаты и напитки собственного производства.",
    "/basket/": "Корзина и оформление заказа: самовывоз из магазинов «Мир Сладостей» или доставка по Саратову.",
    "/auth/": "Личный кабинет покупателя «Мир Сладостей».",
    "/search/": "Поиск по каталогу «Мир Сладостей».",
    "/sale/": "Акции и специальные предложения «Мир Сладостей».",
    "/contacts/": "Контакты «Мир Сладостей»: телефоны, почта, адрес производства и семь фирменных магазинов в Саратове.",
    "/contacts/stores/": "Адреса, телефоны и режим работы фирменных магазинов «Мир Сладостей» в Саратове.",
    "/company/": "«Мир Сладостей» — кондитерское и кулинарное производство в Саратове.",
    "/company/docs/": "Декларации о соответствии на продукцию «Мир Сладостей».",
    "/company/reviews/": "Отзывы покупателей о продукции «Мир Сладостей».",
    "/company/vacancy/": "Вакансии кондитерского производства «Мир Сладостей» в Саратове.",
    "/company/agreement/": "Политика конфиденциальности сайта «Мир Сладостей».",
    "/company/personal-data/": "Положение о защите персональных данных пользователей сайта «Мир Сладостей».",
    "/help/": "Как оформить заказ на сайте «Мир Сладостей»: корзина, звонок менеджера, самовывоз и доставка по Саратову.",
    "/help/delivery/": "Доставка по Саратову на следующий день с 8:00 до 15:00, бесплатно от 3000 ₽; самовывоз "
                       "из фирменных магазинов.",
    "/help/payment/": "Способы оплаты заказа на сайте «Мир Сладостей»: наличные, карта МИР, безналичный расчёт; реквизиты компании.",
    "/info/": "Справочная информация для покупателей «Мир Сладостей».",
    "/info/faq/": "Ответы на частые вопросы о заказе, доставке и оплате на сайте «Мир Сладостей».",
}

PAGE_NAMES = [
    ("Соглашение на обработку персональных данных", "Политика конфиденциальности"),
    ("Лицензии и сертификаты", "Документы"),
    ("Вопрос-ответ", "Вопросы и ответы"),
    ("«МИР СЛАДОСТЕЙ»", "«Мир Сладостей»"),
]

POLICY_PAGES = {
    "/company/agreement/": "Политика конфиденциальности",
    "/company/personal-data/": "Положение о защите персональных данных",
}
_HOME_ONLY = re.compile(r'(<div class="breadcrumbs__item) cat_last(" id="bx_breadcrumb_0".*?<meta itemprop="position" content="1"></a></div>)(</div>)', re.S)

TITLES = [
    (r"Купить (.+?) в Саратове - " + BRAND, r"\1 — " + BRAND),
    (BRAND + " - Изготовление тортов и пирожных в Саратове", BRAND + " — изготовление тортов и пирожных в Саратове"),
    (" - " + BRAND, " — " + BRAND),
]

PAGE_TOP = (
    '<div class="top-block-wrapper">\n<section class="page-top maxwidth-theme ">\n<div class="topic"><div class="topic__inner">'
    '<div class="topic__heading"><h1 id="pagetitle">{title}</h1></div></div></div>\n'
    '<div id="navigation"><div class="breadcrumbs swipeignore" itemscope="" '
    'itemtype="http://schema.org/BreadcrumbList">{crumbs}</div></div>\n</section>\n</div>\n'
)
CRUMB = (
    '<div class="breadcrumbs__item" itemprop="itemListElement" itemscope itemtype="http://schema.org/ListItem">'
    '<a class="breadcrumbs__link" href="{href}" title="{name}" itemprop="item"><span itemprop="name" '
    'class="breadcrumbs__item-name font_xs">{name}</span><meta itemprop="position" content="{pos}"></a></div>'
    '<span class="breadcrumbs__separator">&mdash;</span>'
)
LAST_CRUMB = (
    '<span class="breadcrumbs__item" itemprop="itemListElement" itemscope itemtype="http://schema.org/ListItem">'
    '<link href="{href}" itemprop="item" /><span><span itemprop="name" class="breadcrumbs__item-name font_xs">{name}'
    '</span><meta itemprop="position" content="{pos}"></span></span>'
)


def variants(raw):
    forms = {raw} if '"' in raw else {raw, f'"{raw}"'}
    out = set()
    for form in forms:
        out |= {form, form.replace('"', "&quot;"), form.replace('"', '\\"')}
    return out


def build_renames():
    pairs = [(form, p["title"]) for p in PRODUCTS.values() if p["name"] != p["title"] for form in variants(p["name"])]
    return sorted(pairs, key=lambda pair: -len(pair[0]))


PRODUCT_NAMES = build_renames()
SECTION_NAMES = [(re.compile(r"(?<![А-ЯЁA-Z])" + re.escape(title.upper()) + r"(?![А-ЯЁA-Z])"), title)
                 for title in sorted(SECTIONS.values(), key=len, reverse=True)]


def set_meta(html_text, text):
    value = html.escape(text, quote=True)
    html_text = re.sub(r'(<meta name="description" content=")[^"]*(")', lambda m: m.group(1) + value + m.group(2), html_text)
    return re.sub(r'(<meta property="og:description" content=")[^"]*(")', lambda m: m.group(1) + value + m.group(2), html_text)


def page_text(path):
    match = re.fullmatch(r"/catalog/([a-z_]+)/(\d+)/", path)
    if match and match.group(2) in PRODUCTS:
        p = PRODUCTS[match.group(2)]
        price = f"{p['price']:,}".replace(",", " ")
        lead = f"{p['title']} — {price} ₽/{p['unit']}."
        return f"{lead} {p['composition'].rstrip('.')}." if p.get("composition") else lead
    match = re.fullmatch(r"/catalog/([a-z_]+)/", path)
    if match and match.group(1) in SECTION_TEXT:
        return SECTION_TEXT[match.group(1)]
    return PAGE_TEXT.get(path)


def store_name(html_text):
    match = re.search(r'<div class="address">\s*<div class="title[^"]*">Адрес</div>\s*<div class="value darken">([^<]+)</div>', html_text)
    return match.group(1).replace("г. Саратов, ", "").strip() if match else None


def add_page_top(html_text, title, crumbs):
    if 'id="pagetitle"' in html_text:
        return html_text
    items = "".join(CRUMB.format(href=href, name=name, pos=i + 1) for i, (href, name) in enumerate(crumbs[:-1]))
    href, name = crumbs[-1]
    items += LAST_CRUMB.format(href=href, name=name, pos=len(crumbs))
    block = PAGE_TOP.format(title=html.escape(title, quote=False), crumbs=items)
    return html_text.replace('<div class="wraps hover_shine" id="content">',
                             '<div class="wraps hover_shine" id="content">\n' + block, 1)


def name_stores(html_text, path):
    if path == "/contacts/stores/":
        crumbs = [("/", "Главная"), ("/contacts/", "Контакты"), (path, "Магазины")]
        return add_page_top(html_text, "Магазины", crumbs)
    if not re.fullmatch(r"/contacts/stores/\d+/", path):
        return html_text
    name = store_name(html_text)
    if not name:
        return html_text
    html_text = re.sub(r"<title>[^<]*</title>", f"<title>{html.escape(name, quote=False)} — {BRAND}</title>", html_text, count=1)
    html_text = re.sub(r'(<meta property="og:title" content=")[^"]*(")',
                       lambda m: m.group(1) + html.escape(name, quote=True) + " — " + BRAND + m.group(2), html_text)
    html_text = set_meta(html_text, f"{name}: адрес, телефон и режим работы магазина «{BRAND}».")
    crumbs = [("/", "Главная"), ("/contacts/", "Контакты"), ("/contacts/stores/", "Магазины"), (path, name)]
    return add_page_top(html_text, name, crumbs)


def complete_crumbs(html_text, path):
    if path not in POLICY_PAGES:
        return html_text
    last = '<span class="breadcrumbs__separator">&mdash;</span>' + LAST_CRUMB.format(href=path, name=POLICY_PAGES[path], pos=2)
    return _HOME_ONLY.sub(lambda m: m.group(1) + m.group(2) + last + m.group(3), html_text, count=1)


def name_pages(html_text, path):
    for old, new in PRODUCT_NAMES:
        html_text = html_text.replace(old, new)
    for pattern, title in SECTION_NAMES:
        html_text = pattern.sub(title, html_text)
    for old, new in PAGE_NAMES:
        html_text = html_text.replace(old, new)
    for pattern, new in TITLES:
        html_text = re.sub(pattern, new, html_text)
    if path == "/company/reviews/":
        html_text = html_text.replace("Оставить свой отзыв — ", "Отзывы — ")
        html_text = html_text.replace('<h1 id="pagetitle">Оставить свой отзыв</h1>', '<h1 id="pagetitle">Отзывы</h1>')
        html_text = html_text.replace("'TITLE':'Оставить свой отзыв'", "'TITLE':'Отзывы'")
    html_text = html_text.replace('title="Помощь"', 'title="Как купить"').replace('font_xs">Помощь<', 'font_xs">Как купить<')
    if path == "/help/":
        html_text = html_text.replace("<title>Помощь — ", "<title>Как купить — ")
        html_text = html_text.replace('content="Помощь — ', 'content="Как купить — ')
        html_text = html_text.replace('<h1 id="pagetitle">Помощь</h1>', '<h1 id="pagetitle">Как купить</h1>')
        html_text = html_text.replace("'TITLE':'Помощь'", "'TITLE':'Как купить'")
    html_text = name_stores(html_text, path)
    html_text = complete_crumbs(html_text, path)
    text = page_text(path)
    return set_meta(html_text, text) if text else html_text
