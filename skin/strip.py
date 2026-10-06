import re

_TAG = {tag: re.compile(r"<(/?)%s\b[^>]*>" % tag) for tag in ("div", "li")}
_ANCHOR = re.compile(r"<a\b")
_SVG = re.compile(r"<svg\b.*?</svg>", re.S)


def block_end(html, start, tag):
    depth = 0
    for m in _TAG[tag].finditer(html, start):
        depth += -1 if m.group(1) else 1
        if depth == 0:
            return m.end()
    return -1


_ANY = re.compile(r"<(/?)(div|li)\b[^>]*>")


def enclosing(html, pos):
    stack = []
    for m in _ANY.finditer(html, 0, pos):
        tag = m.group(2)
        if not m.group(1):
            stack.append((tag, m.start()))
            continue
        while stack:
            if stack.pop()[0] == tag:
                break
    for tag, start in reversed(stack):
        yield start, block_end(html, start, tag)


def drop_link_blocks(html, href):
    pattern = re.compile(r'<a\b[^>]*href="' + re.escape(href) + r'"')
    while True:
        m = pattern.search(html)
        if not m:
            return html
        start, end = m.start(), html.find("</a>", m.start()) + 4
        for b_start, b_end in enclosing(html, m.start()):
            if len(_ANCHOR.findall(_SVG.sub("", html[b_start:b_end]))) != 1:
                break
            start, end = b_start, b_end
        html = html[:start] + html[end:]


def drop_column(html, marker, prefix='<div class="col-'):
    while True:
        pos = html.find(marker)
        if pos == -1:
            return html
        start = html.rfind(prefix, 0, pos)
        end = block_end(html, start, "div") if start != -1 else -1
        if end < pos:
            return html
        html = html[:start] + html[end:]


def drop_class_blocks(html, cls, exact=True):
    pattern = re.compile(r'<div class="' + re.escape(cls) + ('"' if exact else '[^"]*"') + r'[^>]*>')
    while True:
        m = pattern.search(html)
        if not m:
            return html
        html = html[:m.start()] + html[block_end(html, m.start(), "div"):]


def widen_footer(html):
    start, end = html.find("<footer"), html.find("</footer>")
    if start == -1 or end == -1:
        return html
    footer = html[start:end].replace('class="col-md-2 col-sm-3"', 'class="col-md-3 col-sm-3"')
    return html[:start] + footer + html[end:]


def strip_sections(html):
    html = drop_link_blocks(html, "/help/warranty/")
    html = drop_link_blocks(html, "/company/licenses/")
    html = drop_link_blocks(html, "/info/brands/")
    html = widen_footer(drop_column(html, 'data-parent="#bottom_help"'))
    html = drop_link_blocks(html, "/basket/#delayed")
    html = drop_class_blocks(html, "wish_item_button")
    html = drop_class_blocks(html, "drag-block container TIZERS", exact=False)
    html = drop_class_blocks(html, "drag-block container COMPANY_TEXT", exact=False)
    return html
