import type { Metadata } from "next";

import { CopilotKit } from "@copilotkit/react-core";
import "./globals.css";
import "@copilotkit/react-ui/styles.css";

export const metadata: Metadata = {
  title: "MAF + CopilotKit Demo",
  description: "Microsoft Agent Framework with CopilotKit UI",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className={"antialiased"}>
        <CopilotKit 
          runtimeUrl="/api/copilotkit"
          agent="weather"
        >
          {children}
        </CopilotKit>
      </body>
    </html>
  );
}
