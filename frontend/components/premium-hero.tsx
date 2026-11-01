import Image from "next/image";
import Link from "next/link";
import { getMessages, type Locale } from "@/lib/i18n";

const copy = {
  ru: { label: "АВТОМОБИЛИ С ХАРАКТЕРОМ", caption: "РЕДАКЦИОННОЕ ФОТО · НЕ ОБЪЯВЛЕНИЕ", scroll: "Исследовать каталог", coordinates: "ДУШАНБЕ · ТАДЖИКИСТАН", photo: "Фото: Wiaskara · CC BY-SA 4.0" },
  tg: { label: "МОШИНАҲО БО ХУСУСИЯТ", caption: "АКСИ ТАҲРИРӢ · ЭЪЛОН НЕСТ", scroll: "Омӯхтани каталог", coordinates: "ДУШАНБЕ · ТОҶИКИСТОН", photo: "Акс: Wiaskara · CC BY-SA 4.0" },
  en: { label: "MOBILITY WITH CHARACTER", caption: "EDITORIAL IMAGE · NOT A LISTING", scroll: "Explore the collection", coordinates: "DUSHANBE · TAJIKISTAN", photo: "Photo: Wiaskara · CC BY-SA 4.0" },
} as const;

const source = "https://commons.wikimedia.org/wiki/File:SUV_car.jpg";
const license = "https://creativecommons.org/licenses/by-sa/4.0/";

export function PremiumHero({ locale }: { locale: Locale }) {
  const t = getMessages(locale);
  const c = copy[locale];
  return <section className="premium-hero" aria-labelledby="hero-title">
    <Image className="premium-hero__photo" src="https://upload.wikimedia.org/wikipedia/commons/thumb/3/35/SUV_car.jpg/1280px-SUV_car.jpg" alt="" fill priority unoptimized sizes="100vw" referrerPolicy="no-referrer" />
    <div className="premium-hero__veil" aria-hidden="true"/><div className="premium-hero__grain" aria-hidden="true"/>
    <div className="premium-hero__content"><div className="premium-hero__brand"><span className="premium-hero__mark"><Image src="/images/qhi-chameleon.webp" alt="" width={128} height={96} priority/></span><span className="premium-hero__auto">QHI <b>AUTO</b></span><i/></div>
      <div className="premium-hero__copy"><p className="premium-hero__eyebrow"><span/> {c.label}</p><h1 id="hero-title">{t.headline.split("\n").map((line,index)=><span key={`${index}-${line}`}>{line}</span>)}</h1><p className="premium-hero__intro">{t.intro}</p><div className="premium-hero__actions"><Link className="premium-hero__cta" href="#catalog"><span>{t.browse}</span><b aria-hidden="true">↗</b></Link><Link className="premium-hero__secondary" href="#process">{t.process}<span aria-hidden="true">↗</span></Link></div></div>
      <div className="premium-hero__foot"><span>{c.coordinates}</span><span className="premium-hero__index">QHI / 01</span></div>
    </div>
    <div className="premium-hero__photo-note"><span>{c.caption}</span><a href={source} target="_blank" rel="noreferrer">{c.photo}</a><a href={license} target="_blank" rel="noreferrer">CC BY-SA 4.0 ↗</a></div>
    <Link className="premium-hero__scroll" href="#catalog" aria-label={c.scroll}><span>{c.scroll}</span><i/></Link>
  </section>;
}
