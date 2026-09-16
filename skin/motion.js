(function () {
  "use strict";

  if (!("IntersectionObserver" in window)) return;
  if (window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches) return;

  var GROUPS = [
    ".cat_sections .owl-item",
    ".catalog_section_list .item_block",
    ".catalog_block .item_block, .CATALOG_TAB .catalog_item",
    ".ms-grid .ms-card",
    ".COMPANY_TEXT .company-block",
    ".TIZERS .item, .TIZERS .tizers_block .item",
    ".MAPS .wrapper_block",
    ".content_wrapper_block .top_block h3, .CATALOG_SECTIONS .sections_wrapper",
    ".product-container .product-detail-gallery, .product-container .info_item, .product-container .bottom-info"
  ];

  var observer = new IntersectionObserver(function (entries) {
    entries.forEach(function (entry) {
      if (!entry.isIntersecting) return;
      entry.target.classList.add("is-in");
      observer.unobserve(entry.target);
    });
  }, { rootMargin: "0px 0px -8% 0px", threshold: 0.08 });

  function prepare(root) {
    var fresh = [];
    GROUPS.forEach(function (selector) {
      var nodes = root.querySelectorAll(selector);
      for (var i = 0; i < nodes.length; i++) {
        var el = nodes[i];
        if (el.classList.contains("ms-reveal")) continue;
        var index = 0, sib = el.previousElementSibling;
        while (sib && index < 5) { index++; sib = sib.previousElementSibling; }
        el.classList.add("ms-reveal");
        if (index) el.classList.add("ms-reveal--" + (index + 1));
        fresh.push(el);
      }
    });
    if (!fresh.length) return;
    void document.body.offsetWidth;
    var vh = window.innerHeight;
    fresh.forEach(function (el) {
      var box = el.getBoundingClientRect();
      if (box.top < vh && box.bottom > 0) el.classList.add("is-in");
      else observer.observe(el);
    });
    setTimeout(function () {
      fresh.forEach(function (el) { el.classList.add("is-in"); observer.unobserve(el); });
    }, 8000);
  }

  function ready(fn) {
    if (document.readyState !== "loading") fn(); else document.addEventListener("DOMContentLoaded", fn);
  }
  ready(function () {
    prepare(document);
    var pending = null;
    new MutationObserver(function () {
      clearTimeout(pending);
      pending = setTimeout(function () { prepare(document); }, 80);
    }).observe(document.body, { childList: true, subtree: true });
  });

  var counters = document.querySelectorAll(".basket_fly .opener .count span.colored_theme_bg");
  for (var i = 0; i < counters.length; i++) {
    new MutationObserver((function (node) {
      return function () {
        node.classList.remove("ms-pop");
        void node.offsetWidth;
        node.classList.add("ms-pop");
      };
    })(counters[i])).observe(counters[i], { childList: true, subtree: true, characterData: true });
  }
})();
