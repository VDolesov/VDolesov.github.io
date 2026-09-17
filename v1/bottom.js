(function () {
  "use strict";

  var API = "https://api-maps.yandex.ru/2.0/?load=package.full&mode=release&lang=ru-RU&wizard=bitrix";
  var MARKER = "data:image/svg+xml;charset=utf-8," + encodeURIComponent(
    '<svg xmlns="http://www.w3.org/2000/svg" width="34" height="44" viewBox="0 0 34 44">' +
    '<path fill="#c7a875" d="M17 43C17 43 3 27.6 3 17a14 14 0 0 1 28 0c0 10.6-14 26-14 26z"/>' +
    '<circle cx="17" cy="17" r="6" fill="#fff8ec"/></svg>');

  var timer;
  function toast(message) {
    var node = document.querySelector("[data-toast]");
    if (!node) return;
    node.textContent = message;
    node.classList.add("is-visible");
    clearTimeout(timer);
    timer = setTimeout(function () { node.classList.remove("is-visible"); }, 3200);
  }

  document.addEventListener("click", function (event) {
    var note = event.target.closest("[data-demo-note]");
    if (!note) return;
    event.preventDefault();
    toast(note.getAttribute("data-demo-note"));
  });

  var box = document.querySelector("[data-store-map]");
  if (!box) return;
  var stores = [].map.call(document.querySelectorAll("[data-store-list] .map-store"), function (el) {
    return {
      el: el,
      coords: el.getAttribute("data-coords").split(",").map(Number),
      title: el.querySelector(".map-store__title").textContent.trim(),
      phone: el.querySelector(".map-store__phone")
    };
  });

  function build() {
    var map = new ymaps.Map(box, { center: [51.565, 46.0], zoom: 11 }, { suppressMapOpenBlock: true });
    ["zoomControl", "typeSelector"].forEach(function (name) {
      try { map.controls.add(name); } catch (e) {}
    });
    stores.forEach(function (store) {
      var html = '<strong>' + store.title + '</strong>' +
        (store.phone ? '<br><a href="' + store.phone.getAttribute("href") + '">' + store.phone.textContent + '</a>' : '');
      store.mark = new ymaps.Placemark(store.coords, { hintContent: store.title, balloonContent: html }, {
        iconLayout: "default#image", iconImageHref: MARKER, iconImageSize: [34, 44], iconImageOffset: [-17, -44]
      });
      map.geoObjects.add(store.mark);
      store.el.querySelector(".map-store__title").addEventListener("click", function () {
        stores.forEach(function (s) { s.el.classList.toggle("is-active", s === store); });
        map.setCenter(store.coords, 16, { duration: 400 });
        if (store.mark.balloon && store.mark.balloon.open) store.mark.balloon.open();
      });
    });
    try {
      map.setBounds(map.geoObjects.getBounds(), { checkZoomRange: true, zoomMargin: 48 });
    } catch (e) {}
    var resized;
    window.addEventListener("resize", function () {
      clearTimeout(resized);
      resized = setTimeout(function () { map.container.fitToViewport(); }, 150);
    });
  }

  var loading = false;
  function load() {
    if (loading) return;
    loading = true;
    var script = document.createElement("script");
    script.src = API;
    script.onload = function () { ymaps.ready(build); };
    script.onerror = function () {
      box.innerHTML = '<div class="map-note">Карта не загрузилась. Адреса магазинов — в списке слева.</div>';
    };
    document.head.appendChild(script);
  }

  if ("IntersectionObserver" in window) {
    var watcher = new IntersectionObserver(function (entries) {
      if (!entries.some(function (e) { return e.isIntersecting; })) return;
      watcher.disconnect();
      load();
    }, { rootMargin: "600px 0px" });
    watcher.observe(box);
    setTimeout(load, 6000);
  } else {
    load();
  }
})();
