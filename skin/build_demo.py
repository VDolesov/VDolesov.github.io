# -*- coding: utf-8 -*-
"""Готовая версия сайта с новым оформлением.

Страницы боевого сайта берутся как есть, добавляется <base>, чтобы стили,
скрипты и картинки грузились с исходного домена, и подключается skin.css.
Вёрстка не правится ни на символ — именно так это будет выглядеть после
подключения файла на сервере.

Фотографии каталога подменяются обработанной серией: на живом сайте их
загружают в карточки товаров, здесь подстановка сделана скриптом, чтобы
результат было видно целиком.

    python skin/build_demo.py
"""
import json
import os
import re
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
APP = os.path.dirname(HERE)
SITE = "https://www.mirsladostey164.ru"
PAGES_ORIGIN = "https://vdolesov.github.io"
OUT = os.path.join(HERE, "demo")

PAGES = [
    ("index.html", "/"),
    ("catalog.html", "/catalog/torty/"),
    ("pirogi.html", "/catalog/pirogi/"),
    ("product.html", "/catalog/torty/747/"),
    ("basket.html", "/basket/"),
    ("contacts.html", "/contacts/"),
]

PHOTO_SCRIPT = """
<script>
/* Фотографии обработанной серии подставляются по коду товара из ссылки.
   На сервере этого скрипта не нужно: файлы загружаются в карточки товаров. */
(function () {
  var ids = %IDS%;
  var pageId = "%PAGE_ID%";

  function swap(img, id) {
    if (img.dataset.skinDone || img.closest(".stickers")) return;
    img.dataset.skinDone = "1";
    img.removeAttribute("srcset");
    img.removeAttribute("data-src");
    img.classList.remove("lazy");
    img.src = "%ORIGIN%/assets/products/" + id + "-v7.webp";
  }

  // страница товара: главное изображение и миниатюры галереи
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
})();
</script>
"""


def fetch(path):
    request = urllib.request.Request(SITE + path, headers={"User-Agent": "Mozilla/5.0"})
    return urllib.request.urlopen(request, timeout=60).read().decode("utf-8", "ignore")


def product_ids():
    data = json.load(open(os.path.join(APP, "build", "catalog.json"), encoding="utf-8"))
    return [item["id"] for item in data["items"]]


def build_page(filename, path, ids):
    html = fetch(path)

    # ресурсы и ссылки продолжают работать с исходного домена
    html = html.replace("<head>", f'<head>\n<base href="{SITE}/">', 1)

    # оформление подключается последним — как это и будет на сервере
    link = f'\n<link rel="stylesheet" href="{PAGES_ORIGIN}/skin/skin.css">\n</head>'
    html = html.replace("</head>", link, 1)

    match = re.search(r"/catalog/[a-z_]+/(\d+)/", path)
    script = (PHOTO_SCRIPT.replace("%IDS%", json.dumps(ids))
                          .replace("%ORIGIN%", PAGES_ORIGIN)
                          .replace("%PAGE_ID%", match.group(1) if match else ""))
    html = html.replace("</body>", script + "\n</body>", 1)

    os.makedirs(OUT, exist_ok=True)
    with open(os.path.join(OUT, filename), "w", encoding="utf-8", newline="\n") as f:
        f.write(html)
    print(f"  {filename} <- {path}")


def main():
    ids = product_ids()
    print("страницы:")
    for filename, path in PAGES:
        try:
            build_page(filename, path, ids)
        except Exception as exc:
            print(f"  {filename}: ошибка {exc}")


if __name__ == "__main__":
    main()
