"""Idempotently create the QHI AUTO 100-card illustrative demo catalog.

Run from the repository root while the local API is running and backend/.env
targets a disposable local database. The importer uses the existing admin API
so each write is validated and audited by the application.
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from sqlalchemy.engine import make_url


ROOT = Path(__file__).resolve().parents[1]
ENV_PATH = ROOT / "backend" / ".env"
API = "http://127.0.0.1:8000/api/v1"
LICENSE = "Unsplash License (commercial use allowed; attribution appreciated)"
LICENSE_URL = "https://unsplash.com/license"
YEARS = (2022, 2023, 2024, 2025, 2026)
PRICE_FACTORS = (0.82, 0.92, 1.0, 1.12, 1.24)
RANGE_FACTORS = (0.90, 0.96, 1.0, 1.06, 1.10)
POWER_FACTORS = (0.82, 0.92, 1.0, 1.10, 1.20)
COLORS = ("Pearl white", "Graphite", "Silver", "Deep blue", "Black")

# Representative public stock car photos. They are explicitly described as
# illustrative and are not claimed to depict the named vehicle or trim.
PHOTO_IDS = (
    "photo-1494976388531-d1058494cdd8",
    "photo-1503376780353-7e6692767b70",
    "photo-1552519507-da3b142c6e3d",
    "photo-1533473359331-0135ef1b58bf",
    "photo-1549399542-7e3f8b79c341",
    "photo-1583121274602-3e2820c69888",
)

# brand, model, category, indicative USD price, range km, battery kWh, power
# kW, torque Nm, 0-100 sec, top speed, drivetrain, dimensions mm (L/W/H/WB),
# seats, is plug-in hybrid, openly available model reference.
MODELS = (
    ("BYD", "Han EV", "sedan", 28000, 605, 85.4, 380, 700, 3.9, 180, "AWD", (4995, 1910, 1495, 2920), 5, False, "BYD_Han"),
    ("BYD", "Seal", "sedan", 26000, 650, 82.5, 390, 670, 3.8, 180, "AWD", (4800, 1875, 1460, 2920), 5, False, "BYD_Seal"),
    ("BYD", "Dolphin", "economy", 14500, 420, 60.5, 150, 310, 7.0, 160, "FWD", (4290, 1770, 1570, 2700), 5, False, "BYD_Dolphin"),
    ("BYD", "Atto 3", "crossover", 19000, 480, 60.5, 150, 310, 7.3, 160, "FWD", (4455, 1875, 1615, 2720), 5, False, "BYD_Atto_3"),
    ("BYD", "Tang EV", "suv", 36000, 635, 108.8, 380, 700, 4.4, 180, "AWD", (4900, 1950, 1725, 2820), 7, False, "BYD_Tang"),
    ("BYD", "Song Plus EV", "suv", 22500, 520, 87.0, 160, 330, 8.5, 175, "FWD", (4785, 1890, 1660, 2765), 5, False, "BYD_Song_Plus"),
    ("BYD", "Seagull", "economy", 10500, 405, 38.9, 55, 135, 13.0, 130, "FWD", (3780, 1715, 1540, 2500), 4, False, "BYD_Seagull"),
    ("BYD", "Qin Plus EV", "sedan", 15500, 510, 57.6, 150, 250, 7.5, 150, "FWD", (4765, 1837, 1515, 2718), 5, False, "BYD_Qin_Plus"),
    ("BYD", "Yuan Up", "crossover", 13000, 401, 45.1, 130, 290, 7.9, 160, "FWD", (4310, 1830, 1675, 2620), 5, False, "BYD_Yuan_Up"),
    ("BYD", "Song L", "suv", 26500, 662, 87.0, 380, 670, 4.3, 201, "AWD", (4840, 1950, 1560, 2930), 5, False, "BYD_Song_L"),
    ("Tesla", "Model 3", "sedan", 32000, 606, 75.0, 366, 493, 4.4, 201, "RWD", (4720, 1848, 1442, 2875), 5, False, "Tesla_Model_3"),
    ("Tesla", "Model Y", "suv", 35000, 600, 75.0, 378, 493, 5.0, 217, "AWD", (4750, 1921, 1624, 2890), 5, False, "Tesla_Model_Y"),
    ("XPeng", "P7", "sedan", 25000, 610, 86.2, 348, 757, 4.1, 200, "AWD", (4888, 1896, 1450, 2998), 5, False, "Xpeng_P7"),
    ("XPeng", "G6", "crossover", 24500, 580, 87.5, 358, 660, 4.1, 202, "AWD", (4758, 1920, 1650, 2890), 5, False, "Xpeng_G6"),
    ("XPeng", "G9", "suv", 38000, 570, 98.0, 405, 717, 3.9, 200, "AWD", (4891, 1937, 1680, 2998), 5, False, "Xpeng_G9"),
    ("NIO", "ET5", "sedan", 36000, 560, 100.0, 360, 700, 4.0, 200, "AWD", (4790, 1960, 1499, 2888), 5, False, "Nio_ET5"),
    ("NIO", "ES6", "suv", 39000, 490, 100.0, 360, 700, 4.5, 200, "AWD", (4854, 1995, 1703, 2915), 5, False, "Nio_ES6"),
    ("Zeekr", "001", "sports", 34000, 620, 100.0, 400, 686, 3.8, 240, "AWD", (4977, 1999, 1533, 3005), 5, False, "Zeekr_001"),
    ("Zeekr", "X", "crossover", 22500, 500, 66.0, 315, 543, 3.8, 190, "AWD", (4450, 1836, 1572, 2750), 5, False, "Zeekr_X"),
    ("Li Auto", "L7", "suv", 41000, 225, 42.8, 330, 620, 5.3, 180, "AWD", (5050, 1995, 1750, 3005), 5, True, "Li_Auto_L7"),
)


def read_admin_token() -> str:
    if not ENV_PATH.exists():
        raise SystemExit(f"Missing local backend settings: {ENV_PATH}")
    values = {}
    for line in ENV_PATH.read_text(encoding="utf-8").splitlines():
        if "=" in line and not line.lstrip().startswith("#"):
            key, _, value = line.partition("=")
            values[key.strip()] = value.strip().strip("\"'")
        if line.startswith("ADMIN_API_KEY="):
            token = line.partition("=")[2].strip().strip("\"'")
            if len(token) < 32:
                break
    dsn = values.get("DATABASE_URL")
    if not dsn:
        raise SystemExit("DATABASE_URL is missing; demo import requires a local disposable test database.")
    database = make_url(dsn)
    if database.host not in {"127.0.0.1", "localhost", "::1"} or not (database.database or "").endswith("_test"):
        raise SystemExit("Refusing to import: DATABASE_URL must target a loopback database ending in _test.")
    token = values.get("ADMIN_API_KEY", "")
    if len(token) >= 32:
        return token
    raise SystemExit("A local ADMIN_API_KEY of at least 32 characters is required.")


def api(method: str, path: str, token: str, payload: dict | None = None):
    body = json.dumps(payload).encode() if payload is not None else None
    request = Request(
        API + path,
        data=body,
        method=method,
        headers={"X-Admin-Token": token, "Content-Type": "application/json"},
    )
    try:
        with urlopen(request, timeout=20) as response:
            return json.loads(response.read())
    except (HTTPError, URLError) as error:
        detail = error.read().decode("utf-8", "replace") if isinstance(error, HTTPError) else str(error)
        raise SystemExit(f"Admin API {method} {path} failed: {detail}") from error


def slug_piece(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")


def photo_items(model_index: int, variant: int, title: str) -> list[dict]:
    items = []
    for view in range(3):
        photo_id = PHOTO_IDS[(model_index * 3 + variant + view) % len(PHOTO_IDS)]
        url = f"https://images.unsplash.com/{photo_id}?auto=format&fit=crop&w=1400&q=82"
        items.append({
            "url": url,
            "alt": f"Illustrative car photo for the QHI AUTO demo card {title}; not a photo of a specific vehicle",
            "attribution": "Unsplash contributor; attribution appreciated",
            "license_name": LICENSE,
            "source_url": url,
        })
    return items


def car_payload(model_index: int, row: tuple, variant: int) -> dict:
    (brand, model, category, base_usd, base_range, battery, base_power, torque,
     acceleration, max_speed, drivetrain, dimensions, seats, is_phev, wiki_slug) = row
    year = YEARS[variant]
    title = f"{brand} {model} · QHI Demo {variant + 1}"
    slug = "demo-" + slug_piece(f"{brand}-{model}-{year}-{variant + 1}")
    usd = round(base_usd * PRICE_FACTORS[variant] / 100) * 100
    tjs = round(usd * 10.9 / 100) * 100
    cny = round(usd * 7.2 / 100) * 100
    range_km = round(base_range * RANGE_FACTORS[variant] / 5) * 5
    power_kw = round(base_power * POWER_FACTORS[variant] / 5) * 5
    length, width, height, wheelbase = dimensions
    note_ru = "ДЕМО-цена и комплектация для показа каталога; не является предложением о продаже. Фото иллюстративные."
    note_tg = "Нархи ДЕМО ва маҷмӯа танҳо барои намоиши каталоганд; пешниҳоди фурӯш нестанд. Суратҳо тасвирӣ мебошанд."
    note_en = "DEMO price and trim for catalog display only; not an offer for sale. Photos are illustrative."
    spec_ru = f"Ориентировочные демонстрационные данные для модельного семейства {brand} {model}; год и комплектация не обозначают реальный автомобиль."
    spec_tg = f"Маълумоти тахминии намоишӣ барои оилаи модели {brand} {model}; сол ва маҷмӯа мошини воқеиро нишон намедиҳанд."
    spec_en = f"Illustrative reference values for the {brand} {model} model family; year and trim do not represent an actual vehicle."
    return {
        "slug": slug,
        "brand": brand,
        "model": model,
        "trim": f"QHI Demo Trim {variant + 1}",
        "year": year,
        "price_cny": cny,
        "price_usd": usd,
        "price_tjs": tjs,
        "price_note": "DEMO estimate only. No real vehicle, seller, or offer is represented.",
        "range_km": range_km,
        "battery_kwh": round(battery * RANGE_FACTORS[variant], 1),
        "power_kw": power_kw,
        "drivetrain": drivetrain,
        "category": category,
        "engine_type": "plug-in hybrid" if is_phev else "battery electric",
        "engine_cc": 1500 if is_phev else None,
        "fuel_type": "plug-in hybrid" if is_phev else "electric",
        "fuel_consumption_l_100km": 1.5 if is_phev else None,
        "torque_nm": round(torque * POWER_FACTORS[variant] / 10) * 10,
        "acceleration_0_100_s": round(acceleration / POWER_FACTORS[variant], 2),
        "max_speed_kmh": max_speed,
        "seats": seats,
        "doors": 4,
        "length_mm": length,
        "width_mm": width,
        "height_mm": height,
        "wheelbase_mm": wheelbase,
        "advantages": "Demo entry for catalog, search, filters, and gallery preview.",
        "specification_source": f"https://en.wikipedia.org/wiki/{wiki_slug}",
        "transmission": "Single-speed reduction gear" if not is_phev else "Hybrid automatic",
        "exterior_color": COLORS[variant],
        "equipment": "Illustrative demo trim; equipment list is not a real vehicle specification.",
        "specifications": f"{spec_ru}\n{spec_en}",
        "is_demo": True,
        "availability": "on_request",
        "published": True,
        "image_items": photo_items(model_index, variant, title),
        "translations": [
            {"locale": "ru", "title": title, "description": f"{spec_ru} {note_ru}"},
            {"locale": "tg", "title": title, "description": f"{spec_tg} {note_tg}"},
            {"locale": "en", "title": title, "description": f"{spec_en} {note_en}"},
        ],
    }


def main() -> None:
    token = read_admin_token()
    cars = api("GET", "/admin/cars", token)
    existing = {car["slug"]: car for car in cars}
    demo_slugs = {
        "demo-" + slug_piece(f"{row[0]}-{row[1]}-{year}-{variant + 1}")
        for row in MODELS for variant, year in enumerate(YEARS)
    }
    created = 0
    updated = 0
    for model_index, row in enumerate(MODELS):
        for variant, _year in enumerate(YEARS):
            payload = car_payload(model_index, row, variant)
            current = existing.get(payload["slug"])
            if current is None:
                result = api("POST", "/admin/cars", token, payload)
                existing[result["slug"]] = result
                created += 1
            elif [item["url"] for item in current["image_details"]] != [item["url"] for item in payload["image_items"]]:
                result = api("PUT", f"/admin/cars/{current['id']}", token, payload)
                existing[result["slug"]] = result
                updated += 1

    inserted = [existing[slug] for slug in sorted(demo_slugs) if slug in existing]
    if len(inserted) != 100:
        raise SystemExit(f"Expected 100 demo cards, found {len(inserted)}")
    if any(not car["is_demo"] or not car["published"] or len(car["images"]) != 3 for car in inserted):
        raise SystemExit("Demo validation failed: check demo flags, publication, or gallery size")
    print(f"Demo catalog ready: total={len(inserted)} created={created} image_updates={updated} images={sum(len(c['images']) for c in inserted)}")
    print("All 100 cards have is_demo=true, three licensed illustrative photos, RU/TG/EN descriptions, and USD/TJS demo prices.")


if __name__ == "__main__":
    main()
