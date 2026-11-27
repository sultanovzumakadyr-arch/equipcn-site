/**
 * Equipcn — приём заявок с сайта equipcngroup.com
 *
 * Где хранится: эта Google Таблица (лист «Заявки») + папка на Google Диске для файлов.
 * Доступ: только у тех, с кем вы поделились таблицей. Сайт может только ДОБАВЛЯТЬ заявки, читать их не может.
 * Уведомления: письмо владельцу таблицы и (по желанию) сообщение в Telegram.
 *
 * Установка (один раз):
 *   1. Расширения → Apps Script → вставить этот код → Сохранить.
 *   2. Выбрать функцию setup → Выполнить → разрешить доступ.
 *   3. Начать развёртывание → Новое развёртывание → Тип «Веб-приложение»,
 *      «Выполнять от имени: меня», «Доступ: все» → Развернуть → скопировать URL веб-приложения.
 *   4. Telegram (по желанию): в таблице меню «Equipcn» → «Подключить Telegram».
 */

var SHEET = 'Заявки';
var HEAD = ['№', 'Дата и время', 'Телефон', 'Что нужно', 'Товар / код', 'Файл', 'Источник', 'utm_source', 'utm_medium',
  'utm_campaign', 'utm_term', 'utm_content', 'gclid / yclid', 'Страница заявки', 'Первая страница визита', 'Откуда пришёл (referrer)',
  'Устройство', 'Статус', 'Менеджер', 'Комментарий', 'ID заявки'];
var STATUSES = ['Новая', 'В работе', 'Отправлено КП', 'Переговоры', 'Оплачено', 'Отказ'];
var MAX_FILE = 10 * 1024 * 1024; // 10 МБ

function setup() {
  var ss = SpreadsheetApp.getActive();
  var sh = ss.getSheetByName(SHEET) || ss.insertSheet(SHEET, 0);
  sh.getRange(1, 1, 1, HEAD.length).setValues([HEAD]).setFontWeight('bold').setBackground('#0B3D91').setFontColor('#ffffff');
  sh.setFrozenRows(1);
  sh.setColumnWidths(1, HEAD.length, 130);
  sh.setColumnWidth(4, 320); sh.setColumnWidth(5, 220); sh.setColumnWidth(14, 260); sh.setColumnWidth(20, 260);
  var rule = SpreadsheetApp.newDataValidation().requireValueInList(STATUSES, true).build();
  sh.getRange(2, 18, 2000, 1).setDataValidation(rule);
  var managers = ss.getSheetByName('Менеджеры') || ss.insertSheet('Менеджеры');
  if (!managers.getRange('A1').getValue()) managers.getRange('A1:A2').setValues([['Менеджер'], ['Улугбек']]).setFontWeight('normal');
  managers.getRange('A1').setFontWeight('bold');
  var mrule = SpreadsheetApp.newDataValidation().requireValueInRange(managers.getRange('A2:A50'), true).build();
  sh.getRange(2, 19, 2000, 1).setDataValidation(mrule);
  // цвета статусов
  var colors = {'Новая': '#fde68a', 'В работе': '#bfdbfe', 'Отправлено КП': '#ddd6fe', 'Переговоры': '#fbcfe8', 'Оплачено': '#bbf7d0', 'Отказ': '#e5e7eb'};
  var range = sh.getRange(2, 18, 2000, 1);
  var rules = Object.keys(colors).map(function (s) {
    return SpreadsheetApp.newConditionalFormatRule().whenTextEqualTo(s).setBackground(colors[s]).setRanges([range]).build();
  });
  sh.setConditionalFormatRules(rules);
  buildReport_(ss);
  setupContent_(ss);
  folder_();
  PropertiesService.getScriptProperties().setProperty('NOTIFY_EMAIL', Session.getEffectiveUser().getEmail());
  SpreadsheetApp.getActive().toast('Готово. Теперь: Начать развёртывание → Веб-приложение.', 'Equipcn', 10);
}

function buildReport_(ss) {
  var r = ss.getSheetByName('Отчёт') || ss.insertSheet('Отчёт');
  r.clear();
  r.getRange('A1').setValue('Заявки по источникам').setFontWeight('bold').setFontSize(13);
  r.getRange('A2').setFormula("=QUERY('Заявки'!A2:U,\"select G, count(A) where A is not null group by G order by count(A) desc label G 'Источник', count(A) 'Заявок'\",0)");
  r.getRange('D1').setValue('По кампаниям (utm_campaign)').setFontWeight('bold').setFontSize(13);
  r.getRange('D2').setFormula("=QUERY('Заявки'!A2:U,\"select H, J, count(A) where A is not null group by H, J order by count(A) desc label H 'utm_source', J 'utm_campaign', count(A) 'Заявок'\",0)");
  r.getRange('H1').setValue('По статусам').setFontWeight('bold').setFontSize(13);
  r.getRange('H2').setFormula("=QUERY('Заявки'!A2:U,\"select R, count(A) where A is not null group by R label R 'Статус', count(A) 'Заявок'\",0)");
  r.getRange('K1').setValue('По неделям').setFontWeight('bold').setFontSize(13);
  r.getRange('K2').setFormula("=QUERY({ARRAYFORMULA(IF('Заявки'!B2:B=\"\",,TEXT('Заявки'!B2:B-WEEKDAY('Заявки'!B2:B,3),\"yyyy-mm-dd\"))),'Заявки'!A2:A},\"select Col1, count(Col2) where Col2 is not null group by Col1 order by Col1 desc label Col1 'Неделя с', count(Col2) 'Заявок'\",0)");
  r.getRange('N1').setValue('Страницы, с которых пришли заявки').setFontWeight('bold').setFontSize(13);
  r.getRange('N2').setFormula("=QUERY('Заявки'!A2:U,\"select N, count(A) where A is not null group by N order by count(A) desc label N 'Страница', count(A) 'Заявок'\",0)");
  r.getRange('A20').setValue('Конверсию (заявки ÷ посетители) смотрите в Google Analytics 4: Отчёты → Привлечение → Источники трафика, ключевое событие generate_lead.').setFontColor('#5b6b82');
}

function folder_() {
  var p = PropertiesService.getScriptProperties();
  var id = p.getProperty('FOLDER_ID');
  if (id) { try { return DriveApp.getFolderById(id); } catch (e) {} }
  var f = DriveApp.createFolder('Equipcn — файлы заявок');
  p.setProperty('FOLDER_ID', f.getId());
  return f;
}

function onOpen() {
  SpreadsheetApp.getUi().createMenu('Equipcn')
    .addItem('Подключить Telegram', 'connectTelegram')
    .addItem('Проверить уведомления', 'testNotify')
    .addItem('Обновить отчёт и оформление', 'setup')
    .addToUi();
}

function json_(o) {
  return ContentService.createTextOutput(JSON.stringify(o)).setMimeType(ContentService.MimeType.JSON);
}

/* Материалы для сайта (только листы «Сайт: …», заявки наружу не отдаются) */
var CONTENT = {
  'Сайт: реквизиты': ['Поле', 'Значение'],
  'Сайт: проекты': ['Название', 'Город', 'Описание', 'Фото (ссылки через запятую)', 'Видео (ссылка)', 'Показывать (да/нет)'],
  'Сайт: отзывы': ['Имя', 'Компания', 'Город', 'Текст отзыва', 'Ссылка на источник', 'Фото', 'Показывать (да/нет)'],
  'Сайт: команда': ['Имя', 'Должность', 'Фото', 'Показывать (да/нет)'],
  'Сайт: видео заводов': ['Название', 'Ссылка (YouTube, TikTok, Drive)', 'Показывать (да/нет)']
};
var REQ_FIELDS = ['Компания', 'БИН', 'Юридический адрес', 'Банк', 'ИИК', 'БИК', 'Договор', 'Условия оплаты', 'Доставка'];

function setupContent_(ss) {
  Object.keys(CONTENT).forEach(function (name) {
    var sh = ss.getSheetByName(name) || ss.insertSheet(name);
    sh.getRange(1, 1, 1, CONTENT[name].length).setValues([CONTENT[name]]).setFontWeight('bold').setBackground('#eaf1fc');
    sh.setFrozenRows(1); sh.setColumnWidths(1, CONTENT[name].length, 220);
    if (name === 'Сайт: реквизиты' && sh.getLastRow() < 2)
      sh.getRange(2, 1, REQ_FIELDS.length, 2).setValues(REQ_FIELDS.map(function (f) { return [f, '']; }));
  });
}

function rows_(ss, name) {
  var sh = ss.getSheetByName(name); if (!sh || sh.getLastRow() < 2) return [];
  return sh.getRange(2, 1, sh.getLastRow() - 1, sh.getLastColumn()).getDisplayValues();
}
function yes_(v) { return /^(да|yes|1|\+|✓)$/i.test(String(v).trim()); }
function img_(u) { // ссылка Google Диска → прямая картинка (файл должен быть открыт «всем, у кого есть ссылка»)
  u = String(u || '').trim(); var m = u.match(/\/d\/([\w-]{20,})|[?&]id=([\w-]{20,})/);
  return m ? 'https://drive.google.com/thumbnail?id=' + (m[1] || m[2]) + '&sz=w1200' : u;
}

function doGet(e) {
  if (!(e && e.parameter && e.parameter.content)) return json_({ok: true, service: 'equipcn-leads'});
  var cache = CacheService.getScriptCache(), c = cache.get('content');
  if (c) return ContentService.createTextOutput(c).setMimeType(ContentService.MimeType.JSON);
  var ss = SpreadsheetApp.getActive(), out = {ok: true, requisites: {}, projects: [], reviews: [], team: [], videos: []};
  rows_(ss, 'Сайт: реквизиты').forEach(function (r) { if (r[0] && r[1]) out.requisites[r[0]] = r[1]; });
  rows_(ss, 'Сайт: проекты').forEach(function (r) { if (r[0] && yes_(r[5])) out.projects.push({title: r[0], city: r[1], text: r[2], photos: String(r[3]).split(',').map(img_).filter(String), video: r[4]}); });
  rows_(ss, 'Сайт: отзывы').forEach(function (r) { if (r[3] && yes_(r[6])) out.reviews.push({name: r[0], company: r[1], city: r[2], text: r[3], link: r[4], photo: img_(r[5])}); });
  rows_(ss, 'Сайт: команда').forEach(function (r) { if (r[0] && yes_(r[3])) out.team.push({name: r[0], role: r[1], photo: img_(r[2])}); });
  rows_(ss, 'Сайт: видео заводов').forEach(function (r) { if (r[1] && yes_(r[2])) out.videos.push({title: r[0], url: r[1]}); });
  var s = JSON.stringify(out); cache.put('content', s, 300);
  return ContentService.createTextOutput(s).setMimeType(ContentService.MimeType.JSON);
}

function doPost(e) {
  var lock = LockService.getScriptLock();
  try {
    var d = JSON.parse((e && e.postData && e.postData.contents) || '{}');
    // защита от ботов: скрытое поле и слишком быстрая отправка
    if (d.website || (d.t_fill && d.t_fill < 2500)) return json_({ok: true, id: 'skip'});
    var phone = String(d.phone || '').replace(/[^\d+]/g, '');
    var digits = phone.replace(/\D/g, '');
    if (digits.length < 10 || digits.length > 15) return json_({ok: false, error: 'phone'});
    var need = clip_(d.need, 2000);
    if (!need && !d.product && !d.file_b64) return json_({ok: false, error: 'need'});
    // не чаще 1 заявки в 20 секунд с одного номера
    var cache = CacheService.getScriptCache();
    if (cache.get('p' + digits)) return json_({ok: true, id: cache.get('p' + digits), dup: true});

    var fileUrl = '';
    if (d.file_b64 && d.file_name) {
      var bytes = Utilities.base64Decode(String(d.file_b64));
      if (bytes.length <= MAX_FILE) {
        var blob = Utilities.newBlob(bytes, clip_(d.file_type, 100) || 'application/octet-stream', clip_(d.file_name, 120));
        fileUrl = folder_().createFile(blob).getUrl();
      }
    }
    lock.waitLock(15000);
    var sh = SpreadsheetApp.getActive().getSheetByName(SHEET);
    var n = Math.max(sh.getLastRow(), 1);
    var id = Utilities.formatDate(new Date(), 'Asia/Almaty', 'yyMMdd') + '-' + n;
    var u = d.utm || {};
    var row = [n, new Date(), "'" + phone, need, clip_(d.product, 300), fileUrl, source_(u, d.referrer),
      clip_(u.utm_source, 100), clip_(u.utm_medium, 100), clip_(u.utm_campaign, 200), clip_(u.utm_term, 200), clip_(u.utm_content, 200),
      clip_(u.gclid || u.yclid || u.fbclid, 200), clip_(d.page, 300), clip_(d.landing, 300), clip_(d.referrer, 300),
      clip_(d.device, 60), 'Новая', '', '', id];
    sh.appendRow(row);
    lock.releaseLock();
    cache.put('p' + digits, id, 20);
    notify_(id, phone, need, d.product, fileUrl, row[6], d.page);
    return json_({ok: true, id: id});
  } catch (err) {
    try { lock.releaseLock(); } catch (x) {}
    return json_({ok: false, error: 'server'});
  }
}

function clip_(v, n) { return String(v == null ? '' : v).slice(0, n); }

function source_(u, ref) {
  if (u.gclid) return 'Google Ads';
  if (u.yclid) return 'Яндекс Директ';
  if (u.utm_source) return u.utm_source + (u.utm_medium ? ' / ' + u.utm_medium : '');
  ref = String(ref || '');
  if (!ref) return 'Прямой заход';
  var m = ref.match(/^https?:\/\/([^\/]+)/);
  var h = m ? m[1].replace(/^www\./, '') : ref;
  if (/google\./.test(h)) return 'Google (поиск)';
  if (/yandex\.|ya\.ru/.test(h)) return 'Яндекс (поиск)';
  if (/chatgpt|openai/.test(h)) return 'ChatGPT';
  if (/instagram|tiktok|facebook|t\.me|telegram|whatsapp/.test(h)) return 'Соцсети: ' + h;
  if (/equipcngroup\.com/.test(h)) return 'Прямой заход';
  return 'Сайт: ' + h;
}

function notify_(id, phone, need, product, fileUrl, src, page) {
  var ssUrl = SpreadsheetApp.getActive().getUrl();
  var text = '🔔 Новая заявка ' + id + '\n☎ ' + phone + '\n🛠 ' + (need || '—') + (product ? '\n📦 ' + product : '') +
    (fileUrl ? '\n📎 ' + fileUrl : '') + '\n🌐 ' + src + (page ? '\n' + page : '') + '\n\nТаблица: ' + ssUrl;
  var p = PropertiesService.getScriptProperties();
  var email = p.getProperty('NOTIFY_EMAIL');
  if (email) { try { MailApp.sendEmail(email, 'Новая заявка с сайта: ' + phone, text); } catch (e) {} }
  var token = p.getProperty('TG_TOKEN'), chats = (p.getProperty('TG_CHATS') || '').split(',').filter(String);
  chats.forEach(function (c) {
    try {
      UrlFetchApp.fetch('https://api.telegram.org/bot' + token + '/sendMessage',
        {method: 'post', payload: {chat_id: c, text: text, disable_web_page_preview: 'true'}, muteHttpExceptions: true});
    } catch (e) {}
  });
}

function connectTelegram() {
  var ui = SpreadsheetApp.getUi(), p = PropertiesService.getScriptProperties();
  var r = ui.prompt('Telegram — шаг 1 из 2',
    'Создайте бота в @BotFather (/newbot) и вставьте сюда его токен. Затем напишите своему боту любое сообщение ' +
    '(или добавьте бота в рабочую группу и напишите там) и нажмите OK.', ui.ButtonSet.OK_CANCEL);
  if (r.getSelectedButton() !== ui.Button.OK) return;
  var token = r.getResponseText().trim();
  var res = JSON.parse(UrlFetchApp.fetch('https://api.telegram.org/bot' + token + '/getUpdates', {muteHttpExceptions: true}).getContentText());
  if (!res.ok) { ui.alert('Токен не подошёл. Проверьте и попробуйте ещё раз.'); return; }
  var chats = {};
  (res.result || []).forEach(function (u) { var m = u.message || u.channel_post || u.my_chat_member; if (m && m.chat) chats[m.chat.id] = m.chat.title || m.chat.first_name || m.chat.id; });
  var ids = Object.keys(chats);
  if (!ids.length) { ui.alert('Бот пока не видит сообщений. Напишите боту (или в группу с ботом) и повторите.'); return; }
  p.setProperty('TG_TOKEN', token);
  p.setProperty('TG_CHATS', ids.join(','));
  ui.alert('Подключено: ' + ids.map(function (i) { return chats[i]; }).join(', ') + '. Нажмите «Проверить уведомления».');
}

function testNotify() {
  notify_('ТЕСТ', '+7 700 000 00 00', 'Проверка уведомлений', '', '', 'Тест', '');
  SpreadsheetApp.getActive().toast('Отправлено тестовое уведомление', 'Equipcn', 5);
}
