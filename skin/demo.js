(function () {
  "use strict";

  var PRODUCTS = window.MS_PRODUCTS || {};
  var PHONE = "+7 (8452) 47-35-69";
  var PHONE2 = "+7 (8452) 21-28-45";
  var MAIL = "mirslad49@mail.ru";

  var NOTES = {
    auth: ["Личный кабинет",
      "На рабочем сайте здесь вход и регистрация: история заказов, адреса, бонусы. В демо-версии заказ оформляется без регистрации — через корзину."],
    callback: ["Заказать звонок",
      "На рабочем сайте форма отправляет номер менеджеру, и он перезванивает. В демо-версии формы не отправляются — позвоните нам напрямую."],
    subscribe: ["Подписка на рассылку",
      "На рабочем сайте здесь подписка на новости и акции. В демо-версии формы не отправляются."],
    question: ["Задать вопрос",
      "На рабочем сайте вопрос уходит менеджеру. В демо-версии формы не отправляются — напишите нам на почту или позвоните."],
    ask: ["Задать вопрос",
      "На рабочем сайте вопрос уходит менеджеру. В демо-версии формы не отправляются — напишите нам на почту или позвоните."],
    contacts: ["Контакты",
      "г. Саратов, ул. Бахметьевская, 49. Магазины: ТЦ «Солнечный», ул. Тархова 29А/1 и кулинария на кольце НИИ."],
    form: ["Форма",
      "На рабочем сайте эта форма отправляется на сервер. В демо-версии формы не отправляются — позвоните или напишите нам."]
  };

  function esc(s) {
    return String(s).replace(/[&<>"]/g, function (c) {
      return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c];
    });
  }
  function tel(s) { return "tel:" + s.replace(/[^\d+]/g, ""); }

  function modal(kind) {
    var note = NOTES[kind] || NOTES.callback;
    close();
    var box = document.createElement("div");
    box.className = "ms-modal";
    box.innerHTML = '<div class="ms-modal__back" data-close></div>' +
      '<div class="ms-modal__box" role="dialog" aria-modal="true">' +
        '<button type="button" class="ms-modal__close" data-close aria-label="Закрыть">&times;</button>' +
        '<div class="ms-modal__label">Демо-версия</div>' +
        '<h3 class="ms-modal__title">' + esc(note[0]) + '</h3>' +
        '<p class="ms-modal__text">' + esc(note[1]) + '</p>' +
        '<div class="ms-modal__contacts">' +
          '<a href="' + tel(PHONE) + '">' + PHONE + '</a>' +
          '<a href="' + tel(PHONE2) + '">' + PHONE2 + '</a>' +
          '<a href="mailto:' + MAIL + '">' + MAIL + '</a>' +
        '</div>' +
        (kind === "auth" ? '<a class="btn btn-default btn-lg ms-modal__btn" href="/basket/">Перейти в корзину</a>' : '') +
      '</div>';
    document.body.appendChild(box);
    document.body.classList.add("ms-modal-open");
    setTimeout(function () { box.classList.add("is-on"); }, 20);
    box.addEventListener("click", function (e) { if (e.target.closest("[data-close]")) close(); });
  }
  function close() {
    var old = document.querySelector(".ms-modal");
    if (old) old.parentNode.removeChild(old);
    document.body.classList.remove("ms-modal-open");
  }
  document.addEventListener("keydown", function (e) { if (e.key === "Escape") close(); });

  document.addEventListener("click", function (e) {
    var t = e.target.closest ? e.target.closest('[data-event="jqm"], a[href="/auth/"], .personal-link') : null;
    if (!t) return;
    var name = (t.getAttribute("data-name") || t.getAttribute("data-param-type") || "").toLowerCase();
    if (name === "fast_view") {
      var id = t.getAttribute("data-param-id");
      if (id && PRODUCTS[id]) {
        e.preventDefault(); e.stopImmediatePropagation();
        location.href = PRODUCTS[id].url;
      }
      return;
    }
    e.preventDefault(); e.stopImmediatePropagation();
    if (!name && (t.getAttribute("href") === "/auth/" || t.classList.contains("personal-link"))) name = "auth";
    modal(NOTES[name] ? name : "callback");
  }, true);

  document.addEventListener("submit", function (e) {
    var form = e.target;
    if (!form || form.classList.contains("ms-form") || form.classList.contains("ms-search")) return;
    if (form.querySelector('input[name="q"]')) return;
    e.preventDefault(); e.stopImmediatePropagation();
    modal("form");
  }, true);

  if (window.arMaxOptions && arMaxOptions.THEME) {
    arMaxOptions.THEME.BIGBANNER_ANIMATIONTYPE = "FADE";
    arMaxOptions.THEME.BIGBANNER_ANIMATIONSPEED = "900";
    arMaxOptions.THEME.BIGBANNER_SLIDESSHOWSPEED = window.innerWidth < 768 ? "0" : "8000";
  }

  function absolute(files) {
    return [].concat(files).map(function (f) {
      return typeof f === "string" && /^\/(bitrix|local|upload)\//.test(f) ? "https://www.mirsladostey164.ru" + f : f;
    });
  }
  if (window.BX) {
    ["loadCSS", "loadScript", "load"].forEach(function (name) {
      var orig = BX[name];
      if (typeof orig !== "function") return;
      BX[name] = function (files) {
        arguments[0] = absolute(files);
        return orig.apply(this, arguments);
      };
    });
  }

  function authPage() {
    if (!/^\/auth\/?$/.test(location.pathname)) return;
    var container = document.querySelector(".wrapper_inner .container_inner .middle > .container");
    if (!container) return;
    container.innerHTML = '<div class="maxwidth-theme"><div class="ms-empty">' +
      '<div class="ms-empty__title">Личный кабинет</div>' +
      '<p class="ms-empty__text">' + esc(NOTES.auth[1]) + '</p>' +
      '<a class="btn btn-default btn-lg" href="/catalog/">Перейти в каталог</a></div></div>';
  }

  function ready(fn) {
    if (document.readyState !== "loading") fn(); else document.addEventListener("DOMContentLoaded", fn);
  }
  ready(authPage);
})();
