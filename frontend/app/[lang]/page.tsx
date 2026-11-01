import { notFound } from "next/navigation";
import { CatalogPage } from "@/components/catalog-page";
import { locales, type Locale } from "@/lib/i18n";
export function generateStaticParams() { return locales.map((lang) => ({ lang })); }
export default async function LocalizedHome({ params }: { params: Promise<{ lang: string }> }) {
  const { lang } = await params;
  if (!locales.includes(lang as Locale)) notFound();
  return <CatalogPage locale={lang as Locale} />;
}
