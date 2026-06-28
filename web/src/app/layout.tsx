import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import Link from "next/link";
import "./globals.css";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "Pays",
  description: "Personal Finance & Asset Management",
};

const navItems = [
  { href: "/", label: "Dashboard", icon: "~" },
  { href: "/news", label: "News", icon: "*" },
  { href: "/assets", label: "Assets", icon: "$" },
  { href: "/settings", label: "Settings", icon: "@" },
];

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html
      lang="en"
      className={`${geistSans.variable} ${geistMono.variable} h-full antialiased`}
    >
      <body className="min-h-full flex">
        <nav className="w-56 shrink-0 border-r border-[var(--card-border)] flex flex-col p-4 gap-1">
          <Link href="/" className="text-xl font-bold mb-6 px-3">
            Pays
          </Link>
          {navItems.map((item) => (
            <Link
              key={item.href}
              href={item.href}
              className="flex items-center gap-3 px-3 py-2 rounded-lg hover:bg-[var(--card)] transition-colors text-sm font-medium text-[var(--muted)] hover:text-[var(--foreground)]"
            >
              <span className="font-mono w-5 text-center text-[var(--accent)]">
                {item.icon}
              </span>
              {item.label}
            </Link>
          ))}
        </nav>
        <main className="flex-1 p-8 overflow-auto">{children}</main>
      </body>
    </html>
  );
}
