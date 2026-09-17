import json
import os
import re
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
APP = os.path.dirname(HERE)
SITE = "https://www.mirsladostey164.ru"
PAGES_ORIGIN = "https://vdolesov.github.io"
OUT = os.path.join(HERE, "demo")
SERIES = "v9"

PAGES = [
    ("index.html", "/"),
    ("catalog.html", "/catalog/torty/"),
    ("pirogi.html", "/catalog/pirogi/"),
    ("product.html", "/catalog/torty/747/"),
    ("basket.html", "/basket/"),
    ("contacts.html", "/contacts/"),
]

DEMO_FIX = """
<style>
li[data-code="NEW"], li[data-code="RECOMMEND"],
.NEW_slides, .RECOMMEND_slides { display: none !important; }
.basket_hover_block.loading_block,
.loading_block_content { background-image: none !important; }
.wrap_basket .basket_hover_block { display: none !important; }
.filter-panel.sort_header, .filter-panel-wrapper, #mobilefilter { display: none !important; }
.CATALOG_TAB .tabs_wrapper { display: none !important; }
</style>
"""

PHOTO_SCRIPT = """
<script>
(function () {
  var ids = %IDS%;
  var pageId = "%PAGE_ID%";

  function swap(img, id) {
    if (img.dataset.skinDone || img.closest(".stickers") || /\\/assets\\/products\\//.test(img.getAttribute("src") || "")) return;
    img.dataset.skinDone = "1";
    img.removeAttribute("srcset");
    img.removeAttribute("data-src");
    img.classList.remove("lazy");
    img.src = "%ORIGIN%/assets/products/" + id + "-%SERIES%.webp";
  }

  if (pageId) {
    document.querySelectorAll(".detail img, .product-detail img, .slides img, .thumbs img")
      .forEach(function (img) { swap(img, pageId); });
  }
  document.querySelectorAll("a[href*='/catalog/']").forEach(function (a) {
    var m = a.getAttribute("href").match(/\\/catalog\\/[a-z_]+\\/(\\d+)\\//);
    if (!m || ids.indexOf(m[1]) === -1) return;
    var card = a.closest(".catalog_item, .product-item-container, .item_block, .catalog_item_wrapp, .detail");
    if (!card) return;
    card.querySelectorAll("img").forEach(function (img) { swap(img, m[1]); });
  });

  var sections = %SECTIONS%;
  document.querySelectorAll(".cat_sections a.thumb, .sections_wrapper a.thumb")
    .forEach(function (a) {
      var m = (a.getAttribute("href") || "").match(/\\/catalog\\/([a-z_]+)\\/$/);
      if (!m || !sections[m[1]]) return;
      var img = a.querySelector("img");
      if (!img) return;
      img.removeAttribute("srcset");
      img.removeAttribute("data-src");
      img.classList.remove("lazy");
      img.src = "%ORIGIN%/assets/products/" + sections[m[1]] + "-%SERIES%.webp";
    });
})();
</script>
"""

SECTION_PHOTOS = {

    "torty": "749",
    "pirogi": "801",
    "vypechka": "746",
    "pirozhnye_i_deserty": "757",
    "pechene": "753",
    "salaty": "765",
    "vtorye_blyuda": "770",
    "polufabrikaty": "760",
    "napitki": "763",
}

BANNER = {
    "/upload/iblock/890/890366e70949176749ee46def14a193b.jpg": "/assets/hero-bg.jpg?v=7",
    "/upload/iblock/a76/a76586772deb02b99d66c209bfda9c22.png": "/assets/hero-bg.jpg?v=7",
}
SLIDES = [
    {"file": "/assets/hero-bg.jpg?v=7", "label": "Собственное производство", "title": "Изготовление тортов и пирожных",
     "text": "Торты, пироги и десерты, которые мы печём сами. Заберите в одном из двух магазинов или закажите доставку по Саратову.",
     "button": "Выбрать торт", "href": "/catalog/torty/"},
    {"file": "/assets/hero-2.jpg?v=1", "label": "Пироги", "title": "Пироги на каждый день",
     "text": "С мясом, капустой, рыбой и вишней — к обеду и к чаю. Заберите в магазине или закажите доставку.",
     "button": "К пирогам", "href": "/catalog/pirogi/"},
    {"file": "/assets/hero-3.jpg?v=3", "label": "На праздник", "title": "Торт на праздник — под заказ",
     "text": "Назовите дату, повод и начинку — остальное сделаем мы. Соберём торт так, как вы его задумали.",
     "button": "Заказать торт", "href": "/catalog/torty/"},
]
_SLIDE_LIST = re.compile(r'(<ul class="slides">)(.*?)(</ul>)', re.S)
_SLIDE = re.compile(r"<li\b.*?</li>", re.S)


def expand_slides(html):
    def build(m):
        first = _SLIDE.search(m.group(2))
        if not first or "top_slider_wrapp" not in html[max(0, m.start() - 3000):m.start()]:
            return m.group(0)
        template = first.group(0)
        out = []
        for i, slide in enumerate(SLIDES):
            li = re.sub(r"https?://[^\"' )]*/assets/hero-[a-z0-9]+\.jpg\?v=\d+", PAGES_ORIGIN + slide["file"], template)
            li = re.sub(r'data-slide_index="\d+"', f'data-slide_index="{i}"', li)
            li = re.sub(r'id="(bx_\d+_\d+)(?:_s\d+)?"', lambda a: f'id="{a.group(1)}' + (f'_s{i}' if i else "") + '"', li)
            li = re.sub(r'(<div class="section font_upper_md">)[^<]*(</div>)', lambda a: a.group(1) + slide["label"] + a.group(2), li)
            li = re.sub(r'(<span class="head-title">\s*)[^<]*?(\s*</span>)', lambda a: a.group(1) + slide["title"] + a.group(2), li)
            li = re.sub(r'(<div class="banner_text">)[^<]*(</div>)', lambda a: a.group(1) + slide["text"] + a.group(2), li)
            li = re.sub(r'(<a href=")[^"]*(" class="btn btn-default btn-lg"[^>]*>\s*)[^<]*?(\s*</a>)',
                        lambda a: a.group(1) + slide["href"] + a.group(2) + slide["button"] + a.group(3), li)
            li = re.sub(r'<img class="plaxy"[^>]*>',
                        lambda a: re.sub(r'(alt|title)="[^"]*"', lambda b: b.group(1) + '="' + slide["title"] + '"', a.group(0)), li)
            out.append(li)
        return m.group(1) + "\n".join(out) + m.group(3)
    return _SLIDE_LIST.sub(build, html, count=1)


IMAGES = {
    "https://www.mirsladostey164.ru/images/contacts_image.jpg": "/assets/about.jpg?v=2",
}

BANNER_COPY = [
    (r'(<div class="section font_upper_md">)Торты(</div>)', r"\1Собственное производство\2"),
    (r'(<div class="banner_text">)Аппетитный внешний вид[^<]*(</div>)',
     r"\1Торты, пироги и десерты, которые мы печём сами. "
     r"Заберите в одном из двух магазинов или закажите доставку по Саратову.\2"),
    (r'(class="btn btn-default btn-lg"[^>]*>\s*)Перейти в каталог(\s*</a>)', r"\1Выбрать торт\2"),
    (r'(<a href=")/catalog/(" class="font_upper muted">)Весь каталог(</a>)', r"\1/catalog/?hit=1\2Все хиты\3"),
    (r'(<img class="plaxy"[^>]*(?:alt|title)=")Изготовление тортов и пирожных(")', r"\1Торт «Шварцвальдский»\2"),
]


def swap_banner(html):
    for old, new in BANNER.items():
        html = html.replace(old, PAGES_ORIGIN + new)
    for old, new in IMAGES.items():
        html = html.replace(old, PAGES_ORIGIN + new)
    for pattern, new in BANNER_COPY:
        html = re.sub(pattern, new, html)
    return expand_slides(html)


def unlazy(html):
    def img(match):
        tag = match.group(0)
        real = re.search(r'data-src="([^"]+)"', tag)
        if not real:
            return tag
        tag = re.sub(r'(?<![-\w])src="[^"]*"', f'src="{real.group(1)}"', tag, count=1)
        if 'src="' not in tag:
            tag = tag.replace("<img", f'<img src="{real.group(1)}"', 1)
        return re.sub(r'class="lazy\s*', 'class="', tag.replace(" lazy", ""))

    html = re.sub(r"<img[^>]*>", img, html)

    def background(match):
        tag = match.group(0)
        real = re.search(r'data-bg="([^"]+)"', tag)
        if not real:
            return tag
        tag = re.sub(r"url\('[^']*double_ring\.svg'\)", f"url('{real.group(1)}')", tag)
        return tag.replace(" lazy", "")

    return re.sub(r"<[a-z]+[^>]*data-bg=\"[^\"]+\"[^>]*>", background, html)


def inline_deferred(html):
    pattern = re.compile(r'<div[^>]*js-load-block[^>]*data-file="([^"]+)"[^>]*>')
    for match in list(pattern.finditer(html)):
        url = match.group(1)
        try:
            request = urllib.request.Request(
                SITE + url,
                headers={"User-Agent": "Mozilla/5.0",
                         "X-Requested-With": "XMLHttpRequest",
                         "Referer": SITE + "/"})
            block = urllib.request.urlopen(request, timeout=45).read().decode("utf-8", "ignore")
        except Exception as exc:
            print(f"    block {url}: {exc}")
            continue

        opening = match.group(0)

        clean = opening.replace(" js-load-block", "").replace(" loader_circle", "")
        html = html.replace(opening, clean + block, 1)
        print(f"    inlined block {url.split('/')[-1]}")
    return html


def fetch(path):
    request = urllib.request.Request(SITE + path, headers={"User-Agent": "Mozilla/5.0"})
    return urllib.request.urlopen(request, timeout=60).read().decode("utf-8", "ignore")


def product_ids():
    data = json.load(open(os.path.join(APP, "build", "catalog.json"), encoding="utf-8"))
    return [item["id"] for item in data["items"]]


def photo_url(pid, size=None):
    return f"{PAGES_ORIGIN}/assets/products/{pid}-{SERIES}{'-' + str(size) if size else ''}.webp"


def photo_files():
    data = json.load(open(os.path.join(APP, "build", "catalog.json"), encoding="utf-8"))
    have = {f.split("-")[0] for f in os.listdir(os.path.join(APP, "assets", "products"))
            if f.endswith(f"-{SERIES}.webp")}
    files = {}
    for item in data["items"]:
        name = os.path.basename(item.get("image") or "")
        if name and item["id"] in have:
            files[name.lower()] = item["id"]
    return files, have


_PHOTO_ATTR = re.compile(r'((?:src|data-src|href|data-original)=")([^"]*?/([0-9a-f]{32}\.(?:jpe?g|png)))(")', re.I)
_CARD_IMG = re.compile(r'(<a href="/catalog/[a-z_]+/(\d+)/"[^>]*class="thumb[^"]*"[^>]*>)(.*?)(</a>)', re.S)
_SECTION_IMG = re.compile(r'(<a href="/catalog/([a-z_]+)/"[^>]*class="thumb[^"]*"[^>]*>)(.*?)(</a>)', re.S)
_IMG = re.compile(r"<img\b[^>]*>")
_SRCSET = re.compile(r'\s(?:srcset|data-srcset)="[^"]*"')


def swap_photos(html, page_id=None):
    files, have = photo_files()

    def attr(m):
        pid = files.get(m.group(3).lower())
        return m.group(1) + photo_url(pid) + m.group(4) if pid else m.group(0)
    html = _PHOTO_ATTR.sub(attr, html)

    if page_id in have:
        url = photo_url(page_id)
        html = re.sub(r'(<a\b[^>]*data-fancybox="gallery"[^>]*\bhref=")[^"]*(")', lambda m: m.group(1) + url + m.group(2), html)
        html = re.sub(r'(<a\b[^>]*\bhref=")[^"]*("[^>]*data-fancybox="gallery")', lambda m: m.group(1) + url + m.group(2), html)
        html = _IMG.sub(lambda m: _SRCSET.sub("", re.sub(r'\s(src|data-src)="[^"]*"', lambda a: f' {a.group(1)}="{url}"', m.group(0)))
                        if "product-detail-gallery" in m.group(0) else m.group(0), html)

    def retarget(m, pid):
        def img(tag):
            tag = re.sub(r'\s(src|data-src)="[^"]*"', lambda a: f' {a.group(1)}="{photo_url(pid, 640)}"', tag.group(0))
            tag = re.sub(r'\s(?:loading|decoding)="[^"]*"', "", _SRCSET.sub("", tag))
            return tag.replace("<img", f'<img srcset="{photo_url(pid, 640)} 640w, {photo_url(pid)} 1024w" '
                                       'sizes="(max-width: 600px) 50vw, (max-width: 1199px) 33vw, 340px" loading="lazy" decoding="async"', 1)
        return m.group(1) + _IMG.sub(img, m.group(3)) + m.group(4)

    html = _CARD_IMG.sub(lambda m: retarget(m, m.group(2)) if m.group(2) in have else m.group(0), html)
    html = _SECTION_IMG.sub(lambda m: retarget(m, SECTION_PHOTOS[m.group(2)])
                            if m.group(2) in SECTION_PHOTOS else m.group(0), html)

    def srcset(m):
        return "" if re.search(r"[0-9a-f]{32}\.(?:jpe?g|png)", m.group(0), re.I) else m.group(0)
    html = _SRCSET.sub(srcset, html)
    return _IMG.sub(lambda m: re.sub(r'class="lazy\s*', 'class="', m.group(0)) if "/assets/products/" in m.group(0) else m.group(0), html)


def build_page(filename, path, ids):
    html = fetch(path)
    html = inline_deferred(html)
    html = unlazy(html)
    html = swap_banner(html)

    html = html.replace("<head>", f'<head>\n<base href="{SITE}/">', 1)

    link = f'\n<link rel="stylesheet" href="{PAGES_ORIGIN}/skin/skin.css">\n</head>'
    html = html.replace("</head>", link, 1)

    match = re.search(r"/catalog/[a-z_]+/(\d+)/", path)
    script = (PHOTO_SCRIPT.replace("%IDS%", json.dumps(ids))
                          .replace("%ORIGIN%", PAGES_ORIGIN)
                          .replace("%PAGE_ID%", match.group(1) if match else "")
                          .replace("%SECTIONS%", json.dumps(SECTION_PHOTOS)))
    html = html.replace("</body>", script + DEMO_FIX + chr(10) + "</body>", 1)

    os.makedirs(OUT, exist_ok=True)
    with open(os.path.join(OUT, filename), "w", encoding="utf-8", newline="\n") as f:
        f.write(html)
    print(f"  {filename} <- {path}")


def main():
    ids = product_ids()
    print("pages:")
    for filename, path in PAGES:
        try:
            build_page(filename, path, ids)
        except Exception as exc:
            print(f"  {filename}: error {exc}")


if __name__ == "__main__":
    main()
