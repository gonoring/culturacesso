import type { Metadata, Viewport } from "next";
import { Analytics } from "@vercel/analytics/next";
import "./globals.css";

export const metadata: Metadata = {
  title: "CulturaAcesso — Editais culturais para o seu projeto",
  description:
    "Descubra quais editais culturais do Espírito Santo são compatíveis com o seu projeto. Gratuito e sem cadastro.",
  manifest: "/manifest.json",
};

export const viewport: Viewport = {
  themeColor: "#0f172a",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="pt-BR">
      <head>
        <meta name="viewport" content="width=device-width, initial-scale=1" />
        <link rel="manifest" href="/manifest.json" />
      </head>
      <body className="bg-slate-900 text-white antialiased">
        {children}
        <Analytics />
      </body>
    </html>
  );
}
