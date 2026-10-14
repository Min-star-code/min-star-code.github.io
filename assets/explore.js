/* Small cross-filter engine and DOM chart renderers shared by the project pages. */
(() => {
  const $ = (s, el = document) => el.querySelector(s);
  const esc = s => String(s).replace(/[&<>"]/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));
  const int = n => Math.round(n).toLocaleString('en-CA');
  const money = v => {
    const a = Math.abs(v), s = v < 0 ? '-' : '';
    if (a >= 1e9) return `${s}$${(a / 1e9).toFixed(a >= 1e10 ? 1 : 2)}B`;
    if (a >= 1e6) return `${s}$${(a / 1e6).toFixed(a >= 1e8 ? 0 : 1)}M`;
    if (a >= 1e3) return `${s}$${(a / 1e3).toFixed(0)}K`;
    return `${s}$${a.toFixed(0)}`;
  };
  const pct = (x, d = 1) => (x * 100).toFixed(d) + '%';

  /* dims: { key: { label, values: [labels], of: i => index, all: 'All regions' } }
     measures: { key: { label, of: i => number, fmt } } */
  function Explorer({ n, dims, measures, measure }) {
    const f = {}, subs = [];
    const keys = Object.keys(dims);
    const ex = {
      n, dims, measures, f, measure,
      get m() { return measures[ex.measure]; },
      pass(i, except) {
        for (const k of keys) if (k !== except && f[k] != null && dims[k].of(i) !== f[k]) return false;
        return true;
      },
      // Sum of a measure per value of one dimension, ignoring that dimension's own filter
      group(k, of = ex.m.of) {
        const out = new Float64Array(dims[k].values.length);
        for (let i = 0; i < n; i++) if (ex.pass(i, k)) { const j = dims[k].of(i); if (j >= 0) out[j] += of(i); }
        return out;
      },
      sum(of) { let t = 0; for (let i = 0; i < n; i++) if (ex.pass(i)) t += of(i); return t; },
      each(fn) { for (let i = 0; i < n; i++) if (ex.pass(i)) fn(i); },
      active() { return keys.filter(k => f[k] != null); },
      set(k, v) { f[k] = v == null || v === f[k] ? null : v; ex.emit(); },
      setMeasure(m) { ex.measure = m; ex.emit(); },
      reset() { keys.forEach(k => f[k] = null); ex.emit(); },
      on(fn) { subs.push(fn); fn(); },
      emit() { subs.forEach(fn => fn()); }
    };
    return ex;
  }

  /* Selects, measure switch, reset and a live count */
  function filterBar(el, ex, { keys, count }) {
    el.innerHTML = `<div class="count num" aria-live="polite"></div>` +
      keys.map(k => `<label>${esc(ex.dims[k].label)}<select data-k="${k}"><option value="">${esc(ex.dims[k].all)}</option>` +
        ex.dims[k].values.map((v, i) => v == null ? '' : `<option value="${i}">${esc(v)}</option>`).join('') + `</select></label>`).join('') +
      (Object.keys(ex.measures).length > 1 ? `<div class="switch" role="group" aria-label="Measure">` +
        Object.entries(ex.measures).map(([k, m]) => `<button data-m="${k}">${esc(m.label)}</button>`).join('') + `</div>` : '') +
      `<button class="reset">Clear filters</button>`;
    el.addEventListener('change', e => { const k = e.target.dataset.k; if (k) { ex.f[k] = e.target.value === '' ? null : +e.target.value; ex.emit(); } });
    el.addEventListener('click', e => {
      if (e.target.dataset.m) ex.setMeasure(e.target.dataset.m);
      if (e.target.classList.contains('reset')) ex.reset();
    });
    ex.on(() => {
      el.querySelectorAll('select').forEach(s => { const v = ex.f[s.dataset.k]; s.value = v == null ? '' : v; s.classList.toggle('on', v != null); });
      el.querySelectorAll('.switch button').forEach(b => b.setAttribute('aria-pressed', b.dataset.m === ex.measure));
      $('.reset', el).disabled = !ex.active().length;
      $('.count', el).innerHTML = count(ex);
    });
  }

  function kpis(el, ex, items) {
    ex.on(() => {
      el.innerHTML = items.map(it => { const r = it(ex); return `<div class="kpi num"><b>${r[0]}</b><span>${esc(r[1])}</span>${r[2] ? `<small>${esc(r[2])}</small>` : ''}</div>`; }).join('');
    });
  }

  // Shared layout for positive-only or diverging values
  function scale(vals) {
    const lo = Math.min(0, ...vals), hi = Math.max(0, ...vals), span = hi - lo || 1;
    return { zero: -lo / span * 100, size: v => Math.abs(v) / span * 100, start: v => (Math.min(0, v) - lo) / span * 100, div: lo < 0 };
  }

  /* Horizontal bars. Click a row to filter by it. opts: top, sort ('value' | 'index'), value(ex) => {vals, fmt, tip} */
  function bars(el, ex, k, opts = {}) {
    const dim = ex.dims[k];
    el.classList.add('rows', 'num');
    const node = {};
    el.addEventListener('click', e => { const r = e.target.closest('.row'); if (r && !opts.fixed) ex.set(k, +r.dataset.i); });
    ex.on(() => {
      const res = opts.value ? opts.value(ex) : { vals: ex.group(k), fmt: ex.m.fmt };
      const vals = res.vals, sel = ex.f[k];
      let idx = [...vals.keys()].filter(i => dim.values[i] != null && (vals[i] !== 0 || i === sel || opts.keepZero));
      if (opts.sort !== 'index') idx.sort((a, b) => vals[b] - vals[a]);
      const hidden = opts.top && idx.length > opts.top ? idx.length - opts.top : 0;
      if (hidden) { const keep = idx.slice(0, opts.top); if (sel != null && !keep.includes(sel)) keep[keep.length - 1] = sel; idx = keep; }
      const sc = scale(idx.map(i => vals[i]));
      if (!idx.length) { el.innerHTML = `<p class="empty">Nothing matches these filters.</p>`; for (const i in node) delete node[i]; return; }
      // Reuse row nodes so bar widths animate between states
      el.querySelectorAll('.empty, .more').forEach(n => n.remove());
      const seen = new Set(idx);
      for (const i in node) if (!seen.has(+i)) { node[i].remove(); delete node[i]; }
      idx.forEach(i => {
        let r = node[i];
        if (!r) {
          r = node[i] = document.createElement('button');
          r.className = 'row'; r.dataset.i = i; if (opts.fixed) r.disabled = true;
          r.innerHTML = `<span class="l">${esc(dim.values[i])}</span><span class="t"><i class="z"></i><i class="f"></i></span><span class="v"></span>`;
        }
        el.appendChild(r);
        const v = vals[i], fill = r.querySelector('.f');
        fill.style.left = sc.start(v) + '%'; fill.style.width = sc.size(v) + '%';
        fill.classList.toggle('neg', v < 0);
        const z = r.querySelector('.z'); z.style.left = sc.zero + '%'; z.style.display = sc.div ? '' : 'none';
        r.querySelector('.v').textContent = res.fmt(v);
        r.classList.toggle('on', sel === i); r.classList.toggle('dim', sel != null && sel !== i);
        if (!opts.fixed) r.setAttribute('aria-pressed', sel === i);
        r.dataset.tip = (res.tip ? res.tip(i, v) : `${dim.values[i]}: ${res.fmt(v)}`) + (opts.fixed ? '' : sel === i ? ' (click to clear)' : ' (click to filter)');
      });
      if (hidden) el.insertAdjacentHTML('beforeend', `<p class="note more">${hidden} more not shown.</p>`);
    });
  }

  /* Vertical columns for ordered dimensions. opts: tick(i, label) => short label or '' */
  function cols(el, ex, k, opts = {}) {
    const dim = ex.dims[k], n = dim.values.length;
    const live = dim.values.map((v, i) => i).filter(i => dim.values[i] != null);
    el.innerHTML = `<p class="peak num"></p><div class="cols"></div><div class="cols-axis num" aria-hidden="true"></div>`;
    const box = $('.cols', el), axis = $('.cols-axis', el), peak = $('.peak', el);
    box.innerHTML = live.map(i => `<button class="col" data-i="${i}"><i class="f"></i></button>`).join('');
    axis.innerHTML = live.map(i => `<span>${esc(opts.tick ? opts.tick(i, dim.values[i]) : dim.values[i])}</span>`).join('');
    const nodes = [...box.children];
    box.addEventListener('click', e => { const c = e.target.closest('.col'); if (c) ex.set(k, +c.dataset.i); });
    ex.on(() => {
      const res = opts.value ? opts.value(ex) : { vals: ex.group(k), fmt: ex.m.fmt };
      const vals = res.vals, sel = ex.f[k], sc = scale(live.map(i => vals[i]));
      let top = live[0]; live.forEach(i => { if (vals[i] > vals[top]) top = i; });
      peak.textContent = vals[top] ? `Highest: ${dim.values[top]}, ${res.fmt(vals[top])}` : 'Nothing matches these filters.';
      nodes.forEach(c => {
        const i = +c.dataset.i, v = vals[i], fill = c.firstChild;
        fill.style.bottom = sc.start(v) + '%'; fill.style.height = sc.size(v) + '%';
        fill.classList.toggle('neg', v < 0);
        c.classList.toggle('dim', sel != null && sel !== i);
        c.setAttribute('aria-pressed', sel === i);
        c.setAttribute('aria-label', `${dim.values[i]}: ${res.fmt(v)}`);
        c.dataset.tip = `${dim.values[i]}: ${res.fmt(v)}` + (sel === i ? ' (click to clear)' : ' (click to filter)');
      });
    });
  }

  /* Two-dimensional grid shaded by the current measure */
  function heat(el, ex, rk, ck, opts = {}) {
    const R = ex.dims[rk].values, C = ex.dims[ck].values;
    el.classList.add('heat', 'num');
    el.style.gridTemplateColumns = `max-content repeat(${C.length}, minmax(0, 1fr))`;
    el.innerHTML = `<span></span>` + C.map((c, j) => `<span class="h">${opts.tick ? opts.tick(j) : esc(c)}</span>`).join('') +
      R.map((r, i) => `<span class="r">${esc(opts.row ? opts.row(r) : r)}</span>` + C.map((c, j) => `<i class="c" data-ij="${i},${j}"></i>`).join('')).join('');
    const cells = [...el.querySelectorAll('.c')];
    const ramp = t => t <= 0 ? 'var(--card)' : `color-mix(in srgb, ${t < .5 ? 'var(--apricot)' : 'var(--ink)'} ${Math.round((t < .5 ? t * 2 : (t - .5) * 2) * 100)}%, ${t < .5 ? 'var(--card)' : 'var(--amber)'})`;
    ex.on(() => {
      const g = new Float64Array(R.length * C.length), of = ex.m.of;
      ex.each(i => { g[ex.dims[rk].of(i) * C.length + ex.dims[ck].of(i)] += of(i); });
      const max = Math.max(...g) || 1;
      cells.forEach((c, x) => {
        c.style.background = ramp(Math.sqrt(g[x] / max));
        c.dataset.tip = `${R[Math.floor(x / C.length)]}, ${opts.col ? opts.col(x % C.length) : C[x % C.length]}: ${ex.m.fmt(g[x])}`;
      });
    });
  }

  /* Dot map on a canvas: every point faintly, matching points in ink */
  function dotMap(canvas, ex, lat, lon) {
    const pts = []; for (let i = 0; i < ex.n; i++) if (lat[i] != null) pts.push(i);
    const b = pts.reduce((a, i) => [Math.min(a[0], lon[i]), Math.max(a[1], lon[i]), Math.min(a[2], lat[i]), Math.max(a[3], lat[i])], [180, -180, 90, -90]);
    const k = Math.cos((b[2] + b[3]) / 2 * Math.PI / 180);
    const css = v => getComputedStyle(document.documentElement).getPropertyValue(v).trim();
    function draw() {
      const w = canvas.clientWidth, h = canvas.clientHeight, dpr = devicePixelRatio || 1;
      canvas.width = w * dpr; canvas.height = h * dpr;
      const g = canvas.getContext('2d'); g.scale(dpr, dpr);
      const pad = 14, s = Math.min((w - pad * 2) / ((b[1] - b[0]) * k), (h - pad * 2) / (b[3] - b[2]));
      const ox = (w - (b[1] - b[0]) * k * s) / 2, oy = (h - (b[3] - b[2]) * s) / 2;
      const X = i => ox + (lon[i] - b[0]) * k * s, Y = i => oy + (b[3] - lat[i]) * s;
      g.fillStyle = css('--mute');
      pts.forEach(i => { g.beginPath(); g.arc(X(i), Y(i), 2, 0, 7); g.fill(); });
      g.fillStyle = css('--key'); g.globalAlpha = .7;
      let shown = 0;
      pts.forEach(i => { if (ex.pass(i)) { shown++; g.beginPath(); g.arc(X(i), Y(i), 2.4, 0, 7); g.fill(); } });
      canvas.setAttribute('aria-label', `Dot map: ${int(shown)} matching project locations out of ${int(pts.length)} with coordinates.`);
      return shown;
    }
    let shown = 0;
    ex.on(() => { shown = draw(); canvas.dispatchEvent(new CustomEvent('drawn', { detail: { shown, total: pts.length } })); });
    addEventListener('resize', draw);
  }

  /* Page chrome: tooltip, nav shadow */
  function chrome() {
    const tip = document.createElement('div'); tip.id = 'tip'; document.body.appendChild(tip);
    document.addEventListener('pointermove', e => {
      const t = e.target.closest ? e.target.closest('[data-tip]') : null;
      if (!t) { tip.style.opacity = 0; return; }
      tip.textContent = t.dataset.tip;
      tip.style.left = Math.max(8, Math.min(e.clientX + 14, innerWidth - tip.offsetWidth - 8)) + 'px';
      const y = e.clientY - tip.offsetHeight - 12;
      tip.style.top = (y < 8 ? e.clientY + 18 : y) + 'px';
      tip.style.opacity = 1;
    });
    const nav = $('.nav');
    const f = () => nav.classList.toggle('scrolled', scrollY > 40);
    addEventListener('scroll', f, { passive: true }); f();
  }


  /* Email links: open the mail app if there is one, and always copy the address */
  (() => {
    const toast = document.createElement('div'); toast.className = 'toast'; toast.setAttribute('role', 'status'); document.body.appendChild(toast);
    let timer;
    document.addEventListener('click', e => {
      const a = e.target.closest && e.target.closest('a[href^="mailto:"]');
      if (!a) return;
      const addr = a.getAttribute('href').slice(7);
      const done = ok => { toast.textContent = ok ? `Email address copied: ${addr}` : `Email: ${addr}`; toast.classList.add('show'); clearTimeout(timer); timer = setTimeout(() => toast.classList.remove('show'), 3200); };
      const legacy = () => { const t = document.createElement('textarea'); t.value = addr; t.style.position = 'fixed'; t.style.opacity = 0; document.body.appendChild(t); t.select(); let ok = false; try { ok = document.execCommand('copy'); } catch (_) {} t.remove(); done(ok); };
      if (navigator.clipboard && navigator.clipboard.writeText) navigator.clipboard.writeText(addr).then(() => done(true), legacy); else legacy();
    });
  })();

  window.EX = { Explorer, filterBar, kpis, bars, cols, heat, dotMap, chrome, int, money, pct, esc, $ };
})();
