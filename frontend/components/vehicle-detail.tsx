"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { ContactTools } from "@/components/contact-tools";
import { fetchCar, type Car } from "@/lib/api";
import type { Locale } from "@/lib/i18n";

const copy = {
  ru: { back: "Назад в каталог", loading: "Загружаем автомобиль…", error: "Не удалось загрузить автомобиль.", description: "Описание", specs: "Характеристики", year: "Год выпуска", price: "Цена в Китае", range: "Запас хода", battery: "Батарея", power: "Мощность", drive: "Привод", availability: "Наличие", contact: "Рассчитать стоимость" },
  tg: { back: "Бозгашт ба феҳрист", loading: "Мошин бор шуда истодааст…", error: "Мошин бор нашуд.", description: "Тавсиф", specs: "Хусусиятҳо", year: "Соли истеҳсол", price: "Нарх дар Чин", range: "Масофаи ҳаракат", battery: "Батарея", power: "Қувва", drive: "Привод", availability: "Мавҷудият", contact: "Ҳисоб кардани арзиш" },
  en: { back: "Back to catalog", loading: "Loading vehicle…", error: "Could not load this vehicle.", description: "Description", specs: "Specifications", year: "Model year", price: "Price in China", range: "Driving range", battery: "Battery", power: "Power", drive: "Drivetrain", availability: "Availability", contact: "Estimate total cost" },
} satisfies Record<Locale, Record<string, string>>;

const number = (locale: Locale) => new Intl.NumberFormat(locale === "en" ? "en-US" : locale === "tg" ? "tg-TJ" : "ru-RU", { maximumFractionDigits: 0 });

export function VehicleDetail({ locale, slug }: { locale: Locale; slug: string }) {
  const t = copy[locale];
  const [car, setCar] = useState<Car | null>(null);
  const [state, setState] = useState<"loading" | "ready" | "error">("loading");

  useEffect(() => {
    const controller = new AbortController();
    setState("loading");
    fetchCar(slug, locale, controller.signal)
      .then((vehicle) => { setCar(vehicle); setState("ready"); })
      .catch((error: unknown) => {
        if (!(error instanceof DOMException && error.name === "AbortError")) setState("error");
      });
    return () => controller.abort();
  }, [locale, slug]);

  if (state === "loading") return <main className="vehicle-state" role="status">{t.loading}</main>;
  if (state === "error" || !car) return <main className="vehicle-state" role="alert"><p>{t.error}</p><Link className="button" href={`/${locale}`}>{t.back}</Link></main>;

  const title = car.localized_title ?? `${car.brand} ${car.model}`;
  const money = number(locale).format(Number(car.price_cny));
  const facts = [
    [t.year, String(car.year)],
    [t.price, `${money} CNY`],
    [t.range, car.range_km ? `${number(locale).format(car.range_km)} km` : "—"],
    [t.battery, car.battery_kwh ? `${car.battery_kwh} kWh` : "—"],
    [t.power, car.power_kw ? `${car.power_kw} kW` : "—"],
    [t.drive, car.drivetrain ?? "—"],
    [t.availability, car.availability.replaceAll("_", " ")],
  ];

  return <main className="vehicle-page">
    <header className="header"><Link className="logo" href={`/${locale}`}><b>Q</b> QHI<span>AUTO</span></Link><Link className="contact-top" href={`/${locale}`}>{t.back}</Link></header>
    <section className="vehicle-hero wrap">
      <div className="vehicle-gallery">
        {car.images.length > 0 ? car.images.map((image, index) => <img key={`${image}-${index}`} src={image} alt={`${title} ${index + 1}`} referrerPolicy="no-referrer"/>) : <div className="vehicle-image-placeholder">QHI AUTO / {car.year}</div>}
      </div>
      <div className="vehicle-summary"><div className="eyebrow dark">{car.brand} · {car.year}</div><h1>{title}</h1>{car.trim && <p className="vehicle-trim">{car.trim}</p>}<p className="vehicle-price">{money} <small>CNY</small></p><Link className="button" href="#vehicle-contact">{t.contact} ↗</Link></div>
    </section>
    <section className="vehicle-information wrap">
      <div><div className="eyebrow dark">QHI AUTO / 01</div><h2>{t.specs}</h2><dl>{facts.map(([label, value]) => <div key={label}><dt>{label}</dt><dd>{value}</dd></div>)}</dl></div>
      {car.localized_description && <article><div className="eyebrow dark">QHI AUTO / 02</div><h2>{t.description}</h2><p>{car.localized_description}</p></article>}
    </section>
    <section id="vehicle-contact" className="contact wrap"><div><div className="eyebrow dark">QHI AUTO / 03</div><h2>{t.contact}</h2></div><ContactTools locale={locale}/></section>
    <footer><Link className="logo" href={`/${locale}`}><b>Q</b> QHI<span>AUTO</span></Link></footer>
  </main>;
}
