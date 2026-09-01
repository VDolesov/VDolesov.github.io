# -*- coding: utf-8 -*-
"""Снимок каталога mirsladostey164.ru: разделы, товары, цены, характеристики.

Результат: build/catalog.json — источник данных для сборки витрины.
Запускать редко, вручную: python build/scrape.py
"""
import html
import json
import os
import re
import time
import urllib.request

BASE = "https://www.mirsladostey164.ru"
UA = {"User-Agent": "Mozilla/5.0 (compatible; MirSladostey-frontend-prototype)"}
OUT = os.path.join(os.path.dirname(__file__), "catalog.json")

SECTIONS = [
    ("torty", "Торты"), ("pirogi", "Пироги"), ("vypechka", "Выпечка"),
    ("pirozhnye_i_deserty", "Пирожные и десерты"), ("pechene", "Печенье"),
    ("salaty", "Салаты"), ("vtorye_blyuda", "Вторые блюда"),
    ("polufabrikaty", "Полуфабрикаты"), ("napitki", "Напитки"),
]


def get(url):
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.read().decode("utf-8", "ignore")


def text_of(fragment):
    t = re.sub(r"<script.*?</script>|<style.*?</style>", " ", fragment, flags=re.S)
    t = html.unescape(re.sub(r"<[^>]+>", " ", t))
    return re.sub(r"\s+", " ", t).strip()


def best_image(page):
    """Самый крупный файл товара среди картинок инфоблока."""
    urls = sorted(set(re.findall(r"/upload/iblock/[^\"'\s]+\.(?:jpg|jpeg|png)", page)))
    best, best_size = "", 0
    for u in urls:
        try:
            req = urllib.request.Request(BASE + u, headers=UA, method="HEAD")
            with urllib.request.urlopen(req, timeout=20) as r:
                size = int(r.headers.get("Content-Length") or 0)
        except Exception:
            size = 0
        if size > best_size:
            best, best_size = u, size
    return best


def parse_item(slug, pid):
    page = get(f"{BASE}/catalog/{slug}/{pid}/")
    t = text_of(page)

    name = ""
    m = re.search(r"<title>(.*?)</title>", page, re.S)
    if m:
        name = html.unescape(m.group(1))
        name = re.sub(r'^\s*Купить\s*"?|"?\s*в Саратове.*$', "", name).strip()
        name = re.sub(r"\s*[-–—]\s*Мир Сладостей.*$", "", name).strip()

    article = price = unit = ""
    m = re.search(r"Артикул:\s*([0-9A-Za-zА-Яа-я\-]+)", t)
    if m:
        article = m.group(1)
    m = re.search(r"Артикул:\s*\S+\s*([\d\s ]+)\s*₽\s*/?\s*(шт|кг|уп|л)?", t)
    if m:
        price = re.sub(r"\D", "", m.group(1))
        unit = m.group(2) or ""

    def grab(label, stop):
        mm = re.search(label + r"\s*—\s*(.*?)(?=" + stop + r")", t)
        return mm.group(1).strip(" .") if mm else ""

    stop = r"Вес|Состав|Энергетическая|Пищевая|Цена действительна|Отзывы|Характеристики|$"
    weight = grab(r"Вес", stop)
    composition = grab(r"Состав", stop)
    energy = grab(r"Энергетическая ценность \??\s*на 100 г\.? продукта", stop)
    nutrition = grab(r"Пищевая ценность \??\s*на 100 г\.? продукта", stop)

    badges = []
    for b in ("Хит", "Новинка", "Акция", "Рекомендуем"):
        if re.search(r">\s*" + b + r"\s*<", page):
            badges.append(b)

    return {
        "id": pid, "section": slug, "name": name, "article": article,
        "price": int(price) if price.isdigit() else None, "unit": unit,
        "weight": weight, "composition": composition,
        "energy": energy, "nutrition": nutrition, "badges": badges,
        "image": best_image(page),
        "url": f"/catalog/{slug}/{pid}/",
    }


def main():
    catalog = {"sections": [], "items": []}
    for slug, title in SECTIONS:
        page = get(f"{BASE}/catalog/{slug}/")
        ids = sorted(set(re.findall(r'href="/catalog/' + slug + r'/(\d+)/"', page)), key=int)
        catalog["sections"].append({"slug": slug, "title": title, "count": len(ids)})
        print(f"{slug}: {len(ids)} товаров")
        for pid in ids:
            try:
                item = parse_item(slug, pid)
                catalog["items"].append(item)
                print("   ", pid, item["name"][:38], item["price"], item["unit"])
            except Exception as e:
                print("   ", pid, "ошибка:", e)
            time.sleep(0.4)

    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(catalog, f, ensure_ascii=False, indent=1)
    print("\nсохранено:", OUT, "| товаров:", len(catalog["items"]))


main()
