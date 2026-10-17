/* Jack Albert Weddings — site interactions (v2)
   No framework, native scrolling. Scroll effects only run while the page moves. */
(function () {
  "use strict";

  var doc = document.documentElement;
  var body = document.body;
  var reduce = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  var small = window.matchMedia("(max-width: 860px)").matches;
  var fine = window.matchMedia("(hover: hover) and (pointer: fine)").matches;
  var CAL = body.dataset.calUrl;
  var track = function (ev, data) { try { if (window.fbq) window.fbq("track", ev, data || {}); } catch (e) {} };
  var store = {
    get: function (k) { try { return sessionStorage.getItem(k); } catch (e) { return null; } },
    set: function (k, v) { try { sessionStorage.setItem(k, v); } catch (e) {} },
    lget: function (k) { try { return localStorage.getItem(k); } catch (e) { return null; } },
    lset: function (k, v) { try { localStorage.setItem(k, v); } catch (e) {} },
    ldel: function (k) { try { localStorage.removeItem(k); } catch (e) {} }
  };
  var clamp = function (v, a, b) { return Math.min(b, Math.max(a, v)); };

  /* ======================================================================
     Intro: film-leader countdown (first visit) / curtain (page changes)
     ====================================================================== */
  var loader = document.querySelector(".loader");
  var curtain = document.querySelector(".curtain");
  function loaded() { body.classList.add("is-loaded"); }

  if (doc.classList.contains("no-loader") || !loader || reduce) {
    if (curtain && store.get("jaw-trans") === "1") {
      curtain.classList.add("is-cover");
      requestAnimationFrame(function () {
        requestAnimationFrame(function () { curtain.classList.remove("is-cover"); curtain.classList.add("is-out"); loaded(); });
      });
      store.set("jaw-trans", "0");
    } else { requestAnimationFrame(loaded); }
  } else {
    store.set("jaw-intro", "1");
    var num = loader.querySelector(".leader__num");
    var sweep = loader.querySelector(".leader__sweep");
    var start = null, dur = 1800;
    var tick = function (t) {
      if (!start) start = t;
      var e = t - start;
      var n = Math.max(1, 3 - Math.floor(e / (dur / 3)));
      if (num.textContent !== String(n)) num.textContent = n;
      sweep.style.setProperty("--p", ((e % (dur / 3)) / (dur / 3) * 360) + "deg");
      if (e < dur) requestAnimationFrame(tick);
      else { loader.classList.add("is-done"); window.setTimeout(loaded, 250); window.setTimeout(function () { loader.remove(); }, 1300); }
    };
    requestAnimationFrame(tick);
  }

  // page-to-page wipe
  document.addEventListener("click", function (e) {
    var a = e.target.closest("a[href]");
    if (!a || !curtain || reduce) return;
    var href = a.getAttribute("href");
    if (a.target === "_blank" || e.metaKey || e.ctrlKey || e.shiftKey || a.hasAttribute("download") || a.hasAttribute("data-yt") || a.hasAttribute("data-calendly")) return;
    if (!/^[\w\-]+\.html([?#].*)?$/.test(href)) return;
    if (href.split("#")[0] === location.pathname.split("/").pop() && href.indexOf("#") > -1) return;
    e.preventDefault();
    store.set("jaw-trans", "1");
    curtain.classList.remove("is-out");
    curtain.classList.add("is-in");
    window.setTimeout(function () { location.href = href; }, 720);
  });
  window.addEventListener("pageshow", function (e) {
    if (e.persisted && curtain) { curtain.classList.remove("is-in", "is-cover"); curtain.classList.add("is-out"); loaded(); }
  });

  function lockScroll(on) { body.style.overflow = on ? "hidden" : ""; }

  /* ======================================================================
     Split headings into words / scrubbed paragraphs
     ====================================================================== */
  function wrapWords(el, cls, inner) {
    var i = 0;
    (function walk(node) {
      Array.prototype.slice.call(node.childNodes).forEach(function (c) {
        if (c.nodeType === 3) {
          var parts = c.textContent.split(/(\s+)/);
          var frag = document.createDocumentFragment();
          parts.forEach(function (p) {
            if (!p) return;
            if (/^\s+$/.test(p)) { frag.appendChild(document.createTextNode(p)); return; }
            var s = document.createElement("span");
            s.className = cls;
            if (inner) { var t = document.createElement("span"); t.textContent = p; t.style.setProperty("--i", i); s.appendChild(t); }
            else s.textContent = p;
            i++;
            frag.appendChild(s);
          });
          c.parentNode.replaceChild(frag, c);
        } else if (c.nodeType === 1 && c.tagName !== "BR") walk(c);
      });
    })(el);
    return i;
  }
  document.querySelectorAll("[data-split]").forEach(function (el) {
    el.classList.add("splt");
    if (el.dataset.delay) el.style.setProperty("--d", el.dataset.delay + "ms");
    el.setAttribute("aria-label", el.textContent.replace(/\s+/g, " ").trim());
    wrapWords(el, "w", true);
    Array.prototype.forEach.call(el.children, function (c) { c.setAttribute("aria-hidden", "true"); });
  });
  var scrubs = [];
  document.querySelectorAll("[data-scrub]").forEach(function (el) {
    el.classList.add("scrub");
    wrapWords(el, "sw", false);
    scrubs.push({ el: el, words: el.querySelectorAll(".sw") });
  });

  /* ======================================================================
     Reveals
     ====================================================================== */
  var revealEls = document.querySelectorAll(".reveal, .reveal-img, .splt:not([data-hero-split])");
  if ("IntersectionObserver" in window && !reduce) {
    var ro = new IntersectionObserver(function (entries) {
      entries.forEach(function (en) { if (en.isIntersecting) { en.target.classList.add("is-visible"); ro.unobserve(en.target); } });
    }, { rootMargin: "0px 0px -8% 0px", threshold: 0.06 });
    revealEls.forEach(function (el) { ro.observe(el); });
  } else revealEls.forEach(function (el) { el.classList.add("is-visible"); });

  /* ======================================================================
     Header, announcement bar, floating CTAs
     ====================================================================== */
  var header = document.querySelector(".site-header");
  var hero = document.querySelector("[data-hero]");
  var mobileCta = document.querySelector(".mobile-cta");
  var floatCta = document.querySelector(".float-cta");
  var lastY = window.scrollY;
  function onHeader(y) {
    var heroH = hero ? hero.offsetHeight - 100 : 0;
    body.classList.toggle("bar-hidden", y > 60);
    if (header) {
      header.classList.toggle("is-over-hero", !!hero && y < heroH);
      header.classList.toggle("is-scrolled", y > 30 && (!hero || y >= heroH));
      header.classList.toggle("is-hidden", y > 500 && y > lastY + 2 && !body.classList.contains("menu-open"));
      if (y < lastY - 2) header.classList.remove("is-hidden");
    }
    var show = y > window.innerHeight * 0.7;
    var nearEnd = y + window.innerHeight > document.documentElement.scrollHeight - 700;
    if (mobileCta) mobileCta.classList.toggle("is-visible", show);
    if (floatCta) floatCta.classList.toggle("is-visible", show && !nearEnd);
    lastY = y;
  }

  /* ======================================================================
     Mobile menu
     ====================================================================== */
  var toggle = document.querySelector(".menu-toggle");
  var menu = document.getElementById("mobile-menu");
  function setMenu(open) {
    body.classList.toggle("menu-open", open);
    if (toggle) { toggle.setAttribute("aria-expanded", open ? "true" : "false"); toggle.setAttribute("aria-label", open ? "Close menu" : "Open menu"); }
    if (menu) menu.setAttribute("aria-hidden", open ? "false" : "true");
  }
  if (toggle) toggle.addEventListener("click", function () { setMenu(!body.classList.contains("menu-open")); });
  if (menu) menu.addEventListener("click", function (e) { if (e.target.closest("a")) setMenu(false); });
  document.addEventListener("keydown", function (e) { if (e.key === "Escape") setMenu(false); });

  /* ======================================================================
     Cursor + magnetic buttons + 3D tilt
     ====================================================================== */
  if (fine && !reduce) {
    var cur = document.createElement("div");
    cur.className = "cursor";
    cur.innerHTML = '<div class="cursor__ring"><span class="cursor__label"></span></div><div class="cursor__dot"></div>';
    body.appendChild(cur);
    body.classList.add("has-cursor");
    var ring = cur.querySelector(".cursor__ring"), dot = cur.querySelector(".cursor__dot"), lab = cur.querySelector(".cursor__label");
    var mx = -100, my = -100, rx = -100, ry = -100;
    window.addEventListener("mousemove", function (e) { mx = e.clientX; my = e.clientY; dot.style.transform = "translate(" + mx + "px," + my + "px)"; }, { passive: true });
    (function loop() { rx += (mx - rx) * 0.18; ry += (my - ry) * 0.18; ring.style.transform = "translate(" + rx + "px," + ry + "px)"; requestAnimationFrame(loop); })();
    document.addEventListener("mouseover", function (e) {
      var l = e.target.closest("[data-cursor]");
      var a = e.target.closest("a, button, summary, label, input, select, textarea");
      cur.classList.toggle("is-label", !!l);
      cur.classList.toggle("is-link", !l && !!a);
      if (l) lab.textContent = l.dataset.cursor;
    });
    document.addEventListener("mouseleave", function () { cur.classList.add("is-hidden"); });
    document.addEventListener("mouseenter", function () { cur.classList.remove("is-hidden"); });

    document.querySelectorAll(".magnetic").forEach(function (m) {
      m.addEventListener("mousemove", function (e) {
        var r = m.getBoundingClientRect();
        var x = (e.clientX - r.left - r.width / 2) * 0.28, y = (e.clientY - r.top - r.height / 2) * 0.35;
        m.style.transform = "translate(" + x + "px," + y + "px)";
      });
      m.addEventListener("mouseleave", function () { m.style.transition = "transform .7s cubic-bezier(.22,1,.36,1)"; m.style.transform = ""; window.setTimeout(function () { m.style.transition = ""; }, 700); });
    });
    document.querySelectorAll("[data-tilt]").forEach(function (c) {
      c.addEventListener("mousemove", function (e) {
        var r = c.getBoundingClientRect();
        var x = (e.clientX - r.left) / r.width - 0.5, y = (e.clientY - r.top) / r.height - 0.5;
        c.style.transform = "rotateY(" + (x * 7) + "deg) rotateX(" + (-y * 7) + "deg) translateZ(0)";
      });
      c.addEventListener("mouseleave", function () { c.style.transform = ""; });
    });
  }

  /* ======================================================================
     Video handling
     ====================================================================== */
  function play(v) { var p = v.play(); if (p && p.catch) p.catch(function () {}); }
  document.querySelectorAll("video[data-src-desktop]").forEach(function (v) {
    if (reduce) return;
    v.src = small && v.dataset.srcMobile ? v.dataset.srcMobile : v.dataset.srcDesktop;
    v.addEventListener("playing", function () { v.classList.add("is-playing"); }, { once: true });
    play(v);
  });
  var loops = document.querySelectorAll("video[data-loop]");
  if ("IntersectionObserver" in window && !reduce) {
    var vo = new IntersectionObserver(function (entries) {
      entries.forEach(function (en) {
        var v = en.target;
        if (en.isIntersecting) {
          if (!v.getAttribute("src") && v.dataset.src) v.src = v.dataset.src;
          v.addEventListener("playing", function () { v.classList.add("is-playing"); }, { once: true });
          play(v);
        } else if (!v.paused) v.pause();
      });
    }, { rootMargin: "300px 0px", threshold: 0.01 });
    loops.forEach(function (v) { vo.observe(v); });
  }
  document.querySelectorAll(".film[data-preview]").forEach(function (f) {
    if (!fine || reduce) return;
    var v = f.querySelector("video");
    if (!v) return;
    f.addEventListener("mouseenter", function () { if (!v.getAttribute("src")) v.src = f.dataset.preview; f.classList.add("is-previewing"); play(v); });
    f.addEventListener("mouseleave", function () { f.classList.remove("is-previewing"); v.pause(); });
  });

  // viewfinder timecode (24fps)
  var tc = document.querySelector("[data-timecode]");
  if (tc) {
    var t0 = performance.now() - 83000;
    var pad = function (n) { return (n < 10 ? "0" : "") + n; };
    window.setInterval(function () {
      var f = Math.floor((performance.now() - t0) / (1000 / 24));
      var fr = f % 24, s = Math.floor(f / 24);
      tc.textContent = pad(Math.floor(s / 3600)) + ":" + pad(Math.floor(s / 60) % 60) + ":" + pad(s % 60) + ":" + pad(fr);
    }, 42);
  }

  /* ======================================================================
     Scroll-driven scenes (one rAF loop)
     ====================================================================== */
  var heroMedia = document.querySelector(".hero__media");
  var heroContent = document.querySelector(".hero__content");
  var reel = document.querySelector(".reel");
  var reelFrame = reel && reel.querySelector(".reel__frame");
  var timeline = document.querySelector(".timeline");
  var tlLine = timeline && timeline.querySelector(".timeline__line");
  var tlSteps = timeline ? timeline.querySelectorAll(".tl-step") : [];
  var paras = Array.prototype.slice.call(document.querySelectorAll("[data-speed]"));
  var readBar = document.querySelector(".read-progress");
  var article = document.querySelector(".prose");
  var queued = false;

  function update() {
    queued = false;
    var y = window.scrollY, vh = window.innerHeight;
    // ---- reads (no style writes until every measurement is taken)
    var reelR = reel && !small && !reduce ? reelFrame.parentElement.getBoundingClientRect() : null;
    var paraR = small || reduce ? [] : paras.map(function (el) { return el.parentElement.getBoundingClientRect(); });
    var scrubR = scrubs.map(function (sc) { return sc.el.getBoundingClientRect(); });
    var tlR = timeline ? timeline.getBoundingClientRect() : null;
    var stepTops = Array.prototype.map.call(tlSteps, function (st) { return st.getBoundingClientRect().top; });
    var artR = readBar && article ? article.getBoundingClientRect() : null;

    // ---- writes
    onHeader(y);
    if (!reduce && heroMedia && y < vh * 1.2) {
      var hp = y / vh;
      heroMedia.style.transform = "translate3d(0," + (y * 0.35).toFixed(1) + "px,0) scale(" + (1 + hp * 0.1).toFixed(4) + ")";
      if (heroContent) { heroContent.style.transform = "translate3d(0," + (y * -0.12).toFixed(1) + "px,0)"; heroContent.style.opacity = String(clamp(1 - hp * 1.4, 0, 1)); }
    }
    if (reelR) {
      // grows from a framed shot to full-bleed while the section passes through; the page never stops
      var p = clamp((vh - reelR.top) / (vh * 0.95), 0, 1);
      var e = 1 - Math.pow(1 - p, 3);
      reel.style.setProperty("--w", (52 + 48 * e).toFixed(2) + "vw");
      reel.style.setProperty("--h", (58 + 42 * e).toFixed(2) + "vh");
      reel.style.setProperty("--r", ((1 - e) * 4).toFixed(2) + "px");
      reel.style.setProperty("--x", (e * 40).toFixed(2) + "vw");
      reel.style.setProperty("--shade", (0.05 + e * 0.3).toFixed(3));
      var pp = clamp((p - 0.75) / 0.25, 0, 1);
      reel.style.setProperty("--po", pp.toFixed(3));
      reel.style.setProperty("--ps", (0.7 + pp * 0.3).toFixed(3));
    }
    paraR.forEach(function (b, k) {
      if (b.bottom < -100 || b.top > vh + 100) return;
      var q = (b.top + b.height / 2 - vh / 2) / vh;
      paras[k].style.transform = "translate3d(0," + (q * -parseFloat(paras[k].dataset.speed)).toFixed(1) + "px,0)";
    });
    scrubs.forEach(function (sc, k) {
      var b = scrubR[k];
      var n = reduce ? sc.words.length : Math.round(clamp((vh * 0.85 - b.top) / (b.height + vh * 0.35), 0, 1) * sc.words.length);
      if (n === sc.n) return;
      sc.n = n;
      for (var i = 0; i < sc.words.length; i++) sc.words[i].classList.toggle("on", i < n);
    });
    if (tlR) {
      tlLine.style.setProperty("--p", clamp((vh * 0.6 - tlR.top) / tlR.height, 0, 1).toFixed(4));
      stepTops.forEach(function (t, k) { tlSteps[k].classList.toggle("is-on", t < vh * 0.6); });
    }
    if (artR) readBar.style.setProperty("--p", clamp(-artR.top / (artR.height - vh * 0.5), 0, 1).toFixed(4));
  }
  function requestUpdate() { if (!queued) { queued = true; requestAnimationFrame(update); } }
  window.addEventListener("scroll", requestUpdate, { passive: true });
  window.addEventListener("resize", function () { small = window.matchMedia("(max-width: 860px)").matches; requestUpdate(); });
  window.addEventListener("load", requestUpdate);
  update();

  // film carousel: swipe, drag, arrows, progress
  document.querySelectorAll(".hgallery").forEach(function (g) {
    var tr = g.querySelector(".hgallery__track"), bar = g.querySelector(".hgallery__progress"), cnt = g.querySelector("[data-hg-current]");
    var cards = tr.querySelectorAll(".hcard:not(.hcard--end)");
    var sync = function () {
      var max = tr.scrollWidth - tr.clientWidth;
      var gp = max > 0 ? tr.scrollLeft / max : 0;
      if (bar) bar.style.setProperty("--p", gp.toFixed(4));
      if (cnt) cnt.textContent = String(Math.min(cards.length, 1 + Math.round(gp * (cards.length - 1))));
    };
    tr.addEventListener("scroll", sync, { passive: true });
    var step = function (dir) { var c = cards[0]; tr.scrollBy({ left: dir * (c ? c.getBoundingClientRect().width + 30 : tr.clientWidth * 0.8), behavior: "smooth" }); };
    g.querySelectorAll("[data-hg]").forEach(function (btn) { btn.addEventListener("click", function () { step(+btn.dataset.hg); }); });
    if (fine) {
      var down = false, moved = false, sx = 0, sl = 0;
      tr.addEventListener("pointerdown", function (e) { if (e.pointerType !== "mouse") return; down = true; moved = false; sx = e.clientX; sl = tr.scrollLeft; tr.classList.add("is-dragging"); });
      window.addEventListener("pointermove", function (e) { if (!down) return; var dx = e.clientX - sx; if (Math.abs(dx) > 5) moved = true; tr.scrollLeft = sl - dx; });
      window.addEventListener("pointerup", function () { if (!down) return; down = false; tr.classList.remove("is-dragging"); });
      tr.addEventListener("click", function (e) { if (moved) { e.preventDefault(); e.stopPropagation(); moved = false; } }, true);
      tr.addEventListener("dragstart", function (e) { e.preventDefault(); });
    }
    sync();
  });

  // scrollytelling image swap
  var scrolly = document.querySelector(".scrolly");
  if (scrolly && "IntersectionObserver" in window) {
    var imgs = scrolly.querySelectorAll(".scrolly__img");
    var counter = scrolly.querySelector(".scrolly__counter");
    var so = new IntersectionObserver(function (entries) {
      entries.forEach(function (en) {
        if (!en.isIntersecting) return;
        var i = +en.target.dataset.i;
        scrolly.querySelectorAll(".scrolly__step").forEach(function (s, k) { s.classList.toggle("is-active", k === i); });
        imgs.forEach(function (im, k) { im.classList.toggle("is-active", k <= i); });
        if (counter) counter.textContent = "0" + (i + 1) + " / 0" + imgs.length;
      });
    }, { rootMargin: "-45% 0px -45% 0px" });
    scrolly.querySelectorAll(".scrolly__step").forEach(function (s, k) { s.dataset.i = k; so.observe(s); });
  }

  // count-up numbers
  if ("IntersectionObserver" in window) {
    var co = new IntersectionObserver(function (entries) {
      entries.forEach(function (en) {
        if (!en.isIntersecting) return;
        co.unobserve(en.target);
        var el = en.target, to = parseFloat(el.dataset.count), dec = (el.dataset.count.split(".")[1] || "").length, t1 = null;
        if (reduce) return;
        (function step(t) {
          if (!t1) t1 = t;
          var k = clamp((t - t1) / 1600, 0, 1), v = to * (1 - Math.pow(1 - k, 4));
          el.textContent = v.toFixed(dec);
          if (k < 1) requestAnimationFrame(step);
        })(performance.now());
      });
    }, { threshold: 0.6 });
    document.querySelectorAll("[data-count]").forEach(function (el) { co.observe(el); });
  }

  /* ======================================================================
     Film modal (YouTube) with a follow-up CTA
     ====================================================================== */
  var modal = document.getElementById("film-modal");
  var lastFocus = null;
  function openFilm(id, title) {
    if (!modal) return;
    lastFocus = document.activeElement;
    modal.querySelector(".modal__frame").innerHTML = '<iframe src="https://www.youtube-nocookie.com/embed/' + encodeURIComponent(id) +
      '?autoplay=1&rel=0&modestbranding=1&playsinline=1" title="' + (title || "Wedding film").replace(/"/g, "") +
      '" allow="autoplay; encrypted-media; picture-in-picture; fullscreen" allowfullscreen></iframe>';
    modal.querySelector(".modal__title").textContent = title || "";
    modal.classList.add("is-open");
    modal.setAttribute("aria-hidden", "false");
    lockScroll(true);
    modal.querySelector(".modal__close").focus();
    track("ViewContent", { content_name: title, content_type: "wedding_film" });
  }
  function closeFilm() {
    if (!modal || !modal.classList.contains("is-open")) return;
    modal.classList.remove("is-open");
    modal.setAttribute("aria-hidden", "true");
    lockScroll(false);
    window.setTimeout(function () { modal.querySelector(".modal__frame").innerHTML = ""; }, 500);
    if (lastFocus) lastFocus.focus();
  }
  document.addEventListener("click", function (e) {
    var t = e.target.closest("[data-yt]");
    if (t) { e.preventDefault(); openFilm(t.dataset.yt, t.dataset.title); }
  });
  if (modal) {
    modal.addEventListener("click", function (e) { if (e.target === modal || e.target.closest(".modal__close")) closeFilm(); });
    modal.querySelector(".modal__after").addEventListener("click", function (e) { if (e.target.closest("a")) closeFilm(); });
  }
  document.addEventListener("keydown", function (e) { if (e.key === "Escape") { closeFilm(); closeExit(); } });

  /* ======================================================================
     Calendly popup (loads on demand; falls back to a new tab)
     ====================================================================== */
  var calLoading = false;
  function openCal() {
    track("Schedule");
    if (window.Calendly) { window.Calendly.initPopupWidget({ url: CAL }); return; }
    if (calLoading) return;
    calLoading = true;
    var css = document.createElement("link"); css.rel = "stylesheet"; css.href = "https://assets.calendly.com/assets/external/widget.css"; document.head.appendChild(css);
    var s = document.createElement("script"); s.src = "https://assets.calendly.com/assets/external/widget.js"; s.async = true;
    s.onload = function () { calLoading = false; window.Calendly.initPopupWidget({ url: CAL }); };
    s.onerror = function () { calLoading = false; window.open(CAL, "_blank", "noopener"); };
    document.head.appendChild(s);
  }
  document.addEventListener("click", function (e) {
    var c = e.target.closest("[data-calendly]");
    if (!c || !CAL) return;
    e.preventDefault();
    openCal();
  });

  /* ======================================================================
     Date checker
     ====================================================================== */
  var DAYS = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"];
  var MONTHS = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"];
  function dateInsight(v) {
    if (!v) return "";
    var p = v.split("-"), d = new Date(+p[0], +p[1] - 1, +p[2]);
    if (isNaN(d)) return "";
    var day = d.getDay(), m = d.getMonth();
    var label = DAYS[day] + ", " + MONTHS[m] + " " + d.getDate() + ", " + d.getFullYear();
    var peak = m >= 5 && m <= 9;
    var note;
    if (day === 6 && peak) note = "a peak-season Saturday. These are the first dates to go.";
    else if (day === 6) note = "a Saturday. Popular, so it’s worth asking early.";
    else if (day === 5 || day === 0) note = "a " + DAYS[day] + ". Often easier to secure, and just as beautiful on film.";
    else note = "a weekday wedding. Gorgeous light, quieter venues, and easier to book.";
    if (!peak && (m >= 10 || m <= 2)) note += " Winter light films beautifully.";
    return label + ": " + note;
  }
  document.querySelectorAll("[data-datecheck]").forEach(function (f) {
    var input = f.querySelector('input[type="date"]');
    var msg = f.parentElement.querySelector(".datecheck__msg");
    if (input) input.min = new Date().toISOString().slice(0, 10);
    if (input) input.addEventListener("change", function () { if (msg) msg.textContent = dateInsight(input.value); });
    f.addEventListener("submit", function (e) {
      e.preventDefault();
      if (!input.value) { input.showPicker ? input.showPicker() : input.focus(); return; }
      track("InitiateCheckout", { content_name: "date_check" });
      store.set("jaw-exit", "1");
      var go = "contact.html?date=" + encodeURIComponent(input.value) + "&src=" + encodeURIComponent(f.dataset.datecheck || "site");
      if (curtain && !reduce) { store.set("jaw-trans", "1"); curtain.classList.remove("is-out"); curtain.classList.add("is-in"); window.setTimeout(function () { location.href = go; }, 720); }
      else location.href = go;
    });
  });

  /* ======================================================================
     Collection finder quiz
     ====================================================================== */
  var COLL = {
    "sweet-simple": { name: "Sweet &amp; Simple", pre: "From", price: "$1,950", why: "A shorter, simpler day, beautifully kept: 6 hours, a 3 to 5 minute cinematic highlight film, drone, and a private 4K gallery." },
    "classic-collection": { name: "Classic Collection", pre: "Investment", price: "$2,750", why: "The full day, the way most couples do it: 10 hours, a 5 to 10 minute film, a social teaser, drone, ceremony/speech/first-dance highlights, and a letter-reading film." },
    "luxury-collection": { name: "Luxury Collection", pre: "From", price: "$3,950", why: "The whole day, kept in full: 12+ hours, an 8 to 10 minute main film, a shorter version to share, extended drone, and all of your footage, raw and colour graded." }
  };
  document.querySelectorAll("[data-quiz]").forEach(function (q) {
    var steps = q.querySelectorAll(".quiz__step"), result = q.querySelector(".quiz__result"), bar = q.querySelector(".quiz__bar"), cnt = q.querySelector("[data-quiz-count]");
    var score = { "sweet-simple": 0, "classic-collection": 0, "luxury-collection": 0 }, i = 0;
    function show(n) {
      steps.forEach(function (s, k) { s.classList.toggle("is-active", k === n); });
      result.classList.toggle("is-active", n >= steps.length);
      bar.style.setProperty("--p", Math.min(1, (n + 1) / steps.length));
      if (cnt) cnt.textContent = n >= steps.length ? "Your match" : "Question " + (n + 1) + " of " + steps.length;
    }
    q.addEventListener("click", function (e) {
      var o = e.target.closest(".quiz__opt");
      if (o) {
        score[o.dataset.v] += +(o.dataset.w || 1);
        i++;
        if (i >= steps.length) {
          var best = Object.keys(score).sort(function (a, b) { return score[b] - score[a] || (b === "classic-collection") - (a === "classic-collection"); })[0];
          var c = COLL[best];
          result.querySelector("[data-r-name]").innerHTML = c.name;
          result.querySelector("[data-r-price]").innerHTML = "<small>" + c.pre + "</small>" + c.price;
          result.querySelector("[data-r-why]").textContent = c.why;
          result.querySelector("[data-r-cta]").href = "contact.html?collection=" + best + "&src=quiz";
          track("CustomizeProduct", { content_name: best });
        }
        show(i);
      }
      if (e.target.closest(".quiz__restart")) { i = 0; Object.keys(score).forEach(function (k) { score[k] = 0; }); show(0); }
    });
    show(0);
  });

  /* ======================================================================
     Reviews carousel
     ====================================================================== */
  document.querySelectorAll("[data-reviews]").forEach(function (wrap) {
    var items = wrap.querySelectorAll(".review"), dotsWrap = wrap.querySelector(".reviews__dots");
    if (!items.length || !dotsWrap) return;
    var i = 0, timer = null, dots = [];
    items.forEach(function (_, n) {
      var b = document.createElement("button");
      b.type = "button"; b.setAttribute("aria-label", "Show review " + (n + 1));
      b.addEventListener("click", function () { go(n, true); });
      dotsWrap.appendChild(b); dots.push(b);
    });
    function go(n, user) {
      i = (n + items.length) % items.length;
      items.forEach(function (it, k) { it.classList.toggle("is-active", k === i); it.setAttribute("aria-hidden", k === i ? "false" : "true"); });
      dots.forEach(function (d, k) { d.classList.remove("is-active"); if (k === i) { void d.offsetWidth; d.classList.add("is-active"); } });
      if (user) restart();
    }
    function restart() { window.clearInterval(timer); if (!reduce) timer = window.setInterval(function () { go(i + 1); }, 7000); }
    var prev = wrap.querySelector(".reviews__arrow--prev"), next = wrap.querySelector(".reviews__arrow--next");
    if (prev) prev.addEventListener("click", function () { go(i - 1, true); });
    if (next) next.addEventListener("click", function () { go(i + 1, true); });
    var sx = null;
    wrap.addEventListener("touchstart", function (e) { sx = e.touches[0].clientX; }, { passive: true });
    wrap.addEventListener("touchend", function (e) { if (sx === null) return; var dx = e.changedTouches[0].clientX - sx; if (Math.abs(dx) > 40) go(dx < 0 ? i + 1 : i - 1, true); sx = null; });
    go(0); restart();
  });

  /* ======================================================================
     Film index: floating preview follows the cursor
     ====================================================================== */
  var fi = document.querySelector(".film-index");
  if (fi && fine && !reduce) {
    var pv = document.createElement("div");
    pv.className = "fi-preview";
    var vids = {};
    fi.querySelectorAll("[data-preview]").forEach(function (row) {
      var v = document.createElement("video");
      v.muted = true; v.loop = true; v.playsInline = true; v.preload = "none"; v.dataset.src = row.dataset.preview;
      pv.appendChild(v); vids[row.dataset.preview] = v;
    });
    body.appendChild(pv);
    var px = 0, py = 0, tx = 0, ty = 0;
    fi.addEventListener("mousemove", function (e) { tx = e.clientX; ty = e.clientY; });
    (function loop() { px += (tx - px) * 0.12; py += (ty - py) * 0.12; pv.style.left = px + "px"; pv.style.top = py + "px"; requestAnimationFrame(loop); })();
    fi.querySelectorAll("[data-preview]").forEach(function (row) {
      row.addEventListener("mouseenter", function () {
        var v = vids[row.dataset.preview];
        if (!v.getAttribute("src")) v.src = v.dataset.src;
        Object.keys(vids).forEach(function (k) { vids[k].classList.toggle("is-current", vids[k] === v); if (vids[k] !== v) vids[k].pause(); });
        play(v); pv.classList.add("is-on");
      });
    });
    fi.addEventListener("mouseleave", function () { pv.classList.remove("is-on"); });
  }

  /* ======================================================================
     Multi-step inquiry form (saves a draft locally)
     ====================================================================== */
  var form = document.getElementById("inquiry-form");
  if (form) {
    var steps = form.querySelectorAll(".msform__step");
    var bar = form.querySelector(".msform__bar");
    var count = form.querySelector(".msform__count");
    var saved = form.querySelector(".msform__saved");
    var stepIdx = 0, started = false, DRAFT = "jaw-inquiry";
    var params = new URLSearchParams(location.search);

    try {
      var d = JSON.parse(store.lget(DRAFT) || "{}");
      Object.keys(d).forEach(function (k) {
        var els = form.querySelectorAll('[name="' + k + '"]');
        els.forEach(function (el) { if (el.type === "radio" || el.type === "checkbox") el.checked = el.value === d[k] || (el.type === "checkbox" && d[k] === "on"); else el.value = d[k]; });
      });
    } catch (e) {}
    if (params.get("date")) form.querySelector('[name="wedding_date"]').value = params.get("date").replace(/[^0-9-]/g, "");
    if (params.get("collection")) { var r = form.querySelector('input[name="collection"][value="' + params.get("collection").replace(/[^a-z-]/g, "") + '"]'); if (r) r.checked = true; }
    if (params.get("src")) form.querySelector('[name="entry_point"]').value = params.get("src").replace(/[^a-z-]/g, "");
    var dateIn = form.querySelector('[name="wedding_date"]');
    dateIn.min = new Date().toISOString().slice(0, 10);
    var noDate = form.querySelector('[name="no_date_yet"]');
    var syncDate = function () { dateIn.required = !noDate.checked; dateIn.disabled = noDate.checked; dateIn.closest(".field").style.opacity = noDate.checked ? ".4" : ""; };
    noDate.addEventListener("change", syncDate); syncDate();
    var insight = form.querySelector("[data-date-insight]");
    var showInsight = function () { if (insight) insight.textContent = dateInsight(dateIn.value); };
    dateIn.addEventListener("change", showInsight); showInsight();

    function saveDraft() {
      var o = {};
      new FormData(form).forEach(function (v, k) { if (k.charAt(0) !== "_") o[k] = v; });
      store.lset(DRAFT, JSON.stringify(o));
      if (saved) { saved.classList.add("is-on"); window.clearTimeout(saveDraft.t); saveDraft.t = window.setTimeout(function () { saved.classList.remove("is-on"); }, 1400); }
    }
    form.addEventListener("input", function () {
      saveDraft();
      if (!started) { started = true; track("InitiateCheckout", { content_name: "inquiry_form" }); }
    });
    function valid(n) {
      var ok = true;
      steps[n].querySelectorAll("input, textarea, select").forEach(function (el) {
        if (el.disabled) return;
        var good = el.checkValidity();
        el.classList.toggle("is-invalid", !good);
        if (!good && ok) { ok = false; el.reportValidity(); }
      });
      return ok;
    }
    function show(n, quiet) {
      stepIdx = n;
      steps.forEach(function (s, k) { s.classList.toggle("is-active", k === n); });
      bar.style.setProperty("--p", (n + 1) / steps.length);
      count.textContent = "Step " + (n + 1) + " of " + steps.length;
      var f = steps[n].querySelector("input:not([type=hidden]):not([type=radio]):not([type=checkbox]), textarea");
      if (f && fine && !quiet) window.setTimeout(function () { f.focus({ preventScroll: true }); }, 350);
    }
    form.addEventListener("click", function (e) {
      if (e.target.closest("[data-next]")) { e.preventDefault(); if (valid(stepIdx)) { show(stepIdx + 1); scrollToForm(); } }
      if (e.target.closest("[data-back]")) { e.preventDefault(); show(stepIdx - 1); }
    });
    form.addEventListener("keydown", function (e) {
      if (e.key === "Enter" && e.target.tagName !== "TEXTAREA" && stepIdx < steps.length - 1) { e.preventDefault(); if (valid(stepIdx)) show(stepIdx + 1); }
    });
    function scrollToForm() {
      var top = form.getBoundingClientRect().top + window.scrollY - 140;
      if (window.scrollY > top) { window.scrollTo({ top: top, behavior: "smooth" }); }
    }
    form.addEventListener("submit", function (e) {
      e.preventDefault();
      if (!valid(stepIdx)) return;
      var status = form.querySelector(".form__status");
      var btn = form.querySelector('button[type="submit"]');
      var label = btn.querySelector(".label"), orig = label.textContent;
      status.textContent = ""; btn.disabled = true; label.textContent = "Sending…";
      if (noDate.checked) dateIn.disabled = false;
      var data = new FormData(form);
      if (noDate.checked) dateIn.disabled = true;
      fetch(form.action, { method: "POST", body: data, headers: { Accept: "application/json" } })
        .then(function (res) {
          if (!res.ok) throw new Error("bad");
          store.ldel(DRAFT); store.set("jaw-exit", "1");
          var wrap = form.closest(".form-wrap");
          var nm = (form.querySelector('[name="name"]').value || "").split(/[&,]| and /)[0].trim();
          var hi = wrap.querySelector("[data-hi]"); if (hi && nm) hi.textContent = nm;
          wrap.classList.add("is-sent");
          track("Lead", { content_name: form.querySelector('input[name="collection"]:checked').value });
          scrollToForm();
        })
        .catch(function () {
          status.innerHTML = 'Something went wrong sending your inquiry. Please try again, or email <a class="text-link" href="mailto:jack@jackalbertweddings.ca">jack@jackalbertweddings.ca</a>.';
        })
        .then(function () { btn.disabled = false; label.textContent = orig; });
    });
    show(0, true);
  }

  /* ======================================================================
     Exit intent: one gentle prompt per session
     ====================================================================== */
  var exit = document.getElementById("exit-modal");
  function openExit() {
    if (!exit || store.get("jaw-exit") === "1" || body.classList.contains("menu-open") || (modal && modal.classList.contains("is-open"))) return;
    store.set("jaw-exit", "1");
    exit.classList.add("is-open"); exit.setAttribute("aria-hidden", "false");
    lockScroll(true);
    track("ViewContent", { content_name: "exit_prompt" });
  }
  function closeExit() { if (!exit || !exit.classList.contains("is-open")) return; exit.classList.remove("is-open"); exit.setAttribute("aria-hidden", "true"); lockScroll(false); }
  if (exit && !form) {
    exit.addEventListener("click", function (e) { if (e.target === exit || e.target.closest(".exit__close")) closeExit(); });
    var armed = false;
    window.setTimeout(function () { armed = true; }, 12000);
    document.addEventListener("mouseout", function (e) { if (armed && !e.relatedTarget && e.clientY < 8) openExit(); });
    if (!fine) {
      var deep = false;
      window.addEventListener("scroll", function () { if (window.scrollY > document.documentElement.scrollHeight * 0.55) deep = true; }, { passive: true });
      window.setTimeout(function check() { if (deep) openExit(); else window.setTimeout(check, 5000); }, 45000);
    }
  }

  /* ======================================================================
     Small things
     ====================================================================== */
  var filter = document.querySelector("[data-filter]");
  if (filter) filter.addEventListener("click", function (e) {
    var b = e.target.closest("button[data-cat]");
    if (!b) return;
    filter.querySelectorAll("button").forEach(function (x) { x.classList.toggle("is-active", x === b); x.setAttribute("aria-pressed", x === b ? "true" : "false"); });
    document.querySelectorAll(".post-card[data-cat]").forEach(function (c) { c.hidden = !(b.dataset.cat === "all" || c.dataset.cat === b.dataset.cat); });
  });
  document.addEventListener("click", function (e) {
    var a = e.target.closest('a[href^="tel:"], a[href^="sms:"], a[href^="mailto:"]');
    if (a) track("Contact", { method: a.getAttribute("href").split(":")[0] });
  });
  // article sidebar: highlight the section being read
  var toc = document.querySelectorAll(".toc a");
  if (toc.length && "IntersectionObserver" in window) {
    var to = new IntersectionObserver(function (entries) {
      entries.forEach(function (en) {
        if (!en.isIntersecting) return;
        toc.forEach(function (a) { a.classList.toggle("is-active", a.getAttribute("href") === "#" + en.target.id); });
      });
    }, { rootMargin: "-20% 0px -70% 0px" });
    toc.forEach(function (a) { var h = document.querySelector(a.getAttribute("href")); if (h) to.observe(h); });
  }
  document.querySelectorAll("[data-year]").forEach(function (el) { el.textContent = new Date().getFullYear(); });
})();
