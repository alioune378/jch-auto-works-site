/* JCH Auto Works — site behavior. No frameworks; ~10 KB. */
(function () {
  "use strict";
  var CFG = window.JCH || {};
  var doc = document.documentElement;
  doc.classList.add("js");
  var $ = function (s, r) { return (r || document).querySelector(s); };
  var $$ = function (s, r) { return Array.prototype.slice.call((r || document).querySelectorAll(s)); };

  /* ---------- analytics (no-op until GA4/GTM IDs exist and consent is given) ---------- */
  window.dataLayer = window.dataLayer || [];
  function track(event, params) {
    var p = params || {}; p.event = event;
    window.dataLayer.push(p);
  }
  document.addEventListener("click", function (e) {
    var a = e.target.closest && e.target.closest("a, button");
    if (!a) return;
    var href = a.getAttribute("href") || "";
    if (href.indexOf("tel:") === 0) track("click_to_call", { location: a.dataset.track || "link" });
    else if (href.indexOf("mailto:") === 0) track("email_click", { location: a.dataset.track || "link" });
    else if (/google\.com\/maps/.test(href)) track("directions_click", { location: a.dataset.track || "link" });
    else if (a.dataset.track) track("cta_click", { location: a.dataset.track });
  });
  (function consent() {
    if (!CFG.ga4Id && !CFG.gtmId) return;
    var KEY = "jch-consent", stored = null;
    try { stored = localStorage.getItem(KEY); } catch (e) {}
    function gtag() { window.dataLayer.push(arguments); }
    gtag("consent", "default", { analytics_storage: "denied", ad_storage: "denied", ad_user_data: "denied", ad_personalization: "denied" });
    function load() {
      gtag("consent", "update", { analytics_storage: "granted" });
      var s = document.createElement("script"); s.async = true;
      s.src = CFG.gtmId ? "https://www.googletagmanager.com/gtm.js?id=" + CFG.gtmId : "https://www.googletagmanager.com/gtag/js?id=" + CFG.ga4Id;
      document.head.appendChild(s);
      if (!CFG.gtmId) { gtag("js", new Date()); gtag("config", CFG.ga4Id); }
      else window.dataLayer.push({ "gtm.start": Date.now(), event: "gtm.js" });
    }
    if (stored === "yes") return load();
    if (stored === "no") return;
    var box = document.createElement("div");
    box.className = "cookie"; box.setAttribute("role", "dialog"); box.setAttribute("aria-label", "Cookie preferences");
    box.innerHTML = '<p>We use analytics cookies to see which pages help customers most. No ads, no selling data. <a href="privacy.html">Privacy</a></p><div class="btn-row"><button class="btn" data-c="yes">Allow analytics</button><button class="btn btn--ghost" data-c="no">No thanks</button></div>';
    document.body.appendChild(box);
    box.addEventListener("click", function (e) {
      var v = e.target.dataset && e.target.dataset.c; if (!v) return;
      try { localStorage.setItem(KEY, v); } catch (err) {}
      box.remove(); if (v === "yes") load();
    });
  })();

  /* ---------- open/closed indicator (shop time, America/New_York) ---------- */
  $$("[data-open-now]").forEach(function openNow(el) {
    try {
      var parts = new Intl.DateTimeFormat("en-US", { timeZone: "America/New_York", weekday: "short", hour: "numeric", minute: "numeric", hour12: false }).formatToParts(new Date());
      var get = function (t) { return (parts.filter(function (p) { return p.type === t; })[0] || {}).value; };
      var day = get("weekday"), h = parseInt(get("hour"), 10) % 24, m = parseInt(get("minute"), 10);
      var mins = h * 60 + m, weekday = ["Mon", "Tue", "Wed", "Thu", "Fri"].indexOf(day) > -1;
      var open = weekday && mins >= 480 && mins < 1020;
      var dot = $(".dot", el);
      if (open) { dot.classList.add("is-open"); $("[data-open-text]", el).textContent = "Open now · until 5:00 PM"; }
      else { $("[data-open-text]", el).textContent = weekday && mins < 480 ? "Closed · opens 8:00 AM" : "Closed · opens Monday 8:00 AM"; if (weekday && mins >= 1020 && day !== "Fri") $("[data-open-text]", el).textContent = "Closed · opens tomorrow 8:00 AM"; }
    } catch (e) {}
  });

  /* ---------- header shrinks once the page scrolls ---------- */
  var hdr = $("[data-header]");
  function onScroll() {
    if (hdr) hdr.classList.toggle("is-compact", scrollY > 40);
    syncBar();
  }

  /* ---------- navigation ---------- */
  $$(".nav-group").forEach(function (g) {
    var b = $("button", g);
    b.addEventListener("click", function () {
      var open = g.hasAttribute("data-open");
      $$(".nav-group[data-open]").forEach(function (x) { x.removeAttribute("data-open"); $("button", x).setAttribute("aria-expanded", "false"); });
      if (!open) { g.setAttribute("data-open", ""); b.setAttribute("aria-expanded", "true"); }
    });
  });
  document.addEventListener("click", function (e) {
    if (!e.target.closest(".nav-group")) $$(".nav-group[data-open]").forEach(function (x) { x.removeAttribute("data-open"); $("button", x).setAttribute("aria-expanded", "false"); });
  });
  document.addEventListener("keydown", function (e) {
    if (e.key !== "Escape") return;
    $$(".nav-group[data-open]").forEach(function (x) { x.removeAttribute("data-open"); $("button", x).setAttribute("aria-expanded", "false"); $("button", x).focus(); });
    if (drawer && !drawer.hidden) closeDrawer();
  });
  var drawer = $("#drawer"), burger = $(".burger");
  function openDrawer() { drawer.hidden = false; burger.setAttribute("aria-expanded", "true"); document.body.style.overflow = "hidden"; $("a, button", drawer).focus(); }
  function closeDrawer() { drawer.hidden = true; burger.setAttribute("aria-expanded", "false"); document.body.style.overflow = ""; burger.focus(); }
  if (burger && drawer) {
    burger.addEventListener("click", openDrawer);
    $("[data-close]", drawer).addEventListener("click", closeDrawer);
    drawer.addEventListener("keydown", function (e) {
      if (e.key !== "Tab") return;
      var f = $$("a, button, summary", drawer).filter(function (x) { return x.offsetParent !== null; }), first = f[0], last = f[f.length - 1];
      if (e.shiftKey && document.activeElement === first) { e.preventDefault(); last.focus(); }
      else if (!e.shiftKey && document.activeElement === last) { e.preventDefault(); first.focus(); }
    });
  }

  /* ---------- mobile action bar: shows only after the page's own call/estimate
     buttons scroll away; hidden over the footer and while typing ---------- */
  var bar = $("[data-actionbar]"), foot = $(".footer"), heroCta = $("[data-hero-cta]");
  var state = { hero: !!heroCta, foot: false, typing: false };
  function syncBar() {
    if (!bar) return;
    var heroOn = heroCta ? state.hero : scrollY < 240;
    bar.classList.toggle("is-hidden", heroOn || state.foot || state.typing);
  }
  if ("IntersectionObserver" in window) {
    if (foot) new IntersectionObserver(function (en) { state.foot = en[0].isIntersecting; syncBar(); }).observe(foot);
    if (heroCta) new IntersectionObserver(function (en) { state.hero = en[0].isIntersecting; syncBar(); }).observe(heroCta);
  } else state.hero = false;
  document.addEventListener("focusin", function (e) { if (e.target.matches("input, textarea, select")) { state.typing = true; syncBar(); } });
  document.addEventListener("focusout", function () { state.typing = false; syncBar(); });
  addEventListener("scroll", onScroll, { passive: true });
  onScroll();

  /* ---------- reveal: only things below the first screen animate ---------- */
  if ("IntersectionObserver" in window && !matchMedia("(prefers-reduced-motion: reduce)").matches) {
    var io = new IntersectionObserver(function (en) {
      en.forEach(function (x) { if (x.isIntersecting) { x.target.classList.remove("pending"); io.unobserve(x.target); } });
    }, { rootMargin: "0px 0px -8% 0px" });
    $$(".reveal").forEach(function (el) {
      if (el.getBoundingClientRect().top > innerHeight) { el.classList.add("pending"); io.observe(el); }
    });
  }

  /* ---------- repair-order journey tabs ---------- */
  $$("[data-ro]").forEach(function (ro) {
    var tabs = $$('[role="tab"]', ro);
    function select(t, focus) {
      tabs.forEach(function (x) { var on = x === t; x.setAttribute("aria-selected", on); x.tabIndex = on ? 0 : -1; $("#" + x.getAttribute("aria-controls")).hidden = !on; });
      if (focus) t.focus();
      t.scrollIntoView({ block: "nearest", inline: "nearest" });
    }
    tabs.forEach(function (t, i) {
      t.addEventListener("click", function () { select(t); });
      t.addEventListener("keydown", function (e) {
        var k = e.key, n = null;
        if (k === "ArrowDown" || k === "ArrowRight") n = tabs[(i + 1) % tabs.length];
        if (k === "ArrowUp" || k === "ArrowLeft") n = tabs[(i - 1 + tabs.length) % tabs.length];
        if (k === "Home") n = tabs[0]; if (k === "End") n = tabs[tabs.length - 1];
        if (n) { e.preventDefault(); select(n, true); }
      });
    });
  });

  /* ---------- before/after slider ---------- */
  $$(".ba input").forEach(function (r) {
    var box = r.closest(".ba");
    var set = function () { box.style.setProperty("--pos", r.value + "%"); };
    r.addEventListener("input", set); set();
  });

  /* ---------- forms ---------- */
  var host = location.hostname;
  var live = CFG.formsMode === "live" || (CFG.formsMode !== "demo" && (/(^|\.)jchautoworksllc\.org$/.test(host) || /\.netlify\.app$/.test(host)));

  function fieldWrap(el) { return el.closest(".field") || el.closest("fieldset"); }
  function setError(el, msg) {
    var w = fieldWrap(el); if (!w) return;
    var e = $(".err", w);
    if (!e) { e = document.createElement("p"); e.className = "err"; e.id = (el.id || el.name) + "-err"; w.appendChild(e); }
    e.textContent = msg || ""; e.hidden = !msg;
    $$("input, select, textarea", w).forEach(function (i) { if (i.type !== "checkbox" && i.type !== "radio") { i.setAttribute("aria-invalid", msg ? "true" : "false"); if (msg) i.setAttribute("aria-describedby", e.id); } });
  }
  function validate(scope) {
    var firstBad = null;
    $$("[data-req]", scope).forEach(function (el) {
      if (el.closest("[hidden]")) { setError(el, ""); return; }
      var v = (el.value || "").trim(), msg = "", rule = el.dataset.req;
      if (el.type === "checkbox" && rule === "check") { if (!el.checked) msg = el.dataset.msg || "Please tick this box to continue."; }
      else if (rule === "group") {
        var g = el.closest("fieldset, .field"), checked = $$("input:checked", g).length;
        if (!checked) msg = el.dataset.msg || "Choose at least one option.";
      }
      else if (!v) msg = el.dataset.msg || "This field is required.";
      else if (rule === "phone" && v.replace(/\D/g, "").replace(/^1/, "").length !== 10) msg = "Enter a 10-digit phone number, like (315) 555-0142.";
      else if (rule === "email" && !/^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/.test(v)) msg = "Enter an email address like name@example.com.";
      else if (rule === "year") { var y = parseInt(v, 10), max = new Date().getFullYear() + 2; if (!(y >= 1950 && y <= max)) msg = "Enter a model year between 1950 and " + max + "."; }
      else if (rule === "vin" && v && !/^[A-HJ-NPR-Z0-9]{17}$/i.test(v)) msg = "A VIN is 17 letters and numbers (no I, O or Q). Leave it blank if you're not sure.";
      setError(el, msg);
      if (msg && !firstBad) firstBad = el;
    });
    // optional VIN check even when not required
    $$('[name="vin"]', scope).forEach(function (el) {
      var v = el.value.trim(); var bad = v && !/^[A-HJ-NPR-Z0-9]{17}$/i.test(v);
      setError(el, bad ? "A VIN is 17 letters and numbers (no I, O or Q). Leave it blank if you're not sure." : "");
      if (bad && !firstBad) firstBad = el;
    });
    if (firstBad) { (firstBad.type === "hidden" ? fieldWrap(firstBad) : firstBad).focus && firstBad.focus(); }
    return !firstBad;
  }

  // conditional fields: <div data-show-if="name=value">
  function syncConditions(form) {
    $$("[data-show-if]", form).forEach(function (box) {
      var p = box.dataset.showIf.split("="), name = p[0], vals = p[1].split("|");
      var picked = $$('[name="' + name + '"]', form).filter(function (i) { return (i.type === "radio" || i.type === "checkbox") ? i.checked : true; }).map(function (i) { return i.value; });
      box.hidden = !picked.some(function (v) { return vals.indexOf(v) > -1; });
    });
  }

  // photo handling: preview + client-side downscale so a phone's photos fit the upload limit
  var MAX_FILES = 6, MAX_RAW = 20 * 1024 * 1024, OK_TYPES = /^image\/(jpeg|png|webp|heic|heif)$/;
  function fmt(b) { return b > 1048576 ? (b / 1048576).toFixed(1) + " MB" : Math.round(b / 1024) + " KB"; }
  function shrink(file) {
    return new Promise(function (res) {
      if (!/^image\/(jpeg|png|webp)$/.test(file.type)) return res(file);
      var img = new Image(), url = URL.createObjectURL(file);
      img.onload = function () {
        var s = Math.min(1, 1800 / Math.max(img.width, img.height));
        var c = document.createElement("canvas"); c.width = Math.round(img.width * s); c.height = Math.round(img.height * s);
        c.getContext("2d").drawImage(img, 0, 0, c.width, c.height);
        URL.revokeObjectURL(url);
        c.toBlob(function (b) { res(b && b.size < file.size ? new File([b], file.name.replace(/\.\w+$/, "") + ".jpg", { type: "image/jpeg" }) : file); }, "image/jpeg", .82);
      };
      img.onerror = function () { URL.revokeObjectURL(url); res(file); };
      img.src = url;
    });
  }
  function setupPhotos(form) {
    var drop = $(".drop", form); if (!drop) return null;
    var picker = $("#photo-picker", form), list = $(".thumbs", form), status = $("[data-photo-status]", form);
    var files = [];
    function render() {
      list.innerHTML = "";
      files.forEach(function (f, i) {
        var d = document.createElement("div"); d.className = "thumb";
        var im = document.createElement("img"); im.alt = "Damage photo " + (i + 1); im.src = URL.createObjectURL(f);
        im.onerror = function () { im.replaceWith(Object.assign(document.createElement("span"), { textContent: "Photo " + (i + 1), className: "size" })); };
        var x = document.createElement("button"); x.type = "button"; x.setAttribute("aria-label", "Remove photo " + (i + 1)); x.textContent = "×";
        x.onclick = function () { files.splice(i, 1); render(); };
        var s = document.createElement("span"); s.className = "size"; s.textContent = fmt(f.size);
        d.append(im, x, s); list.appendChild(d);
      });
      status.textContent = files.length ? files.length + " of " + MAX_FILES + " photos added" : "";
    }
    function add(fl) {
      var msgs = [];
      Array.prototype.forEach.call(fl, function (f) {
        if (files.length >= MAX_FILES) { msgs.push("You can add up to " + MAX_FILES + " photos."); return; }
        if (!OK_TYPES.test(f.type) && !/\.(heic|heif)$/i.test(f.name)) { msgs.push(f.name + " isn't a photo (use JPG, PNG, WebP or HEIC)."); return; }
        if (f.size > MAX_RAW) { msgs.push(f.name + " is larger than 20 MB."); return; }
        files.push(f);
      });
      setError(picker, msgs.filter(function (v, i, a) { return a.indexOf(v) === i; }).join(" "));
      Promise.all(files.map(shrink)).then(function (out) { files = out; render(); });
    }
    drop.addEventListener("click", function () { picker.click(); });
    drop.addEventListener("keydown", function (e) { if (e.key === "Enter" || e.key === " ") { e.preventDefault(); picker.click(); } });
    picker.addEventListener("change", function () { add(picker.files); picker.value = ""; });
    ["dragenter", "dragover"].forEach(function (t) { drop.addEventListener(t, function (e) { e.preventDefault(); drop.classList.add("is-over"); }); });
    ["dragleave", "drop"].forEach(function (t) { drop.addEventListener(t, function (e) { e.preventDefault(); drop.classList.remove("is-over"); }); });
    drop.addEventListener("drop", function (e) { add(e.dataTransfer.files); });
    return { get: function () { return files; } };
  }

  $$("form[data-jch-form]").forEach(function (form) {
    var steps = $$("[data-step]", form), cur = 0, prog = $$(".form-progress li", form.parentNode);
    var photos = setupPhotos(form);
    var shell = form.closest(".form-shell") || form.parentNode;
    if (!live) {
      var b = document.createElement("div"); b.className = "demo-banner"; b.setAttribute("role", "note");
      b.innerHTML = "<strong>Preview mode.</strong> This form is fully interactive, but nothing is sent from this preview. On the live site, inquiries go straight to the shop's inbox.";
      shell.insertBefore(b, shell.firstChild);
    }
    form.addEventListener("change", function () { syncConditions(form); });
    syncConditions(form);
    function show(i) {
      steps.forEach(function (s, j) { s.hidden = j !== i; });
      prog.forEach(function (p, j) { p.classList.toggle("done", j < i); if (j === i) p.setAttribute("aria-current", "step"); else p.removeAttribute("aria-current"); });
      $$("[data-prev]", form).forEach(function (b) { b.hidden = i === 0; });
      $$("[data-next]", form).forEach(function (b) { b.hidden = i === steps.length - 1; });
      $$("[data-submit]", form).forEach(function (b) { b.hidden = i !== steps.length - 1; });
      cur = i;
      var lg = $("legend", steps[i]); if (lg) { lg.tabIndex = -1; lg.focus({ preventScroll: true }); }
      var top = shell.getBoundingClientRect().top; if (top < 0) shell.scrollIntoView({ behavior: "smooth", block: "start" });
      track("form_step", { form: form.name, step: i + 1 });
    }
    if (steps.length) {
      $$("[data-next]", form).forEach(function (b) { b.addEventListener("click", function () { if (validate(steps[cur])) show(cur + 1); }); });
      $$("[data-prev]", form).forEach(function (b) { b.addEventListener("click", function () { show(cur - 1); }); });
      show(0);
    }
    form.addEventListener("submit", function (e) {
      e.preventDefault();
      if (!validate(steps.length ? steps[cur] : form)) return;
      var fd = new FormData(form);
      fd.delete("photo-picker");
      if (photos) photos.get().forEach(function (f, i) { fd.set("photo" + (i + 1), f, f.name); });
      var total = 0; fd.forEach(function (v) { if (v && v.size) total += v.size; });
      if (total > 7.5 * 1048576) { setError($("#photo-picker", form), "Your photos add up to " + fmt(total) + ". Remove one or two so the total is under 7.5 MB."); return; }
      var ref = "JCH-" + new Date().toISOString().slice(2, 10).replace(/-/g, "") + "-" + Math.random().toString(36).slice(2, 6).toUpperCase();
      fd.set("reference", ref);
      var result = $("[data-result]", shell), sub = $("[data-submit]", form), barEl = $(".bar", form);
      if (!live) {
        var summary = [];
        fd.forEach(function (v, k) { if (k === "form-name" || k === "bot-field" || k === "reference" || !v || (v.size === 0)) return; summary.push(k + ": " + (v.name ? v.name + " (" + fmt(v.size) + ")" : v)); });
        form.hidden = true; result.hidden = false;
        $("[data-result-eyebrow]", result).textContent = "Preview mode";
        $("[data-result-title]", result).textContent = "Preview complete. Nothing was sent.";
        $("[data-result-body]", result).textContent = "This is how the confirmation step works. On the live site, the inquiry below is emailed to the shop and saved in the Netlify inbox.";
        var pre = $("[data-result-detail]", result); pre.hidden = false; pre.textContent = summary.join("\n");
        $(".ref", result).textContent = "Sample reference " + ref;
        result.focus();
        return;
      }
      sub.disabled = true; sub.textContent = "Sending…"; if (barEl) barEl.hidden = false;
      var xhr = new XMLHttpRequest();
      xhr.open("POST", form.getAttribute("action") || "/");
      xhr.upload.onprogress = function (ev) { if (ev.lengthComputable && barEl) $("i", barEl).style.width = Math.round(ev.loaded / ev.total * 100) + "%"; };
      xhr.onload = function () {
        if (xhr.status >= 200 && xhr.status < 400) {
          form.hidden = true; result.hidden = false; $(".ref", result).textContent = "Reference " + ref; result.focus();
          track("generate_lead", { form: form.name });
        } else fail();
      };
      xhr.onerror = fail;
      function fail() {
        sub.disabled = false; sub.textContent = sub.dataset.label; if (barEl) barEl.hidden = true;
        var n = $("[data-send-error]", form); n.hidden = false;
        n.textContent = "We couldn't send your inquiry (" + (xhr.status || "no connection") + "). Check your connection and try again, or call us at " + (CFG.phone || "the shop") + ".";
        n.focus();
      }
      xhr.send(fd);
    });
  });
})();
