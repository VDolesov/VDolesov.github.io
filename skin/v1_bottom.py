import io
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
V1 = os.path.join(os.path.dirname(HERE), "v1")
VERSION = "7"

STORES = [
    ("51.610035,46.000893", "ТЦ «Солнечный», г. Саратов, ул. Тархова 29А/1"),
    ("51.586484,45.968415", "Магазин-кулинария, г. Саратов, ул. Приовражная, б/н (кольцо НИИ)"),
    ("51.578719,45.962787", "Магазин-кулинария, г. Саратов, ул. Одесская 20А"),
    ("51.53252,46.030304", "Магазин-кулинария, г. Саратов, ул. Б. Казачья, 17/39 (угол ул. М. Горького)"),
    ("51.528604,46.024402", "Магазин-кулинария, г. Саратов, ул. Советская 30"),
    ("51.525202,46.04174", "Магазин-кулинария, г. Саратов, ул. Чернышевского 144"),
    ("51.525664,46.012283", "ТЦ «Арига», г. Саратов, ул. Бахметьевская 49"),
]
PHONE = ("+78452473569", "+7 (8452) 47-35-69")
DEMO_NOTE = "В демо-версии формы не отправляются — позвоните нам: +7 (8452) 47-35-69"


def store_items():
    out = []
    for i, (coords, title) in enumerate(STORES):
        active = " is-active" if i == 0 else ""
        out.append(
            f'        <div class="map-store{active}" data-coords="{coords}">\n'
            f'          <button class="map-store__title" type="button">{title}</button>\n'
            f'          <a class="map-store__phone" href="tel:{PHONE[0]}">{PHONE[1]}</a>\n'
            f'        </div>'
        )
    return "\n".join(out)


MAP_BLOCK = f'''
    <section class="map-block" id="stores" aria-labelledby="mapTitle">
      <div class="shell">
        <div class="map-block__head">
          <h2 id="mapTitle">Адреса магазинов</h2>
          <a class="map-block__more" href="/v1/contacts/">Перейти в раздел</a>
        </div>
        <div class="map-block__body">
          <div class="map-block__list" data-store-list>
{store_items()}
          </div>
          <div class="map-block__map" data-store-map aria-label="Карта магазинов"></div>
        </div>
      </div>
    </section>
'''

FOOTER = f'''<footer class="foot" id="footer">
    <div class="shell">
      <div class="foot__grid">
        <nav class="foot__col foot__col--main" aria-label="Основные разделы">
          <a href="/v1/catalog/">Каталог</a>
          <a href="/v1/#custom">Торты на заказ</a>
          <a href="/v1/#delivery">Доставка</a>
          <a href="/v1/contacts/">Контакты</a>
        </nav>
        <div class="foot__col">
          <h3>Компания</h3>
          <a href="/v1/about/">О компании</a>
          <a href="/v1/contacts/">Контакты</a>
          <a href="/v1/contacts/#storesTitle">Магазины</a>
          <a href="mailto:mirslad49@mail.ru">Написать нам</a>
        </div>
        <div class="foot__col">
          <h3>Информация</h3>
          <a href="/v1/#delivery">Условия доставки</a>
          <a href="/v1/#delivery">Условия оплаты</a>
          <a href="/v1/#delivery">Самовывоз</a>
          <a href="/v1/#faq">Перед заказом</a>
        </div>
        <div class="foot__col">
          <h3>Помощь</h3>
          <a href="/v1/#faq">Как оформить заказ</a>
          <a href="/v1/#custom">Торт на заказ</a>
          <button type="button" data-open-cart aria-controls="cartDrawer" aria-expanded="false">Корзина</button>
          <a href="/v1/#faq">Состав и аллергены</a>
        </div>
        <div class="foot__contact">
          <button class="foot__subscribe" type="button" data-demo-note="{DEMO_NOTE}">
            Подписаться на рассылку
            <svg viewBox="0 0 24 24" aria-hidden="true"><path d="M3 12 21 4l-4 16-6-5-8-3Zm8 3 6-9"/></svg>
          </button>
          <div class="foot__row foot__row--phone">
            <svg viewBox="0 0 24 24" aria-hidden="true"><path d="M7 3h3l1.5 5-2 1.5a15 15 0 0 0 5 5l1.5-2L21 14v3c0 2.2-1.8 4-4 4C9.3 21 3 14.7 3 7c0-2.2 1.8-4 4-4Z"/></svg>
            <div>
              <a href="tel:{PHONE[0]}">{PHONE[1]}</a>
              <button class="foot__callback" type="button" data-demo-note="{DEMO_NOTE}">заказать звонок</button>
            </div>
          </div>
          <div class="foot__row">
            <svg viewBox="0 0 24 24" aria-hidden="true"><path d="M3 6h18v12H3zM3 7l9 6 9-6"/></svg>
            <a href="mailto:mirslad49@mail.ru">mirslad49@mail.ru</a>
          </div>
          <div class="foot__row">
            <svg viewBox="0 0 24 24" aria-hidden="true"><path d="M12 21s-7-6.6-7-12a7 7 0 0 1 14 0c0 5.4-7 12-7 12Z"/><circle cx="12" cy="9" r="2.5"/></svg>
            <span>г. Саратов, ул. Бахметьевская 49</span>
          </div>
        </div>
      </div>
      <div class="foot__bottom">
        <span><span data-year></span> © Мир Сладостей</span>
        <div class="foot__pays" aria-label="Принимаем к оплате">
          <i class="pay pay--mc" title="MasterCard"></i>
          <span class="pay pay--visa" title="Visa">VISA</span>
          <span class="pay pay--mir" title="Мир">МИР</span>
        </div>
      </div>
    </div>
  </footer>'''

_FOOTER = re.compile(r"<footer class=\"(?:site-footer|foot)\".*?</footer>", re.S)


def patch(path, with_map):
    html = io.open(path, encoding="utf-8").read()
    original = html
    html = _FOOTER.sub(lambda m: FOOTER, html, count=1)
    if 'href="/v1/bottom.css' not in html:
        html = html.replace('<link rel="stylesheet" href="/v1/pages.css?v=9">',
                            '<link rel="stylesheet" href="/v1/pages.css?v=9">\n'
                            f'  <link rel="stylesheet" href="/v1/bottom.css?v={VERSION}">', 1)
        html = re.sub(r'(<script src="/v1/app\.js\?v=\d+" defer></script>)',
                      lambda m: m.group(1) + f'\n  <script src="/v1/bottom.js?v={VERSION}" defer></script>', html, count=1)
    html = re.sub(r"/v1/bottom\.(css|js)\?v=\d+", lambda m: f"/v1/bottom.{m.group(1)}?v={VERSION}", html)
    if with_map:
        html = re.sub(r'\n\s*<section class="map-block".*?</section>\n', "\n", html, count=1, flags=re.S)
        html = html.replace("  </main>", MAP_BLOCK + "  </main>", 1)
    if html != original:
        io.open(path, "w", encoding="utf-8", newline="\n").write(html)
        return True
    return False


def main():
    count = 0
    for root, _, files in os.walk(V1):
        for name in files:
            if name != "index.html":
                continue
            path = os.path.join(root, name)
            if patch(path, with_map=os.path.dirname(path) == V1):
                count += 1
    print(f"v1 pages patched: {count}")


if __name__ == "__main__":
    main()
