"""LazerTruba — сайт лазерных станков для резки труб (продаёт Equipcn).
Запуск: python build.py → папка site/. Все пути относительные, сайт работает и в подпапке, и на своём домене.
Цены: прайс завода (¥, с экспортной упаковкой и доставкой по Китаю) → $ по курсу + наценка → ₸.
"""
import html, json, math, pathlib, datetime

ROOT = pathlib.Path(__file__).parent
OUT = ROOT.parent / "site" / "lazertruba"
SITE = "https://equipcngroup.com/lazertruba"   # поменять на свой домен, когда будет куплен
BRAND = "LazerTruba"
WA_NUM = "77787586354"
PHONE = "+7 778 758-63-54"
CNY_PER_USD = 6.68      # ориентир ноябрь 2026
KZT_PER_USD = 458.28    # НБ РК, 25.11.2026
RATE_NOTE = "курс 1 $ = 458 ₸"
TRACK = json.loads((ROOT / "tracking.json").read_text("utf8")) if (ROOT / "tracking.json").exists() else {}

THICK = [("1500 Вт", "3 мм", "3 мм", "1 мм"), ("2000 Вт", "4 мм", "4 мм", "1,5 мм"), ("3000 Вт", "6 мм", "6 мм", "2 мм")]

SERIES = [
    dict(slug="m", name="Серия M", tag="Ручной патрон · самый доступный", img="m-4",
         lead="Надёжный станок для резки круглых и профильных труб с ручным патроном. Простой, неприхотливый, с лучшим соотношением цены и качества.",
         configs=[("Патрон 100 мм", "круглая 12–114 мм, профильная 15–100 мм", [27500, 36600, 45400]),
                  ("Патрон 120 мм", "круглая 12–120 мм, профильная 15–120 мм", [29400, 38100, 46900])],
         feats=["Ручной патрон: сильный зажим, высокая стабильность, мало поломок", "Станина из трёх складных секций — удобно перевозить",
                "Встроенная библиотека фигур — рисовать чертёж не нужно", "Серводвигатели: стабильная работа и точное позиционирование",
                "Отличное соотношение цены и качества"],
         cfg=[("Лазер", "Raycus"), ("Лазерная головка", "Raytools"), ("Система ЧПУ", "Shanghai Fangling"), ("Чиллер", "S&A")],
         photos=["m-4", "m-1", "m-2", "m-3", "m-5", "m-6", "m-8", "m-9", "m-10", "m-11", "m-12", "m-13"],
         videos=[("m-krug", "Резка круглой трубы"), ("m-profil-10mm", "Профильная труба 10 мм, стенка 3 мм"), ("m-3000w-5mm", "3000 Вт: сталь 5,5 мм"), ("m-ugolok", "Резка уголка")],
         markup=None),
    dict(slug="xq", name="Серия XQ", tag="Два пневмопатрона · быстрее и точнее", img="xq-1",
         lead="Передний и задний пневматические патроны, следящая лазерная головка и автопоиск кромки. Для цехов, где важны скорость и точность.",
         configs=[("Патрон 100 мм", "круглая 12–100 мм, профильная 15–100 мм", [32700, 41500, 50200]),
                  ("Патрон 120 мм", "круглая 10–120 мм, профильная 10–120 мм, остаток ~60 мм", [38100, 46900, 55600])],
         feats=["Следящая лазерная головка с сервоприводом, автоподъём — точнее рез", "Передний и задний пневмопатроны — выше скорость резки",
                "Станина из трёх складных секций — удобно перевозить", "Встроенная библиотека фигур — рисовать не нужно",
                "Автопоиск кромки и повторная прошивка — выше точность", "Сенсорный экран, кнопки и пульт ДУ — просто управлять",
                "Патрон 120 мм: задний патрон проходит в передний, остаток трубы всего ~60 мм"],
         cfg=[("Лазер", "Raycus"), ("Лазерная головка", "Raytools"), ("Система ЧПУ", "Shanghai Fangling"), ("Чиллер", "S&A")],
         photos=["xq-1", "xq-2", "xq-3"],
         videos=[("xq-120-hvost", "Патрон 120 мм: остаток трубы ~60 мм"), ("xq-3000w", "3000 Вт, резка 2 мм"), ("xq-1500w", "1500 Вт, резка 2 мм"), ("xq-2", "Резка профиля")],
         markup=None),
    dict(slug="xe", name="Серия XE (6012XE)", tag="Новинка ноября 2026 · промышленный ПК", img="xe-1",
         lead="Компактный станок с промышленным компьютером: режет фасонные профили, работает быстрее и точнее. Остаток трубы всего 90–100 мм.",
         configs=[("Патрон 120 мм", "трубы 19–120 мм, круглые и профильные", [44400, 53000, 61700])],
         feats=["Промышленный компьютер — резка фасонных профилей", "Следящая лазерная головка с сервоприводом, автоподъём",
                "Передний и задний пневмопатроны — выше скорость", "Станина из трёх складных секций — удобно перевозить",
                "Встроенная библиотека фигур — рисовать не нужно", "Остаток трубы всего около 90–100 мм"],
         cfg=[("Лазер", "Raycus"), ("Лазерная головка", "Raytools"), ("Система ЧПУ", "промышленный компьютер"), ("Чиллер", "S&A")],
         photos=["xe-1", "xe-2"], videos=[("rezka-profil", "Фигурная резка профиля")], markup=None),
    dict(slug="mys", name="Серия MYS", tag="Скоростной · патрон 120 мм · остаток 40 мм", img="mys-1",
         lead="Скоростной станок с задним патроном «пушечного» типа: остаток трубы всего 40 мм. Промышленный ПК с 3D-моделями — рисовать не нужно.",
         configs=[("Патрон 120 мм", "круглая 8–120 мм, профильная 18–120 мм", [71200, 79900, 88700])],
         feats=["Задний патрон «пушечного» типа: передний уходит в сторону, задний проходит насквозь — остаток трубы 40 мм",
                "Промышленный компьютер, встроенные 3D-модели — рисовать не нужно, режет фасонные профили",
                "Станина из двух частей — помещается в 20-футовый контейнер, дешевле доставка"],
         cfg=[("Лазер", "Raycus"), ("Лазерная головка", "Raytools"), ("Система ЧПУ", "промышленный компьютер"), ("Чиллер", "S&A")],
         photos=["mys-1", "mys-2", "mys-3"],
         videos=[("mys-1", "Резка профильной трубы"), ("mys-ugolok", "Резка уголка"), ("mys-45", "Рез под 45° и гибка"), ("mys-2", "Работа станка")],
         markup=1500),
    dict(slug="yq", name="Серия YQ", tag="Скоростной · патрон 160 мм · остаток 40 мм", img="yq-2",
         lead="Самый производительный: трубы до 160 мм, задний патрон «пушечного» типа и остаток всего 40 мм. Для серийного производства.",
         configs=[("Патрон 160 мм", "круглая 10–160 мм, профильная 10–160 мм", [81200, 89900, 98700])],
         feats=["Задний патрон «пушечного» типа: передний уходит в сторону, задний проходит насквозь — остаток трубы 40 мм",
                "Промышленный компьютер, встроенные 3D-модели — рисовать не нужно, режет фасонные профили",
                "Станина из двух частей — помещается в 20-футовый контейнер, дешевле доставка"],
         cfg=[("Лазер", "Raycus"), ("Лазерная головка", "Raytools"), ("Система ЧПУ", "промышленный компьютер"), ("Чиллер", "S&A")],
         photos=["yq-2", "yq-1", "yq-3", "yq-4", "yq-5", "yq-6", "yq-7", "yq-8"],
         videos=[("yq-1", "Резка на YQ"), ("yq-2", "Резка перфорированного профиля")], markup=2000),
    dict(slug="r219", name="Серия 219", tag="Только круглые трубы до ⌀219 мм", img="r219-1",
         lead="Специальный станок для круглых труб большого диаметра: от 25 до 219 мм, после настройки — до 250 мм. V-образные опоры с подъёмом.",
         configs=[("Круглые трубы", "⌀25–219 мм (после настройки до 250 мм), только круглые", [29900, 39400, 48700])],
         feats=["Режет только круглые трубы ⌀25–219 мм, после настройки специалистом — до 250 мм", "Следящая лазерная головка с сервоприводом, автоподъём",
                "Станина из трёх складных секций — удобно перевозить", "Встроенная библиотека фигур — рисовать не нужно",
                "Автопоиск кромки и повторная прошивка — выше точность", "Сенсорный экран, кнопки и пульт ДУ"],
         cfg=[("Лазер", "Raycus"), ("Лазерная головка", "Raytools"), ("Система ЧПУ", "Shanghai Fangling"), ("Чиллер", "S&A")],
         photos=["r219-1", "r219-2", "r219-3", "r219-4", "r219-5", "r219-6", "r219-7"],
         videos=[("r219-max", "Максимум — труба ⌀219 мм"), ("r219-1", "Резка перфорированной трубы"), ("r219-2", "Резка круглой трубы"), ("r219-3", "Работа станка")],
         markup=None),
]
POWERS = ["1500 Вт", "2000 Вт", "3000 Вт"]
WHITE = {"m-4", "xq-1", "yq-2", "r219-1"}  # фото на белом фоне — показывать целиком


def price(cny, markup):
    m = markup or (800 if cny < 45000 else 900)
    usd = cny / CNY_PER_USD + m
    return int(math.ceil(usd / 10) * 10), int(math.ceil(usd * KZT_PER_USD / 10000) * 10000)


def fm(n):
    return f"{n:,}".replace(",", " ")


for s in SERIES:
    s["rows"] = [(c, rng, p, *price(cny, s["markup"])) for c, rng, cnys in s["configs"] for p, cny in zip(POWERS, cnys)]
    s["from_kzt"] = min(r[4] for r in s["rows"])
    s["from_usd"] = min(r[3] for r in s["rows"])

e = lambda t: html.escape(str(t), quote=True)

CSS = """
:root{--navy:#0B1F3A;--navy2:#13305c;--accent:#2F80ED;--logo:#1F5FC9;--spark:#ff7a1a;--text:#121a26;--muted:#5d6878;--edge:#dfe5ee;--bg:#f4f6f9;--graphite:#2b2f36;
--display:"Manrope",system-ui,sans-serif;--body:"Golos Text",system-ui,-apple-system,"Segoe UI",sans-serif}
*{box-sizing:border-box}html{scroll-behavior:smooth}body{margin:0;background:var(--bg);color:var(--text);font:16px/1.6 var(--body)}
img,video{max-width:100%;display:block}a{color:var(--logo)}
.wrap{max-width:1180px;margin:0 auto;padding:0 20px}
h1,h2,h3{font-family:var(--display);line-height:1.15;margin:0}
h2{font-size:clamp(1.6rem,3.4vw,2.4rem);font-weight:800;margin-bottom:10px}
.btn{display:inline-flex;align-items:center;justify-content:center;gap:8px;border-radius:12px;padding:14px 22px;font-weight:700;text-decoration:none;border:0;cursor:pointer;font-size:1rem;font-family:inherit}
.btn-main{background:var(--accent);color:#fff}.btn-main:hover{background:#1f6fd8}.btn-line{background:#fff;color:var(--navy);border:1px solid var(--edge)}
header.top{position:sticky;top:0;z-index:50;background:rgba(255,255,255,.95);backdrop-filter:blur(8px);border-bottom:1px solid var(--edge)}
header.top .wrap{display:flex;align-items:center;justify-content:space-between;gap:16px;height:68px}
.logo{display:flex;align-items:center;gap:10px;text-decoration:none;color:var(--navy);font:800 1.35rem var(--display)}
.logo i{width:34px;height:34px;border-radius:9px;background:linear-gradient(135deg,var(--navy),var(--navy2));display:grid;place-items:center;position:relative}
.logo i:after{content:"";width:16px;height:16px;border:3px solid #fff;border-radius:50%}.logo i:before{content:"";position:absolute;right:5px;top:5px;width:8px;height:8px;border-radius:50%;background:var(--spark);box-shadow:0 0 8px var(--spark)}
.logo small{display:block;font:500 .7rem var(--body);color:var(--muted);letter-spacing:.02em}
nav.mn{display:flex;gap:22px}nav.mn a{color:var(--graphite);text-decoration:none;font-weight:500;font-size:.95rem}
.hcta{display:flex;gap:8px}.hcta .btn{padding:10px 16px;font-size:.92rem;white-space:nowrap}
.hero{background:radial-gradient(1200px 500px at 80% -10%,#1c437f 0,transparent 60%),linear-gradient(160deg,var(--navy),#0e2748);color:#fff}
.hero .wrap{display:grid;grid-template-columns:1.1fr .9fr;gap:36px;align-items:center;padding-top:48px;padding-bottom:56px}
.eyebrow{display:inline-block;font-size:.8rem;font-weight:700;letter-spacing:.08em;text-transform:uppercase;color:#9cc3fa}
.hero h1{font-size:clamp(2rem,4.4vw,3.3rem);font-weight:800;margin:14px 0}
.hero .sub{color:#c9d6ea;font-size:1.08rem;margin:0 0 18px}
.ben{list-style:none;padding:0;margin:0 0 24px;display:grid;gap:8px}
.ben li{position:relative;padding-left:28px}.ben li:before{content:"✓";position:absolute;left:0;top:0;width:20px;height:20px;border-radius:50%;background:var(--accent);color:#fff;font-size:.75rem;display:grid;place-items:center;font-weight:800}
.hero .ctas{display:flex;gap:10px;flex-wrap:wrap}.hero .btn-line{background:transparent;color:#fff;border-color:rgba(255,255,255,.35)}
.hero-media{position:relative}.hero-media video{border-radius:18px;width:100%;aspect-ratio:9/12;object-fit:cover;box-shadow:0 30px 60px -30px #000}
.facts{display:grid;grid-template-columns:repeat(4,1fr);gap:1px;background:var(--edge);border:1px solid var(--edge);border-radius:18px;overflow:hidden;margin-top:-28px;position:relative}
.facts div{background:#fff;padding:18px 20px}.facts b{display:block;font:800 1.3rem var(--display);color:var(--navy)}.facts span{color:var(--muted);font-size:.9rem}
section.blk{padding:64px 0}.blk .lead{color:var(--muted);max-width:760px;margin:0 0 26px}
.cards{display:grid;grid-template-columns:repeat(3,1fr);gap:18px}
.card{background:#fff;border:1px solid var(--edge);border-radius:18px;overflow:hidden;display:flex;flex-direction:column;transition:transform .15s,box-shadow .15s}
.card:hover{transform:translateY(-3px);box-shadow:0 20px 40px -28px rgba(11,31,58,.5)}
.card .ph{aspect-ratio:4/3;background:#fff;position:relative;overflow:hidden}.card .ph img{position:absolute;inset:0;width:100%;height:100%;object-fit:cover}.card .ph img.wb{object-fit:contain;padding:12px}
.card .bd{padding:18px 20px 20px;display:flex;flex-direction:column;gap:8px;flex:1}
.card .tg{font-size:.8rem;font-weight:700;color:var(--logo);text-transform:uppercase;letter-spacing:.04em}
.card h3{font-size:1.3rem}.card p{margin:0;color:var(--muted);font-size:.93rem}
.card .pr{font:800 1.35rem var(--display);color:var(--navy);margin-top:auto}.card .pr small{font:500 .85rem var(--body);color:var(--muted)}
.card .bt{display:flex;gap:8px}.card .bt .btn{flex:1;padding:11px 10px;font-size:.92rem}
table.cmp{width:100%;border-collapse:collapse;background:#fff;border-radius:16px;overflow:hidden;font-size:.93rem}
table.cmp th,table.cmp td{padding:12px 14px;border-bottom:1px solid var(--edge);text-align:left;vertical-align:top}
table.cmp th{background:var(--navy);color:#fff;font-weight:600}table.cmp tr:last-child td{border-bottom:0}
.tw{overflow-x:auto;border-radius:16px;border:1px solid var(--edge)}
.vids{display:grid;grid-template-columns:repeat(4,1fr);gap:14px}
.vid{background:#000;border-radius:14px;overflow:hidden;position:relative}.vid video{width:100%;aspect-ratio:9/14;object-fit:cover}
.vid span{position:absolute;left:0;right:0;bottom:0;padding:24px 12px 10px;color:#fff;font-size:.85rem;background:linear-gradient(transparent,rgba(0,0,0,.75));pointer-events:none}
.steps{display:grid;grid-template-columns:repeat(6,1fr);gap:12px;counter-reset:s}
.steps div{background:#fff;border:1px solid var(--edge);border-radius:16px;padding:18px 16px}
.steps div:before{counter-increment:s;content:counter(s);display:block;font:800 1.6rem var(--display);color:var(--accent);margin-bottom:6px}
.steps b{display:block;margin-bottom:4px}.steps span{color:var(--muted);font-size:.88rem}
.faq details{background:#fff;border:1px solid var(--edge);border-radius:14px;padding:16px 20px;margin-bottom:10px}
.faq summary{font-weight:700;cursor:pointer}.faq p{margin:10px 0 0;color:#3b4554}
.lead-box{display:grid;grid-template-columns:1fr 430px;gap:30px;background:linear-gradient(135deg,var(--navy),var(--navy2));color:#fff;border-radius:24px;padding:clamp(24px,4vw,44px)}
.lead-box p{color:#c9d6ea}.lead-box .cl{display:grid;gap:10px;margin-top:20px}.lead-box .cl span{display:block;color:#9fb3d1;font-size:.82rem}.lead-box .cl a{color:#fff;font-weight:700}
.nf{display:flex;align-items:center;justify-content:space-between;gap:16px;flex-wrap:wrap;background:#fff;border:1px dashed #b9cbe6;border-radius:18px;padding:20px 24px;margin-top:22px}
.nf p{margin:4px 0 0;color:var(--muted)}
.crumbs{font-size:.88rem;color:var(--muted);padding:16px 0}.crumbs a{color:var(--muted)}
.sp{display:grid;grid-template-columns:1.05fr .95fr;gap:32px;align-items:start}
.gal .main{background:#fff;border:1px solid var(--edge);border-radius:18px;aspect-ratio:1;position:relative;overflow:hidden}.gal .main img{position:absolute;inset:0;width:100%;height:100%;object-fit:contain}
.gal .th{display:flex;gap:8px;flex-wrap:wrap;margin-top:10px}.gal .th button{border:1px solid var(--edge);border-radius:10px;padding:0;width:70px;height:70px;overflow:hidden;cursor:pointer;background:#fff}
.gal .th button.on{outline:2px solid var(--accent)}.gal .th img{width:100%;height:100%;object-fit:cover}
.sp h1{font-size:clamp(1.8rem,3.6vw,2.6rem);font-weight:800;margin:6px 0 10px}
.price{font:800 1.8rem var(--display);color:var(--navy)}.price small{font:500 .95rem var(--body);color:var(--muted)}
.note{color:var(--muted);font-size:.88rem}
.box{background:#fff;border:1px solid var(--edge);border-radius:18px;padding:22px;margin-top:18px}.box h2{font-size:1.3rem}
.box ul{margin:0;padding-left:20px}.box li{margin:6px 0}
table.kv{width:100%;border-collapse:collapse}table.kv td{padding:8px 0;border-bottom:1px solid var(--edge)}table.kv td:first-child{color:var(--muted);width:45%}
footer{background:var(--graphite);color:#c4cad3;padding:36px 0;margin-top:40px;font-size:.92rem}footer a{color:#fff}
footer .fl{display:flex;flex-wrap:wrap;gap:8px 18px;margin:12px 0}
@media(max-width:980px){nav.mn{display:none}.hero .wrap{grid-template-columns:1fr}.hero-media{display:none}.cards{grid-template-columns:1fr 1fr}.vids{grid-template-columns:1fr 1fr}.steps{grid-template-columns:1fr 1fr 1fr}.lead-box,.sp{grid-template-columns:1fr}.facts{grid-template-columns:1fr 1fr}}
@media(max-width:640px){.cards{grid-template-columns:1fr}.steps{grid-template-columns:1fr 1fr}.hero .ben,.hero .ctas{display:none}.hero .wrap{padding-top:26px;gap:18px}.hero h1{font-size:1.85rem}.hcta .btn-line{display:none}section.blk{padding:44px 0}.facts{margin-top:16px}.ptab td:nth-child(4),.ptab th:nth-child(4){display:none}table.cmp th,table.cmp td{padding:9px 8px;font-size:.86rem}}
"""

STEPS = [("Заявка", "Вы оставляете заявку: какие трубы и что режете."), ("Уточняем задачу", "Подбираем серию, патрон и мощность лазера."),
         ("Подбор на заводе", "Согласуем комплектацию с производителем в Китае."), ("Коммерческое предложение", "Присылаем КП с ценой и расчётом доставки."),
         ("Договор и закупка", "Заключаем договор и организуем закупку."), ("Проверка и доставка", "Проверяем станок перед отправкой и доставляем до объекта.")]
FAQ = [("Что входит в цену на сайте?", "Цена указана на заводе в Китае с экспортной деревянной упаковкой и доставкой по Китаю, без доставки в Казахстан и таможенных платежей. Точную стоимость с доставкой до вашего города рассчитает менеджер."),
       ("Какую мощность лазера выбрать?", "1500 Вт режет чёрную и нержавеющую сталь до 3 мм, 2000 Вт — до 4 мм, 3000 Вт — до 6 мм. Алюминий: 1, 1,5 и 2 мм соответственно. Если не уверены, пришлите размеры труб и толщину стенки — подберём."),
       ("Чем отличаются серии?", "M — ручной патрон, самый доступный. XQ — два пневмопатрона и следящая головка, быстрее и точнее. XE — новинка с промышленным компьютером. MYS и YQ — скоростные, остаток трубы 40 мм. Серия 219 — только круглые трубы большого диаметра до 219 мм."),
       ("Нужно ли рисовать чертежи?", "Нет. Во всех станках есть встроенная библиотека фигур, а в сериях XE, MYS и YQ — промышленный компьютер с 3D-моделями для фасонной резки."),
       ("Как проходит оплата?", "Работаем по официальному договору. Порядок и условия оплаты фиксируются в договоре до начала закупки."),
       ("Как проверяете станок?", "Проверяем оборудование перед отправкой с завода и сопровождаем закупку до доставки на ваш объект."),
       ("Сколько ждать поставку?", "Срок зависит от наличия на заводе и маршрута доставки. Точный срок указываем в коммерческом предложении.")]


def head(title, desc, canon, img, extra=""):
    t = TRACK
    cfg = {"endpoint": t.get("lead_endpoint", ""), "conv": {k: f"{t.get('google_ads_id')}/{v}" for k, v in (t.get("conversions") or {}).items() if v and t.get("google_ads_id")},
           "gtm": bool(t.get("gtm_id")), "wa": WA_NUM}
    tags = [i for i in (t.get("google_ads_id"), "" if t.get("gtm_id") else t.get("ga4_id")) if i]
    ga = ""
    if tags:
        ga = (f'<script async src="https://www.googletagmanager.com/gtag/js?id={tags[0]}"></script><script>window.dataLayer=window.dataLayer||[];'
              "function gtag(){dataLayer.push(arguments);}gtag('js',new Date());" + "".join(f"gtag('config','{i}');" for i in tags) + "</script>")
    return f"""<!DOCTYPE html><html lang="ru"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(title)}</title><meta name="description" content="{e(desc)}"><link rel="canonical" href="{canon}">
<meta property="og:type" content="website"><meta property="og:title" content="{e(title)}"><meta property="og:description" content="{e(desc)}">
<meta property="og:url" content="{canon}"><meta property="og:image" content="{SITE}/media/p/{img}.webp"><meta name="theme-color" content="#0B1F3A">
<link rel="icon" href="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 32 32'%3E%3Crect width='32' height='32' rx='7' fill='%230B1F3A'/%3E%3Ccircle cx='16' cy='16' r='7' fill='none' stroke='white' stroke-width='3'/%3E%3Ccircle cx='24' cy='8' r='3' fill='%23ff7a1a'/%3E%3C/svg%3E">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Manrope:wght@700;800&family=Golos+Text:wght@400;500;600;700&display=swap" rel="stylesheet">
<link rel="stylesheet" href="{{R}}assets/lead.css"><style>{CSS}</style>
<script>window.EQ_CFG={json.dumps(cfg)};</script>{ga}{extra}</head><body>"""


def header(r):
    return f"""<header class="top"><div class="wrap"><a class="logo" href="{r}index.html"><i></i><span>{BRAND}<small>лазерная резка труб · Equipcn</small></span></a>
<nav class="mn"><a href="{r}index.html#series">Станки</a><a href="{r}index.html#compare">Сравнение</a><a href="{r}index.html#video">Видео</a><a href="{r}index.html#how">Как работаем</a><a href="{r}index.html#faq">Вопросы</a></nav>
<div class="hcta"><a class="btn btn-line" href="tel:+{WA_NUM}">{PHONE}</a><a class="btn btn-main" href="#lead">Получить расчёт</a></div></div></header>"""


def footer(r):
    links = "".join(f'<a href="{r}seriya/{s["slug"]}.html">{e(s["name"])}</a>' for s in SERIES)
    return f"""<footer><div class="wrap"><b style="color:#fff;font-family:var(--display);font-size:1.2rem">{BRAND}</b> — лазерные станки для резки труб с завода в Китае. Продажа и поставка: Equipcn, Алматы, ул. Жандосова, 4В · <a href="tel:+{WA_NUM}">{PHONE}</a> · Пн–Пт 10:00–18:00
<div class="fl">{links}<a href="https://equipcngroup.com/">Всё оборудование Equipcn</a><a href="https://equipcngroup.com/privacy">Политика обработки данных</a></div>
<div>Цены на сайте — ориентир на заводе в Китае ({RATE_NOTE}), без доставки в Казахстан и таможенных платежей. Не являются публичной офертой.</div></div></footer>
<div class="mbar"><a class="m1" href="#lead">Получить расчёт</a><a class="m2" href="https://wa.me/{WA_NUM}" target="_blank" rel="noopener">WhatsApp</a></div>
<a class="wa" style="display:none"></a><script defer src="{r}assets/lead.js"></script></body></html>"""


def vid(slug, title, r, autoplay=False):
    a = 'autoplay muted loop playsinline preload="metadata"' if autoplay else 'muted playsinline controls preload="none"'
    return f'<div class="vid"><video {a} poster="{r}media/v/{slug}.jpg"><source src="{r}media/v/{slug}.mp4" type="video/mp4"></video><span>{e(title)}</span></div>'


def card(s, r):
    return (f'<div class="card"><a class="ph" href="{r}seriya/{s["slug"]}.html"><img loading="lazy"{' class="wb"' if s["img"] in WHITE else ''} src="{r}media/p/{s["img"]}-c.webp" alt="{e(s["name"])} — лазерный станок для резки труб"></a>'
            f'<div class="bd"><span class="tg">{e(s["tag"])}</span><h3><a href="{r}seriya/{s["slug"]}.html" style="color:inherit;text-decoration:none">{e(s["name"])}</a></h3><p>{e(s["lead"])}</p>'
            f'<div class="pr"><small>от </small>{fm(s["from_kzt"])} ₸ <small>≈ ${fm(s["from_usd"])}</small></div>'
            f'<div class="bt"><a class="btn btn-line" href="{r}seriya/{s["slug"]}.html">Подробнее</a><a class="btn btn-main" href="#lead" data-ask="{e(s["name"])} — лазерный станок для резки труб">Узнать стоимость</a></div></div></div>')


def lead_box(title, text, place):
    return (f'<section class="blk" id="zayavka" data-place="{place}"><div class="wrap"><div class="lead-box"><div><span class="eyebrow">Заявка</span><h2>{e(title)}</h2><p>{e(text)}</p>'
            f'<div class="cl"><div><span>Телефон и WhatsApp</span><a href="tel:+{WA_NUM}">{PHONE}</a></div><div><span>Адрес</span>Алматы, ул. Жандосова, 4В</div><div><span>Часы работы</span>Пн–Пт 10:00–18:00</div></div></div>'
            f'<div data-leadform data-ph="Например: круглая труба ⌀60, стенка 3 мм, нержавейка" data-title="Получить стоимость с доставкой"></div></div></div></section>')


def page_index():
    r = ""
    min_kzt = min(s["from_kzt"] for s in SERIES)
    thick = "".join(f"<tr><td><b>{p}</b></td><td>{a}</td><td>{b}</td><td>{c}</td></tr>" for p, a, b, c in THICK)
    cmp_rows = "".join(f'<tr><td><a href="seriya/{s["slug"]}.html"><b>{e(s["name"])}</b></a><br><small>{e(s["tag"])}</small></td><td>{"<br>".join(e(c[0] + ": " + c[1]) for c in s["configs"])}</td><td>1500 / 2000 / 3000 Вт</td><td><b>от {fm(s["from_kzt"])} ₸</b><br><small>≈ ${fm(s["from_usd"])}</small></td></tr>' for s in SERIES)
    allv = [("m-3000w-5mm", "3000 Вт: сталь 5,5 мм"), ("mys-45", "Рез под 45° и гибка"), ("r219-max", "Труба ⌀219 мм"), ("xq-120-hvost", "Остаток трубы ~60 мм"),
            ("m-ugolok", "Резка уголка"), ("yq-2", "Перфорация профиля"), ("r219-1", "Перфорированная труба"), ("rezka-profil", "Фигурная резка")]
    faq_ld = {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in FAQ]}
    body = f"""{header(r)}<main>
<section class="hero" data-place="hero"><div class="wrap"><div>
<span class="eyebrow">Китай → Казахстан и СНГ</span>
<h1>Лазерные станки для резки труб напрямую с завода в Китае</h1>
<p class="sub">Круглые и профильные трубы, уголок, швеллер. Мощность 1500–3000 Вт, сталь до 6 мм. Подберём станок под ваши трубы и бюджет, проверим перед отправкой и доставим до вашего цеха.</p>
<ul class="ben"><li>Прямые поставки от производителя</li><li>Работа по официальному договору</li><li>Проверка оборудования перед отправкой</li><li>Сопровождение закупки и логистики</li><li>Индивидуальный подбор станка</li></ul>
<div class="ctas"><a class="btn btn-main" href="#lead">Получить расчёт стоимости</a><a class="btn btn-line" href="#series">Смотреть станки</a></div>
</div><div id="lead" data-leadform data-ph="Например: профильная труба 40×40, стенка 2 мм, чёрная сталь" data-title="Узнайте стоимость с доставкой"></div></div></section>
<div class="wrap"><div class="facts"><div><b>6 серий</b><span>от ручного патрона до скоростных</span></div><div><b>от {fm(min_kzt)} ₸</b><span>цена на заводе в Китае</span></div><div><b>до ⌀219 мм</b><span>трубы, до 6 мм стенка</span></div><div><b>Договор</b><span>и проверка перед отправкой</span></div></div></div>

<section class="blk" id="series"><div class="wrap"><span class="eyebrow" style="color:var(--logo)">Станки</span><h2>6 серий лазерных труборезов</h2>
<p class="lead">Цены — на заводе в Китае с экспортной упаковкой, без доставки в Казахстан. Реальную стоимость с доставкой до вашего города рассчитает менеджер.</p>
<div class="cards">{"".join(card(s, r) for s in SERIES)}</div>
<div class="nf"><div><b>Не нашли подходящий станок?</b><p>Отправьте нам фото труб или техническое задание — подберём подходящий вариант в Китае.</p></div><a class="btn btn-main" href="#zayavka">Отправить фото или ТЗ</a></div>
</div></section>

<section class="blk" id="compare" style="padding-top:0"><div class="wrap"><h2>Сравнение серий</h2><p class="lead">Все станки: лазер Raycus, головка Raytools, чиллер S&amp;A. Мощность — 1500, 2000 или 3000 Вт на выбор.</p>
<div class="tw"><table class="cmp"><tr><th>Серия</th><th>Патрон и трубы</th><th>Мощность</th><th>Цена</th></tr>{cmp_rows}</table></div>
<h2 style="margin-top:34px;font-size:1.5rem">Какую толщину режет</h2>
<div class="tw"><table class="cmp"><tr><th>Мощность лазера</th><th>Чёрная сталь</th><th>Нержавеющая сталь</th><th>Алюминий</th></tr>{thick}</table></div>
</div></section>

<section class="blk" id="video" style="padding-top:0"><div class="wrap"><h2>Видео резки</h2><p class="lead">Реальные видео с завода: резка круглых и профильных труб, уголка, перфорация.</p>
<div class="vids">{"".join(vid(a, b, r) for a, b in allv)}</div></div></section>

<section class="blk" id="how" style="padding-top:0"><div class="wrap"><h2>Как мы работаем</h2><p class="lead">Шесть шагов от заявки до станка в вашем цехе.</p>
<div class="steps">{"".join(f"<div><b>{a}</b><span>{b}</span></div>" for a, b in STEPS)}</div></div></section>

<section class="blk" id="trust" hidden style="padding-top:0"><div class="wrap"><h2>Проекты, отзывы и условия работы</h2><div class="tr-body"></div></div></section>

<section class="blk" id="faq" style="padding-top:0"><div class="wrap"><h2>Частые вопросы</h2><div class="faq">{"".join(f"<details><summary>{e(q)}</summary><p>{e(a)}</p></details>" for q, a in FAQ)}</div></div></section>
{lead_box("Получите расчёт стоимости с доставкой", "Напишите, какие трубы режете (диаметр, толщина стенки, материал), и оставьте телефон — подберём станок и посчитаем доставку до вашего города.", "contact")}
</main>{footer(r)}"""
    h = head(f"Лазерный станок для резки труб купить в Казахстане — цены | {BRAND}",
             f"Лазерные труборезы 1500–3000 Вт с завода в Китае: 6 серий, трубы до ⌀219 мм, сталь до 6 мм. Цены от {fm(min_kzt)} ₸. Договор, проверка, доставка по Казахстану и СНГ.",
             SITE + "/", "m-4", '<script type="application/ld+json">' + json.dumps(faq_ld, ensure_ascii=False) + "</script>")
    (OUT / "index.html").write_text((h + body).replace("{R}", r), "utf8")


def page_series(s):
    r = "../"
    th = "".join(f'<button type="button" data-src="{r}media/p/{p}-c.webp"{" class=on" if i == 0 else ""}><img loading="lazy" src="{r}media/p/{p}-c.webp" alt=""></button>' for i, p in enumerate(s["photos"]))
    rows = "".join(f'<tr><td>{e(c)}<br><small>{e(rng)}</small></td><td>{p}</td><td><b>{fm(kzt)} ₸</b><br><small>≈ ${fm(usd)}</small></td>'
                   f'<td><a class="btn btn-main" style="padding:8px 12px;font-size:.85rem" href="#lead" data-ask="{e(s["name"])}, {e(c)}, {p}">Узнать стоимость</a></td></tr>'
                   for c, rng, p, usd, kzt in s["rows"])
    others = "".join(card(o, r) for o in SERIES if o is not s)[:0]
    prod_ld = {"@context": "https://schema.org", "@type": "Product", "name": f"{s['name']} — лазерный станок для резки труб", "description": s["lead"],
               "image": [f"{SITE}/media/p/{p}.webp" for p in s["photos"][:3]], "brand": {"@type": "Brand", "name": BRAND},
               "offers": {"@type": "AggregateOffer", "priceCurrency": "KZT", "lowPrice": s["from_kzt"], "highPrice": max(x[4] for x in s["rows"]), "offerCount": len(s["rows"]), "availability": "https://schema.org/PreOrder"}}
    body = f"""{header(r)}<main class="wrap" data-view-item="{s['slug']}" data-name="{e(s['name'])}" data-cat="Лазерные труборезы">
<div class="crumbs"><a href="{r}index.html">Главная</a> / <a href="{r}index.html#series">Станки</a> / {e(s['name'])}</div>
<div class="sp"><div class="gal"><div class="main"><img id="mi" src="{r}media/p/{s['photos'][0]}-c.webp" alt="{e(s['name'])} — лазерный станок для резки труб"></div><div class="th">{th}</div></div>
<div><span class="eyebrow" style="color:var(--logo)">{e(s['tag'])}</span><h1>{e(s['name'])} — лазерный станок для резки труб</h1><p>{e(s['lead'])}</p>
<div class="price"><small>от </small>{fm(s['from_kzt'])} ₸ <small>≈ ${fm(s['from_usd'])}</small></div>
<p class="note">Цена на заводе в Китае с экспортной упаковкой, без доставки в Казахстан и таможенных платежей. Реальную стоимость доставки уточнит менеджер.</p>
<div id="lead" data-place="series" data-leadform data-title="Узнать стоимость с доставкой" data-product="{e(s['name'])}" data-need="Нужна стоимость с доставкой: {e(s['name'])}"></div>
<p style="margin-top:12px"><a class="btn btn-line" href="https://wa.me/{WA_NUM}?text={e('Здравствуйте! Интересует ' + s['name'] + ' (лазерный станок для резки труб)')}" target="_blank" rel="noopener">Спросить в WhatsApp</a></p></div></div>
<div class="box"><h2>Комплектации и цены</h2><div class="tw" style="margin-top:10px"><table class="cmp ptab"><tr><th>Патрон / трубы</th><th>Мощность</th><th>Цена на заводе</th><th></th></tr>{rows}</table></div>
<p class="note">{RATE_NOTE}. Цена без доставки и таможенных платежей; точную сумму фиксируем в коммерческом предложении.</p></div>
<div class="box"><h2>Особенности</h2><ul>{"".join(f"<li>{e(x)}</li>" for x in s['feats'])}</ul></div>
<div class="sp" style="margin-top:0"><div class="box"><h2>Комплектующие</h2><table class="kv">{"".join(f"<tr><td>{a}</td><td>{b}</td></tr>" for a, b in s['cfg'])}</table></div>
<div class="box"><h2>Толщина резки</h2><table class="kv"><tr><td><b>Мощность</b></td><td><b>Сталь / нерж. / алюминий</b></td></tr>{"".join(f"<tr><td>{p}</td><td>{a} / {b} / {c}</td></tr>" for p, a, b, c in THICK)}</table></div></div>
<div class="box"><h2>Видео резки</h2><div class="vids" style="margin-top:12px">{"".join(vid(a, b, r) for a, b in s['videos'])}</div></div>
<div class="box"><h2>Как мы работаем</h2><div class="steps" style="margin-top:12px">{"".join(f"<div><b>{a}</b><span>{b}</span></div>" for a, b in STEPS)}</div></div>
<div class="box faq"><h2>Частые вопросы</h2>{"".join(f"<details><summary>{e(q)}</summary><p>{e(a)}</p></details>" for q, a in FAQ)}</div>
<div class="box"><h2>Другие серии</h2><p>{" · ".join(f'<a href="{o["slug"]}.html">{e(o["name"])} — от {fm(o["from_kzt"])} ₸</a>' for o in SERIES if o is not s)}</p></div>
</main>
{lead_box("Получите расчёт с доставкой", "Опишите ваши трубы и задачу — подберём комплектацию и посчитаем доставку до вашего города.", "series-bottom")}
<script>document.querySelectorAll('.gal .th button').forEach(b=>b.onclick=()=>{{document.getElementById('mi').src=b.dataset.src;document.querySelectorAll('.gal .th button').forEach(x=>x.classList.toggle('on',x===b));}});</script>
{footer(r)}"""
    h = head(f"{s['name']} — лазерный станок для резки труб, цена от {fm(s['from_kzt'])} ₸ | {BRAND}",
             f"{s['name']}: {s['tag']}. {s['lead']} Цена от {fm(s['from_kzt'])} ₸ на заводе в Китае. Доставка в Казахстан и СНГ.",
             f"{SITE}/seriya/{s['slug']}.html", s["photos"][0], '<script type="application/ld+json">' + json.dumps(prod_ld, ensure_ascii=False) + "</script>")
    (OUT / "seriya").mkdir(exist_ok=True)
    (OUT / "seriya" / f"{s['slug']}.html").write_text((h + body).replace("{R}", r), "utf8")


def main():
    page_index()
    for s in SERIES:
        page_series(s)
    today = datetime.date.today().isoformat()
    urls = [SITE + "/"] + [f"{SITE}/seriya/{s['slug']}.html" for s in SERIES]
    (OUT / "sitemap.xml").write_text('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
                                     + "".join(f"<url><loc>{u}</loc><lastmod>{today}</lastmod></url>\n" for u in urls) + "</urlset>\n", "utf8")
    for s in SERIES:
        print(s["name"], "от", fm(s["from_kzt"]), "₸", [(c[:12], p, usd, kzt) for c, _, p, usd, kzt in s["rows"]])


if __name__ == "__main__":
    main()
