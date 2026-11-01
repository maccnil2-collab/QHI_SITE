import { notFound } from "next/navigation";
import { AccountPanel } from "@/components/account-panel";
import { locales, type Locale } from "@/lib/i18n";
export default async function AccountPage({params,searchParams}:{params:Promise<{lang:string}>;searchParams:Promise<{car?:string}>}) {
 const {lang}=await params; const {car}=await searchParams;
 if(!locales.includes(lang as Locale)) notFound();
 return <AccountPanel locale={lang as Locale} initialCarId={car??""}/>;
}
