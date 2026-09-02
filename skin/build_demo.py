# -*- coding: utf-8 -*-
"""Демонстрация скина на реальных страницах сайта.

Берём страницы боевого сайта как есть, добавляем <base>, чтобы стили,
скрипты и картинки грузились с исходного домена, и подключаем skin.css
последним. Вёрстка не правится ни на символ — это и есть суть подхода.

Дополнительно демо подменяет фотографии товаров на обработанную серию
и показывает переключатель «до/после».

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
    ("home.html", "/", "Главная"),
    ("catalog.html", "/catalog/torty/", "Раздел каталога"),
    ("product.html", "/catalog/torty/747/", "Карточка товара"),
    ("basket.html", "/basket/", "Корзина"),
]

PANEL = """
<div id="skin-demo-panel">
  <div class="skin-demo-panel__title">Оформление</div>
  <label class="skin-demo-switch">
    <input type="checkbox" id="skin-demo-toggle" checked>
    <span></span>
    <b>новое</b>
  </label>
  <div class="skin-demo-panel__links"><a href="index.html">← обзор</a>%LINKS%</div>
  <p class="skin-demo-panel__note">Страница сайта как есть — меняется только подключённый CSS.</p>
</div>
<style>
#skin-demo-panel {
  position: fixed; z-index: 100000; right: 18px; bottom: 18px; width: 232px;
  padding: 16px 18px; border-radius: 4px; background: #1b1211; color: #f0e6d8;
  box-shadow: 0 20px 50px rgba(0,0,0,.35); font: 13px/1.5 system-ui, sans-serif;
}
.skin-demo-panel__title { color: #b08b4f; font-size: 10px; letter-spacing: .16em; text-transform: uppercase; margin-bottom: 12px; }
.skin-demo-switch { display: flex; align-items: center; gap: 10px; cursor: pointer; }
.skin-demo-switch input { position: absolute; opacity: 0; }
.skin-demo-switch span { position: relative; width: 40px; height: 22px; border-radius: 11px; background: #4a3a38; transition: background .2s; }
.skin-demo-switch span:after { content: ""; position: absolute; top: 3px; left: 3px; width: 16px; height: 16px; border-radius: 50%; background: #fff; transition: transform .2s; }
.skin-demo-switch input:checked + span { background: #8f1737; }
.skin-demo-switch input:checked + span:after { transform: translateX(18px); }
.skin-demo-switch b { font-weight: 600; }
.skin-demo-panel__links { display: grid; gap: 5px; margin-top: 14px; padding-top: 12px; border-top: 1px solid rgba(255,255,255,.14); }
.skin-demo-panel__links a { color: #e8d8c4; text-decoration: none; font-size: 12px; }
.skin-demo-panel__links a:hover { color: #b08b4f; }
.skin-demo-panel__links a.current { color: #b08b4f; }
.skin-demo-panel__note { margin: 12px 0 0; color: rgba(240,230,216,.5); font-size: 11px; line-height: 1.4; }
@media (max-width: 700px) { #skin-demo-panel { right: 10px; bottom: 10px; width: 190px; padding: 12px 14px; } }
</style>
<script>
(function () {
  var link = document.getElementById("skin-demo-css");
  var toggle = document.getElementById("skin-demo-toggle");
  toggle.addEventListener("change", function () {
    link.disabled = !toggle.checked;
    document.querySelectorAll("[data-skin-photo]").forEach(function (img) {
      img.src = toggle.checked ? img.dataset.skinPhoto : img.dataset.skinOriginal;
    });
  });

  // Фотографии обработанной серии подставляются по коду товара из ссылки.
  var ids = %IDS%;
  document.querySelectorAll("a[href*='/catalog/']").forEach(function (a) {
    var m = a.getAttribute("href").match(/\\/catalog\\/[a-z_]+\\/(\\d+)\\//);
    if (!m || ids.indexOf(m[1]) === -1) return;
    var card = a.closest(".catalog_item, .product-item-container, .item_block, .catalog_item_wrapp");
    var img = card && card.querySelector("img");
    if (!img || img.dataset.skinPhoto) return;
    img.dataset.skinOriginal = img.getAttribute("src") || "";
    img.dataset.skinPhoto = "%ORIGIN%/assets/products/" + m[1] + "-v7.webp";
    img.removeAttribute("srcset");
    img.src = img.dataset.skinPhoto;
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

    # скин подключается последним — как это и будет на сайте
    skin = (f'\n<link id="skin-demo-css" rel="stylesheet" '
            f'href="{PAGES_ORIGIN}/skin/skin.css">\n</head>')
    html = html.replace("</head>", skin, 1)

    links = ""
    for name, _, title in PAGES:
        current = ' class="current"' if name == filename else ""
        links += f'<a href="{name}"{current}>{title}</a>'
    panel = (PANEL.replace("%LINKS%", links)
                  .replace("%IDS%", json.dumps(ids))
                  .replace("%ORIGIN%", PAGES_ORIGIN))
    html = html.replace("</body>", panel + "\n</body>", 1)

    os.makedirs(OUT, exist_ok=True)
    with open(os.path.join(OUT, filename), "w", encoding="utf-8", newline="\n") as f:
        f.write(html)
    print(f"  {filename} ← {path}")


def main():
    ids = product_ids()
    print("страницы демонстрации:")
    for filename, path, _ in PAGES:
        try:
            build_page(filename, path, ids)
        except Exception as exc:
            print(f"  {filename}: ошибка {exc}")


if __name__ == "__main__":
    main()
