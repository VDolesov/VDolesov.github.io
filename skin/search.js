(function () {
  "use strict";

  var PRODUCTS = window.MS_PRODUCTS || {};
  var SECTIONS = window.MS_SECTIONS || [];
  var PHOTOS = window.MS_PHOTOS || [];
  var ORIGIN = window.MS_ORIGIN || "";

  function esc(s) {
    return String(s).replace(/[&<>"]/g, function (c) {
      return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c];
    });
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
  function sectionName(slug) {
    for (var i = 0; i < SECTIONS.length; i++) if (SECTIONS[i].slug === slug) return SECTIONS[i].name;
    return "";
  }
  function norm(s) {
    return String(s || "").toLowerCase().replace(/ё/g, "е").replace(/[^a-zа-я0-9]+/g, " ").trim();
  }
  function stem(w) {
    if (w.length > 6) return w.slice(0, -2);
    if (w.length > 4) return w.slice(0, -1);
    return w;
  }
  function find(query) {
    var words = norm(query).split(" ").filter(Boolean).map(stem);
    if (!words.length) return [];
    var out = [];
    for (var id in PRODUCTS) {
      var p = PRODUCTS[id];
      var hay = norm(p.name + " " + sectionName(p.section) + " " + (p.composition || ""));
      var name = norm(p.name);
      var ok = true, score = 0;
      for (var i = 0; i < words.length; i++) {
        if (hay.indexOf(words[i]) === -1) { ok = false; break; }
        if (name.indexOf(words[i]) !== -1) score += 2; else score += 1;
      }
      if (ok) out.push({ id: id, score: score });
    }
    out.sort(function (a, b) { return b.score - a.score || PRODUCTS[a.id].name.localeCompare(PRODUCTS[b.id].name, "ru"); });
    return out.map(function (x) { return x.id; });
  }

  function card(id) {
    var p = PRODUCTS[id];
    var img = photo(id);
    return '<div class="ms-card" data-item="' + id + '">' +
      '<a class="ms-card__pic" href="' + esc(p.url) + '">' + (img ? '<img src="' + esc(img) + '" alt="' + esc(p.name) + '" loading="lazy">' : "") + '</a>' +
      '<div class="ms-card__body">' +
        '<div class="ms-card__section">' + esc(sectionName(p.section)) + '</div>' +
        '<a class="ms-card__name" href="' + esc(p.url) + '">' + esc(p.name) + '</a>' +
        '<div class="ms-card__price">' + money(p.price) + '<small>/' + esc(p.unit || "шт") + '</small></div>' +
        '<button type="button" class="btn btn-default btn-lg to-cart ms-card__btn" data-item="' + id + '"><span>В корзину</span></button>' +
      '</div>' +
    '</div>';
  }

  function render(root, query) {
    var ids = find(query);
    var n = ids.length;
    var html = '<form class="ms-search" action="/search/" method="get" role="search">' +
      '<input class="ms-search__input" type="search" name="q" value="' + esc(query) + '" placeholder="Например, медовик или пирог с мясом" autocomplete="off">' +
      '<button type="submit" class="btn btn-default btn-lg">Найти</button>' +
    '</form>';
    if (!query.trim()) {
      html += '<p class="ms-search__hint">Введите название или ингредиент — ищем по всему каталогу.</p>';
    } else if (!n) {
      html += '<div class="ms-search__empty">' +
        '<div class="ms-search__title">По запросу «' + esc(query) + '» ничего не нашлось</div>' +
        '<p>Попробуйте короче — «торт», «пирог», «мясо» — или загляните в разделы:</p>' +
        '<div class="ms-search__sections">' + SECTIONS.map(function (s) {
          return '<a href="/catalog/' + esc(s.slug) + '/">' + esc(s.name) + '</a>';
        }).join("") + '</div></div>';
    } else {
      html += '<div class="ms-search__count">' + n + ' ' + plural(n, "товар", "товара", "товаров") +
        ' по запросу «' + esc(query) + '»</div>' +
        '<div class="ms-grid">' + ids.map(card).join("") + '</div>';
    }
    root.innerHTML = html;
    var input = root.querySelector(".ms-search__input");
    if (!query.trim() && input) input.focus();
    markInCart(root);
  }

  function renderBadge(root, badge, label) {
    var ids = Object.keys(PRODUCTS).filter(function (id) {
      return (PRODUCTS[id].badges || []).indexOf(badge) !== -1;
    }).sort(function (a, b) { return PRODUCTS[a].name.localeCompare(PRODUCTS[b].name, "ru"); });
    var n = ids.length;
    root.innerHTML = '<div class="ms-search__count">' + n + ' ' + plural(n, "товар", "товара", "товаров") +
      ' со стикером «' + esc(label) + '»</div>' +
      '<div class="ms-grid">' + ids.map(card).join("") + '</div>' +
      '<div class="ms-search__sections ms-search__sections--foot">' + SECTIONS.map(function (s) {
        return '<a href="/catalog/' + esc(s.slug) + '/">' + esc(s.name) + '</a>';
      }).join("") + '</div>';
    markInCart(root);
  }

  function markInCart(root) {
    var cart = {};
    try { cart = JSON.parse(localStorage.getItem("ms_cart") || "{}"); } catch (e) {}
    for (var id in cart) {
      var btn = root.querySelector('.to-cart[data-item="' + id + '"]');
      if (btn) { btn.classList.add("ms-added"); btn.querySelector("span").textContent = "В корзине"; }
    }
  }

  function mount() {
    var path = location.pathname.replace(/\/+$/, "/");
    var m = location.search.match(/[?&]q=([^&]*)/);
    var hit = path === "/catalog/" && /[?&]hit=/.test(location.search);
    var query = m ? decodeURIComponent(m[1].replace(/\+/g, " ")) : "";
    var isSearch = path === "/search/";
    if (!isSearch && !hit && !(path === "/catalog/" && m)) return;

    var container = document.querySelector(".wrapper_inner .container_inner .middle > .container");
    if (!container) return;
    var root = document.createElement("div");
    root.className = "ms-search-root";
    container.innerHTML = '<div class="maxwidth-theme"></div>';
    container.firstChild.appendChild(root);
    var title = document.getElementById("pagetitle");
    if (hit) {
      if (title) title.textContent = "Хиты";
      document.title = "Хиты — Мир Сладостей";
      renderBadge(root, "хит", "Хит");
      return;
    }
    if (title) title.textContent = query.trim() ? "Поиск" : "Поиск по каталогу";
    document.title = (query.trim() ? "Поиск: " + query : "Поиск") + " — Мир Сладостей";
    render(root, query);
  }

  function ready(fn) {
    if (document.readyState !== "loading") fn(); else document.addEventListener("DOMContentLoaded", fn);
  }
  ready(mount);
})();
