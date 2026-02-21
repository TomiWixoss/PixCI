import type { Metadata } from "next";
import { Space_Mono } from "next/font/google";
import "./globals.css";
import { QueryProvider } from "@/components/providers/QueryProvider";
import { ToastProvider } from "@/components/providers/ToastProvider";
import { ThemeProvider } from "next-themes";

const pixelFont = Space_Mono({ 
  weight: ["400", "700"], 
  subsets: ["latin", "vietnamese"],
  variable: "--font-pixel"
});

export const metadata: Metadata = {
  title: "PixCI - AI Pixel Studio",
  description: "Trình chỉnh sửa Pixel Art bằng AI chuẩn Awwwards",
  viewport: {
    width: 'device-width',
    initialScale: 1,
    maximumScale: 1,
  },
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="vi" suppressHydrationWarning>
      <body className={`${pixelFont.variable} font-pixel antialiased overflow-hidden selection:bg-black selection:text-[#00ff00] dark:selection:bg-[#00ff00] dark:selection:text-black`}>
        <ThemeProvider attribute="class" defaultTheme="dark" enableSystem={false}>
          <QueryProvider>
            {children}
            <ToastProvider />
          </QueryProvider>
        </ThemeProvider>
      </body>
    </html>
  );
}
