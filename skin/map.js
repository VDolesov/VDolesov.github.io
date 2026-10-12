(function () {
  "use strict";

  var PHOTO_TYPES = ["yandex#satellite", "yandex#hybrid", "yandex#publicMapHybrid"];

  function track(map) {
    var node = map.container && map.container.getElement && map.container.getElement();
    if (!node || node.hasAttribute("data-ms-map")) return;
    node.setAttribute("data-ms-map", "1");
    function apply() {
      var type = map.getType && map.getType();
      var name = typeof type === "string" ? type : "";
      node.classList.toggle("ms-map-photo", PHOTO_TYPES.indexOf(name) !== -1);
    }
    map.events.add("typechange", apply);
    apply();
  }

  function hintOf(text) {
    if (!text) return "";
    var box = document.createElement("div");
    box.innerHTML = String(text);
    var head = box.querySelector(".title") || box.firstElementChild;
    return (head ? head.textContent : box.textContent).replace(/\s+/g, " ").trim();
  }

  var tip = null;
  var pointer = null;

  function place() {
    if (!tip || !pointer || tip.parentNode !== pointer.node) return;
    tip.style.left = pointer.x + "px";
    tip.style.top = pointer.y + "px";
  }

  function hideTip() {
    if (tip) tip.hidden = true;
  }

  function trackPointer(node) {
    if (node.hasAttribute("data-ms-pointer")) return;
    node.setAttribute("data-ms-pointer", "1");
    if (getComputedStyle(node).position === "static") node.style.position = "relative";
    node.addEventListener("mousemove", function (e) {
      var rect = node.getBoundingClientRect();
      pointer = { node: node, x: e.clientX - rect.left, y: e.clientY - rect.top };
      if (tip && !tip.hidden) place();
    });
    node.addEventListener("mouseleave", hideTip);
  }

  function showTip(mark, text) {
    var map = mark.getMap && mark.getMap();
    var node = map && map.container && map.container.getElement && map.container.getElement();
    if (!node) return;
    trackPointer(node);
    if (!tip) {
      tip = document.createElement("div");
      tip.className = "ms-map-tip";
      tip.setAttribute("role", "tooltip");
    }
    if (tip.parentNode !== node) node.appendChild(tip);
    tip.textContent = text;
    tip.hidden = false;
    place();
  }

  function enhance(mark) {
    if (!mark || !mark.properties || !mark.events || mark.__msHint) return;
    mark.__msHint = true;
    var text = hintOf(mark.properties.get("balloonContent"));
    if (!text) return;
    mark.events.add("mouseenter", function () { showTip(mark, text); });
    mark.events.add(["mouseleave", "click"], hideTip);
  }

  function hints(object) {
    if (!object) return;
    if (object.properties && object.properties.get && object.geometry) {
      enhance(object);
      return;
    }
    if (object.each) object.each(hints);
  }

  function wrapPlacemarks() {
    var original = window.BX_YMapAddPlacemark;
    if (typeof original !== "function" || original.__msWrapped) return;
    var wrapped = function () {
      var mark = original.apply(this, arguments);
      try { enhance(mark); } catch (e) {}
      return mark;
    };
    wrapped.__msWrapped = true;
    window.BX_YMapAddPlacemark = wrapped;
  }

  function scan() {
    wrapPlacemarks();
    var maps = window.GLOBAL_arMapObjects;
    if (!maps) return;
    Object.keys(maps).forEach(function (id) {
      try {
        if (maps[id]) {
          track(maps[id]);
          hints(maps[id].geoObjects);
        }
      } catch (e) {}
    });
  }

  function start() {
    wrapPlacemarks();
    var tries = 0;
    var timer = setInterval(function () {
      scan();
      if (++tries > 60) clearInterval(timer);
    }, 500);
  }

  function lazyApi() {
    var url = window.MS_YMAPS_URL;
    var nodes = document.querySelectorAll(".bx-yandex-map");
    if (!url || window.ymaps || !nodes.length) return;
    var loaded = false;
    var load = function () {
      if (loaded) return;
      loaded = true;
      var script = document.createElement("script");
      script.src = url;
      document.head.appendChild(script);
      start();
    };
    if (!("IntersectionObserver" in window)) return load();
    var observer = new IntersectionObserver(function (entries) {
      for (var i = 0; i < entries.length; i++) {
        if (entries[i].isIntersecting) {
          observer.disconnect();
          load();
          return;
        }
      }
    }, { rootMargin: "600px 0px" });
    Array.prototype.forEach.call(nodes, function (node) { observer.observe(node); });
  }

  function init() {
    lazyApi();
    start();
  }

  if (document.readyState !== "loading") init(); else document.addEventListener("DOMContentLoaded", init);
})();
