import os
import re
import subprocess
import sys
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
APP = os.path.dirname(HERE)
SITE = "https://www.mirsladostey164.ru"
VENDOR = os.path.join(APP, "vendor")
UA = {"User-Agent": "Mozilla/5.0"}
THEME_SCRIPT = "/bitrix/templates/aspro_max/js/setTheme.php"
THEME_LOCAL = "/bitrix/templates/aspro_max/js/settheme.js"

_PAGE_REF = re.compile(r'(?:src|href|data-src)="' + re.escape(SITE) + r'(/(?:bitrix|upload|images|local)/[^"?#]+)')
_ASSET = re.compile(r"((?:src|href|data-src)=\"|url\(\s*[\"']?)" + re.escape(SITE)
                    + r"(/(?:bitrix|upload|images|local)/[^\"'?#)\s]+)(\?[^\"')\s]*)?")
_CSS_REF = re.compile(r"url\(\s*['\"]?" + re.escape(SITE) + r"(/[^'\")?#]+)")


def local_path(path):
    return os.path.join(VENDOR, *path.lstrip("/").split("/"))


def local_url(path):
    return "/vendor" + (THEME_LOCAL if path == THEME_SCRIPT else path)


def built_pages():
    files = subprocess.run(["git", "ls-files", "*index.html"], cwd=APP, capture_output=True, text=True).stdout.split()
    return [os.path.join(APP, f) for f in files if not re.match(r"v\d+/", f)]


def references():
    paths = set()
    for page in built_pages():
        text = open(page, encoding="utf-8", errors="ignore").read()
        paths.update(_PAGE_REF.findall(text))
        paths.update(_CSS_REF.findall(text))
    for root, _, names in os.walk(os.path.join(VENDOR, "css")):
        for name in names:
            paths.update(_CSS_REF.findall(open(os.path.join(root, name), encoding="utf-8", errors="ignore").read()))
    return sorted(paths)


def fetch(path):
    target = local_path(THEME_LOCAL if path == THEME_SCRIPT else path)
    if os.path.exists(target):
        return True
    query = "?site_id=s1&site_dir=/" if path == THEME_SCRIPT else ""
    try:
        request = urllib.request.Request(SITE + path + query, headers=UA)
        data = urllib.request.urlopen(request, timeout=60).read()
    except Exception as exc:
        print(f"  {path}: {exc}")
        return False
    os.makedirs(os.path.dirname(target), exist_ok=True)
    with open(target, "wb") as f:
        f.write(data)
    return True


def vendored(path):
    return os.path.exists(local_path(THEME_LOCAL if path == THEME_SCRIPT else path))


def vendor_assets(html):
    return _ASSET.sub(lambda m: m.group(1) + local_url(m.group(2)) if vendored(m.group(2)) else m.group(0), html)


def relink_css():
    for root, _, names in os.walk(os.path.join(VENDOR, "css")):
        for name in names:
            full = os.path.join(root, name)
            css = open(full, encoding="utf-8", errors="ignore").read()
            fresh = _CSS_REF.sub(lambda m: m.group(0).replace(SITE + m.group(1), local_url(m.group(1)))
                                 if vendored(m.group(1)) else m.group(0), css)
            if fresh != css:
                with open(full, "w", encoding="utf-8", newline="\n") as f:
                    f.write(fresh)


_CSS_URL = re.compile(r"url\(\s*(['\"]?)(?!data:|https?:|//|#)([^'\")?#]+)([^'\")]*)\1\s*\)")


def css_assets(path):
    target = local_path(path)
    css = open(target, encoding="utf-8", errors="ignore").read()
    base = path.rsplit("/", 1)[0] + "/"
    found = []

    def link(m):
        ref = m.group(2).strip()
        if ref.startswith("/vendor/"):
            found.append(ref[len("/vendor"):])
            return m.group(0)
        absolute = ref if ref.startswith("/") else os.path.normpath(base + ref).replace(os.sep, "/")
        found.append(absolute)
        return f"url({m.group(1)}/vendor{absolute}{m.group(3)}{m.group(1)})" if ref.startswith("/") else m.group(0)

    fresh = _CSS_URL.sub(link, css)
    if fresh != css:
        with open(target, "w", encoding="utf-8", newline="\n") as f:
            f.write(fresh)
    return found


def main(paths=None):
    queue = list(paths or references())
    seen, done = set(), 0
    while queue:
        path = queue.pop(0)
        if path in seen:
            continue
        seen.add(path)
        if fetch(path):
            done += 1
            if path.endswith(".css"):
                queue.extend(css_assets(path))
    relink_css()
    print(f"vendored {done} of {len(seen)} files")


if __name__ == "__main__":
    main(sys.argv[1:])
