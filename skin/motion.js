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

  var FINE = window.matchMedia && window.matchMedia("(hover: hover) and (pointer: fine)").matches;

  function heroParallax() {
    var wrap = document.querySelector(".top_slider_wrapp");
    if (!wrap || wrap.classList.contains("ms-parallax") || !FINE || window.innerWidth < 768) return;
    var slides = wrap.querySelectorAll(".slides > li.box");
    if (!slides.length) return;
    var layers = [], copies = [];
    for (var i = 0; i < slides.length; i++) {
      var li = slides[i];
      var src = li.getAttribute("data-bg") || li.getAttribute("data-src");
      if (!src) {
        var m = /url\((['"]?)(.*?)\1\)/.exec(li.style.backgroundImage || "");
        src = m && m[2];
      }
      if (!src) continue;
      var par = document.createElement("div");
      par.className = "ms-hero-par";
      par.innerHTML = '<div class="ms-hero-bg"></div>';
      par.firstChild.style.backgroundImage = "url(" + src + ")";
      li.insertBefore(par, li.firstChild);
      layers.push(par);
      var copy = li.querySelector(".wrapper_inner");
      if (copy) copies.push(copy);
    }
    if (!layers.length) return;
    wrap.classList.add("ms-parallax");

    var tx = 0, ty = 0, cx = 0, cy = 0, raf = null;
    function frame() {
      cx += (tx - cx) * .09;
      cy += (ty - cy) * .09;
      var bg = "translate3d(" + (-cx * 26).toFixed(2) + "px," + (-cy * 16).toFixed(2) + "px,0)";
      var fg = "translate3d(" + (cx * 12).toFixed(2) + "px," + (cy * 8).toFixed(2) + "px,0)";
      for (var i = 0; i < layers.length; i++) layers[i].style.transform = bg;
      for (var j = 0; j < copies.length; j++) copies[j].style.transform = fg;
      raf = Math.abs(tx - cx) + Math.abs(ty - cy) > .002 ? requestAnimationFrame(frame) : null;
    }
    function kick() { if (!raf) raf = requestAnimationFrame(frame); }

    wrap.addEventListener("mousemove", function (e) {
      var box = wrap.getBoundingClientRect();
      tx = (e.clientX - box.left) / box.width - .5;
      ty = (e.clientY - box.top) / box.height - .5;
      kick();
    });
    wrap.addEventListener("mouseleave", function () {
      tx = 0; ty = 0;
      kick();
    });
  }

  function ready(fn) {
    if (document.readyState !== "loading") fn(); else document.addEventListener("DOMContentLoaded", fn);
  }
  ready(function () {
    heroParallax();
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
