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

  function scan() {
    var maps = window.GLOBAL_arMapObjects;
    if (!maps) return;
    Object.keys(maps).forEach(function (id) {
      try { if (maps[id]) track(maps[id]); } catch (e) {}
    });
  }

  function start() {
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
