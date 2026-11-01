"use client";

import Link from "next/link";
import Image from "next/image";
import { useEffect, useState } from "react";
import { ContactTools } from "@/components/contact-tools";
import { fetchCar, type Car } from "@/lib/api";
import type { Locale } from "@/lib/i18n";

const copy = {
  ru: { back:"\u041d\u0430\u0437\u0430\u0434 \u0432 \u043a\u0430\u0442\u0430\u043b\u043e\u0433", loading:"\u0417\u0430\u0433\u0440\u0443\u0436\u0430\u0435\u043c \u0430\u0432\u0442\u043e\u043c\u043e\u0431\u0438\u043b\u044c\u2026", error:"\u041d\u0435 \u0443\u0434\u0430\u043b\u043e\u0441\u044c \u0437\u0430\u0433\u0440\u0443\u0437\u0438\u0442\u044c \u0430\u0432\u0442\u043e\u043c\u043e\u0431\u0438\u043b\u044c.", description:"\u041e\u043f\u0438\u0441\u0430\u043d\u0438\u0435", specs:"\u0425\u0430\u0440\u0430\u043a\u0442\u0435\u0440\u0438\u0441\u0442\u0438\u043a\u0438", year:"\u0413\u043e\u0434 \u0432\u044b\u043f\u0443\u0441\u043a\u0430", price:"\u0426\u0435\u043d\u0430 \u0432 \u041a\u0438\u0442\u0430\u0435", category:"\u041a\u0430\u0442\u0435\u0433\u043e\u0440\u0438\u044f", engine:"\u0422\u0438\u043f \u0434\u0432\u0438\u0433\u0430\u0442\u0435\u043b\u044f", volume:"\u041e\u0431\u044a\u0451\u043c \u0434\u0432\u0438\u0433\u0430\u0442\u0435\u043b\u044f", range:"\u0417\u0430\u043f\u0430\u0441 \u0445\u043e\u0434\u0430 / \u0440\u0430\u0441\u0445\u043e\u0434", battery:"\u0411\u0430\u0442\u0430\u0440\u0435\u044f", power:"\u041c\u043e\u0449\u043d\u043e\u0441\u0442\u044c", drive:"\u041f\u0440\u0438\u0432\u043e\u0434", transmission:"\u041a\u043e\u0440\u043e\u0431\u043a\u0430 \u043f\u0435\u0440\u0435\u0434\u0430\u0447", mileage:"\u041f\u0440\u043e\u0431\u0435\u0433", color:"\u0426\u0432\u0435\u0442 \u043a\u0443\u0437\u043e\u0432\u0430", equipment:"\u041a\u043e\u043c\u043f\u043b\u0435\u043a\u0442\u0430\u0446\u0438\u044f", availability:"\u0421\u0442\u0430\u0442\u0443\u0441 \u043a\u0430\u0442\u0430\u043b\u043e\u0433\u0430", contact:"\u0420\u0430\u0441\u0441\u0447\u0438\u0442\u0430\u0442\u044c \u0441\u0442\u043e\u0438\u043c\u043e\u0441\u0442\u044c", demo:"\u0414\u0415\u041c\u041e \u00b7 \u043f\u0440\u0438\u043c\u0435\u0440 \u0434\u0430\u043d\u043d\u044b\u0445", image:"\u0424\u043e\u0442\u043e \u0430\u0432\u0442\u043e\u043c\u043e\u0431\u0438\u043b\u044f", close:"\u0417\u0430\u043a\u0440\u044b\u0442\u044c \u043f\u0440\u043e\u0441\u043c\u043e\u0442\u0440", previous:"\u041f\u0440\u0435\u0434\u044b\u0434\u0443\u0449\u0435\u0435 \u0444\u043e\u0442\u043e", next:"\u0421\u043b\u0435\u0434\u0443\u044e\u0449\u0435\u0435 \u0444\u043e\u0442\u043e" },
  tg: { back:"\u0411\u043e\u0437\u0433\u0430\u0448\u0442 \u0431\u0430 \u0444\u0435\u04b3\u0440\u0438\u0441\u0442", loading:"\u041c\u043e\u0448\u0438\u043d \u0431\u043e\u0440 \u0448\u0443\u0434\u0430 \u0438\u0441\u0442\u043e\u0434\u0430\u0430\u0441\u0442\u2026", error:"\u041c\u043e\u0448\u0438\u043d \u0431\u043e\u0440 \u043a\u0430\u0440\u0434\u0430 \u043d\u0430\u0448\u0443\u0434.", description:"\u0422\u0430\u0432\u0441\u0438\u0444", specs:"\u0425\u0443\u0441\u0443\u0441\u0438\u044f\u0442\u04b3\u043e", year:"\u0421\u043e\u043b\u0438 \u0438\u0441\u0442\u0435\u04b3\u0441\u043e\u043b", price:"\u041d\u0430\u0440\u0445 \u0434\u0430\u0440 \u0427\u0438\u043d", category:"\u041a\u0430\u0442\u0435\u0433\u043e\u0440\u0438\u044f", engine:"\u041d\u0430\u0432\u044a\u0438 \u043c\u0443\u04b3\u0430\u0440\u0440\u0438\u043a", volume:"\u04b2\u0430\u04b7\u043c\u0438 \u043c\u0443\u04b3\u0430\u0440\u0440\u0438\u043a", range:"\u041c\u0430\u0441\u043e\u0444\u0430 / \u0438\u0441\u0442\u0435\u044a\u043c\u043e\u043b", battery:"\u0411\u0430\u0442\u0430\u0440\u0435\u044f", power:"\u049a\u0443\u0432\u0432\u0430", drive:"\u0414\u0430\u0441\u0433\u043e\u04b3", transmission:"\u049a\u0443\u0442\u0442\u0438\u0438 \u0438\u043d\u0442\u0438\u049b\u043e\u043b", mileage:"\u041c\u0430\u0441\u043e\u0444\u0430\u0438 \u0442\u0430\u0439\u0448\u0443\u0434\u0430", color:"\u0420\u0430\u043d\u0433", equipment:"\u041c\u0430\u04b7\u043c\u04ef\u0430", availability:"\u04b2\u043e\u043b\u0430\u0442\u0438 \u0444\u0435\u04b3\u0440\u0438\u0441\u0442", contact:"\u04b2\u0438\u0441\u043e\u0431\u0438 \u0430\u0440\u0437\u0438\u0448", demo:"\u041d\u0410\u041c\u0423\u041d\u0410 \u00b7 \u043c\u0430\u044a\u043b\u0443\u043c\u043e\u0442\u0438 \u0442\u0430\u0441\u0432\u0438\u0440\u04e3", image:"\u0410\u043a\u0441\u0438 \u043c\u043e\u0448\u0438\u043d", close:"\u041f\u04ef\u0448\u0438\u0434\u0430\u043d", previous:"\u0410\u043a\u0441\u0438 \u049b\u0430\u0431\u043b\u04e3", next:"\u0410\u043a\u0441\u0438 \u043d\u0430\u0432\u0431\u0430\u0442\u04e3" },
  en: { back:"Back to catalog", loading:"Loading vehicle\u2026", error:"Could not load this vehicle.", description:"Description", specs:"Specifications", year:"Model year", price:"Price in China", category:"Category", engine:"Engine type", volume:"Engine displacement", range:"Range / fuel consumption", battery:"Battery", power:"Power", drive:"Drivetrain", transmission:"Transmission", mileage:"Mileage", color:"Exterior color", equipment:"Equipment", availability:"Catalog status", contact:"Estimate cost", demo:"DEMO \u00b7 illustrative data", image:"Vehicle photo", close:"Close viewer", previous:"Previous photo", next:"Next photo" },
} satisfies Record<Locale, Record<string, string>>;

const detailCopy = {
  ru: { fuel:"Топливо", torque:"Крутящий момент", acceleration:"0–100 км/ч", maxSpeed:"Макс. скорость", seats:"Мест", doors:"Дверей", dimensions:"Габариты", advantages:"Преимущества", specSource:"Источник характеристик", photoSource:"Источник фото", priceNote:"Примечание к цене", priceSource:"Источник цены" },
  tg: { fuel:"Сӯзишворӣ", torque:"Моменти чархонӣ", acceleration:"0–100 км/с", maxSpeed:"Суръати акс.", seats:"Ҷой", doors:"Дар", dimensions:"Андозаҳо", advantages:"Бартариҳо", specSource:"Манбаи хусусиятҳо", photoSource:"Манбаи акс", priceNote:"Эзоҳи нарх", priceSource:"Манбаи нарх" },
  en: { fuel:"Fuel type", torque:"Torque", acceleration:"0–100 km/h", maxSpeed:"Top speed", seats:"Seats", doors:"Doors", dimensions:"Dimensions", advantages:"Key advantages", specSource:"Specification source", photoSource:"Photo source", priceNote:"Price note", priceSource:"Price source" },
} satisfies Record<Locale, Record<string, string>>;

const number = (locale: Locale) => new Intl.NumberFormat(locale === "en" ? "en-US" : locale === "tg" ? "tg-TJ" : "ru-RU", { maximumFractionDigits: 0 });

export function VehicleDetail({ locale, slug }: { locale: Locale; slug: string }) {
  const t = copy[locale];
  const d = detailCopy[locale];
  const [car, setCar] = useState<Car | null>(null);
  const [state, setState] = useState<"loading" | "ready" | "error">("loading");
  const [activeImage, setActiveImage] = useState<number | null>(null);

  useEffect(() => {
    const controller = new AbortController();
    setState("loading");
    fetchCar(slug, locale, controller.signal)
      .then((vehicle) => { setCar(vehicle); setState("ready"); })
      .catch((error: unknown) => { if (!(error instanceof DOMException && error.name === "AbortError")) setState("error"); });
    return () => controller.abort();
  }, [locale, slug]);

  useEffect(() => {
    if (activeImage === null || !car) return;
    const key = (event: KeyboardEvent) => {
      if (event.key === "Escape") setActiveImage(null);
      if (event.key === "ArrowRight") setActiveImage((activeImage + 1) % car.images.length);
      if (event.key === "ArrowLeft") setActiveImage((activeImage - 1 + car.images.length) % car.images.length);
    };
    window.addEventListener("keydown", key);
    document.body.style.overflow = "hidden";
    return () => { window.removeEventListener("keydown", key); document.body.style.overflow = ""; };
  }, [activeImage, car]);

  if (state === "loading") return <main className="vehicle-state" role="status">{t.loading}</main>;
  if (state === "error" || !car) return <main className="vehicle-state" role="alert"><p>{t.error}</p><Link className="button" href={`/${locale}`}>{t.back}</Link></main>;

  const title = car.localized_title ?? `${car.brand} ${car.model}`;
  const money = number(locale).format(Number(car.price_cny));
  const dash = "—";
  const facts = [
    [t.year, String(car.year)], [t.category, car.category ?? dash], [t.price, `${money} CNY`],
    [t.engine, car.engine_type ?? dash], [d.fuel, car.fuel_type ?? dash], [t.volume, car.engine_cc ? `${number(locale).format(car.engine_cc)} cm³` : dash],
    [d.torque, car.torque_nm ? `${number(locale).format(car.torque_nm)} Nm` : dash], [d.acceleration, car.acceleration_0_100_s ? `${car.acceleration_0_100_s} s` : dash],
    [d.maxSpeed, car.max_speed_kmh ? `${number(locale).format(car.max_speed_kmh)} km/h` : dash], [d.seats, car.seats ? String(car.seats) : dash], [d.doors, car.doors ? String(car.doors) : dash],
    [t.range, car.range_km ? `${number(locale).format(car.range_km)} km` : car.fuel_consumption_l_100km ? `${car.fuel_consumption_l_100km} L/100 km` : dash],
    [t.battery, car.battery_kwh ? `${car.battery_kwh} kWh` : dash], [t.power, car.power_kw ? `${car.power_kw} kW` : dash],
    [t.drive, car.drivetrain ?? dash], [t.transmission, car.transmission ?? dash],
    [t.mileage, car.mileage_km !== null ? `${number(locale).format(car.mileage_km)} km` : dash],
    [d.dimensions, car.length_mm && car.width_mm && car.height_mm ? `${car.length_mm} × ${car.width_mm} × ${car.height_mm} mm${car.wheelbase_mm ? ` · ${car.wheelbase_mm} mm WB` : ""}` : dash],
    [t.color, car.exterior_color ?? dash], [t.equipment, car.equipment ?? dash], [t.availability, car.availability.replaceAll("_", " ")],
  ];
  const step = (direction: number) => setActiveImage(index => index === null ? 0 : (index + direction + car.images.length) % car.images.length);

  return <main className="vehicle-page">
    <header className="header"><Link className="logo" href={`/${locale}`} aria-label="QHI AUTO"><b>Q</b> QHI<span>AUTO</span></Link><Link className="contact-top" href={`/${locale}`}>{t.back}</Link></header>
    <section className="vehicle-hero wrap">
      <div className="vehicle-gallery" aria-label={t.image}>
        {car.images.length > 0 ? car.images.map((image, index) => <button className="vehicle-gallery__item" key={`${image}-${index}`} type="button" onClick={() => setActiveImage(index)} aria-label={`${t.image} ${index + 1}`}><Image src={image} alt={car.image_details?.[index]?.alt ?? `${title} ${index + 1}`} width={1200} height={900} unoptimized referrerPolicy="no-referrer"/><span>{String(index + 1).padStart(2, "0")} / {String(car.images.length).padStart(2, "0")}</span></button>) : <div className="vehicle-image-placeholder">QHI AUTO / {car.year}</div>}
      </div>
      <div className="vehicle-summary"><div className="eyebrow dark">{car.brand} · {car.year}</div>{car.is_demo && <span className="demo-label">{t.demo}</span>}<h1>{title}</h1>{car.trim && <p className="vehicle-trim">{car.trim}</p>}<p className="vehicle-price">{money} <small>CNY</small></p>{car.price_usd&&<p className="vehicle-alt-price">{number(locale).format(Number(car.price_usd))} USD</p>}{car.price_tjs&&<p className="vehicle-alt-price">{number(locale).format(Number(car.price_tjs))} TJS</p>}{car.price_note&&<p className="vehicle-price-note">{car.price_note}</p>}<Link className="button" href="#vehicle-contact">{t.contact} ↗</Link></div>
    </section>
    <section className="vehicle-information wrap">
      <div><div className="eyebrow dark">QHI AUTO / 01</div><h2>{t.specs}</h2><dl>{facts.map(([label, value]) => <div key={label}><dt>{label}</dt><dd>{value}</dd></div>)}</dl></div>
      {(car.localized_description || car.advantages || car.specification_source || car.price_source) && <article><div className="eyebrow dark">QHI AUTO / 02</div><h2>{t.description}</h2>{car.localized_description&&<p>{car.localized_description}</p>}{car.advantages&&<p><b>{d.advantages}</b><br/>{car.advantages}</p>}{car.specification_source&&<p>{d.specSource}: <a href={car.specification_source} target="_blank" rel="noreferrer">{car.brand} / {car.model}</a></p>}{car.price_note&&<p>{d.priceNote}: {car.price_note}</p>}{car.price_source&&<p>{d.priceSource}: <a href={car.price_source} target="_blank" rel="noreferrer">{car.brand} / {car.model}</a></p>}</article>}
    </section>
    <section id="vehicle-contact" className="contact wrap"><div><div className="eyebrow dark">QHI AUTO / 03</div><h2>{t.contact}</h2></div><ContactTools locale={locale}/></section>
    <footer><Link className="logo" href={`/${locale}`} aria-label="QHI AUTO"><b>Q</b> QHI<span>AUTO</span></Link></footer>
    {activeImage !== null && <div className="vehicle-lightbox" role="dialog" aria-modal="true" aria-label={t.image} onClick={() => setActiveImage(null)}><button className="vehicle-lightbox__close" aria-label={t.close} onClick={() => setActiveImage(null)}>×</button><button className="vehicle-lightbox__prev" aria-label={t.previous} onClick={event => { event.stopPropagation(); step(-1); }}>‹</button><Image src={car.images[activeImage]} alt={car.image_details?.[activeImage]?.alt ?? `${title} ${activeImage + 1}`} width={1800} height={1200} unoptimized referrerPolicy="no-referrer" onClick={event => event.stopPropagation()}/>{car.image_details?.[activeImage]?.attribution&&<small className="vehicle-lightbox__credit">{car.image_details[activeImage].attribution} · {car.image_details[activeImage].license_name}{car.image_details[activeImage].source_url&&<> · <a href={car.image_details[activeImage].source_url} target="_blank" rel="noreferrer">{d.photoSource}</a></>}</small>}<button className="vehicle-lightbox__next" aria-label={t.next} onClick={event => { event.stopPropagation(); step(1); }}>›</button><span>{String(activeImage + 1).padStart(2, "0")} / {String(car.images.length).padStart(2, "0")}</span></div>}
  </main>;
}
