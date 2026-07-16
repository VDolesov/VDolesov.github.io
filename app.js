(() => {
  "use strict";

  const { CATEGORY_META, PRODUCTS, FEATURED_IDS, MIN_ORDER, FREE_DELIVERY, DELIVERY_FEE } = window.MS_DATA;

  const CART_KEY = "mir-sladostey-classic-cart-v1";
  const FAV_KEY = "mir-sladostey-classic-favorites-v1";

  const PAGE_CATEGORY = document.body.dataset.category || "";

  const state = {
    category: PAGE_CATEGORY || "all",
    query: "",
    sort: "featured",
    visible: 12,
    cart: readStore(CART_KEY, {}),
    favorites: new Set(readStore(FAV_KEY, [])),
    dialogProductId: null,
    cartTrigger: null
  };

  const qs = (selector, root = document) => root.querySelector(selector);
  const qsa = (selector, root = document) => [...root.querySelectorAll(selector)];
  const money = value => new Intl.NumberFormat("ru-RU").format(value) + " ₽";
  const hasResponsiveImage = image => /-v\d+\.webp$/.test(image);
  const smallImage = image => hasResponsiveImage(image) ? image.replace(/\.webp$/, "-640.webp") : image;
  const responsiveSrcset = image => `${smallImage(image)} 640w, ${image} 1024w`;

  function readStore(key, fallback) {
    try {
      const value = localStorage.getItem(key);
      return value ? JSON.parse(value) : fallback;
    } catch (_) {
      return fallback;
    }
  }

  function writeStore(key, value) {
    try { localStorage.setItem(key, JSON.stringify(value)); } catch (_) { /* local file privacy mode */ }
  }

  function escapeHtml(value) {
    return String(value).replace(/[&<>'"]/g, char => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", "'": "&#39;", '"': "&quot;" })[char]);
  }

  function pluralizeProducts(count) {
    const mod10 = count % 10;
    const mod100 = count % 100;
    if (mod10 === 1 && mod100 !== 11) return `${count} товар`;
    if (mod10 >= 2 && mod10 <= 4 && (mod100 < 12 || mod100 > 14)) return `${count} товара`;
    return `${count} товаров`;
  }

  function productCardMarkup(item, featured = false) {
    const isFavorite = state.favorites.has(item.id);
    const responsive = hasResponsiveImage(item.image);
    const sizes = featured
      ? "(max-width: 720px) 82vw, (max-width: 1100px) 45vw, 25vw"
      : "(max-width: 720px) 82vw, (max-width: 1100px) 45vw, 31vw";
    return `
      <article class="product-card${featured ? " reveal is-visible" : ""}" data-card-id="${item.id}">
        <div class="product-card__visual">
          <button class="product-card__image" type="button" data-quick-view="${item.id}" aria-label="Подробнее: ${escapeHtml(item.name)}">
            <img src="${item.image}"${responsive ? ` srcset="${responsiveSrcset(item.image)}" sizes="${sizes}"` : ""} alt="${escapeHtml(item.name)}" width="1024" height="1024" loading="lazy" decoding="async">
          </button>
          ${item.badge ? `<span class="product-card__badge">${escapeHtml(item.badge)}</span>` : ""}
          <button class="product-card__favorite${isFavorite ? " is-active" : ""}" type="button" data-favorite="${item.id}" aria-label="${isFavorite ? "Убрать из избранного" : "Добавить в избранное"}" aria-pressed="${isFavorite}">
            <svg viewBox="0 0 24 24" aria-hidden="true"><path d="M20.8 4.6a5.4 5.4 0 0 0-7.6 0L12 5.8l-1.2-1.2a5.4 5.4 0 0 0-7.6 7.6L12 21l8.8-8.8a5.4 5.4 0 0 0 0-7.6Z"/></svg>
          </button>
          <button class="product-card__quick" type="button" data-quick-view="${item.id}">Быстрый просмотр</button>
        </div>
        <div class="product-card__body">
          <span class="product-card__category">${CATEGORY_META[item.category].label} · Арт. ${item.article}</span>
          <h3 class="product-card__title">${escapeHtml(item.name)}</h3>
          <div class="product-card__price">${money(item.price)}<small>за ${item.unit}</small></div>
          <span class="product-card__availability">${item.availability}</span>
          <button class="product-card__add" type="button" data-add="${item.id}">Добавить в корзину +</button>
        </div>
      </article>`;
  }

  function renderFeatured() {
    const grid = qs("#featuredGrid");
    if (!grid) return;
    const featured = FEATURED_IDS.map(id => PRODUCTS.find(item => item.id === id)).filter(Boolean);
    grid.innerHTML = featured.map(item => productCardMarkup(item, true)).join("");
  }

  function getFilteredProducts() {
    const query = state.query.trim().toLocaleLowerCase("ru");
    let result = PRODUCTS.filter(item => {
      const matchesCategory = state.category === "all"
        || (state.category === "favorites" && state.favorites.has(item.id))
        || item.category === state.category;
      const matchesQuery = !query || `${item.name} ${CATEGORY_META[item.category].label}`.toLocaleLowerCase("ru").includes(query);
      return matchesCategory && matchesQuery;
    });

    if (state.sort === "price-asc") result.sort((a, b) => a.price - b.price);
    if (state.sort === "price-desc") result.sort((a, b) => b.price - a.price);
    if (state.sort === "name") result.sort((a, b) => a.name.localeCompare(b.name, "ru"));
    return result;
  }

  function renderCatalog() {
    const grid = qs("#productGrid");
    if (!grid) return;
    const filtered = getFilteredProducts();
    const visible = filtered.slice(0, state.visible);

    if (visible.length) {
      grid.innerHTML = visible.map(item => productCardMarkup(item)).join("");
    } else {
      grid.innerHTML = `<div class="catalog-empty"><span>0</span><h3>Ничего не нашлось</h3><p>Попробуйте другую категорию или более короткий запрос.</p></div>`;
    }

    const count = qs("[data-catalog-count]");
    if (count) count.textContent = pluralizeProducts(filtered.length);
    const more = qs("[data-load-more]");
    if (more) more.hidden = state.visible >= filtered.length;
    const clear = qs("[data-clear-filters]");
    if (clear) clear.hidden = (state.category === "all" || state.category === PAGE_CATEGORY) && !state.query;
    qsa("button[data-filter]").forEach(button => {
      const active = button.dataset.filter === state.category;
      button.classList.toggle("is-active", active);
      button.setAttribute("aria-pressed", String(active));
    });
  }

  function findProduct(id) { return PRODUCTS.find(item => item.id === String(id)); }

  function openProductDialog(id) {
    const item = findProduct(id);
    const dialog = qs("[data-product-dialog]");
    if (!item || !dialog) return;
    state.dialogProductId = item.id;
    const image = qs("[data-dialog-image]", dialog);
    image.src = item.image;
    image.alt = item.name;
    qs("[data-dialog-category]", dialog).textContent = `${CATEGORY_META[item.category].label} · Арт. ${item.article}`;
    qs("[data-dialog-name]", dialog).textContent = item.name;
    qs("[data-dialog-description]", dialog).textContent = item.description;
    qs("[data-dialog-price]", dialog).textContent = money(item.price);
    qs("[data-dialog-unit]", dialog).textContent = `Цена за ${item.unit}`;
    const tags = qsa(".product-dialog__tags span", dialog);
    if (tags[0]) tags[0].textContent = item.availability;
    if (tags[1]) tags[1].textContent = "Собственное производство";
    qs("[data-dialog-qty]", dialog).value = 1;
    dialog.showModal();
  }

  function toggleFavorite(id) {
    const item = findProduct(id);
    if (!item) return;
    if (state.favorites.has(id)) {
      state.favorites.delete(id);
      showToast(`${item.name}: убрано из избранного`);
    } else {
      state.favorites.add(id);
      showToast(`${item.name}: добавлено в избранное`);
    }
    writeStore(FAV_KEY, [...state.favorites]);
    renderFeatured();
    renderCatalog();
  }

  function addToCart(id, quantity = 1) {
    const item = findProduct(id);
    if (!item) return;
    state.cart[id] = (state.cart[id] || 0) + Number(quantity || 1);
    writeStore(CART_KEY, state.cart);
    updateCartUI();
    showToast(`${item.name} — добавлено в корзину`);
  }

  function setCartQuantity(id, quantity) {
    if (quantity <= 0) delete state.cart[id];
    else state.cart[id] = Math.min(99, quantity);
    writeStore(CART_KEY, state.cart);
    updateCartUI();
  }

  function cartLines() {
    return Object.entries(state.cart).map(([id, quantity]) => ({ item: findProduct(id), quantity })).filter(line => line.item && line.quantity > 0);
  }

  function updateCartUI() {
    const lines = cartLines();
    const count = lines.reduce((sum, line) => sum + line.quantity, 0);
    const total = lines.reduce((sum, line) => sum + line.item.price * line.quantity, 0);
    qsa("[data-cart-count]").forEach(node => node.textContent = count);
    const itemsNode = qs("[data-cart-items]");
    if (!itemsNode) return;
    itemsNode.innerHTML = lines.map(({ item, quantity }) => `
      <article class="cart-item">
        <div class="cart-item__image"><img src="${smallImage(item.image)}" alt="" width="82" height="82" decoding="async"></div>
        <div>
          <h3>${escapeHtml(item.name)}</h3>
          <span class="cart-item__meta">${CATEGORY_META[item.category].label} · за ${item.unit}</span>
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
      </article>`).join("");

    qs("[data-cart-empty]").hidden = lines.length > 0;
    qs("[data-cart-footer]").hidden = lines.length === 0;
    qs("[data-cart-total]").textContent = money(total);

    const remaining = Math.max(0, FREE_DELIVERY - total);
    const minimumRemaining = Math.max(0, MIN_ORDER - total);
    const percent = Math.min(100, total / FREE_DELIVERY * 100);
    qs("[data-progress-bar]").style.width = `${percent}%`;
    qs("[data-progress-label]").textContent = minimumRemaining ? "До минимальной суммы заказа" : remaining ? "До бесплатной доставки" : "Бесплатная доставка доступна";
    qs("[data-progress-value]").textContent = minimumRemaining ? money(minimumRemaining) : remaining ? money(remaining) : "Готово";
    const deliveryNode = qs("[data-cart-delivery]");
    if (deliveryNode) deliveryNode.textContent = total >= FREE_DELIVERY ? "Доставка: бесплатно" : `Доставка по Саратову: ${money(DELIVERY_FEE)} · самовывоз бесплатно`;
    const checkout = qs("[data-checkout]");
    if (checkout) checkout.textContent = minimumRemaining ? `Добавьте ещё ${money(minimumRemaining)}` : "Перейти к оформлению";
  }

  function orderSummaryText() {
    const lines = cartLines();
    const total = lines.reduce((sum, line) => sum + line.item.price * line.quantity, 0);
    return ["Заказ «Мир сладостей»", ...lines.map(({ item, quantity }) => `${item.name} — ${quantity} × ${money(item.price)}`), `Итого: ${money(total)}`].join("\n");
  }

  function updateOrderSummary() {
    const node = qs("[data-order-summary]");
    if (!node) return;
    const lines = cartLines();
    const total = lines.reduce((sum, line) => sum + line.item.price * line.quantity, 0);
    node.innerHTML = `<div>${lines.map(({ item, quantity }) => `<span>${escapeHtml(item.name)} × ${quantity}</span>`).join("")}</div><strong>${money(total)}</strong>`;
  }

  function openCart(trigger = null) {
    state.cartTrigger = trigger;
    qs("[data-cart-drawer]").classList.add("is-open");
    qs("[data-cart-drawer]").setAttribute("aria-hidden", "false");
    qsa("[data-open-cart]").forEach(button => button.setAttribute("aria-expanded", "true"));
    qs("[data-overlay]").classList.add("is-visible");
    document.body.classList.add("is-locked");
    window.setTimeout(() => qs("[data-close-cart]").focus(), 120);
  }

  function closeCart() {
    const trigger = state.cartTrigger;
    qs("[data-cart-drawer]").classList.remove("is-open");
    qs("[data-cart-drawer]").setAttribute("aria-hidden", "true");
    qsa("[data-open-cart]").forEach(button => button.setAttribute("aria-expanded", "false"));
    qs("[data-overlay]").classList.remove("is-visible");
    document.body.classList.remove("is-locked");
    state.cartTrigger = null;
    if (trigger) trigger.focus();
  }

  let toastTimer;
  function showToast(message) {
    const toast = qs("[data-toast]");
    toast.textContent = message;
    toast.classList.add("is-visible");
    clearTimeout(toastTimer);
    toastTimer = setTimeout(() => toast.classList.remove("is-visible"), 2600);
  }

  function setCategory(category) {
    state.category = category;
    state.visible = 12;
    renderCatalog();
  }

  function initEvents() {
    document.addEventListener("click", event => {
      const quick = event.target.closest("[data-quick-view]");
      if (quick) { openProductDialog(quick.dataset.quickView); return; }

      const add = event.target.closest("[data-add]");
      if (add) { addToCart(add.dataset.add); return; }

      const favorite = event.target.closest("[data-favorite]");
      if (favorite) { toggleFavorite(favorite.dataset.favorite); return; }

      const filter = event.target.closest("button[data-filter]");
      if (filter) { setCategory(filter.dataset.filter); return; }

      const plus = event.target.closest("[data-cart-plus]");
      if (plus) { setCartQuantity(plus.dataset.cartPlus, (state.cart[plus.dataset.cartPlus] || 0) + 1); return; }

      const minus = event.target.closest("[data-cart-minus]");
      if (minus) { setCartQuantity(minus.dataset.cartMinus, (state.cart[minus.dataset.cartMinus] || 0) - 1); return; }

      const remove = event.target.closest("[data-cart-remove]");
      if (remove) { setCartQuantity(remove.dataset.cartRemove, 0); return; }

      if (event.target.closest("[data-open-cart]")) { openCart(event.target.closest("[data-open-cart]")); return; }
      if (event.target.closest("[data-close-cart]") || event.target.matches("[data-overlay]")) { closeCart(); return; }

      if (event.target.closest("[data-cart-to-catalog]")) {
        closeCart();
        const grid = qs("#productGrid");
        if (grid) grid.scrollIntoView({ behavior: "smooth" });
        else window.location.href = "/catalog/";
        return;
      }

      if (event.target.closest("[data-checkout]")) {
        const total = cartLines().reduce((sum, line) => sum + line.item.price * line.quantity, 0);
        if (total < MIN_ORDER) { showToast(`Минимальная сумма заказа — ${money(MIN_ORDER)}`); return; }
        closeCart();
        updateOrderSummary();
        qs("[data-order-dialog]").showModal();
        return;
      }

      if (event.target.closest("[data-open-custom]")) {
        qs("[data-custom-dialog]").showModal();
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
    });

    const sort = qs("[data-catalog-sort]");
    if (sort) sort.addEventListener("change", event => {
      state.sort = event.target.value;
      renderCatalog();
    });

    const more = qs("[data-load-more]");
    if (more) more.addEventListener("click", () => {
      state.visible += 8;
      renderCatalog();
    });

    const clear = qs("[data-clear-filters]");
    if (clear) clear.addEventListener("click", () => {
      state.category = PAGE_CATEGORY || "all";
      state.query = "";
      state.visible = 12;
      const searchInput = qs("[data-catalog-search]");
      if (searchInput) searchInput.value = "";
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
      qsa("a", mobileMenu).forEach(link => link.addEventListener("click", () => {
        menuButton.setAttribute("aria-expanded", "false");
        mobileMenu.classList.remove("is-open");
      }));
    }

    const orderForm = qs("[data-order-form]");
    if (orderForm) orderForm.addEventListener("submit", event => {
      event.preventDefault();
      const formData = new FormData(event.currentTarget);
      const method = formData.get("delivery-method");
      const destination = method === "Доставка" ? `Адрес: ${formData.get("address")}` : `Самовывоз: ${formData.get("pickup")}`;
      const summary = `${orderSummaryText()}\n\nПолучатель: ${formData.get("name")}\nТелефон: ${formData.get("phone")}\nСпособ: ${method}\n${destination}\nДата: ${formData.get("date") || "уточнить"}\nОплата: ${formData.get("payment")}\nКомментарий: ${formData.get("comment") || "—"}`;
      if (navigator.clipboard?.writeText) navigator.clipboard.writeText(summary).catch(() => {});
      qs("[data-order-dialog]").close();
      showToast("Заказ подготовлен и скопирован — подтвердите его по телефону");
    });

    const customForm = qs("[data-custom-form]");
    if (customForm) customForm.addEventListener("submit", event => {
      event.preventDefault();
      const formData = new FormData(event.currentTarget);
      const summary = `Индивидуальный торт\nИмя: ${formData.get("name")}\nТелефон: ${formData.get("phone")}\nДата события: ${formData.get("date")}\nГостей: ${formData.get("guests")}\nПожелания: ${formData.get("idea")}\nРеференс: ${formData.get("reference") || "—"}`;
      if (navigator.clipboard?.writeText) navigator.clipboard.writeText(summary).catch(() => {});
      qs("[data-custom-dialog]").close();
      event.currentTarget.reset();
      showToast("Заявка подготовлена и скопирована — подтвердите её по телефону");
    });

    document.addEventListener("keydown", event => {
      if (event.key === "Escape" && qs("[data-cart-drawer]").classList.contains("is-open")) closeCart();
    });

    const method = qs("[data-delivery-method]");
    const syncDeliveryFields = () => {
      if (!method) return;
      const delivery = method.value === "Доставка";
      const address = qs("[data-address-field]");
      const pickup = qs("[data-pickup-field]");
      address.hidden = !delivery;
      pickup.hidden = delivery;
      qs("input", address).required = delivery;
      qs("select", pickup).required = !delivery;
    };
    if (method) { method.addEventListener("change", syncDeliveryFields); syncDeliveryFields(); }

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
    let scrollFrame = 0;
    const syncScrollState = () => {
      scrollFrame = 0;
      header.classList.toggle("is-scrolled", window.scrollY > 40);
      const scrollable = document.documentElement.scrollHeight - window.innerHeight;
      if (progress) progress.style.transform = `scaleX(${scrollable > 0 ? Math.min(1, window.scrollY / scrollable) : 0})`;
    };
    const scheduleScrollState = () => {
      if (!scrollFrame) scrollFrame = requestAnimationFrame(syncScrollState);
    };
    syncScrollState();
    window.addEventListener("scroll", scheduleScrollState, { passive: true });
    window.addEventListener("resize", scheduleScrollState, { passive: true });

    const reducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    const revealItems = qsa(".reveal:not(.is-visible)");
    if (reducedMotion || !("IntersectionObserver" in window)) {
      revealItems.forEach(item => item.classList.add("is-visible"));
    } else {
      const observer = new IntersectionObserver(entries => {
        entries.forEach(entry => {
          if (entry.isIntersecting) {
            entry.target.classList.add("is-visible");
            observer.unobserve(entry.target);
          }
        });
      }, { threshold: .08, rootMargin: "0px 0px -60px" });
      revealItems.forEach(item => observer.observe(item));
    }

    const revealHashTarget = () => {
      const target = location.hash ? document.getElementById(location.hash.slice(1)) : null;
      if (!target) return;
      if (target.matches(".reveal")) target.classList.add("is-visible");
      qsa(".reveal", target).forEach(item => item.classList.add("is-visible"));
    };
    revealHashTarget();
    window.addEventListener("hashchange", revealHashTarget);

    const hero = qs(".hero");
    if (hero && !reducedMotion && window.matchMedia("(pointer: fine)").matches) {
      hero.addEventListener("pointermove", event => {
        const x = (event.clientX / window.innerWidth - .5) * -10;
        const y = (event.clientY / window.innerHeight - .5) * -7;
        hero.style.setProperty("--hero-x", `${x}px`);
        hero.style.setProperty("--hero-y", `${y}px`);
      });
      hero.addEventListener("pointerleave", () => {
        hero.style.setProperty("--hero-x", "0px");
        hero.style.setProperty("--hero-y", "0px");
      });
    }
  }

  function init() {
    renderFeatured();
    renderCatalog();
    updateCartUI();
    initEvents();
    initMotion();
    qsa("[data-year]").forEach(node => node.textContent = new Date().getFullYear());
    const tomorrow = new Date(Date.now() + 86400000).toISOString().slice(0, 10);
    qsa('input[type="date"]').forEach(dateInput => dateInput.min = tomorrow);
  }

  init();
})();
