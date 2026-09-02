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
# Красный сохраняем как акцент, но берём глубокий бордо: узнаваемость
# остаётся, агрессивная «распродажная» яркость уходит.
COLOR_MAP = {
    "#f3103a": "#6d1226",   # основной акцент — глубокий бордо
    "#f42d52": "#8a1f36",   # наведение
    "#f30b36": "#6d1226",   # вариант основного
    "#e00a31": "#530d1c",   # нажатие, тёмный вариант
    "#ff1441": "#8a1f36",
    "#e5062d": "#530d1c",
}

ACCENT = "#6d1226"
ACCENT_HOVER = "#8a1f36"
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
/* ======================================================================
   Ручной слой: типографика, воздух, карточки, кнопки.
   Разметка не меняется — только оформление поверх шаблона.
   ====================================================================== */

@import url("https://fonts.googleapis.com/css2?family=Playfair+Display:wght@500;600&family=Inter:wght@400;500;600&display=swap");

/* --- основа ------------------------------------------------------------ */
body, .wrapper1, .wrapper_inner {{ background: {PAPER}; color: {INK}; }}
body {{
  font-family: Inter, "Segoe UI", Arial, sans-serif !important;
  font-size: 16px; line-height: 1.65; -webkit-font-smoothing: antialiased;
}}
p, li, td, dd, label, .muted, .description {{ font-family: inherit; }}
ul.menu .child a, #order_form_div input[type=submit] {{ font-family: inherit !important; }}

/* --- заголовки --------------------------------------------------------- */
h1, h2, h3, h4, .h1, .h2, .h3, .h4,
.topic, .topic span, .title_block, .top_block .title, .section_title,
.front-block .title, .detail .element-title, .item-title, .item-title a,
.popup-window-titlebar, .basket-title, .page-top .topic, .tabs_section .title {{
  font-family: "Playfair Display", Georgia, serif !important;
  font-weight: 500 !important;
  letter-spacing: -.02em;
  text-transform: none !important;
  color: {INK};
}}
.topic, .page-top .topic {{ font-size: clamp(34px, 4vw, 56px) !important; line-height: 1.08 !important; }}
h1 {{ font-size: clamp(32px, 3.6vw, 50px); line-height: 1.1; }}
h2, .title_block, .top_block .title {{ font-size: clamp(26px, 2.8vw, 40px) !important; line-height: 1.14; }}
h3 {{ font-size: clamp(20px, 1.8vw, 26px); }}

/* подписи над заголовками секций — тонкие, разрядка */
.top_block .title_wrapper > .muted, .section-subtitle {{
  color: {GOLD} !important; font-size: 11px; letter-spacing: .18em; text-transform: uppercase;
}}

/* --- воздух между секциями --------------------------------------------- */
.front-block, .drag-block, .section_block {{ padding-top: clamp(46px, 5vw, 86px) !important; padding-bottom: clamp(46px, 5vw, 86px) !important; }}
.front-block .top_block, .drag-block .top_block {{ margin-bottom: clamp(26px, 3vw, 46px) !important; }}
.grey_block, .grey {{ background: #f3ede3 !important; }}

/* --- шапка ------------------------------------------------------------- */
.header_wrap, .header_wrap .logo_and_menu-row, .header-v2 .logo_and_menu-row {{
  background: #fffdfa !important; border-bottom: 1px solid rgba(36,26,26,.08);
}}
.header_wrap .line-row, .header-v1 .line-row {{ background: #1b1211 !important; color: rgba(255,255,255,.75) !important; }}
.header_wrap .line-row a {{ color: rgba(255,255,255,.85) !important; }}
.menu-row .menu_wrap ul.menu > li > a {{
  font-size: 14px !important; font-weight: 500 !important; letter-spacing: .01em;
  text-transform: none !important; padding: 14px 16px !important;
}}
.menu-row .menu_wrap ul.menu > li.current > a, .menu-row .menu_wrap ul.menu > li:hover > a {{ color: {ACCENT} !important; }}
.mega-menu .dropdown, .menu_wrap .dropdown {{
  border-radius: 10px !important; border: 1px solid rgba(36,26,26,.08) !important;
  box-shadow: 0 24px 60px rgba(36,26,26,.14) !important;
}}
.wrap_icon svg, .header_wrap svg {{ stroke-width: 1.4; }}

/* --- кнопки: скруглённые, с воздухом ----------------------------------- */
.btn, .btn.btn-default, .btn.btn-lg, .btn.btn-sm, .btn.btn-xs, button.btn, input[type=submit] {{
  border-radius: 999px !important;
  padding: 13px 30px !important;
  font-family: Inter, sans-serif !important;
  font-size: 14px !important; font-weight: 600 !important;
  letter-spacing: .01em !important; text-transform: none !important;
  border-width: 1px !important;
  box-shadow: none !important;
  transition: background-color .2s ease, color .2s ease, border-color .2s ease, transform .2s ease;
}}
.btn.btn-lg {{ padding: 16px 38px !important; font-size: 15px !important; }}
.btn.btn-sm, .btn.btn-xs {{ padding: 9px 20px !important; font-size: 13px !important; }}
.btn.btn-default, .btn-primary, input[type=submit] {{ background-color: {ACCENT} !important; border-color: {ACCENT} !important; color: #fff !important; }}
.btn.btn-default:hover, .btn-primary:hover, input[type=submit]:hover {{ background-color: {ACCENT_HOVER} !important; border-color: {ACCENT_HOVER} !important; transform: translateY(-1px); }}
.btn.btn-transparent, .btn.btn-default.transparent, .btn.btn-default.white {{
  color: {ACCENT} !important; border-color: rgba(109,18,38,.35) !important; background: transparent !important;
}}
.btn.btn-transparent:hover, .btn.btn-default.transparent:hover {{ color: #fff !important; background: {ACCENT} !important; border-color: {ACCENT} !important; }}

/* --- карточки товара ---------------------------------------------------- */
.catalog_block .item_block, .catalog_block .catalog_item_wrapp {{ background: transparent !important; border: 0 !important; }}
.item_block .catalog_item, .catalog_item_wrapp .catalog_item, .product-item-container {{
  background: {CARD} !important;
  border: 0 !important;
  border-radius: 14px !important;
  padding: 14px 14px 20px !important;
  box-shadow: 0 1px 2px rgba(36,26,26,.06), 0 8px 24px rgba(36,26,26,.05) !important;
  transition: box-shadow .3s ease, transform .3s ease !important;
}}
.item_block:hover .catalog_item, .catalog_item_wrapp:hover .catalog_item {{
  box-shadow: 0 20px 46px rgba(36,26,26,.13) !important;
  transform: translateY(-3px);
}}
.catalog_item .image_wrapper_block, .product-item-image-wrapper {{
  background: #fbf6ee !important; border-radius: 10px !important; overflow: hidden;
}}
.catalog_item .image_wrapper_block img {{ mix-blend-mode: normal; transition: transform .5s ease; }}
.item_block:hover .image_wrapper_block img {{ transform: scale(1.03); }}
.catalog_item .item-title, .product-item-title {{ margin-top: 14px !important; }}
.item-title a, .product-item-title a {{ font-size: 18px !important; line-height: 1.28 !important; letter-spacing: -.01em; }}
.catalog_item .article_block, .catalog_item .article, .item .article_block {{
  color: rgba(36,26,26,.42) !important; font-size: 12px !important; letter-spacing: .02em;
}}
.catalog_item .price, .price_matrix_wrapper .price, .product-item-price-current, .price_value {{
  font-family: "Playfair Display", Georgia, serif !important;
  font-size: 24px !important; font-weight: 500 !important; color: {INK} !important;
}}
.price_measure, .item .price_measure {{ color: rgba(36,26,26,.45) !important; font-size: 13px !important; }}

/* метки: цвет задан на вложенном элементе, поэтому целимся в него */
.stickers > div, .sticker_wrapper > div {{ background: transparent !important; box-shadow: none !important; }}
[class*="sticker_"], .stickers .sticker, .product-item-label-text {{
  border-radius: 999px !important;
  padding: 5px 13px !important;
  font-family: Inter, sans-serif !important;
  font-size: 10px !important; font-weight: 600 !important;
  letter-spacing: .1em !important; text-transform: uppercase !important;
  background: {ACCENT} !important; color: #fff !important;
  box-shadow: none !important; border: 0 !important;
}}
[class*="sticker_new"], [class*="sticker_novink"] {{ background: {GOLD} !important; color: #241a1a !important; }}
[class*="sticker_sovetuem"], [class*="sticker_recommend"], [class*="sticker_hit"] {{ background: #3f2b28 !important; }}

/* рейтинг-звёзды приглушаем: он почти везде пустой */
.catalog_item .rating, .item_block .rating, .votes_block {{ opacity: .35; }}

/* --- карточка товара ---------------------------------------------------- */
.detail .element_detail_wrapper, .detail_wrapper, .detail .price_block {{ background: transparent !important; }}
.detail .prices_block .price_value, .detail .price_value {{ font-size: clamp(30px, 3vw, 44px) !important; }}
.detail .img_wrapper, .detail .product-detail-gallery {{ background: #fbf6ee !important; border-radius: 16px !important; overflow: hidden; }}
.detail .tabs .tab-list li a, .tabs_section .tab-list li a {{
  font-family: Inter, sans-serif !important; font-size: 15px !important; letter-spacing: .01em;
  text-transform: none !important;
}}
.tabs .tab-list li.active a, .tabs_section .tab-list li.active a {{ color: {ACCENT} !important; border-color: {ACCENT} !important; }}
.detail .characteristic .props_list td, .props_list td {{ font-size: 15px !important; padding: 11px 0 !important; }}

/* --- фильтры, сортировка, хлебные крошки -------------------------------- */
.breadcrumbs, .bx-breadcrumb {{ font-size: 12px !important; letter-spacing: .03em; margin-bottom: 18px !important; }}
.breadcrumbs a, .bx-breadcrumb a {{ color: rgba(36,26,26,.5) !important; }}
.breadcrumbs a:hover, .bx-breadcrumb a:hover {{ color: {ACCENT} !important; }}
.sort_header, .display_list, .filter_form, .smartfilter {{ font-size: 14px; }}
.sort_header .sort_item, .filter_form .btn {{ border-radius: 999px !important; }}
.sidebar .menu_top_block li a, .sidebar_menu li a {{ font-size: 15px !important; letter-spacing: 0; }}

/* --- формы -------------------------------------------------------------- */
input[type="text"], input[type="tel"], input[type="email"], input[type="password"],
textarea, select, .form-control, .input-group .form-control {{
  border-radius: 10px !important;
  border: 1px solid rgba(36,26,26,.14) !important;
  background: #fff !important;
  padding: 12px 16px !important;
  font-family: Inter, sans-serif !important; font-size: 15px !important;
}}
input:focus, textarea:focus, select:focus, .form-control:focus {{
  border-color: {ACCENT} !important; box-shadow: 0 0 0 3px rgba(109,18,38,.10) !important;
}}

/* --- подвал ------------------------------------------------------------- */
.footer_inner, .footer-block, footer.footer {{ background: #1b1211 !important; color: rgba(255,255,255,.66) !important; }}
.footer_inner a, footer.footer a {{ color: rgba(255,255,255,.78) !important; }}
.footer_inner a:hover, footer.footer a:hover {{ color: {GOLD} !important; }}
.footer_inner .title, footer.footer .title, .footer_inner .bottom_block .title {{
  color: {GOLD} !important; font-family: Inter, sans-serif !important;
  font-size: 11px !important; letter-spacing: .16em !important; text-transform: uppercase !important;
}}
.footer_inner .bottom_inner, .copyright {{ border-top: 1px solid rgba(255,255,255,.10) !important; }}

/* --- баннер на главной -------------------------------------------------- */
.top_big_banners .main_info .text, .top_slider_wrapp .text {{ font-size: 17px !important; line-height: 1.6 !important; }}
.top_big_banners .main_info .title, .top_slider_wrapp .title {{
  font-family: "Playfair Display", Georgia, serif !important;
  font-size: clamp(34px, 4vw, 58px) !important; line-height: 1.08 !important; font-weight: 500 !important;
}}

/* --- разделители и мелочи ----------------------------------------------- */
hr, .border, .item-separator, .top_block, .section-title-wrapper {{ border-color: {LINE} !important; }}
.scroll-top, .fixed_menu, #mobilemenu .menu_item {{ border-radius: 999px; }}
.wrap_icon .count, .basket_count, .icon_count {{ background: {ACCENT} !important; }}
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
