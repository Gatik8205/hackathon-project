import type { Metadata } from 'next'
import { Fraunces, Inter } from 'next/font/google'
import Sidebar from '@/components/Sidebar'
import './globals.css'

const fraunces = Fraunces({
  subsets: ['latin'],
  variable: '--font-fraunces',
  weight: ['400', '500', '600'],
})

const inter = Inter({
  subsets: ['latin'],
  variable: '--font-inter',
})

export const metadata: Metadata = {
  title: 'RakshakAI — Public Safety Intelligence',
  description:
    'AI-powered platform for detecting digital arrest scams, counterfeit currency, and fraud networks.',
}

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" className={`${fraunces.variable} ${inter.variable}`}>
      <body className="font-body flex min-h-screen">
        <Sidebar />
        <main className="flex-1 bg-cream min-h-screen">{children}</main>
      </body>
    </html>
  )
}
