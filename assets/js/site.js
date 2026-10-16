/* Jack Albert Weddings — site interactions */
(function () {
  "use strict";

  var doc = document.documentElement;
  var body = document.body;
  var reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  var isSmall = window.matchMedia("(max-width: 860px)").matches;

  /* ---------- intro curtain: once per session ---------- */
  var seen = false;
  try { seen = sessionStorage.getItem("jaw-intro") === "1"; sessionStorage.setItem("jaw-intro", "1"); } catch (e) {}
  if (seen || reduceMotion) body.classList.add("no-curtain");
  function loaded() { body.classList.add("is-loaded"); }
  if (seen || reduceMotion) requestAnimationFrame(loaded);
  else window.setTimeout(loaded, 900);

  /* ---------- header behaviour ---------- */
  var header = document.querySelector(".site-header");
  var hero = document.querySelector("[data-hero]");
  var lastY = window.scrollY;
  var mobileCta = document.querySelector(".mobile-cta");
  function onScroll() {
    var y = window.scrollY;
    var heroH = hero ? hero.offsetHeight - 80 : 0;
    if (header) {
      header.classList.toggle("is-over-hero", !!hero && y < heroH);
      header.classList.toggle("is-scrolled", y > 24 && (!hero || y >= heroH));
      var hide = y > 400 && y > lastY && !body.classList.contains("menu-open");
      header.classList.toggle("is-hidden", hide);
    }
    if (mobileCta) mobileCta.classList.toggle("is-visible", y > window.innerHeight * 0.6);
    lastY = y;
  }
  window.addEventListener("scroll", onScroll, { passive: true });
  onScroll();

  /* ---------- mobile menu ---------- */
  var toggle = document.querySelector(".menu-toggle");
  var menu = document.getElementById("mobile-menu");
  function setMenu(open) {
    body.classList.toggle("menu-open", open);
    if (toggle) {
      toggle.setAttribute("aria-expanded", open ? "true" : "false");
      toggle.setAttribute("aria-label", open ? "Close menu" : "Open menu");
    }
    if (menu) menu.setAttribute("aria-hidden", open ? "false" : "true");
    if (open && header) header.classList.remove("is-hidden");
  }
  if (toggle) toggle.addEventListener("click", function () { setMenu(!body.classList.contains("menu-open")); });
  if (menu) menu.addEventListener("click", function (e) { if (e.target.closest("a")) setMenu(false); });
  document.addEventListener("keydown", function (e) { if (e.key === "Escape") setMenu(false); });
  window.addEventListener("resize", function () { if (window.innerWidth > 1100) setMenu(false); });

  /* ---------- hero video: right file for the screen, fade in once playing ---------- */
  document.querySelectorAll("video[data-src-desktop]").forEach(function (v) {
    if (reduceMotion) return;
    var src = isSmall && v.dataset.srcMobile ? v.dataset.srcMobile : v.dataset.srcDesktop;
    v.src = src;
    v.addEventListener("playing", function () { v.classList.add("is-playing"); }, { once: true });
    var p = v.play(); if (p && p.catch) p.catch(function () {});
  });

  /* ---------- lazy autoplay loops (pause when off-screen) ---------- */
  var loops = document.querySelectorAll("video[data-loop]");
  if ("IntersectionObserver" in window && !reduceMotion) {
    var vo = new IntersectionObserver(function (entries) {
      entries.forEach(function (en) {
        var v = en.target;
        if (en.isIntersecting) {
          if (!v.src && v.dataset.src) v.src = v.dataset.src;
          v.addEventListener("playing", function () { v.classList.add("is-playing"); }, { once: true });
          var p = v.play(); if (p && p.catch) p.catch(function () {});
        } else if (!v.paused) v.pause();
      });
    }, { rootMargin: "200px 0px", threshold: 0.01 });
    loops.forEach(function (v) { vo.observe(v); });
  }

  /* ---------- film tiles: hover preview on desktop ---------- */
  var canHover = window.matchMedia("(hover: hover)").matches;
  document.querySelectorAll(".film[data-preview]").forEach(function (f) {
    if (!canHover || reduceMotion) return;
    var v = f.querySelector("video");
    if (!v) return;
    f.addEventListener("mouseenter", function () {
      if (!v.src) v.src = f.dataset.preview;
      f.classList.add("is-previewing");
      var p = v.play(); if (p && p.catch) p.catch(function () {});
    });
    f.addEventListener("mouseleave", function () { f.classList.remove("is-previewing"); v.pause(); });
  });

  /* ---------- video modal (YouTube, privacy-enhanced) ---------- */
  var modal = document.getElementById("film-modal");
  var lastFocus = null;
  function openFilm(id, title) {
    if (!modal) return;
    lastFocus = document.activeElement;
    modal.querySelector(".modal__frame").innerHTML =
      '<iframe src="https://www.youtube-nocookie.com/embed/' + encodeURIComponent(id) +
      '?autoplay=1&rel=0&modestbranding=1&playsinline=1" title="' + (title || "Wedding film").replace(/"/g, "") +
      '" allow="autoplay; encrypted-media; picture-in-picture; fullscreen" allowfullscreen></iframe>';
    modal.querySelector(".modal__title").textContent = title || "";
    modal.classList.add("is-open");
    modal.setAttribute("aria-hidden", "false");
    body.style.overflow = "hidden";
    modal.querySelector(".modal__close").focus();
  }
  function closeFilm() {
    if (!modal || !modal.classList.contains("is-open")) return;
    modal.classList.remove("is-open");
    modal.setAttribute("aria-hidden", "true");
    body.style.overflow = "";
    window.setTimeout(function () { modal.querySelector(".modal__frame").innerHTML = ""; }, 500);
    if (lastFocus) lastFocus.focus();
  }
  document.addEventListener("click", function (e) {
    var t = e.target.closest("[data-yt]");
    if (t) { e.preventDefault(); openFilm(t.dataset.yt, t.dataset.title); }
  });
  if (modal) {
    modal.addEventListener("click", function (e) { if (e.target === modal || e.target.closest(".modal__close")) closeFilm(); });
    document.addEventListener("keydown", function (e) { if (e.key === "Escape") closeFilm(); });
  }

  /* ---------- scroll reveals ---------- */
  var revealEls = document.querySelectorAll(".reveal, .reveal-img");
  if ("IntersectionObserver" in window && !reduceMotion) {
    var ro = new IntersectionObserver(function (entries) {
      entries.forEach(function (en) {
        if (en.isIntersecting) { en.target.classList.add("is-visible"); ro.unobserve(en.target); }
      });
    }, { rootMargin: "0px 0px -8% 0px", threshold: 0.08 });
    revealEls.forEach(function (el) { ro.observe(el); });
  } else {
    revealEls.forEach(function (el) { el.classList.add("is-visible"); });
  }

  /* ---------- subtle parallax on marked media (desktop only) ---------- */
  var para = document.querySelectorAll("[data-parallax]");
  if (para.length && !reduceMotion && !isSmall) {
    var ticking = false;
    var run = function () {
      ticking = false;
      var vh = window.innerHeight;
      para.forEach(function (el) {
        var r = el.parentElement.getBoundingClientRect();
        if (r.bottom < 0 || r.top > vh) return;
        var p = (r.top + r.height / 2 - vh / 2) / vh;
        el.style.transform = "translate3d(0," + (p * -parseFloat(el.dataset.parallax || 60)).toFixed(1) + "px,0) scale(1.12)";
      });
    };
    window.addEventListener("scroll", function () { if (!ticking) { ticking = true; requestAnimationFrame(run); } }, { passive: true });
    run();
  }

  /* ---------- testimonials ---------- */
  document.querySelectorAll("[data-reviews]").forEach(function (wrap) {
    var items = wrap.querySelectorAll(".review");
    var dotsWrap = wrap.querySelector(".reviews__dots");
    if (!items.length || !dotsWrap) return;
    var i = 0, timer = null;
    var dots = [];
    items.forEach(function (_, n) {
      var b = document.createElement("button");
      b.type = "button";
      b.setAttribute("aria-label", "Show review " + (n + 1));
      b.addEventListener("click", function () { go(n, true); });
      dotsWrap.appendChild(b);
      dots.push(b);
    });
    function go(n, user) {
      i = (n + items.length) % items.length;
      items.forEach(function (it, k) { it.classList.toggle("is-active", k === i); it.setAttribute("aria-hidden", k === i ? "false" : "true"); });
      dots.forEach(function (d, k) { d.classList.remove("is-active"); if (k === i) { void d.offsetWidth; d.classList.add("is-active"); } });
      if (user) restart();
    }
    function restart() { window.clearInterval(timer); if (!reduceMotion) timer = window.setInterval(function () { go(i + 1); }, 7000); }
    var prev = wrap.querySelector(".reviews__arrow--prev");
    var next = wrap.querySelector(".reviews__arrow--next");
    if (prev) prev.addEventListener("click", function () { go(i - 1, true); });
    if (next) next.addEventListener("click", function () { go(i + 1, true); });
    var sx = null;
    wrap.addEventListener("touchstart", function (e) { sx = e.touches[0].clientX; }, { passive: true });
    wrap.addEventListener("touchend", function (e) {
      if (sx === null) return;
      var dx = e.changedTouches[0].clientX - sx;
      if (Math.abs(dx) > 40) go(dx < 0 ? i + 1 : i - 1, true);
      sx = null;
    });
    go(0); restart();
  });

  /* ---------- journal filter ---------- */
  var filter = document.querySelector("[data-filter]");
  if (filter) {
    filter.addEventListener("click", function (e) {
      var b = e.target.closest("button[data-cat]");
      if (!b) return;
      filter.querySelectorAll("button").forEach(function (x) { x.classList.toggle("is-active", x === b); x.setAttribute("aria-pressed", x === b ? "true" : "false"); });
      var cat = b.dataset.cat;
      document.querySelectorAll(".post-card[data-cat]").forEach(function (c) {
        c.hidden = !(cat === "all" || c.dataset.cat === cat);
      });
    });
  }

  /* ---------- collection preselect from URL (?collection=classic-collection) ---------- */
  var form = document.getElementById("inquiry-form");
  if (form) {
    var params = new URLSearchParams(window.location.search);
    var pick = params.get("collection");
    if (pick) {
      var r = form.querySelector('input[name="collection"][value="' + pick.replace(/[^a-z-]/g, "") + '"]');
      if (r) r.checked = true;
    }
    var date = form.querySelector('input[type="date"]');
    if (date) date.min = new Date().toISOString().slice(0, 10);

    form.addEventListener("submit", function (e) {
      e.preventDefault();
      var status = form.querySelector(".form__status");
      var btn = form.querySelector('button[type="submit"]');
      if (!form.checkValidity()) { form.reportValidity(); return; }
      if (status) status.textContent = "";
      btn.disabled = true;
      var label = btn.querySelector(".label");
      var original = label ? label.textContent : "";
      if (label) label.textContent = "Sending…";
      fetch(form.action, { method: "POST", body: new FormData(form), headers: { Accept: "application/json" } })
        .then(function (res) {
          if (!res.ok) throw new Error("bad");
          var wrap = form.closest(".form-wrap");
          if (wrap) wrap.classList.add("is-sent");
          if (window.fbq) window.fbq("track", "Lead");
          window.scrollTo({ top: (wrap || form).getBoundingClientRect().top + window.scrollY - 120, behavior: "smooth" });
        })
        .catch(function () {
          if (status) status.innerHTML = 'Something went wrong sending your inquiry. Please try again, or email <a class="text-link" href="mailto:jack@jackalbertweddings.ca">jack@jackalbertweddings.ca</a>.';
        })
        .then(function () { btn.disabled = false; if (label) label.textContent = original; });
    });
  }

  /* ---------- year ---------- */
  document.querySelectorAll("[data-year]").forEach(function (el) { el.textContent = new Date().getFullYear(); });
})();
