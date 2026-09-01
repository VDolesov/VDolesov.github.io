# -*- coding: utf-8 -*-
"""Полная пересборка витрины.

    python build/build_all.py

Сначала удаляются ранее сгенерированные каталоги, затем создаются заново:
главная, каталог, разделы, карточки товаров, корзина, оформление, поиск,
отложенные и текстовые разделы. Адреса совпадают со структурой
mirsladostey164.ru, чтобы вёрстку можно было положить на существующий бэкенд.
"""
import os
import shutil
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import pages
import pages_text

APP = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

GENERATED = ["catalog", "basket", "order", "search", "favorites", "company",
             "contacts", "help", "sale", "services", "info", "personal", "about"]


def clean():
    for folder in GENERATED:
        path = os.path.join(APP, folder)
        if os.path.isdir(path):
            shutil.rmtree(path)


def main():
    clean()
    items = pages.load_items()

    pages.build_home()
    pages.build_catalog_index()
    for section in pages.SECTIONS:
        pages.build_section(section, items)
    for item in items:
        pages.build_product(item, items)

    pages.build_basket()
    pages.build_order()
    pages.build_search()
    pages.build_favorites()
    pages_text.build_all_text()

    total = sum(len(files) for _, _, files in os.walk(APP)
                if True)
    html = sum(1 for root, _, files in os.walk(APP) for f in files
               if f == "index.html")
    print(f"товаров: {len(items)}")
    print(f"страниц: {html}")


main()
