import type { Metadata } from "next";
import "./globals.css";
import { AuthProvider } from "@/components/auth-provider";
import { BrandSplash } from "@/components/brand-splash";
export const metadata: Metadata = { title: "QHI AUTO — Electric vehicles from China", description: "EV selection and delivery coordination to Dushanbe." };
export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) { return <html lang="ru"><body><BrandSplash/><AuthProvider>{children}</AuthProvider></body></html>; }
