import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "ChatCommerce — WhatsApp Commerce Automation for Micro-Sellers",
  description:
    "Automate WhatsApp sales, recover abandoned carts, and stay compliant. Built for micro-sellers who sell via WhatsApp.",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body className="antialiased bg-white text-gray-900">{children}</body>
    </html>
  );
}
