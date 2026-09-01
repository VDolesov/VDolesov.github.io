(() => {
  "use strict";

  const { SECTIONS, SECTION_MAP, PRODUCTS, FEATURED_IDS, MIN_ORDER, FREE_DELIVERY, DELIVERY_FEE } = window.MS_DATA;

  const CART_KEY = "mir-sladostey-cart-v3";
  const FAV_KEY = "mir-sladostey-favorites-v3";
  const PAGE_SECTION = document.body.dataset.section || "";
  const IS_FAVORITES_PAGE = "favoritesPage" in document.body.dataset;
  const IS_SEARCH_PAGE = "searchPage" in document.body.dataset;

  const qs = (sel, root = document) => root.querySelector(sel);
  const qsa = (sel, root = document) => [...root.querySelectorAll(sel)];
  const money = value => new Intl.NumberFormat("ru-RU").format(value) + " ₽";
  const small = image => image.replace(/\.webp$/, "-640.webp");

  const state = {
    section: PAGE_SECTION || "all",
    query: "",
    sort: "featured",
    visible: 12,
    cart: readStore(CART_KEY, {}),
    favorites: new Set(readStore(FAV_KEY, [])),
    dialogProductId: null,
    cartTrigger: null
  };

  function readStore(key, fallback) {
    try {
      const value = localStorage.getItem(key);
      return value ? JSON.parse(value) : fallback;
    } catch (_) {
      return fallback;
    }
  }

  function writeStore(key, value) {
    try { localStorage.setItem(key, JSON.stringify(value)); } catch (_) { /* приватный режим */ }
  }

  function escapeHtml(value) {
    return String(value).replace(/[&<>'"]/g, char => ({
      "&": "&amp;", "<": "&lt;", ">": "&gt;", "'": "&#39;", '"': "&quot;"
    })[char]);
  }

  function pluralize(count) {
    const mod10 = count % 10;
    const mod100 = count % 100;
    if (mod10 === 1 && mod100 !== 11) return `${count} товар`;
    if (mod10 >= 2 && mod10 <= 4 && (mod100 < 12 || mod100 > 14)) return `${count} товара`;
    return `${count} товаров`;
  }

  function findProduct(id) {
    return PRODUCTS.find(item => item.id === String(id));
  }

  // ------------------------------------------------------------- каталог

  function cardMarkup(item) {
    const isFavorite = state.favorites.has(item.id);
    return `
      <article class="product-card" data-card-id="${item.id}">
        <div class="product-card__visual">
          <a class="product-card__image" href="${item.url}" aria-label="${escapeHtml(item.name)}">
            <img src="${item.image}" srcset="${small(item.image)} 640w, ${item.image} 1024w"
                 sizes="(max-width: 720px) 82vw, (max-width: 1100px) 45vw, 31vw"
                 alt="${escapeHtml(item.name)}" width="1024" height="1024" loading="lazy" decoding="async">
          </a>
          ${item.badge ? `<span class="product-card__badge">${escapeHtml(item.badge)}</span>` : ""}
          <button class="product-card__favorite${isFavorite ? " is-active" : ""}" type="button"
                  data-favorite="${item.id}" aria-pressed="${isFavorite}"
                  aria-label="${isFavorite ? "Убрать из отложенных" : "Отложить"}">
            <svg viewBox="0 0 24 24" aria-hidden="true"><path d="M20.8 4.6a5.4 5.4 0 0 0-7.6 0L12 5.8l-1.2-1.2a5.4 5.4 0 0 0-7.6 7.6L12 21l8.8-8.8a5.4 5.4 0 0 0 0-7.6Z"/></svg>
          </button>
          <button class="product-card__quick" type="button" data-quick-view="${item.id}">Быстрый просмотр</button>
        </div>
        <div class="product-card__body">
          <span class="product-card__category">${escapeHtml(item.sectionTitle)} · Арт. ${escapeHtml(item.article)}</span>
          <h3 class="product-card__title"><a href="${item.url}">${escapeHtml(item.name)}</a></h3>
          <div class="product-card__price">${money(item.price)}<small>за ${escapeHtml(item.unit)}</small></div>
          <span class="product-card__availability">${escapeHtml(item.availability)}</span>
          <button class="product-card__add" type="button" data-add="${item.id}">Добавить в корзину +</button>
        </div>
      </article>`;
  }

  function filteredProducts() {
    const query = state.query.trim().toLocaleLowerCase("ru");
    let result = PRODUCTS.filter(item => {
      if (IS_FAVORITES_PAGE && !state.favorites.has(item.id)) return false;
      const matchesSection = state.section === "all"
        || (state.section === "favorites" && state.favorites.has(item.id))
        || item.section === state.section;
      const haystack = `${item.name} ${item.sectionTitle} ${item.composition || ""}`.toLocaleLowerCase("ru");
      return matchesSection && (!query || haystack.includes(query));
    });

    if (state.sort === "price-asc") result.sort((a, b) => a.price - b.price);
    if (state.sort === "price-desc") result.sort((a, b) => b.price - a.price);
    if (state.sort === "name") result.sort((a, b) => a.name.localeCompare(b.name, "ru"));
    if (state.sort === "featured") {
      const weight = id => {
        const index = FEATURED_IDS.indexOf(id);
        return index === -1 ? FEATURED_IDS.length : index;
      };
      result.sort((a, b) => weight(a.id) - weight(b.id));
    }
    return result;
  }

  function renderCatalog() {
    const grid = qs("#productGrid");
    if (!grid) return;
    const filtered = filteredProducts();
    const visible = filtered.slice(0, state.visible);

    if (visible.length) {
      grid.innerHTML = visible.map(cardMarkup).join("");
    } else {
      const message = IS_FAVORITES_PAGE
        ? "Отложенных товаров пока нет. Отметьте понравившиеся сердечком в каталоге."
        : "Попробуйте другой раздел или более короткий запрос.";
      grid.innerHTML = `<div class="catalog-empty"><span>0</span><h3>Ничего не нашлось</h3><p>${message}</p></div>`;
    }

    const count = qs("[data-catalog-count]");
    if (count) count.textContent = pluralize(filtered.length);
    const more = qs("[data-load-more]");
    if (more) more.hidden = state.visible >= filtered.length;
    const clear = qs("[data-clear-filters]");
    if (clear) clear.hidden = (state.section === "all" || state.section === PAGE_SECTION) && !state.query;

    qsa("button[data-filter]").forEach(button => {
      const active = button.dataset.filter === state.section;
      button.classList.toggle("is-active", active);
      button.setAttribute("aria-pressed", String(active));
    });
  }

  function renderCounters() {
    qsa("[data-section-count]").forEach(node => {
      const slug = node.dataset.sectionCount;
      node.textContent = pluralize(PRODUCTS.filter(p => p.section === slug).length);
    });
    const total = qs("[data-total-count]");
    if (total) total.textContent = `${PRODUCTS.length}`;
  }

  // ------------------------------------------------------- быстрый просмотр

  function openProductDialog(id) {
    const item = findProduct(id);
    const dialog = qs("[data-product-dialog]");
    if (!item || !dialog) return;
    state.dialogProductId = item.id;
    const image = qs("[data-dialog-image]", dialog);
    image.src = item.image;
    image.alt = item.name;
    qs("[data-dialog-category]", dialog).textContent = `${item.sectionTitle} · Арт. ${item.article}`;
    qs("[data-dialog-name]", dialog).textContent = item.name;
    qs("[data-dialog-description]", dialog).textContent = item.description;
    qs("[data-dialog-price]", dialog).textContent = money(item.price);
    qs("[data-dialog-unit]", dialog).textContent = `Цена за ${item.unit}`;
    const link = qs("[data-dialog-link]", dialog);
    if (link) link.href = item.url;
    const tags = qsa(".product-dialog__tags span", dialog);
    if (tags[0]) tags[0].textContent = item.availability;
    if (tags[1]) tags[1].textContent = "Собственное производство";
    qs("[data-dialog-qty]", dialog).value = 1;
    dialog.showModal();
  }

  // ---------------------------------------------------------------- корзина

  function cartLines() {
    return Object.entries(state.cart)
      .map(([id, quantity]) => ({ item: findProduct(id), quantity }))
      .filter(line => line.item && line.quantity > 0);
  }

  function cartTotal() {
    return cartLines().reduce((sum, line) => sum + line.item.price * line.quantity, 0);
  }

  function addToCart(id, quantity = 1) {
    const item = findProduct(id);
    if (!item) return;
    state.cart[id] = (state.cart[id] || 0) + Number(quantity || 1);
    writeStore(CART_KEY, state.cart);
    updateCart();
    showToast(`${item.name} — добавлено в корзину`);
  }

  function setQuantity(id, quantity) {
    if (quantity <= 0) delete state.cart[id];
    else state.cart[id] = Math.min(99, quantity);
    writeStore(CART_KEY, state.cart);
    updateCart();
  }

  function toggleFavorite(id) {
    const item = findProduct(id);
    if (!item) return;
    if (state.favorites.has(id)) {
      state.favorites.delete(id);
      showToast(`${item.name}: убрано из отложенных`);
    } else {
      state.favorites.add(id);
      showToast(`${item.name}: отложено`);
    }
    writeStore(FAV_KEY, [...state.favorites]);
    qsa("[data-favorites-count]").forEach(node => node.textContent = state.favorites.size);
    qsa(`[data-favorite="${id}"]`).forEach(button => {
      const active = state.favorites.has(id);
      button.classList.toggle("is-active", active);
      button.setAttribute("aria-pressed", String(active));
    });
    if (IS_FAVORITES_PAGE) renderCatalog();
  }

  function cartItemMarkup({ item, quantity }, variant) {
    const wide = variant === "page";
    return `
      <article class="cart-item${wide ? " cart-item--page" : ""}">
        <div class="cart-item__image"><a href="${item.url}"><img src="${small(item.image)}" alt="" width="82" height="82" decoding="async"></a></div>
        <div>
          <h3><a href="${item.url}">${escapeHtml(item.name)}</a></h3>
          <span class="cart-item__meta">${escapeHtml(item.sectionTitle)} · ${money(item.price)} за ${escapeHtml(item.unit)}</span>
          <div class="cart-item__controls">
            <button type="button" data-cart-minus="${item.id}" aria-label="Уменьшить количество">−</button>
            <span>${quantity}</span>
            <button type="button" data-cart-plus="${item.id}" aria-label="Увеличить количество">+</button>
          </div>
        </div>
        <div class="cart-item__right">
          <button class="cart-item__remove" type="button" data-cart-remove="${item.id}" aria-label="Удалить">×</button>
          <strong>${money(item.price * quantity)}</strong>
        </div>
      </article>`;
  }

  function updateCart() {
    const lines = cartLines();
    const count = lines.reduce((sum, line) => sum + line.quantity, 0);
    const total = cartTotal();

    qsa("[data-cart-count]").forEach(node => node.textContent = count);
    qsa("[data-favorites-count]").forEach(node => node.textContent = state.favorites.size);

    const drawerItems = qs("[data-cart-items]");
    if (drawerItems) drawerItems.innerHTML = lines.map(line => cartItemMarkup(line, "drawer")).join("");
    const drawerEmpty = qs("[data-cart-empty]");
    if (drawerEmpty) drawerEmpty.hidden = lines.length > 0;
    const drawerFooter = qs("[data-cart-footer]");
    if (drawerFooter) drawerFooter.hidden = lines.length === 0;
    const drawerTotal = qs("[data-cart-total]");
    if (drawerTotal) drawerTotal.textContent = money(total);

    const remaining = Math.max(0, FREE_DELIVERY - total);
    const missing = Math.max(0, MIN_ORDER - total);
    qsa("[data-progress-bar]").forEach(node => node.style.width = `${Math.min(100, total / FREE_DELIVERY * 100)}%`);
    qsa("[data-progress-label]").forEach(node => {
      node.textContent = missing ? "До минимальной суммы заказа"
        : remaining ? "До бесплатной доставки" : "Бесплатная доставка доступна";
    });
    qsa("[data-progress-value]").forEach(node => {
      node.textContent = missing ? money(missing) : remaining ? money(remaining) : "Готово";
    });
    qsa("[data-cart-delivery]").forEach(node => {
      node.textContent = total >= FREE_DELIVERY
        ? "Доставка по Саратову: бесплатно"
        : `Доставка по Саратову: ${money(DELIVERY_FEE)} · самовывоз бесплатно`;
    });

    renderBasketPage(lines, total, missing);
    renderOrderSummary(lines, total);
  }

  function renderBasketPage(lines, total, missing) {
    const layout = qs("[data-basket-layout]");
    if (!layout) return;
    const empty = qs("[data-basket-empty]");
    layout.hidden = lines.length === 0;
    if (empty) empty.hidden = lines.length > 0;

    qs("[data-basket-items]").innerHTML = lines.map(line => cartItemMarkup(line, "page")).join("");
    qs("[data-basket-total]").textContent = money(total);
    const delivery = qs("[data-basket-delivery]");
    if (delivery) {
      delivery.textContent = total >= FREE_DELIVERY ? "бесплатно" : `${money(DELIVERY_FEE)} по Саратову`;
    }
    const checkout = qs("[data-basket-checkout]");
    if (checkout) {
      const blocked = missing > 0;
      checkout.classList.toggle("is-disabled", blocked);
      checkout.textContent = blocked ? `Добавьте ещё ${money(missing)}` : "Перейти к оформлению";
    }
  }

  function renderOrderSummary(lines, total) {
    const node = qs("[data-order-summary]");
    if (!node) return;
    if (!lines.length) {
      node.innerHTML = '<p class="order-summary__empty">Корзина пуста — <a href="/catalog/">выберите изделия</a>.</p>';
      return;
    }
    const rows = lines.map(({ item, quantity }) =>
      `<div><span>${escapeHtml(item.name)} × ${quantity}</span><b>${money(item.price * quantity)}</b></div>`).join("");
    node.innerHTML = `<div class="order-summary__rows">${rows}</div>
      <div class="order-summary__total"><span>Итого</span><strong>${money(total)}</strong></div>`;
  }

  function orderText() {
    const lines = cartLines();
    return ["Заказ «Мир сладостей»",
      ...lines.map(({ item, quantity }) => `${item.name} (арт. ${item.article}) — ${quantity} × ${money(item.price)}`),
      `Итого: ${money(cartTotal())}`].join("\n");
  }

  // ------------------------------------------------------------------ drawer

  function openCart(trigger = null) {
    const drawer = qs("[data-cart-drawer]");
    if (!drawer) return;
    state.cartTrigger = trigger;
    drawer.classList.add("is-open");
    drawer.setAttribute("aria-hidden", "false");
    qsa("[data-open-cart]").forEach(button => button.setAttribute("aria-expanded", "true"));
    qs("[data-overlay]").classList.add("is-visible");
    document.body.classList.add("is-locked");
    setTimeout(() => qs("[data-close-cart]").focus(), 120);
  }

  function closeCart() {
    const drawer = qs("[data-cart-drawer]");
    if (!drawer) return;
    drawer.classList.remove("is-open");
    drawer.setAttribute("aria-hidden", "true");
    qsa("[data-open-cart]").forEach(button => button.setAttribute("aria-expanded", "false"));
    qs("[data-overlay]").classList.remove("is-visible");
    document.body.classList.remove("is-locked");
    if (state.cartTrigger) state.cartTrigger.focus();
    state.cartTrigger = null;
  }

  let toastTimer;
  function showToast(message) {
    const toast = qs("[data-toast]");
    if (!toast) return;
    toast.textContent = message;
    toast.classList.add("is-visible");
    clearTimeout(toastTimer);
    toastTimer = setTimeout(() => toast.classList.remove("is-visible"), 2600);
  }

  // ------------------------------------------------------------------ события

  function initEvents() {
    document.addEventListener("click", event => {
      const quick = event.target.closest("[data-quick-view]");
      if (quick) { openProductDialog(quick.dataset.quickView); return; }

      const add = event.target.closest("[data-add]");
      if (add) {
        const qtyInput = add.hasAttribute("data-add-qty") ? qs("[data-qty-input]") : null;
        addToCart(add.dataset.add, qtyInput ? Math.max(1, Number(qtyInput.value) || 1) : 1);
        return;
      }

      const favorite = event.target.closest("[data-favorite]");
      if (favorite) { toggleFavorite(favorite.dataset.favorite); return; }

      const filter = event.target.closest("button[data-filter]");
      if (filter) {
        state.section = filter.dataset.filter;
        state.visible = 12;
        renderCatalog();
        return;
      }

      const plus = event.target.closest("[data-cart-plus]");
      if (plus) { setQuantity(plus.dataset.cartPlus, (state.cart[plus.dataset.cartPlus] || 0) + 1); return; }

      const minus = event.target.closest("[data-cart-minus]");
      if (minus) { setQuantity(minus.dataset.cartMinus, (state.cart[minus.dataset.cartMinus] || 0) - 1); return; }

      const remove = event.target.closest("[data-cart-remove]");
      if (remove) { setQuantity(remove.dataset.cartRemove, 0); return; }

      const qtyMinus = event.target.closest("[data-qty-minus]");
      if (qtyMinus) {
        const input = qs("[data-qty-input]");
        input.value = Math.max(1, Number(input.value) - 1);
        return;
      }
      const qtyPlus = event.target.closest("[data-qty-plus]");
      if (qtyPlus) {
        const input = qs("[data-qty-input]");
        input.value = Math.min(99, Number(input.value) + 1);
        return;
      }

      if (event.target.closest("[data-open-cart]")) { openCart(event.target.closest("[data-open-cart]")); return; }
      if (event.target.closest("[data-close-cart]") || event.target.matches("[data-overlay]")) { closeCart(); return; }

      if (event.target.closest("[data-open-custom]")) { qs("[data-custom-dialog]").showModal(); return; }
      if (event.target.closest("[data-open-callback]")) { qs("[data-callback-dialog]").showModal(); return; }

      const basketCheckout = event.target.closest("[data-basket-checkout]");
      if (basketCheckout && basketCheckout.classList.contains("is-disabled")) {
        event.preventDefault();
        showToast(`Минимальная сумма заказа — ${money(MIN_ORDER)}`);
        return;
      }

      const closeDialog = event.target.closest("[data-close-dialog]");
      if (closeDialog) closeDialog.closest("dialog").close();
    });

    qsa("dialog").forEach(dialog => {
      dialog.addEventListener("click", event => { if (event.target === dialog) dialog.close(); });
    });

    const dialogAdd = qs("[data-dialog-add]");
    if (dialogAdd) dialogAdd.addEventListener("click", () => {
      const qty = Math.max(1, Number(qs("[data-dialog-qty]").value) || 1);
      addToCart(state.dialogProductId, qty);
      qs("[data-product-dialog]").close();
      openCart();
    });

    const search = qs("[data-catalog-search]");
    if (search) search.addEventListener("input", event => {
      state.query = event.target.value;
      state.visible = 12;
      renderCatalog();
      if (IS_SEARCH_PAGE) {
        const url = new URL(window.location);
        if (state.query) url.searchParams.set("q", state.query);
        else url.searchParams.delete("q");
        history.replaceState(null, "", url);
      }
    });

    const sort = qs("[data-catalog-sort]");
    if (sort) sort.addEventListener("change", event => {
      state.sort = event.target.value;
      renderCatalog();
    });

    const more = qs("[data-load-more]");
    if (more) more.addEventListener("click", () => {
      state.visible += 12;
      renderCatalog();
    });

    const clear = qs("[data-clear-filters]");
    if (clear) clear.addEventListener("click", () => {
      state.section = PAGE_SECTION || "all";
      state.query = "";
      state.visible = 12;
      if (search) search.value = "";
      renderCatalog();
    });

    const menuButton = qs("[data-menu-toggle]");
    const mobileMenu = qs("#mobileMenu");
    if (menuButton && mobileMenu) {
      menuButton.addEventListener("click", () => {
        const open = menuButton.getAttribute("aria-expanded") === "true";
        menuButton.setAttribute("aria-expanded", String(!open));
        mobileMenu.classList.toggle("is-open", !open);
      });
    }

    const orderForm = qs("[data-order-form]");
    if (orderForm) orderForm.addEventListener("submit", event => {
      event.preventDefault();
      if (!cartLines().length) { showToast("Корзина пуста"); return; }
      const data = new FormData(event.currentTarget);
      const method = data.get("delivery-method");
      const where = method === "Доставка" ? `Адрес: ${data.get("address")}` : `Самовывоз: ${data.get("pickup")}`;
      const summary = `${orderText()}\n\nПолучатель: ${data.get("name")}\nТелефон: ${data.get("phone")}\n` +
        `Способ: ${method}\n${where}\nДата: ${data.get("date") || "уточнить"}\n` +
        `Оплата: ${data.get("payment")}\nКомментарий: ${data.get("comment") || "—"}`;
      if (navigator.clipboard?.writeText) navigator.clipboard.writeText(summary).catch(() => {});
      showToast("Заказ подготовлен и скопирован — подтвердите его по телефону");
    });

    const customForm = qs("[data-custom-form]");
    if (customForm) customForm.addEventListener("submit", event => {
      event.preventDefault();
      const data = new FormData(event.currentTarget);
      const summary = `Индивидуальный торт\nИмя: ${data.get("name")}\nТелефон: ${data.get("phone")}\n` +
        `Дата события: ${data.get("date")}\nГостей: ${data.get("guests")}\n` +
        `Пожелания: ${data.get("idea")}\nРеференс: ${data.get("reference") || "—"}`;
      if (navigator.clipboard?.writeText) navigator.clipboard.writeText(summary).catch(() => {});
      qs("[data-custom-dialog]").close();
      event.currentTarget.reset();
      showToast("Заявка подготовлена и скопирована — подтвердите её по телефону");
    });

    const callbackForm = qs("[data-callback-form]");
    if (callbackForm) callbackForm.addEventListener("submit", event => {
      event.preventDefault();
      qs("[data-callback-dialog]").close();
      event.currentTarget.reset();
      showToast("Заявка принята — менеджер перезвонит в рабочее время");
    });

    const reviewForm = qs("[data-review-form]");
    if (reviewForm) reviewForm.addEventListener("submit", event => {
      event.preventDefault();
      event.currentTarget.reset();
      showToast("Спасибо! Отзыв отправлен на модерацию");
    });

    const loginForm = qs("[data-login-form]");
    if (loginForm) loginForm.addEventListener("submit", event => {
      event.preventDefault();
      showToast("Личный кабинет подключается вместе с серверной частью");
    });

    document.addEventListener("keydown", event => {
      if (event.key === "Escape") closeCart();
    });

    const method = qs("[data-delivery-method]");
    if (method) {
      const sync = () => {
        const delivery = method.value === "Доставка";
        const address = qs("[data-address-field]");
        const pickup = qs("[data-pickup-field]");
        address.hidden = !delivery;
        pickup.hidden = delivery;
        qs("input", address).required = delivery;
        qs("select", pickup).required = !delivery;
      };
      method.addEventListener("change", sync);
      sync();
    }

    qsa('input[name="phone"]').forEach(input => input.addEventListener("input", () => {
      const digits = input.value.replace(/\D/g, "").replace(/^8/, "7").slice(0, 11);
      const body = digits.startsWith("7") ? digits.slice(1) : digits;
      let value = "+7";
      if (body.length) value += ` (${body.slice(0, 3)}`;
      if (body.length >= 3) value += ")";
      if (body.length > 3) value += ` ${body.slice(3, 6)}`;
      if (body.length > 6) value += `-${body.slice(6, 8)}`;
      if (body.length > 8) value += `-${body.slice(8, 10)}`;
      input.value = value;
    }));
  }

  function initMotion() {
    const header = qs("#siteHeader");
    const progress = qs("[data-scroll-progress]");
    let frame = 0;
    const sync = () => {
      frame = 0;
      if (header) header.classList.toggle("is-scrolled", window.scrollY > 40);
      const scrollable = document.documentElement.scrollHeight - window.innerHeight;
      if (progress) progress.style.transform = `scaleX(${scrollable > 0 ? Math.min(1, window.scrollY / scrollable) : 0})`;
    };
    const schedule = () => { if (!frame) frame = requestAnimationFrame(sync); };
    sync();
    window.addEventListener("scroll", schedule, { passive: true });
    window.addEventListener("resize", schedule, { passive: true });

    const reduced = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    const items = qsa(".reveal:not(.is-visible)");
    if (reduced || !("IntersectionObserver" in window)) {
      items.forEach(item => item.classList.add("is-visible"));
    } else {
      const observer = new IntersectionObserver(entries => {
        entries.forEach(entry => {
          if (entry.isIntersecting) {
            entry.target.classList.add("is-visible");
            observer.unobserve(entry.target);
          }
        });
      }, { threshold: .08, rootMargin: "0px 0px -60px" });
      items.forEach(item => observer.observe(item));
    }
  }

  function init() {
    if (IS_SEARCH_PAGE) {
      const query = new URLSearchParams(window.location.search).get("q") || "";
      state.query = query;
      const input = qs("[data-catalog-search]");
      if (input) input.value = query;
    }
    renderCounters();
    renderCatalog();
    updateCart();
    initEvents();
    initMotion();
    qsa("[data-year]").forEach(node => node.textContent = new Date().getFullYear());
    const tomorrow = new Date(Date.now() + 86400000).toISOString().slice(0, 10);
    qsa('input[type="date"]').forEach(input => input.min = tomorrow);
  }

  init();
})();
