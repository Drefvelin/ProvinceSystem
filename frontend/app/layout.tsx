import type { Metadata } from "next";
import { Fraunces, Source_Sans_3 } from "next/font/google";
import SiteHeader from "./components/shell/SiteHeader";
import "./internal/globals.css";

const fraunces = Fraunces({
  variable: "--font-fraunces",
  subsets: ["latin"],
  display: "swap",
});

const sourceSans = Source_Sans_3({
  variable: "--font-source-sans",
  subsets: ["latin"],
  display: "swap",
});

export const metadata: Metadata = {
  title: "TFMC",
  description: "Maps, skins, and server tools for TFMC.",
  icons: {
    icon: "/server-icon.png",
  },
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body
        className={`${fraunces.variable} ${sourceSans.variable} min-h-dvh antialiased`}
      >
        <SiteHeader />
        {children}
      </body>
    </html>
  );
}
