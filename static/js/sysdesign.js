// System design playground: walks the learner through one problem, one question at a time.
// Data comes from the page (json_script #sd-data). Signed-in learners sync progress to their account
// (data-progress-url / data-save-url); anonymous learners keep it in this browser (localStorage).
(function () {
  var app = document.getElementById('sd-app');
  var dataEl = document.getElementById('sd-data');
  if (!app || !dataEl) return;

  var problem = JSON.parse(dataEl.textContent);
  var steps = problem.steps;
  var courseBase = app.dataset.course;
  var KEY = 'sd:' + app.dataset.slug;

  var els = {
    step: document.getElementById('sd-step'),
    dots: document.getElementById('sd-dots'),
    phase: document.getElementById('sd-phase'),
    count: document.getElementById('sd-count'),
    fill: document.getElementById('sd-progress-fill'),
    notes: document.getElementById('sd-notes'),
    notesEmpty: document.getElementById('sd-notes-empty'),
    diagram: document.getElementById('sd-diagram'),
    reset: document.getElementById('sd-reset'),
  };

  // ---- state -------------------------------------------------------------
  var progressUrl = app.dataset.progressUrl;
  var saveUrl = app.dataset.saveUrl;
  var synced = false;           // true once the account copy has been loaded; from then on saves go to the server
  var state = loadLocal();

  function loadLocal() {
    try {
      var raw = JSON.parse(localStorage.getItem(KEY) || 'null');
      if (raw && raw.answers) return { answers: raw.answers, current: Math.min(raw.current || 0, steps.length) };
    } catch (e) { /* storage blocked or corrupt: start fresh */ }
    return { answers: {}, current: 0 };
  }
  function saveLocal() {
    try { localStorage.setItem(KEY, JSON.stringify(state)); } catch (e) { /* ignore */ }
  }
  function clearLocal() {
    try { localStorage.removeItem(KEY); } catch (e) { /* ignore */ }
  }
  function save() {
    if (synced) queueSync(); else saveLocal();
  }

  // ---- account sync ------------------------------------------------------
  function cookie(name) {
    var m = document.cookie.match(new RegExp('(?:^|; )' + name + '=([^;]*)'));
    return m ? decodeURIComponent(m[1]) : '';
  }
  function post(body) {
    return fetch(saveUrl, {
      method: 'POST', credentials: 'same-origin',
      headers: { 'Content-Type': 'application/json', 'X-CSRFToken': cookie('csrftoken') },
      body: JSON.stringify(body),
    }).then(function (r) { if (!r.ok) throw new Error('save failed'); return r.json(); });
  }
  var timer = null, inflight = false, dirty = false;
  function queueSync() {
    dirty = true;
    clearTimeout(timer);
    timer = setTimeout(flush, 300);
  }
  function flush() {
    if (inflight || !dirty) return;
    inflight = true; dirty = false;
    post({ answers: state.answers, current: state.current }).then(clearLocal, function () {
      saveLocal();          // offline or expired session: keep a local copy, merged into the account on the next load
    }).then(function () { inflight = false; if (dirty) flush(); });
  }
  // First signed-in load: fetch the account copy and merge in anything saved in this browser before signing in.
  function loadFromAccount() {
    return fetch(progressUrl, { credentials: 'same-origin', headers: { Accept: 'application/json' } })
      .then(function (r) { if (!r.ok) throw new Error('load failed'); return r.json(); })
      .then(function (server) {
        var local = state;
        var hasLocal = Object.keys(local.answers).length > 0;
        var merged = {};
        Object.keys(local.answers).forEach(function (k) { merged[k] = local.answers[k]; });
        Object.keys(server.answers || {}).forEach(function (k) { merged[k] = server.answers[k]; });   // the account wins
        state = { answers: merged, current: Math.min(Math.max(server.current || 0, hasLocal ? local.current : 0), steps.length) };
        synced = true;
        if (hasLocal) {
          return post({ answers: local.answers, current: local.current, merge: true }).then(clearLocal, function () { /* retried next load */ });
        }
      });
  }
  function firstOpen() {
    for (var i = 0; i < steps.length; i++) if (!state.answers[steps[i].id]) return i;
    return steps.length;
  }

  // ---- tiny DOM helpers --------------------------------------------------
  function h(tag, attrs, kids) {
    var el = document.createElement(tag);
    Object.keys(attrs || {}).forEach(function (k) {
      if (k === 'class') el.className = attrs[k];
      else if (k === 'text') el.textContent = attrs[k];
      else if (k === 'html') el.innerHTML = attrs[k];
      else if (k.slice(0, 2) === 'on') el.addEventListener(k.slice(2), attrs[k]);
      else if (attrs[k] !== false && attrs[k] != null) el.setAttribute(k, attrs[k] === true ? '' : attrs[k]);
    });
    (kids || []).forEach(function (c) { if (c) el.appendChild(typeof c === 'string' ? document.createTextNode(c) : c); });
    return el;
  }
  function esc(s) {
    return String(s).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
  }
  // Supports **bold**, `code`, "- " bullet lines and blank-line paragraphs. Input is escaped first.
  function mini(text) {
    var inline = function (s) {
      return esc(s).replace(/`([^`]+)`/g, '<code>$1</code>').replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>')
        .replace(/\*([^*]+)\*/g, '<em>$1</em>');
    };
    return String(text).split(/\n\n+/).map(function (block) {
      var lines = block.split('\n');
      if (lines.every(function (l) { return /^- /.test(l); })) {
        return '<ul>' + lines.map(function (l) { return '<li>' + inline(l.slice(2)) + '</li>'; }).join('') + '</ul>';
      }
      return '<p>' + inline(block) + '</p>';
    }).join('');
  }
  function rich(tag, cls, text) { return h(tag, { class: cls, html: mini(text) }); }

  // ---- number parsing for estimates ---------------------------------------
  function parseNumber(raw) {
    var m = String(raw).trim().toLowerCase().replace(/,/g, '').replace(/\s+/g, '').match(/^(\d*\.?\d+)(k|m|b|t)?/);
    if (!m) return NaN;
    var mult = { k: 1e3, m: 1e6, b: 1e9, t: 1e12 }[m[2]] || 1;
    return parseFloat(m[1]) * mult;
  }
  function fmt(n) {
    return Number(n).toLocaleString(undefined, { maximumFractionDigits: 2 });
  }

  // ---- rendering ---------------------------------------------------------
  function render() {
    var idx = Math.min(state.current, steps.length);
    renderChrome(idx);
    els.step.innerHTML = '';
    if (idx >= steps.length) els.step.appendChild(finishCard());
    else els.step.appendChild(stepCard(steps[idx], state.answers[steps[idx].id]));
    renderNotes();
    renderDiagram();
    els.step.scrollIntoView({ block: 'nearest' });
  }

  function renderChrome(idx) {
    var done = Object.keys(state.answers).length;
    els.fill.style.width = Math.round(100 * done / steps.length) + '%';
    els.count.textContent = idx >= steps.length ? 'All ' + steps.length + ' steps done' : 'Step ' + (idx + 1) + ' of ' + steps.length;
    els.phase.textContent = idx >= steps.length ? 'Finished' : steps[idx].phase;
    els.dots.innerHTML = '';
    var reachable = firstOpen();
    steps.forEach(function (s, i) {
      var cls = 'sd-dot' + (state.answers[s.id] ? ' done' : '') + (i === idx ? ' now' : '');
      var b = h('button', {
        type: 'button', class: cls, title: (i + 1) + '. ' + s.title, 'aria-label': 'Step ' + (i + 1) + ': ' + s.title,
        'aria-current': i === idx ? 'step' : false, disabled: i > reachable,
        onclick: function () { go(i); },
      }, [String(i + 1)]);
      els.dots.appendChild(h('li', {}, [b]));
    });
  }

  function go(i) { state.current = i; save(); render(); }

  function stepCard(step, answered) {
    var card = h('div', { class: 'sd-card' });
    card.appendChild(h('h2', { class: 'sd-title', text: step.title }));
    card.appendChild(rich('div', 'sd-prompt-text', step.prompt));

    var body = h('div', { class: 'sd-body' });
    var actions = h('div', { class: 'sd-actions' });
    var feedback = h('div', { class: 'sd-feedback', hidden: !answered });
    var input = buildInput(step, answered, actions, feedback);
    body.appendChild(input.el);
    card.appendChild(body);

    if (!answered && step.hint) {
      var hint = h('div', { class: 'sd-hint', hidden: true, html: '<strong>Hint:</strong> ' + mini(step.hint).replace(/^<p>|<\/p>$/g, '') });
      actions.appendChild(h('button', {
        type: 'button', class: 'btn ghost sm sd-hint-btn',
        onclick: function (e) { hint.hidden = !hint.hidden; e.currentTarget.textContent = hint.hidden ? 'Show hint' : 'Hide hint'; },
      }, ['Show hint']));
      card.appendChild(hint);
    }
    card.appendChild(actions);
    card.appendChild(feedback);
    if (answered) input.show(answered, true);
    return card;
  }

  // Each builder returns { el, show(result, restoring) } and wires its own Check button into `actions`.
  function buildInput(step, answered, actions, feedback) {
    var builders = { choice: choiceInput, multi: multiInput, estimate: estimateInput, reflect: reflectInput, order: orderInput };
    var b = builders[step.type](step, answered);
    var checkLabel = step.type === 'reflect' ? 'Reveal model answer' : 'Check my answer';
    var check = h('button', { type: 'button', class: 'btn sm', disabled: true, onclick: function () {
      var res = b.read();
      if (!res) return;
      state.answers[step.id] = res;
      save();
      renderChrome(state.current);
      renderNotes();
      renderDiagram();
      check.hidden = true;
      Array.prototype.forEach.call(actions.querySelectorAll('.sd-hint-btn'), function (x) { x.hidden = true; });
      b.show(res, false);
    } }, [checkLabel]);
    b.onReady(function (ok) { check.disabled = !ok; });
    actions.insertBefore(check, actions.firstChild);
    if (answered) check.hidden = true;

    var origShow = b.show;
    b.show = function (res, restoring) {
      origShow(res);
      feedback.hidden = false;
      feedback.innerHTML = '';
      feedback.appendChild(feedbackBlock(step, res));
      if (!restoring) feedback.scrollIntoView({ block: 'nearest', behavior: 'smooth' });
    };
    return b;
  }

  function verdict(res) {
    if (res.verdict === 'good') return ['sd-good', 'Correct'];
    if (res.verdict === 'partial') return ['sd-partial', 'Close, but not quite'];
    if (res.verdict === 'done') return ['sd-good', 'Compare with the model answer'];
    return ['sd-bad', 'Not quite'];
  }

  function feedbackBlock(step, res) {
    var v = verdict(res);
    var box = h('div', { class: 'sd-fb ' + v[0] });
    box.appendChild(h('div', { class: 'sd-verdict', text: v[1] }));
    if (res.note) box.appendChild(h('p', { class: 'sd-note', text: res.note }));
    if (step.work) {
      var ul = h('ol', { class: 'sd-work' });
      step.work.forEach(function (w) { ul.appendChild(h('li', { html: mini(w).replace(/^<p>|<\/p>$/g, '') })); });
      box.appendChild(h('div', { class: 'sd-label', text: 'How to work it out' }));
      box.appendChild(ul);
    }
    box.appendChild(h('div', { class: 'sd-label', text: 'The takeaway' }));
    box.appendChild(rich('div', 'sd-explain', step.explain));
    if (step.pitfall) {
      box.appendChild(h('div', { class: 'sd-extra sd-pitfall' }, [h('strong', { text: 'Common mistake. ' }), h('span', { html: mini(step.pitfall).replace(/^<p>|<\/p>$/g, '') })]));
    }
    if (step.followup) {
      box.appendChild(h('div', { class: 'sd-extra sd-followup' }, [h('strong', { text: 'The interviewer may ask next. ' }), h('span', { html: mini(step.followup).replace(/^<p>|<\/p>$/g, '') })]));
    }
    if (step.chapter) {
      box.appendChild(h('p', { class: 'sd-learn-link' }, [
        'Learn more: ',
        h('a', { href: courseBase + step.chapter.href, target: '_blank', rel: 'noopener', text: step.chapter.title + ' ↗' }),
      ]));
    }
    var last = state.current >= steps.length - 1;
    box.appendChild(h('button', { type: 'button', class: 'btn', onclick: function () { go(state.current + 1); } },
      [last ? 'Finish' : 'Next step →']));
    return box;
  }

  // ---- input types -------------------------------------------------------
  function choiceInput(step, answered) {
    var name = 'c-' + step.id, readyCb = function () {};
    var wrap = h('fieldset', { class: 'sd-options' }, [h('legend', { class: 'sr-only', text: 'Choose one answer' })]);
    step.options.forEach(function (o, i) {
      var inp = h('input', { type: 'radio', name: name, value: i, disabled: !!answered, onchange: function () { readyCb(true); } });
      wrap.appendChild(h('label', { class: 'sd-opt', 'data-i': i }, [inp, h('span', { html: mini(o.text).replace(/^<p>|<\/p>$/g, '') })]));
    });
    return {
      el: wrap,
      onReady: function (cb) { readyCb = cb; },
      read: function () {
        var sel = wrap.querySelector('input:checked');
        if (!sel) return null;
        var i = Number(sel.value);
        return { picked: i, verdict: step.options[i].correct ? 'good' : 'bad' };
      },
      show: function (res) {
        step.options.forEach(function (o, i) {
          var lab = wrap.querySelector('[data-i="' + i + '"]');
          var inp = lab.querySelector('input');
          inp.checked = (i === res.picked); inp.disabled = true;
          if (o.correct) lab.classList.add('is-correct');
          else if (i === res.picked) lab.classList.add('is-wrong');
          lab.appendChild(h('small', { class: 'sd-why', text: (o.correct ? '✓ ' : '✗ ') + o.why }));
        });
      },
    };
  }

  function multiInput(step, answered) {
    var readyCb = function () {};
    var wrap = h('fieldset', { class: 'sd-options' }, [h('legend', { class: 'sr-only', text: 'Select all that apply' })]);
    function anyChecked() { return wrap.querySelectorAll('input:checked').length > 0; }
    step.options.forEach(function (o, i) {
      var inp = h('input', { type: 'checkbox', value: i, disabled: !!answered, onchange: function () { readyCb(anyChecked()); } });
      wrap.appendChild(h('label', { class: 'sd-opt', 'data-i': i }, [inp, h('span', { html: mini(o.text).replace(/^<p>|<\/p>$/g, '') })]));
    });
    return {
      el: wrap,
      onReady: function (cb) { readyCb = cb; },
      read: function () {
        var picked = Array.prototype.map.call(wrap.querySelectorAll('input:checked'), function (x) { return Number(x.value); });
        if (!picked.length) return null;
        var right = 0, wrong = 0, missed = 0;
        step.options.forEach(function (o, i) {
          var on = picked.indexOf(i) !== -1;
          if (on && o.correct) right++; else if (on) wrong++; else if (o.correct) missed++;
        });
        var v = wrong === 0 && missed === 0 ? 'good' : (right > 0 ? 'partial' : 'bad');
        var note = v === 'good' ? '' : 'You got ' + right + ' right' + (wrong ? ', picked ' + wrong + ' that do not belong' : '') + (missed ? ', and missed ' + missed : '') + '.';
        return { picked: picked, verdict: v, note: note };
      },
      show: function (res) {
        step.options.forEach(function (o, i) {
          var lab = wrap.querySelector('[data-i="' + i + '"]');
          var inp = lab.querySelector('input');
          var on = res.picked.indexOf(i) !== -1;
          inp.checked = on; inp.disabled = true;
          var mark;
          if (o.correct && on) { lab.classList.add('is-correct'); mark = '✓ '; }
          else if (o.correct) { lab.classList.add('is-missed'); mark = '↳ Should be selected. '; }
          else if (on) { lab.classList.add('is-wrong'); mark = '✗ '; }
          else mark = 'Leave out. ';
          lab.appendChild(h('small', { class: 'sd-why', text: mark + o.why }));
        });
      },
    };
  }

  function estimateInput(step, answered) {
    var readyCb = function () {};
    var inp = h('input', {
      type: 'text', inputmode: 'decimal', class: 'sd-num', placeholder: 'e.g. 5000 or 5k', autocomplete: 'off',
      'aria-label': 'Your estimate in ' + step.unit, disabled: !!answered,
      oninput: function () { readyCb(!isNaN(parseNumber(inp.value))); },
    });
    var el = h('div', { class: 'sd-estimate' }, [inp, h('span', { class: 'sd-unit', text: step.unit }),
      h('small', { class: 'muted', text: 'A rough number is fine. You can use k, M, B or T (4k = 4,000).' })]);
    return {
      el: el,
      onReady: function (cb) { readyCb = cb; },
      read: function () {
        var v = parseNumber(inp.value);
        if (isNaN(v) || v <= 0) return null;
        var ratio = Math.max(v / step.answer, step.answer / v);
        var verdict = ratio <= step.factor ? 'good' : (ratio <= step.factor * 3 ? 'partial' : 'bad');
        var note = 'You said ' + fmt(v) + ' ' + step.unit + '. A good estimate is about ' + fmt(step.answer) + ' ' + step.unit + '.';
        return { value: v, verdict: verdict, note: note };
      },
      show: function (res) { inp.value = fmt(res.value); inp.disabled = true; },
    };
  }

  function reflectInput(step, answered) {
    var readyCb = function () {};
    var ta = h('textarea', {
      rows: 5, class: 'sd-text', placeholder: 'Write your thinking here before you reveal the model answer (at least a sentence).',
      'aria-label': 'Your answer', disabled: !!answered,
      oninput: function () { readyCb(ta.value.trim().length >= 20); },
    });
    var model = h('div', { class: 'sd-model' });
    var el = h('div', {}, [ta, model]);
    return {
      el: el,
      onReady: function (cb) { readyCb = cb; },
      read: function () {
        var t = ta.value.trim();
        return t.length >= 20 ? { text: t, verdict: 'done', ticked: [] } : null;
      },
      show: function (res) {
        ta.value = res.text; ta.disabled = true;
        model.innerHTML = '';
        model.appendChild(h('div', { class: 'sd-label', text: 'Model answer' }));
        model.appendChild(rich('div', 'sd-model-text', step.model));
        model.appendChild(h('div', { class: 'sd-label', text: 'Tick the points your answer covered' }));
        var list = h('ul', { class: 'sd-points' });
        step.points.forEach(function (p, i) {
          var cb = h('input', { type: 'checkbox', checked: (res.ticked || []).indexOf(i) !== -1, onchange: function () {
            var t = [];
            Array.prototype.forEach.call(list.querySelectorAll('input'), function (x, j) { if (x.checked) t.push(j); });
            state.answers[step.id].ticked = t; save();
          } });
          list.appendChild(h('li', {}, [h('label', {}, [cb, h('span', { html: mini(p).replace(/^<p>|<\/p>$/g, '') })])]));
        });
        model.appendChild(list);
      },
    };
  }

  function orderInput(step, answered) {
    var readyCb = function () {};
    var n = step.items.length;
    // Start from a fixed scramble (so a reload shows the same list): item i goes to position (i * k) mod n.
    var k = [3, 5, 7, 2].filter(function (c) { return gcd(c, n) === 1; })[0] || 1;
    var seq = [];
    for (var i = 0; i < n; i++) seq.push((i * k + 1) % n);
    if (seq.every(function (v, i) { return v === i; })) seq.reverse();
    var list = h('ol', { class: 'sd-order' });
    var locked = !!answered;
    function gcd(a, b) { return b ? gcd(b, a % b) : a; }
    function draw(marks) {
      list.innerHTML = '';
      seq.forEach(function (idx, pos) {
        var it = step.items[idx];
        var li = h('li', { class: 'sd-order-item' + (marks ? (idx === pos ? ' is-correct' : ' is-wrong') : '') });
        li.appendChild(h('span', { class: 'sd-order-text', html: mini(it.text).replace(/^<p>|<\/p>$/g, '') }));
        if (!locked) {
          li.appendChild(h('span', { class: 'sd-order-btns' }, [
            h('button', { type: 'button', class: 'btn ghost sm', 'aria-label': 'Move up', disabled: pos === 0, onclick: function () { move(pos, -1); } }, ['↑']),
            h('button', { type: 'button', class: 'btn ghost sm', 'aria-label': 'Move down', disabled: pos === n - 1, onclick: function () { move(pos, 1); } }, ['↓']),
          ]));
        } else if (marks) {
          li.appendChild(h('small', { class: 'sd-why', text: (idx === pos ? '✓ ' : '✗ Belongs at step ' + (idx + 1) + '. ') + it.why }));
        }
        list.appendChild(li);
      });
    }
    function move(pos, d) {
      var t = seq[pos]; seq[pos] = seq[pos + d]; seq[pos + d] = t;
      draw(false);
      var b = list.children[pos + d] && list.children[pos + d].querySelector(d < 0 ? '[aria-label="Move up"]' : '[aria-label="Move down"]');
      if (b && !b.disabled) b.focus();
    }
    draw(false);
    return {
      el: h('div', {}, [h('p', { class: 'muted small', text: 'Use the arrows to put these in the right order, first at the top.' }), list]),
      onReady: function (cb) { readyCb = cb; cb(true); },
      read: function () {
        var right = seq.filter(function (idx, pos) { return idx === pos; }).length;
        var v = right === n ? 'good' : (right >= Math.ceil(n / 2) ? 'partial' : 'bad');
        return { order: seq.slice(), verdict: v, note: right === n ? '' : 'You placed ' + right + ' of ' + n + ' in the right position.' };
      },
      show: function (res) { seq = res.order.slice(); locked = true; draw(true); },
    };
  }

  function finishCard() {
    var stmt = problem.statement || {};
    var sum = stmt.summary || {};
    var done = steps.filter(function (s) { return state.answers[s.id]; });
    var scoredSteps = steps.filter(function (s) { return s.type !== 'reflect'; });
    var good = scoredSteps.filter(function (s) { return state.answers[s.id] && state.answers[s.id].verdict === 'good'; }).length;
    var card = h('div', { class: 'sd-card sd-finish' });
    card.appendChild(h('h2', { class: 'sd-title', text: 'Design complete 🎉' }));
    card.appendChild(h('p', { text: 'You built the whole design step by step. You got ' + good + ' of ' + scoredSteps.length + ' scored questions right first time (' + done.length + ' of ' + steps.length + ' steps finished). The diagram below is the system you designed.' }));

    // Score per phase, so the learner can see which part of the interview to practise next.
    var phases = [], byPhase = {};
    scoredSteps.forEach(function (s) {
      if (!byPhase[s.phase]) { byPhase[s.phase] = { total: 0, good: 0 }; phases.push(s.phase); }
      byPhase[s.phase].total++;
      if (state.answers[s.id] && state.answers[s.id].verdict === 'good') byPhase[s.phase].good++;
    });
    if (phases.length) {
      card.appendChild(h('h3', { text: 'Scorecard by phase' }));
      var sc = h('ul', { class: 'sd-score' });
      phases.forEach(function (ph) {
        var r = byPhase[ph], pct = Math.round(100 * r.good / r.total);
        sc.appendChild(h('li', {}, [
          h('span', { class: 'sd-score-name', text: ph }),
          h('span', { class: 'sd-score-bar', 'aria-hidden': 'true' }, [h('span', { style: 'width:' + pct + '%' })]),
          h('span', { class: 'sd-score-num', text: r.good + '/' + r.total }),
        ]));
      });
      card.appendChild(sc);
    }

    if (sum.takeaways && sum.takeaways.length) {
      card.appendChild(h('h3', { text: 'Say this in the interview' }));
      card.appendChild(h('ul', { class: 'sd-takeaways' }, sum.takeaways.map(function (t) { return h('li', { html: mini(t).replace(/^<p>|<\/p>$/g, '') }); })));
    }
    if (sum.tradeoffs && sum.tradeoffs.length) {
      card.appendChild(h('h3', { text: 'Trade-offs you made' }));
      var tb = h('table', { class: 'sd-tradeoffs' }, [h('thead', {}, [h('tr', {}, [h('th', { text: 'Choice' }), h('th', { text: 'What you gain' }), h('th', { text: 'What it costs' })])])]);
      var body = h('tbody');
      sum.tradeoffs.forEach(function (t) {
        body.appendChild(h('tr', {}, [h('td', { html: mini(t.choice).replace(/^<p>|<\/p>$/g, '') }), h('td', { text: t.gain }), h('td', { text: t.cost })]));
      });
      tb.appendChild(body);
      card.appendChild(h('div', { class: 'sd-table-wrap' }, [tb]));
    }
    if (sum.extensions && sum.extensions.length) {
      card.appendChild(h('h3', { text: 'If you have time left' }));
      card.appendChild(h('ul', {}, sum.extensions.map(function (t) { return h('li', { html: mini(t).replace(/^<p>|<\/p>$/g, '') }); })));
    }

    card.appendChild(h('h3', { text: 'Next' }));
    card.appendChild(h('ul', {}, [
      h('li', {}, ['Redraw the diagram from memory and explain each box out loud in 5 minutes.']),
      h('li', {}, [h('a', { href: courseBase, text: 'Revisit the System Design course chapters you found hard' }), '.']),
      h('li', {}, [h('a', { href: '/system-design/', text: 'Try another problem' }), '.']),
    ]));
    var row = h('div', { class: 'sd-actions' });
    var copyBtn = h('button', { type: 'button', class: 'btn', onclick: function () { copyNotes(copyBtn); } }, ['Copy my design notes']);
    row.appendChild(copyBtn);
    row.appendChild(h('button', { type: 'button', class: 'btn ghost', onclick: function () { go(0); } }, ['Review from step 1']));
    card.appendChild(row);
    return card;
  }

  // The "locked in" decisions as plain text, ready to paste into a notebook.
  function notesText() {
    var lines = [problem.title, ''];
    steps.forEach(function (s) {
      if (!state.answers[s.id] || !s.adds || !s.adds.notes) return;
      s.adds.notes.forEach(function (t) { lines.push('- ' + t); });
    });
    return lines.join('\n');
  }
  function copyNotes(btn) {
    var text = notesText();
    function ok() { btn.textContent = 'Copied ✓'; setTimeout(function () { btn.textContent = 'Copy my design notes'; }, 2000); }
    if (navigator.clipboard && navigator.clipboard.writeText) navigator.clipboard.writeText(text).then(ok, function () { window.prompt('Copy your notes:', text); });
    else window.prompt('Copy your notes:', text);
  }

  // ---- "locked in so far" notes (left) ----------------------------------
  function renderNotes() {
    els.notes.innerHTML = '';
    var n = 0;
    steps.forEach(function (s) {
      if (!state.answers[s.id] || !s.adds || !s.adds.notes) return;
      s.adds.notes.forEach(function (t) { els.notes.appendChild(h('li', { text: t })); n++; });
    });
    els.notesEmpty.hidden = n > 0;
  }

  // ---- architecture diagram (right) ---------------------------------------
  // A problem can ship its own diagram in statement.diagram = { viewBox, nodes: {id: {x, y, w, h?, label, kind?}},
  // edges: [[from, to, label?, 'dashed'?]] }. Without one, the TinyURL layout below is used.
  var DEFAULT_DIAGRAM = {
    viewBox: '0 0 620 250',
    nodes: {
      client:  { x: 10,  y: 100, w: 90,  label: 'Client', kind: 'client' },
      lb:      { x: 135, y: 100, w: 110, label: 'Load balancer', kind: 'edge' },
      app:     { x: 280, y: 100, w: 120, label: 'App servers', kind: 'service' },
      idgen:   { x: 280, y: 190, w: 120, label: 'ID ranges (coordinator)', kind: 'service' },
      cache:   { x: 450, y: 40,  w: 150, label: 'Cache', kind: 'cache' },
      db:      { x: 450, y: 125, w: 150, label: 'Key-value DB', kind: 'data' },
      replica: { x: 450, y: 195, w: 150, label: 'Replicas (multi-zone)', kind: 'data' },
    },
    edges: [['client', 'lb'], ['lb', 'app'], ['app', 'idgen'], ['app', 'cache'], ['app', 'db'], ['db', 'replica'], ['cache', 'db', 'miss', 'dashed']],
  };
  var KIND_NAMES = { client: 'Client', edge: 'Entry point', service: 'Service', cache: 'Cache', data: 'Data store', queue: 'Queue or stream', external: 'External system' };
  var DIAGRAM = (problem.statement && problem.statement.diagram) || DEFAULT_DIAGRAM;
  var NODES = DIAGRAM.nodes, EDGES = DIAGRAM.edges || [];
  var NH = 44;
  function nh(n) { return n.h || NH; }

  function renderDiagram() {
    var shown = {}, labels = {}, order = [];
    steps.forEach(function (s) {
      if (!state.answers[s.id] || !s.adds) return;
      (s.adds.components || []).forEach(function (c) { if (NODES[c] && !shown[c]) { shown[c] = true; order.push(c); } });
      Object.keys(s.adds.labels || {}).forEach(function (k) { labels[k] = s.adds.labels[k]; });
    });
    els.diagram.innerHTML = '';
    if (!order.length) {
      els.diagram.appendChild(h('p', { class: 'muted small', text: 'Components appear here as you decide on them.' }));
      return;
    }
    var NS = 'http://www.w3.org/2000/svg';
    var svg = document.createElementNS(NS, 'svg');
    svg.setAttribute('viewBox', DIAGRAM.viewBox || '0 0 620 250');
    svg.setAttribute('class', 'sd-svg');
    svg.setAttribute('role', 'img');
    svg.setAttribute('aria-label', 'Architecture so far: ' + order.map(function (c) { return labels[c] || NODES[c].label; }).join(', '));
    function mk(tag, attrs) {
      var e = document.createElementNS(NS, tag);
      Object.keys(attrs).forEach(function (k) { e.setAttribute(k, attrs[k]); });
      return e;
    }
    var defs = mk('defs', {});
    var mark = mk('marker', { id: 'sd-arrow', viewBox: '0 0 10 10', refX: 9, refY: 5, markerWidth: 7, markerHeight: 7, orient: 'auto-start-reverse' });
    mark.appendChild(mk('path', { d: 'M0,0 L10,5 L0,10 z', class: 'sd-head' }));
    defs.appendChild(mark); svg.appendChild(defs);

    function anchor(a, b) {
      var A = NODES[a], B = NODES[b];
      if (A.x + A.w <= B.x) return [A.x + A.w, A.y + nh(A) / 2, B.x, B.y + nh(B) / 2];
      if (B.x + B.w <= A.x) return [A.x, A.y + nh(A) / 2, B.x + B.w, B.y + nh(B) / 2];
      var down = B.y > A.y;
      return [A.x + A.w / 2, down ? A.y + nh(A) : A.y, B.x + B.w / 2, down ? B.y : B.y + nh(B)];
    }
    EDGES.forEach(function (e) {
      if (!shown[e[0]] || !shown[e[1]]) return;
      var p = anchor(e[0], e[1]);
      svg.appendChild(mk('line', { x1: p[0], y1: p[1], x2: p[2], y2: p[3], class: 'sd-edge' + (e[3] === 'dashed' ? ' sd-dash' : ''), 'marker-end': 'url(#sd-arrow)' }));
      if (e[2]) {
        var t = mk('text', { x: (p[0] + p[2]) / 2, y: (p[1] + p[3]) / 2 - 5, 'text-anchor': 'middle', class: 'sd-edge-label' });
        t.textContent = e[2];
        svg.appendChild(t);
      }
    });
    var latest = steps.filter(function (s) { return state.answers[s.id] && s.adds && (s.adds.components || []).length; }).pop();
    var fresh = latest ? latest.adds.components : [];
    var kinds = {};
    order.forEach(function (c) {
      var n = NODES[c], kind = n.kind || 'service';
      kinds[kind] = true;
      var g = mk('g', { class: 'sd-node k-' + kind + (fresh.indexOf(c) !== -1 ? ' new' : '') });
      g.appendChild(mk('rect', { x: n.x, y: n.y, width: n.w, height: nh(n), rx: 10 }));
      var label = labels[c] || n.label, lines = String(label).split('\n');
      var tx = mk('text', { x: n.x + n.w / 2, y: n.y + nh(n) / 2 - (lines.length - 1) * 8, 'text-anchor': 'middle', 'dominant-baseline': 'middle' });
      lines.forEach(function (ln, i) {
        var ts = mk('tspan', { x: n.x + n.w / 2, dy: i ? 16 : 0 });
        ts.textContent = ln;
        tx.appendChild(ts);
      });
      g.appendChild(tx); svg.appendChild(g);
    });
    els.diagram.appendChild(svg);
    var legend = h('ul', { class: 'sd-legend', 'aria-label': 'Colour key' });
    Object.keys(KIND_NAMES).forEach(function (k) {
      if (kinds[k]) legend.appendChild(h('li', {}, [h('i', { class: 'sw k-' + k }), KIND_NAMES[k]]));
    });
    els.diagram.appendChild(legend);
  }

  els.reset.addEventListener('click', function () {
    if (!confirm('Clear your answers for this problem and start again?')) return;
    state = { answers: {}, current: 0 };
    save(); render();
  });

  function start() {
    state.current = Math.min(state.current, firstOpen());
    render();
  }
  if (progressUrl && saveUrl) loadFromAccount().then(start, start);   // on failure fall back to this browser's copy
  else start();
})();
