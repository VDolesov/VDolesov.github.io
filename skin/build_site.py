# -*- coding: utf-8 -*-
"""Полный сайт с новым оформлением — все страницы, все ссылки внутри.

Обходит боевой сайт по внутренним ссылкам, каждую страницу пропускает
через ту же обработку, что и демонстрация (встраивание отложенных блоков,
раскрытие ленивых картинок, свой баннер, своя фотосерия), и кладёт в корень
репозитория по тому же адресу, что и на боевом сайте:

    /catalog/torty/747/  →  catalog/torty/747/index.html

Ссылки между страницами остаются относительными и ведут внутрь. Стили,
скрипты и картинки шаблона грузятся с исходного домена — их адреса
переписаны в абсолютные. Файл оформления подключается локально.

    python skin/build_site.py
"""
import hashlib
import io
import json
import os
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
APP = os.path.dirname(HERE)
sys.path.insert(0, HERE)

from build_demo import (DEMO_FIX, PAGES_ORIGIN, PHOTO_SCRIPT, SECTION_PHOTOS,  # noqa: E402
                        SITE, inline_deferred, product_ids, swap_banner, unlazy)

HOSTS = {"www.mirsladostey164.ru", "mirsladostey164.ru"}
SEEDS = ["/", "/catalog/", "/basket/", "/personal/", "/search/", "/contacts/",
         "/company/", "/help/", "/info/", "/news/", "/sale/", "/services/"]
LIMIT = 320
PAUSE = 0.25

# сюда не ходим: служебные разделы и всё, что требует запроса или входа
SKIP_PREFIX = ("/bitrix/", "/upload/", "/local/", "/ajax/", "/include/",
               "/auth/", "/login/", "/personal/order/", "/personal/cart/",
               "/personal/profile/", "/personal/subscribe/", "/order/")
ASSET_EXT = (".css", ".js", ".ico", ".png", ".jpg", ".jpeg", ".gif", ".svg",
             ".webp", ".woff", ".woff2", ".ttf", ".eot", ".xml", ".json",
             ".pdf", ".mp4", ".txt", ".zip", ".doc", ".docx", ".xls", ".xlsx")


def is_page(path):
    """Внутренняя страница: без расширения файла и не из служебных разделов."""
    if not path.startswith("/") or path.startswith("//"):
        return False
    if path.startswith(SKIP_PREFIX):
        return False
    tail = path.rsplit("/", 1)[-1]
    if "." in tail:
        return False
    return True


def normalize(href, current):
    """Абсолютный путь страницы или None, если ссылка не внутренняя."""
    href = href.strip()
    if not href or href.startswith(("#", "javascript:", "mailto:", "tel:", "data:")):
        return None
    parsed = urllib.parse.urlparse(href)
    if parsed.scheme and parsed.netloc and parsed.netloc not in HOSTS:
        return None
    path = parsed.path or "/"
    if not path.startswith("/"):
        path = urllib.parse.urljoin(current, path)
    path = re.sub(r"/{2,}", "/", path)
    if not path.endswith("/"):
        path += "/"
    return path if is_page(path) else None


def discover(html, current):
    found = set()
    for href in re.findall(r'<a\s[^>]*?href="([^"]*)"', html, flags=re.I):
        path = normalize(href, current)
        if path:
            found.add(path)
    return found


def fetch(path):
    request = urllib.request.Request(SITE + path, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(request, timeout=60) as response:
        final = urllib.parse.urlparse(response.geturl()).path
        return response.read().decode("utf-8", "ignore"), final


# ------------------------------------------------------------ переписывание

_ATTR_SRC = re.compile(r'\b(src|data-src|data-bg|data-original|poster)="(/(?!/)[^"]*)"', re.I)
_ATTR_SRCSET = re.compile(r'\b(srcset|data-srcset)="([^"]*)"', re.I)
_ATTR_HREF = re.compile(r'\bhref="(/(?!/)[^"]*)"', re.I)
_CSS_URL = re.compile(r"url\((['\"]?)(/(?!/)[^'\")]*)\1\)", re.I)
_A_HREF = re.compile(r'(<a\s[^>]*?href=")([^"]*)(")', re.I | re.S)
_FORM = re.compile(r'(<form\b[^>]*?\baction=")([^"]*)(")', re.I)


def _asset_href(url):
    base = url.split("?", 1)[0].split("#", 1)[0]
    return (base.lower().endswith(ASSET_EXT)
            or base.startswith(("/bitrix/", "/upload/", "/local/", "/images/", "/img/")))


def absolutize_assets(html):
    """Ресурсы шаблона — с исходного домена; свои (/assets, /skin) — местные."""
    def own(url):
        return url.startswith(("/assets/", "/skin/"))

    html = _ATTR_SRC.sub(lambda m: m.group(0) if own(m.group(2))
                         else f'{m.group(1)}="{SITE}{m.group(2)}"', html)

    def srcset(m):
        parts = []
        for item in m.group(2).split(","):
            item = item.strip()
            if item.startswith("/") and not item.startswith("//") and not own(item):
                item = SITE + item
            parts.append(item)
        return f'{m.group(1)}="{", ".join(parts)}"'
    html = _ATTR_SRCSET.sub(srcset, html)

    html = _ATTR_HREF.sub(lambda m: f'href="{SITE}{m.group(1)}"'
                          if _asset_href(m.group(1)) and not own(m.group(1)) else m.group(0), html)
    html = _CSS_URL.sub(lambda m: m.group(0) if own(m.group(2))
                        else f"url({m.group(1)}{SITE}{m.group(2)}{m.group(1)})", html)
    return html


def localize_links(html, current):
    """Ссылки на страницы — внутрь сайта, без запросов и без исходного домена."""
    def link(m):
        href = m.group(2)
        parsed = urllib.parse.urlparse(href.strip())
        if parsed.scheme and parsed.netloc in HOSTS:
            href = parsed.path or "/"
            if parsed.fragment:
                href += "#" + parsed.fragment
        path = normalize(href, current)
        if path is None:
            return m.group(0)
        fragment = urllib.parse.urlparse(href).fragment
        return f"{m.group(1)}{path}{'#' + fragment if fragment else ''}{m.group(3)}"
    html = _A_HREF.sub(link, html)

    # формы поиска и обратной связи некуда отправлять — ведут на каталог
    html = _FORM.sub(lambda m: f'{m.group(1)}/catalog/{m.group(3)}', html)
    return html


def skin_version():
    with open(os.path.join(HERE, "skin.css"), "rb") as f:
        return hashlib.md5(f.read()).hexdigest()[:8]


def build_page(path, html, ids, version):
    html = inline_deferred(html)
    html = unlazy(html)
    html = swap_banner(html)
    html = absolutize_assets(html)
    html = localize_links(html, path)

    # <base> не нужен: страницы лежат по своим адресам, ссылки относительные
    html = re.sub(r"<base\s[^>]*>", "", html, flags=re.I)

    link = f'\n<link rel="stylesheet" href="/skin/skin.css?v={version}">\n</head>'
    html = html.replace("</head>", link, 1)

    match = re.search(r"/catalog/[a-z_]+/(\d+)/", path)
    script = (PHOTO_SCRIPT.replace("%IDS%", json.dumps(ids))
                          .replace("%ORIGIN%", PAGES_ORIGIN)
                          .replace("%PAGE_ID%", match.group(1) if match else "")
                          .replace("%SECTIONS%", json.dumps(SECTION_PHOTOS)))
    return html.replace("</body>", script + DEMO_FIX + "\n</body>", 1)


def write(path, html):
    folder = os.path.join(APP, *[p for p in path.split("/") if p])
    os.makedirs(folder, exist_ok=True)
    with io.open(os.path.join(folder, "index.html"), "w", encoding="utf-8", newline="\n") as f:
        f.write(html)


def main():
    ids = product_ids()
    version = skin_version()
    queue = list(SEEDS)
    seen = set(queue)
    done, failed = [], []

    while queue and len(done) < LIMIT:
        path = queue.pop(0)
        try:
            raw, final = fetch(path)
        except urllib.error.HTTPError as exc:
            failed.append((path, exc.code))
            print(f"  {path}: {exc.code}")
            continue
        except Exception as exc:
            failed.append((path, str(exc)[:40]))
            print(f"  {path}: {exc}")
            continue

        if not final.endswith("/"):
            final += "/"
        if final != path and final in seen:
            # адрес перенаправился на уже известную страницу
            continue
        seen.add(final)

        for link in sorted(discover(raw, final)):
            if link not in seen:
                seen.add(link)
                queue.append(link)

        html = build_page(final, raw, ids, version)
        write(final, html)
        done.append(final)
        print(f"  {final}")
        time.sleep(PAUSE)

    with io.open(os.path.join(HERE, "site-pages.json"), "w", encoding="utf-8") as f:
        json.dump({"pages": done, "failed": failed, "skin": version}, f, ensure_ascii=False, indent=1)
    print(f"страниц собрано: {len(done)}, не удалось: {len(failed)}, в очереди осталось: {len(queue)}")


def restamp():
    """Обновляет версию skin.css во всех собранных страницах без обхода сайта."""
    version = skin_version()
    pattern = re.compile(r"/skin/skin\.css\?v=[0-9a-f]+")
    count = 0
    for root, dirs, files in os.walk(APP):
        dirs[:] = [d for d in dirs if d not in (".git", "skin", "build", "assets")]
        for name in files:
            if name != "index.html":
                continue
            full = os.path.join(root, name)
            html = io.open(full, encoding="utf-8").read()
            fresh = pattern.sub(f"/skin/skin.css?v={version}", html)
            if fresh != html:
                io.open(full, "w", encoding="utf-8", newline="\n").write(fresh)
                count += 1
    print(f"версия {version} проставлена в {count} страницах")


if __name__ == "__main__":
    if "--stamp" in sys.argv:
        restamp()
    else:
        main()
