(function () {
  "use strict";

  var KEY = "ms_cart";
  var ORDER_KEY = "ms_orders";
  var PRODUCTS = window.MS_PRODUCTS || {};
  var PHOTOS = window.MS_PHOTOS || [];
  var ORIGIN = window.MS_ORIGIN || "";
  var SHOP_MAIL = "mirslad49@mail.ru";
  var SHOP_PHONE = "+7 (8452) 47-35-69";
  var FREE_DELIVERY = 3000;
  var DELIVERY_FEE = 150;
  var MIN_ORDER = 800;

  function load() {
    var raw = {};
    try { raw = JSON.parse(localStorage.getItem(KEY) || "{}") || {}; } catch (e) { return {}; }
    var cart = {}, dropped = false;
    Object.keys(raw).forEach(function (id) {
      var qty = parseInt(raw[id], 10);
      if (PRODUCTS[id] && qty > 0) cart[id] = qty; else dropped = true;
    });
    if (dropped) { try { localStorage.setItem(KEY, JSON.stringify(cart)); } catch (e) {} }
    return cart;
  }
  function save(cart) {
    try { localStorage.setItem(KEY, JSON.stringify(cart)); } catch (e) {}
    badge();
  }
  function count(cart) {
    var n = 0; for (var id in cart) n += cart[id];
    return n;
  }
  function total(cart) {
    var s = 0;
    for (var id in cart) s += (PRODUCTS[id] ? PRODUCTS[id].price : 0) * cart[id];
    return s;
  }
  function money(n) {
    return String(Math.round(n)).replace(/\B(?=(\d{3})+(?!\d))/g, " ") + " ₽";
  }
  function plural(n, one, few, many) {
    var m = n % 100;
    if (m >= 11 && m <= 19) return many;
    m = n % 10;
    if (m === 1) return one;
    if (m >= 2 && m <= 4) return few;
    return many;
  }
  function photo(id) {
    return PHOTOS.indexOf(id) !== -1
      ? ORIGIN + "/assets/products/" + id + "-" + (window.MS_SERIES || "v9") + "-640.webp"
      : (PRODUCTS[id] && PRODUCTS[id].image) || "";
  }

  function badge() {
    var n = count(load());
    var nodes = document.querySelectorAll(".basket_count, .wrap_basket .count, .header-cart .count, .fixed-basket .count");
    for (var i = 0; i < nodes.length; i++) {
      var el = nodes[i];

      var target = el.querySelector(".items span, .items, .count span:last-child, .count") || el;
      while (target.children.length === 1) target = target.children[0];
      if (target.children.length === 0) target.textContent = String(n);
      el.classList.toggle("empty", n === 0);
      el.classList.toggle("ms-has-items", n > 0);
      var countBox = el.querySelector(".count");
      if (countBox) countBox.classList.toggle("empty_items", n === 0);
      if (el.getAttribute("title")) el.setAttribute("title", n ? "В корзине: " + n : "Корзина пуста");
    }
    var links = document.querySelectorAll("a.basket-link.basket, a.basket-link.in-cart");
    for (var k = 0; k < links.length; k++) {
      links[k].setAttribute("title", n ? "В корзине: " + n : "Корзина пуста");
    }
  }

  function productIdFrom(el) {
    var holder = el.closest("[data-item]");
    if (holder && holder.getAttribute("data-item")) return holder.getAttribute("data-item");
    var card = el.closest(".catalog_item, .item_block, .product-container, .detail, .basket_fly, .fixed-basket");
    var link = card && card.querySelector('a[href*="/catalog/"]');
    var m = link && link.getAttribute("href").match(/\/catalog\/[a-z_]+\/(\d+)\//);
    return m ? m[1] : null;
  }
  function quantityFor(el, id) {
    var scope = el.closest(".footer_button, .buy_block, .counter_wrapp, .product-container, .detail, .catalog_item, .item_block") || document;
    var input = scope.querySelector('.counter_block[data-item="' + id + '"] input, .counter_block input');
    var q = input ? parseInt(input.value, 10) : parseInt(el.getAttribute("data-quantity") || "1", 10);
    return q > 0 ? q : 1;
  }
  function markInCart(id) {
    var buttons = document.querySelectorAll('.to-cart[data-item="' + id + '"]');
    for (var i = 0; i < buttons.length; i++) {
      var btn = buttons[i];
      var twin = btn.parentElement && btn.parentElement.querySelector('.in-cart[data-item="' + id + '"]');
      if (twin) { btn.style.display = "none"; twin.style.display = ""; }
      else { btn.classList.add("ms-added"); var s = btn.querySelector("span"); if (s) s.textContent = "В корзине"; }
    }
  }
  function toast(id, qty) {
    var p = PRODUCTS[id] || { name: "Товар" };
    var old = document.querySelector(".ms-toast");
    if (old) old.parentNode.removeChild(old);
    var box = document.createElement("div");
    box.className = "ms-toast";
    box.innerHTML = '<div class="ms-toast__text"><b>' + esc(p.name) + '</b> — в корзине' +
      (qty > 1 ? ", " + qty + " шт." : "") + '</div>' +
      '<a class="ms-toast__link" href="/basket/">Перейти в корзину</a>';
    document.body.appendChild(box);
    setTimeout(function () { box.classList.add("is-on"); }, 20);
    setTimeout(function () { box.classList.remove("is-on"); }, 4200);
    setTimeout(function () { if (box.parentNode) box.parentNode.removeChild(box); }, 4800);
  }
  function add(id, qty) {
    if (!PRODUCTS[id]) return false;
    var cart = load();
    cart[id] = (cart[id] || 0) + qty;
    save(cart);
    markInCart(id);
    return true;
  }

  function unmarkInCart(id) {
    var buttons = document.querySelectorAll('.to-cart[data-item="' + id + '"]');
    for (var i = 0; i < buttons.length; i++) {
      var btn = buttons[i];
      var twin = btn.parentElement && btn.parentElement.querySelector('.in-cart[data-item="' + id + '"]');
      if (twin) { btn.style.display = ""; twin.style.display = "none"; }
      else { btn.classList.remove("ms-added"); var s = btn.querySelector("span"); if (s) s.textContent = "В корзину"; }
    }
  }

  function onBasketPage() {
    return /^\/basket\/?$/.test(location.pathname);
  }
  function sectionName(slug) {
    var list = window.MS_SECTIONS || [];
    for (var i = 0; i < list.length; i++) if (list[i].slug === slug) return list[i].name;
    return "";
  }

  var drawer = null, lastFocus = null, closing = null;

  function drawerRow(id, qty) {
    var p = PRODUCTS[id], img = photo(id);
    var meta = [sectionName(p.section), money(p.price) + " / " + esc(p.unit || "шт")].filter(Boolean).join(" · ");
    return '<div class="ms-drawer__item" data-id="' + id + '">' +
      '<a class="ms-drawer__pic" href="' + esc(p.url) + '">' + (img ? '<img src="' + esc(img) + '" alt="" loading="lazy">' : "") + '</a>' +
      '<div class="ms-drawer__body">' +
        '<a class="ms-drawer__name" href="' + esc(p.url) + '">' + esc(p.name) + '</a>' +
        '<div class="ms-drawer__meta">' + meta + '</div>' +
      '</div>' +
      '<button type="button" class="ms-drawer__remove" data-dact="remove" aria-label="Убрать">&times;</button>' +
      '<div class="ms-drawer__row">' +
        '<div class="ms-drawer__qty">' +
          '<button type="button" data-dact="minus" aria-label="Меньше">&minus;</button>' +
          '<span>' + qty + '</span>' +
          '<button type="button" data-dact="plus" aria-label="Больше">+</button>' +
        '</div>' +
        '<div class="ms-drawer__sum">' + money(p.price * qty) + '</div>' +
      '</div>' +
    '</div>';
  }

  function renderDrawer() {
    var content = drawer.querySelector(".ms-drawer__content");
    var cart = load(), ids = Object.keys(cart);
    if (!ids.length) {
      content.innerHTML = '<div class="ms-drawer__empty">' +
        '<p>В корзине пока пусто. Загляните в каталог — торты, пироги и выпечка ждут.</p>' +
        '<a class="btn btn-default btn-lg ms-drawer__go" href="/catalog/">Перейти в каталог</a></div>';
      return;
    }
    var sum = total(cart);
    var scroll = content.querySelector(".ms-drawer__list");
    var top = scroll ? scroll.scrollTop : 0;
    content.innerHTML = shipBlock(sum) +
      '<div class="ms-drawer__list">' + ids.map(function (id) { return drawerRow(id, cart[id]); }).join("") + '</div>' +
      '<div class="ms-drawer__foot">' +
        '<div class="ms-drawer__total"><span>Товары</span><b>' + money(sum) + '</b></div>' +
        '<div class="ms-drawer__note">' + (sum >= FREE_DELIVERY
          ? "Доставка по Саратову: бесплатно · самовывоз бесплатно"
          : "Доставка по Саратову: до " + money(DELIVERY_FEE) + ", в радиусе 3 км от центра — бесплатно · самовывоз бесплатно") + '</div>' +
        checkoutButton(sum, "ms-drawer__go", "/basket/#order", "Перейти к оформлению") +
        '<div class="ms-drawer__fine">Наличие, итоговую стоимость и время подтверждает менеджер.</div>' +
      '</div>';
    var list = content.querySelector(".ms-drawer__list");
    if (list) list.scrollTop = top;
  }

  function buildDrawer() {
    drawer = document.createElement("div");
    drawer.className = "ms-drawer";
    drawer.hidden = true;
    drawer.innerHTML = '<div class="ms-drawer__shade" data-dclose></div>' +
      '<aside class="ms-drawer__panel" role="dialog" aria-modal="true" aria-labelledby="ms-drawer-title" tabindex="-1">' +
        '<div class="ms-drawer__head">' +
          '<div><div class="ms-drawer__eyebrow">Ваш заказ</div><div class="ms-drawer__title" id="ms-drawer-title">Корзина</div></div>' +
          '<button type="button" class="ms-drawer__close" data-dclose aria-label="Закрыть корзину">&times;</button>' +
        '</div>' +
        '<div class="ms-drawer__content"></div>' +
      '</aside>';
    document.body.appendChild(drawer);
    drawer.addEventListener("click", function (e) {
      if (e.target.closest("[data-dclose]")) { closeDrawer(); return; }
      var b = e.target.closest("[data-dact]");
      if (!b) return;
      var id = b.closest(".ms-drawer__item").getAttribute("data-id");
      var c = load(), act = b.getAttribute("data-dact");
      if (act === "plus") c[id] += 1;
      if (act === "minus") c[id] = Math.max(1, c[id] - 1);
      if (act === "remove") { delete c[id]; unmarkInCart(id); }
      save(c);
      renderDrawer();
    });
    document.addEventListener("keydown", function (e) {
      if (e.key === "Escape" && drawer && !drawer.hidden) closeDrawer();
    });
  }

  function openDrawer() {
    if (!drawer) buildDrawer();
    clearTimeout(closing);
    renderDrawer();
    lastFocus = document.activeElement;
    drawer.hidden = false;
    document.documentElement.classList.add("ms-lock");
    requestAnimationFrame(function () {
      requestAnimationFrame(function () { drawer.classList.add("is-open"); });
    });
    var close = drawer.querySelector(".ms-drawer__close");
    if (close) close.focus({ preventScroll: true });
  }

  function closeDrawer() {
    if (!drawer || drawer.hidden) return;
    drawer.classList.remove("is-open");
    document.documentElement.classList.remove("ms-lock");
    closing = setTimeout(function () { drawer.hidden = true; }, 380);
    if (lastFocus && lastFocus.focus) lastFocus.focus({ preventScroll: true });
  }

  function goCart() {
    if (onBasketPage()) {
      var root = document.querySelector(".ms-basket-root");
      if (root) window.scrollTo({ top: root.getBoundingClientRect().top + window.scrollY - 120, behavior: "smooth" });
      return;
    }
    openDrawer();
  }

  function isCartLink(a) {
    if (!a || !a.getAttribute) return false;
    var href = a.getAttribute("href") || "";
    return /^(https?:\/\/[^/]+)?\/basket\/?$/.test(href);
  }

  document.addEventListener("click", function (e) {
    var side = e.target.closest ? e.target.closest(".basket_wrapp") : null;
    if (side) {
      e.preventDefault(); e.stopImmediatePropagation();
      goCart();
      return;
    }
    var link = e.target.closest ? e.target.closest("a") : null;
    if (isCartLink(link) && !e.target.closest(".ms-drawer")) {
      e.preventDefault(); e.stopImmediatePropagation();
      goCart();
      return;
    }
    var t = e.target.closest ? e.target.closest(".to-cart, .in-cart, .one_click, .basket_fly .basket-link, .basket-link") : null;
    if (!t) return;

    if (t.classList.contains("to-cart")) {
      e.preventDefault(); e.stopImmediatePropagation();
      var id = productIdFrom(t);
      if (!id) return;
      var qty = quantityFor(t, id);
      if (add(id, qty)) toast(id, qty);
      return;
    }
    if (t.classList.contains("one_click")) {
      e.preventDefault(); e.stopImmediatePropagation();
      var oid = productIdFrom(t);
      if (oid) { add(oid, quantityFor(t, oid)); location.href = "/basket/#order"; }
      return;
    }
    if (t.classList.contains("in-cart") || t.classList.contains("basket-link")) {
      e.preventDefault(); e.stopImmediatePropagation();
      goCart();
    }
  }, true);

  function esc(s) {
    return String(s).replace(/[&<>"]/g, function (c) {
      return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c];
    });
  }

  function itemRow(id, qty) {
    var p = PRODUCTS[id];
    var img = photo(id);
    return '<div class="ms-item" data-id="' + id + '">' +
      '<a class="ms-item__pic" href="' + esc(p.url) + '">' + (img ? '<img src="' + esc(img) + '" alt="">' : "") + '</a>' +
      '<div class="ms-item__body">' +
        '<a class="ms-item__name" href="' + esc(p.url) + '">' + esc(p.name) + '</a>' +
        '<div class="ms-item__meta">' + (p.weight ? esc(p.weight) + ' · ' : '') + money(p.price) + ' / ' + esc(p.unit || "шт") + '</div>' +
      '</div>' +
      '<div class="ms-qty">' +
        '<button type="button" class="ms-qty__btn" data-act="minus" aria-label="Меньше">&minus;</button>' +
        '<input class="ms-qty__input" type="text" inputmode="numeric" value="' + qty + '">' +
        '<button type="button" class="ms-qty__btn" data-act="plus" aria-label="Больше">+</button>' +
      '</div>' +
      '<div class="ms-item__sum">' + money(p.price * qty) + '</div>' +
      '<button type="button" class="ms-item__remove" data-act="remove" aria-label="Убрать">&times;</button>' +
    '</div>';
  }

  function shippingText(sum, mode) {
    if (mode !== "delivery") return "самовывоз, бесплатно";
    return sum >= FREE_DELIVERY ? "бесплатно" : "до " + money(DELIVERY_FEE);
  }
  function totalLabel(sum, mode) {
    return mode === "delivery" && sum < FREE_DELIVERY ? "Итого без доставки" : "Итого";
  }
  function belowMinimum(sum) {
    return sum < MIN_ORDER;
  }
  function checkoutButton(sum, cls, href, label) {
    if (belowMinimum(sum)) {
      return '<span class="btn btn-default btn-lg ' + cls + ' is-disabled" aria-disabled="true">Минимальный заказ — ' + money(MIN_ORDER) + '</span>';
    }
    return '<a class="btn btn-default btn-lg ' + cls + '" href="' + href + '">' + label + '</a>';
  }

  function shipBlock(sum) {
    if (belowMinimum(sum)) {
      return '<div class="ms-ship">' +
        '<div class="ms-ship__head"><span>До минимальной суммы заказа</span><b>' + money(MIN_ORDER - sum) + '</b></div>' +
        '<div class="ms-ship__bar"><i style="width:' + Math.min(100, sum / MIN_ORDER * 100).toFixed(1) + '%"></i></div>' +
        '<div class="ms-ship__hint">Минимальная сумма заказа — ' + money(MIN_ORDER) + '.</div>' +
      '</div>';
    }
    var left = Math.max(0, FREE_DELIVERY - sum);
    var pct = Math.min(100, sum / FREE_DELIVERY * 100);
    return '<div class="ms-ship' + (left ? "" : " is-free") + '">' +
      '<div class="ms-ship__head"><span>' + (left ? "До бесплатной доставки" : "Доставка по Саратову — бесплатно") + '</span>' +
        (left ? '<b>' + money(left) + '</b>' : "") + '</div>' +
      '<div class="ms-ship__bar"><i style="width:' + pct.toFixed(1) + '%"></i></div>' +
      '<div class="ms-ship__hint">' + (left
        ? "Доставляем только по Саратову: в радиусе 3 км от центра и при заказе от " + money(FREE_DELIVERY) +
          " — бесплатно, дальше по городу — " + money(DELIVERY_FEE) + "."
        : "Доставляем только по Саратову.") + '</div>' +
    '</div>';
  }

  function summaryRows(cart, mode) {
    var n = count(cart), sum = total(cart);
    return '<div class="ms-summary__row"><span>' + n + ' ' + plural(n, "товар", "товара", "товаров") + '</span><span>' + money(sum) + '</span></div>' +
      '<div class="ms-summary__row"><span>Доставка</span><span>' + shippingText(sum, mode) + '</span></div>' +
      '<div class="ms-summary__row ms-summary__row--total"><span>' + totalLabel(sum, mode) + '</span><span>' + money(sum) + '</span></div>';
  }

  function orderText(order) {
    var lines = ["Заказ " + order.number + " — Мир Сладостей", ""];
    order.items.forEach(function (it) {
      lines.push(it.name + " × " + it.qty + " — " + money(it.price * it.qty).replace(/ /g, " "));
    });
    if (order.delivery === "delivery") lines.push("", "Доставка: " + order.shipping.replace(/ /g, " "));
    lines.push("", totalLabel(order.total, order.delivery) + ": " + money(order.total).replace(/ /g, " "));
    lines.push("", "Имя: " + order.name, "Телефон: " + order.phone,
      "Получение: " + (order.delivery === "delivery" ? "доставка, " + order.address : "самовывоз"));
    if (order.date) lines.push("Когда: " + order.date);
    if (order.comment) lines.push("Комментарий: " + order.comment);
    return lines.join("\n");
  }

  function renderCart(root) {
    var cart = load();
    var ids = Object.keys(cart);
    var picked = root.querySelector('input[name="delivery"]:checked');
    var mode = picked ? picked.value : "pickup";
    var kept = {};
    root.querySelectorAll(".ms-form input[type=text], .ms-form input[type=tel]").forEach(function (el) { kept[el.name] = el.value; });

    if (!ids.length) {
      root.innerHTML = '<div class="ms-empty">' +
        '<div class="ms-empty__title">В корзине пока пусто</div>' +
        '<p class="ms-empty__text">Загляните в каталог — торты, пироги и выпечка ждут.</p>' +
        '<a class="btn btn-default btn-lg" href="/catalog/">Перейти в каталог</a></div>';
      return;
    }

    var html = '<div class="ms-cart">' +
      '<div class="ms-cart__list">' + ids.map(function (id) { return itemRow(id, cart[id]); }).join("") + '</div>' +
      '<aside class="ms-summary">' +
        shipBlock(total(cart)) +
        '<div class="ms-summary__rows">' + summaryRows(cart, mode) + '</div>' +
        checkoutButton(total(cart), "ms-summary__btn", "#order", "Оформить заказ") +
        '<div class="ms-summary__note">Самовывоз из магазина — бесплатно, в день заказа.<br>Доставка — только по Саратову, на следующий день.</div>' +
      '</aside>' +
    '</div>' +
    '<section class="ms-order" id="order">' +
      '<div class="ms-order__label">Оформление</div>' +
      '<h2 class="ms-order__title">Куда и когда привезти</h2>' +
      '<form class="ms-form" novalidate>' +
        '<label class="ms-field"><span>Ваше имя</span><input name="name" type="text" required autocomplete="name"></label>' +
        '<label class="ms-field"><span>Телефон</span><input name="phone" type="tel" required autocomplete="tel" placeholder="+7 (___) ___-__-__"></label>' +
        '<div class="ms-field ms-field--wide"><span>Получение</span>' +
          '<div class="ms-choice">' +
            '<label><input type="radio" name="delivery" value="pickup"' + (mode === "pickup" ? " checked" : "") + '><b>Самовывоз</b><small>ул. Бахметьевская, 49 · сегодня</small></label>' +
            '<label><input type="radio" name="delivery" value="delivery"' + (mode === "delivery" ? " checked" : "") + '><b>Доставка</b><small>только по Саратову · завтра</small></label>' +
          '</div></div>' +
        '<label class="ms-field ms-field--wide ms-field--address"' + (mode === "delivery" ? "" : " hidden") + '><span>Адрес доставки в Саратове</span><input name="address" type="text" autocomplete="street-address" placeholder="улица, дом, квартира"></label>' +
        '<label class="ms-field"><span>Желаемая дата и время</span><input name="date" type="text" placeholder="например, суббота к 12:00"></label>' +
        '<label class="ms-field"><span>Комментарий</span><input name="comment" type="text" placeholder="надпись на торте, свечи, аллергии"></label>' +
        '<div class="ms-form__foot">' +
          '<button type="submit" class="btn btn-default btn-lg">Подтвердить заказ</button>' +
          '<div class="ms-form__hint">Менеджер перезвонит, чтобы подтвердить состав, время и стоимость доставки.</div>' +
        '</div>' +
        '<div class="ms-form__legal">Нажимая «Подтвердить заказ», вы соглашаетесь с ' +
          '<a href="/company/agreement/" target="_blank">политикой обработки персональных данных</a>. ' +
          'Имя, телефон и адрес нужны только для выполнения заказа.</div>' +
        '<div class="ms-form__error" hidden></div>' +
      '</form>' +
    '</section>';
    root.innerHTML = html;
    Object.keys(kept).forEach(function (name) {
      var el = root.querySelector('.ms-form [name="' + name + '"]');
      if (el) el.value = kept[name];
    });

    if (location.hash === "#order") {
      setTimeout(function () {
        var o = document.getElementById("order");
        if (o) window.scrollTo({ top: o.getBoundingClientRect().top + window.scrollY - 110, behavior: "smooth" });
      }, 120);
    }
  }

  function bindCart(root) {
    root.addEventListener("click", function (e) {
      var b = e.target.closest("[data-act]");
      if (!b) return;
      var row = b.closest(".ms-item"), id = row.getAttribute("data-id");
      var c = load();
      if (b.getAttribute("data-act") === "plus") c[id] += 1;
      if (b.getAttribute("data-act") === "minus") c[id] = Math.max(1, c[id] - 1);
      if (b.getAttribute("data-act") === "remove") delete c[id];
      save(c); renderCart(root);
    });
    root.addEventListener("change", function (e) {
      if (e.target.classList.contains("ms-qty__input")) {
        var row = e.target.closest(".ms-item"), id = row.getAttribute("data-id");
        var c = load(), v = parseInt(e.target.value, 10);
        c[id] = v > 0 ? v : 1; save(c); renderCart(root);
      }
      if (e.target.name === "delivery") {
        root.querySelector(".ms-field--address").hidden = e.target.value !== "delivery";
        var rows = root.querySelector(".ms-summary__rows");
        if (rows) rows.innerHTML = summaryRows(load(), e.target.value);
      }
    });
    root.addEventListener("submit", function (e) {
      var form = e.target;
      if (!form.classList.contains("ms-form")) return;
      e.preventDefault();
      var f = form.elements, err = form.querySelector(".ms-form__error");
      var phone = f.phone.value.replace(/\D/g, "");
      var problems = [];
      if (!f.name.value.trim()) problems.push("имя");
      if (phone.length < 10) problems.push("телефон");
      if (f.delivery.value === "delivery" && !f.address.value.trim()) problems.push("адрес доставки");
      var c = load(), sum = total(c);
      if (belowMinimum(sum)) {
        err.hidden = false;
        err.textContent = "Минимальная сумма заказа — " + money(MIN_ORDER) + ": добавьте ещё " + money(MIN_ORDER - sum) + ".";
        return;
      }
      if (problems.length) {
        err.hidden = false; err.textContent = "Заполните: " + problems.join(", ") + ".";
        return;
      }
      var order = {
        number: nextNumber(),
        date: f.date.value.trim(), comment: f.comment.value.trim(),
        name: f.name.value.trim(), phone: f.phone.value.trim(),
        delivery: f.delivery.value, address: f.address.value.trim(),
        items: Object.keys(c).map(function (id) {
          return { id: id, name: PRODUCTS[id].name, price: PRODUCTS[id].price, qty: c[id] };
        }),
        shipping: shippingText(sum, f.delivery.value), total: sum, created: new Date().toISOString()
      };
      try {
        var orders = JSON.parse(localStorage.getItem(ORDER_KEY) || "[]");
        orders.push(order); localStorage.setItem(ORDER_KEY, JSON.stringify(orders));
      } catch (x) {}
      save({});
      renderDone(root, order);
      window.scrollTo({ top: root.getBoundingClientRect().top + window.scrollY - 120, behavior: "smooth" });
    });
  }

  function nextNumber() {
    var d = new Date(), seq = 1;
    try {
      seq = (JSON.parse(localStorage.getItem(ORDER_KEY) || "[]").length || 0) + 1;
    } catch (e) {}
    return "MS-" + String(d.getFullYear()).slice(2) + ("0" + (d.getMonth() + 1)).slice(-2) +
      ("0" + d.getDate()).slice(-2) + "-" + ("00" + seq).slice(-3);
  }

  function renderDone(root, order) {
    var text = orderText(order);
    var mail = "mailto:" + SHOP_MAIL + "?subject=" + encodeURIComponent("Заказ " + order.number) +
      "&body=" + encodeURIComponent(text);
    root.innerHTML = '<div class="ms-done">' +
      '<div class="ms-done__label">Заказ принят</div>' +
      '<h2 class="ms-done__title">' + esc(order.number) + '</h2>' +
      '<p class="ms-done__text">Спасибо, ' + esc(order.name) + '. Менеджер перезвонит на ' + esc(order.phone) +
        ', подтвердит состав и ' + (order.delivery === "delivery" ? "время доставки" : "время, когда всё будет готово") + '.</p>' +
      '<div class="ms-done__list">' + order.items.map(function (it) {
        return '<div class="ms-done__row"><span>' + esc(it.name) + ' × ' + it.qty + '</span><span>' + money(it.price * it.qty) + '</span></div>';
      }).join("") +
      (order.delivery === "delivery" ? '<div class="ms-done__row"><span>Доставка по Саратову</span><span>' + order.shipping + '</span></div>' : "") +
      '<div class="ms-done__row ms-done__row--total"><span>' + totalLabel(order.total, order.delivery) + '</span><span>' + money(order.total) + '</span></div></div>' +
      '<div class="ms-done__actions">' +
        '<a class="btn btn-default btn-lg" href="' + mail + '">Отправить заказ на почту</a>' +
        '<button type="button" class="btn btn-transparent btn-lg" data-copy>Скопировать заказ</button>' +
        '<a class="ms-done__phone" href="tel:' + SHOP_PHONE.replace(/[^\d+]/g, "") + '">' + SHOP_PHONE + '</a>' +
      '</div>' +
      '<p class="ms-done__note">Сайт собран для демонстрации: заказ сохранён в вашем браузере и не ушёл на сервер. На рабочем сайте эту форму обслуживает штатный модуль заказов.</p>' +
      '<a class="ms-done__back" href="/catalog/">Вернуться в каталог</a>' +
    '</div>';
    var copy = root.querySelector("[data-copy]");
    copy.addEventListener("click", function () {
      var ok = function () { copy.textContent = "Скопировано"; };
      if (navigator.clipboard) navigator.clipboard.writeText(text).then(ok, ok);
      else ok();
    });
  }

  function mountCart() {
    if (!/^\/basket\/?$/.test(location.pathname)) return;

    var container = document.querySelector(".wrapper_inner .container_inner .middle > .container")
      || document.querySelector(".wrapper_inner .container_inner .middle")
      || document.querySelector(".wrapper_inner");
    if (!container) return;
    var root = document.createElement("div");
    root.className = "ms-basket-root";
    container.innerHTML = '<div class="maxwidth-theme"></div>';
    var wrap = container.firstChild;
    wrap.appendChild(root);
    bindCart(root);
    renderCart(root);
  }

  function ready(fn) {
    if (document.readyState !== "loading") fn(); else document.addEventListener("DOMContentLoaded", fn);
  }
  ready(function () {
    badge();
    var cart = load();
    for (var id in cart) markInCart(id);
    mountCart();
  });
})();
