import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "LandShield AI — Flagship Land Title Intelligence & Due Diligence",
  description: "Bank-grade autonomous property legal verification, deed OCR intelligence, and boundary risk detection.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body className="min-h-screen antialiased bg-slate-50 dark:bg-[#07090e] text-slate-900 dark:text-slate-100 selection:bg-blue-600 selection:text-white transition-colors duration-200">
        {children}
      </body>
    </html>
  );
}
