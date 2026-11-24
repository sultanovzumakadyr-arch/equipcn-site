"""Выгрузка каталога (для приложения) и таблицы источников цен. Запуск: python scraper/export.py <папка>"""
import json, re, sys, pathlib
import pandas as pd
from openpyxl import load_workbook
from openpyxl.styles import Font, PatternFill

ROOT = pathlib.Path(__file__).resolve().parent.parent
out = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else ROOT / "export")
out.mkdir(parents=True, exist_ok=True)
t = (ROOT / "site" / "index.html").read_text("utf8")
i = t.index("const PRODUCTS=") + 15
P, _ = json.JSONDecoder().raw_decode(t[i:])
G = dict(json.loads(re.search(r"const GROUPS=(\[.*?\])\.concat", t).group(1))); G["other"] = "Другое оборудование"
d = json.loads((ROOT / "data" / "extra.json").read_text("utf8")); ex = {e["id"]: e for e in d}

def style(path, widths, links):
    wb = load_workbook(path); ws = wb.active
    for c in ws[1]: c.font = Font(name="Arial", bold=True, color="FFFFFF"); c.fill = PatternFill("solid", fgColor="0B3D91")
    for r in ws.iter_rows(min_row=2):
        for c in r: c.font = Font(name="Arial")
        for j in links:
            c = r[j]
            if c.value and str(c.value).startswith("http") and "," not in str(c.value):
                c.hyperlink = c.value; c.font = Font(name="Arial", color="1F5FC9", underline="single")
    for k, w in enumerate(widths): ws.column_dimensions[chr(65 + k)].width = w
    ws.freeze_panes = "A2"; ws.auto_filter.ref = ws.dimensions; wb.save(path)

rows = []
for p in P:
    pr = str(p.get("price", "")); n = int(re.sub(r"\D", "", pr) or 0)
    rows.append({"Код": p["id"], "Направление": G.get(p["cat"], p["cat"]), "Название": p["name"], "Цена, ₸": n or None,
                 "Тип цены": "от" if pr.startswith("~") else ("точная" if n else "по запросу"),
                 "Источник": "подбор Equipcn" if p["id"] in ex else "Satu",
                 "Характеристики": "; ".join(f"{a}: {b}" for a, b in p.get("specs", [])), "Описание": p.get("desc", ""),
                 "Фото": ", ".join(x if x.startswith("http") else "https://equipcngroup.com/" + x for x in p.get("images", [])),
                 "Ссылка": f"https://equipcngroup.com/#p-{p['id']}"})
df = pd.DataFrame(rows); base = out / "equipcn-katalog"
df.to_csv(f"{base}.csv", index=False, encoding="utf-8-sig")
json.dump(rows, open(f"{base}.json", "w", encoding="utf8"), ensure_ascii=False, indent=1)
df.to_excel(f"{base}.xlsx", index=False, sheet_name="Каталог"); style(f"{base}.xlsx", [10, 26, 50, 14, 11, 14, 60, 60, 40, 34], [9])

src = [{"Код": e["id"], "Направление": G.get(e["cat"], e["cat"]), "Название": e["name"], "Ссылка на сайте": f"https://equipcngroup.com/#p-{e['id']}",
        "Цена на сайте, ₸ (от)": int(e["price"].lstrip("~")), "Наш FOB, $": e["fob_usd"], "Цена в объявлении, $": e.get("source_price_usd", ""),
        "Объявление (откуда фото)": e["source_url"], "Фото": e["images"][0] if e["images"] else "",
        "Поиск Alibaba": e["src"]["alibaba"], "Поиск Made-in-China": e["src"]["made_in_china"]} for e in d]
o = out / "equipcn-istochniki-tsen.xlsx"
pd.DataFrame(src).to_excel(o, index=False, sheet_name="Источники"); style(o, [9, 24, 46, 32, 16, 11, 16, 50, 40, 22, 22], [3, 7, 8, 9, 10])
print(len(df), len(src))
