import io
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
APP = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(APP, "build"))
sys.path.insert(0, HERE)

from data import pretty
from build_demo import PAGES_ORIGIN, SERIES


def main():
    catalog = json.load(io.open(os.path.join(APP, "build", "catalog.json"), encoding="utf-8"))
    photos = {f.split("-")[0] for f in os.listdir(os.path.join(APP, "assets", "products"))
              if f.endswith(f"-{SERIES}-640.webp")}

    products = {}
    for item in catalog["items"]:
        products[item["id"]] = {
            "name": pretty(item["name"], item["section"]),
            "price": item["price"],
            "unit": item.get("unit") or "шт",
            "weight": item.get("weight") or "",
            "url": f"/catalog/{item['section']}/{item['id']}/",
            "image": item.get("image") or "",
            "section": item["section"],
            "composition": item.get("composition") or "",
        }

    body = (
            f"window.MS_ORIGIN = {json.dumps(PAGES_ORIGIN)};\n"
            f"window.MS_SERIES = {json.dumps(SERIES)};\n"
            f"window.MS_SECTIONS = {json.dumps([{'slug': x['slug'], 'name': x['title']} for x in catalog['sections']], ensure_ascii=False)};\n"
            f"window.MS_PHOTOS = {json.dumps(sorted(photos))};\n"
            f"window.MS_PRODUCTS = {json.dumps(products, ensure_ascii=False, indent=1)};\n")
    path = os.path.join(HERE, "cart-data.js")
    io.open(path, "w", encoding="utf-8", newline="\n").write(body)
    print(f"products: {len(products)}, with photos: {len(photos & set(products))}, written {path}")


if __name__ == "__main__":
    main()
