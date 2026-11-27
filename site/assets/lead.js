/* Equipcn: заявки, UTM, аналитика. Подключается на всех страницах сайта.
   Настройки приходят из window.EQ_CFG (вставляет build.py из data/tracking.json):
   {endpoint, conv:{form,whatsapp,phone}, gtm:boolean, wa:'77787586354'} */
(function () {
  'use strict';
  var CFG = window.EQ_CFG || {};
  var WA = 'https://wa.me/' + (CFG.wa || '77787586354');
  var LS = window.localStorage, SS = window.sessionStorage;
  function get(s, k) { try { return JSON.parse(s.getItem(k) || 'null'); } catch (e) { return null; } }
  function set(s, k, v) { try { s.setItem(k, JSON.stringify(v)); } catch (e) {} }

  /* ---------- UTM и источник визита: сохраняем между страницами (90 дней) ---------- */
  var KEYS = ['utm_source', 'utm_medium', 'utm_campaign', 'utm_term', 'utm_content', 'gclid', 'yclid', 'fbclid'];
  (function captureUtm() {
    var q = new URLSearchParams(location.search), u = {}, any = false;
    KEYS.forEach(function (k) { var v = q.get(k); if (v) { u[k] = v.slice(0, 200); any = true; } });
    if (any) set(LS, 'eq_utm', {v: u, t: Date.now()});
    var ref = document.referrer && document.referrer.indexOf(location.host) < 0 ? document.referrer : '';
    if (!get(SS, 'eq_land')) set(SS, 'eq_land', {page: location.href.split('#')[0], ref: ref});
    if (any || ref) set(LS, 'eq_src', {page: location.href.split('#')[0], ref: ref, t: Date.now()});
  })();
  function utm() { var x = get(LS, 'eq_utm'); return x && Date.now() - x.t < 90 * 864e5 ? x.v : {}; }

  /* ---------- события аналитики (без дублей) ---------- */
  function ev(name, params) {
    params = params || {};
    try {
      if (CFG.gtm) { (window.dataLayer = window.dataLayer || []).push(Object.assign({event: name}, params)); }
      else if (window.gtag) { gtag('event', name, params); }
    } catch (e) {}
  }
  function adsConv(kind, extra) {
    var c = (CFG.conv || {})[kind];
    if (c && window.gtag) try { gtag('event', 'conversion', Object.assign({send_to: c}, extra || {})); } catch (e) {}
  }
  window.EQ = {ev: ev};

  document.addEventListener('click', function (e) {
    var a = e.target.closest && e.target.closest('a');
    if (!a) return;
    var h = a.getAttribute('href') || '';
    if (h.indexOf('https://wa.me') === 0) { ev('whatsapp_click', {link_text: (a.textContent || '').trim().slice(0, 60), page_location: location.href}); adsConv('whatsapp'); }
    else if (h.indexOf('tel:') === 0) { ev('phone_click', {page_location: location.href}); adsConv('phone'); }
  }, true);

  /* ---------- форма заявки ---------- */
  var FORM_HTML = function (o) {
    o = o || {};
    var id = 'lf' + Math.random().toString(36).slice(2, 7);
    return '<form class="lf" data-lead novalidate>' +
      (o.title ? '<div class="lf-t">' + o.title + '</div>' : '') +
      '<label for="' + id + 'n">Какое оборудование вам необходимо?<textarea id="' + id + 'n" name="need" rows="2" maxlength="2000" placeholder="Например: линия газоблоков 100 м³/сутки или ссылка/модель">' + (o.need ? esc(o.need) : '') + '</textarea></label>' +
      '<label for="' + id + 'p">Номер телефона<input id="' + id + 'p" name="phone" type="tel" inputmode="tel" autocomplete="tel" placeholder="+7 7__ ___ __ __" required></label>' +
      '<label class="lf-file" for="' + id + 'f"><input id="' + id + 'f" name="file" type="file" accept="image/*,.pdf,.doc,.docx,.xls,.xlsx,.txt"><span>📎 Прикрепить фото или ТЗ <small>(необязательно, до 10 МБ)</small></span></label>' +
      '<input type="hidden" name="product" value="' + esc(o.product || '') + '">' +
      '<input class="lf-hp" name="website" tabindex="-1" autocomplete="off" aria-hidden="true">' +
      '<button class="btn btn-main lf-b" type="submit">Получить стоимость с доставкой</button>' +
      '<div class="lf-out" role="status" aria-live="polite"></div>' +
      '<p class="lf-note">Без регистрации. Нажимая кнопку, вы соглашаетесь на <a href="/privacy">обработку данных</a>.</p></form>';
  };
  function esc(t) { return String(t || '').replace(/[&<>"]/g, function (c) { return {'&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;'}[c]; }); }
  window.EQ.formHTML = FORM_HTML;

  function readFile(file) {
    return new Promise(function (res, rej) {
      if (!file) return res(null);
      if (file.size > 10 * 1024 * 1024) return rej('size');
      var r = new FileReader();
      r.onload = function () { res({name: file.name, type: file.type, b64: String(r.result).split(',')[1]}); };
      r.onerror = function () { rej('read'); };
      r.readAsDataURL(file);
    });
  }
  function waText(need, phone, product) {
    return 'Здравствуйте! Заявка с сайта equipcngroup.com\nЧто нужно: ' + (need || '—') + (product ? '\nТовар: ' + product : '') + '\nТелефон: ' + phone;
  }
  function send(payload) {
    return fetch(CFG.endpoint, {method: 'POST', headers: {'Content-Type': 'text/plain;charset=utf-8'}, body: JSON.stringify(payload), redirect: 'follow'})
      .then(function (r) { return r.json(); });
  }
  // заявки, которые не ушли из-за сети, отправляем повторно при следующем открытии сайта
  (function retryQueue() {
    var q = get(LS, 'eq_queue') || [];
    if (!q.length || !CFG.endpoint) return;
    set(LS, 'eq_queue', []);
    q.forEach(function (p) { send(p).then(function (r) { if (r && r.ok) ev('generate_lead', {lead_id: r.id, retry: true}); }).catch(function () { var x = get(LS, 'eq_queue') || []; x.push(p); set(LS, 'eq_queue', x); }); });
  })();

  function bind(f) {
    if (f.__eq) return; f.__eq = true;
    var t0 = Date.now(), started = false;
    f.addEventListener('input', function () { if (!started) { started = true; ev('form_start', {form_location: formPlace(f)}); } });
    var fileIn = f.querySelector('input[type=file]');
    if (fileIn) fileIn.addEventListener('change', function () {
      var s = f.querySelector('.lf-file span'); if (s && fileIn.files[0]) s.textContent = '📎 ' + fileIn.files[0].name;
    });
    f.addEventListener('submit', function (e) {
      e.preventDefault();
      var out = f.querySelector('.lf-out'), btn = f.querySelector('button[type=submit]');
      var need = (f.need.value || '').trim(), phone = (f.phone.value || '').trim(), product = f.product ? f.product.value : '';
      var file = fileIn && fileIn.files[0];
      out.className = 'lf-out';
      if (phone.replace(/\D/g, '').length < 10) { out.textContent = 'Укажите номер телефона, чтобы мы могли с вами связаться.'; out.classList.add('err'); f.phone.focus(); return; }
      if (!need && !product && !file) { out.textContent = 'Напишите, какое оборудование нужно, или прикрепите фото.'; out.classList.add('err'); f.need.focus(); return; }
      var wa = WA + '?text=' + encodeURIComponent(waText(need, phone, product));
      if (!CFG.endpoint) { // приём заявок ещё не подключён — передаём заявку через WhatsApp
        out.innerHTML = 'Остался один шаг: <a class="btn btn-main" target="_blank" rel="noopener" href="' + wa + '">Отправить заявку в WhatsApp</a>';
        return;
      }
      btn.disabled = true; btn.textContent = 'Отправляем…';
      var land = get(SS, 'eq_land') || {}, src = get(LS, 'eq_src') || {};
      readFile(file).then(function (fd) {
        var p = {need: need, phone: phone, product: product, page: location.href.split('#')[0], landing: src.page || land.page || '',
          referrer: src.ref || land.ref || '', utm: utm(), device: (matchMedia('(max-width:820px)').matches ? 'mobile' : 'desktop') + ' · ' + navigator.language,
          website: f.website ? f.website.value : '', t_fill: Date.now() - t0};
        if (fd) { p.file_name = fd.name; p.file_type = fd.type; p.file_b64 = fd.b64; }
        return send(p).catch(function (err) { var x = get(LS, 'eq_queue') || []; delete p.file_b64; x.push(p); set(LS, 'eq_queue', x); throw err; });
      }).then(function (r) {
        if (!r || !r.ok) throw new Error(r && r.error || 'server');
        var done = get(SS, 'eq_leads') || [];
        if (done.indexOf(r.id) < 0) { // одна заявка = одна конверсия
          done.push(r.id); set(SS, 'eq_leads', done);
          ev('generate_lead', {lead_id: r.id, form_location: formPlace(f), currency: 'KZT', value: 1});
          adsConv('form', {transaction_id: r.id});
        }
        f.innerHTML = '<div class="lf-ok"><b>Спасибо! Ваша заявка принята.</b><p>Наш специалист свяжется с вами для уточнения деталей.</p>' +
          '<a class="btn btn-line" target="_blank" rel="noopener" href="' + wa + '">Написать в WhatsApp</a></div>';
      }).catch(function (err) {
        var msg = err === 'size' ? 'Файл больше 10 МБ. Уменьшите его или отправьте в WhatsApp.' : 'Не удалось отправить заявку. Попробуйте ещё раз или отправьте её в WhatsApp — это займёт секунду.';
        ev('form_error', {error: String(err && err.message || err).slice(0, 60), form_location: formPlace(f)});
        out.innerHTML = esc(msg) + ' <a target="_blank" rel="noopener" href="' + wa + '">Отправить в WhatsApp →</a>';
        out.classList.add('err');
        btn.disabled = false; btn.textContent = 'Получить стоимость с доставкой';
      });
    });
  }
  function formPlace(f) { var s = f.closest('[data-place]'); return s ? s.getAttribute('data-place') : location.pathname; }
  function bindAll(root) { (root || document).querySelectorAll('form[data-lead]').forEach(bind); }
  window.EQ.bind = bindAll;

  // «Узнать стоимость»: подставляем товар в ближайшую форму
  document.addEventListener('click', function (e) {
    var b = e.target.closest && e.target.closest('[data-ask]');
    if (!b) return;
    e.preventDefault();
    var f = document.querySelector(b.getAttribute('data-target') || '#lead form[data-lead]') || document.querySelector('form[data-lead]');
    if (!f) return;
    var name = b.getAttribute('data-ask');
    if (f.product) f.product.value = name;
    if (f.need && !f.need.value) f.need.value = 'Нужна стоимость с доставкой: ' + name;
    f.scrollIntoView({behavior: 'smooth', block: 'center'});
    setTimeout(function () { f.phone && f.phone.focus({preventScroll: true}); }, 400);
  });

  /* ---------- блок доверия: проекты, отзывы, команда, видео, реквизиты из Google Таблицы ---------- */
  function trust() {
    var box = document.getElementById('trust');
    if (!box || !CFG.endpoint) return;
    fetch(CFG.endpoint + '?content=1').then(function (r) { return r.json(); }).then(function (d) {
      if (!d || !d.ok) return;
      var h = '';
      function pic(u) { return u ? '<img loading="lazy" referrerpolicy="no-referrer" src="' + esc(u) + '" alt="">' : ''; }
      if (d.projects && d.projects.length) h += '<h3>Реализованные проекты</h3><div class="tr-grid">' + d.projects.map(function (p) {
        return '<div class="tr-c">' + pic(p.photos[0]) + '<b>' + esc(p.title) + '</b>' + (p.city ? '<small>' + esc(p.city) + '</small>' : '') + '<p>' + esc(p.text) + '</p>' + (p.video ? '<a href="' + esc(p.video) + '" target="_blank" rel="noopener">Смотреть видео →</a>' : '') + '</div>'; }).join('') + '</div>';
      if (d.videos && d.videos.length) h += '<h3>Видео с заводов</h3><div class="tr-grid">' + d.videos.map(function (v) {
        return '<a class="tr-c tr-v" href="' + esc(v.url) + '" target="_blank" rel="noopener">▶ <b>' + esc(v.title) + '</b></a>'; }).join('') + '</div>';
      if (d.reviews && d.reviews.length) h += '<h3>Отзывы клиентов</h3><div class="tr-grid">' + d.reviews.map(function (r) {
        return '<div class="tr-c">' + pic(r.photo) + '<p>«' + esc(r.text) + '»</p><b>' + esc(r.name) + '</b><small>' + esc([r.company, r.city].filter(Boolean).join(', ')) + '</small>' + (r.link ? '<a href="' + esc(r.link) + '" target="_blank" rel="noopener">Источник →</a>' : '') + '</div>'; }).join('') + '</div>';
      if (d.team && d.team.length) h += '<h3>Команда</h3><div class="tr-grid tr-team">' + d.team.map(function (t) {
        return '<div class="tr-c">' + pic(t.photo) + '<b>' + esc(t.name) + '</b><small>' + esc(t.role) + '</small></div>'; }).join('') + '</div>';
      var rq = d.requisites || {};
      var info = ['Договор', 'Условия оплаты', 'Доставка'].filter(function (k) { return rq[k]; });
      if (info.length) h += '<h3>Договор и оплата</h3><div class="tr-grid">' + info.map(function (k) { return '<div class="tr-c"><b>' + k + '</b><p>' + esc(rq[k]) + '</p></div>'; }).join('') + '</div>';
      var req = Object.keys(rq).filter(function (k) { return rq[k] && info.indexOf(k) < 0; });
      if (req.length) h += '<h3>Реквизиты</h3><table class="tr-req">' + req.map(function (k) { return '<tr><td>' + esc(k) + '</td><td>' + esc(rq[k]) + '</td></tr>'; }).join('') + '</table>';
      if (h) { box.querySelector('.tr-body').innerHTML = h; box.hidden = false; }
    }).catch(function () {});
  }

  function ready() {
    document.querySelectorAll('[data-leadform]').forEach(function (el) {
      el.innerHTML = FORM_HTML({title: el.getAttribute('data-title') || '', need: el.getAttribute('data-need') || '', product: el.getAttribute('data-product') || ''});
    });
    bindAll();
    trust();
    var vi = document.querySelector('[data-view-item]');
    if (vi) ev('view_item', {item_id: vi.getAttribute('data-view-item'), item_name: vi.getAttribute('data-name') || '', item_category: vi.getAttribute('data-cat') || ''});
    var vl = document.querySelector('[data-view-list]');
    if (vl) ev('view_item_list', {item_list_id: vl.getAttribute('data-view-list'), item_list_name: vl.getAttribute('data-name') || ''});
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', ready); else ready();
})();
