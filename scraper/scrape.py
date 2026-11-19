"""Сборщик каталога с сайта на Сату (equipcngroup.com).

Проходит по всем страницам каталога, открывает каждый товар и сохраняет:
название, цену, полное описание и фотографии.
Результат: data/scraped.json и фото в site/img/.
Уже скачанные фото повторно не скачиваются.
"""
import json, re, time, pathlib, sys
import requests
from bs4 import BeautifulSoup

BASE = "https://equipcngroup.com"
ROOT = pathlib.Path(__file__).resolve().parent.parent
IMG_DIR = ROOT / "site" / "img"
OUT = ROOT / "data" / "scraped.json"
MAX_IMAGES = 6
S = requests.Session()
S.headers.update({
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0 Safari/537.36",
    "Accept-Language": "ru-RU,ru;q=0.9",
})
PID = re.compile(r"/p(\d+)-[^\"'?#\s]*\.html")


def get(url, tries=4):
    for i in range(tries):
        try:
            r = S.get(url, timeout=40)
            if r.status_code == 200:
                return r
            print(f"  {r.status_code} {url}")
        except requests.RequestException as e:
            print(f"  error {e} {url}")
        time.sleep(3 * (i + 1))
    return None


def list_products():
    found = {}
    page = 1
    while page < 60:
        url = f"{BASE}/product_list" + ("" if page == 1 else f"/page_{page}")
        r = get(url)
        if not r:
            break
        new = 0
        for m in PID.finditer(r.text):
            pid = m.group(1)
            if pid not in found:
                found[pid] = m.group(0)
                new += 1
        print(f"Страница {page}: +{new}, всего {len(found)}")
        if new == 0:
            break
        page += 1
        time.sleep(1)
    return found


def text_of(el):
    for br in el.find_all("br"):
        br.replace_with("\n")
    for p in el.find_all(["p", "li", "div", "h2", "h3", "h4", "tr"]):
        p.insert_after("\n")
    t = el.get_text("")
    t = re.sub(r"[ \t ]+", " ", t)
    t = re.sub(r"\n\s*\n+", "\n\n", t)
    return t.strip()


def parse_product(pid, path):
    r = get(BASE + path)
    if not r:
        return None
    soup = BeautifulSoup(r.text, "html.parser")
    prod = {}
    for s in soup.find_all("script", type="application/ld+json"):
        try:
            data = json.loads(s.string or "")
        except Exception:
            continue
        items = data if isinstance(data, list) else [data]
        for it in items:
            if isinstance(it, dict) and it.get("@type") == "Product":
                prod = it
    name = (soup.find("h1").get_text(" ", strip=True) if soup.find("h1") else prod.get("name", "")).strip()
    # описание: блок описания на странице, иначе описание из разметки
    desc = ""
    for sel in ['[data-qaid="product_description"]', '[data-qaid="descriptions"]', '[itemprop="description"]', ".b-user-content"]:
        el = soup.select_one(sel)
        if el and len(el.get_text(strip=True)) > 20:
            desc = text_of(el)
            break
    if not desc:
        desc = (prod.get("description") or "").strip()
    # характеристики
    specs = []
    for row in soup.select('[data-qaid="attribute_row"], .b-product-info tr'):
        cells = [c.get_text(" ", strip=True) for c in row.find_all(["td", "th", "span"], recursive=True) if c.get_text(strip=True)]
        if len(cells) >= 2:
            specs.append([cells[0], cells[-1]])
    imgs = prod.get("image") or []
    if isinstance(imgs, str):
        imgs = [imgs]
    if not imgs:
        imgs = [m for m in re.findall(r"https://images\.satu\.kz/\d+_w\d+_h\d+_[^\"'\s]+\.(?:jpg|jpeg|png|webp)", r.text)]
    seen, ids = set(), []
    for u in imgs:
        m = re.search(r"images\.satu\.kz/(\d+)_", str(u))
        if m and m.group(1) not in seen:
            seen.add(m.group(1))
            ids.append(m.group(1))
    offer = prod.get("offers") or {}
    if isinstance(offer, list):
        offer = offer[0] if offer else {}
    price = str(offer.get("price") or "").split(".")[0]
    return {"id": pid, "path": path, "name": name, "price": price, "desc": desc,
            "specs": specs[:30], "img_ids": ids[:MAX_IMAGES]}


def download_images(p):
    files = []
    for n, iid in enumerate(p["img_ids"]):
        f = IMG_DIR / f"{p['id']}_{n}.jpg"
        if not f.exists() or f.stat().st_size < 1000:
            r = get(f"https://images.satu.kz/{iid}_w800_h800_{p['id']}.jpg")
            if not r or not r.headers.get("content-type", "").startswith("image"):
                continue
            f.write_bytes(r.content)
            time.sleep(0.3)
        files.append(f"img/{f.name}")
    return files


def main():
    IMG_DIR.mkdir(parents=True, exist_ok=True)
    old = {}
    if OUT.exists():
        old = {p["id"]: p for p in json.loads(OUT.read_text("utf8"))}
    links = list_products()
    if len(links) < 10:
        print("Слишком мало товаров найдено, оставляю старые данные.")
        sys.exit(0 if old else 1)
    result = []
    for i, (pid, path) in enumerate(links.items(), 1):
        p = parse_product(pid, path)
        if not p:
            if pid in old:
                result.append(old[pid])
            continue
        p["images"] = download_images(p)
        result.append(p)
        print(f"[{i}/{len(links)}] {p['name'][:60]} — фото: {len(p['images'])}, описание: {len(p['desc'])} симв.")
        time.sleep(0.7)
    OUT.write_text(json.dumps(result, ensure_ascii=False, indent=1), "utf8")
    print(f"Готово: {len(result)} товаров")


if __name__ == "__main__":
    main()
