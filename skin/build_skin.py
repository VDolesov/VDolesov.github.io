import os
import re
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
SITE = "https://www.mirsladostey164.ru"
CACHE = os.path.join(HERE, "aspro.css")
OUT = os.path.join(HERE, "skin.css")

COLOR_MAP = {
    "#f3103a": "#d6a459",
    "#f42d52": "#e6b96f",
    "#f30b36": "#d6a459",
    "#e00a31": "#b88a45",
    "#ff1441": "#e6b96f",
    "#e5062d": "#b88a45",
}

ACCENT = "#d6a459"
ACCENT_HOVER = "#e6b96f"
ACCENT_DEEP = "#b88a45"
ON_ACCENT = "#120b08"
INK = "#f3e8d8"
MUTED = "rgba(243, 232, 216, .55)"
GROUND = "#120b08"
PANEL = "#170e0b"
CARD = "#1c1310"
FIELD = "#0e0806"
LINE = "rgba(243, 232, 216, .07)"
GOLD = "#d6a459"
GOLD_LINE = "rgba(214, 164, 89, .38)"
TILE = "#130c09"
ACCENT_SOFT = "rgba(214, 164, 89, .12)"


def fetch_css():
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

KEEP_LIGHT = ("sticker", "label", "btn", "button", "badge", "tooltip",
              "flex-direction", "owl-", "slick-", "colorpicker")


def _swap(value, mapping):
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


HEX = re.compile(r"(?<![0-9a-fA-F#])#([0-9a-fA-F]{3}|[0-9a-fA-F]{6})(?![0-9a-fA-F])")


def _grey(value, mapping):
    def swap(match):
        h = match.group(1)
        if len(h) == 3:
            h = "".join(c * 2 for c in h)
        r, g, b = int(h[:2], 16), int(h[2:4], 16), int(h[4:], 16)
        if max(r, g, b) - min(r, g, b) > 24:
            return match.group(0)
        luma = r * .299 + g * .587 + b * .114
        if mapping is FILL_MAP:
            if luma >= 248:
                return CARD
            if luma >= 222:
                return PANEL
            if 28 <= luma <= 140:
                return PANEL
        elif mapping is EDGE_MAP:
            if luma >= 96:
                return LINE
        elif mapping is TEXT_MAP:
            if luma <= 96:
                return INK
            if luma <= 180:
                return MUTED
        return match.group(0)
    return HEX.sub(swap, value)


def redark(css):
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
            fresh = _grey(_swap(value, mapping), mapping)
            if fresh != value:
                kept.append(f"{prop.strip()}:{fresh.strip()}")
        if kept:
            rules.append(" ".join(selector.split()) + "{" + ";".join(kept) + "}")
    return rules

FONTS = """@import url("https://fonts.googleapis.com/css2?family=Prata&family=Golos+Text:wght@400;500;600&display=swap");
"""

MANUAL = f"""

html, body, .wrapper1, .wrapper_inner, .wraps, #content, .middle,
.container, .container_inner, .maxwidth-theme, .section-content-wrapper,
.front-block, .drag-block, .page-top, .content_wrapper {{
  background-color: {GROUND} !important;
}}
body {{
  color: {INK} !important;
  font-family: "Golos Text", "Segoe UI", Arial, sans-serif !important;
  font-size: 16px; line-height: 1.65; -webkit-font-smoothing: antialiased;
}}
::selection {{ background: {ACCENT}; color: {ON_ACCENT}; }}

p, li, td, th, dd, dt, label, span, div, section, article,
.text, .description, .tab-content, .props_list td, .char_name, .char_value {{
  color: inherit !important;
}}
a, a:visited {{ color: {INK} !important; }}
a:hover, a:focus {{ color: {ACCENT_HOVER} !important; }}
.muted, .small, .article_block, .article, .price_measure, .date,
.hint, .quantity, .measure, .copyright {{ color: {MUTED} !important; }}
::placeholder {{ color: rgba(243, 232, 216, .34) !important; }}

h1, h2, h3, h4, .h1, .h2, .h3, .h4,
.topic, .topic span, .title_block, .top_block .title, .section_title,
.front-block .title, .detail .element-title, .item-title, .item-title a,
.popup-window-titlebar, .basket-title, .page-top .topic, .tabs_section .title {{
  font-family: Prata, Georgia, serif !important;
  font-weight: 400 !important;
  letter-spacing: 0;
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

.front-block, .drag-block, .section_block {{
  padding-top: clamp(46px, 5vw, 86px) !important;
  padding-bottom: clamp(46px, 5vw, 86px) !important;
}}
.front-block .top_block, .drag-block .top_block {{ margin-bottom: clamp(26px, 3vw, 46px) !important; }}

.grey_block, .grey, .block_wr.grey, .front-block.grey, .drag-block.grey {{
  background-color: {PANEL} !important;
}}

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
  border-radius: 0 !important;
  box-shadow: 0 24px 60px rgba(0, 0, 0, .55) !important;
}}

.popup-window, .popup_window, .bx-core-popup-window, .basket_hover_block,
.fancybox-skin, .modal-content, .ui-widget-content, .white_block {{
  background: {PANEL} !important; color: {INK} !important;
  border-color: {LINE} !important;
}}
.popup-window-titlebar, .bx-core-popup-window-titlebar {{
  background: transparent !important; border-bottom: 1px solid {LINE} !important;
}}

.btn, .btn.btn-default, .btn.btn-lg, .btn.btn-sm, .btn.btn-xs, button.btn, input[type=submit] {{
  border-radius: 0 !important;
  padding: 13px 30px !important;
  font-family: "Golos Text", "Segoe UI", sans-serif !important;
  font-size: 14px !important; font-weight: 600 !important;
  letter-spacing: .01em !important; text-transform: none !important;
  border-width: 1px !important; box-shadow: none !important;
  transition: background-color .2s ease, color .2s ease, border-color .2s ease, transform .2s ease;
}}
.btn.btn-lg {{ padding: 16px 38px !important; font-size: 15px !important; }}
.btn.btn-sm, .btn.btn-xs {{ padding: 9px 20px !important; font-size: 13px !important; }}
.btn.btn-default, .btn-primary, input[type=submit] {{
  background-color: {ACCENT} !important; border-color: {ACCENT} !important; color: {ON_ACCENT} !important;
}}
.btn.btn-default:hover, .btn-primary:hover, input[type=submit]:hover {{
  background-color: {ACCENT_HOVER} !important; border-color: {ACCENT_HOVER} !important;
  color: {ON_ACCENT} !important; transform: none;
}}
.btn.btn-transparent, .btn.btn-default.transparent, .btn.btn-default.white {{
  color: {INK} !important; border-color: rgba(243, 232, 216, .26) !important; background: transparent !important;
}}
.btn.btn-transparent:hover, .btn.btn-default.transparent:hover {{
  color: {ON_ACCENT} !important; background: {ACCENT} !important; border-color: {ACCENT} !important;
}}

.catalog_block .item_block, .catalog_block .catalog_item_wrapp {{ background: transparent !important; border: 0 !important; }}
.item_block .catalog_item, .catalog_item_wrapp .catalog_item, .product-item-container {{
  background: {CARD} !important;
  border: 1px solid {LINE} !important;
  border-radius: 0 !important;
  padding: 14px 14px 20px !important;
  box-shadow: none !important;
  transition: border-color .3s ease, box-shadow .3s ease, transform .3s ease !important;
}}
.item_block:hover .catalog_item, .catalog_item_wrapp:hover .catalog_item {{
  border-color: {GOLD_LINE} !important;
  box-shadow: 0 22px 48px rgba(0, 0, 0, .55) !important;
  transform: translateY(-3px);
}}
.catalog_item .image_wrapper_block, .product-item-image-wrapper {{
  background: {TILE} !important; border-radius: 0 !important; overflow: hidden;
}}
.catalog_item .image_wrapper_block img {{ transition: transform .5s ease; }}
.item_block:hover .image_wrapper_block img {{ transform: scale(1.03); }}
.catalog_item .item-title, .product-item-title {{ margin-top: 14px !important; }}
.item-title a, .product-item-title a {{ font-size: 18px !important; line-height: 1.28 !important; letter-spacing: -.01em; }}
.catalog_item .price, .price_matrix_wrapper .price, .product-item-price-current, .price_value {{
  font-family: Prata, Georgia, serif !important;
  font-size: 24px !important; font-weight: 500 !important; color: {INK} !important;
}}

.stickers .sticker, .product-item-label-text, .sticker_wrapper .sticker, .stickers > div {{
  border-radius: 0 !important; padding: 5px 12px !important;
  font-size: 10px !important; font-weight: 600 !important;
  letter-spacing: .1em !important; text-transform: uppercase !important;
  background: {ACCENT} !important; color: {ON_ACCENT} !important; box-shadow: none !important;
}}
.stickers .sticker.new, .sticker_wrapper .sticker.new {{ background: transparent !important; color: {GOLD} !important; box-shadow: inset 0 0 0 1px {GOLD_LINE} !important; }}
.stickers .sticker.recommend, .sticker_wrapper .sticker.recommend {{ background: #3a2a22 !important; }}
.catalog_item .rating, .item_block .rating, .votes_block {{ opacity: .35; }}

.detail .element_detail_wrapper, .detail_wrapper, .detail .price_block {{ background: transparent !important; }}
.detail .prices_block .price_value, .detail .price_value {{ font-size: clamp(30px, 3vw, 44px) !important; }}
.detail .img_wrapper, .detail .product-detail-gallery, .detail .slides {{
  background: {TILE} !important; border-radius: 0 !important; overflow: hidden;
}}
.detail .tabs .tab-list li a, .tabs_section .tab-list li a {{
  font-family: "Golos Text", "Segoe UI", sans-serif !important; font-size: 15px !important;
  letter-spacing: .01em; text-transform: none !important;
}}
.tabs .tab-list li.active a, .tabs_section .tab-list li.active a {{
  color: {ACCENT_HOVER} !important; border-color: {ACCENT_HOVER} !important;
}}
.detail .characteristic .props_list td, .props_list td {{
  font-size: 15px !important; padding: 11px 0 !important; border-color: {LINE} !important;
}}

table td, table th, .table > tbody > tr > td {{ border-color: {LINE} !important; }}
.breadcrumbs, .bx-breadcrumb {{ font-size: 12px !important; letter-spacing: .03em; margin-bottom: 18px !important; }}
.breadcrumbs a, .bx-breadcrumb a, .breadcrumbs span, .bx-breadcrumb span {{ color: {MUTED} !important; }}
.breadcrumbs a:hover, .bx-breadcrumb a:hover {{ color: {ACCENT_HOVER} !important; }}
.sort_header, .display_list, .filter_form, .smartfilter {{ font-size: 14px; }}
.sort_header .sort_item, .filter_form .btn {{ border-radius: 0 !important; }}
.sidebar .menu_top_block li a, .sidebar_menu li a, .left_block a {{ font-size: 15px !important; letter-spacing: 0; }}
.left_block .internal_sections_list li.cur > a, .left_block .internal_sections_list li:hover > a {{ color: {ACCENT_HOVER} !important; }}

input[type="text"], input[type="tel"], input[type="email"], input[type="password"],
input[type="search"], input[type="number"], textarea, select, .form-control, .input-group .form-control {{
  border-radius: 0 !important;
  border: 1px solid {LINE} !important;
  background: {FIELD} !important;
  color: {INK} !important;
  padding: 12px 16px !important;
  font-family: "Golos Text", "Segoe UI", sans-serif !important; font-size: 15px !important;
}}
input:focus, textarea:focus, select:focus, .form-control:focus {{
  border-color: {ACCENT} !important; box-shadow: 0 0 0 3px rgba(214, 164, 89, .18) !important;
}}

.footer_inner, .footer-block, footer.footer, .footer_bottom {{
  background: #0c0705 !important; color: {MUTED} !important;
}}
.footer_inner a, footer.footer a {{ color: rgba(243, 232, 216, .74) !important; }}
.footer_inner a:hover, footer.footer a:hover {{ color: {GOLD} !important; }}
.footer_inner .title, footer.footer .title, .footer_inner .bottom_block .title {{
  color: {GOLD} !important; font-family: "Golos Text", "Segoe UI", sans-serif !important;
  font-size: 11px !important; letter-spacing: .16em !important; text-transform: uppercase !important;
}}
.footer_inner .bottom_inner, .copyright {{ border-top: 1px solid rgba(243, 232, 216, .08) !important; }}

hr, .border, .item-separator, .top_block, .section-title-wrapper {{ border-color: {LINE} !important; }}
.scroll-top, .fixed_menu, #mobilemenu .menu_item {{ border-radius: 0; }}
.wrap_icon .count, .basket_count, .icon_count {{ background: {ACCENT} !important; color: {ON_ACCENT} !important; }}

[class*="sticker_"] {{
  border-radius: 0 !important; padding: 5px 12px !important;
  font-size: 10px !important; font-weight: 600 !important;
  letter-spacing: .1em !important; text-transform: uppercase !important;
  background: {ACCENT} !important; color: {ON_ACCENT} !important; box-shadow: none !important;
}}
[class*="sticker_novinka"], [class*="sticker_new"] {{ background: transparent !important; color: {GOLD} !important; box-shadow: inset 0 0 0 1px {GOLD_LINE} !important; }}
[class*="sticker_sovetuem"], [class*="sticker_recommend"] {{ background: #3a2a22 !important; }}
.stickers, .sticker_wrapper {{ background: transparent !important; }}

.logo svg .st0, .logo svg .st1, .logo svg path, .logo svg polygon {{ fill: {INK} !important; }}
.logo svg {{ transition: opacity .25s ease; }}
.logo:hover svg {{ opacity: .82; }}

.basket_fly, .basket_fly .wrap_cont, .fly_basket, .basket_fly_wrapper,
.scrollbar-filter, #mobilefilter {{
  background: {PANEL} !important; color: {INK} !important;
}}

.product-detail-gallery li.bordered, .detail .thumbs li, .slides li.bordered {{
  background: {TILE} !important; border-color: {LINE} !important;
}}

::-webkit-scrollbar {{ width: 11px; height: 11px; }}
::-webkit-scrollbar-track {{ background: {GROUND}; }}
::-webkit-scrollbar-thumb {{ background: #3a2a22; border-radius: 999px; border: 3px solid {GROUND}; }}
::-webkit-scrollbar-thumb:hover {{ background: {ACCENT_DEEP}; }}
"""

LAYOUT = f"""

.header_wrap, .header-wrapper, header > .header-wrapper {{
  position: sticky !important; top: 0; z-index: 900;
  background: rgba(18, 11, 8, .94) !important;
  backdrop-filter: blur(12px); -webkit-backdrop-filter: blur(12px);
  box-shadow: 0 1px 0 rgba(243, 232, 216, .07), 0 14px 34px rgba(0, 0, 0, .45) !important;
  border-bottom: 0 !important;
}}
.header_wrap .logo_and_menu-row, .header-wrapper .logo_and_menu-row,
.header_wrap .menu-row, .header_wrap #header {{
  background: transparent !important; border-color: {LINE} !important;
}}
.header_wrap .logo_and_menu-row {{ min-height: 104px !important; }}
.header_wrap .line-row, .header-v1 .line-row, .top-block-item {{
  background: #0c0705 !important; color: {MUTED} !important;
}}
.logo img {{ transition: transform .3s ease; }}
.logo:hover img {{ transform: scale(1.03); }}

.header_wrap .phone a, .header_wrap .phone .no-decript {{
  font-family: "Golos Text", "Segoe UI", sans-serif !important; font-size: 18px !important;
  font-weight: 600 !important; letter-spacing: -.01em; color: {INK} !important;
}}
.header_wrap .phone_wrap .more_phone a {{ font-size: 15px !important; }}
.header_wrap .personal-link, .header_wrap .auth_wr_inner a {{
  font-size: 15px !important; font-weight: 500 !important;
}}

.header_wrap .wrap_icon, .header_wrap .wrap_icon_block {{
  width: 46px !important; height: 46px !important;
  border-radius: 0 !important; transition: background-color .2s ease;
}}
.header_wrap .wrap_icon:hover {{ background: rgba(243, 232, 216, .08) !important; }}
.header_wrap svg {{ width: 22px !important; height: 22px !important; }}
.header_wrap .count, .header_wrap .basket_count {{
  min-width: 20px !important; height: 20px !important;
  border-radius: 0 !important; font-size: 11px !important; font-weight: 600 !important;
  background: {ACCENT} !important; color: {ON_ACCENT} !important;
}}
.header_wrap .burger, .header_wrap .menu-burger, .mega_fixed_menu_btn {{
  border-radius: 0 !important; padding: 11px 14px !important;
  transition: background-color .2s ease;
}}
.header_wrap .burger:hover, .header_wrap .menu-burger:hover {{ background: rgba(243, 232, 216, .08) !important; }}
.fixed_side_panel, .right_fixed_panel, .fix_menu {{ border-radius: 0 !important; overflow: hidden; }}

.catalog_block.items.row::before, .catalog_block.items.row::after {{ display: none !important; content: none !important; }}
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

.page-top, .section-content-wrapper > .page-top {{ padding: 40px 0 10px !important; }}
.page-top .topic {{ margin-bottom: 6px !important; }}
.sort_header, .panel_sort, .display_wrapper {{
  background: transparent !important; border: 0 !important;
  border-bottom: 1px solid {LINE} !important; padding: 10px 0 18px !important;
}}
.sort_header .sort_item a, .sort_header a {{ font-size: 14px !important; }}

.catalog_item .footer_button {{
  display: block !important; opacity: 1 !important; visibility: visible !important;
  position: static !important; height: auto !important; margin-top: 16px !important;
}}
.catalog_item .footer_button .counter_wrapp {{ display: flex !important; gap: 10px; align-items: center; }}
.catalog_item .footer_button .btn {{ flex: 1 1 auto; justify-content: center; }}

.wrapper1 {{ overflow-x: clip; }}


@media (min-width: 992px) {{
  body .product-info .flexbox--row > .product-detail-gallery {{
    flex: 0 0 54% !important; max-width: 54% !important;
  }}
  body .product-info .flexbox--row > .product-main {{
    flex: 0 0 46% !important; max-width: 46% !important; padding-left: 46px !important;
  }}
}}

body .product-detail-gallery .product-detail-gallery__container {{ width: 100% !important; }}
body .product-detail-gallery .product-detail-gallery__slider {{
  width: 100% !important; max-width: none !important;
}}
body .product-detail-gallery .product-detail-gallery__slider .owl-stage-outer {{ width: 100% !important; }}
body .product-detail-gallery .product-detail-gallery__slider .owl-stage {{
  width: 100% !important; transform: none !important; transition: none !important;
}}
body .product-detail-gallery .product-detail-gallery__slider .owl-item {{
  width: 100% !important; margin: 0 !important; float: none !important;
}}
body .product-detail-gallery .product-detail-gallery__slider .owl-item:not(.active) {{
  display: none !important;
}}
body .product-detail-gallery .product-detail-gallery__item {{
  width: 100% !important; height: auto !important; max-width: none !important;
  aspect-ratio: 1 / 1; background: {TILE} !important;
  border-radius: 0 !important; overflow: hidden;
  display: grid !important; place-items: center; margin: 0 !important;
}}
body .product-detail-gallery .product-detail-gallery__link {{
  display: block !important; width: 100% !important; height: 100% !important;
}}
body .product-detail-gallery .product-detail-gallery__picture {{
  width: 100% !important; height: 100% !important;
  max-width: none !important; max-height: none !important; object-fit: cover;
}}

body .product-detail-gallery__thmb-inner {{
  display: flex !important; flex-wrap: wrap; gap: 10px;
  justify-content: flex-start; margin-top: 14px !important;
}}
body .product-detail-gallery__thmb-inner > * {{
  width: 78px !important; height: 78px !important; margin: 0 !important;
  border-radius: 0 !important; overflow: hidden;
  background: {TILE} !important; border: 1px solid {LINE} !important;
  transition: border-color .2s ease;
}}
body .product-detail-gallery__thmb-inner > *:hover,
body .product-detail-gallery__thmb-inner > .active {{ border-color: {ACCENT} !important; }}
body .product-detail-gallery__thmb-inner img {{
  width: 100% !important; height: 100% !important; object-fit: cover;
}}

body .product-main .flexbox--row {{ display: block !important; }}
body .product-main .product-action.flex-50,
body .product-main .product-chars.flex-50 {{
  width: 100% !important; max-width: none !important; flex: none !important;
  padding-left: 0 !important; padding-right: 0 !important;
}}
body .product-main .product-chars {{
  margin-top: 28px !important; padding-top: 26px !important;
  border-top: 1px solid {LINE} !important;
}}
body .product-main .char-side {{ width: 100% !important; }}

body .detail .prices_block .price_value {{ font-size: clamp(34px, 3.4vw, 48px) !important; }}
body .detail .prices_block .price_currency {{ font-size: 26px !important; }}
body .detail .prices_block .price_measure {{ font-size: 14px !important; margin-left: 8px; }}
body .detail .prices_block {{ margin-bottom: 22px !important; }}

body .detail .buy_block .counter_wrapp {{
  display: flex !important; gap: 14px; align-items: stretch; flex-wrap: nowrap;
}}
body .detail .buy_block .counter_block_inner {{ flex: 0 0 auto; }}
body .detail .buy_block .btn {{
  flex: 1 1 auto; justify-content: center;
  padding: 16px 30px !important; font-size: 15px !important;
}}

body .char-side__title {{
  font-family: Prata, Georgia, serif !important;
  font-size: 21px !important; font-weight: 500 !important;
  margin-bottom: 14px !important; text-transform: none !important;
}}
body .product-chars .properties__item {{
  display: grid !important; grid-template-columns: 148px 1fr; gap: 0 20px;
  padding: 11px 0 !important; margin: 0 !important;
  border-bottom: 1px solid {LINE} !important;
}}
body .product-chars .properties__item:last-child {{ border-bottom: 0 !important; }}
body .product-chars .properties__hr {{ display: none !important; }}
body .product-chars .properties__title {{
  color: {MUTED} !important; font-size: 14px !important; line-height: 1.5;
}}
body .product-chars .properties__value {{
  font-size: 14px !important; line-height: 1.55; text-align: left !important;
}}


@media (max-width: 600px) {{
  body .product-chars .properties__item {{
    grid-template-columns: 1fr !important; gap: 3px 0; padding: 12px 0 !important;
  }}
  body .product-chars .properties__title {{
    font-size: 11px !important; letter-spacing: .08em; text-transform: uppercase;
  }}
  body .product-main .product-chars {{ margin-top: 22px !important; padding-top: 22px !important; }}
}}

body .bottom-info .tabs .nav-tabs {{
  border-bottom: 1px solid {LINE} !important; display: flex !important;
  flex-wrap: wrap; gap: 2px; margin-bottom: 0 !important;
}}
body .bottom-info .tabs .nav-tabs > li {{
  background: transparent !important; border: 0 !important;
  border-radius: 0 !important; margin: 0 !important;
}}
body .bottom-info .tabs .nav-tabs > li > a {{
  padding: 15px 20px !important; border: 0 !important; border-radius: 0 !important;
  background: transparent !important; font-size: 15px !important;
  color: {MUTED} !important; box-shadow: none !important;
}}
body .bottom-info .tabs .nav-tabs > li:hover > a {{ color: {INK} !important; }}
body .bottom-info .tabs .nav-tabs > li.active > a {{
  color: {INK} !important; box-shadow: inset 0 -2px 0 {ACCENT} !important;
}}
body .bottom-info .tab-content > .tab-pane > .bordered {{
  border: 0 !important; background: transparent !important;
  padding: 28px 0 0 !important; border-radius: 0 !important;
}}
body .bottom-info .ordered-block__title {{
  font-family: Prata, Georgia, serif !important;
  font-size: 26px !important; font-weight: 500 !important; text-transform: none !important;
}}

body .bottom-info-wrapper .side-block {{
  background: {CARD} !important; border: 1px solid {LINE} !important;
  border-radius: 0 !important; overflow: hidden;
}}
body .bottom-info-wrapper .side-block__bottom {{ border-top: 1px solid {LINE} !important; }}

body .cat_sections.cat_sections .owl-stage-outer {{ overflow: visible !important; }}
body .cat_sections.cat_sections .owl-stage {{
  display: grid !important;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 24px !important;
  width: auto !important;
  transform: none !important;
  transition: none !important;
}}
body .cat_sections.cat_sections .owl-item {{
  width: auto !important; margin: 0 !important; float: none !important;
}}
body .cat_sections.cat_sections .owl-nav, body .cat_sections.cat_sections .owl-dots {{ display: none !important; }}
body .cat_sections.cat_sections .item_block {{ height: auto !important; }}

body .cat_sections.cat_sections .item.compact {{
  background: {CARD} !important;
  border: 1px solid {LINE} !important;
  border-radius: 0 !important;
  overflow: hidden;
  height: 100%;
  transition: border-color .3s ease, box-shadow .3s ease, transform .3s ease;
}}
body .cat_sections.cat_sections .item.compact:hover {{
  border-color: {GOLD_LINE} !important;
  box-shadow: 0 20px 44px rgba(0, 0, 0, .55);
  transform: translateY(-3px);
}}
body .cat_sections.cat_sections .item.compact .img.shine {{
  width: 100% !important; height: auto !important;
  aspect-ratio: 4 / 3; background: {TILE} !important;
  margin: 0 !important; padding: 0 !important; overflow: hidden;
}}
body .cat_sections.cat_sections .item.compact .img.shine a.thumb {{
  display: block !important; width: 100% !important; height: 100% !important;
}}
body .cat_sections.cat_sections .item.compact .img.shine img {{
  width: 100% !important; height: 100% !important;
  max-width: none !important; object-fit: cover;
  transition: transform .5s ease;
}}
body .cat_sections.cat_sections .item.compact:hover .img.shine img {{ transform: scale(1.04); }}
body .cat_sections.cat_sections .item.compact .name {{
  padding: 16px 16px 18px !important; margin: 0 !important; text-align: center;
}}
body .cat_sections.cat_sections .item.compact .name a {{
  font-family: Prata, Georgia, serif !important;
  font-size: 18px !important; font-weight: 500 !important;
  letter-spacing: .01em !important; line-height: 1.25 !important;
}}
@media (max-width: 1199px) {{
  body .cat_sections.cat_sections .owl-stage {{ grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 18px !important; }}
}}
@media (max-width: 600px) {{
  body .cat_sections.cat_sections .owl-stage {{ grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 12px !important; }}
  body .cat_sections.cat_sections .item.compact .name a {{ font-size: 14px !important; }}
}}

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
  background: {ACCENT} !important; border-color: {ACCENT} !important; color: {ON_ACCENT} !important;
}}
.top_slider_wrapp .banner_buttons .btn:hover {{
  background: {ACCENT_HOVER} !important; border-color: {ACCENT_HOVER} !important; color: {ON_ACCENT} !important;
}}

.btn.wish_item, .btn.compare_item, .wish_item.btn, .compare_item.btn,
.btn.btn-search, button.btn-search, .top-btn, .btn.subscribe,
.btn[class*="icon_"], .btn.close {{
  width: 42px !important; height: 42px !important;
  min-width: 0 !important; max-width: none !important;
  padding: 0 !important; line-height: 1 !important;
  display: inline-flex !important; align-items: center !important; justify-content: center !important;
  border-radius: 0 !important;
  border: 1px solid {LINE} !important; background: transparent !important;
  transition: border-color .2s ease, background-color .2s ease;
}}
.btn.wish_item:hover, .btn.compare_item:hover, .btn.btn-search:hover, .top-btn:hover {{
  border-color: {ACCENT} !important; background: {ACCENT_SOFT} !important;
}}
.catalog_item .btn.wish_item, .catalog_item .btn.compare_item,
.catalog_item .wish_item.btn, .catalog_item .compare_item.btn {{
  width: 36px !important; height: 36px !important;
}}
.btn.wish_item svg, .btn.compare_item svg, .btn.btn-search svg {{
  width: 17px !important; height: 17px !important; margin: 0 !important;
}}
body .inline-search-block .search-button-div .btn.btn-search.btn-lg,
body .search-button-div .btn.btn-search.btn-lg,
body .search-button-div .btn, body .search-button-div button {{
  width: 42px !important; height: 42px !important; padding: 0 !important;
  min-width: 0 !important; border-radius: 0 !important;
  display: inline-flex !important; align-items: center !important; justify-content: center !important;
}}
.search-button-div {{ right: 6px !important; left: auto !important; }}

body .counter_wrapp .counter_block, body .counter_block.md, body .counter_block {{
  position: relative !important; display: inline-block !important;
  width: 138px !important; min-width: 0 !important; max-width: none !important;
  height: 54px !important; padding: 0 !important; margin: 0 !important;
  flex: 0 0 auto !important;
  border: 1px solid {LINE} !important; border-radius: 0 !important;
  overflow: hidden !important; background: transparent !important;
}}
body .counter_block .minus, body .counter_block .plus {{
  position: absolute !important; top: 0 !important; bottom: 0 !important;
  width: 42px !important; height: auto !important; padding: 0 !important; margin: 0 !important;
  display: flex !important; align-items: center !important; justify-content: center !important;
  background: transparent !important; border: 0 !important; cursor: pointer;
  color: {MUTED} !important; transition: color .2s ease; z-index: 2;
}}
body .counter_block .minus {{ left: 0 !important; right: auto !important; }}
body .counter_block .plus {{ right: 0 !important; left: auto !important; }}
body .counter_block .minus:hover, body .counter_block .plus:hover {{ color: {INK} !important; }}
body .counter_block input.text, body .counter_block .text, body .counter_block input {{
  position: static !important; display: block !important;
  width: 100% !important; height: 100% !important; padding: 0 42px !important; margin: 0 !important;
  text-align: center !important; border: 0 !important; border-radius: 0 !important;
  background: transparent !important; color: {INK} !important;
  font-family: "Golos Text", "Segoe UI", sans-serif !important; font-size: 16px !important; font-weight: 600 !important;
  box-shadow: none !important; line-height: 52px !important;
}}
body .counter_block input:focus {{ box-shadow: none !important; outline: 0 !important; }}
body .catalog_item .counter_block {{ width: 112px !important; height: 46px !important; }}
body .catalog_item .counter_block .minus, body .catalog_item .counter_block .plus {{ width: 36px !important; }}
body .catalog_item .counter_block input {{ padding: 0 36px !important; font-size: 15px !important; line-height: 44px !important; }}

.svg.inline svg, .svg.inline svg rect, .svg.inline svg path,
.svg.inline svg circle, .svg.inline svg polygon, .svg.inline svg ellipse {{
  fill: currentColor !important;
}}
.svg.inline svg [fill="none"] {{ fill: none !important; }}
body .counter_block .minus, body .counter_block .plus {{ color: rgba(243, 232, 216, .72) !important; }}

.top_block .title_wrapper > .muted, .section-subtitle,
body .char-side__title, .ordered-block__title--small,
.footer_inner .title, footer.footer .title,
.top_slider_wrapp .slides > li .banner_title .section {{
  font-family: "Golos Text", "Segoe UI", sans-serif !important;
  font-size: 11px !important; font-weight: 600 !important;
  letter-spacing: .14em !important; text-transform: uppercase !important;
  color: {GOLD} !important;
}}
body .char-side__title {{ margin-bottom: 16px !important; }}

.article_block, .article, .price_measure, .item .article_block {{
  font-family: "Golos Text", "Segoe UI", sans-serif !important;
  font-size: 12px !important; letter-spacing: .04em !important;
  color: {MUTED} !important; text-transform: none !important;
}}

.catalog_item .rating, .item_block .rating, .votes_block,
.product-info-headnote .rating {{ opacity: .3; }}

body .header_wrap .logo-row .row > .col-md-12,
body .header-wrapper .logo-row .row > .col-md-12 {{
  display: flex !important; align-items: center !important;
  min-height: 92px !important; height: auto !important;
}}
body .header_wrap .logo-row [class*="pull-"],
body .header-wrapper .logo-row [class*="pull-"] {{ float: none !important; height: auto !important; }}

body .header_wrap .logo-row .burger, body .header-wrapper .logo-row .burger {{
  height: 44px !important; width: 44px !important; padding: 0 !important;
  margin: 0 16px 0 0 !important; display: inline-flex !important;
  align-items: center !important; justify-content: center !important;
  border-radius: 0 !important;
}}
body .header_wrap .logo-row .burger svg, body .header-wrapper .logo-row .burger svg {{
  width: 22px !important; height: 22px !important;
}}

body .header_wrap .logo-block, body .header-wrapper .logo-block {{
  height: auto !important; margin: 0 22px 0 0 !important; padding: 0 !important;
}}
body .header_wrap .logo, body .header-wrapper .logo {{
  height: auto !important; width: auto !important; line-height: 0 !important;
  display: block !important; padding: 0 !important;
}}
body .header_wrap .logo a, body .header-wrapper .logo a {{ display: inline-block !important; line-height: 0 !important; }}
body .header_wrap .logo svg, body .header-wrapper .logo svg {{
  width: auto !important; height: 54px !important; max-width: none !important;
}}

body .header_wrap .logo-row .float_wrapper, body .header-wrapper .logo-row .float_wrapper {{
  height: auto !important; margin: 0 40px 0 0 !important; padding: 0 !important;
}}
body .header_wrap .logo-row .float_wrapper .hidden-sm,
body .header-wrapper .logo-row .float_wrapper .hidden-sm {{
  height: auto !important; max-width: 220px !important;
  font-size: 13px !important; line-height: 1.35 !important;
  color: {MUTED} !important; padding: 0 !important;
}}

body .header_wrap .logo-row .wrap_icon.inner-table-block,
body .header-wrapper .logo-row .wrap_icon.inner-table-block {{
  width: auto !important; height: auto !important; display: block !important;
  border-radius: 0 !important; background: transparent !important;
}}
body .header_wrap .phone-block, body .header-wrapper .phone-block {{
  display: flex !important; flex-direction: column !important; gap: 2px !important;
  align-items: flex-start !important;
}}
body .header_wrap .phone.with_dropdown, body .header-wrapper .phone.with_dropdown {{
  display: inline-flex !important; align-items: center !important; gap: 8px !important;
  height: auto !important; line-height: 1.2 !important; padding: 0 !important;
}}
body .header_wrap .phone > a, body .header-wrapper .phone > a {{
  font-size: 18px !important; font-weight: 600 !important; letter-spacing: -.01em !important;
  color: {INK} !important; line-height: 1.2 !important;
}}
body .header_wrap .phone .svg-inline-phone, body .header-wrapper .phone .svg-inline-phone {{ display: none !important; }}
body .header_wrap .phone .svg-inline-down, body .header-wrapper .phone .svg-inline-down {{
  display: inline-flex !important; align-items: center !important; opacity: .6;
}}
body .header_wrap .phone .svg-inline-down svg, body .header-wrapper .phone .svg-inline-down svg {{
  width: 10px !important; height: 10px !important;
}}
body .header_wrap .callback-block, body .header-wrapper .callback-block {{
  font-family: "Golos Text", "Segoe UI", sans-serif !important; font-size: 11px !important; font-weight: 600 !important;
  letter-spacing: .12em !important; text-transform: uppercase !important;
  color: {GOLD} !important; cursor: pointer;
}}
body .header_wrap .callback-block:hover, body .header-wrapper .callback-block:hover {{ color: {INK} !important; }}

body .header_wrap .right-icons, body .header-wrapper .right-icons {{
  margin-left: auto !important; display: flex !important; align-items: center !important;
  flex-direction: row-reverse !important;  gap: 8px !important; height: auto !important; float: none !important;
}}
body .header_wrap .right-icons > .pull-right, body .header-wrapper .right-icons > .pull-right {{
  float: none !important; margin: 0 !important; width: auto !important;
}}
body .header_wrap .right-icons .wrap_icon, body .header-wrapper .right-icons .wrap_icon {{
  width: auto !important; height: auto !important; padding: 0 !important; margin: 0 !important;
  display: block !important; border-radius: 0 !important; background: transparent !important;
}}
body .header_wrap .right-icons .top-btn, body .header-wrapper .right-icons .top-btn,
body .header_wrap .right-icons .personal-link, body .header-wrapper .right-icons .personal-link {{
  display: inline-flex !important; align-items: center !important; justify-content: center !important;
  gap: 9px !important; height: 42px !important; width: auto !important; min-width: 0 !important;
  padding: 0 16px !important; margin: 0 !important;
  border: 1px solid {LINE} !important; border-radius: 0 !important;
  background: transparent !important; box-shadow: none !important;
  font-family: "Golos Text", "Segoe UI", sans-serif !important; font-size: 13px !important; font-weight: 500 !important;
  letter-spacing: .01em !important; text-transform: none !important; color: {INK} !important;
  transition: border-color .2s ease, background-color .2s ease;
}}
body .header_wrap .right-icons .top-btn:hover, body .header-wrapper .right-icons .top-btn:hover,
body .header_wrap .right-icons .personal-link:hover, body .header-wrapper .right-icons .personal-link:hover {{
  border-color: {ACCENT} !important; background: {ACCENT_SOFT} !important; color: {INK} !important;
}}
body .header_wrap .right-icons svg, body .header-wrapper .right-icons svg {{
  width: 18px !important; height: 18px !important; margin: 0 !important;
}}
body .header_wrap .right-icons .svg, body .header-wrapper .right-icons .svg {{
  display: inline-flex !important; align-items: center !important; margin: 0 !important; position: static !important;
}}
body .header_wrap .right-icons .title, body .header-wrapper .right-icons .title,
body .header_wrap .right-icons .wrap, body .header-wrapper .right-icons .wrap,
body .header_wrap .right-icons .name, body .header-wrapper .right-icons .name {{
  display: inline !important; position: static !important; margin: 0 !important; padding: 0 !important;
  font-family: "Golos Text", "Segoe UI", sans-serif !important; font-size: 13px !important; font-weight: 500 !important;
  letter-spacing: .01em !important; text-transform: none !important; line-height: 1 !important;
  color: inherit !important;
}}

.ms-toast {{
  position: fixed; right: 24px; bottom: 24px; z-index: 5000;
  display: flex; align-items: center; gap: 18px;
  padding: 14px 18px 14px 20px; border-radius: 0;
  background: {PANEL}; color: {INK}; border: 1px solid {LINE};
  box-shadow: 0 24px 60px rgba(0, 0, 0, .55);
  transform: translateY(16px); opacity: 0; transition: transform .25s ease, opacity .25s ease;
  font-family: "Golos Text", "Segoe UI", sans-serif; font-size: 14px; max-width: min(420px, calc(100vw - 48px));
}}
.ms-toast.is-on {{ transform: none; opacity: 1; }}
.ms-toast__link {{
  flex: 0 0 auto; padding: 9px 16px; border-radius: 0;
  background: {ACCENT} !important; color: {ON_ACCENT} !important; font-weight: 600; font-size: 13px;
}}
.ms-toast__link:hover {{ background: {ACCENT_HOVER} !important; }}
.to-cart.ms-added {{ background: #3a2a22 !important; border-color: #3a2a22 !important; }}
.basket_count.ms-has-items, .wrap_basket .count.ms-has-items {{ background: {ACCENT} !important; color: {ON_ACCENT} !important; }}

.ms-basket-root {{ padding: 8px 0 40px; }}
.ms-cart {{ display: grid; grid-template-columns: minmax(0, 1fr) 340px; gap: 40px; align-items: start; }}
.ms-cart__list {{ display: flex; flex-direction: column; }}
.ms-item {{
  display: grid; grid-template-columns: 96px minmax(0, 1fr) auto auto auto;
  gap: 20px; align-items: center; padding: 18px 0;
  border-bottom: 1px solid {LINE};
}}
.ms-item__pic {{
  width: 96px; height: 96px; border-radius: 0; overflow: hidden;
  background: {TILE}; display: block;
}}
.ms-item__pic img {{ width: 100%; height: 100%; object-fit: cover; display: block; }}
.ms-item__name {{
  font-family: Prata, Georgia, serif !important; font-size: 19px !important;
  font-weight: 500 !important; color: {INK} !important; line-height: 1.25;
}}
.ms-item__meta {{ margin-top: 6px; font-size: 13px; color: {MUTED}; }}
.ms-item__sum {{ min-width: 92px; text-align: right; font-family: Prata, Georgia, serif; font-size: 21px; }}
.ms-item__remove {{
  width: 36px; height: 36px; border-radius: 0; border: 1px solid {LINE};
  background: transparent; color: {MUTED}; font-size: 20px; line-height: 1; cursor: pointer;
  transition: color .2s ease, border-color .2s ease;
}}
.ms-item__remove:hover {{ color: {INK}; border-color: {ACCENT}; }}
.ms-qty {{ display: inline-flex; align-items: stretch; height: 44px; border: 1px solid {LINE}; border-radius: 0; overflow: hidden; }}
.ms-qty__btn {{
  width: 38px; border: 0; background: transparent; color: {MUTED}; font-size: 18px; cursor: pointer;
}}
.ms-qty__btn:hover {{ color: {INK}; }}
.ms-qty__input {{
  width: 46px !important; border: 0 !important; background: transparent !important; text-align: center !important;
  padding: 0 !important; font-family: "Golos Text", "Segoe UI", sans-serif !important; font-size: 15px !important; font-weight: 600 !important;
  color: {INK} !important; border-radius: 0 !important; box-shadow: none !important;
}}

.ms-summary {{
  position: sticky; top: 118px;
  background: {CARD}; border: 1px solid {LINE}; border-radius: 0; padding: 24px;
}}
.ms-summary__row {{ display: flex; justify-content: space-between; font-size: 14px; color: {MUTED}; padding: 6px 0; }}
.ms-summary__row--total {{
  margin-top: 8px; padding-top: 16px; border-top: 1px solid {LINE};
  color: {INK}; font-family: Prata, Georgia, serif; font-size: 26px;
}}
.ms-summary__btn {{ display: flex !important; justify-content: center; width: 100%; margin-top: 18px; }}
.ms-summary__note {{ margin-top: 16px; font-size: 12px; line-height: 1.55; color: {MUTED}; }}

.ms-order {{ margin-top: 56px; padding-top: 40px; border-top: 1px solid {LINE}; }}
.ms-order__label, .ms-done__label {{
  font-size: 11px; font-weight: 600; letter-spacing: .14em; text-transform: uppercase; color: {GOLD}; margin-bottom: 10px;
}}
.ms-order__title, .ms-done__title {{
  font-family: Prata, Georgia, serif !important; font-size: clamp(26px, 2.8vw, 36px) !important;
  font-weight: 500 !important; margin: 0 0 26px !important; color: {INK} !important;
}}
.ms-form {{ display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 18px 24px; max-width: 860px; }}
.ms-field {{ display: flex; flex-direction: column; gap: 8px; }}
.ms-field > span {{ font-size: 12px; letter-spacing: .04em; color: {MUTED}; }}
.ms-field--wide {{ grid-column: 1 / -1; }}
.ms-field input[type="text"], .ms-field input[type="tel"] {{ width: 100%; }}
.ms-choice {{ display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 14px; }}
.ms-choice label {{
  display: grid; grid-template-columns: auto 1fr; grid-template-rows: auto auto; column-gap: 12px;
  padding: 14px 16px; border: 1px solid {LINE}; border-radius: 0; cursor: pointer; align-items: center;
  transition: border-color .2s ease;
}}
.ms-choice label:has(input:checked) {{ border-color: {ACCENT}; }}
.ms-choice input {{ grid-row: 1 / span 2; accent-color: {ACCENT}; width: 16px; height: 16px; margin: 0; }}
.ms-choice b {{ font-weight: 600; font-size: 15px; }}
.ms-choice small {{ font-size: 12px; color: {MUTED}; }}
.ms-form__foot {{ grid-column: 1 / -1; display: flex; align-items: center; gap: 22px; flex-wrap: wrap; margin-top: 6px; }}
.ms-form__hint {{ font-size: 13px; color: {MUTED}; }}
.ms-form__error {{ grid-column: 1 / -1; color: #e0596f; font-size: 14px; }}

.ms-empty {{ padding: 40px 0 20px; max-width: 520px; }}
.ms-empty__title {{ font-family: Prata, Georgia, serif; font-size: 30px; margin-bottom: 10px; }}
.ms-empty__text {{ color: {MUTED}; margin: 0 0 24px; }}

.ms-done {{ max-width: 720px; padding: 10px 0 20px; }}
.ms-done__text {{ font-size: 16px; line-height: 1.6; margin: 0 0 24px; }}
.ms-done__list {{ border-top: 1px solid {LINE}; margin-bottom: 26px; }}
.ms-done__row {{ display: flex; justify-content: space-between; gap: 20px; padding: 11px 0; border-bottom: 1px solid {LINE}; font-size: 15px; }}
.ms-done__row--total {{ font-family: Prata, Georgia, serif; font-size: 22px; }}
.ms-done__actions {{ display: flex; align-items: center; gap: 14px; flex-wrap: wrap; }}
.ms-done__phone {{ font-size: 16px; font-weight: 600; color: {INK} !important; margin-left: 6px; }}
.ms-done__note {{ margin: 26px 0 18px; font-size: 13px; line-height: 1.55; color: {MUTED}; }}
.ms-done__back {{ font-size: 14px; color: {MUTED} !important; text-decoration: underline; }}


@media (max-width: 991px) {{
  .ms-cart {{ grid-template-columns: 1fr; gap: 26px; }}
  .ms-summary {{ position: static; }}
  .ms-form, .ms-choice {{ grid-template-columns: 1fr; }}
}}
@media (max-width: 600px) {{
  .ms-item {{ grid-template-columns: 72px minmax(0, 1fr) auto; grid-template-rows: auto auto; gap: 12px 14px; }}
  .ms-item__pic {{ width: 72px; height: 72px; grid-row: 1 / span 2; }}
  .ms-item__remove {{ grid-column: 3; grid-row: 1; }}
  .ms-qty {{ grid-column: 2; grid-row: 2; height: 40px; }}
  .ms-item__sum {{ grid-column: 3; grid-row: 2; text-align: right; font-size: 18px; }}
  .ms-toast {{ right: 12px; left: 12px; bottom: 76px; max-width: none; }}
}}


@media (min-width: 992px) {{
  body .cat_sections.cat_sections .owl-stage {{
    grid-template-columns: repeat(4, minmax(0, 1fr)) !important;
    gap: 20px !important;
  }}
  body .cat_sections.cat_sections .owl-item:first-child {{ grid-column: span 2; grid-row: span 2; }}
  body .cat_sections.cat_sections .owl-item:first-child .item.compact .img.shine {{
    aspect-ratio: auto !important; height: 100% !important;
  }}
  body .cat_sections.cat_sections .owl-item:first-child .item.compact .name a {{ font-size: 28px !important; }}
}}
body .cat_sections.cat_sections .item.compact {{ position: relative; height: 100%; }}
body .cat_sections.cat_sections .item.compact .img.shine {{ aspect-ratio: 1 / 1; }}
body .cat_sections.cat_sections .item.compact .name {{
  position: absolute !important; left: 0; right: 0; bottom: 0;
  padding: 54px 20px 18px !important; text-align: left !important;
  background: linear-gradient(to top, rgba(18, 11, 8, .88) 0%, rgba(18, 11, 8, .55) 55%, rgba(18, 11, 8, 0) 100%);
  pointer-events: none;
}}
body .cat_sections.cat_sections .item.compact .name a {{
  color: #fff !important; pointer-events: auto; text-shadow: 0 1px 12px rgba(0, 0, 0, .5);
}}
@media (max-width: 991px) {{
  body .cat_sections.cat_sections .owl-item:first-child {{ grid-column: span 2; }}
  body .cat_sections.cat_sections .owl-item:first-child .item.compact .img.shine {{ aspect-ratio: 2 / 1 !important; }}
}}

body .CATALOG_SECTIONS {{ padding-top: clamp(40px, 4vw, 64px) !important; padding-bottom: clamp(30px, 3vw, 48px) !important; }}

body .CATALOG_TAB .tab_slider_wrapp .tabs {{ border-bottom: 1px solid {LINE} !important; margin-bottom: 26px !important; }}
body .CATALOG_TAB .tab_slider_wrapp .tabs li a, body .CATALOG_TAB .nav-tabs li a {{
  font-family: Prata, Georgia, serif !important; font-size: 26px !important;
  font-weight: 500 !important; text-transform: none !important; letter-spacing: -.01em !important;
  padding: 0 0 14px !important; background: transparent !important; border: 0 !important;
  color: {MUTED} !important;
}}
body .CATALOG_TAB .tabs li.cur a, body .CATALOG_TAB .nav-tabs li.active a {{
  color: {INK} !important; box-shadow: inset 0 -2px 0 {ACCENT} !important;
}}

body .COMPANY_TEXT .company-block .row.flexbox {{ align-items: stretch !important; margin: 0 !important; width: 100% !important; }}
body .COMPANY_TEXT .text-block .item, body .COMPANY_TEXT .text-block .item-inner {{ width: 100% !important; }}
body .COMPANY_TEXT .text-block .text {{
  width: 100% !important; max-width: 560px !important; margin: 0 !important; padding: 0 40px 0 0 !important;
  font-size: 16px !important; line-height: 1.7 !important;
}}
body .COMPANY_TEXT .text-block .text p {{ font-size: 16px !important; line-height: 1.7 !important; }}
body .COMPANY_TEXT .image-block .item.video-block {{
  width: 100% !important; min-height: 360px !important; height: 100% !important;
  border-radius: 0 !important; overflow: hidden;
  background: {PANEL} url("/assets/about.jpg?v=1") center / cover no-repeat !important;
  border: 1px solid {LINE} !important;
}}
body .COMPANY_TEXT {{ padding-top: clamp(56px, 6vw, 96px) !important; padding-bottom: clamp(56px, 6vw, 96px) !important; }}
@media (max-width: 991px) {{
  body .COMPANY_TEXT .text-block .text {{ max-width: none !important; padding: 0 0 26px !important; }}
  body .COMPANY_TEXT .image-block .item.video-block {{ min-height: 240px !important; }}
}}

body .TIZERS .item {{ padding: 26px 18px !important; }}
body .TIZERS .item .icon, body .TIZERS .item .icon svg, body .TIZERS .item svg {{ color: {GOLD} !important; }}
body .TIZERS .item .title {{
  font-family: Prata, Georgia, serif !important; font-size: 19px !important;
  font-weight: 500 !important; margin: 14px 0 8px !important; text-transform: none !important;
}}
body .TIZERS .item .text, body .TIZERS .item .muted {{ font-size: 14px !important; line-height: 1.55 !important; color: {MUTED} !important; }}

body .footer-inner .footer_top {{ padding: 56px 0 40px !important; }}
body .footer-inner .footer_middle {{ display: none !important; }}
body .footer-inner .footer_bottom {{ padding: 20px 0 !important; border-top: 1px solid rgba(243, 232, 216, .08) !important; }}
body .footer-inner .footer_bottom, body .footer-inner .footer_bottom * {{ font-size: 12px !important; }}
body footer .bottom-menu li a, body footer .footer_top .menu li a {{ font-size: 14px !important; line-height: 1.5 !important; }}

.item_block:hover .catalog_item, .catalog_item_wrapp:hover .catalog_item {{ border-color: {LINE} !important; }}
body .cat_sections.cat_sections .item.compact:hover {{ border-color: {LINE} !important; }}

.btn.wish_item, .btn.compare_item, .wish_item.btn, .compare_item.btn,
.btn.btn-search, button.btn-search, .btn.subscribe, .btn[class*="icon_"], .btn.close,
body .search-button-div .btn, body .search-button-div button {{
  border: 0 !important; background: {CARD} !important;
}}
.btn.wish_item:hover, .btn.compare_item:hover, .wish_item.btn:hover, .compare_item.btn:hover,
.btn.btn-search:hover, button.btn-search:hover,
body .search-button-div .btn:hover, body .search-button-div button:hover {{
  border: 0 !important; background: {ACCENT} !important; color: {ON_ACCENT} !important;
}}

body .header_wrap .right-icons .top-btn, body .header-wrapper .right-icons .top-btn,
body .header_wrap .right-icons .personal-link, body .header-wrapper .right-icons .personal-link {{
  border: 0 !important; padding: 0 12px !important; background: transparent !important;
}}
body .header_wrap .right-icons .top-btn:hover, body .header-wrapper .right-icons .top-btn:hover,
body .header_wrap .right-icons .personal-link:hover, body .header-wrapper .right-icons .personal-link:hover {{
  border: 0 !important; background: transparent !important; color: {ACCENT_HOVER} !important;
}}
body .header_wrap .logo-row .burger:hover, body .header-wrapper .logo-row .burger:hover,
.header_wrap .wrap_icon:hover, .header_wrap .burger:hover, .header_wrap .menu-burger:hover {{
  background: transparent !important; color: {ACCENT_HOVER} !important;
}}

.btn, .btn.btn-default, .btn.btn-lg, .btn.btn-sm, .btn.btn-xs, button.btn, input[type=submit] {{
  font-family: "Golos Text", "Segoe UI", sans-serif !important;
  font-size: 12px !important; font-weight: 600 !important;
  letter-spacing: .14em !important; text-transform: uppercase !important;
  line-height: 1 !important; padding: 18px 32px !important;
}}
.btn.btn-lg {{ padding: 20px 38px !important; }}
.btn.btn-sm, .btn.btn-xs {{ padding: 13px 18px !important; font-size: 11px !important; }}
.btn.btn-transparent, .btn.btn-default.transparent, .btn.btn-default.white {{
  color: {GOLD} !important; border-color: {GOLD_LINE} !important; background: transparent !important;
}}
.btn.btn-transparent:hover, .btn.btn-default.transparent:hover, .btn.btn-default.white:hover {{
  color: {ON_ACCENT} !important; background: {ACCENT} !important; border-color: {ACCENT} !important;
}}

.logo svg .st0, .logo svg .st1, .logo svg path, .logo svg polygon {{ fill: {GOLD} !important; }}
body .header_wrap .logo-row .float_wrapper .hidden-sm,
body .header-wrapper .logo-row .float_wrapper .hidden-sm {{
  font-size: 11px !important; letter-spacing: .12em !important; text-transform: uppercase !important;
  line-height: 1.5 !important; max-width: 200px !important;
}}
body .header_wrap .phone > a, body .header-wrapper .phone > a {{
  font-size: 17px !important; font-weight: 500 !important; letter-spacing: 0 !important;
}}
body .header_wrap .right-icons .title, body .header-wrapper .right-icons .title,
body .header_wrap .right-icons .wrap, body .header-wrapper .right-icons .wrap,
body .header_wrap .right-icons .name, body .header-wrapper .right-icons .name {{
  font-size: 11px !important; font-weight: 600 !important;
  letter-spacing: .14em !important; text-transform: uppercase !important;
}}
.header_wrap, .header-wrapper, header > .header-wrapper {{
  box-shadow: 0 1px 0 {LINE} !important;
}}

.item_block .catalog_item, .catalog_item_wrapp .catalog_item, .product-item-container {{
  background: {CARD} !important; border: 1px solid {LINE} !important; padding: 16px 16px 18px !important;
}}
.item_block:hover .catalog_item, .catalog_item_wrapp:hover .catalog_item {{
  border-color: {LINE} !important; box-shadow: 0 24px 50px rgba(0, 0, 0, .5) !important; transform: translateY(-2px);
}}
.catalog_item .image_wrapper_block, .product-item-image-wrapper {{
  background: {TILE} !important; border: 1px solid {LINE} !important;
}}
@media (min-width: 768px) {{
  .item_block .catalog_item, .catalog_item_wrapp .catalog_item {{ padding: 16px 16px 18px !important; }}
  .item-title a, .product-item-title a {{ font-size: 20px !important; }}
  .catalog_item .price, .price_value {{ font-size: 22px !important; }}
}}
.item-title a, .product-item-title a {{ font-family: Prata, Georgia, serif !important; font-weight: 400 !important; }}
.catalog_item .price, .price_matrix_wrapper .price, .product-item-price-current, .price_value,
.catalog_item .price .price_value, .catalog_item .price .price_currency {{
  color: {GOLD} !important; font-family: Prata, Georgia, serif !important; font-weight: 400 !important;
}}
.catalog_item .footer_button .btn, .catalog_item .footer_button .btn.to-cart,
.catalog_item .footer_button .btn.btn-default {{
  background: transparent !important; border: 1px solid rgba(243, 232, 216, .22) !important;
  color: {INK} !important; font-size: 11px !important; padding: 14px 16px !important;
}}
.catalog_item .footer_button .btn:hover, .catalog_item .footer_button .btn.to-cart:hover {{
  background: {ACCENT} !important; border-color: {ACCENT} !important; color: {ON_ACCENT} !important;
}}
.catalog_item .footer_button .btn.ms-added, .to-cart.ms-added {{
  background: {ACCENT_SOFT} !important; border-color: {GOLD_LINE} !important; color: {GOLD} !important;
}}

body .product-detail-gallery .product-detail-gallery__item {{
  background: {TILE} !important; border: 1px solid {LINE} !important;
}}
body .product-detail-gallery__thmb-inner > * {{ width: 84px !important; height: 84px !important; }}
body .detail .prices_block .price_value, body .detail .prices_block .price_currency,
body .detail .price_value {{
  color: {GOLD} !important; font-family: Prata, Georgia, serif !important; font-weight: 400 !important;
}}
body .product-main .product-chars {{ border-top: 1px solid {GOLD_LINE} !important; }}
body .product-chars .properties__item {{ grid-template-columns: 180px 1fr; padding: 13px 0 !important; }}
body .product-chars .properties__value {{ font-size: 15px !important; }}
body .detail .buy_block .btn {{ padding: 20px 30px !important; }}
body .bottom-info .tabs .nav-tabs > li > a {{
  font-size: 11px !important; font-weight: 600 !important;
  letter-spacing: .14em !important; text-transform: uppercase !important;
}}
body .bottom-info .tabs .nav-tabs > li.active > a {{ box-shadow: inset 0 -1px 0 {GOLD} !important; }}

.top_slider_wrapp .slides > li .banner_title .head-title {{
  font-family: Prata, Georgia, serif !important; font-weight: 400 !important;
  font-size: clamp(38px, 5vw, 76px) !important; line-height: 1.04 !important;
  letter-spacing: 0 !important; text-transform: none !important; color: {INK} !important;
}}
.top_slider_wrapp .slides > li .banner_title {{ color: {INK} !important; }}
.top_slider_wrapp .slides > li .banner_text {{
  color: rgba(243, 232, 216, .65) !important; font-size: 17px !important; line-height: 1.65 !important;
  max-width: 460px;
}}
.top_slider_wrapp td.img img {{ max-width: min(44vw, 660px) !important; }}

body .cat_sections.cat_sections .owl-stage {{
  display: flex !important; flex-wrap: wrap !important; justify-content: center !important;
  gap: 16px !important;
}}
body .cat_sections.cat_sections .owl-item {{ width: calc((100% - 5 * 16px) / 6) !important; }}
body .cat_sections.cat_sections .owl-item:first-child {{ grid-column: auto; grid-row: auto; }}
body .cat_sections.cat_sections .item.compact,
body .cat_sections.cat_sections .item.compact:hover {{
  background: transparent !important; border: 0 !important; box-shadow: none !important; transform: none !important;
}}
body .cat_sections.cat_sections .item.compact .img.shine,
body .cat_sections.cat_sections .owl-item:first-child .item.compact .img.shine {{
  aspect-ratio: 1 / 1 !important; height: auto !important;
  border: 1px solid {LINE} !important; background: {TILE} !important;
}}
body .cat_sections.cat_sections .item.compact:hover .img.shine img {{ transform: scale(1.03); }}
body .cat_sections.cat_sections .item.compact .name {{
  position: static !important; padding: 14px 0 0 !important;
  background: none !important; text-align: left !important; pointer-events: auto;
}}
body .cat_sections.cat_sections .item.compact .name a,
body .cat_sections.cat_sections .owl-item:first-child .item.compact .name a {{
  font-family: Prata, Georgia, serif !important; font-weight: 400 !important;
  font-size: 20px !important; color: {INK} !important; text-shadow: none !important;
}}
@media (max-width: 1199px) {{
  body .cat_sections.cat_sections .owl-item {{ width: calc((100% - 3 * 16px) / 4) !important; }}
}}
@media (max-width: 600px) {{
  body .cat_sections.cat_sections .owl-item {{ width: calc((100% - 12px) / 2) !important; }}
  body .cat_sections.cat_sections .owl-stage {{ gap: 12px !important; }}
  body .cat_sections.cat_sections .item.compact .name a {{ font-size: 16px !important; }}
}}


@media (min-width: 1200px) {{
  body .CATALOG_TAB .catalog_block.items.row {{ grid-template-columns: repeat(4, minmax(0, 1fr)) !important; gap: 16px !important; }}
}}
body .CATALOG_TAB .tab_slider_wrapp .tabs {{ border-bottom: 1px solid {GOLD_LINE} !important; }}
body .CATALOG_TAB .tab_slider_wrapp .tabs li a, body .CATALOG_TAB .nav-tabs li a {{
  font-family: Prata, Georgia, serif !important; font-weight: 400 !important; font-size: 34px !important;
}}
body .CATALOG_TAB .tabs li.cur a, body .CATALOG_TAB .nav-tabs li.active a {{ box-shadow: none !important; }}

body .COMPANY_TEXT .company-block .row.flexbox {{ border: 1px solid {GOLD_LINE} !important; }}
body .COMPANY_TEXT .text-block .item, body .COMPANY_TEXT .text-block .item-inner {{ height: 100% !important; }}
body .COMPANY_TEXT .text-block .text {{ padding: 52px 56px 52px 8px !important; }}
body .COMPANY_TEXT .image-block .item.video-block {{
  border: 0 !important; border-left: 1px solid {GOLD_LINE} !important; min-height: 420px !important;
  background-image: url("/assets/about.jpg?v=2") !important;
}}
body .COMPANY_TEXT .company-block .title, body .COMPANY_TEXT .top_block .title {{ font-size: clamp(30px, 3vw, 44px) !important; }}
@media (max-width: 991px) {{
  body .COMPANY_TEXT .text-block .text {{ padding: 28px 24px !important; }}
  body .COMPANY_TEXT .image-block .item.video-block {{ border-left: 0 !important; border-top: 1px solid {GOLD_LINE} !important; min-height: 260px !important; }}
}}

body .TIZERS .item {{ text-align: left !important; padding: 22px 0 0 !important; border-top: 1px solid {GOLD_LINE} !important; }}
body .TIZERS .item .image {{ display: none !important; }}
body .TIZERS .item .title {{ font-family: Prata, Georgia, serif !important; font-weight: 400 !important; font-size: 22px !important; margin: 0 0 10px !important; }}
body .TIZERS .item .value, body .TIZERS .item .text {{ font-size: 14px !important; line-height: 1.65 !important; color: {MUTED} !important; }}
body .TIZERS .item-wrapper {{ padding-left: 20px !important; padding-right: 20px !important; }}

.ms-item__name, .ms-item__sum, .ms-summary__row--total, .ms-done__row--total, .ms-empty__title {{
  font-family: Prata, Georgia, serif !important; font-weight: 400 !important;
}}
.ms-item__sum, .ms-summary__row--total {{ color: {GOLD}; }}
.ms-summary {{ background: transparent; border: 1px solid {GOLD_LINE}; }}
.ms-toast__link {{ font-size: 11px; letter-spacing: .14em; text-transform: uppercase; padding: 11px 16px; }}
.ms-item__pic {{ border: 1px solid {LINE}; }}

.footer_inner, .footer-block, footer.footer, .footer_bottom {{ background: #0c0705 !important; }}
body .footer-inner .footer_top {{ border-top: 1px solid {LINE} !important; }}

.stickers > div:not([class*="sticker_"]) {{
  background: transparent !important; padding: 0 !important; margin: 0 0 6px !important; box-shadow: none !important;
}}
body .cat_sections.cat_sections .item.compact .name a {{ display: block !important; text-transform: lowercase !important; }}
body .cat_sections.cat_sections .item.compact .name a::first-letter {{ text-transform: uppercase !important; }}
body .CATALOG_SECTIONS .sections_wrapper {{ padding-bottom: 0 !important; }}
body .CATALOG_SECTIONS {{ padding-bottom: 24px !important; }}
body .catalog_item .item-title a {{ display: block !important; text-transform: lowercase !important; }}
body .catalog_item .item-title a::first-letter {{ text-transform: uppercase !important; }}

.page-top, .section-content-wrapper > .page-top {{ padding: 40px 16px 10px !important; }}
.catalog_page_detail .page-top, .catalog_page .page-top {{ padding-left: 30px !important; padding-right: 30px !important; }}
.ms-basket-root {{ padding: 8px 16px 40px; }}
.page-top .topic, h1#pagetitle, .detail .topic h1 {{ text-transform: lowercase !important; }}
.page-top .topic::first-letter, h1#pagetitle::first-letter {{ text-transform: uppercase !important; }}
.drag-block.SALE:not(:has(*)), .drag-block.REVIEWS:not(:has(*)) {{ display: none !important; }}

.item_block .catalog_item, .catalog_item_wrapp .catalog_item, .product-item-container,
.catalog_item .image_wrapper_block, .product-item-image-wrapper,
body .cat_sections.cat_sections .item.compact .img.shine,
body .cat_sections.cat_sections .owl-item:first-child .item.compact .img.shine,
body .product-detail-gallery .product-detail-gallery__item,
body .product-detail-gallery__thmb-inner > *,
.ms-item__pic, .ms-summary, body .bottom-info-wrapper .side-block {{ border: 0 !important; }}
body .product-detail-gallery__thmb-inner > .active {{ box-shadow: inset 0 0 0 1px {GOLD} !important; }}
body .counter_wrapp .counter_block, body .counter_block.md, body .counter_block {{
  border: 0 !important; background: {FIELD} !important;
}}
.catalog_item .footer_button .btn, .catalog_item .footer_button .btn.to-cart,
.catalog_item .footer_button .btn.btn-default {{
  border: 0 !important; background: #2a1d17 !important;
}}
.catalog_item .footer_button .btn:hover, .catalog_item .footer_button .btn.to-cart:hover {{
  background: {ACCENT} !important; color: {ON_ACCENT} !important;
}}
.header_wrap, .header-wrapper, header > .header-wrapper {{ box-shadow: none !important; }}
input[type="text"], input[type="tel"], input[type="email"], input[type="password"],
input[type="search"], input[type="number"], textarea, select, .form-control, .input-group .form-control {{
  border-color: transparent !important;
}}
input:focus, textarea:focus, select:focus, .form-control:focus {{ border-color: {GOLD_LINE} !important; box-shadow: none !important; }}
.ms-qty, .ms-item__remove, .ms-choice label {{ border-color: transparent !important; background: {FIELD}; }}
.ms-choice label:has(input:checked) {{ border-color: {GOLD_LINE} !important; }}
.btn.wish_item, .btn.compare_item, .wish_item.btn, .compare_item.btn, .btn.btn-search, button.btn-search {{ background: #2a1d17 !important; }}

.content_wrapper_block, .block_container.bordered, .contacts_map.bordered, .basket_sort,
.map_type_2 .item, .item.initied, .footer_top, .bordered {{ border-color: transparent !important; }}
.footer-inner, .footer-inner .maxwidth-theme, footer .maxwidth-theme, .footer_top, .footer_bottom,
.footer_inner, .footer-block, footer.footer {{ background: #0c0705 !important; }}
.footer_bottom {{ border-top: 0 !important; }}
.footer_bottom .pays a {{ display: none !important; }}
.footer_bottom .pays i {{ opacity: .45; }}
footer .btn, footer span.btn {{ background: {ACCENT} !important; border-color: {ACCENT} !important; color: {ON_ACCENT} !important; }}
"""


def main():
    css = re.sub(r"/\*.*?\*/", "", fetch_css(), flags=re.S)
    rules = recolor(css)
    dark = redark(css)

    body = (FONTS
            + "\n\n"
            + "\n".join(rules) + "\n"
            + "\n\n"
            + "\n".join(dark) + "\n" + MANUAL + LAYOUT)

    with open(OUT, "w", encoding="utf-8", newline="\n") as f:
        f.write(body)

    print(f"recolored rules: {len(rules)}, darkened: {len(dark)}")
    print(f"skin.css size: {os.path.getsize(OUT) // 1024} KB")
    print("written:", OUT)


if __name__ == "__main__":
    main()
