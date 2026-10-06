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

  if (document.readyState !== "loading") start(); else document.addEventListener("DOMContentLoaded", start);
})();
