# -*- coding: utf-8 -*-
"""Данные товаров для корзины: skin/cart-data.js из build/catalog.json.

    python skin/build_cart_data.py
"""
import io
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
APP = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(APP, "build"))

from data import pretty  # noqa: E402  — тот же нормализатор названий, что в каталоге

PAGES_ORIGIN = "https://vdolesov.github.io"


def main():
    catalog = json.load(io.open(os.path.join(APP, "build", "catalog.json"), encoding="utf-8"))
    photos = {f.split("-")[0] for f in os.listdir(os.path.join(APP, "assets", "products"))
              if f.endswith("-v7-640.webp")}

    products = {}
    for item in catalog["items"]:
        products[item["id"]] = {
            "name": pretty(item["name"], item["section"]),
            "price": item["price"],
            "unit": item.get("unit") or "шт",
            "weight": item.get("weight") or "",
            "url": f"/catalog/{item['section']}/{item['id']}/",
            "image": item.get("image") or "",
        }

    body = ("/* Сгенерировано build_cart_data.py из build/catalog.json. */\n"
            f"window.MS_ORIGIN = {json.dumps(PAGES_ORIGIN)};\n"
            f"window.MS_PHOTOS = {json.dumps(sorted(photos))};\n"
            f"window.MS_PRODUCTS = {json.dumps(products, ensure_ascii=False, indent=1)};\n")
    path = os.path.join(HERE, "cart-data.js")
    io.open(path, "w", encoding="utf-8", newline="\n").write(body)
    print(f"товаров: {len(products)}, с фотографиями: {len(photos & set(products))}, записано {path}")


if __name__ == "__main__":
    main()
