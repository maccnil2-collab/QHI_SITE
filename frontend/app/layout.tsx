import type { Metadata } from "next";
import "./globals.css";
export const metadata: Metadata = { title: "QHI AUTO — Electric vehicles from China", description: "EV selection and delivery coordination to Dushanbe." };
export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) { return <html><body>{children}</body></html>; }
