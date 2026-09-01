# -*- coding: utf-8 -*-
"""Сборка products.js из снимка каталога.

Данные берутся из build/catalog.json (реальные цены, артикулы, состав и КБЖУ
с сайта предприятия) и дополняются позициями, которых в нём ещё нет —
осетинскими пирогами собственной съёмки.
"""
import json
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
APP = os.path.dirname(HERE)
OUT = os.path.join(APP, "products.js")

SECTIONS = [
    ("torty", "Торты", "Торты", "Праздничный торт собственного производства: мягкие коржи, крем и сбалансированная сладость."),
    ("pirogi", "Пироги", "Пироги", "Домашний пирог с щедрой начинкой и румяным тестом — для семейного стола, офиса и праздника."),
    ("vypechka", "Выпечка", "Выпечка", "Свежая выпечка из слоёного теста — хрустящая снаружи и сочная внутри."),
    ("pirozhnye_i_deserty", "Пирожные и десерты", "Десерты", "Порционный десерт с выразительной текстурой и аккуратной подачей."),
    ("pechene", "Печенье", "Печенье", "Печенье собственной выпечки — к чаю, кофе и в подарочный набор."),
    ("salaty", "Салаты", "Салаты", "Готовый салат для домашнего обеда или праздничного стола. Небольшие партии."),
    ("vtorye_blyuda", "Вторые блюда", "Горячее", "Горячее блюдо собственного производства. Остаётся разогреть и подать к столу."),
    ("polufabrikaty", "Полуфабрикаты", "Полуфабрикаты", "Домашние полуфабрикаты для быстрого ужина — удобно хранить и легко приготовить."),
    ("napitki", "Напитки", "Напитки", "Фруктово-ягодный напиток в удобном формате — к выпечке, обеду или празднику."),
]

# позиции собственной съёмки, которых нет в каталоге предприятия
EXTRA = [
    {"id": "801", "section": "pirogi", "name": "Осетинский пирог с мясом", "price": 890,
     "unit": "шт", "article": "10801", "badges": ["Новинка"],
     "weight": "1000 г", "composition": "Мука пшеничная в/с, вода, дрожжи, соль, говядина, лук репчатый, специи",
     "energy": "", "nutrition": "",
     "note": "Традиционный фыдджын: тонкое тесто и сочная начинка из рубленого мяса с луком."},
    {"id": "802", "section": "pirogi", "name": "Осетинский пирог с картофелем и сыром", "price": 690,
     "unit": "шт", "article": "10802", "badges": [],
     "weight": "1000 г", "composition": "Мука пшеничная в/с, вода, дрожжи, соль, картофель, сыр, масло сливочное",
     "energy": "", "nutrition": "",
     "note": "Картофджын с мягким картофелем и сыром — сливочный и сытный."},
    {"id": "803", "section": "pirogi", "name": "Осетинский пирог с зеленью и сыром", "price": 720,
     "unit": "шт", "article": "10803", "badges": ["Сезонный"],
     "weight": "1000 г", "composition": "Мука пшеничная в/с, вода, дрожжи, соль, зелень, сыр",
     "energy": "", "nutrition": "",
     "note": "Цахараджын со свежей зеленью и сыром — яркий аромат и тонкая румяная корочка."},
]

TYPE_BY_SECTION = {
    "torty": "Торт", "salaty": "Салат", "pechene": "Печенье",
}


def pretty(name, section):
    """Приводит названия каталога к читаемому виду.

    «ПИРОГ С ВИШНЕЙ» → «Пирог с вишней», «Торт "ПРАГА"» → «Торт «Прага»».
    """
    PREPOSITIONS = ("с ", "со ", "из ", "по ", "в ", "на ")
    name = name.strip().strip('"').strip()

    m = re.match(r'^(Торт|Салат|Десерт|Печенье|Пирог)\s+"?(.+?)"?$', name, re.I)
    prefix, core = (m.group(1), m.group(2)) if m else ("", name)

    if core.isupper():
        core = core.capitalize()
    if not prefix:
        prefix = TYPE_BY_SECTION.get(section, "")

    if not prefix:
        return core
    prefix = prefix.capitalize()

    # «с вишней» — это описание начинки, имя собственное берём в кавычки
    if core.lower().startswith(PREPOSITIONS):
        return f"{prefix} {core[0].lower() + core[1:]}"
    if core.lower().startswith(prefix.lower()):
        return core
    return f"{prefix} «{core}»"


def js_string(value):
    return json.dumps(value or "", ensure_ascii=False)


def main():
    catalog = json.load(open(os.path.join(HERE, "catalog.json"), encoding="utf-8"))
    items = []
    for it in catalog["items"]:
        items.append({
            "id": it["id"], "section": it["section"],
            "name": pretty(it["name"], it["section"]),
            "price": it["price"], "unit": it["unit"] or "шт",
            "article": it["article"], "badges": it["badges"],
            "weight": it["weight"], "composition": it["composition"],
            "energy": it["energy"], "nutrition": it["nutrition"], "note": "",
        })
    items += EXTRA

    order = {s[0]: i for i, s in enumerate(SECTIONS)}
    items.sort(key=lambda x: (order.get(x["section"], 99), int(x["id"])))

    lines = []
    lines.append("/* Данные каталога «Мир сладостей».")
    lines.append("   Собрано автоматически: build/data.py из build/catalog.json.")
    lines.append("   Разделы и адреса повторяют структуру mirsladostey164.ru. */")
    lines.append("(() => {")
    lines.append('  "use strict";')
    lines.append("")
    lines.append("  const SECTIONS = [")
    for slug, title, short, descr in SECTIONS:
        lines.append(f"    {{ slug: {js_string(slug)}, title: {js_string(title)}, "
                     f"short: {js_string(short)}, description: {js_string(descr)} }},")
    lines.append("  ];")
    lines.append("")
    lines.append("  const PRODUCTS = [")
    for it in items:
        badge = it["badges"][0] if it["badges"] else ""
        lines.append("    {")
        lines.append(f"      id: {js_string(it['id'])}, section: {js_string(it['section'])},")
        lines.append(f"      name: {js_string(it['name'])},")
        lines.append(f"      price: {it['price']}, unit: {js_string(it['unit'])},")
        lines.append(f"      article: {js_string(it['article'])}, badge: {js_string(badge)},")
        lines.append(f"      weight: {js_string(it['weight'])},")
        lines.append(f"      composition: {js_string(it['composition'])},")
        lines.append(f"      energy: {js_string(it['energy'])}, nutrition: {js_string(it['nutrition'])},")
        lines.append(f"      note: {js_string(it['note'])},")
        lines.append(f"      image: \"/assets/products/{it['id']}-v7.webp\"")
        lines.append("    },")
    lines.append("  ];")
    lines.append("")
    lines.append("  const SECTION_MAP = Object.fromEntries(SECTIONS.map(s => [s.slug, s]));")
    lines.append("  PRODUCTS.forEach(p => {")
    lines.append("    p.sectionTitle = SECTION_MAP[p.section].title;")
    lines.append('    p.availability = ["torty", "pirogi"].includes(p.section)')
    lines.append('      ? "Предзаказ от 24 часов" : "Наличие уточнит менеджер";')
    lines.append("    p.description = p.note || SECTION_MAP[p.section].description;")
    lines.append('    p.url = `/catalog/${p.section}/${p.id}/`;')
    lines.append("  });")
    lines.append("")
    lines.append("  window.MS_DATA = {")
    lines.append("    SECTIONS, SECTION_MAP, PRODUCTS,")
    lines.append('    FEATURED_IDS: ["801", "747", "749", "778", "746", "765"],')
    lines.append("    MIN_ORDER: 800, FREE_DELIVERY: 3000, DELIVERY_FEE: 150")
    lines.append("  };")
    lines.append("})();")

    with open(OUT, "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(lines) + "\n")

    print("товаров:", len(items))
    for slug, title, *_ in SECTIONS:
        n = len([i for i in items if i["section"] == slug])
        print(f"  {title}: {n}")
    print("записано:", OUT)


if __name__ == "__main__":
    main()
