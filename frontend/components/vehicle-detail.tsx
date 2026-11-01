"use client";

import Link from "next/link";
import Image from "next/image";
import { useEffect, useState } from "react";
import { ContactTools } from "@/components/contact-tools";
import { fetchCar, type Car } from "@/lib/api";
import type { Locale } from "@/lib/i18n";

const copy = {
  ru: { back:"Назад в каталог", loading:"Загружаем автомобиль…", error:"Не удалось загрузить автомобиль.", description:"Описание", specs:"Характеристики", year:"Год выпуска", price:"Цена в Китае", category:"Категория", engine:"Тип двигателя", volume:"Объём двигателя", range:"Запас хода / расход", battery:"Батарея", power:"Мощность", drive:"Привод", transmission:"Коробка передач", mileage:"Пробег", color:"Цвет", equipment:"Комплектация", availability:"Статус каталога", contact:"Рассчитать стоимость", demo:"ДЕМО · данные для примера" },
  tg: { back:"Бозгашт ба феҳрист", loading:"Мошин бор шуда истодааст…", error:"Мошин бор карда нашуд.", description:"Тавсиф", specs:"Хусусиятҳо", year:"Соли истеҳсол", price:"Нарх дар Чин", category:"Категория", engine:"Навъи муҳаррик", volume:"Ҳаҷми муҳаррик", range:"Масофа / истеъмол", battery:"Батарея", power:"Қувва", drive:"Привод", transmission:"Қуттии интиқол", mileage:"Ҳаракат", color:"Ранг", equipment:"Маҷмӯа", availability:"Ҳолати феҳрист", contact:"Ҳисоби арзиш", demo:"НАМУНА · маълумоти тасвирӣ" },
  en: { back:"Back to catalog", loading:"Loading vehicle…", error:"Could not load this vehicle.", description:"Description", specs:"Specifications", year:"Model year", price:"Price in China", category:"Category", engine:"Engine type", volume:"Engine displacement", range:"Range / fuel consumption", battery:"Battery", power:"Power", drive:"Drivetrain", transmission:"Transmission", mileage:"Mileage", color:"Exterior color", equipment:"Equipment", availability:"Catalog status", contact:"Estimate cost", demo:"DEMO · illustrative data" },
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
      .catch((error: unknown) => { if (!(error instanceof DOMException && error.name === "AbortError")) setState("error"); });
    return () => controller.abort();
  }, [locale, slug]);

  if (state === "loading") return <main className="vehicle-state" role="status">{t.loading}</main>;
  if (state === "error" || !car) return <main className="vehicle-state" role="alert"><p>{t.error}</p><Link className="button" href={`/${locale}`}>{t.back}</Link></main>;

  const title = car.localized_title ?? `${car.brand} ${car.model}`;
  const money = number(locale).format(Number(car.price_cny));
  const facts = [
    [t.year, String(car.year)], [t.category, car.category ?? "—"], [t.price, `${money} CNY`],
    [t.engine, car.engine_type ?? "—"], [t.volume, car.engine_cc ? `${number(locale).format(car.engine_cc)} cm³` : "—"],
    [t.range, car.range_km ? `${number(locale).format(car.range_km)} km` : car.fuel_consumption_l_100km ? `${car.fuel_consumption_l_100km} L/100 km` : "—"],
    [t.battery, car.battery_kwh ? `${car.battery_kwh} kWh` : "—"], [t.power, car.power_kw ? `${car.power_kw} kW` : "—"],
    [t.drive, car.drivetrain ?? "—"], [t.transmission, car.transmission ?? "—"],
    [t.mileage, car.mileage_km !== null ? `${number(locale).format(car.mileage_km)} km` : "—"],
    [t.color, car.exterior_color ?? "—"], [t.equipment, car.equipment ?? "—"], [t.availability, car.availability.replaceAll("_", " ")],
  ];

  return <main className="vehicle-page">
    <header className="header"><Link className="logo" href={`/${locale}`} aria-label="QHI AUTO"><b>Q</b> QHI<span>AUTO</span></Link><Link className="contact-top" href={`/${locale}`}>{t.back}</Link></header>
    <section className="vehicle-hero wrap">
      <div className="vehicle-gallery">
        {car.images.length > 0 ? car.images.map((image, index) => <Image key={`${image}-${index}`} src={image} alt={`${title} ${index + 1}`} width={1200} height={900} unoptimized referrerPolicy="no-referrer" />) : <div className="vehicle-image-placeholder">QHI AUTO / {car.year}</div>}
      </div>
      <div className="vehicle-summary"><div className="eyebrow dark">{car.brand} · {car.year}</div>{car.is_demo && <span className="demo-label">{t.demo}</span>}<h1>{title}</h1>{car.trim && <p className="vehicle-trim">{car.trim}</p>}<p className="vehicle-price">{money} <small>CNY</small></p><Link className="button" href="#vehicle-contact">{t.contact} ↗</Link></div>
    </section>
    <section className="vehicle-information wrap">
      <div><div className="eyebrow dark">QHI AUTO / 01</div><h2>{t.specs}</h2><dl>{facts.map(([label, value]) => <div key={label}><dt>{label}</dt><dd>{value}</dd></div>)}</dl></div>
      {car.localized_description && <article><div className="eyebrow dark">QHI AUTO / 02</div><h2>{t.description}</h2><p>{car.localized_description}</p></article>}
    </section>
    <section id="vehicle-contact" className="contact wrap"><div><div className="eyebrow dark">QHI AUTO / 03</div><h2>{t.contact}</h2></div><ContactTools locale={locale}/></section>
    <footer><Link className="logo" href={`/${locale}`} aria-label="QHI AUTO"><b>Q</b> QHI<span>AUTO</span></Link></footer>
  </main>;
}
