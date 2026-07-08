export function PageHeader({
  eyebrow,
  title,
  description,
}: {
  eyebrow: string
  title: string
  description: string
}) {
  return (
    <div className="border-b border-navy/10 px-10 py-8 bg-cream">
      <p className="text-xs tracking-[0.14em] uppercase text-brass-dark font-semibold mb-2">
        {eyebrow}
      </p>
      <h1 className="font-display text-3xl text-navy tracking-tight mb-2">{title}</h1>
      <p className="text-navy/60 max-w-2xl leading-relaxed">{description}</p>
    </div>
  )
}

export function Card({
  children,
  className = '',
}: {
  children: React.ReactNode
  className?: string
}) {
  return (
    <div className={`bg-white border border-navy/10 rounded-sm p-6 ${className}`}>
      {children}
    </div>
  )
}

const VERDICT_STYLES: Record<
  string,
  { bg: string; text: string; label: string }
> = {
  likely_scam: { bg: 'bg-alert', text: 'text-white', label: 'Likely Scam' },
  possibly_scam: { bg: 'bg-brass', text: 'text-navy', label: 'Possibly a Scam' },
  likely_safe: { bg: 'bg-navy-light', text: 'text-cream', label: 'Likely Safe' },
}

export function VerdictBadge({ verdict }: { verdict: string }) {
  const style = VERDICT_STYLES[verdict] ?? {
    bg: 'bg-navy/20',
    text: 'text-navy',
    label: verdict,
  }
  return (
    <span
      className={`inline-flex items-center px-3 py-1.5 rounded-sm text-sm font-semibold ${style.bg} ${style.text}`}
    >
      {style.label}
    </span>
  )
}

const PRIORITY_STYLES: Record<string, string> = {
  critical: 'bg-alert text-white',
  high: 'bg-brass text-navy',
  medium: 'bg-navy-light text-cream',
  low: 'bg-navy/10 text-navy/70',
}

export function PriorityBadge({ priority }: { priority: string }) {
  const style = PRIORITY_STYLES[priority] ?? 'bg-navy/10 text-navy/70'
  return (
    <span
      className={`inline-flex items-center px-3 py-1.5 rounded-sm text-sm font-semibold uppercase tracking-wide ${style}`}
    >
      {priority}
    </span>
  )
}

export function ConfidenceBar({ value }: { value: number }) {
  const pct = Math.round(value * 100)
  return (
    <div>
      <div className="flex justify-between text-xs text-navy/60 mb-1">
        <span>Confidence</span>
        <span>{pct}%</span>
      </div>
      <div className="h-1.5 bg-navy/10 rounded-full overflow-hidden">
        <div
          className="h-full bg-brass transition-all duration-500"
          style={{ width: `${pct}%` }}
        />
      </div>
    </div>
  )
}
