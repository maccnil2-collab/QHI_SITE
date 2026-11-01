import { notFound } from "next/navigation";
import { VehicleDetail } from "@/components/vehicle-detail";
import { locales, type Locale } from "@/lib/i18n";

export default async function VehiclePage({ params }: { params: Promise<{ lang: string; slug: string }> }) {
  const { lang, slug } = await params;
  if (!locales.includes(lang as Locale)) notFound();
  return <VehicleDetail locale={lang as Locale} slug={slug}/>;
}
