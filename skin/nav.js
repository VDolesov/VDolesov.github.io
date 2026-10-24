(function () {
  var SECTIONS = window.MS_SECTIONS || [];
  var EXTRA = [{ url: "/sale/", name: "Акции" }, { url: "/contacts/", name: "Контакты" }];

  function build() {
    if (!SECTIONS.length || document.querySelector(".ms-nav")) return;
    var host = document.querySelector(".header_wrap .logo-row") || document.querySelector(".header-wrapper .logo-row");
    if (!host) return;
    var path = location.pathname;
    var nav = document.createElement("nav");
    nav.className = "ms-nav";
    var inner = document.createElement("div");
    inner.className = "ms-nav__inner";
    SECTIONS.concat(EXTRA).forEach(function (s) {
      var a = document.createElement("a");
      a.href = s.url || ("/catalog/" + s.slug + "/");
      a.textContent = s.name;
      if (path.indexOf(a.getAttribute("href")) === 0) a.className = "is-current";
      inner.appendChild(a);
    });
    nav.appendChild(inner);
    host.parentNode.insertBefore(nav, host.nextSibling);
    if (window.ResizeObserver) {
      var observer = new ResizeObserver(positionBasket);
      observer.observe(nav);
      observer.observe(host);
    }
    positionBasket();
  }

  function positionBasket() {
    var nav = document.querySelector(".ms-nav");
    var top = 148;
    if (nav && window.matchMedia("(min-width: 992px)").matches) {
      top = Math.max(top, Math.ceil(nav.getBoundingClientRect().bottom) + 8);
    }
    document.documentElement.style.setProperty("--ms-basket-opener-top", top + "px");
  }

  function trackScroll() {
    var root = document.documentElement;
    var update = function () {
      root.classList.toggle("ms-scrolled", window.pageYOffset > 8);
      positionBasket();
    };
    window.addEventListener("scroll", update, { passive: true });
    window.addEventListener("resize", positionBasket);
    update();
  }

  if (document.readyState !== "loading") build(); else document.addEventListener("DOMContentLoaded", build);
  trackScroll();
})();
