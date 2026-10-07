import io
import os
import re

import subprocess

import vendor
from vendor_local import CONTAINER, ENV, WEB, container_file, save

APP = vendor.APP
CACHE = "/bitrix/cache/css/s1/aspro_max/"
BUNDLES = {"page": ("sale.location.selector.search", "/vendor/order/order-page.css"),
           "template": ("sale.order.ajax/v1/style", "/vendor/order/template-order.css")}
STATIC_CSS = {
    "/bitrix/css/main/themes/blue/style.min.css": "/vendor/order/theme-blue.css",
    "/bitrix/templates/aspro_max/css/mirsladostey-design/native-components.css": "/vendor/order/native-components.css",
}
PAY_LOGOS = ("/upload/sale/paysystem/logotip/ae5/ae562c5ef5496bc1fcf9d687ebd6fc69.png",
             "/upload/sale/paysystem/logotip/277/277bac3584decb235d4c33e57d86e33d.png")
PAGE_LINKS = ["/vendor/order/theme-blue.css", "/vendor/order/order-page.css"]
NATIVE = "/vendor/order/native-components.css"
TITLE = "Оформление заказа"
DESCRIPTION = "Оформление заказа «Мир Сладостей»: самовывоз из магазинов или доставка по Саратову."
_URL = re.compile(r"url\(\s*(['\"]?)(/(?!/)[^'\")]+)\1\s*\)")


def order_bundle(kind, marker):
    cmd = f"grep -l '{marker}' $(ls -t {WEB}{CACHE}{kind}_*/*_v1.css) | head -1"
    out = subprocess.run(["docker", "exec", CONTAINER, "sh", "-c", cmd], capture_output=True, text=True, env=ENV)
    found = out.stdout.strip()
    if not found:
        raise SystemExit(f"no {kind} bundle with {marker}; open /order/ on the local site with items in the basket")
    return found[len(WEB):]


def local_css():
    css = {order_bundle(kind, marker): target for kind, (marker, target) in BUNDLES.items()}
    css.update(STATIC_CSS)
    return css


def vendor_css():
    assets = set()
    local = local_css()
    for source, target in local.items():
        data = container_file(source)
        if data is None:
            raise SystemExit("missing " + source)
        css = data.decode("utf-8", "surrogateescape")

        def link(m):
            path = m.group(2).split("?")[0].split("#")[0]
            if path.startswith("/vendor/"):
                return m.group(0)
            assets.add(path)
            return "url(" + m.group(1) + "/vendor" + m.group(2) + m.group(1) + ")"
        css = _URL.sub(link, css)
        full = os.path.join(APP, *target.strip("/").split("/"))
        os.makedirs(os.path.dirname(full), exist_ok=True)
        io.open(full, "w", encoding="utf-8", errors="surrogateescape", newline="\n").write(css.replace("\r\n", "\n"))
    assets.update(PAY_LOGOS)
    copied = 0
    for path in sorted(assets):
        if vendor.vendored(path):
            continue
        data = container_file(path)
        if data is not None:
            save(path, data)
            copied += 1
    print(f"order css: {len(local)} files, {copied} new assets")


def link_tag(href):
    return f'<link href="{href}" type="text/css" rel="stylesheet" />\n'


def swap_link(html, pattern, links):
    old = re.search(r'<link[^>]+href="' + pattern + r'"[^>]*>\n?', html)
    if not old:
        raise SystemExit("no link " + pattern)
    return html.replace(old.group(0), "".join(link_tag(h) for h in links), 1)


def build_order():
    basket = io.open(os.path.join(APP, "basket", "index.html"), encoding="utf-8").read()
    html = re.sub(r"<title>[^<]*</title>", f"<title>{TITLE} — Мир Сладостей</title>", basket, count=1)
    html = re.sub(r'(<meta property="og:title" content=")[^"]*(")', lambda m: m.group(1) + TITLE + " — Мир Сладостей" + m.group(2), html, count=1)
    html = re.sub(r'(<meta name="description" content=")[^"]*(")', lambda m: m.group(1) + DESCRIPTION + m.group(2), html, count=1)
    html = re.sub(r'(<meta property="og:description" content=")[^"]*(")', lambda m: m.group(1) + DESCRIPTION + m.group(2), html, count=1)
    html = re.sub(r'(<meta property="og:url" content="[^"]*?)/basket/(")', r"\1/order/\2", html, count=1)
    html = html.replace('<h1 id="pagetitle">Корзина</h1>', f'<h1 id="pagetitle">{TITLE}</h1>', 1)
    html = re.sub(r'(<span itemprop="name" class="breadcrumbs__item-name font_xs">)Корзина(</span>)', r"\1" + TITLE + r"\2", html)
    html = re.sub(r'(<link href=")/basket/(" itemprop="item")', r"\1/order/\2", html)
    html = swap_link(html, r"/vendor/css/page_[0-9a-f]+_v1\.css", PAGE_LINKS)
    html = swap_link(html, r"/vendor/css/template_[0-9a-f]+_v1\.css", [BUNDLES["template"][1]])
    if TITLE not in html:
        raise SystemExit("order title not set")
    folder = os.path.join(APP, "order")
    os.makedirs(folder, exist_ok=True)
    io.open(os.path.join(folder, "index.html"), "w", encoding="utf-8", newline="\n").write(html)
    print("order/index.html written")


def link_native():
    for page in ("basket", "order"):
        full = os.path.join(APP, page, "index.html")
        html = io.open(full, encoding="utf-8").read()
        skin = re.search(r'<link rel="stylesheet" href="/skin/skin\.css\?v=[0-9a-f]+">', html)
        if NATIVE in html or not skin:
            continue
        html = html.replace(skin.group(0), skin.group(0) + "\n" + f'<link rel="stylesheet" href="{NATIVE}">', 1)
        io.open(full, "w", encoding="utf-8", newline="\n").write(html)
        print("native components linked on", page)


def main():
    vendor_css()
    build_order()
    link_native()


if __name__ == "__main__":
    main()
