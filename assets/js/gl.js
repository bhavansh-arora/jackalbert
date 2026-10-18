/* Jack Albert Weddings — WebGL layer
   1. [data-gl-video]  : live video through a liquid / chromatic shader (heroes)
   2. [data-gl-slider] : full-screen film slider with displacement transitions
   Each scene renders only while on screen, caps pixel ratio, and leaves the
   plain <video>/<img> in place if WebGL is unavailable. */
(function () {
  "use strict";
  var reduce = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  var fine = window.matchMedia("(hover: hover) and (pointer: fine)").matches;
  var DPR = Math.min(window.devicePixelRatio || 1, fine ? 1.5 : 1.25);

  var VERT = "attribute vec2 p;varying vec2 vUv;void main(){vUv=p*.5+.5;gl_Position=vec4(p,0.,1.);}";
  var COMMON = [
    "precision mediump float;",
    "varying vec2 vUv;",
    "uniform vec2 uRes;uniform float uTime;",
    "vec2 cover(vec2 uv, vec2 tr){float rs=uRes.x/uRes.y,ri=tr.x/tr.y;vec2 s=rs>ri?vec2(1.,ri/rs):vec2(rs/ri,1.);return (uv-.5)*s+.5;}",
    "float hash(vec2 p){return fract(sin(dot(p,vec2(12.9898,78.233)))*43758.5453);}",
    "float noise(vec2 p){vec2 i=floor(p),f=fract(p);f=f*f*(3.-2.*f);return mix(mix(hash(i),hash(i+vec2(1,0)),f.x),mix(hash(i+vec2(0,1)),hash(i+vec2(1,1)),f.x),f.y);}",
    "vec3 grade(vec3 c, vec2 uv){float v=smoothstep(1.25,.25,length(uv-.5)*1.35);c*=mix(.5,1.,v);c=mix(c,c*vec3(1.06,.98,.88),.55);c+=(hash(uv*uRes+fract(uTime)*91.)-.5)*.055;return c;}"
  ].join("\n");

  var FRAG_VIDEO = COMMON + [
    "uniform sampler2D uTex;uniform vec2 uTexRes,uMouse;uniform float uHover,uVel;",
    "void main(){",
    " vec2 uv=vUv;float asp=uRes.x/uRes.y;",
    " vec2 d2=(uv-uMouse)*vec2(asp,1.);float d=length(d2);",
    " float rip=sin(d*34.-uTime*4.)*exp(-d*6.)*.014*uHover;",
    " uv+=normalize(d2+1e-4)*rip/vec2(asp,1.);",
    " uv.x+=sin(uv.y*9.+uTime*1.3)*.0025*uVel;",
    " float ca=.006*uHover*exp(-d*3.5)+.004*uVel;",
    " vec3 c=vec3(texture2D(uTex,cover(uv+vec2(ca,0.),uTexRes)).r,texture2D(uTex,cover(uv,uTexRes)).g,texture2D(uTex,cover(uv-vec2(ca,0.),uTexRes)).b);",
    " gl_FragColor=vec4(grade(c,vUv),1.);",
    "}"
  ].join("\n");

  var FRAG_SLIDER = COMMON + [
    "uniform sampler2D uA,uB;uniform vec2 uAR,uBR,uMouse;uniform float uP,uDir,uHover;",
    "void main(){",
    " vec2 uv=vUv;float asp=uRes.x/uRes.y;",
    " float n=noise(uv*vec2(3.5,2.)+uTime*.05);",
    " float p=uP;",
    " vec2 a=uv+vec2(uDir*p*(n*.55+.15),0.);",
    " vec2 b=uv-vec2(uDir*(1.-p)*(n*.55+.15),0.);",
    " vec2 d2=(uv-uMouse)*vec2(asp,1.);float d=length(d2);",
    " vec2 w=normalize(d2+1e-4)*sin(d*26.-uTime*3.)*exp(-d*5.)*.01*uHover/vec2(asp,1.);",
    " vec4 ca=texture2D(uA,cover(a+w,uAR));vec4 cb=texture2D(uB,cover(b+w,uBR));",
    " float m=smoothstep(.0,1.,p*1.6-n*.6);",
    " vec3 c=mix(ca.rgb,cb.rgb,m);",
    " c=mix(c,vec3(1.,.93,.82),smoothstep(.0,.5,p)*smoothstep(1.,.5,p)*.08);",
    " gl_FragColor=vec4(grade(c,vUv),1.);",
    "}"
  ].join("\n");

  function makeGL(canvas) {
    // refuse software rendering (SwiftShader, llvmpipe, ...): those draw on the CPU and would make scrolling stutter
    var gl = canvas.getContext("webgl", { antialias: false, alpha: false, powerPreference: "high-performance", premultipliedAlpha: false, failIfMajorPerformanceCaveat: true });
    if (!gl) return null;
    try {
      var dbg = gl.getExtension("WEBGL_debug_renderer_info");
      var rn = dbg ? String(gl.getParameter(dbg.UNMASKED_RENDERER_WEBGL)) : "";
      if (/swiftshader|llvmpipe|software|basic render/i.test(rn)) return null;
    } catch (e) {}
    gl.pixelStorei(gl.UNPACK_FLIP_Y_WEBGL, true);
    var buf = gl.createBuffer();
    gl.bindBuffer(gl.ARRAY_BUFFER, buf);
    gl.bufferData(gl.ARRAY_BUFFER, new Float32Array([-1, -1, 1, -1, -1, 1, 1, 1]), gl.STATIC_DRAW);
    return gl;
  }
  function program(gl, frag) {
    function sh(type, src) {
      var s = gl.createShader(type); gl.shaderSource(s, src); gl.compileShader(s);
      if (!gl.getShaderParameter(s, gl.COMPILE_STATUS)) throw new Error(gl.getShaderInfoLog(s));
      return s;
    }
    var p = gl.createProgram();
    gl.attachShader(p, sh(gl.VERTEX_SHADER, VERT)); gl.attachShader(p, sh(gl.FRAGMENT_SHADER, frag)); gl.linkProgram(p);
    if (!gl.getProgramParameter(p, gl.LINK_STATUS)) throw new Error(gl.getProgramInfoLog(p));
    gl.useProgram(p);
    var loc = gl.getAttribLocation(p, "p");
    gl.enableVertexAttribArray(loc); gl.vertexAttribPointer(loc, 2, gl.FLOAT, false, 0, 0);
    var u = {};
    return { p: p, u: function (n) { return u[n] || (u[n] = gl.getUniformLocation(p, n)); } };
  }
  function texture(gl, unit) {
    var t = gl.createTexture();
    gl.activeTexture(gl.TEXTURE0 + unit); gl.bindTexture(gl.TEXTURE_2D, t);
    gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_WRAP_S, gl.CLAMP_TO_EDGE);
    gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_WRAP_T, gl.CLAMP_TO_EDGE);
    gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MIN_FILTER, gl.LINEAR);
    gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MAG_FILTER, gl.LINEAR);
    gl.texImage2D(gl.TEXTURE_2D, 0, gl.RGBA, 1, 1, 0, gl.RGBA, gl.UNSIGNED_BYTE, new Uint8Array([10, 9, 8, 255]));
    return t;
  }
  function sizer(canvas, gl, prog) {
    var w = 0, h = 0;
    return function () {
      var r = canvas.getBoundingClientRect();
      var k = Math.min(DPR, 1280 / Math.max(1, r.width));
      var nw = Math.max(1, Math.round(r.width * k)), nh = Math.max(1, Math.round(r.height * k));
      if (nw !== w || nh !== h) { w = canvas.width = nw; h = canvas.height = nh; gl.viewport(0, 0, w, h); gl.uniform2f(prog.u("uRes"), w, h); }
    };
  }
  function visible(el, cb) {
    if (!("IntersectionObserver" in window)) { cb(true); return; }
    new IntersectionObserver(function (e) { cb(e[e.length - 1].isIntersecting); }, { rootMargin: "80px" }).observe(el);
  }
  function pointer(el) {
    var s = { x: .5, y: .5, tx: .5, ty: .5, h: 0, th: 0 };
    el.addEventListener("pointermove", function (e) {
      var r = el.getBoundingClientRect();
      s.tx = (e.clientX - r.left) / r.width; s.ty = 1 - (e.clientY - r.top) / r.height; s.th = 1;
    }, { passive: true });
    el.addEventListener("pointerleave", function () { s.th = 0; });
    s.step = function () { s.x += (s.tx - s.x) * .08; s.y += (s.ty - s.y) * .08; s.h += (s.th - s.h) * .05; };
    s.moving = function () { return Math.abs(s.tx - s.x) + Math.abs(s.ty - s.y) + Math.abs(s.th - s.h) > .002; };
    return s;
  }

  /* ---------------------------------------------------------------- video heroes */
  function videoScene(host) {
    var video = host.querySelector("video");
    if (!video) return;
    var canvas = document.createElement("canvas");
    canvas.className = "gl-canvas";
    var gl = makeGL(canvas);
    if (!gl) return;
    var prog;
    try { prog = program(gl, FRAG_VIDEO); } catch (e) { return; }
    var tex = texture(gl, 0);
    gl.uniform1i(prog.u("uTex"), 0);
    host.appendChild(canvas);
    var resize = sizer(canvas, gl, prog);
    var ptr = pointer(host.closest("[data-hero]") || host);
    var on = false, running = false, dead = false, ready = false, t0 = performance.now(), lastY = window.scrollY, vel = 0, frames = 0, checks = 0, lastT = -1, tw = 0, th = 0;
    // exactly one render loop at a time: it stops when the hero is off screen, the tab is hidden or the GPU drops the context
    function start() { if (running || !on || dead || document.hidden) return; running = true; requestAnimationFrame(loop); }
    function fallback() { dead = true; host.classList.remove("gl-on"); if (canvas.parentNode) canvas.remove(); }
    visible(host, function (v) { on = v; start(); });
    document.addEventListener("visibilitychange", start);
    canvas.addEventListener("webglcontextlost", function (e) { e.preventDefault(); fallback(); });
    window.addEventListener("resize", resize);
    function loop() {
      if (!on || dead || document.hidden) { running = false; return; }
      requestAnimationFrame(loop);
      resize(); ptr.step();
      var y = window.scrollY; vel += (Math.min(1, Math.abs(y - lastY) / 40) - vel) * .1; lastY = y;
      var fresh = false;
      if (video.readyState >= 2 && video.videoWidth && video.currentTime !== lastT) {
        lastT = video.currentTime; fresh = true;
        gl.bindTexture(gl.TEXTURE_2D, tex);
        // allocate once, then update in place: re-allocating a 1080p texture every frame wears the GPU down over time
        if (video.videoWidth !== tw || video.videoHeight !== th) {
          tw = video.videoWidth; th = video.videoHeight;
          gl.texImage2D(gl.TEXTURE_2D, 0, gl.RGB, gl.RGB, gl.UNSIGNED_BYTE, video);
          gl.uniform2f(prog.u("uTexRes"), tw, th);
        } else gl.texSubImage2D(gl.TEXTURE_2D, 0, 0, 0, gl.RGB, gl.UNSIGNED_BYTE, video);
        if (!ready) { ready = true; host.classList.add("gl-on"); }
      }
      if (!ready) return;
      // between video frames, only redraw while the ripple or scroll wobble is moving
      if (!fresh && ptr.h < .003 && vel < .003 && !ptr.moving()) return;
      gl.uniform1f(prog.u("uTime"), (performance.now() - t0) / 1000);
      gl.uniform2f(prog.u("uMouse"), ptr.x, ptr.y);
      gl.uniform1f(prog.u("uHover"), ptr.h);
      gl.uniform1f(prog.u("uVel"), vel);
      gl.drawArrays(gl.TRIANGLE_STRIP, 0, 4);
      // self-check: if the browser can't hand video frames to WebGL (output stays black), fall back to the plain video
      if (checks < 12 && ++frames % 10 === 0) {
        checks++;
        var px = new Uint8Array(4), lit = 0;
        [[.3, .3], [.5, .5], [.7, .6], [.5, .8]].forEach(function (q) { gl.readPixels(Math.floor(canvas.width * q[0]), Math.floor(canvas.height * q[1]), 1, 1, gl.RGBA, gl.UNSIGNED_BYTE, px); lit += px[0] + px[1] + px[2]; });
        if (lit > 40) checks = 99;
        else if (checks >= 12) fallback();
      }
    }
  }

  /* ---------------------------------------------------------------- film slider */
  function sliderScene(root) {
    var slides = Array.prototype.slice.call(root.querySelectorAll("[data-slide]"));
    var stage = root.querySelector(".fs__stage");
    var titles = root.querySelectorAll(".fs__title");
    var metas = root.querySelectorAll(".fs__meta");
    var cur = root.querySelector("[data-fs-cur]");
    var bars = root.querySelectorAll(".fs__bars span");
    var play = root.querySelector("[data-fs-play]");
    var n = slides.length, idx = 0, busy = false, timer = null, inView = false;

    function setText(i) {
      titles.forEach(function (t, k) { t.classList.toggle("is-active", k === i); });
      metas.forEach(function (t, k) { t.classList.toggle("is-active", k === i); });
      if (cur) cur.textContent = "0" + (i + 1);
      bars.forEach(function (b, k) { b.classList.toggle("is-done", k < i); b.classList.remove("is-active"); if (k === i) { void b.offsetWidth; b.classList.add("is-active"); } });
      if (play) { play.dataset.yt = slides[i].dataset.yt; play.dataset.title = slides[i].dataset.title; }
    }

    // --- WebGL path
    var canvas = document.createElement("canvas");
    canvas.className = "gl-canvas";
    var gl = !reduce && makeGL(canvas), prog = null, texs = [], sizes = [];
    if (gl) { try { prog = program(gl, FRAG_SLIDER); } catch (e) { gl = null; } }
    // each change runs on the clock (fixed length, eased), not a slow exponential chase
    var p = 0, dir = 1, from = 0, to = 0, tStart = 0, DUR = 1100;
    function ease(k) { return k < .5 ? 4 * k * k * k : 1 - Math.pow(-2 * k + 2, 3) / 2; }

    if (gl) {
      stage.appendChild(canvas);
      gl.uniform1i(prog.u("uA"), 0); gl.uniform1i(prog.u("uB"), 1);
      slides.forEach(function (s, k) {
        texs[k] = texture(gl, 0); sizes[k] = [16, 9];
        var img = new Image();
        img.onload = function () {
          gl.activeTexture(gl.TEXTURE0); gl.bindTexture(gl.TEXTURE_2D, texs[k]);
          gl.texImage2D(gl.TEXTURE_2D, 0, gl.RGB, gl.RGB, gl.UNSIGNED_BYTE, img);
          sizes[k] = [img.naturalWidth, img.naturalHeight];
          if (k === 0) root.classList.add("gl-on");
        };
        img.src = s.dataset.img;
      });
      var resize = sizer(canvas, gl, prog);
      var ptr = pointer(stage);
      var t0 = performance.now();
      window.addEventListener("resize", resize);
      var running = false, dead = false, idle = 0;
      var wake = function () { idle = 0; if (running || !inView || dead || document.hidden) return; running = true; requestAnimationFrame(render); };
      stage.addEventListener("pointermove", wake, { passive: true });
      stage.addEventListener("pointerleave", wake);
      document.addEventListener("visibilitychange", wake);
      canvas.addEventListener("webglcontextlost", function (e) {
        e.preventDefault(); dead = true; root.classList.remove("gl-on"); root.classList.add("gl-off");
        slides.forEach(function (s, k) { s.classList.toggle("is-active", k === idx); });
      });
      var render = function () {
        // settled, no hover, nothing transitioning: draw a few more frames then sleep until something changes
        if (!inView || dead || document.hidden || (!busy && !ptr.moving() && ptr.h < .003 && ++idle > 3)) { running = false; return; }
        requestAnimationFrame(render);
        resize(); ptr.step();
        if (busy) { var k = Math.min(1, (performance.now() - tStart) / DUR); p = ease(k); }
        gl.activeTexture(gl.TEXTURE0); gl.bindTexture(gl.TEXTURE_2D, texs[from]);
        gl.activeTexture(gl.TEXTURE1); gl.bindTexture(gl.TEXTURE_2D, texs[to]);
        gl.uniform2f(prog.u("uAR"), sizes[from][0], sizes[from][1]);
        gl.uniform2f(prog.u("uBR"), sizes[to][0], sizes[to][1]);
        gl.uniform1f(prog.u("uP"), p);
        gl.uniform1f(prog.u("uDir"), dir);
        gl.uniform1f(prog.u("uTime"), (performance.now() - t0) / 1000);
        gl.uniform2f(prog.u("uMouse"), ptr.x, ptr.y);
        gl.uniform1f(prog.u("uHover"), ptr.h);
        gl.drawArrays(gl.TRIANGLE_STRIP, 0, 4);
        if (busy && p >= 1) { busy = false; from = to; p = 0; }
      };
      visible(root, function (v) { inView = v; wake(); auto(); });
    } else {
      root.classList.add("gl-off");
      visible(root, function (v) { inView = v; auto(); });
    }

    function go(i, d) {
      i = (i + n) % n;
      if (i === idx) return;
      dir = d || (i > idx ? 1 : -1);
      // a click mid-change lands the current slide at once and starts the next, so no click is ever ignored
      if (gl && !dead) { from = idx; to = i; p = 0; tStart = performance.now(); busy = true; wake(); }
      else slides.forEach(function (s, k) { s.classList.toggle("is-active", k === i); });
      idx = i; setText(i); auto();
    }
    function auto() {
      window.clearTimeout(timer);
      if (inView && !reduce) timer = window.setTimeout(function () { go(idx + 1, 1); }, 6500);
    }
    root.querySelectorAll("[data-fs]").forEach(function (b) { b.addEventListener("click", function () { go(idx + (+b.dataset.fs), +b.dataset.fs); }); });
    bars.forEach(function (b, k) { b.parentElement && b.addEventListener("click", function () { go(k); }); });
    // swipe: only a clearly sideways drag that starts on the stage counts; a scroll cancels it
    var sx = null, sy = null;
    stage.addEventListener("pointerdown", function (e) { sx = e.clientX; sy = e.clientY; });
    stage.addEventListener("pointercancel", function () { sx = null; });
    window.addEventListener("pointerup", function (e) {
      if (sx === null) return;
      var dx = e.clientX - sx, dy = e.clientY - sy; sx = null;
      if (Math.abs(dx) > 50 && Math.abs(dx) > Math.abs(dy) * 1.5) go(idx + (dx < 0 ? 1 : -1), dx < 0 ? 1 : -1);
    });
    root.addEventListener("keydown", function (e) { if (e.key === "ArrowRight") go(idx + 1, 1); if (e.key === "ArrowLeft") go(idx - 1, -1); });
    setText(0);
  }

  function init() {
    if (reduce) return;
    if (fine) document.querySelectorAll("[data-gl-video]").forEach(videoScene);
    document.querySelectorAll("[data-gl-slider]").forEach(sliderScene);
  }
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", init); else init();
})();
