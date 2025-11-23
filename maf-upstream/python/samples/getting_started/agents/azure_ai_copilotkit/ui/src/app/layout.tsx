import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Azure AI Weather Agent - CopilotKit Demo",
  description: "Production-ready Azure AI agent with CopilotKit UI",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
