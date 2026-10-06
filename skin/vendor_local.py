import io
import os
import re
import subprocess
import sys
import urllib.error
import urllib.request

import vendor
from vendor import SITE, THEME_LOCAL, THEME_SCRIPT, local_path, vendored

CONTAINER = "mirslad-local-web-1"
WEB = "/var/www/html"
LOCAL = "http://127.0.0.1:8087"
ENV = {**os.environ, "MSYS_NO_PATHCONV": "1"}
CUSTOM_EVENT = "/bitrix/js/main/polyfill/customevent/main.polyfill.customevent.min.js"
ROOT_DIRS = ("/bitrix/images/main/smiles/2/",)
FALLBACK = ((re.compile(r"^/catalog/[a-z_]+/\d+/$"), "/catalog/torty/752/"),
            (re.compile(r"^/catalog/[a-z_]+/$"), "/catalog/torty/"),
            (re.compile(r"^/"), "/"))

_ANY = re.compile(re.escape(SITE) + r"(/(?:bitrix|upload|images|local)/[^\"'?#)\s,\\]+)(\?[^\"')\s,\\]*)?")
_BUNDLE = re.compile(r"(?:https?://[^/\"']+)?(/bitrix/cache/js/s1/aspro_max/([a-z_]+?)(?:_[0-9a-f]{32})?/[^\"'?/]+_v1\.js)")


def page_path(file):
    rel = os.path.relpath(os.path.dirname(file), vendor.APP).replace(os.sep, "/")
    return "/" if rel == "." else "/" + rel + "/"


def local_page(path):
    try:
        return urllib.request.urlopen(LOCAL + path, timeout=120).read().decode("utf-8", "replace")
    except urllib.error.HTTPError:
        return None


def bundles(html):
    found, seen = [], set()
    for m in _BUNDLE.finditer(html):
        if m.group(1) not in seen:
            seen.add(m.group(1))
            found.append((m.group(2), m.group(1)))
    return found


def by_kind(items):
    groups = {}
    for kind, path in items:
        groups.setdefault(kind, []).append(path)
    return groups


def container_file(path):
    out = subprocess.run(["docker", "exec", CONTAINER, "cat", WEB + path], capture_output=True, env=ENV)
    return None if out.returncode else out.stdout


def save(path, data):
    if path.endswith((".js", ".css", ".svg")):
        data = data.replace(b"\r\n", b"\n")
    target = local_path(path)
    os.makedirs(os.path.dirname(target), exist_ok=True)
    with open(target, "wb") as f:
        f.write(data)


def map_bundles(pages):
    plan, local_cache = {}, {}
    for file in pages:
        path = page_path(file)
        demo = bundles(open(file, encoding="utf-8", errors="ignore").read())
        if all(p in plan for _, p in demo):
            continue
        html = local_page(path)
        if html is None:
            fallback = next(f for rule, f in FALLBACK if rule.match(path))
            html = local_cache.get(fallback) or local_page(fallback)
            local_cache[fallback] = html
        local = by_kind(bundles(html))
        for kind, items in by_kind(demo).items():
            for i, live in enumerate(items):
                if live in plan or kind.startswith("kernel_"):
                    continue
                if i < len(local.get(kind, [])):
                    plan[live] = local[kind][i]
                else:
                    print(f"  no local {kind} for {path}")
    return plan


def vendor_bundles(pages):
    plan = map_bundles(pages)
    done = 0
    for live, local in plan.items():
        data = container_file(local)
        if data is None:
            print(f"  missing {local}")
            continue
        save(live, data)
        done += 1
    kernels = set()
    for file in pages:
        kernels.update(p for kind, p in bundles(open(file, encoding="utf-8", errors="ignore").read()) if kind.startswith("kernel_"))
    for live in sorted(kernels):
        data = container_file(CUSTOM_EVENT) if "polyfill_customevent" in live else container_file(live)
        if data is None:
            print(f"  missing kernel {live}")
            continue
        save(live, data)
        done += 1
    print(f"bundles: {done} of {len(plan) + len(kernels)}")


def vendor_files(pages):
    queue = []
    for file in pages:
        text = open(file, encoding="utf-8", errors="ignore").read()
        queue.extend(m.group(1) for m in _ANY.finditer(text) if not m.group(1).startswith("/bitrix/cache/"))
    for root, _, names in os.walk(os.path.join(vendor.VENDOR, "css")):
        for name in names:
            queue.extend(vendor._CSS_REF.findall(open(os.path.join(root, name), encoding="utf-8", errors="ignore").read()))
    seen, done, missing = set(), 0, []
    while queue:
        path = queue.pop(0)
        if path in seen:
            continue
        seen.add(path)
        if path == THEME_SCRIPT:
            data = urllib.request.urlopen(LOCAL + THEME_SCRIPT + "?site_id=s1&site_dir=/", timeout=60).read()
            save(THEME_LOCAL, data)
            done += 1
            continue
        if not vendored(path):
            data = container_file(path)
            if data is None:
                missing.append(path)
                continue
            save(path, data)
        done += 1
        if path.endswith(".css"):
            queue.extend(vendor.css_assets(path))
    print(f"files: {done} of {len(seen)}")
    for path in missing:
        print(f"  missing {path}")


def root_files():
    done = 0
    for folder in ROOT_DIRS:
        out = subprocess.run(["docker", "exec", CONTAINER, "ls", WEB + folder], capture_output=True, text=True, env=ENV)
        for name in out.stdout.split():
            data = container_file(folder + name)
            if data is None:
                continue
            target = os.path.join(vendor.APP, *(folder + name).strip("/").split("/"))
            os.makedirs(os.path.dirname(target), exist_ok=True)
            with open(target, "wb") as f:
                f.write(data)
            done += 1
    print(f"root files: {done}")


def localize(text):
    def swap(m):
        path = m.group(1)
        if not vendored(path):
            return m.group(0)
        return vendor.local_url(path) + ("" if path == THEME_SCRIPT else (m.group(2) or ""))
    return _ANY.sub(swap, text)


def rewrite(pages):
    changed = 0
    css = [os.path.join(r, n) for r, _, names in os.walk(os.path.join(vendor.VENDOR, "css")) for n in names]
    for file in pages + css:
        text = io.open(file, encoding="utf-8", newline="").read()
        fresh = localize(text)
        if fresh != text:
            io.open(file, "w", encoding="utf-8", newline="").write(fresh)
            changed += 1
    print(f"rewritten: {changed} files")


def main():
    pages = vendor.built_pages()
    vendor_bundles(pages)
    vendor_files(pages)
    root_files()
    rewrite(pages)


if __name__ == "__main__":
    main()
