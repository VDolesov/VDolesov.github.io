# -*- coding: utf-8 -*-
"""Сборка skin.css — надстройки над текущим оформлением сайта.

Идея: вёрстка и логика сайта (1С-Битрикс, шаблон Aspro Максимум) остаются
как есть. Меняется только внешний слой — палитра, шрифты, фон, карточки.

Скрипт читает боевой CSS шаблона, находит все правила с фирменным красным
(#f3103a и его оттенками) и переписывает их новым цветом. Так покрываются
все места, где акцент используется, без ручного перебора селекторов.
Поверх добавляется небольшой ручной блок: типографика, фон, карточки.

    python skin/build_skin.py

Результат: skin/skin.css — один файл, который подключается последним.
"""
import os
import re
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
SITE = "https://www.mirsladostey164.ru"
CACHE = os.path.join(HERE, "aspro.css")
OUT = os.path.join(HERE, "skin.css")

# Текущая палитра шаблона → новая.
# Красный сохраняем как акцент, но берём винный оттенок: узнаваемость
# остаётся, агрессивная «распродажная» яркость уходит.
COLOR_MAP = {
    "#f3103a": "#8f1737",   # основной акцент
    "#f42d52": "#a8264a",   # наведение
    "#f30b36": "#8f1737",   # вариант основного
    "#e00a31": "#77122c",   # нажатие, тёмный вариант
    "#ff1441": "#a8264a",
    "#e5062d": "#77122c",
}

ACCENT = "#8f1737"
ACCENT_HOVER = "#a8264a"
INK = "#241a1a"
PAPER = "#faf6ef"        # тёплая бумага вместо белого
CARD = "#ffffff"
LINE = "rgba(36, 26, 26, .12)"
GOLD = "#b08b4f"


def fetch_css():
    """Боевой CSS шаблона: берём по ссылке с сайта, затем кэшируем."""
    if os.path.exists(CACHE):
        return open(CACHE, encoding="utf-8", errors="ignore").read()
    home = urllib.request.urlopen(
        urllib.request.Request(SITE, headers={"User-Agent": "Mozilla/5.0"}),
        timeout=40).read().decode("utf-8", "ignore")
    href = re.search(r'/bitrix/cache/css/s1/aspro_max/[^"]+\.css[^"]*', home).group(0)
    css = urllib.request.urlopen(
        urllib.request.Request(SITE + href, headers={"User-Agent": "Mozilla/5.0"}),
        timeout=90).read().decode("utf-8", "ignore")
    open(CACHE, "w", encoding="utf-8").write(css)
    return css


def recolor(css):
    """Правила с фирменным красным → те же селекторы с новым цветом."""
    pattern = re.compile(r"([^{}]+)\{([^{}]*)\}")
    targets = tuple(COLOR_MAP)
    rules = []
    for match in pattern.finditer(css):
        selector, body = match.group(1).strip(), match.group(2)
        if not any(color in body.lower() for color in targets):
            continue
        if selector.startswith("@"):
            continue

        kept = []
        for declaration in body.split(";"):
            if ":" not in declaration:
                continue
            prop, value = declaration.split(":", 1)
            low = value.lower()
            if not any(color in low for color in targets):
                continue
            for old, new in COLOR_MAP.items():
                value = re.sub(old, new, value, flags=re.I)
            kept.append(f"{prop.strip()}:{value.strip()}")
        if kept:
            selector = " ".join(selector.split())
            rules.append(f"{selector}{{{';'.join(kept)}}}")
    return rules


MANUAL = f"""
/* --- шрифты ------------------------------------------------------------ */
@import url("https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;500;600&display=swap");

body, .wrapper1 {{ background: {PAPER}; color: {INK}; }}

/* Заголовки: в шаблоне это не только h1-h6, но и .topic, .title_block и т.п.
   Поэтому перечисляем реальные классы и ставим приоритет явно. */
h1, h2, h3, h4, .h1, .h2, .h3, .h4,
.topic, .topic span, .title_block, .top_block .title, .section_title,
.front-block .title, .detail .element-title, .item-title, .item-title a,
.popup-window-titlebar, .basket-title, .page-top .topic {{
  font-family: "Playfair Display", Georgia, serif !important;
  font-weight: 500 !important;
  letter-spacing: -.015em;
  text-transform: none;
}}
.topic, .page-top .topic {{ font-size: clamp(28px, 3.2vw, 44px) !important; line-height: 1.12 !important; }}
h1 {{ font-size: clamp(30px, 3.4vw, 46px); line-height: 1.12; }}
h2 {{ font-size: clamp(25px, 2.6vw, 36px); line-height: 1.15; }}

/* --- шапка и подвал ---------------------------------------------------- */
.header_wrap .logo_and_menu-row,
.header-v2 .logo_and_menu-row,
.header_wrap .menu-row {{ background: #ffffff; }}
.header_wrap .top-block-item,
.header-v1 .line-row, .header_wrap .line-row {{
  color: rgba(255, 255, 255, .72); background: #1b1211;
}}
.header_wrap .line-row a {{ color: rgba(255, 255, 255, .82); }}
.footer_inner, .footer-block, footer.footer {{ background: #1b1211; color: rgba(255, 255, 255, .68); }}
.footer_inner a, footer.footer a {{ color: rgba(255, 255, 255, .78); }}
.footer_inner a:hover, footer.footer a:hover {{ color: {GOLD}; }}
.footer_inner .title, footer.footer .title {{ color: {GOLD}; letter-spacing: .1em; }}

/* --- кнопки ------------------------------------------------------------ */
.btn, .btn.btn-default, .btn.btn-lg, .btn.btn-sm, button.btn {{
  border-radius: 2px; letter-spacing: .04em; font-weight: 600;
  transition: background-color .2s ease, border-color .2s ease, color .2s ease;
}}
.btn.btn-default, .btn-primary {{ background-color: {ACCENT}; border-color: {ACCENT}; color: #fff; }}
.btn.btn-default:hover, .btn-primary:hover {{ background-color: {ACCENT_HOVER}; border-color: {ACCENT_HOVER}; }}
.btn.btn-transparent, .btn.btn-default.transparent {{ color: {ACCENT}; border-color: {ACCENT}; background: transparent; }}
.btn.btn-transparent:hover, .btn.btn-default.transparent:hover {{ color: #fff; background: {ACCENT}; }}

/* --- карточки товара --------------------------------------------------- */
.catalog_block .catalog_item_wrapp, .catalog_item_wrapp .catalog_item,
.item_block .catalog_item, .product-item-container {{
  background: {CARD};
  border: 1px solid {LINE};
  border-radius: 3px;
  transition: box-shadow .28s ease, transform .28s ease;
}}
.catalog_item_wrapp:hover .catalog_item, .item_block:hover .catalog_item {{
  box-shadow: 0 18px 40px rgba(36, 26, 26, .10);
  transform: translateY(-2px);
}}
.catalog_item .image_wrapper_block, .product-item-image-wrapper {{ background: #fdfbf7; }}
.catalog_item .item-title a, .product-item-title a {{
  font-family: "Playfair Display", Georgia, serif; font-size: 17px; letter-spacing: -.01em;
}}
.catalog_item .price, .price_matrix_wrapper .price, .product-item-price-current {{
  font-family: "Playfair Display", Georgia, serif; font-size: 22px; color: {INK};
}}
.stickers .sticker, .product-item-label-text, .sticker_wrapper .sticker {{
  border-radius: 2px; letter-spacing: .06em; text-transform: uppercase; font-size: 10px;
}}

/* --- витрина каталога --------------------------------------------------- */
.catalog_block .item_block, .catalog_block .catalog_item_wrapp {{ background: transparent; }}
.catalog_item .image_wrapper_block img, .product-item-image-wrapper img {{ mix-blend-mode: normal; }}
.item_block .catalog_item, .catalog_item_wrapp .catalog_item {{ padding: 6px 6px 14px; }}
.item-title a {{ font-size: 17px !important; line-height: 1.25 !important; }}
.muted, .article, .item .article_block {{ color: rgba(36, 26, 26, .45) !important; }}

/* --- секции и разделители ---------------------------------------------- */
.wrapper_inner > .container, .section_block, .front-block {{ background: transparent; }}
.top_block, .section-title-wrapper {{ border-color: {LINE}; }}
hr, .border, .item-separator {{ border-color: {LINE}; }}
.breadcrumbs, .bx-breadcrumb {{ font-size: 12px; letter-spacing: .04em; }}
.breadcrumbs a, .bx-breadcrumb a {{ color: rgba(36, 26, 26, .55); }}
.breadcrumbs a:hover, .bx-breadcrumb a:hover {{ color: {ACCENT}; }}

/* --- меню -------------------------------------------------------------- */
.menu-row .menu_wrap ul.menu > li > a {{ letter-spacing: .03em; font-weight: 600; }}
.menu-row .menu_wrap ul.menu > li.current > a,
.menu-row .menu_wrap ul.menu > li:hover > a {{ color: {ACCENT}; }}
.mega-menu .dropdown, .menu_wrap .dropdown {{ border-radius: 2px; box-shadow: 0 20px 50px rgba(36, 26, 26, .14); }}

/* --- карточка товара --------------------------------------------------- */
.detail .price_matrix_wrapper .price_value {{ font-family: "Playfair Display", Georgia, serif; }}
.detail .element_detail_wrapper, .detail_wrapper {{ background: {CARD}; }}
.tabs .tab-list li.active a, .tabs_section .tab-list li.active a {{ color: {ACCENT}; border-color: {ACCENT}; }}

/* --- формы ------------------------------------------------------------- */
input[type="text"], input[type="tel"], input[type="email"], textarea, select,
.form-control, .input-group .form-control {{
  border-radius: 2px; border-color: {LINE}; background: #fff;
}}
input:focus, textarea:focus, select:focus, .form-control:focus {{
  border-color: {ACCENT}; box-shadow: 0 0 0 3px rgba(143, 23, 55, .08);
}}
"""


def main():
    css = fetch_css()
    rules = recolor(css)

    header = (
        "/* skin.css — надстройка оформления для mirsladostey164.ru\n"
        "   Подключается последним, поверх шаблона Aspro Максимум.\n"
        "   Вёрстка и логика сайта не меняются: только цвет, шрифты и фон.\n"
        f"   Правил перекраски: {len(rules)}. Собрано скриптом skin/build_skin.py */\n")

    body = ("\n/* --- перекраска фирменного акцента ------------------------------------ */\n"
            + "\n".join(rules) + "\n" + MANUAL)

    with open(OUT, "w", encoding="utf-8", newline="\n") as f:
        f.write(header + body)

    print(f"правил перекрашено: {len(rules)}")
    print(f"размер skin.css: {os.path.getsize(OUT) // 1024} КБ")
    print("записано:", OUT)


if __name__ == "__main__":
    main()
