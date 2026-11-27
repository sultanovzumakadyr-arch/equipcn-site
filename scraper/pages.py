"""Отдельные страницы для поисковиков: /p/<код> (товар), /c/<группа> (направление) и sitemap.xml.

Вызывается из build.py после сборки index.html. Дизайн — облегчённая версия главной.
"""
import datetime
import html
import json
import re

SITE = "https://equipcngroup.com"
WA = "https://wa.me/77787586354"
PHONE = "+7 778 758-63-54"
TODAY = datetime.date.today().isoformat()

CSS = """
:root{--bg:#f5f8fd;--navy:#0B3D91;--accent:#2F80ED;--logo:#1F5FC9;--text:#0f1d33;--muted:#5b6b82;--edge:#dbe4f1;
--display:"Manrope",system-ui,sans-serif;--body:"Golos Text",system-ui,-apple-system,"Segoe UI",sans-serif}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--text);font:16px/1.6 var(--body)}
a{color:var(--logo)}.wrap{max-width:1120px;margin:0 auto;padding:0 20px}
header{background:#fff;border-bottom:1px solid var(--edge)}header .wrap{display:flex;align-items:center;justify-content:space-between;height:64px;gap:12px}
.logo{display:flex;align-items:center;gap:8px;text-decoration:none;color:var(--navy);font:800 1.3rem var(--display)}
.btn{display:inline-flex;align-items:center;justify-content:center;gap:8px;border-radius:999px;padding:13px 22px;font-weight:600;text-decoration:none;border:0}
.btn.wa{background:var(--accent);color:#fff}.btn.tel{background:#fff;color:var(--navy);border:1px solid var(--edge)}
.crumbs{font-size:.88rem;color:var(--muted);margin:18px 0}.crumbs a{color:var(--muted)}
h1{font:800 clamp(1.5rem,3.4vw,2.3rem)/1.15 var(--display);margin:0 0 12px;color:var(--text)}
.prod{display:grid;grid-template-columns:1.05fr 1fr;gap:28px;align-items:start}
.gal{background:#fff;border:1px solid var(--edge);border-radius:20px;padding:12px}
.gal .main{width:100%;aspect-ratio:1;object-fit:contain;border-radius:14px;background:#fff}
.thumbs{display:flex;gap:8px;margin-top:8px;flex-wrap:wrap}.thumbs img{width:74px;height:74px;object-fit:cover;border-radius:10px;border:1px solid var(--edge);cursor:pointer}
.price{font:800 1.7rem var(--display);color:var(--navy);margin:6px 0 4px}.price small{font:500 1rem var(--body);color:var(--muted)}
.note{color:var(--muted);font-size:.9rem;margin:0 0 18px}.cta{display:flex;flex-wrap:wrap;gap:10px;margin-bottom:22px}
.card{background:#fff;border:1px solid var(--edge);border-radius:18px;padding:20px 22px;margin-bottom:18px}
.card h2{font:700 1.15rem var(--display);margin:0 0 10px}.card p{margin:0 0 10px}
table{width:100%;border-collapse:collapse}td{padding:8px 0;border-bottom:1px solid var(--edge);vertical-align:top}td:first-child{color:var(--muted);width:45%;padding-right:12px}
.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(230px,1fr));gap:14px;margin:18px 0 30px}
.it{background:#fff;border:1px solid var(--edge);border-radius:16px;overflow:hidden;text-decoration:none;color:var(--text);display:flex;flex-direction:column}
.it img{width:100%;aspect-ratio:4/3;object-fit:cover;background:#eaf1fc}.it .ph{aspect-ratio:4/3;background:#eaf1fc}
.it b{display:block;padding:12px 14px 4px;font-weight:600;line-height:1.35}.it span{padding:0 14px 14px;color:var(--navy);font-weight:700}
.dirs{display:flex;flex-wrap:wrap;gap:8px;margin:10px 0 0}.dirs a{background:#fff;border:1px solid var(--edge);border-radius:999px;padding:7px 14px;text-decoration:none;color:var(--text);font-size:.92rem}
footer{border-top:1px solid var(--edge);margin-top:40px;padding:26px 0;color:var(--muted);font-size:.9rem}
.btn-main{background:var(--accent);color:#fff}.btn-line{background:#fff;color:var(--navy);border:1px solid var(--edge)}
.lead-box{display:grid;grid-template-columns:1fr 420px;gap:28px;align-items:start;background:linear-gradient(135deg,#0B3D91,#1F5FC9);color:#fff;border-radius:24px;padding:clamp(22px,4vw,40px);margin:24px 0}
.lead-box h2{font:800 clamp(1.4rem,3vw,2rem)/1.2 var(--display);margin:0 0 10px}.lead-box p{color:#d5e3fa;margin:0 0 10px}
.nf{display:flex;align-items:center;justify-content:space-between;gap:16px;flex-wrap:wrap;background:#fff;border:1px dashed #b9cbe6;border-radius:18px;padding:18px 22px;margin:20px 0}
.nf p{margin:4px 0 0;color:var(--muted)}
.ben{display:grid;grid-template-columns:repeat(auto-fill,minmax(220px,1fr));gap:12px;margin:18px 0}
.ben div{background:#fff;border:1px solid var(--edge);border-radius:16px;padding:16px}.ben b{display:block;margin-bottom:4px}.ben span{color:var(--muted);font-size:.93rem}
.faq details{background:#fff;border:1px solid var(--edge);border-radius:14px;padding:14px 18px;margin-bottom:10px}.faq summary{font-weight:600;cursor:pointer}.faq p{margin:10px 0 0;color:#334155}
.steps{counter-reset:s;display:grid;grid-template-columns:repeat(auto-fill,minmax(160px,1fr));gap:10px;margin:14px 0}
.steps div{background:#fff;border:1px solid var(--edge);border-radius:14px;padding:14px;font-size:.92rem}.steps div:before{counter-increment:s;content:counter(s);display:block;font:800 1.3rem var(--display);color:var(--accent)}
@media(max-width:820px){.prod{grid-template-columns:1fr}.cta .btn{flex:1}.lead-box{grid-template-columns:1fr}.hide-m{display:none}}
"""

LOGO = ('<svg width="28" height="28" viewBox="0 0 48 48" aria-hidden="true"><g fill="#1F5FC9">'
        '<circle cx="24" cy="24" r="13"/>' + "".join(
            f'<rect x="20" y="2" width="8" height="10" rx="2" transform="rotate({a} 24 24)"/>' for a in range(0, 360, 45)) +
        '</g><circle cx="24" cy="24" r="5" fill="#fff"/></svg>')


def esc(s):
    return html.escape(str(s or ""), quote=True)


def img_url(u):
    return u if u.startswith("http") else "/" + u.lstrip("/")


def abs_img(u):
    return u if u.startswith("http") else SITE + "/" + u.lstrip("/")


def price_parts(price):
    p = str(price or "").strip()
    n = int(re.sub(r"\D", "", p) or 0)
    if not n:
        return None, "Цена по запросу"
    txt = f"{n:,}".replace(",", " ") + " ₸"
    return n, ("от " + txt if p.startswith("~") else txt)


def page(title, desc, canonical, body, head_extra="", image=None):
    og = image or SITE + "/og.jpg"
    return f"""<!DOCTYPE html>
<html lang="ru"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(title)}</title><meta name="description" content="{esc(desc)}">
<link rel="canonical" href="{canonical}">
<meta property="og:type" content="website"><meta property="og:site_name" content="Equipcn"><meta property="og:title" content="{esc(title)}">
<meta property="og:description" content="{esc(desc)}"><meta property="og:url" content="{canonical}"><meta property="og:image" content="{esc(og)}">
<meta name="referrer" content="no-referrer">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Manrope:wght@700;800&family=Golos+Text:wght@400;500;600&display=swap" rel="stylesheet">
<link rel="stylesheet" href="/assets/lead.css"><style>{CSS}</style>{head_extra}</head><body>
<header><div class="wrap"><a class="logo" href="/">{LOGO}equipcn</a><div style="display:flex;gap:8px"><a class="btn tel hide-m" href="tel:+77787586354">{PHONE}</a><a class="btn wa" href="#lead">Получить расчёт</a></div></div></header>
<main class="wrap">{body}</main>
<footer><div class="wrap">© 2026 Equipcn · Промышленное оборудование из Китая под ключ · Алматы, ул. Жандосова, 4В · <a href="tel:+77787586354">{PHONE}</a> · Доставка по Казахстану и СНГ
<div class="dirs">{{DIRS}}</div><div class="dirs">{{LANDS}}</div><p><a href="/privacy">Политика обработки данных</a></p></div></footer>
<div class="mbar"><a class="m1" href="#lead">Получить расчёт</a><a class="m2" href="{WA}" target="_blank" rel="noopener">WhatsApp</a></div>
<script defer src="/assets/lead.js"></script>
</body></html>"""


NOT_FOUND = ('<div class="nf"><div><b>Не нашли нужное оборудование?</b><p>Отправьте нам фото или техническое задание — '
             'подберём подходящий вариант в Китае.</p></div><a class="btn btn-main" href="#lead">Отправить фото или ТЗ</a></div>')


def lead_box(title, text, place, need=""):
    return (f'<section class="lead-box" data-place="{place}"><div><h2>{esc(title)}</h2><p>{esc(text)}</p>'
            '<p>Без регистрации: достаточно описания и телефона. Можно приложить фото или ТЗ.</p></div>'
            f'<div id="lead" data-leadform data-need="{esc(need)}"></div></section>')


def build(products, groups, out_dir, tracking="", logo=None):
    global LOGO
    if logo: LOGO = logo
    """products: список товаров как в index.html; groups: [(ключ, название)]."""
    gname = dict(groups)
    by_cat = {}
    for p in products:
        by_cat.setdefault(p["cat"], []).append(p)
    live = [(k, v) for k, v in groups if by_cat.get(k)]
    dirs = "".join(f'<a href="/c/{k}">{esc(v)} ({len(by_cat[k])})</a>' for k, v in live)

    pdir, cdir = out_dir / "p", out_dir / "c"
    for d in (pdir, cdir):
        d.mkdir(parents=True, exist_ok=True)
        for f in d.glob("*.html"):
            f.unlink()

    urls = [(SITE + "/", "1.0")]
    for k, v in live:
        items = by_cat[k]
        cards = []
        for p in items:
            _, ptxt = price_parts(p.get("price"))
            im = p.get("images") or []
            pic = f'<img loading="lazy" src="{esc(img_url(im[0]))}" alt="{esc(p["name"])}">' if im else '<div class="ph"></div>'
            cards.append(f'<a class="it" href="/p/{esc(p["id"])}">{pic}<b>{esc(p["name"])}</b><span>{esc(ptxt)}</span></a>')
        title = f"{v} из Китая — купить в Казахстане | Equipcn"
        desc = (f"{v}: {len(items)} позиций напрямую с заводов Китая. "
                f"Подбор под задачу, под ключ, доставка по Казахстану и СНГ. Цены и КП в WhatsApp.")
        body = (f'<div class="crumbs"><a href="/">Главная</a> / {esc(v)}</div><h1>{esc(v)}</h1>'
                f'<p class="note">{len(items)} позиций под заказ напрямую с заводов Китая. Не нашли нужное — пришлите ТЗ или фото, подберём.</p>'
                f'<div class="cta"><a class="btn wa" href="{WA}?text={esc("Здравствуйте! Интересует: " + v)}" target="_blank" rel="noopener">Подобрать в WhatsApp</a>'
                f'<a class="btn tel" href="tel:+77787586354">{PHONE}</a></div><div class="grid" data-view-list="{k}" data-name="{esc(v)}">{"".join(cards)}</div>'
                + NOT_FOUND + lead_box("Получите расчёт стоимости с доставкой", "Опишите, что нужно, — подберём производителя в Китае и посчитаем стоимость до вашего объекта.", "category"))
        ld = {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "Главная", "item": SITE + "/"},
            {"@type": "ListItem", "position": 2, "name": v, "item": f"{SITE}/c/{k}"}]}
        h = page(title, desc, f"{SITE}/c/{k}", body, tracking + f'<script type="application/ld+json">{json.dumps(ld, ensure_ascii=False)}</script>')
        (cdir / f"{k}.html").write_text(h.replace("{DIRS}", dirs), "utf8")
        urls.append((f"{SITE}/c/{k}", "0.8"))

    for p in products:
        pid, name, cat = p["id"], p["name"], p["cat"]
        g = gname.get(cat, "Оборудование")
        n, ptxt = price_parts(p.get("price"))
        ims = [img_url(u) for u in (p.get("images") or [])]
        desc_txt = re.sub(r"\s+", " ", p.get("desc") or "").strip()
        meta = f"{name} — {ptxt.lower() if n else 'цена по запросу'}. Напрямую с завода в Китае, доставка по Казахстану и СНГ. " + desc_txt
        meta = meta[:157].rsplit(" ", 1)[0] + "…" if len(meta) > 160 else meta
        gal = ""
        if ims:
            th = "".join(f'<img src="{esc(u)}" alt="{esc(name)} — фото {i + 1}" onclick="document.getElementById(\'mi\').src=this.src">' for i, u in enumerate(ims[:6]))
            gal = f'<div class="gal"><img id="mi" class="main" src="{esc(ims[0])}" alt="{esc(name)}">' + (f'<div class="thumbs">{th}</div>' if len(ims) > 1 else "") + "</div>"
        else:
            gal = '<div class="gal"><div class="main" style="background:#eaf1fc"></div></div>'
        paras = "".join(f"<p>{esc(x)}</p>" for x in re.split(r"\n\s*\n|\n", p.get("desc") or "") if x.strip())
        specs = "".join(f"<tr><td>{esc(a)}</td><td>{esc(b)}</td></tr>" for a, b in (p.get("specs") or []))
        wa_text = f"Здравствуйте! Интересует {name} (код {pid}), {SITE}/p/{pid}"
        info = (f'<div><div class="crumbs"><a href="/">Главная</a> / <a href="/c/{esc(cat)}">{esc(g)}</a></div>'
                f'<h1>{esc(name)}</h1><div class="price">{esc(ptxt)}</div>'
                f'<p class="note">Под заказ · Код товара: {esc(pid)}' + (" · Цена за базовую комплектацию, без доставки" if n else "") + '</p>'
                '<p class="note">Доставка по Казахстану и СНГ — стоимость доставки включим в расчёт.</p>'
                f'<div id="lead" data-place="product-page" data-leadform data-title="Узнать стоимость с доставкой" data-product="{esc(name)} (код {esc(pid)})" data-need="Нужна стоимость с доставкой: {esc(name)}"></div>'
                f'<div class="cta" style="margin-top:12px"><a class="btn tel" href="{WA}?text={esc(wa_text)}" target="_blank" rel="noopener">Спросить в WhatsApp</a>'
                f'<a class="btn tel" href="tel:+77787586354">Позвонить: {PHONE}</a></div>'
                + (f'<div class="card"><h2>Характеристики</h2><table>{specs}</table></div>' if specs else "") + "</div>")
        body = (f'<div class="prod" data-view-item="{esc(pid)}" data-name="{esc(name)}" data-cat="{esc(g)}">{gal}{info}</div>'
                + (f'<div class="card"><h2>Описание</h2>{paras}</div>' if paras else "")
                + f'<p><a href="/c/{esc(cat)}">← Все товары: {esc(g)}</a> · <a href="/#p-{esc(pid)}">Открыть в каталоге</a></p>')
        ld = {"@context": "https://schema.org", "@type": "Product", "name": name, "sku": pid, "category": g,
              "description": desc_txt[:500] or name, "brand": {"@type": "Brand", "name": "Equipcn"},
              "url": f"{SITE}/p/{pid}"}
        if ims:
            ld["image"] = [abs_img(u) for u in ims[:3]]
        if n:
            ld["offers"] = {"@type": "AggregateOffer", "priceCurrency": "KZT", "lowPrice": n, "offerCount": 1,
                            "availability": "https://schema.org/PreOrder",
                            "seller": {"@type": "Organization", "name": "Equipcn"}}
        bc = {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "Главная", "item": SITE + "/"},
            {"@type": "ListItem", "position": 2, "name": g, "item": f"{SITE}/c/{cat}"},
            {"@type": "ListItem", "position": 3, "name": name, "item": f"{SITE}/p/{pid}"}]}
        extra = tracking + "".join('<script type="application/ld+json">' + json.dumps(x, ensure_ascii=False).replace("</", "<\\/") + "</script>" for x in (ld, bc))
        title = f"{name} — купить в Казахстане | Equipcn"
        h = page(title, meta, f"{SITE}/p/{pid}", body, extra, abs_img(ims[0]) if ims else None)
        (pdir / f"{pid}.html").write_text(h.replace("{DIRS}", dirs), "utf8")
        urls.append((f"{SITE}/p/{pid}", "0.6"))

    lands = "".join(f'<a href="/l/{s}">{esc(h)}</a>' for s, h, _, _ in LANDINGS)
    urls += build_landings(products, gname, out_dir, tracking, dirs, lands)
    (out_dir / "privacy.html").write_text(page("Политика обработки данных | Equipcn", "Как Equipcn обрабатывает данные из заявок.",
                                               f"{SITE}/privacy", PRIVACY, tracking).replace("{DIRS}", dirs).replace("{LANDS}", lands), "utf8")
    for d in (pdir, cdir):  # подставить ссылки на посадочные страницы в уже созданные страницы
        for f in d.glob("*.html"):
            f.write_text(f.read_text("utf8").replace("{LANDS}", lands), "utf8")
    sm = ['<?xml version="1.0" encoding="UTF-8"?>', '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    sm += [f"<url><loc>{u}</loc><lastmod>{TODAY}</lastmod><priority>{pr}</priority></url>" for u, pr in urls]
    sm.append("</urlset>")
    (out_dir / "sitemap.xml").write_text("\n".join(sm) + "\n", "utf8")
    return len(urls), dirs, lands


# ---------- посадочные страницы для рекламы: /l/<slug> ----------
BEN = [("Прямые поставки", "Покупаем у производителя, без цепочки посредников."),
       ("Официальный договор", "Цена, комплектация и сроки фиксируются в договоре."),
       ("Проверка перед отправкой", "Проверяем оборудование до отгрузки с завода."),
       ("Закупка и логистика", "Сопровождаем закупку и доставку до вашего объекта.")]
STEPS = ["Вы оставляете заявку", "Уточняем техническое задание", "Подбираем производителей в Китае",
         "Присылаем коммерческое предложение", "Заключаем договор и организуем закупку", "Проверяем и доставляем оборудование"]
FAQ = [("Как узнать точную стоимость?", "Оставьте заявку: что нужно и телефон. Мы уточним задачу и пришлём коммерческое предложение со стоимостью оборудования и доставки до вашего города."),
       ("Можно заказать оборудование, которого нет на сайте?", "Да. Пришлите название, фото или техническое задание — подберём подходящие варианты у производителей в Китае."),
       ("Как проходит оплата?", "Работаем по официальному договору. Порядок и условия оплаты фиксируются в договоре до начала закупки."),
       ("Как вы проверяете оборудование?", "Проверяем оборудование перед отправкой с завода и сопровождаем закупку до доставки."),
       ("Куда доставляете?", "По Казахстану и в страны СНГ — до вашего объекта. Стоимость доставки включаем в расчёт."),
       ("Сколько времени занимает поставка?", "Срок зависит от изготовления на заводе и маршрута доставки. Точный срок указываем в коммерческом предложении.")]
LANDINGS = [
    ("proizvodstvennoe-oborudovanie", "Производственное оборудование из Китая", "Линии и станки для запуска и расширения производства: переработка пластика, упаковка, стекло и окна, электроника, компрессоры и генераторы.", {"cats": ["plast", "pack", "glass", "power", "weld", "elec", "metal"]}),
    ("pishchevoe-oborudovanie", "Пищевое оборудование из Китая", "Оборудование для мясных, молочных и пищевых цехов, холодильные камеры и склады — от отдельной машины до цеха под ключ.", {"cats": ["food", "meat", "dairy", "cold"]}),
    ("oborudovanie-dlya-restoranov-i-kafe", "Оборудование для ресторанов и кафе из Китая", "Печи, слайсеры, мясорубки, льдогенераторы, холодильные камеры и оборудование для заготовочных цехов. Чего нет в каталоге — подберём под ваш проект.", {"kw": r"печь|слайсер|мясоруб|волчок|ледоген|льдоген|пельмен|котлет|холодильн|шоков|лапш|макарон|коптильн|куттер|фаршемеш|чиллер|розлив воды"}),
    ("upakovochnoe-oborudovanie", "Упаковочное оборудование из Китая", "Фасовочные и упаковочные машины, линии для пакетов, бумажных стаканов, гофрокартона и маркировки.", {"cats": ["pack"]}),
    ("derevoobrabatyvayushchie-stanki", "Деревообрабатывающие станки из Китая", "Раскроечные и кромкооблицовочные станки, ЧПУ, линии для корпусной мебели и деревообработки.", {"cats": ["wood"]}),
    ("metalloobrabatyvayushchie-stanki", "Металлообрабатывающие станки из Китая", "Лазерные и плазменные станки, листогибы, гильотины, токарные и фрезерные станки, сварочное оборудование.", {"cats": ["metal", "weld"]}),
    ("stroitelnoe-oborudovanie", "Оборудование для производства стройматериалов из Китая", "Вибропрессы, линии газоблоков и брусчатки, бетонные заводы, профилегибы и оборудование для сухих смесей.", {"cats": ["build"]}),
    ("podbor-oborudovaniya", "Индивидуальный подбор оборудования в Китае", "Опишите задачу или пришлите фото и ТЗ — подберём производителей в Китае, сравним варианты и посчитаем стоимость с доставкой до вашего объекта.", {}),
]


def build_landings(products, gname, out_dir, tracking, dirs, lands):
    ldir = out_dir / "l"
    ldir.mkdir(parents=True, exist_ok=True)
    for f in ldir.glob("*.html"):
        f.unlink()
    urls = []
    for slug, h1, sub, sel in LANDINGS:
        if sel.get("cats"):
            pools = [[p for p in products if p["cat"] == c] for c in sel["cats"]]
            items, i = [], 0
            while len(items) < 24 and any(i < len(pl) for pl in pools):  # по очереди из каждого направления
                items += [pl[i] for pl in pools if i < len(pl)]
                i += 1
            items = items[:24]
        elif sel.get("kw"):
            items = [p for p in products if re.search(sel["kw"], p["name"], re.I)][:24]
        else:
            items = []
        cards = "".join(
            f'<div class="it"><a href="/p/{esc(p["id"])}" style="text-decoration:none;color:inherit">'
            + (f'<img loading="lazy" src="{esc(img_url(p["images"][0]))}" alt="{esc(p["name"])}">' if p.get("images") else '<div class="ph"></div>')
            + f'<b>{esc(p["name"])}</b></a><span>{esc(price_parts(p.get("price"))[1])}</span>'
            f'<a class="btn btn-main" style="margin:0 14px 14px;padding:10px" href="#lead" data-ask="{esc(p["name"])} (код {esc(p["id"])})">Узнать стоимость</a></div>'
            for p in items)
        cats = sel.get("cats") or []
        more = " · ".join(f'<a href="/c/{c}">{esc(gname.get(c, c))}</a>' for c in cats)
        body = (f'<div class="crumbs"><a href="/">Главная</a> / {esc(h1)}</div>'
                f'<section class="lead-box" data-place="landing-top"><div><h1 style="color:#fff">{esc(h1)}</h1><p>{esc(sub)}</p>'
                '<p>✓ Прямые поставки от производителей<br>✓ Работа по официальному договору<br>✓ Проверка оборудования перед отправкой<br>'
                '✓ Сопровождение закупки и логистики<br>✓ Индивидуальный подбор оборудования</p></div>'
                '<div id="lead" data-leadform data-title="Получить расчёт стоимости"></div></section>'
                + ('<h2>Оборудование в каталоге</h2>' + (f'<p class="note">Полный список: {more}</p>' if more else '')
                   + f'<div class="grid" data-view-list="landing-{slug}" data-name="{esc(h1)}">{cards}</div>' if cards else "")
                + NOT_FOUND
                + '<div class="ben">' + "".join(f"<div><b>{a}</b><span>{b}</span></div>" for a, b in BEN) + '</div>'
                + '<h2>Как мы работаем</h2><div class="steps">' + "".join(f"<div>{s}</div>" for s in STEPS) + '</div>'
                + '<h2>Частые вопросы</h2><div class="faq">' + "".join(f"<details><summary>{q}</summary><p>{a}</p></details>" for q, a in FAQ) + '</div>'
                + '<section class="lead-box" data-place="landing-bottom"><div><h2>Получите стоимость с доставкой</h2><p>Опишите оборудование и оставьте телефон — менеджер свяжется и уточнит детали.</p></div>'
                '<div data-leadform data-title=""></div></section>')
        ld = {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [
            {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in FAQ]}
        extra = tracking + '<script type="application/ld+json">' + json.dumps(ld, ensure_ascii=False) + "</script>"
        h = page(f"{h1} — доставка в Казахстан | Equipcn", sub[:158], f"{SITE}/l/{slug}", body, extra)
        (ldir / f"{slug}.html").write_text(h.replace("{DIRS}", dirs).replace("{LANDS}", lands), "utf8")
        urls.append((f"{SITE}/l/{slug}", "0.7"))
    return urls


PRIVACY = """<div class="crumbs"><a href="/">Главная</a> / Политика обработки данных</div><h1>Политика обработки персональных данных</h1>
<div class="card"><p>Сайт equipcngroup.com (Equipcn) собирает только данные, которые вы сами указываете в форме заявки: номер телефона, описание нужного оборудования и прикреплённые файлы, а также технические данные о переходе на сайт (рекламный источник, UTM-метки, страница заявки).</p>
<p>Данные используются только для связи с вами по заявке и подготовки коммерческого предложения. Мы не передаём их третьим лицам, кроме случаев, предусмотренных законодательством Республики Казахстан.</p>
<p>Доступ к заявкам есть только у сотрудников Equipcn, которые обрабатывают обращения. Чтобы удалить свои данные, напишите нам в WhatsApp или позвоните: <a href="tel:+77787586354">+7 778 758-63-54</a>.</p>
<p>Сайт использует Google Analytics и Google Ads для оценки эффективности рекламы. Эти сервисы могут сохранять cookie в вашем браузере.</p></div>"""
