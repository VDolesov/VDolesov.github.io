import hashlib
import os
import re
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
SITE = "https://www.mirsladostey164.ru"
APP = os.path.dirname(HERE)
CACHE = os.path.join(HERE, "cache")
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


def bundle_urls():
    order = {"kernel": 0, "template": 1, "page": 2, "default": 3, "components": 4}
    seen = {}
    for root, dirs, files in os.walk(APP):
        dirs[:] = [d for d in dirs if d not in (".git", "skin", "build", "assets")]
        if "index.html" not in files:
            continue
        html = open(os.path.join(root, "index.html"), encoding="utf-8", errors="ignore").read()
        links = re.findall(r'<link[^>]+href="([^"]+\.css)[^"]*"', html)
        links += [SITE + u for u in re.findall(r"'(/bitrix/templates/aspro_max/[^']+\.css)[^']*'", html)]
        for url in links:
            if "aspro_max" not in url:
                continue
            kind = next((k for k in order if "/" + k in url or "/" + k + "_" in url), "components")
            seen.setdefault(url, (order[kind], len(seen)))
    return [u for u, _ in sorted(seen.items(), key=lambda kv: kv[1])]


def fetch_css():
    os.makedirs(CACHE, exist_ok=True)
    parts = []
    for url in bundle_urls():
        name = hashlib.md5(url.encode()).hexdigest()[:12] + ".css"
        path = os.path.join(CACHE, name)
        if not os.path.exists(path):
            try:
                css = urllib.request.urlopen(
                    urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"}),
                    timeout=90).read().decode("utf-8", "ignore")
            except Exception as exc:
                print(f"  skip {url}: {exc}")
                continue
            open(path, "w", encoding="utf-8").write(css)
        parts.append(open(path, encoding="utf-8", errors="ignore").read())
    return "\n".join(parts)


def recolor(css):
    pattern = re.compile(r"([^{}]+)\{([^{}]*)\}")
    targets = tuple(COLOR_MAP)
    rules = []
    seen = set()
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
            rule = f"{selector}{{{';'.join(kept)}}}"
            if rule not in seen:
                seen.add(rule)
                rules.append(rule)
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
    if "border" in prop or "outline" in prop or prop == "box-shadow":
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
    seen = set()
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
            rule = " ".join(selector.split()) + "{" + ";".join(kept) + "}"
            if rule not in seen:
                seen.add(rule)
                rules.append(rule)
    return rules

FONTS = """@import url("https://fonts.googleapis.com/css2?family=Prata&family=Golos+Text:wght@400;500;600&display=swap");
@font-face {
  font-family: "Golos Digits";
  src: url("fonts/golos-text-latin.woff2") format("woff2");
  font-weight: 400 900;
  font-display: swap;
  unicode-range: U+0030-0039;
}
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
  font-family: "Golos Digits", Prata, Georgia, serif !important;
  font-weight: 400 !important;
  letter-spacing: 0;
  text-transform: none !important;
  color: {INK} !important;
}}
.topic, .page-top .topic {{ font-size: clamp(34px, 4vw, 56px) !important; line-height: 1.08 !important; }}
h1 {{ font-size: clamp(32px, 3.6vw, 50px); line-height: 1.1; }}
@media (max-width: 400px) {{ h1, h1#pagetitle {{ font-size: 26px !important; }} }}
body .topic__heading, body .topic__inner {{ overflow: visible !important; white-space: normal !important; }}
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
  font-family: "Golos Digits", Prata, Georgia, serif !important;
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
  display: flex !important; gap: 14px; align-items: stretch; flex-wrap: wrap; width: auto !important;
}}
body .detail .buy_block .counter_block_inner {{ flex: 0 0 auto; width: auto !important; margin: 0 !important; }}
body .detail .buy_block .counter_block_inner .counter_block {{ width: 136px !important; }}
body .detail .buy_block .button_block {{ flex: 1 0 150px; width: auto !important; min-width: 0; margin: 0 !important; }}
body .detail .buy_block .btn {{
  display: flex; width: 100% !important; min-width: 0 !important; justify-content: center; align-items: center;
  padding: 0 22px !important; font-size: 12px !important; height: 56px !important; line-height: 56px !important;
  white-space: nowrap !important;
}}
body .detail .buy_block .btn[style*="none"] {{ display: none !important; }}

body .char-side__title {{
  font-family: "Golos Digits", Prata, Georgia, serif !important;
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
  font-family: "Golos Digits", Prata, Georgia, serif !important;
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
  font-family: "Golos Digits", Prata, Georgia, serif !important;
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
  width: auto !important; height: 42px !important; padding: 0 16px !important;
  min-width: 42px !important; border-radius: 0 !important; overflow: visible !important;
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
.to-cart.ms-added, .btn.btn-default.to-cart.ms-added {{ background: #3a2a22 !important; border-color: #3a2a22 !important; color: {INK} !important; }}
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
  font-family: "Golos Digits", Prata, Georgia, serif !important; font-size: 19px !important;
  font-weight: 500 !important; color: {INK} !important; line-height: 1.25;
}}
.ms-item__meta {{ margin-top: 6px; font-size: 13px; color: {MUTED}; }}
.ms-item__sum {{ min-width: 92px; text-align: right; font-family: "Golos Digits", Prata, Georgia, serif; font-size: 21px; }}
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
  color: {INK}; font-family: "Golos Digits", Prata, Georgia, serif; font-size: 26px;
}}
.ms-summary__btn {{ display: flex !important; justify-content: center; width: 100%; margin-top: 18px; }}
.ms-summary__note {{ margin-top: 16px; font-size: 12px; line-height: 1.55; color: {MUTED}; }}

.ms-order {{ margin-top: 56px; padding-top: 40px; border-top: 1px solid {LINE}; }}
.ms-order__label, .ms-done__label {{
  font-size: 11px; font-weight: 600; letter-spacing: .14em; text-transform: uppercase; color: {GOLD}; margin-bottom: 10px;
}}
.ms-order__title, .ms-done__title {{
  font-family: "Golos Digits", Prata, Georgia, serif !important; font-size: clamp(26px, 2.8vw, 36px) !important;
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
.ms-empty__title {{ font-family: "Golos Digits", Prata, Georgia, serif; font-size: 30px; margin-bottom: 10px; }}
.ms-empty__text {{ color: {MUTED}; margin: 0 0 24px; }}

.ms-done {{ max-width: 720px; padding: 10px 0 20px; }}
.ms-done__text {{ font-size: 16px; line-height: 1.6; margin: 0 0 24px; }}
.ms-done__list {{ border-top: 1px solid {LINE}; margin-bottom: 26px; }}
.ms-done__row {{ display: flex; justify-content: space-between; gap: 20px; padding: 11px 0; border-bottom: 1px solid {LINE}; font-size: 15px; }}
.ms-done__row--total {{ font-family: "Golos Digits", Prata, Georgia, serif; font-size: 22px; }}
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
  font-family: "Golos Digits", Prata, Georgia, serif !important; font-size: 26px !important;
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
  font-family: "Golos Digits", Prata, Georgia, serif !important; font-size: 19px !important;
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
.item-title a, .product-item-title a {{ font-family: "Golos Digits", Prata, Georgia, serif !important; font-weight: 400 !important; }}
.catalog_item .price, .price_matrix_wrapper .price, .product-item-price-current, .price_value,
.catalog_item .price .price_value, .catalog_item .price .price_currency {{
  color: {GOLD} !important; font-family: "Golos Digits", Prata, Georgia, serif !important; font-weight: 400 !important;
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
  color: {GOLD} !important; font-family: "Golos Digits", Prata, Georgia, serif !important; font-weight: 400 !important;
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
  font-family: "Golos Digits", Prata, Georgia, serif !important; font-weight: 400 !important;
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
  font-family: "Golos Digits", Prata, Georgia, serif !important; font-weight: 400 !important;
  font-size: 20px !important; color: {INK} !important; text-shadow: none !important;
}}
@media (max-width: 1199px) {{
  body .cat_sections.cat_sections .owl-item {{ width: calc((100% - 3 * 16px) / 4) !important; }}
}}
@media (max-width: 600px) {{
  body .cat_sections.cat_sections .owl-item {{ width: calc((100% - 12px) / 2) !important; }}
  body .cat_sections.cat_sections .owl-stage {{ gap: 12px !important; }}
  body .cat_sections.cat_sections .item.compact .name a,
  body .cat_sections.cat_sections .owl-item:first-child .item.compact .name a {{ font-size: 16px !important; }}
}}


@media (min-width: 1200px) {{
  body .CATALOG_TAB .catalog_block.items.row {{ grid-template-columns: repeat(4, minmax(0, 1fr)) !important; gap: 16px !important; }}
}}
body .CATALOG_TAB .tab_slider_wrapp .tabs {{ border-bottom: 1px solid {GOLD_LINE} !important; }}
body .CATALOG_TAB .tab_slider_wrapp .tabs li a, body .CATALOG_TAB .nav-tabs li a {{
  font-family: "Golos Digits", Prata, Georgia, serif !important; font-weight: 400 !important; font-size: 34px !important;
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
body .TIZERS .item .title {{ font-family: "Golos Digits", Prata, Georgia, serif !important; font-weight: 400 !important; font-size: 22px !important; margin: 0 0 10px !important; }}
body .TIZERS .item .value, body .TIZERS .item .text {{ font-size: 14px !important; line-height: 1.65 !important; color: {MUTED} !important; }}
body .TIZERS .item-wrapper {{ padding-left: 20px !important; padding-right: 20px !important; }}

.ms-item__name, .ms-item__sum, .ms-summary__row--total, .ms-done__row--total, .ms-empty__title {{
  font-family: "Golos Digits", Prata, Georgia, serif !important; font-weight: 400 !important;
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

.item_block .catalog_item, .catalog_item_wrapp .catalog_item, .product-item-container {{
  background: transparent !important; padding: 0 0 6px !important;
}}
.item_block:hover .catalog_item, .catalog_item_wrapp:hover .catalog_item {{ box-shadow: none !important; transform: none !important; }}
.catalog_item .image_wrapper_block, .product-item-image-wrapper,
body .cat_sections.cat_sections .item.compact .img.shine,
body .cat_sections.cat_sections .owl-item:first-child .item.compact .img.shine,
body .product-detail-gallery .product-detail-gallery__item,
body .product-detail-gallery__thmb-inner > *, .ms-item__pic {{ background: {GROUND} !important; }}
.catalog_item .item-title, .product-item-title {{ margin-top: 16px !important; }}
.catalog_item .article_block, .catalog_item .article {{ display: none !important; }}
.catalog_item .footer_button {{ margin-top: 12px !important; }}
.item_block .catalog_item .stickers, .catalog_item .stickers {{ left: 0 !important; top: 0 !important; }}

@media (min-width: 1200px) {{
  body .cat_sections.cat_sections .owl-item {{ width: calc((100% - 8 * 14px) / 9) !important; }}
  body .cat_sections.cat_sections .owl-stage {{ gap: 14px !important; justify-content: flex-start !important; }}
  body .cat_sections.cat_sections .item.compact .name a,
  body .cat_sections.cat_sections .owl-item:first-child .item.compact .name a {{ font-size: 17px !important; }}
}}
body .cat_sections.cat_sections .item.compact .name {{ padding: 12px 0 0 !important; }}
body .CATALOG_SECTIONS .sections_wrapper::before {{
  content: "Что печём"; display: block;
  font-family: "Golos Digits", Prata, Georgia, serif; font-size: clamp(26px, 2.8vw, 40px); line-height: 1.1;
  color: {INK}; margin: 0 0 26px;
}}
body .CATALOG_SECTIONS {{ padding-top: clamp(48px, 5vw, 72px) !important; }}

body .product-info-headnote .rating, body .product-info .rating {{ display: none !important; }}
body .wrapper_inner > .left_block.product-side {{ display: none !important; }}
body .ordered-block.goods:not(:has(.catalog_item)) {{ display: none !important; }}
body .bottom-info .ordered-block.goods {{ margin-top: 40px !important; }}

body .MAPS [class*="ground-pane"] {{ filter: grayscale(1) invert(.92) brightness(.72) contrast(.92) sepia(.35); }}
body .MAPS .contacts_map, body .MAPS .map_type_2 .items {{ background: {PANEL} !important; }}
body .MAPS {{ padding-bottom: clamp(40px, 4vw, 64px) !important; }}
footer .btn, footer span.btn {{ border-radius: 0 !important; }}
body .footer-inner .footer_top {{ padding: 48px 0 36px !important; }}

.catalog_item .inner_wrap, .catalog_item_wrapp .inner_wrap {{ box-shadow: none !important; }}
body .cat_sections.cat_sections .item.compact .name a {{ white-space: normal !important; text-overflow: clip !important; overflow: visible !important; line-height: 1.25 !important; hyphens: auto; overflow-wrap: break-word; }}
body .cat_sections.cat_sections .item.compact, body .cat_sections.cat_sections .item.compact .name {{ overflow: visible !important; }}

body .catalog_block .item, body .catalog_item_wrapp.catalog_item, body .item_block .catalog_item,
body .catalog_item .inner_wrap, body .catalog_item .item_info {{ height: auto !important; min-height: 0 !important; }}
body .catalog_item .inner_wrap {{ display: flex !important; flex-direction: column !important; }}
body .catalog_item .footer_button {{ margin-top: 14px !important; }}

.catalog_item .rating, .item_block .rating, .votes_block, .product-item-container .rating {{ display: none !important; }}
body .left_block .menu_top_block .slide-block__head {{
  font-family: "Golos Text", "Segoe UI", sans-serif !important; font-size: 11px !important; font-weight: 600 !important;
  letter-spacing: .14em !important; text-transform: uppercase !important; color: {GOLD} !important;
  padding: 0 0 14px !important; background: transparent !important;
}}
body .left_block .menu_top_block ul.menu > li > a {{
  background: transparent !important; border: 0 !important; padding: 9px 0 !important;
  font-family: "Golos Digits", Prata, Georgia, serif !important; font-size: 17px !important; font-weight: 400 !important;
  text-transform: lowercase !important; letter-spacing: 0 !important; color: {INK} !important;
}}
body .left_block .menu_top_block ul.menu > li > a .name {{ display: inline-block !important; }}
body .left_block .menu_top_block ul.menu > li > a .name::first-letter {{ text-transform: uppercase !important; }}
body .left_block .menu_top_block ul.menu > li.current > a, body .left_block .menu_top_block ul.menu > li > a:hover {{ color: {GOLD} !important; }}
body .left_block .menu_top_block ul.menu > li > a .toggle_block {{ display: none !important; }}
body .left_block .subscribe-block, body .left_block .side-block {{ background: transparent !important; border: 0 !important; padding: 28px 0 0 !important; }}
body .page-top .topic .count, body .topic .topic__count, body .page-top .count {{
  font-family: "Golos Text", "Segoe UI", sans-serif !important; font-size: 13px !important; color: {MUTED} !important;
  background: transparent !important; border: 0 !important; vertical-align: super; margin-left: 6px;
}}
body .filter-panel .filter_title span, body .filter-panel .dropdown-select__title {{ font-size: 13px !important; color: {MUTED} !important; }}

body [class*="ground-pane"] {{ filter: grayscale(1) invert(.92) brightness(.72) contrast(.92) sepia(.35); }}
body .contacts img, body .contacts_block img {{ filter: none; }}

@media (max-width: 600px) {{
  body .cat_sections.cat_sections .owl-item {{ width: calc((100% - 2 * 10px) / 3) !important; }}
  body .cat_sections.cat_sections .owl-stage {{ gap: 10px !important; justify-content: flex-start !important; }}
  body .cat_sections.cat_sections .item.compact .name a,
  body .cat_sections.cat_sections .owl-item:first-child .item.compact .name a {{ font-size: 14px !important; }}
  body .cat_sections.cat_sections .item.compact .name {{ padding-top: 8px !important; }}
}}

.ms-nav {{ display: none; }}
@media (min-width: 992px) {{
  .ms-nav {{ display: block; border-top: 1px solid rgba(243, 232, 216, .06); }}
  .ms-nav__inner {{
    display: flex; align-items: center; gap: 4px; flex-wrap: wrap;
    max-width: 1400px; margin: 0 auto; padding: 0 16px; min-height: 46px;
  }}
  .ms-nav__inner a {{
    display: inline-flex; align-items: center; height: 46px; padding: 0 14px;
    font-family: "Golos Text", "Segoe UI", sans-serif !important; font-size: 11px !important; font-weight: 600 !important;
    letter-spacing: .14em !important; text-transform: uppercase !important; color: rgba(243, 232, 216, .78) !important;
    text-decoration: none !important; transition: color .2s ease, box-shadow .2s ease;
  }}
  .ms-nav__inner a:hover {{ color: {INK} !important; }}
  .ms-nav__inner a.is-current {{ color: {GOLD} !important; box-shadow: inset 0 -1px 0 {GOLD}; }}
  .ms-nav__inner a:nth-last-child(2) {{ margin-left: auto; }}
}}

body .element-count-wrapper .element-count {{
  background: transparent !important; border: 0 !important; padding: 0 !important;
  font-family: "Golos Text", "Segoe UI", sans-serif !important; font-size: 14px !important; color: {MUTED} !important;
  vertical-align: super !important; margin-left: 4px !important;
}}

body .left_block .menu_top_block ul.left_menu > li > a {{
  background: transparent !important; border: 0 !important; padding: 9px 0 !important;
  font-family: "Golos Digits", Prata, Georgia, serif !important; font-size: 17px !important; font-weight: 400 !important; color: {INK} !important;
}}
body .left_block .menu_top_block ul.left_menu > li.current > a,
body .left_block .menu_top_block ul.left_menu > li > a:hover {{ color: {GOLD} !important; }}
body .left_block .menu_top_block ul.left_menu > li > a .toggle_block {{ display: none !important; }}
body .left_block .menu_top_block.menu-type1 {{ padding-top: 6px !important; }}

.top_slider_wrapp td.img {{ display: none !important; }}
.top_slider_wrapp .slides > li.box, .top_slider_wrapp .slides > li .main_info {{
  background-position: 68% 50% !important; background-size: cover !important;
}}
.top_slider_wrapp .slides > li.box {{ min-height: 640px !important; }}
.top_slider_wrapp .slides > li .wrapper_inner, .top_slider_wrapp table, .top_slider_wrapp td.text {{ min-height: 640px !important; }}
.top_slider_wrapp .slides > li .wrapper_inner {{ padding-top: 0 !important; }}
.top_slider_wrapp .flexslider, .top_slider_wrapp .flexslider .slides > li,
.top_slider_wrapp .flexslider .slides > li td, .top_slider_wrapp .flexslider .slides > li tr {{ height: auto !important; }}
.top_slider_wrapp td.text {{ vertical-align: middle !important; }}
@media (max-width: 767px) {{
  .top_slider_wrapp .slides > li.box {{ min-height: 560px !important; position: relative; background-position: 74% 30% !important; }}
  .top_slider_wrapp .slides > li.box[data-slide_index="2"] {{ background-position: 96% 30% !important; }}
  .top_slider_wrapp .slides > li .main_info {{ background-image: none !important; }}
  .top_slider_wrapp .slides > li.box::after {{
    content: ""; position: absolute; left: 0; right: 0; top: 0; bottom: 0; pointer-events: none;
    background: linear-gradient(180deg, rgba(18, 11, 8, 0) 0%, rgba(18, 11, 8, .08) 30%, rgba(18, 11, 8, .84) 62%, rgba(18, 11, 8, .97) 100%);
  }}
  .top_slider_wrapp .slides > li.box .wrapper_inner {{ position: relative; z-index: 1; }}
  .top_slider_wrapp .slides > li .wrapper_inner, .top_slider_wrapp table, .top_slider_wrapp td.text {{ min-height: 560px !important; }}
  .top_slider_wrapp td.text {{ vertical-align: bottom !important; text-align: left !important; padding: 0 16px 36px !important; }}
  .top_slider_wrapp td.text .banner_title, .top_slider_wrapp td.text .banner_text, .top_slider_wrapp .banner_buttons,
  .top_slider_wrapp .slides > li .banner_title .head-title {{ text-align: left !important; }}
  .top_slider_wrapp .slides > li .banner_title .head-title {{ font-size: 34px !important; }}
  .top_slider_wrapp .slides > li .banner_text {{ font-size: 15px !important; line-height: 1.55 !important; margin: 12px 0 0 !important; }}
  .top_slider_wrapp .banner_buttons {{ margin-top: 22px !important; }}
  .top_slider_wrapp .banner_buttons .btn {{ width: auto !important; }}
}}

.top_slider_wrapp td.text {{ width: 100% !important; }}
.top_slider_wrapp td.text .banner_title, .top_slider_wrapp td.text .banner_text {{ max-width: 540px !important; }}
.top_slider_wrapp .slides > li .banner_title .head-title {{ display: block !important; }}

.btn:not(.round-ignore), .btn.btn-default:not(.round-ignore) {{ border-radius: 0 !important; }}
.content_wrapper_block:has(> .maxwidth-theme.wide:empty) {{ display: none !important; }}
#mobilemenu ul.dropdown > li > a {{ text-transform: lowercase !important; }}
#mobilemenu ul.dropdown > li > a span::first-letter, #mobilemenu ul.dropdown > li > a::first-letter {{ text-transform: uppercase !important; }}

body .inline-search-block.fixed .search-input {{
  height: 84px !important; border: 0 !important; background: transparent !important;
  font-family: "Golos Text", "Segoe UI", sans-serif !important; font-size: 20px !important; padding: 0 110px 0 0 !important;
}}
body .inline-search-block.fixed .search-input::placeholder {{ color: {MUTED}; }}
body .inline-search-block.fixed .search-button-div .btn-search {{
  display: inline-block !important; width: auto !important; height: 42px !important; padding: 0 16px !important;
  font-size: 11px !important; letter-spacing: .14em !important; overflow: visible !important;
}}
body .inline-search-block .close-block .close-icons {{ background: none !important; width: 16px !important; height: 16px !important; }}
body .inline-search-block .close-block .close-icons::before, body .inline-search-block .close-block .close-icons::after {{
  content: ""; position: absolute; left: 50%; top: 50%; width: 20px; height: 1.5px; background: {INK};
  transform: translate(-50%, -50%) rotate(45deg);
}}
body .inline-search-block .close-block .close-icons::after {{ transform: translate(-50%, -50%) rotate(-45deg); }}
body .inline-search-block .close-block:hover .close-icons::before, body .inline-search-block .close-block:hover .close-icons::after {{ background: {ACCENT}; }}
@media (max-width: 767px) {{
  body .inline-search-block.fixed .search-input {{ font-size: 17px !important; padding-right: 96px !important; }}
  body .inline-search-block.fixed .search-button-div .btn-search {{ height: 38px !important; padding: 0 12px !important; }}
  body .MAPS .items.scroll-init, body .MAPS .block_container .items {{ height: auto !important; max-height: none !important; overflow: visible !important; }}
  body .MAPS .contacts_map_list {{ margin-top: 16px !important; }}
}}

.ms-modal {{ position: fixed; inset: 0; z-index: 5000; display: flex; align-items: center; justify-content: center; padding: 16px; opacity: 0; transition: opacity .25s; }}
.ms-modal.is-on {{ opacity: 1; }}
.ms-modal__back {{ position: absolute; inset: 0; background: rgba(8, 4, 3, .78); }}
.ms-modal__box {{ position: relative; width: 100%; max-width: 460px; background: {PANEL}; border: 1px solid {GOLD_LINE}; padding: 34px 36px 32px; }}
.ms-modal__close {{
  position: absolute; top: 8px; right: 10px; width: 40px; height: 40px; border: 0; background: none;
  color: {MUTED}; font-size: 28px; line-height: 1; cursor: pointer;
}}
.ms-modal__close:hover {{ color: {INK}; }}
.ms-modal__label {{ font-size: 11px; letter-spacing: .14em; text-transform: uppercase; color: {GOLD}; margin-bottom: 12px; }}
.ms-modal__title {{ font-family: "Golos Digits", Prata, Georgia, serif; font-size: 26px; font-weight: 400; margin: 0 0 12px; color: {INK}; }}
.ms-modal__text {{ font-size: 15px; line-height: 1.6; color: {MUTED}; margin: 0 0 20px; }}
.ms-modal__contacts {{ display: flex; flex-direction: column; gap: 8px; }}
.ms-modal__contacts a {{ font-size: 17px; color: {INK} !important; text-decoration: none; }}
.ms-modal__contacts a:hover {{ color: {ACCENT} !important; }}
.ms-modal__btn {{ margin-top: 22px; }}
body.ms-modal-open {{ overflow: hidden; }}
@media (max-width: 600px) {{ .ms-modal__box {{ padding: 28px 22px 26px; }} .ms-modal__title {{ font-size: 22px; }} }}

body .catalog_section_list.type_sections_5, body .catalog_section_list.items {{
  display: grid !important; grid-template-columns: repeat(5, minmax(0, 1fr)); gap: 16px; margin: 0 0 40px !important;
}}
body .catalog_section_list.row::before, body .catalog_section_list.row::after {{ display: none !important; }}
body .catalog_section_list .item_block {{ width: auto !important; max-width: none !important; padding: 0 !important; margin: 0 !important; float: none !important; }}
body .catalog_section_list .section_item {{
  background: transparent !important; border: 0 !important; box-shadow: none !important;
  padding: 0 !important; height: auto !important; transform: none !important;
}}
body .catalog_section_list .section_item_inner, body .catalog_section_list .section_item_inner tbody,
body .catalog_section_list .section_item_inner tr {{ display: block !important; width: 100% !important; }}
body .catalog_section_list td.image {{ display: block !important; width: 100% !important; height: auto !important; padding: 0 !important; }}
body .catalog_section_list td.image a.thumb {{ display: block !important; aspect-ratio: 1; background: {TILE} !important; overflow: hidden; }}
body .catalog_section_list td.image img {{
  width: 100% !important; height: 100% !important; max-width: none !important; max-height: none !important;
  object-fit: cover; transition: transform .4s;
}}
body .catalog_section_list .section_item:hover td.image img {{ transform: scale(1.03); }}
body .catalog_section_list td.section_info {{ display: block !important; width: 100% !important; padding: 12px 0 0 !important; text-align: left !important; vertical-align: top !important; }}
body .catalog_section_list td.section_info ul {{ margin: 0 !important; padding: 0 !important; }}
body .catalog_section_list .name {{ text-align: left !important; }}
body .catalog_section_list .name a.dark_link, body .catalog_section_list .name a.dark_link span.font_md {{
  display: block !important; font-family: "Golos Digits", Prata, Georgia, serif !important; font-weight: 400 !important;
  font-size: 18px !important; line-height: 1.25 !important; color: {INK} !important; text-transform: lowercase !important;
}}
body .catalog_section_list .name a.dark_link span.font_md::first-letter {{ text-transform: uppercase !important; }}
body .catalog_section_list .name a.dark_link:hover span.font_md {{ color: {ACCENT} !important; }}
body .catalog_section_list .element-count2 {{ display: block !important; margin-top: 5px !important; font-size: 13px !important; color: {MUTED} !important; }}
@media (max-width: 1199px) {{ body .catalog_section_list.type_sections_5, body .catalog_section_list.items {{ grid-template-columns: repeat(4, minmax(0, 1fr)); }} }}
@media (max-width: 767px) {{ body .catalog_section_list.type_sections_5, body .catalog_section_list.items {{ grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 10px; }} body .catalog_section_list .name a.dark_link span.font_md {{ font-size: 15px !important; }} }}
@media (max-width: 480px) {{ body .catalog_section_list.type_sections_5, body .catalog_section_list.items {{ grid-template-columns: repeat(2, minmax(0, 1fr)); }} }}

html body .catalog_item .price, html body .catalog_item .price .price_value, html body .catalog_item .price .price_currency,
html body .price_matrix_wrapper .price, html body .product-item-price-current, html body .price_value,
html body .detail .prices_block .price_value, html body .detail .prices_block .price_currency,
html body .ms-item__sum, html body .ms-summary__row--total, html body .ms-done__row--total,
html body .ms-card__price, html body .ms-done__title, html body .ms-modal__contacts a, html body .page-top .topic .count,
html body .topic .topic__count, html body .catalog_section_list .element-count2 {{
  font-weight: 500 !important; font-variant-numeric: lining-nums tabular-nums;
}}

body .CATALOG_TAB .tab_slider_wrapp ul.tabs {{ border-bottom: 0 !important; margin: 0 !important; }}
body .CATALOG_TAB .tab_slider_wrapp ul.tabs > li {{ margin: 0 0 0 22px !important; padding: 0 !important; }}
body .CATALOG_TAB .tab_slider_wrapp ul.tabs > li:first-child {{ margin-left: 0 !important; }}
body .CATALOG_TAB .tab_slider_wrapp ul.tabs > li span {{
  font-family: "Golos Text", "Segoe UI", sans-serif !important; font-size: 11px !important; font-weight: 600 !important;
  letter-spacing: .14em !important; text-transform: uppercase !important; line-height: 1 !important;
  color: {MUTED} !important; border-bottom: 1px solid transparent !important; padding: 0 0 7px !important; cursor: pointer;
}}
body .CATALOG_TAB .tab_slider_wrapp ul.tabs > li.cur span {{ color: {INK} !important; border-bottom-color: {GOLD} !important; }}
body .CATALOG_TAB .tab_slider_wrapp ul.tabs > li:not(.cur) span:hover {{ color: {INK} !important; }}
body .CATALOG_TAB .top_block .right_block_wrapper {{ display: flex !important; align-items: baseline !important; gap: 28px !important; }}
body .CATALOG_TAB .top_block .right_block_wrapper .tabs_wrapper {{ margin: 0 !important; }}
body .CATALOG_TAB .top_block .right_block_wrapper a.font_upper.muted {{ margin: 0 !important; padding-bottom: 7px !important; }}
.ms-search__sections--foot {{ margin-top: 40px; }}

body .top_slider_wrapp .flex-control-nav {{
  position: absolute !important; left: 0 !important; right: 0 !important; top: auto !important; bottom: 26px !important; z-index: 5 !important;
  height: auto !important; display: flex !important; align-items: center !important; justify-content: center !important;
  gap: 10px !important; margin: 0 !important; padding: 0 !important; width: auto !important; text-align: center !important;
}}
body .top_slider_wrapp .flex-control-nav li {{ margin: 0 !important; padding: 0 !important; display: block !important; }}
body .top_slider_wrapp .flex-control-nav li a {{
  display: block !important; width: 28px !important; height: 2px !important; border-radius: 0 !important;
  background: rgba(243, 232, 216, .28) !important; box-shadow: none !important; text-indent: -9999px !important;
  transition: background .3s !important; cursor: pointer;
}}
body .top_slider_wrapp .flex-control-nav li a.flex-active, body .top_slider_wrapp .flex-control-nav li a:hover {{ background: {GOLD} !important; }}
body .top_slider_wrapp .flex-control-nav, body .top_slider_wrapp .flex-control-nav li {{ list-style: none !important; }}
body .top_slider_wrapp .flex-control-nav li a::before, body .top_slider_wrapp .flex-control-nav li a::after {{ display: none !important; content: none !important; }}
body .top_slider_wrapp .flex-direction-nav a {{
  width: 44px !important; height: 44px !important; border-radius: 0 !important;
  background: rgba(18, 11, 8, .55) !important; border: 1px solid {GOLD_LINE} !important; opacity: 0 !important;
  transition: opacity .3s, background .3s !important;
}}
body .top_slider_wrapp .flexslider:hover .flex-direction-nav a {{ opacity: 1 !important; }}
body .top_slider_wrapp .flex-direction-nav a:hover {{ background: {ACCENT_SOFT} !important; }}
body .top_slider_wrapp .flex-direction-nav .flex-prev {{ left: 24px !important; }}
body .top_slider_wrapp .flex-direction-nav .flex-next {{ right: 24px !important; }}
@media (max-width: 767px) {{
  body .top_slider_wrapp .flex-direction-nav {{ display: none !important; }}
  body .top_slider_wrapp .flex-control-nav {{ bottom: 14px !important; justify-content: flex-start !important; padding: 0 16px !important; }}
}}

body .basket_fly .opener {{ background: {PANEL} !important; border: 1px solid {GOLD_LINE} !important; border-right: 0 !important; width: 72px !important; left: -72px !important; }}
body .basket_fly .opener .basket_count, body .basket_fly .opener .wish_count {{ width: 72px !important; height: 72px !important; position: relative !important; }}
body .basket_fly .opener .wraps_icon_block {{
  display: flex !important; flex-direction: column !important; align-items: center !important; justify-content: center !important;
  gap: 7px !important; width: 100% !important; height: 100% !important; padding: 0 !important; margin: 0 !important; position: static !important;
}}
body .basket_fly .opener .wraps_icon_block .svg {{ position: static !important; margin: 0 !important; display: block !important; line-height: 0 !important; }}
body .basket_fly .opener .wraps_icon_block::after {{
  font-family: "Golos Text", "Segoe UI", sans-serif; font-size: 9px; font-weight: 600; letter-spacing: .1em; text-transform: uppercase; line-height: 1;
}}
body .basket_fly .opener .wraps_icon_block.basket::after {{ content: "корзина"; color: {ON_ACCENT}; }}
body .basket_fly .opener .wraps_icon_block.delay::after {{ content: "отложено"; color: rgba(243, 232, 216, .7); }}
body .basket_fly .opener .wish_count:hover .wraps_icon_block.delay::after {{ color: {ACCENT}; }}
body .basket_fly .opener .count {{ position: absolute !important; top: 6px !important; right: 6px !important; left: auto !important; bottom: auto !important; margin: 0 !important; }}
body .basket_fly .opener .basket_count.ms-has-items .wraps_icon_block .svg, body .basket_fly .opener .wish_count.ms-has-items .wraps_icon_block .svg {{ transform: none; }}
body .basket_fly .opener .count span.colored_theme_bg.ms-pop {{ animation: ms-pop .4s ease; }}
@keyframes ms-pop {{ 0% {{ transform: scale(.6); }} 60% {{ transform: scale(1.15); }} 100% {{ transform: scale(1); }} }}
body .basket_fly .opener .basket_count {{ background: {ACCENT} !important; }}
body .basket_fly .opener .basket_count svg path {{ fill: {ON_ACCENT} !important; }}
body .basket_fly .opener .wish_count {{ background: transparent !important; border-top: 1px solid {GOLD_LINE} !important; }}
body .basket_fly .opener .wish_count svg path {{ fill: rgba(243, 232, 216, .7) !important; }}
body .basket_fly .opener .wish_count:hover svg path {{ fill: {ACCENT} !important; }}
body .basket_fly .opener .count span.colored_theme_bg {{
  background: {INK} !important; color: {GROUND} !important; border-radius: 0 !important;
  min-width: 18px !important; height: 18px !important; line-height: 18px !important; padding: 0 5px !important;
  font-family: "Golos Text", "Segoe UI", sans-serif !important; font-size: 11px !important; font-weight: 600 !important;
}}
body .basket_fly .opener .count span.colored_theme_bg span {{ background: transparent !important; color: inherit !important; }}
body .basket_fly .opener .wish_count .count span.colored_theme_bg {{ background: rgba(243, 232, 216, .85) !important; }}
body .basket_fly .opener .count.empty_items {{ display: none !important; }}
body .basket_fly .opener .basket_count.ms-has-items .count {{ display: block !important; }}

.ms-delayed {{ margin-top: 56px; padding-top: 40px; border-top: 1px solid {LINE}; padding-bottom: 40px; }}
.ms-delayed[hidden] {{ display: none; }}
.ms-fav {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(320px, 1fr)); gap: 16px; margin-top: 8px; }}
.ms-fav__item {{ display: grid; grid-template-columns: 96px minmax(0, 1fr); gap: 16px; background: {CARD}; padding: 14px; }}
.ms-fav__pic {{ display: block; width: 96px; height: 96px; background: {GROUND}; overflow: hidden; }}
.ms-fav__pic img {{ width: 100%; height: 100%; object-fit: cover; display: block; }}
.ms-fav__name {{ display: block; font-family: "Golos Digits", Prata, Georgia, serif; font-size: 16px; line-height: 1.3; color: {INK} !important; }}
.ms-fav__name:hover {{ color: {ACCENT} !important; }}
.ms-fav__price {{ margin: 6px 0 12px; font-size: 13px; color: {MUTED}; }}
.ms-fav__actions {{ display: flex; align-items: center; gap: 14px; flex-wrap: wrap; }}
.ms-fav__buy.btn {{ height: 40px !important; line-height: 40px !important; padding: 0 16px !important; font-size: 11px !important; }}
.ms-fav__remove {{ background: none; border: 0; padding: 0; font-size: 13px; color: {MUTED}; text-decoration: underline; cursor: pointer; }}
.ms-fav__remove:hover {{ color: {INK}; }}
.wish_item.added svg path, .wish_item.in svg path {{ fill: {ACCENT} !important; }}

.ms-reveal {{ opacity: 0; transform: translateY(18px); transition: opacity .7s ease, transform .7s cubic-bezier(.2, .7, .2, 1); }}
.ms-reveal.is-in {{ opacity: 1; transform: none; }}
.ms-reveal--2 {{ transition-delay: .08s; }} .ms-reveal--3 {{ transition-delay: .16s; }} .ms-reveal--4 {{ transition-delay: .24s; }}
.ms-reveal--5 {{ transition-delay: .32s; }} .ms-reveal--6 {{ transition-delay: .4s; }}
@keyframes ms-rise {{ from {{ opacity: 0; transform: translateY(22px); }} to {{ opacity: 1; transform: none; }} }}
body .top_slider_wrapp .slides > li.flex-active-slide .banner_title .section {{ animation: ms-rise .7s .1s cubic-bezier(.2, .7, .2, 1) both; }}
body .top_slider_wrapp .slides > li.flex-active-slide .banner_title .head-title {{ animation: ms-rise .8s .2s cubic-bezier(.2, .7, .2, 1) both; }}
body .top_slider_wrapp .slides > li.flex-active-slide .banner_text {{ animation: ms-rise .8s .35s cubic-bezier(.2, .7, .2, 1) both; }}
body .top_slider_wrapp .slides > li.flex-active-slide .banner_buttons {{ animation: ms-rise .8s .5s cubic-bezier(.2, .7, .2, 1) both; }}
body .top_slider_wrapp.ms-parallax .slides > li.box {{ overflow: hidden; }}
body .top_slider_wrapp.ms-parallax .slides > li.box > div[id] {{ position: relative; z-index: 1; }}
body .top_slider_wrapp.ms-parallax .slides > li .main_info {{ background-image: none !important; }}
body .top_slider_wrapp.ms-parallax .slides > li .wrapper_inner {{ will-change: transform; }}
.ms-hero-par {{ position: absolute; left: -3%; right: -3%; top: -4%; bottom: -4%; z-index: 0; will-change: transform; pointer-events: none; }}
.ms-hero-bg {{ position: absolute; left: 0; right: 0; top: 0; bottom: 0; background-size: cover; background-position: 68% 50%; background-repeat: no-repeat; }}
body .top_slider_wrapp .slides > li.flex-active-slide .ms-hero-bg {{ animation: ms-drift 18s cubic-bezier(.2, .5, .3, 1) both; }}
@keyframes ms-drift {{ from {{ transform: scale(1); }} to {{ transform: scale(1.07); }} }}
body .catalog_item, body .catalog_item .inner_wrap {{ transition: transform .35s cubic-bezier(.2, .7, .2, 1), background-color .35s !important; }}
body .catalog_item:hover {{ transform: translateY(-4px); }}
body .catalog_item .image_wrapper_block img, body .ms-card__pic img, body .cat_sections.cat_sections .item.compact .img.shine img {{ transition: transform .6s cubic-bezier(.2, .7, .2, 1) !important; }}
body .catalog_item:hover .image_wrapper_block img {{ transform: scale(1.04); }}
body .ms-card {{ transition: transform .35s cubic-bezier(.2, .7, .2, 1); }}
body .ms-card:hover {{ transform: translateY(-4px); }}
body .catalog_section_list .section_item {{ transition: transform .35s cubic-bezier(.2, .7, .2, 1) !important; }}
body .catalog_section_list .section_item:hover {{ transform: translateY(-4px) !important; }}
.btn, .btn.btn-default, button.btn {{ transition: background-color .25s, border-color .25s, color .25s, transform .2s !important; }}
.btn.btn-default:active {{ transform: translateY(1px); }}
.ms-nav__inner a {{ position: relative; }}
.ms-nav__inner a::after {{ content: ""; position: absolute; left: 0; right: 0; bottom: 6px; height: 1px; background: {GOLD}; transform: scaleX(0); transform-origin: left; transition: transform .3s cubic-bezier(.2, .7, .2, 1); }}
.ms-nav__inner a:hover::after, .ms-nav__inner a.is-current::after {{ transform: scaleX(1); }}
@media (prefers-reduced-motion: reduce) {{
  .ms-reveal {{ opacity: 1; transform: none; transition: none; }}
  body .top_slider_wrapp .slides > li.flex-active-slide .banner_title .section, body .top_slider_wrapp .slides > li.flex-active-slide .banner_title .head-title,
  body .top_slider_wrapp .slides > li.flex-active-slide .banner_text, body .top_slider_wrapp .slides > li.flex-active-slide .banner_buttons {{ animation: none; }}
  body .top_slider_wrapp .slides > li.flex-active-slide .ms-hero-bg {{ animation: none; }}
  body .catalog_item:hover, body .ms-card:hover, body .catalog_section_list .section_item:hover {{ transform: none !important; }}
}}

.ms-search-root {{ padding: 4px 0 48px; }}
.ms-search {{ display: flex; gap: 12px; max-width: 720px; margin-bottom: 26px; }}
.ms-search__input {{ flex: 1 1 auto; min-width: 0; }}
.ms-search__hint {{ color: {MUTED}; font-size: 15px; }}
.ms-search__count {{ font-size: 14px; color: {MUTED}; margin-bottom: 22px; }}
.ms-search__empty {{ max-width: 620px; }}
.ms-search__title {{ font-family: "Golos Digits", Prata, Georgia, serif; font-size: 26px; margin-bottom: 10px; }}
.ms-search__empty p {{ color: {MUTED}; margin: 0 0 18px; }}
.ms-search__sections {{ display: flex; flex-wrap: wrap; gap: 8px; }}
.ms-search__sections a {{
  display: inline-block; padding: 9px 14px; border: 1px solid {GOLD_LINE}; color: {INK} !important;
  font-size: 13px; text-decoration: none;
}}
.ms-search__sections a:hover {{ border-color: {ACCENT}; color: {ACCENT} !important; }}
.ms-grid {{ display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: 16px; }}
.ms-card {{ display: flex; flex-direction: column; background: {CARD}; }}
.ms-card__pic {{ display: block; aspect-ratio: 1; background: {GROUND}; overflow: hidden; }}
.ms-card__pic img {{ width: 100%; height: 100%; object-fit: cover; display: block; transition: transform .4s; }}
.ms-card:hover .ms-card__pic img {{ transform: scale(1.03); }}
.ms-card__body {{ display: flex; flex-direction: column; flex: 1 1 auto; padding: 16px 18px 20px; }}
.ms-card__section {{ font-size: 11px; letter-spacing: .12em; text-transform: uppercase; color: {MUTED}; margin-bottom: 8px; }}
.ms-card__name {{ font-family: "Golos Digits", Prata, Georgia, serif; font-size: 17px; line-height: 1.3; color: {INK} !important; text-decoration: none; }}
.ms-card__name:hover {{ color: {ACCENT} !important; }}
.ms-card__price {{ margin: 12px 0 16px; font-family: "Golos Digits", Prata, Georgia, serif; font-size: 22px; color: {GOLD}; }}
.ms-card__price small {{ font-family: "Golos Text", "Segoe UI", sans-serif; font-size: 13px; color: {MUTED}; margin-left: 4px; }}
.ms-card__btn.btn.btn-lg {{ margin-top: auto; align-self: flex-start; padding: 0 24px !important; height: 48px; line-height: 48px; }}
@media (max-width: 1199px) {{ .ms-grid {{ grid-template-columns: repeat(3, minmax(0, 1fr)); }} }}
@media (max-width: 767px) {{
  .ms-grid {{ grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 10px; }}
  .ms-card__body {{ padding: 12px 12px 16px; }}
  .ms-card__name {{ font-size: 15px; }}
  .ms-card__price {{ font-size: 19px; margin: 10px 0 12px; }}
  .ms-card__btn.btn.btn-lg {{ width: 100%; display: flex !important; align-items: center; justify-content: center; padding: 0 10px !important; letter-spacing: .1em !important; }}
  .ms-search {{ flex-direction: column; }}
}}
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
