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
    "#f3103a": "#a8213c",   # основной акцент — бордо, читаемое на тёмном
    "#f42d52": "#c42b4c",   # наведение
    "#f30b36": "#a8213c",   # вариант основного
    "#e00a31": "#7d1329",   # нажатие, тёмный вариант
    "#ff1441": "#c42b4c",
    "#e5062d": "#7d1329",
}

ACCENT = "#a8213c"
ACCENT_HOVER = "#c42b4c"
ACCENT_DEEP = "#7d1329"
INK = "#f1eae3"          # основной текст — светлый
MUTED = "rgba(241, 234, 227, .52)"
GROUND = "#15100f"       # фон страницы
PANEL = "#1c1615"        # полосы секций, выпадающие панели
CARD = "#221b19"         # карточки товара
FIELD = "#171211"        # поля ввода
LINE = "rgba(241, 234, 227, .10)"
GOLD = "#c2a15f"
TILE = "#f6efe4"         # плитка под фотографией товара


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



# Шаблон рассчитан на белый фон: тёмный текст, белые заливки, светлые рамки.
# Второй проход переписывает их так же, как первый переписывает акцент, —
# теми же селекторами, поэтому специфичность совпадает, а наш файл идёт
# последним и выигрывает. Ручными правилами это не перекрыть: в шаблоне
# сотни мест с !important и длинными селекторами.
TEXT_MAP = {
    "#000000": INK, "#000": INK, "#111111": INK, "#111": INK,
    "#1a1a1a": INK, "#202020": INK, "#212121": INK, "#222222": INK, "#222": INK,
    "#2b2b2b": INK, "#303030": INK, "#333333": INK, "#333": INK,
    "#3c3c3c": INK, "#404040": INK, "#444444": INK, "#444": INK,
    "#4d4d4d": MUTED, "#555555": MUTED, "#555": MUTED, "#5c5c5c": MUTED,
    "#666666": MUTED, "#666": MUTED, "#707070": MUTED, "#757575": MUTED,
    "#777777": MUTED, "#777": MUTED, "#808080": MUTED, "#888888": MUTED,
    "#888": MUTED, "#8c8c8c": MUTED, "#919191": MUTED, "#999999": MUTED,
    "#999": MUTED, "#a0a0a0": MUTED, "#aaaaaa": MUTED, "#aaa": MUTED,
    "black": INK,
}
FILL_MAP = {
    "#ffffff": CARD, "#fff": CARD, "white": CARD,
    "#fefefe": CARD, "#fdfdfd": CARD, "#fcfcfc": PANEL, "#fbfbfb": PANEL,
    "#fafafa": PANEL, "#f9f9f9": PANEL, "#f8f8f8": PANEL, "#f7f7f7": PANEL,
    "#f6f6f6": PANEL, "#f5f5f5": PANEL, "#f4f4f4": PANEL, "#f3f3f3": PANEL,
    "#f2f2f2": PANEL, "#f1f1f1": PANEL, "#f0f0f0": PANEL,
    "#ededed": PANEL, "#ebebeb": PANEL, "#eeeeee": PANEL, "#eee": PANEL,
}
EDGE_MAP = {
    "#ffffff": LINE, "#fff": LINE, "white": LINE,
    "#f5f5f5": LINE, "#f0f0f0": LINE, "#ededed": LINE, "#ebebeb": LINE,
    "#eeeeee": LINE, "#eee": LINE, "#e8e8e8": LINE, "#e5e5e5": LINE,
    "#e3e3e3": LINE, "#e0e0e0": LINE, "#dedede": LINE, "#dddddd": LINE,
    "#ddd": LINE, "#d9d9d9": LINE, "#d6d6d6": LINE, "#d5d5d5": LINE,
    "#d0d0d0": LINE, "#cccccc": LINE, "#ccc": LINE, "#c8c8c8": LINE,
}

# правила шаблона, которые трогать нельзя: там светлый фон осмыслен
KEEP_LIGHT = ("sticker", "label", "btn", "button", "badge", "tooltip",
              "flex-direction", "owl-", "slick-", "colorpicker")


def _swap(value, mapping):
    """Замена цвета с границами слова: #fff не должен попасть в #ffffff."""
    for old in sorted(mapping, key=len, reverse=True):
        if old.startswith("#"):
            rx = r"(?<![0-9a-fA-F])" + re.escape(old) + r"(?![0-9a-fA-F])"
        else:
            rx = r"\b" + re.escape(old) + r"\b"
        value = re.sub(rx, mapping[old], value, flags=re.I)
    return value


def _mapping(prop):
    prop = prop.strip().lower()
    if prop.startswith(("background", "fill")):
        return FILL_MAP
    if "border" in prop or "outline" in prop:
        return EDGE_MAP
    if prop == "color" or prop.endswith("-color") or prop == "stroke":
        return TEXT_MAP
    return None


def redark(css):
    """Светлая схема шаблона → тёмная, правило за правилом."""
    pattern = re.compile(r"([^{}]+)\{([^{}]*)\}")
    rules = []
    for match in pattern.finditer(css):
        selector, body = match.group(1).strip(), match.group(2)
        if selector.startswith("@") or any(k in selector for k in KEEP_LIGHT):
            continue

        kept = []
        for declaration in body.split(";"):
            if ":" not in declaration:
                continue
            prop, value = declaration.split(":", 1)
            mapping = _mapping(prop)
            if mapping is None or "url(" in value.lower():
                continue
            fresh = _swap(value, mapping)
            if fresh != value:
                kept.append(f"{prop.strip()}:{fresh.strip()}")
        if kept:
            rules.append(" ".join(selector.split()) + "{" + ";".join(kept) + "}")
    return rules

FONTS = """/* Шрифты подключаются первой строкой: правило @import
   действует только до первых стилей, ниже по файлу браузер его отбрасывает. */
@import url("https://fonts.googleapis.com/css2?family=Playfair+Display:wght@500;600&family=Inter:wght@400;500;600&display=swap");
"""


MANUAL = f"""
/* ======================================================================
   Ручной слой: тёмная палитра, типографика, карточки, формы.
   Разметка не меняется — только оформление поверх шаблона.
   ====================================================================== */

/* --- основа ------------------------------------------------------------ */
html, body, .wrapper1, .wrapper_inner, .wraps, #content, .middle,
.container, .container_inner, .maxwidth-theme, .section-content-wrapper,
.front-block, .drag-block, .page-top, .content_wrapper {{
  background-color: {GROUND} !important;
}}
body {{
  color: {INK} !important;
  font-family: Inter, "Segoe UI", Arial, sans-serif !important;
  font-size: 16px; line-height: 1.65; -webkit-font-smoothing: antialiased;
}}
::selection {{ background: {ACCENT}; color: #fff; }}

/* цвет текста задан в шаблоне сотнями правил — переводим в светлый */
p, li, td, th, dd, dt, label, span, div, section, article,
.text, .description, .tab-content, .props_list td, .char_name, .char_value {{
  color: inherit !important;
}}
a, a:visited {{ color: {INK} !important; }}
a:hover, a:focus {{ color: {ACCENT_HOVER} !important; }}
.muted, .small, .article_block, .article, .price_measure, .date,
.hint, .quantity, .measure, .copyright {{ color: {MUTED} !important; }}
::placeholder {{ color: rgba(241, 234, 227, .34) !important; }}

/* --- заголовки --------------------------------------------------------- */
h1, h2, h3, h4, .h1, .h2, .h3, .h4,
.topic, .topic span, .title_block, .top_block .title, .section_title,
.front-block .title, .detail .element-title, .item-title, .item-title a,
.popup-window-titlebar, .basket-title, .page-top .topic, .tabs_section .title {{
  font-family: "Playfair Display", Georgia, serif !important;
  font-weight: 500 !important;
  letter-spacing: -.02em;
  text-transform: none !important;
  color: {INK} !important;
}}
.topic, .page-top .topic {{ font-size: clamp(34px, 4vw, 56px) !important; line-height: 1.08 !important; }}
h1 {{ font-size: clamp(32px, 3.6vw, 50px); line-height: 1.1; }}
h2, .title_block, .top_block .title {{ font-size: clamp(26px, 2.8vw, 40px) !important; line-height: 1.14; }}
h3 {{ font-size: clamp(20px, 1.8vw, 26px); }}
.top_block .title_wrapper > .muted, .section-subtitle {{
  color: {GOLD} !important; font-size: 11px; letter-spacing: .18em; text-transform: uppercase;
}}

/* --- воздух между секциями --------------------------------------------- */
.front-block, .drag-block, .section_block {{
  padding-top: clamp(46px, 5vw, 86px) !important;
  padding-bottom: clamp(46px, 5vw, 86px) !important;
}}
.front-block .top_block, .drag-block .top_block {{ margin-bottom: clamp(26px, 3vw, 46px) !important; }}

/* чередование полос: одна тёмная, другая чуть светлее */
.grey_block, .grey, .block_wr.grey, .front-block.grey, .drag-block.grey {{
  background-color: {PANEL} !important;
}}

/* --- меню и выпадающие панели ------------------------------------------ */
.menu-row .menu_wrap ul.menu > li > a {{
  font-size: 14px !important; font-weight: 500 !important; letter-spacing: .01em;
  text-transform: none !important; padding: 14px 16px !important;
}}
.menu-row .menu_wrap ul.menu > li.current > a,
.menu-row .menu_wrap ul.menu > li:hover > a {{ color: {ACCENT_HOVER} !important; }}
.mega-menu .dropdown, .menu_wrap .dropdown, .dropdown-menu,
#mobilemenu, .mobile_menu, .search_popup, .ik_select_list,
.bx_filter_select_popup, .jq-selectbox__dropdown, .tooltip-inner {{
  background: {PANEL} !important;
  color: {INK} !important;
  border: 1px solid {LINE} !important;
  border-radius: 10px !important;
  box-shadow: 0 24px 60px rgba(0, 0, 0, .55) !important;
}}

/* окна: обратная связь, быстрый заказ, корзина при наведении */
.popup-window, .popup_window, .bx-core-popup-window, .basket_hover_block,
.fancybox-skin, .modal-content, .ui-widget-content, .white_block {{
  background: {PANEL} !important; color: {INK} !important;
  border-color: {LINE} !important;
}}
.popup-window-titlebar, .bx-core-popup-window-titlebar {{
  background: transparent !important; border-bottom: 1px solid {LINE} !important;
}}

/* --- кнопки ------------------------------------------------------------ */
.btn, .btn.btn-default, .btn.btn-lg, .btn.btn-sm, .btn.btn-xs, button.btn, input[type=submit] {{
  border-radius: 999px !important;
  padding: 13px 30px !important;
  font-family: Inter, sans-serif !important;
  font-size: 14px !important; font-weight: 600 !important;
  letter-spacing: .01em !important; text-transform: none !important;
  border-width: 1px !important; box-shadow: none !important;
  transition: background-color .2s ease, color .2s ease, border-color .2s ease, transform .2s ease;
}}
.btn.btn-lg {{ padding: 16px 38px !important; font-size: 15px !important; }}
.btn.btn-sm, .btn.btn-xs {{ padding: 9px 20px !important; font-size: 13px !important; }}
.btn.btn-default, .btn-primary, input[type=submit] {{
  background-color: {ACCENT} !important; border-color: {ACCENT} !important; color: #fff !important;
}}
.btn.btn-default:hover, .btn-primary:hover, input[type=submit]:hover {{
  background-color: {ACCENT_HOVER} !important; border-color: {ACCENT_HOVER} !important;
  color: #fff !important; transform: translateY(-1px);
}}
.btn.btn-transparent, .btn.btn-default.transparent, .btn.btn-default.white {{
  color: {INK} !important; border-color: rgba(241, 234, 227, .26) !important; background: transparent !important;
}}
.btn.btn-transparent:hover, .btn.btn-default.transparent:hover {{
  color: #fff !important; background: {ACCENT} !important; border-color: {ACCENT} !important;
}}

/* --- карточки товара ---------------------------------------------------- */
.catalog_block .item_block, .catalog_block .catalog_item_wrapp {{ background: transparent !important; border: 0 !important; }}
.item_block .catalog_item, .catalog_item_wrapp .catalog_item, .product-item-container {{
  background: {CARD} !important;
  border: 1px solid {LINE} !important;
  border-radius: 14px !important;
  padding: 14px 14px 20px !important;
  box-shadow: none !important;
  transition: border-color .3s ease, box-shadow .3s ease, transform .3s ease !important;
}}
.item_block:hover .catalog_item, .catalog_item_wrapp:hover .catalog_item {{
  border-color: rgba(168, 33, 60, .55) !important;
  box-shadow: 0 22px 48px rgba(0, 0, 0, .55) !important;
  transform: translateY(-3px);
}}
.catalog_item .image_wrapper_block, .product-item-image-wrapper {{
  background: {TILE} !important; border-radius: 10px !important; overflow: hidden;
}}
.catalog_item .image_wrapper_block img {{ transition: transform .5s ease; }}
.item_block:hover .image_wrapper_block img {{ transform: scale(1.03); }}
.catalog_item .item-title, .product-item-title {{ margin-top: 14px !important; }}
.item-title a, .product-item-title a {{ font-size: 18px !important; line-height: 1.28 !important; letter-spacing: -.01em; }}
.catalog_item .price, .price_matrix_wrapper .price, .product-item-price-current, .price_value {{
  font-family: "Playfair Display", Georgia, serif !important;
  font-size: 24px !important; font-weight: 500 !important; color: {INK} !important;
}}

/* метки: одна палитра вместо пёстрых плашек */
.stickers .sticker, .product-item-label-text, .sticker_wrapper .sticker, .stickers > div {{
  border-radius: 999px !important; padding: 5px 12px !important;
  font-size: 10px !important; font-weight: 600 !important;
  letter-spacing: .1em !important; text-transform: uppercase !important;
  background: {ACCENT} !important; color: #fff !important; box-shadow: none !important;
}}
.stickers .sticker.new, .sticker_wrapper .sticker.new {{ background: {GOLD} !important; color: #1a1211 !important; }}
.stickers .sticker.recommend, .sticker_wrapper .sticker.recommend {{ background: #4a3330 !important; }}
.catalog_item .rating, .item_block .rating, .votes_block {{ opacity: .35; }}

/* --- карточка товара ---------------------------------------------------- */
.detail .element_detail_wrapper, .detail_wrapper, .detail .price_block {{ background: transparent !important; }}
.detail .prices_block .price_value, .detail .price_value {{ font-size: clamp(30px, 3vw, 44px) !important; }}
.detail .img_wrapper, .detail .product-detail-gallery, .detail .slides {{
  background: {TILE} !important; border-radius: 16px !important; overflow: hidden;
}}
.detail .tabs .tab-list li a, .tabs_section .tab-list li a {{
  font-family: Inter, sans-serif !important; font-size: 15px !important;
  letter-spacing: .01em; text-transform: none !important;
}}
.tabs .tab-list li.active a, .tabs_section .tab-list li.active a {{
  color: {ACCENT_HOVER} !important; border-color: {ACCENT_HOVER} !important;
}}
.detail .characteristic .props_list td, .props_list td {{
  font-size: 15px !important; padding: 11px 0 !important; border-color: {LINE} !important;
}}

/* --- таблицы, фильтры, крошки ------------------------------------------- */
table td, table th, .table > tbody > tr > td {{ border-color: {LINE} !important; }}
.breadcrumbs, .bx-breadcrumb {{ font-size: 12px !important; letter-spacing: .03em; margin-bottom: 18px !important; }}
.breadcrumbs a, .bx-breadcrumb a, .breadcrumbs span, .bx-breadcrumb span {{ color: {MUTED} !important; }}
.breadcrumbs a:hover, .bx-breadcrumb a:hover {{ color: {ACCENT_HOVER} !important; }}
.sort_header, .display_list, .filter_form, .smartfilter {{ font-size: 14px; }}
.sort_header .sort_item, .filter_form .btn {{ border-radius: 999px !important; }}
.sidebar .menu_top_block li a, .sidebar_menu li a, .left_block a {{ font-size: 15px !important; letter-spacing: 0; }}
.left_block .internal_sections_list li.cur > a, .left_block .internal_sections_list li:hover > a {{ color: {ACCENT_HOVER} !important; }}

/* --- формы -------------------------------------------------------------- */
input[type="text"], input[type="tel"], input[type="email"], input[type="password"],
input[type="search"], input[type="number"], textarea, select, .form-control, .input-group .form-control {{
  border-radius: 10px !important;
  border: 1px solid {LINE} !important;
  background: {FIELD} !important;
  color: {INK} !important;
  padding: 12px 16px !important;
  font-family: Inter, sans-serif !important; font-size: 15px !important;
}}
input:focus, textarea:focus, select:focus, .form-control:focus {{
  border-color: {ACCENT} !important; box-shadow: 0 0 0 3px rgba(168, 33, 60, .18) !important;
}}

/* --- подвал ------------------------------------------------------------- */
.footer_inner, .footer-block, footer.footer, .footer_bottom {{
  background: #0e0a0a !important; color: {MUTED} !important;
}}
.footer_inner a, footer.footer a {{ color: rgba(241, 234, 227, .74) !important; }}
.footer_inner a:hover, footer.footer a:hover {{ color: {GOLD} !important; }}
.footer_inner .title, footer.footer .title, .footer_inner .bottom_block .title {{
  color: {GOLD} !important; font-family: Inter, sans-serif !important;
  font-size: 11px !important; letter-spacing: .16em !important; text-transform: uppercase !important;
}}
.footer_inner .bottom_inner, .copyright {{ border-top: 1px solid rgba(241, 234, 227, .08) !important; }}

/* --- разделители и мелочи ----------------------------------------------- */
hr, .border, .item-separator, .top_block, .section-title-wrapper {{ border-color: {LINE} !important; }}
.scroll-top, .fixed_menu, #mobilemenu .menu_item {{ border-radius: 999px; }}
.wrap_icon .count, .basket_count, .icon_count {{ background: {ACCENT} !important; color: #fff !important; }}

/* --- то, что не поймал автоматический проход ---------------------------- */

/* метки на карточках: у шаблона они синяя, зелёная и фиолетовая */
[class*="sticker_"] {{
  border-radius: 999px !important; padding: 5px 12px !important;
  font-size: 10px !important; font-weight: 600 !important;
  letter-spacing: .1em !important; text-transform: uppercase !important;
  background: {ACCENT} !important; color: #fff !important; box-shadow: none !important;
}}
[class*="sticker_novinka"], [class*="sticker_new"] {{ background: {GOLD} !important; color: #1a1211 !important; }}
[class*="sticker_sovetuem"], [class*="sticker_recommend"] {{ background: #4a3330 !important; }}
.stickers, .sticker_wrapper {{ background: transparent !important; }}

/* логотип нарисован тёмно-красным по светлому — на тёмной шапке пропадает */
.logo svg .st0, .logo svg .st1, .logo svg path, .logo svg polygon {{ fill: {INK} !important; }}
.logo svg {{ transition: opacity .25s ease; }}
.logo:hover svg {{ opacity: .82; }}

/* выезжающая корзина и мобильный фильтр остались белыми панелями */
.basket_fly, .basket_fly .wrap_cont, .fly_basket, .basket_fly_wrapper,
.scrollbar-filter, #mobilefilter {{
  background: {PANEL} !important; color: {INK} !important;
}}

/* миниатюры галереи — та же тёплая плитка, что и под крупным фото */
.product-detail-gallery li.bordered, .detail .thumbs li, .slides li.bordered {{
  background: {TILE} !important; border-color: {LINE} !important;
}}

/* полоса прокрутки в тон */
::-webkit-scrollbar {{ width: 11px; height: 11px; }}
::-webkit-scrollbar-track {{ background: {GROUND}; }}
::-webkit-scrollbar-thumb {{ background: #3a2c2a; border-radius: 999px; border: 3px solid {GROUND}; }}
::-webkit-scrollbar-thumb:hover {{ background: {ACCENT_DEEP}; }}
"""


LAYOUT = f"""

/* ======================================================================
   Сетка каталога, шапка и баннер. Разметка прежняя, меняется раскладка.
   ====================================================================== */

/* --- шапка: липкая, тёмная, со стеклом ---------------------------------- */
.header_wrap, .header-wrapper, header > .header-wrapper {{
  position: sticky !important; top: 0; z-index: 900;
  background: rgba(18, 13, 12, .92) !important;
  backdrop-filter: blur(12px); -webkit-backdrop-filter: blur(12px);
  box-shadow: 0 1px 0 rgba(241, 234, 227, .07), 0 14px 34px rgba(0, 0, 0, .45) !important;
  border-bottom: 0 !important;
}}
.header_wrap .logo_and_menu-row, .header-wrapper .logo_and_menu-row,
.header_wrap .menu-row, .header_wrap #header {{
  background: transparent !important; border-color: {LINE} !important;
}}
.header_wrap .logo_and_menu-row {{ min-height: 104px !important; }}
.header_wrap .line-row, .header-v1 .line-row, .top-block-item {{
  background: #0e0a0a !important; color: {MUTED} !important;
}}
.logo img {{ transition: transform .3s ease; }}
.logo:hover img {{ transform: scale(1.03); }}

/* телефон и вход */
.header_wrap .phone a, .header_wrap .phone .no-decript {{
  font-family: Inter, sans-serif !important; font-size: 18px !important;
  font-weight: 600 !important; letter-spacing: -.01em; color: {INK} !important;
}}
.header_wrap .phone_wrap .more_phone a {{ font-size: 15px !important; }}
.header_wrap .personal-link, .header_wrap .auth_wr_inner a {{
  font-size: 15px !important; font-weight: 500 !important;
}}

/* иконки: крупнее, с мягкой подложкой при наведении */
.header_wrap .wrap_icon, .header_wrap .wrap_icon_block {{
  width: 46px !important; height: 46px !important;
  border-radius: 999px !important; transition: background-color .2s ease;
}}
.header_wrap .wrap_icon:hover {{ background: rgba(241, 234, 227, .08) !important; }}
.header_wrap svg {{ width: 22px !important; height: 22px !important; }}
.header_wrap .count, .header_wrap .basket_count {{
  min-width: 20px !important; height: 20px !important;
  border-radius: 999px !important; font-size: 11px !important; font-weight: 600 !important;
  background: {ACCENT} !important; color: #fff !important;
}}
.header_wrap .burger, .header_wrap .menu-burger, .mega_fixed_menu_btn {{
  border-radius: 999px !important; padding: 11px 14px !important;
  transition: background-color .2s ease;
}}
.header_wrap .burger:hover, .header_wrap .menu-burger:hover {{ background: rgba(241, 234, 227, .08) !important; }}
.fixed_side_panel, .right_fixed_panel, .fix_menu {{ border-radius: 14px 0 0 14px !important; overflow: hidden; }}

/* --- сетка каталога: крупные карточки ---------------------------------- */
@media (min-width: 1200px) {{
  .catalog_block.items.row {{
    display: grid !important;
    grid-template-columns: repeat(3, minmax(0, 1fr));
    gap: 30px !important; margin: 0 !important;
  }}
  .catalog_block.items.row > [class*="col-"] {{
    width: 100% !important; max-width: none !important;
    flex: none !important; padding: 0 !important; margin: 0 !important;
  }}
}}
@media (min-width: 768px) and (max-width: 1199px) {{
  .catalog_block.items.row {{
    display: grid !important;
    grid-template-columns: repeat(2, minmax(0, 1fr));
    gap: 22px !important; margin: 0 !important;
  }}
  .catalog_block.items.row > [class*="col-"] {{
    width: 100% !important; max-width: none !important;
    flex: none !important; padding: 0 !important; margin: 0 !important;
  }}
}}
@media (min-width: 768px) {{
  .item_block .catalog_item, .catalog_item_wrapp .catalog_item {{ padding: 18px 18px 24px !important; }}
  .catalog_item .image_wrapper_block {{ aspect-ratio: 1 / 1; display: grid; place-items: center; }}
  .catalog_item .image_wrapper_block img {{ width: 100%; height: 100%; object-fit: cover; }}
  .item-title a, .product-item-title a {{ font-size: 21px !important; }}
  .catalog_item .price, .price_value {{ font-size: 27px !important; }}
}}

/* заголовок раздела и панель сортировки */
.page-top, .section-content-wrapper > .page-top {{ padding: 40px 0 10px !important; }}
.page-top .topic {{ margin-bottom: 6px !important; }}
.sort_header, .panel_sort, .display_wrapper {{
  background: transparent !important; border: 0 !important;
  border-bottom: 1px solid {LINE} !important; padding: 10px 0 18px !important;
}}
.sort_header .sort_item a, .sort_header a {{ font-size: 14px !important; }}

/* кнопка покупки видна сразу, а не при наведении */
.catalog_item .footer_button {{
  display: block !important; opacity: 1 !important; visibility: visible !important;
  position: static !important; height: auto !important; margin-top: 16px !important;
}}
.catalog_item .footer_button .counter_wrapp {{ display: flex !important; gap: 10px; align-items: center; }}
.catalog_item .footer_button .btn {{ flex: 1 1 auto; justify-content: center; }}


/* --- разделы на главной: карусель мелких квадратиков → сетка плиток ----- */
.cat_sections .owl-stage-outer {{ overflow: visible !important; }}
.cat_sections .owl-stage {{
  display: grid !important;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 24px !important;
  width: auto !important;
  transform: none !important;
  transition: none !important;
}}
.cat_sections .owl-item {{
  width: auto !important; margin: 0 !important; float: none !important;
}}
.cat_sections .owl-nav, .cat_sections .owl-dots {{ display: none !important; }}
.cat_sections .item_block {{ height: auto !important; }}

.cat_sections .item.compact {{
  background: {CARD} !important;
  border: 1px solid {LINE} !important;
  border-radius: 14px !important;
  overflow: hidden;
  height: 100%;
  transition: border-color .3s ease, box-shadow .3s ease, transform .3s ease;
}}
.cat_sections .item.compact:hover {{
  border-color: rgba(168, 33, 60, .55) !important;
  box-shadow: 0 20px 44px rgba(0, 0, 0, .55);
  transform: translateY(-3px);
}}
.cat_sections .item.compact .img {{
  width: 100% !important; height: auto !important;
  aspect-ratio: 4 / 3; background: {TILE} !important;
  margin: 0 !important; padding: 0 !important; overflow: hidden;
}}
.cat_sections .item.compact .img a.thumb {{
  display: block !important; width: 100% !important; height: 100% !important;
}}
.cat_sections .item.compact .img img {{
  width: 100% !important; height: 100% !important;
  max-width: none !important; object-fit: cover;
  transition: transform .5s ease;
}}
.cat_sections .item.compact:hover .img img {{ transform: scale(1.04); }}
.cat_sections .item.compact .name {{
  padding: 16px 16px 18px !important; margin: 0 !important; text-align: center;
}}
.cat_sections .item.compact .name a {{
  font-family: "Playfair Display", Georgia, serif !important;
  font-size: 18px !important; font-weight: 500 !important;
  letter-spacing: .01em !important; line-height: 1.25 !important;
}}
@media (max-width: 1199px) {{
  .cat_sections .owl-stage {{ grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 18px !important; }}
}}
@media (max-width: 600px) {{
  .cat_sections .owl-stage {{ grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 12px !important; }}
  .cat_sections .item.compact .name a {{ font-size: 14px !important; }}
}}

/* --- главный баннер ----------------------------------------------------- */
/* внутри слайда лежит свой .wrapper_inner — он закрашивал подложку */
.top_slider_wrapp .wrapper_inner, .top_big_banners .wrapper_inner,
.top_slider_wrapp table, .top_slider_wrapp td {{ background: transparent !important; }}
.top_slider_wrapp .slides > li .banner_title .section {{
  color: {GOLD} !important; letter-spacing: .18em !important; text-transform: uppercase !important;
}}
.top_slider_wrapp .slides > li .banner_title .head-title,
.top_slider_wrapp .slides > li .banner_title {{ color: #fff !important; }}
.top_slider_wrapp .slides > li .banner_text {{ color: rgba(255, 255, 255, .80) !important; }}
.top_slider_wrapp .slides > li:before {{ display: none !important; }}
.top_slider_wrapp td.img img {{
  max-width: min(46vw, 720px) !important; height: auto !important;
}}
.top_slider_wrapp .banner_buttons .btn {{
  background: #fff !important; border-color: #fff !important; color: {ACCENT_DEEP} !important;
}}
.top_slider_wrapp .banner_buttons .btn:hover {{
  background: {GOLD} !important; border-color: {GOLD} !important; color: #1a1211 !important;
}}
"""


def main():
    css = fetch_css()
    rules = recolor(css)
    dark = redark(css)

    header = (
        "/* skin.css — надстройка оформления для mirsladostey164.ru\n"
        "   Подключается последним, поверх шаблона Aspro Максимум.\n"
        "   Вёрстка и логика сайта не меняются: только цвет, шрифты и фон.\n"
        f"   Правил перекраски: {len(rules)}. Собрано скриптом skin/build_skin.py */\n")

    body = (FONTS
            + "\n/* --- перекраска фирменного акцента ------------------------------------ */\n"
            + "\n".join(rules) + "\n"
            + "\n/* --- светлая схема шаблона переведена в тёмную --- */\n"
            + "\n".join(dark) + "\n" + MANUAL + LAYOUT)

    with open(OUT, "w", encoding="utf-8", newline="\n") as f:
        f.write(header + body)

    print(f"правил перекрашено: {len(rules)}, затемнено: {len(dark)}")
    print(f"размер skin.css: {os.path.getsize(OUT) // 1024} КБ")
    print("записано:", OUT)


if __name__ == "__main__":
    main()
