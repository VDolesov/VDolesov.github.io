(function () {
  "use strict";

  function keyboard(el) {
    try { return el.matches(":focus-visible"); } catch (e) { return true; }
  }

  function setOpen(block, open) {
    block.classList.toggle("ms-share-open", open);
    var icon = block.querySelector("[data-ms-share-toggle]");
    if (icon) icon.setAttribute("aria-expanded", open ? "true" : "false");
  }

  function menus() {
    document.querySelectorAll(".share .shares-block").forEach(function (block) {
      if (block.hasAttribute("data-ms-share-menu") || !block.querySelector(".ms-share")) return;
      var icon = block.querySelector(":scope > .svg");
      if (!icon) return;
      block.setAttribute("data-ms-share-menu", "");
      icon.setAttribute("data-ms-share-toggle", "");
      icon.removeAttribute("aria-hidden");
      icon.setAttribute("role", "button");
      icon.setAttribute("aria-label", "Поделиться");
      icon.setAttribute("aria-expanded", "false");
      icon.tabIndex = 0;
      block.addEventListener("focusin", function (e) {
        var hold = block.__msHold;
        block.__msHold = false;
        if (!hold && keyboard(e.target)) setOpen(block, true);
      });
      block.addEventListener("focusout", function (e) {
        if (!block.contains(e.relatedTarget)) setOpen(block, false);
      });
      block.addEventListener("keydown", function (e) {
        if ((e.key === "Enter" || e.key === " ") && e.target === icon) {
          e.preventDefault();
          setOpen(block, true);
          var first = block.querySelector(".ms-share .ya-share2__link");
          if (first) first.focus();
        } else if (e.key === "Escape" && block.classList.contains("ms-share-open")) {
          setOpen(block, false);
          if (e.target !== icon) {
            block.__msHold = true;
            icon.focus();
          }
        }
      });
    });
  }

  function fallbackCopy(text) {
    var area = document.createElement("textarea");
    area.value = text;
    area.setAttribute("readonly", "");
    area.style.position = "fixed";
    area.style.opacity = "0";
    document.body.appendChild(area);
    area.select();
    var ok = false;
    try { ok = document.execCommand("copy"); } catch (e) {}
    document.body.removeChild(area);
    return ok;
  }

  function say(button, text) {
    var box = button.closest(".ms-share");
    var status = box && box.querySelector(".ms-share__status");
    if (!status) return;
    status.textContent = text;
    clearTimeout(status.__msTimer);
    status.__msTimer = setTimeout(function () { status.textContent = ""; }, 2500);
  }

  function copy(e) {
    var button = e.target && e.target.closest ? e.target.closest("[data-ms-share-copy]") : null;
    if (!button) return;
    e.preventDefault();
    var url = location.href.split("#")[0];
    var done = function () { say(button, "Ссылка скопирована"); };
    var failed = function () { say(button, fallbackCopy(url) ? "Ссылка скопирована" : url); };
    if (navigator.clipboard && navigator.clipboard.writeText) {
      navigator.clipboard.writeText(url).then(done, failed);
    } else {
      failed();
    }
  }

  function start() {
    menus();
    document.addEventListener("click", copy);
  }

  if (document.readyState !== "loading") start(); else document.addEventListener("DOMContentLoaded", start);
})();
