# -*- coding: utf-8 -*-
"""Скачивает исходные фотографии товаров с сайта в build/photos/<id>.jpg."""
import json
import os
import time
import urllib.request

BASE = "https://www.mirsladostey164.ru"
UA = {"User-Agent": "Mozilla/5.0 (compatible; MirSladostey-frontend-prototype)"}
HERE = os.path.dirname(__file__)
OUT = os.path.join(HERE, "photos")

os.makedirs(OUT, exist_ok=True)
catalog = json.load(open(os.path.join(HERE, "catalog.json"), encoding="utf-8"))

for item in catalog["items"]:
    url = item.get("image")
    if not url:
        print(f"{item['id']}: фото нет")
        continue
    dst = os.path.join(OUT, f"{item['id']}.jpg")
    if os.path.exists(dst):
        continue
    req = urllib.request.Request(BASE + url, headers=UA)
    try:
        with urllib.request.urlopen(req, timeout=40) as r, open(dst, "wb") as f:
            f.write(r.read())
        print(f"{item['id']}: скачано {os.path.getsize(dst)//1024} КБ")
    except Exception as e:
        print(f"{item['id']}: ошибка {e}")
    time.sleep(0.3)
