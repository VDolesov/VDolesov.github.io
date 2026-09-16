import io
import os
import re
import shutil
import subprocess
import sys
import tarfile

HERE = os.path.dirname(os.path.abspath(__file__))
APP = os.path.dirname(HERE)
ORIGIN = "https://vdolesov.github.io"

_ATTR = re.compile(r'((?:href|src|action|content|poster|data-src|data-bg)=["\'])/(?!/)')
_URL = re.compile(r'(url\(["\']?)/(?!/)')
_ABS = re.compile(re.escape(ORIGIN) + r"/(?!v\d+/)")
_JS = re.compile(r'(["\'`])/(?!/)([a-z][a-z0-9_./-]*)(?=["\'`$])')


def rewrite(text, prefix):
    text = _ABS.sub(ORIGIN + prefix + "/", text)
    text = _ATTR.sub(lambda m: m.group(1) + prefix + "/", text)
    text = _URL.sub(lambda m: m.group(1) + prefix + "/", text)
    return text


def rewrite_js(text, prefix):
    text = _ABS.sub(ORIGIN + prefix + "/", text)
    return _JS.sub(lambda m: m.group(1) + prefix + "/" + m.group(2), text)


def main(commit, name):
    prefix = "/" + name
    target = os.path.join(APP, name)
    if os.path.exists(target):
        shutil.rmtree(target)
    os.makedirs(target)
    data = subprocess.run(["git", "archive", "--format=tar", commit], cwd=APP, capture_output=True, check=True).stdout
    with tarfile.open(fileobj=io.BytesIO(data)) as tar:
        members = [m for m in tar.getmembers() if not m.name.startswith((".git", "skin/", "build/"))
                   and m.name not in ("README.md", ".gitignore", ".nojekyll")]
        tar.extractall(target, members=members)
    count = 0
    for root, dirs, files in os.walk(target):
        for f in files:
            path = os.path.join(root, f)
            ext = f.rsplit(".", 1)[-1].lower()
            if ext not in ("html", "css", "js"):
                continue
            text = io.open(path, encoding="utf-8", errors="ignore").read()
            fresh = rewrite_js(text, prefix) if ext == "js" else rewrite(text, prefix)
            if fresh != text:
                io.open(path, "w", encoding="utf-8", newline="\n").write(fresh)
                count += 1
    print(f"{name}: {commit} -> {target}, rewritten {count} files")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
