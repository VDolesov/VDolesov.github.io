import io
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
APP = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(APP, "build"))
sys.path.insert(0, HERE)

from data import EXTRA
from build_demo import PAGES_ORIGIN, SERIES

TEMPLATE_ID = "736"
TEMPLATE_NAME = "ПИРОГ С МЯСОМ"
TEMPLATE_PRICE = "780"
TEMPLATE_ARTICLE = "20002"
TEMPLATE_WEIGHT = "1000 г."
TEMPLATE_COMPOSITION = "Мука пшеничная в/с, сахар, маргарин, соль, масло растительное, дрожжи, говядина, свинина, лук"
TEMPLATE_PHOTOS = (
    "https://www.mirsladostey164.ru/upload/iblock/10e/10efb1f3909aeb35622f80442b8a4956.JPG",
    "https://www.mirsladostey164.ru/upload/iblock/969/969afa49f6b6c20c0ba4ffc44d19e394.JPG",
)
SECTION = os.path.join(APP, "catalog", "pirogi")


def read(path):
    return io.open(path, encoding="utf-8").read()


def write(path, html):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    io.open(path, "w", encoding="utf-8", newline="\n").write(html)


def div_end(html, start):
    depth, pos = 0, start
    tag = re.compile(r"<(/?)div\b[^>]*>")
    while True:
        m = tag.search(html, pos)
        depth += -1 if m.group(1) else 1
        pos = m.end()
        if depth == 0:
            return pos


def drop_property(html, title):
    m = re.search(r'<div class="properties__item properties__item--compact font_xs">\s*'
                  r'<div class="properties__title muted properties__item--inline">\s*' + title, html)
    if not m:
        return html
    return html[:m.start()] + html[div_end(html, m.start()):]


def retarget(html, item):
    pid, price = item["id"], str(item["price"])
    html = re.sub(r"(?<![\d.\-])" + TEMPLATE_ID + r"(?![\d.])", pid, html)
    html = html.replace(TEMPLATE_NAME, item["name"])
    html = re.sub(r"(?<!\d)" + TEMPLATE_ARTICLE + r"(?!\d)", item["article"], html)
    html = re.sub(r"'" + TEMPLATE_PRICE + r"( &#8381;)?'", lambda m: "'" + price + (m.group(1) or "") + "'", html)
    html = re.sub(r'(data-value|content)="' + TEMPLATE_PRICE + '"', lambda m: f'{m.group(1)}="{price}"', html)
    html = html.replace(f'<span class="price_value">{TEMPLATE_PRICE}</span>', f'<span class="price_value">{price}</span>')
    html = html.replace('<span class="price_measure">/кг</span>', f'<span class="price_measure">/{item["unit"]}</span>')
    for photo in TEMPLATE_PHOTOS:
        html = html.replace(photo, f"{PAGES_ORIGIN}/assets/products/{pid}-{SERIES}.webp")
    return html


def build_page(template, item):
    html = retarget(template, item)
    html = html.replace(TEMPLATE_COMPOSITION, item["composition"])
    html = html.replace(TEMPLATE_WEIGHT, item["weight"] + ".")
    if not item.get("energy"):
        html = drop_property(html, "Энергетическая ценность")
    if not item.get("nutrition"):
        html = drop_property(html, "Пищевая ценность")
    return html


def card_bounds(html, pid):
    anchor = html.find(f'id="bx_basket_div_{pid}_block"')
    if anchor == -1:
        return None
    start = html.rfind('<div class="col-', 0, anchor)
    return start, div_end(html, start)


def add_cards(items):
    path = os.path.join(SECTION, "index.html")
    html = read(path)
    for item in items:
        bounds = card_bounds(html, item["id"])
        if bounds:
            html = html[:bounds[0]] + html[bounds[1]:]
    start, end = card_bounds(html, TEMPLATE_ID)
    card = html[start:end]
    first = re.search(r'<div class="col-[^"]*item_block', html).start()
    cards = "\n".join(retarget(card, item) for item in items) + "\n"
    write(path, html[:first] + cards + html[first:])


def main():
    template = read(os.path.join(SECTION, TEMPLATE_ID, "index.html"))
    for item in EXTRA:
        write(os.path.join(SECTION, item["id"], "index.html"), build_page(template, item))
        print(f"  /catalog/pirogi/{item['id']}/")
    add_cards(EXTRA)
    print(f"  /catalog/pirogi/: {len(EXTRA)} cards")


if __name__ == "__main__":
    main()
