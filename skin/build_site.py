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

from legal import legal_copy
from naming import name_pages
from vendor import vendor_assets
from strip import strip_sections
from build_demo import (BANNER, BANNER_COPY, IMAGES, DEMO_FIX, PAGES_ORIGIN, PHOTO_SCRIPT,
                        SECTION_PHOTOS, SERIES, SITE, inline_deferred, product_ids,
                        add_faq, expand_slides, swap_banner, swap_photos, unlazy)

HOSTS = {"www.mirsladostey164.ru", "mirsladostey164.ru"}
SEEDS = ["/", "/catalog/", "/basket/", "/personal/", "/search/", "/contacts/",
         "/company/", "/help/", "/info/", "/news/", "/sale/", "/services/"]
LIMIT = 320
PAUSE = 0.25


SKIP_PREFIX = ("/bitrix/", "/upload/", "/local/", "/ajax/", "/include/",
               "/auth/", "/login/", "/personal/order/", "/personal/cart/",
               "/personal/profile/", "/personal/subscribe/", "/order/")
ALIAS = {
    "/personal/": "/auth/",
    "/company/index.php/": "/company/",
    "/include/licenses_detail.php": "/company/agreement/",
    "/include/licenses_pologenie.php": "/company/personal-data/",
}
SOURCE = {alias: path for path, alias in ALIAS.items() if path.endswith(".php")}
DROP = ("/info/brands/rss/", "/help/warranty/", "/company/licenses/", "/info/brands/", "/services/", "/blog/")
_COUNTER = re.compile(r"<!-- Yandex\.Metrika counter -->.*?<!-- /Yandex\.Metrika counter -->", re.S)
_MONTSERRAT = re.compile(r'[ \t]*<link rel="(?:preload|stylesheet)" href="https://fonts\.googleapis\.com/css\?family=Montserrat[^"]*"[^>]*>\n?')
_BEACON = re.compile(r"<script>new Image\(\)\.src='https?://[^']*spread\.php[^<]*</script>")
_YMAPS_LOADER = re.compile(r"<script>\s*var script = document\.createElement\('script'\);\s*script\.src = '(https://api-maps\.yandex\.ru/[^']+)';"
                           r"\s*\(document\.head \|\| document\.documentElement\)\.appendChild\(script\);\s*script\.onload = function \(\) \{"
                           r"\s*this\.parentNode\.removeChild\(script\);\s*\};\s*</script>")
_SCRIPT = re.compile(r"<script\b[^>]*>.*?</script>[ \t]*\n?", re.S | re.I)


def lazy_map(html):
    return _YMAPS_LOADER.sub(lambda m: "<script>window.MS_YMAPS_URL = '" + m.group(1) + "';</script>", html)


def move_scripts(html):
    end = html.rfind("</body>")
    if end == -1:
        return html
    moved = []

    def take(m):
        if "data-skip-moving" in m.group(0)[:m.group(0).find(">")]:
            return m.group(0)
        moved.append(m.group(0).strip())
        return ""
    rest = _SCRIPT.sub(take, html[:end])
    return rest + "\n".join(moved) + "\n" + html[end:]
PRELOAD = '<link rel="preload" as="image" href="%s">\n'
FONT_FILES = ("golos-text-cyrillic.woff2", "prata-cyrillic.woff2")
FONT_PRELOAD = "".join(f'<link rel="preload" as="font" type="font/woff2" href="/skin/fonts/{name}" crossorigin>\n'
                       for name in FONT_FILES)
ASSET_EXT = (".css", ".js", ".ico", ".png", ".jpg", ".jpeg", ".gif", ".svg",
             ".webp", ".woff", ".woff2", ".ttf", ".eot", ".xml", ".json",
             ".pdf", ".mp4", ".txt", ".zip", ".doc", ".docx", ".xls", ".xlsx")


def is_page(path):
    if not path.startswith("/") or path.startswith("//"):
        return False
    if path.startswith(SKIP_PREFIX):
        return False
    tail = path.rsplit("/", 1)[-1]
    if "." in tail:
        return False
    return True


def normalize(href, current):
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
    alias = ALIAS.get(path, ALIAS.get(path + "/"))
    if alias:
        return alias
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

_ATTR_SRC = re.compile(r'\b(src|data-src|data-bg|data-original|poster)="(/(?!/)[^"]*)"', re.I)
_ATTR_SRCSET = re.compile(r'\b(srcset|data-srcset)="([^"]*)"', re.I)
_ATTR_HREF = re.compile(r'\bhref="(/(?!/)[^"]*)"', re.I)
_CSS_URL = re.compile(r"url\((['\"]?)(/(?!/)[^'\")]*)\1\)", re.I)
_A_HREF = re.compile(r'(<a\s[^>]*?href=")([^"]*)(")', re.I | re.S)
_FORM = re.compile(r'(<form\b[^>]*?\baction=")([^"]*)(")', re.I)
_LOAD = re.compile(r"(BX\.(?:loadCSS|loadScript|load)\(\[)([^\]]*)(\])")


def absolutize_loads(html):
    return _LOAD.sub(lambda m: m.group(1) + m.group(2).replace("'/bitrix/", f"'{SITE}/bitrix/")
                     .replace("'/local/", f"'{SITE}/local/") + m.group(3), html)


_SOURCE_CSS = re.compile(r'(<link\b[^>]*?href=")(https://www\.mirsladostey164\.ru/bitrix/cache/css/[^"?]+\.css)(?:\?[^"]*)?(")')
_SOURCE_JUNK = re.compile(r'[ \t]*<link\b[^>]*?href="https://www\.mirsladostey164\.ru/bitrix/js/'
                          r'(?:ui/buttons/src/css/ui\.buttons\.ie|main/core/css/core_finder\.min)\.css[^"]*"[^>]*>\n?')
_ROOT_URL = re.compile(r"""url\(\s*(['"]?)/(?!/)""")
VENDOR = os.path.join(APP, "vendor", "css")


def vendor_css(html):
    def local(m):
        url = m.group(2)
        cached = os.path.join(HERE, "cache", hashlib.md5(url.encode()).hexdigest()[:12] + ".css")
        if not os.path.exists(cached):
            return m.group(0)
        name = url.rsplit("/", 1)[1]
        target = os.path.join(VENDOR, name)
        if not os.path.exists(target):
            os.makedirs(VENDOR, exist_ok=True)
            css = io.open(cached, encoding="utf-8", errors="ignore").read()
            css = _ROOT_URL.sub(lambda u: f"url({u.group(1)}{SITE}/", css)
            io.open(target, "w", encoding="utf-8", newline="\n").write(css)
        return f"{m.group(1)}/vendor/css/{name}{m.group(3)}"
    html = _SOURCE_JUNK.sub("", html)
    return _SOURCE_CSS.sub(local, html)


def _asset_href(url):
    base = url.split("?", 1)[0].split("#", 1)[0]
    return (base.lower().endswith(ASSET_EXT)
            or base.startswith(("/bitrix/", "/upload/", "/local/", "/images/", "/img/")))


def absolutize_assets(html):
    def own(url):
        return url.startswith(("/assets/", "/skin/", "/vendor/"))

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

    html = _FORM.sub(lambda m: f'{m.group(1)}/catalog/{m.group(3)}', html)
    return html

SCRIPTS = ("cart-data.js", "cart.js", "nav.js", "search.js", "demo.js", "motion.js", "map.js")


def skin_version():
    digest = hashlib.md5()
    for name in ("skin.css",) + SCRIPTS:
        with open(os.path.join(HERE, name), "rb") as f:
            digest.update(f.read())
    return digest.hexdigest()[:8]


def script_tags(version):
    return "".join(f'<script src="/skin/{name}?v={version}"></script>\n' for name in SCRIPTS)


def build_page(path, html, ids, version):
    html = inline_deferred(html)
    html = unlazy(html)
    html = swap_banner(html)
    html = absolutize_assets(html)
    html = localize_links(html, path)
    html = absolutize_loads(html)
    html = swap_photos(html, page_id(path))
    html = add_faq(html)
    html = _COUNTER.sub("", html)
    html = _MONTSERRAT.sub("", html)
    html = vendor_css(html)
    html = vendor_assets(html)
    html = strip_sections(html)
    html = legal_copy(html)
    html = name_pages(html, path)
    html = _BEACON.sub("", html)

    html = re.sub(r"<base\s[^>]*>", "", html, flags=re.I)

    link = f'\n<link rel="stylesheet" href="/skin/skin.css?v={version}">\n</head>'
    html = html.replace("</head>", link, 1)
    html = preload_hero(html, path)

    return html.replace("</body>", photo_script(path, ids) + DEMO_FIX + "\n" + script_tags(version) + "</body>", 1)


def preload_hero(html, path):
    html = re.sub(r'<link rel="preload" as="image" href="[^"]*/assets/hero-[^"]*">\n', "", html)
    html = re.sub(r'<link rel="preload" as="font" type="font/woff2" href="/skin/fonts/[^"]*" crossorigin>\n', "", html)
    early = FONT_PRELOAD
    if path == "/":
        early += PRELOAD % (PAGES_ORIGIN + list(BANNER.values())[0])
    return re.sub(r"(<head\b[^>]*>\n?)", lambda m: m.group(1) + early, html, count=1)


def photo_script(path, ids):
    return (PHOTO_SCRIPT.replace("%IDS%", json.dumps(ids))
                        .replace("%ORIGIN%", PAGES_ORIGIN)
                        .replace("%SERIES%", SERIES)
                        .replace("%PAGE_ID%", page_id(path) or "")
                        .replace("%SECTIONS%", json.dumps(SECTION_PHOTOS)))


def write(path, html):
    folder = os.path.join(APP, *[p for p in path.split("/") if p])
    os.makedirs(folder, exist_ok=True)
    with io.open(os.path.join(folder, "index.html"), "w", encoding="utf-8", newline="\n") as f:
        f.write(html.replace("\r\n", "\n"))


def main(targets=None):
    ids = product_ids()
    version = skin_version()
    queue = list(targets or SEEDS)
    seen = set(queue)
    done, failed = [], []
    manifest = os.path.join(HERE, "site-pages.json")

    while queue and len(done) < LIMIT:
        path = queue.pop(0)
        try:
            raw, final = fetch(SOURCE.get(path, path))
        except urllib.error.HTTPError as exc:
            failed.append((path, exc.code))
            print(f"  {path}: {exc.code}")
            continue
        except Exception as exc:
            failed.append((path, str(exc)[:40]))
            print(f"  {path}: {exc}")
            continue

        final = ALIAS.get(final, final)
        if not final.endswith("/"):
            final += "/"
        if final != path and final in seen:

            continue
        seen.add(final)

        html = build_page(final, raw, ids, version)
        if not targets:
            for link in sorted(discover(html, final)):
                if link not in seen and link not in DROP:
                    seen.add(link)
                    queue.append(link)
        write(final, html)
        done.append(final)
        print(f"  {final}")
        time.sleep(PAUSE)

    if targets and os.path.exists(manifest):
        with io.open(manifest, encoding="utf-8") as f:
            previous = json.load(f)
        done = sorted(set(previous["pages"]) | set(done))
        failed = previous["failed"] + failed
    with io.open(manifest, "w", encoding="utf-8", newline="\n") as f:
        json.dump({"pages": done, "failed": failed, "skin": version}, f, ensure_ascii=False, indent=1)
        f.write("\n")
    print(f"pages built: {len(done)}, failed: {len(failed)}, left in queue: {len(queue)}")


def page_id(path):
    match = re.search(r"/catalog/[a-z_]+/(\d+)/", path)
    return match.group(1) if match else None


def refresh(html, path=""):
    html = re.sub(r'(/assets/products/" \+ [^"]+ \+ ")-v\d+\.webp"',
                  lambda m: m.group(1) + "-" + SERIES + '.webp"', html)
    html = re.sub(r"/assets/hero-bg\.(?:jpg|webp)\?v=\d+", next(iter(BANNER.values())), html)
    for pattern, new in BANNER_COPY:
        html = re.sub(pattern, new, html)
    html = expand_slides(html)
    for old, new in IMAGES.items():
        html = html.replace(old, PAGES_ORIGIN + new)
    for old, new in ALIAS.items():
        html = html.replace(f'href="{old}"', f'href="{new}"')
    html = _COUNTER.sub("", html)
    html = _MONTSERRAT.sub("", html)
    html = vendor_css(html)
    html = vendor_assets(html)
    html = strip_sections(html)
    html = legal_copy(html)
    html = name_pages(html, path)
    html = _BEACON.sub("", html)
    html = absolutize_loads(html)
    html = swap_photos(html, page_id(path))
    html = preload_hero(html, path)
    html = re.sub(r"<script>\n\(function \(\) \{\n  var ids = .*?</script>",
                  lambda m: photo_script(path, product_ids()).strip(), html, count=1, flags=re.S)
    html = re.sub(r'<style>\nli\[data-code="NEW"\].*?</style>', DEMO_FIX.strip(), html, count=1, flags=re.S)
    html = add_faq(html)
    return move_scripts(lazy_map(html))


def restamp():
    version = skin_version()
    pattern = re.compile(r"/skin/skin\.css\?v=[0-9a-f]+")
    count = 0
    for root, dirs, files in os.walk(APP):
        dirs[:] = [d for d in dirs if d not in (".git", "skin", "build", "assets") and not re.fullmatch(r"v\d+", d)]
        for name in files:
            if name != "index.html":
                continue
            full = os.path.join(root, name)
            html = io.open(full, encoding="utf-8").read()
            rel = os.path.relpath(root, APP).replace(os.sep, "/")
            fresh = refresh(pattern.sub(f"/skin/skin.css?v={version}", html), "/" if rel == "." else f"/{rel}/")
            fresh = re.sub(r'<script src="/skin/[a-z-]+\.js\?v=[0-9a-f]+"></script>\n?', "", fresh)
            fresh = fresh.replace("</body>", script_tags(version) + "</body>", 1)
            if fresh != html:
                io.open(full, "w", encoding="utf-8", newline="\n").write(fresh)
                count += 1
    print(f"version {version} stamped into {count} pages")


if __name__ == "__main__":
    if "--stamp" in sys.argv:
        restamp()
    else:
        main(["/" + arg.strip("/") + "/" for arg in sys.argv[1:] if not arg.startswith("-")])
