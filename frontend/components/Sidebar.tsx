'use client'

import Link from 'next/link'
import { usePathname } from 'next/navigation'
import { ShieldAlert, MessageCircleWarning, ScanLine, Network, ShieldCheck } from 'lucide-react'

const NAV_ITEMS = [
  { href: '/', label: 'Overview', icon: ShieldCheck },
  { href: '/chat', label: 'Citizen Fraud Shield', icon: MessageCircleWarning },
  { href: '/scam-check', label: 'Scam Session Detector', icon: ShieldAlert },
  { href: '/currency-check', label: 'Currency Verification', icon: ScanLine },
  { href: '/fraud-network', label: 'Fraud Network Intelligence', icon: Network },
]

export default function Sidebar() {
  const pathname = usePathname()

  return (
    <aside className="w-72 shrink-0 bg-navy text-cream min-h-screen flex flex-col">
      <div className="px-6 py-7 border-b border-white/10">
        <div className="flex items-center gap-2.5">
          <div className="w-9 h-9 rounded-sm bg-brass flex items-center justify-center">
            <ShieldCheck size={20} className="text-navy" strokeWidth={2.5} />
          </div>
          <div>
            <p className="font-display text-lg leading-none tracking-tight">RakshakAI</p>
            <p className="text-[11px] text-cream/50 mt-1 tracking-wide uppercase">Public Safety Intelligence</p>
          </div>
        </div>
      </div>

      <nav className="flex-1 px-3 py-6 space-y-1">
        {NAV_ITEMS.map(({ href, label, icon: Icon }) => {
          const active = pathname === href
          return (
            <Link
              key={href}
              href={href}
              className={`flex items-center gap-3 px-3 py-2.5 rounded-sm text-sm transition-colors ${
                active
                  ? 'bg-white/10 text-cream border-l-2 border-brass'
                  : 'text-cream/60 hover:text-cream hover:bg-white/5 border-l-2 border-transparent'
              }`}
            >
              <Icon size={17} strokeWidth={active ? 2.2 : 1.8} />
              <span>{label}</span>
            </Link>
          )
        })}
      </nav>

      <div className="px-6 py-5 border-t border-white/10">
        <p className="text-[11px] text-cream/40 leading-relaxed">
          If you have lost money to fraud, report immediately at{' '}
          <span className="text-brass">cybercrime.gov.in</span> or call{' '}
          <span className="text-brass">1930</span>.
        </p>
      </div>
    </aside>
  )
}
