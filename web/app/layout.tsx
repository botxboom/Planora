import type { Metadata } from "next";
import { Plus_Jakarta_Sans } from "next/font/google";
import "./globals.css";

const plusJakarta = Plus_Jakarta_Sans({
  subsets: ["latin"],
  variable: "--font-plus-jakarta",
  display: "swap",
});

export const metadata: Metadata = {
  title: "Planora — Smart trip planning",
  description: "Discover curated itineraries tailored to your budget and style.",
};

export default function RootLayout({
  children,
}: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en" className={`${plusJakarta.variable}`}>
      <body className={`${plusJakarta.className} min-h-screen bg-brand-cream antialiased`}>
        {children}
      </body>
    </html>
  );
}
