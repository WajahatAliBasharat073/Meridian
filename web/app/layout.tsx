import type { Metadata } from "next";
import { IBM_Plex_Mono, Manrope } from "next/font/google";
import { QueryProvider } from "@/providers/QueryProvider";
import "./globals.css";

const manrope = Manrope({
  variable: "--font-manrope",
  subsets: ["latin"],
  display: "swap",
});

const plexMono = IBM_Plex_Mono({
  variable: "--font-plex-mono",
  subsets: ["latin"],
  weight: ["400", "500"],
  display: "swap",
});

export const metadata: Metadata = {
  title: "Meridian",
  description: "What do I do right now?",
};

export default function RootLayout({ children }: LayoutProps<"/">) {
  return (
    <html
      lang="en"
      data-theme="dark"
      className={`${manrope.variable} ${plexMono.variable} h-full`}
      suppressHydrationWarning
    >
      {/* Some browser extensions (password managers, form-fillers) tag
          <body> with their own attribute before React hydrates, which
          React then reports as a mismatch — harmless, not a real bug. */}
      <body className="min-h-full" suppressHydrationWarning>
        <QueryProvider>{children}</QueryProvider>
      </body>
    </html>
  );
}
