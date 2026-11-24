"""Собирает site/index.html из шаблона и данных.

data/curated.txt — наши проверенные группы, названия и цены (id|группа|название|цена|фото).
data/scraped.json — то, что собрал scrape.py (описания, фото, новые товары).
Новые товары, которых нет в curated.txt, получают группу автоматически по ключевым словам.
"""
import json, re, pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
RULES = [
    ("fish", r"рыб|узв|аэратор|озонатор|икр|аквакульт|лосос"),
    ("mine", r"щеков|конусн|мельниц|флотац|золот|грохот|концентрац|руд"),
    ("wood", r"mingan|мебел|лдсп|мдф|древесин|дерев|кромкооблиц|фасад"),
    ("glass", r"стекл|окон|оконн|триплекс"),
    ("build", r"бетон|блок|брусчат|бордюр|асфальт|кирпич|газоблок|пенобетон|профнастил|металлочерепиц|сетк|забор|желоб|сухих строит|арматур"),
    ("auto", r"автомо|шиномонт|балансир|автосерв|стиральн|поломоечн|форсун|прачечн"),
    ("elec", r"smt|pcb|печатн|пайк|паяльн|hmi|сенсорн"),
    ("air", r"vrf|фанкойл|кондицион|приточно|осушител|вентилятор|hvac"),
    ("power", r"компрессор|генератор|энерг|насос|частотн"),
    ("agro", r"корм|комбикорм|зерн|комбайн|доильн|инкубатор|птиц|медогон|пчел|соломы|силос|теплиц"),
    ("food", r"розлив|молок|макарон|лапш|консерв|мяс|коптил|хлеб|печь|маслопресс|сушил|овощ|фрукт|куттер|льдо|лёд|холодильн|пищев"),
    ("pack", r"упаков|фасовк|бумажн|стакан|тарел|гофрокартон|пакет|принтер|паллет|запайщик"),
    ("plast", r"пластик|экструз|экструдер|шредер|pet|шин|резинов|текстил|мусор|отход|кабел|макулатур|полистирол|пленк|плёнк|перчат|салфет"),
    ("metal", r"лазер|станок|cnc|чпу|гиб|токарн|фрезер|пресс|плазм|свар|ножниц|пил|сверл|проволок|маркир"),
]


def guess_group(name):
    low = name.lower()
    for g, rx in RULES:
        if re.search(rx, low):
            return g
    return "other"


def clean_name(n):
    n = re.sub(r"\s+", " ", n).replace("Краткое описание", "").strip()
    n = re.split(r" \| | \|\| | — ", n)[0].strip()
    return n[:1].upper() + n[1:]


def tracking_html():
    tp = ROOT / "data" / "tracking.json"
    if not tp.exists():
        return ""
    t = json.loads(tp.read_text("utf8"))
    ads, ga = t.get("google_ads_id", "").strip(), t.get("ga4_id", "").strip()
    if not ads and not ga:
        return ""
    first = ads or ga
    conv = {k: v for k, v in (t.get("conversions") or {}).items() if v}
    cfg = "".join(f"gtag('config','{i}');" for i in (ads, ga) if i)
    return ("<script async src=\"https://www.googletagmanager.com/gtag/js?id=" + first + "\"></script>"
            "<script>window.dataLayer=window.dataLayer||[];function gtag(){dataLayer.push(arguments);}"
            "gtag('js',new Date());" + cfg +
            "window.EQ_CONV=" + json.dumps({k: f"{ads}/{v}" for k, v in conv.items()} if ads else {}) + ";</script>")


def main():
    curated = {}
    for line in (ROOT / "data" / "curated.txt").read_text("utf8").strip().splitlines():
        pid, g, name, price, img = (line.split("|") + [""] * 5)[:5]
        curated[pid] = {"id": pid, "cat": g, "name": name, "price": price, "img": img}
    sp = ROOT / "data" / "scraped.json"
    scraped = json.loads(sp.read_text("utf8")) if sp.exists() else []
    hp = ROOT / "data" / "hidden.txt"
    hidden = set(hp.read_text("utf8").split()) if hp.exists() else set()
    scraped = [x for x in scraped if x["id"] not in hidden]
    products = []
    if scraped:
        for s in scraped:
            c = curated.get(s["id"])
            p = {
                "id": s["id"],
                "cat": c["cat"] if c else guess_group(s["name"]),
                "name": c["name"] if c else clean_name(s["name"]),
                "price": c["price"] if c and c["price"] else s.get("price", ""),
                "images": s.get("images") or [],
                "desc": s.get("desc", ""),
                "specs": s.get("specs", []),
            }
            products.append(p)
    else:  # данных сборщика ещё нет — используем список и фото с Сату
        for c in curated.values():
            products.append({"id": c["id"], "cat": c["cat"], "name": c["name"], "price": c["price"],
                             "images": [f"https://images.satu.kz/{c['img']}_w640_h640_p.jpg"] if c["img"] else [],
                             "desc": "", "specs": []})
    # товары, добавленные напрямую на сайт (без Сату): data/extra.json
    ep = ROOT / "data" / "extra.json"
    if ep.exists():
        known = {p["id"] for p in products}
        for e in json.loads(ep.read_text("utf8")):
            if e.get("id") in hidden or e.get("id") in known:
                continue
            products.append({"id": e["id"], "cat": e.get("cat") or guess_group(e["name"]), "name": e["name"],
                             "price": str(e.get("price", "")), "images": e.get("images", []),
                             "desc": e.get("desc", ""), "specs": e.get("specs", [])})
    products.sort(key=lambda p: (p["price"] == "", p["cat"]))
    tpl = (ROOT / "template.html").read_text("utf8")
    data = json.dumps(products, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")
    html = re.sub(r"/\*DATA\*/.*?/\*END\*/", lambda m: data, tpl, count=1, flags=re.S)
    html = html.replace("</head>", tracking_html() + "</head>", 1)
    out = ROOT / "site" / "index.html"
    out.parent.mkdir(exist_ok=True)
    out.write_text(html, "utf8")
    new = [p for p in products if p["id"] not in curated]
    print(f"Собрано: {len(products)} товаров, новых без ручной группы: {len(new)}")


if __name__ == "__main__":
    main()
