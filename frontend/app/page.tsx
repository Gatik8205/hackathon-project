import Link from 'next/link'
import { MessageCircleWarning, ShieldAlert, ScanLine, Network, ArrowRight } from 'lucide-react'
import { PageHeader, Card } from '@/components/ui'

const FEATURES = [
  {
    href: '/chat',
    icon: MessageCircleWarning,
    title: 'Citizen Fraud Shield',
    description:
      'Describe a suspicious call or message and get an instant risk assessment with clear next steps.',
  },
  {
    href: '/scam-check',
    icon: ShieldAlert,
    title: 'Scam Session Detector',
    description:
      'Classify an active or recorded call transcript for digital arrest and impersonation scam patterns.',
  },
  {
    href: '/currency-check',
    icon: ScanLine,
    title: 'Currency Verification',
    description:
      'Upload a photo of a currency note for a preliminary authenticity check.',
  },
  {
    href: '/fraud-network',
    icon: Network,
    title: 'Fraud Network Intelligence',
    description:
      'Visualize how fraud reports connect through shared phone numbers, devices, and accounts.',
  },
]

export default function HomePage() {
  return (
    <div>
      <PageHeader
        eyebrow="ET AI Hackathon 2026 · Public Safety"
        title="Digital Public Safety Intelligence"
        description="A unified platform for detecting digital arrest scams, counterfeit currency, and organised fraud networks — shifting law enforcement and citizens from reactive complaint handling to proactive threat detection."
      />

      <div className="px-10 py-10 grid grid-cols-1 md:grid-cols-2 gap-5 max-w-5xl">
        {FEATURES.map(({ href, icon: Icon, title, description }) => (
          <Link key={href} href={href}>
            <Card className="h-full hover:border-brass transition-colors group cursor-pointer">
              <div className="w-10 h-10 rounded-sm bg-navy/5 flex items-center justify-center mb-4">
                <Icon size={20} className="text-navy" strokeWidth={1.8} />
              </div>
              <h3 className="font-display text-lg text-navy mb-2">{title}</h3>
              <p className="text-sm text-navy/60 leading-relaxed mb-4">{description}</p>
              <span className="inline-flex items-center gap-1.5 text-sm font-medium text-brass-dark group-hover:gap-2.5 transition-all">
                Open <ArrowRight size={14} />
              </span>
            </Card>
          </Link>
        ))}
      </div>
    </div>
  )
}
