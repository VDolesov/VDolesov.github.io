(function () {
  "use strict";

  var KEY = "ms_cart";
  var SEQ_KEY = "ms_cart_seq";
  var ORDER_KEY = "ms_orders";
  var PRODUCTS = window.MS_PRODUCTS || {};
  var PHOTOS = window.MS_PHOTOS || [];
  var ORIGIN = window.MS_ORIGIN || "";
  var SHOP_MAIL = "mirslad49@mail.ru";
  var SHOP_PHONE = "+7 (8452) 47-35-69";
  var FREE_DELIVERY = 3000;
  var DELIVERY_FEE = 150;
  var MIN_ORDER = 800;
  var ICON = {"close": "<svg xmlns=\"http://www.w3.org/2000/svg\" width=\"16\" height=\"16\" viewBox=\"0 0 16 16\"><path data-name=\"Rounded Rectangle 114 copy 3\" class=\"cccls-1\" d=\"M334.411,138l6.3,6.3a1,1,0,0,1,0,1.414,0.992,0.992,0,0,1-1.408,0l-6.3-6.306-6.3,6.306a1,1,0,0,1-1.409-1.414l6.3-6.3-6.293-6.3a1,1,0,0,1,1.409-1.414l6.3,6.3,6.3-6.3A1,1,0,0,1,340.7,131.7Z\" transform=\"translate(-325 -130)\"></path></svg>", "remove": "<svg xmlns=\"http://www.w3.org/2000/svg\" width=\"8.031\" height=\"8\" viewBox=\"0 0 8.031 8\"><path data-name=\"Rounded Rectangle 893 copy\" class=\"cls-1\" d=\"M756.41,668.967l2.313,2.315a1,1,0,0,1-1.415,1.409L755,670.379l-2.309,2.312a1,1,0,0,1-1.414-1.409l2.312-2.315-2.281-2.284a1,1,0,1,1,1.414-1.409L755,667.555l2.277-2.281a1,1,0,1,1,1.414,1.409Z\" transform=\"translate(-751 -665)\"></path></svg>", "closes": "<svg xmlns=\"http://www.w3.org/2000/svg\" width=\"8.031\" height=\"8\" viewBox=\"0 0 8.031 8\"><path data-name=\"Rounded Rectangle 893 copy\" class=\"cls-1\" d=\"M756.41,668.967l2.313,2.315a1,1,0,0,1-1.415,1.409L755,670.379l-2.309,2.312a1,1,0,0,1-1.414-1.409l2.312-2.315-2.281-2.284a1,1,0,1,1,1.414-1.409L755,667.555l2.277-2.281a1,1,0,1,1,1.414,1.409Z\" transform=\"translate(-751 -665)\"></path></svg>", "price": "<svg id=\"Group_278_copy\" data-name=\"Group 278 copy\" xmlns=\"http://www.w3.org/2000/svg\" width=\"38\" height=\"38\" viewBox=\"0 0 38 38\"><path id=\"Ellipse_305_copy_2\" data-name=\"Ellipse 305 copy 2\" class=\"clswm-1\" d=\"M1851,561a19,19,0,1,1,19-19A19,19,0,0,1,1851,561Zm0-36a17,17,0,1,0,17,17A17,17,0,0,0,1851,525Zm3.97,10.375-0.03.266c-0.01.062-.02,0.127-0.03,0.188l-0.94,7.515h0a2.988,2.988,0,0,1-5.94,0H1848l-0.91-7.525c-0.01-.041-0.01-0.086-0.02-0.128l-0.04-.316h0.01c-0.01-.125-0.04-0.246-0.04-0.375a4,4,0,0,1,8,0c0,0.129-.03.25-0.04,0.375h0.01ZM1851,533a2,2,0,0,0-2,2,1.723,1.723,0,0,0,.06.456L1850,543a1,1,0,0,0,2,0l0.94-7.544A1.723,1.723,0,0,0,1853,535,2,2,0,0,0,1851,533Zm0,14a3,3,0,1,1-3,3A3,3,0,0,1,1851,547Zm0,4a1,1,0,1,0-1-1A1,1,0,0,0,1851,551Z\" transform=\"translate(-1832 -523)\"></path> <path class=\"clswm-2 op-cls\" d=\"M1853,543l-1,1h-2l-1-1-1-8,1-2,1-1h2l1,1,1,2Zm-1,5,1,1v2l-1,1h-2l-1-1v-2l1-1h2Z\" transform=\"translate(-1832 -523)\"></path></svg>"};
  var CASH_TEXT = "Оплата производится наличными деньгами, в момент получения заказа. Подтверждением вашей оплаты является фискальный кассовый чек, вручаемый во время получения и оплаты заказа.";
  var REGION = "Саратов, Саратов, Саратовская область, Поволжье, Россия";
  var FINE = "Наличие, итоговую стоимость и время подтверждает менеджер.";
  var DONE_TITLE = "Заказ сформирован";
  var CASH_LOGO = "/vendor/upload/sale/paysystem/logotip/ae5/ae562c5ef5496bc1fcf9d687ebd6fc69.png";
  var PAY_LOGO = { "1": CASH_LOGO, "8": CASH_LOGO, "7": "/vendor/upload/sale/paysystem/logotip/277/277bac3584decb235d4c33e57d86e33d.png" };

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
    try {
      localStorage.setItem(KEY, JSON.stringify(cart));
      localStorage.setItem(SEQ_KEY, JSON.stringify(sequence().filter(function (id) { return cart[id]; })));
    } catch (e) {}
    badge();
  }
  function sequence() {
    try { return JSON.parse(localStorage.getItem(SEQ_KEY) || "[]") || []; } catch (e) { return []; }
  }
  function ordered(cart) {
    var seq = sequence().filter(function (id) { return cart[id]; });
    Object.keys(cart).forEach(function (id) { if (seq.indexOf(id) === -1) seq.push(id); });
    return seq;
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
    return String(Math.round(n)).replace(/\B(?=(\d{3})+(?!\d))/g, " ") + " ₽";
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
  function esc(s) {
    return String(s).replace(/[&<>"]/g, function (c) {
      return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c];
    });
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
    var card = el.closest(".catalog_item, .item_block, .product-container, .detail, .fixed-basket");
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
  function unmarkInCart(id) {
    var buttons = document.querySelectorAll('.to-cart[data-item="' + id + '"]');
    for (var i = 0; i < buttons.length; i++) {
      var btn = buttons[i];
      var twin = btn.parentElement && btn.parentElement.querySelector('.in-cart[data-item="' + id + '"]');
      if (twin) { btn.style.display = ""; twin.style.display = "none"; }
      else { btn.classList.remove("ms-added"); var s = btn.querySelector("span"); if (s) s.textContent = "В корзину"; }
    }
  }
  function add(id, qty) {
    if (!PRODUCTS[id]) return false;
    var cart = load();
    if (!cart[id]) {
      var seq = sequence().filter(function (x) { return x !== id; });
      seq.push(id);
      try { localStorage.setItem(SEQ_KEY, JSON.stringify(seq)); } catch (e) {}
    }
    cart[id] = (cart[id] || 0) + qty;
    save(cart);
    markInCart(id);
    return true;
  }
  function change(id, act, value) {
    var c = load();
    if (!c[id]) return;
    if (act === "plus") c[id] += 1;
    if (act === "minus") c[id] = Math.max(1, c[id] - 1);
    if (act === "qty") { var v = parseInt(value, 10); c[id] = v > 0 ? v : 1; }
    if (act === "remove") { delete c[id]; unmarkInCart(id); }
    save(c);
  }
  function clearCart() {
    Object.keys(load()).forEach(unmarkInCart);
    save({});
  }

  function shipBlock(sum) {
    if (sum < MIN_ORDER) {
      return '<div class="ms-ship"><div class="ms-ship__head"><span>До минимальной суммы заказа</span><b>' + money(MIN_ORDER - sum) + '</b></div>' +
        '<div class="ms-ship__bar"><i style="width:' + Math.min(100, sum / MIN_ORDER * 100).toFixed(1) + '%"></i></div>' +
        '<div class="ms-ship__hint">Минимальная сумма заказа — ' + money(MIN_ORDER) + '.</div></div>';
    }
    var left = Math.max(0, FREE_DELIVERY - sum);
    return '<div class="ms-ship' + (left ? "" : " is-free") + '"><div class="ms-ship__head"><span>' +
      (left ? "До бесплатной доставки" : "Доставка по Саратову — бесплатно") + '</span>' + (left ? '<b>' + money(left) + '</b>' : "") + '</div>' +
      '<div class="ms-ship__bar"><i style="width:' + Math.min(100, sum / FREE_DELIVERY * 100).toFixed(1) + '%"></i></div>' +
      '<div class="ms-ship__hint">' + (left
        ? "Доставляем только по Саратову: в радиусе 3 км от центра и при заказе от " + money(FREE_DELIVERY) + " — бесплатно, дальше по городу — " + money(DELIVERY_FEE) + "."
        : "Доставляем только по Саратову.") + '</div></div>';
  }
  function noteText(sum) {
    return sum >= FREE_DELIVERY
      ? "Доставка по Саратову: бесплатно · самовывоз бесплатно"
      : "Доставка по Саратову: до " + money(DELIVERY_FEE) + ", в радиусе 3 км от центра — бесплатно · самовывоз бесплатно";
  }

  function flyEl() {
    return document.querySelector("#basket_line .basket_fly");
  }
  function flyAvailable() {
    var line = document.getElementById("basket_line");
    return !!line && getComputedStyle(line).display !== "none" && !!flyEl();
  }
  function flyItem(id, qty) {
    var p = PRODUCTS[id], img = photo(id);
    return '<div class="item" data-id="' + id + '" product-id="' + id + '"><div class="wrap clearfix">' +
      '<div class="image"><a href="' + esc(p.url) + '" class="thumb">' +
        (img ? '<img src="' + esc(img) + '" alt="' + esc(p.name) + '" title="' + esc(p.name) + '">' : "") + '</a></div>' +
      '<div class="body-info">' +
        '<div class="description"><div class="name"><a href="' + esc(p.url) + '">' + esc(p.name) + '</a></div></div>' +
        '<div class="bottom">' +
          '<div class="prices notes"><div class="cost prices clearfix"><div class="price price_new">' + money(p.price) + '</div><div class="price_name">Розничная цена</div></div></div> ' +
          '<div class="buy_block"><div class="counter_block basket"> ' +
            '<span class="minus" data-fly="minus"></span> <input type="text" class="text" value="' + qty + '" data-fly="qty"> <span class="plus" data-fly="plus"></span> ' +
          '</div> </div> ' +
          '<div class="summ"><div class="cost prices"><div class="price">' + money(p.price * qty) + '</div></div></div> ' +
        '</div>' +
        '<div class="remove-cell"><a class="remove" href="#" data-fly="remove" title="Удалить"><i class="svg svg-inline-remove colored_theme_hover_text" aria-hidden="true">' + ICON.remove + '</i></a></div>' +
      '</div></div></div>';
  }
  function flyHead() {
    return '<div class="basket_sort"><div class="basket_title"><div class="ms-fly__eyebrow">Ваш заказ</div>' +
      '<a href="/basket/" class="dark-color basket-link option-font-bold">Корзина</a></div>' +
      '<i class="svg svg-inline-close colored_theme_hover_text" aria-hidden="true" data-fly="close">' + ICON.close + '</i></div>';
  }
  function flyButtons(sum) {
    if (sum < MIN_ORDER) {
      return '<div class="error_block"> <span class="icon_error_block"> <i class="svg svg-inline-price colored_theme_svg" aria-hidden="true">' + ICON.price +
          '</i> <b>Минимальная сумма заказа ' + money(MIN_ORDER) + '</b><br>Пожалуйста, добавьте еще товаров в корзину </span> </div> ' +
        '<div class="buttons clearfix"><div class="basket_back pull-right"><div class="wrap_button">' +
        '<a href="/order/" class="btn btn-transparent-border-color btn-lg is-disabled"><span>Минимальный заказ — ' + money(MIN_ORDER) + '</span></a>' +
        '<div class="ms-fly__fine">' + FINE + '</div></div><div class="description">Полноценное оформление<br> заказа</div></div></div>';
    }
    return '<div class="buttons clearfix"><div class="wrap_button pull-right">' +
      '<a href="/order/" class="btn btn-transparent-border-color btn-lg"><span>Перейти к оформлению</span></a>' +
      '<div class="description">Полноценное оформление<br> заказа</div><div class="ms-fly__fine">' + FINE + '</div></div></div>';
  }
  function renderFly() {
    var fly = flyEl();
    var cont = fly && fly.querySelector(".wrap_cont");
    if (!cont) return;
    var cart = load(), ids = ordered(cart).reverse(), sum = total(cart);
    var oldList = cont.querySelector(".items_wrap");
    var top = oldList ? oldList.scrollTop : 0;
    var body;
    if (!ids.length) {
      body = flyHead() + '<form class="basket_wrapp" id="basket_form" data-ms="1"><ul class="tabs_content basket"><li class="cur">' +
        '<div class="cart-empty"><div class="cart-empty__picture"><div class="img"></div></div><div class="cart-empty__info">' +
        '<div class="title">Ваша корзина пуста</div><p>Исправить это просто: выберите в каталоге интересующий <br>товар и нажмите кнопку «В корзину». </p>' +
        '<a class="btn btn-default round-ignore btn-lg" href="/catalog/"><span>Перейти в каталог</span></a></div></div></li></ul></form>';
    } else {
      body = flyHead() + shipBlock(sum) +
        '<form class="basket_wrapp" id="basket_form" data-ms="1"><ul class="tabs_content basket"><li class="cur"><div class="basket_wrap">' +
          '<div class="items_wrap"><div class="items">' + ids.map(function (id) { return flyItem(id, cart[id]); }).join("") + '</div></div>' +
          '<div class="foot clearfix"><div class="pull-left"><span class="wrap_remove_button basket_action">' +
            '<span class="colored_theme_hover_text remove_all_basket cur" data-fly="clear"><i class="svg svg-inline-closes" aria-hidden="true">' + ICON.closes + '</i> Очистить </span>' +
          '</span></div><div class="total pull-right"><div class="item_title">Итого</div><div class="wrap_prices"><div data-type="price_normal"><div class="price">' +
            money(sum) + '</div></div></div></div></div>' +
          '<div class="ms-fly__note">' + noteText(sum) + '</div>' + flyButtons(sum) +
        '</div></li></ul></form>';
    }
    Array.prototype.slice.call(cont.children).forEach(function (child) {
      if (!child.classList.contains("opener")) cont.removeChild(child);
    });
    cont.insertAdjacentHTML("beforeend", body);
    var list = cont.querySelector(".items_wrap");
    if (list) list.scrollTop = top;
    badge();
  }
  function flyIsOpen() {
    var fly = flyEl();
    return !!fly && fly.classList.contains("ms-open");
  }
  function openFly() {
    var fly = flyEl();
    if (!fly) return;
    renderFly();
    fly.classList.add("ms-open");
    fly.style.right = "0px";
  }
  function closeFly() {
    var fly = flyEl();
    if (!fly) return;
    fly.classList.remove("ms-open");
    fly.style.right = "";
  }

  function emptyBasket() {
    return '<div class="bx-sbb-empty-cart-container"><div class="bx-sbb-empty-cart-image">' +
      '<img src="data:image/gif;base64,R0lGODlhAQABAAAAACH5BAEKAAEALAAAAAABAAEAAAICTAEAOw==" alt=""></div>' +
      '<div class="bx-sbb-empty-cart-text">Ваша корзина пуста</div>' +
      '<div class="bx-sbb-empty-cart-desc"><a href="/catalog/">Нажмите здесь</a>, чтобы продолжить покупки </div></div>';
  }
  function basketRow(id, qty) {
    var p = PRODUCTS[id], img = photo(id), unit = esc(p.unit || "шт");
    return '<tr class="basket-items-list-item-container" data-id="' + id + '">' +
      '<td class="basket-items-list-item-descriptions"><div class="basket-items-list-item-descriptions-inner">' +
        '<div class="basket-item-block-image"><a href="' + esc(p.url) + '" class="basket-item-image-link">' +
          (img ? '<img class="basket-item-image" alt="' + esc(p.name) + '" src="' + esc(img) + '">' : "") + '</a></div>' +
        '<div class="basket-item-block-info"><span class="basket-item-actions-remove visible-xs" data-bact="remove"></span>' +
          '<h2 class="basket-item-info-name"><a href="' + esc(p.url) + '" class="basket-item-info-name-link"><span>' + esc(p.name) + '</span></a></h2>' +
          '<div class="basket-item-block-properties"></div><div class="ms-basket-unit">' + money(p.price) + ' / ' + unit + '</div></div>' +
      '</div></td>' +
      '<td class="basket-items-list-item-price basket-items-list-item-price-for-one hidden-xs"><div class="basket-item-block-price">' +
        '<div class="basket-item-price-current"><span class="basket-item-price-current-text">' + money(p.price) + '</span></div>' +
        '<div class="basket-item-price-title">цена за 1 ' + unit + '</div></div></td>' +
      '<td class="basket-items-list-item-amount"><div class="basket-item-block-amount">' +
        '<span class="basket-item-amount-btn-minus" data-bact="minus"></span>' +
        '<div class="basket-item-amount-filed-block"><input type="text" class="basket-item-amount-filed" value="' + qty + '" data-bact="qty"></div>' +
        '<span class="basket-item-amount-btn-plus" data-bact="plus"></span><div class="basket-item-amount-field-description">' + unit + '</div></div></td>' +
      '<td class="basket-items-list-item-price"><div class="basket-item-block-price"><div class="basket-item-price-current">' +
        '<span class="basket-item-price-current-text">' + money(p.price * qty) + '</span></div></div></td>' +
      '<td class="basket-items-list-item-remove hidden-xs"><div class="basket-item-block-actions"><span class="basket-item-actions-remove" data-bact="remove"></span></div></td>' +
    '</tr>';
  }
  function renderBasket(root) {
    var cart = load(), ids = ordered(cart), sum = total(cart);
    if (!ids.length) { root.innerHTML = emptyBasket(); return; }
    root.innerHTML = '<div id="basket-root" class="bx-basket bx-blue bx-step-opacity">' +
      '<div class="row"><div class="col-xs-12"><div class="basket-checkout-container visible"><div class="basket-checkout-section">' +
        '<div class="ms-basket-sum">' + shipBlock(sum) +
          '<div class="ms-basket-line"><span>' + ids.length + " " + plural(ids.length, "товар", "товара", "товаров") + '</span><span>' + money(sum) + '</span></div>' +
          '<div class="ms-basket-line"><span>Доставка</span><span>самовывоз, бесплатно</span></div></div>' +
        '<div class="basket-checkout-section-inner">' +
          '<div class="basket-checkout-block basket-checkout-block-total"><div class="basket-checkout-block-total-inner"><div class="basket-checkout-block-total-title">Итого</div></div></div>' +
          '<div class="basket-checkout-block basket-checkout-block-total-price"><div class="basket-checkout-block-total-price-inner">' +
            '<div class="basket-coupon-block-total-price-current">' + money(sum) + '</div></div></div>' +
          '<div class="basket-checkout-block basket-checkout-block-btn">' + (sum < MIN_ORDER
            ? '<div class="icon_error_wrapper"><div class="icon_error_block"><i class="svg svg-inline-price colored_theme_svg" aria-hidden="true">' + ICON.price +
              '</i><b>Минимальная сумма заказа ' + money(MIN_ORDER) + '</b><br>Пожалуйста, добавьте еще товаров в корзину</div></div>'
            : '<button type="button" class="btn btn-lg btn-default basket-btn-checkout" data-bact="checkout">Оформить заказ</button>') + '</div>' +
        '</div>' +
        '<div class="ms-basket-note">Самовывоз из магазина — бесплатно, в день заказа.<br>Доставка — только по Саратову, на следующий день.</div>' +
      '</div></div></div></div>' +
      '<div class="row"><div class="col-xs-12"><div class="alert alert-warning" style="display:none"></div></div></div>' +
      '<div class="row"><div class="col-xs-12"><div class="basket-items-list-wrapper basket-items-list-wrapper-height-fixed basket-items-list-wrapper-light">' +
        '<div class="basket-items-list-container"><div class="basket-items-list"><table class="basket-items-list-table"><tbody>' +
          ids.map(function (id) { return basketRow(id, cart[id]); }).join("") +
        '</tbody></table></div></div></div></div></div>' +
    '</div>';
  }
  function bindBasket(root) {
    root.addEventListener("click", function (e) {
      var b = e.target.closest("[data-bact]");
      if (!b || b.getAttribute("data-bact") === "qty") return;
      e.preventDefault();
      if (b.getAttribute("data-bact") === "checkout") { location.href = "/order/"; return; }
      var row = b.closest("[data-id]");
      if (!row) return;
      change(row.getAttribute("data-id"), b.getAttribute("data-bact"));
      renderBasket(root);
    });
    root.addEventListener("change", function (e) {
      if (e.target.getAttribute("data-bact") !== "qty") return;
      change(e.target.closest("[data-id]").getAttribute("data-id"), "qty", e.target.value);
      renderBasket(root);
    });
  }

  var order = { delivery: "courier", pay: "1" };

  function deliveries(sum) {
    var free = sum >= FREE_DELIVERY;
    return [
      { key: "courier", id: free ? "5" : "1", title: "Доставка курьером", cost: free ? "бесплатно" : money(DELIVERY_FEE), fee: free ? 0 : DELIVERY_FEE,
        period: "от 1 до 2 дней", text: "Доставка осуществляется на следующий день в удобное для вас время." },
      { key: "pickup", id: "2", title: "Самовывоз", cost: "бесплатно", fee: 0, text: "Вы можете самостоятельно забрать заказ из нашего магазина." }
    ];
  }
  function payments(key) {
    return key === "pickup"
      ? [{ id: "8", title: "Наличный расчет", text: "" }, { id: "7", title: "Оплата картой онлайн", text: "" }]
      : [{ id: "1", title: "Наличные курьеру", text: CASH_TEXT }, { id: "7", title: "Оплата картой онлайн", text: "" }];
  }
  function card(kind, item, selected) {
    var cls = "bx-soa-pp-company bx-soa-pp-company-item" +
      (kind === "delivery" ? " bx-soa-pp-company--hasprice" + (item.period ? " bx-soa-pp-company--hasperiod" : "") : "") +
      " col-lg-4 col-sm-4 col-xs-6" + (selected ? " bx-selected" : "");
    var html = '<div class="' + cls + '" data-pick="' + kind + '" data-value="' + (kind === "delivery" ? item.key : item.id) + '">' +
      '<div class="bx-soa-pp-company-graf-container"><input type="checkbox" class="bx-soa-pp-company-checkbox" value="' + item.id + '"' + (selected ? " checked" : "") + '></div>' +
      '<div class="bx-soa-pp-company-smalltitle">' + item.title + '</div>';
    if (kind === "delivery") {
      html += '<div class="bx-soa-pp-delivery-cost"><div class="bx-soa-pp-list-termin">Стоимость:</div><div class="bx-soa-pp-list-description">' + item.cost + '</div></div>' +
        (item.period ? '<div class="bx-soa-pp-delivery-period"><div class="bx-soa-pp-list-termin">Срок доставки:</div><div class="bx-soa-pp-list-description"> ' + item.period + ' </div></div>' : "") +
        '<div class="bx-soa-pp-company-description">' + item.text + '</div>';
    }
    return html + '</div>';
  }
  function section(id, title, content, extraClass, aside) {
    return '<div id="' + id + '" class="bx-soa-section bx-active' + (extraClass || "") + '"><div class="bx-soa-section-title-container">' +
      '<h2 class="bx-soa-section-title col-sm-9"><span class="bx-soa-section-title-count"></span>' + title + ' </h2>' + (aside || "") + '</div>' +
      '<div class="bx-soa-section-content container-fluid">' + content + '</div></div>';
  }
  function field(row, name, label, kind, required) {
    var id = "soa-property-" + row;
    var control = kind === "textarea"
      ? '<textarea cols="30" rows="3" name="' + name + '" id="' + id + '" class="form-control bx-ios-fix"></textarea>'
      : '<input type="' + kind + '" name="' + name + '" id="' + id + '" class="form-control bx-soa-customer-input bx-ios-fix">';
    return '<div class="form-group bx-soa-customer-field" data-property-id-row="' + row + '"><label for="' + id + '" class="bx-soa-custom-label"> ' + label +
      (required ? '<span class="bx-authform-starrequired"> *</span>' : "") + '</label><div class="soa-property-container">' + control + '</div></div>';
  }
  function totals(sum, fee) {
    return '<div class="bx-soa-cart-total"><div class="change_basket">Ваш заказ<a href="/basket/" class="change_link">Изменить</a></div>' +
      '<div class="bx-soa-cart-total-line"><span class="bx-soa-cart-t">Товаров на:</span><span class="bx-soa-cart-d">' + money(sum) + '</span></div>' +
      '<div class="bx-soa-cart-total-line"><span class="bx-soa-cart-t">Доставка:</span><span class="bx-soa-cart-d">' + (fee ? money(fee) : "бесплатно") + '</span></div>' +
      '<div class="bx-soa-cart-total-line bx-soa-cart-total-line-total"><span class="bx-soa-cart-t">Итого:</span><span class="bx-soa-cart-d">' + money(sum + fee) + '</span></div>' +
      '<div class="bx-soa-cart-total-button-container lic_condition"><a href="#" class="btn btn-default btn-lg btn-order-save" data-oact="save">Оформить заказ</a></div></div>';
  }
  function orderItems(cart) {
    var head = '<div class="bx-soa-item-tr hidden-sm hidden-xs">' + ["Наименование", "Скидка", "Цена", "Количество", "Сумма"].map(function (t, i) {
      return '<div class="bx-soa-item-td' + (i ? " bx-soa-item-properties bx-text-right" : "") + '" style="padding-bottom: 5px;"><div class="bx-soa-item-td-title">' + t + '</div></div>';
    }).join("") + '</div>';
    var rows = ordered(cart).map(function (id, i) {
      var p = PRODUCTS[id], qty = cart[id], img = photo(id), unit = esc(p.unit || "шт");
      var cell = function (title, value) {
        return '<div class="bx-soa-item-td bx-soa-item-properties bx-text-right"><div class="bx-soa-item-td-title visible-xs visible-sm">' + title + '</div>' +
          '<div class="bx-soa-item-td-text">' + value + '</div></div>';
      };
      return '<div class="bx-soa-item-tr bx-soa-basket-info' + (i ? "" : " bx-soa-item-tr-first") + '"><div class="bx-soa-item-td" style="min-width: 300px;"><div class="bx-soa-item-block">' +
          '<div class="bx-soa-item-img-block"><a href="' + esc(p.url) + '"><div class="bx-soa-item-imgcontainer"' + (img ? ' style="background-image: url(\'' + esc(img) + '\')"' : "") + '></div></a></div>' +
          '<div class="bx-soa-item-content"><div class="bx-soa-item-title"><a href="' + esc(p.url) + '">' + esc(p.name) + '</a></div></div>' +
        '</div></div>' +
        cell("Скидка", "<span>0%</span>") + cell("Цена", '<strong class="bx-price">' + money(p.price) + '</strong>') +
        cell("Количество", "<span>" + qty + " " + unit + "</span>") + cell("Сумма", '<strong class="bx-price all">' + money(p.price * qty) + '</strong>') +
      '</div>';
    }).join("");
    return '<div class="bx-soa-table-fade"><div style="overflow: auto hidden;"><div class="bx-soa-item-table">' + head + rows + '</div></div></div>';
  }
  function renderOrder(root) {
    var kept = {};
    root.querySelectorAll("input[name], textarea[name]").forEach(function (el) { kept[el.name] = el.value; });
    var cart = load(), sum = total(cart);
    if (sum < MIN_ORDER) { location.replace("/basket/"); return; }
    var list = deliveries(sum);
    var picked = list.filter(function (d) { return d.key === order.delivery; })[0] || list[0];
    var pays = payments(picked.key);
    if (!pays.some(function (p) { return p.id === order.pay; })) order.pay = pays[0].id;
    var pay = pays.filter(function (p) { return p.id === order.pay; })[0];
    var region = '<div class="alert alert-danger" style="display:none"></div><div class="bx_soa_location row"><div class="col-xs-12">' +
      '<div class="form-group bx-soa-location-input-container" data-property-id-row="6"><label class="bx-soa-custom-label"> Местоположение<span class="bx-authform-starrequired"> *</span></label>' +
      '<div class="bx-sls"><div class="bx-ui-sls-quick-locations quick-locations"><a href="javascript:void(0)" class="quick-location-tag">Саратов</a></div>' +
      '<div class="dropdown-block bx-ui-sls-input-block form-control"><span class="dropdown-icon"></span>' +
        '<div class="bx-ui-sls-container" style="margin: 0px; padding: 0px; border: none; position: relative;">' +
        '<input type="text" disabled="disabled" autocomplete="off" class="bx-ui-sls-route" style="padding: 0px; margin: 0px;" value="' + REGION + '">' +
        '<input type="text" readonly autocomplete="off" class="bx-ui-sls-fake" value="Саратов" title="' + REGION + '" aria-label="Местоположение"></div>' +
        '<div class="bx-ui-sls-clear" title="Отменить выбор"></div></div></div></div>' +
      '<div class="bx-soa-reference">Выберите свой город в списке. Если вы не нашли свой город, выберите "другое местоположение", а город впишите в поле "Город"</div></div></div>';
    var delivery = '<div class="alert alert-danger" style="display:none"></div><div class="bx-soa-pp row"><div class="col-sm-12 bx-soa-pp-item-container">' +
      list.map(function (d) { return card("delivery", d, d.key === picked.key); }).join("") + '</div></div>';
    var payment = '<div class="alert alert-danger" style="display:none"></div><div class="bx-soa-pp row"><div class="col-sm-12 bx-soa-pp-item-container">' +
      pays.map(function (p) { return card("pay", p, p.id === pay.id); }).join("") + '</div>' +
      (pay.text ? '<div class="col-sm-12 bx-soa-pp-company-description">' + pay.text + '</div>' : "") + '</div>';
    var props = '<div class="alert alert-danger" style="display:none"></div><div class="row"><div class="col-sm-12 bx-soa-customer">' +
      field(1, "name", "Ф.И.О.", "text", true) + field(2, "email", "E-Mail", "text", true) + field(3, "phone", "Телефон", "tel", true) +
      (picked.key === "courier" ? field(7, "address", "Адрес доставки", "textarea", true) : "") +
      '</div><div class="col-sm-12"><div class="form-group bx-soa-customer-field"><label for="orderDescription" class="bx-soa-customer-label">Комментарии к заказу:</label>' +
      '<textarea id="orderDescription" cols="4" class="form-control bx-soa-customer-textarea bx-ios-fix" name="comment"></textarea></div></div></div>';
    var consent = '<div class="form"><div class="license_order_wrap"><div class="licence_block filter label_block onoff">' +
      '<label data-for="licenses_order" class="hidden error">Согласитесь с условиями</label>' +
      '<input type="checkbox" name="licenses_order" id="ms-licenses" value="Y" checked>' +
      '<label class="license" for="ms-licenses">Я согласен на <a href="/company/agreement/" target="_blank">обработку персональных данных</a></label></div></div></div>' +
      '<div id="bx-soa-orderSave" class="lic_condition"><a href="#" style="margin: 10px 0" class="pull-right btn btn-default btn-lg hidden-xs" data-oact="save"> Оформить заказ </a></div>';
    root.innerHTML = '<form name="ORDER_FORM" id="bx-soa-order-form" novalidate><div id="bx-soa-order" class="row orderform--v1 bx-blue">' +
      '<div class="col-sm-9 bx-soa"><div id="bx-soa-main-notifications"><div class="alert alert-danger" style="display:none"></div></div>' +
        '<div id="bx-soa-total-mobile" class="visible-xs">' + totals(sum, picked.fee) + '</div>' +
        section("bx-soa-region", "Тип покупателя и регион доставки", region, " bx-selected") +
        '<div class="pandd">' + section("bx-soa-delivery", "Способ доставки", delivery) + section("bx-soa-paysystem", "Способ оплаты", payment) + '</div>' +
        section("bx-soa-properties", "Покупатель", props) +
        section("bx-soa-basket", "Товары в заказе", orderItems(cart), "", '<div class="col-xs-12 col-sm-3 text-right"><a href="/basket/" class="bx-soa-editstep">Подробнее</a></div>') +
        consent +
      '</div><div id="bx-soa-total" class="col-sm-3 bx-soa-sidebar">' + totals(sum, picked.fee) + '</div>' +
    '</div></form>';
    Object.keys(kept).forEach(function (name) {
      var el = root.querySelector('[name="' + name + '"]');
      if (el && el.type !== "checkbox") el.value = kept[name];
    });
  }
  function required(label) {
    return 'Поле "' + label + '" обязательно для заполнения';
  }
  function fieldError(input) {
    var value = input.value.trim();
    if (input.name === "name") return value ? "" : required("Ф.И.О.");
    if (input.name === "email") return !value ? required("E-Mail") : /^\S+@\S+\.\S+$/.test(value) ? "" : "Введен неверный e-mail";
    if (input.name === "phone") {
      var digits = value.replace(/\D/g, "");
      return !digits ? required("Телефон") : digits.length < 10 ? 'Поле "Телефон" имеет неверный формат' : "";
    }
    if (input.name === "address") return value ? "" : required("Адрес доставки");
    return "";
  }
  function markField(input, text) {
    var group = input.closest(".form-group"), tip = group.querySelector(".bx-soa-tooltip");
    group.classList.toggle("has-error", !!text);
    if (!text) { if (tip) tip.remove(); return; }
    if (!tip) {
      tip = document.createElement("div");
      tip.className = "bx-soa-tooltip bx-soa-tooltip-static bx-soa-tooltip-danger tooltip top";
      tip.innerHTML = '<div class="tooltip-arrow"></div><div class="tooltip-inner"></div>';
      group.insertBefore(tip, group.querySelector(".soa-property-container"));
    }
    tip.setAttribute("data-state", "opened");
    tip.style.cssText = "opacity: 1; display: block;";
    tip.lastChild.textContent = text;
  }
  function checkFields(root) {
    var errors = [];
    root.querySelectorAll("#bx-soa-properties [data-property-id-row] .form-control").forEach(function (input) {
      var text = fieldError(input);
      markField(input, text);
      if (text) errors.push(esc(text));
    });
    var box = root.querySelector("#bx-soa-properties .alert-danger");
    box.innerHTML = errors.length ? "<div>" + errors.join("<br>") + "</div>" : "";
    box.style.display = errors.length ? "" : "none";
    return !errors.length;
  }
  function stamp(d) {
    var two = function (n) { return ("0" + n).slice(-2); };
    return two(d.getDate()) + "." + two(d.getMonth() + 1) + "." + d.getFullYear() + " " + two(d.getHours()) + ":" + two(d.getMinutes());
  }
  function savedOrders() {
    try { return JSON.parse(localStorage.getItem(ORDER_KEY) || "[]"); } catch (e) { return []; }
  }
  function submitOrder(root) {
    var form = root.querySelector("#bx-soa-order-form");
    var f = form.elements, cart = load(), sum = total(cart);
    if (sum < MIN_ORDER) { location.href = "/basket/"; return; }
    var picked = deliveries(sum).filter(function (d) { return d.key === order.delivery; })[0];
    var valid = checkFields(root);
    root.querySelector(".license_order_wrap label.error").classList.toggle("hidden", f.licenses_order.checked);
    if (!valid) {
      var props = root.querySelector("#bx-soa-properties");
      window.scrollTo({ top: props.getBoundingClientRect().top + window.scrollY - 50, behavior: "smooth" });
      return;
    }
    if (!f.licenses_order.checked) return;
    var pay = payments(picked.key).filter(function (p) { return p.id === order.pay; })[0];
    var orders = savedOrders();
    var done = {
      number: String(orders.length + 1), stamp: stamp(new Date()), name: f.name.value.trim(), email: f.email.value.trim(), phone: f.phone.value.trim(),
      delivery: picked.key === "courier" ? "delivery" : "pickup", address: f.address ? f.address.value.trim() : "",
      comment: f.comment.value.trim(), pay: pay.title, payId: pay.id,
      items: ordered(cart).map(function (id) { return { id: id, name: PRODUCTS[id].name, price: PRODUCTS[id].price, qty: cart[id] }; }),
      shipping: picked.fee ? money(picked.fee) : "бесплатно", fee: picked.fee, total: sum + picked.fee, created: new Date().toISOString()
    };
    orders.push(done);
    try { localStorage.setItem(ORDER_KEY, JSON.stringify(orders)); } catch (x) {}
    clearCart();
    try { history.replaceState(null, "", location.pathname + "?ORDER_ID=" + done.number); } catch (x) {}
    renderDone(root, done);
    window.scrollTo(0, 0);
  }
  function bindOrder(root) {
    root.addEventListener("click", function (e) {
      var pick = e.target.closest("[data-pick]");
      if (pick) {
        e.preventDefault();
        if (pick.getAttribute("data-pick") === "delivery") order.delivery = pick.getAttribute("data-value");
        else order.pay = pick.getAttribute("data-value");
        renderOrder(root);
        return;
      }
      var act = e.target.closest("[data-oact]");
      if (act) { e.preventDefault(); submitOrder(root); }
    });
    root.addEventListener("focusout", function (e) {
      if (e.target.matches("#bx-soa-properties [data-property-id-row] .form-control")) markField(e.target, fieldError(e.target));
    });
    root.addEventListener("change", function (e) {
      if (e.target.name === "licenses_order" && e.target.checked) root.querySelector(".license_order_wrap label.error").classList.add("hidden");
    });
  }

  function orderText(o) {
    var lines = ["Заказ №" + o.number + " от " + o.stamp + " — Мир Сладостей", ""];
    o.items.forEach(function (it) { lines.push(it.name + " × " + it.qty + " — " + money(it.price * it.qty)); });
    lines.push("", "Доставка: " + o.shipping, "Итого: " + money(o.total), "",
      "Ф.И.О.: " + o.name, "Телефон: " + o.phone, "E-Mail: " + o.email,
      "Получение: " + (o.delivery === "delivery" ? "доставка, " + o.address : "самовывоз"), "Оплата: " + o.pay);
    if (o.comment) lines.push("Комментарий: " + o.comment);
    return lines.join("\n");
  }
  function renderDone(root, o) {
    var title = document.getElementById("pagetitle");
    if (title) title.textContent = DONE_TITLE;
    document.title = DONE_TITLE + " — Мир Сладостей";
    var mail = "mailto:" + SHOP_MAIL + "?subject=" + encodeURIComponent("Заказ №" + o.number) + "&body=" + encodeURIComponent(orderText(o));
    root.innerHTML = '<table class="sale_order_full_table"><tbody><tr><td> Ваш заказ <b>№' + esc(o.number) + '</b> от ' + esc(o.stamp) +
        ' успешно создан. Номер вашей оплаты: <b>№' + esc(o.number) + '/1</b><br><br> Вы можете следить за выполнением своего заказа в ' +
        '<a href="/auth/">Персональном разделе сайта</a>. Обратите внимание, что для входа в этот раздел вам необходимо будет ввести логин и пароль пользователя сайта. </td></tr></tbody></table>' +
      '<br><br><table class="sale_order_full_table"><tbody><tr><td class="ps_logo"><div class="pay_name">Оплата заказа</div>' +
        '<div class="image"><img src="' + (PAY_LOGO[o.payId] || PAY_LOGO["1"]) + '" style="width:100px" alt="" width="100" height="34"></div>' +
        '<div class="paysystem_name">' + esc(o.pay) + '</div><br></td></tr><tr><td></td></tr></tbody></table>' +
      '<p class="ms-demo-note">Это демонстрационная копия сайта: заказ сохранён только в вашем браузере и в магазин не отправлен. ' +
        '<a href="' + mail + '">Отправить заказ на почту</a> или позвонить: <a href="tel:' + SHOP_PHONE.replace(/[^\d+]/g, "") + '">' + SHOP_PHONE + '</a>.</p>';
  }

  function pageRoot() {
    var container = document.querySelector(".wrapper_inner .container_inner .middle > .container")
      || document.querySelector(".wrapper_inner .container_inner .middle")
      || document.querySelector(".wrapper_inner");
    if (!container) return null;
    container.innerHTML = '<div class="maxwidth-theme"></div>';
    return container.firstChild;
  }
  function mountPages() {
    var path = location.pathname;
    if (/^\/basket\/?$/.test(path)) {
      var basket = pageRoot();
      if (basket) { bindBasket(basket); renderBasket(basket); }
    }
    if (/^\/order\/?$/.test(path)) {
      var id = (location.search.match(/[?&]ORDER_ID=([^&]+)/) || [])[1];
      var done = id && savedOrders().filter(function (o) { return o.number === decodeURIComponent(id) && o.stamp; })[0];
      if (!done && total(load()) < MIN_ORDER) { location.replace("/basket/"); return; }
      var form = pageRoot();
      if (form && done) renderDone(form, done);
      else if (form) { bindOrder(form); renderOrder(form); }
    }
  }

  function onFly(e) {
    var fly = flyEl();
    if (!fly || !fly.contains(e.target)) return false;
    var opener = e.target.closest(".opener");
    if (opener) {
      e.preventDefault(); e.stopImmediatePropagation();
      if (flyIsOpen()) closeFly(); else openFly();
      return true;
    }
    var b = e.target.closest("[data-fly]");
    if (!b) return false;
    var act = b.getAttribute("data-fly");
    if (act === "qty") return true;
    e.preventDefault(); e.stopImmediatePropagation();
    if (act === "close") { closeFly(); return true; }
    if (act === "clear") clearCart();
    else change(b.closest("[data-id]").getAttribute("data-id"), act);
    renderFly();
    return true;
  }

  document.addEventListener("click", function (e) {
    if (!e.target.closest) return;
    if (onFly(e)) return;
    if (flyIsOpen() && !e.target.closest(".basket_fly") && !e.target.closest(".to-cart")) closeFly();
    var t = e.target.closest(".to-cart, .one_click");
    if (!t) return;
    e.preventDefault(); e.stopImmediatePropagation();
    var id = productIdFrom(t);
    if (!id) return;
    if (t.classList.contains("one_click")) { add(id, quantityFor(t, id)); location.href = "/order/"; return; }
    if (add(id, quantityFor(t, id)) && flyAvailable()) openFly();
  }, true);
  document.addEventListener("change", function (e) {
    if (!e.target.getAttribute || e.target.getAttribute("data-fly") !== "qty") return;
    change(e.target.closest("[data-id]").getAttribute("data-id"), "qty", e.target.value);
    renderFly();
  }, true);
  document.addEventListener("keydown", function (e) {
    if (e.key === "Escape" && flyIsOpen()) closeFly();
  });

  function ready(fn) {
    if (document.readyState !== "loading") fn(); else document.addEventListener("DOMContentLoaded", fn);
  }
  ready(function () {
    document.documentElement.classList.add("ms-demo-cart");
    badge();
    var cart = load();
    for (var id in cart) markInCart(id);
    mountPages();
  });
})();
