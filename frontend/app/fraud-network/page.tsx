'use client'

import { useState, useEffect } from 'react'
import { Loader2, AlertTriangle, RefreshCw, Network } from 'lucide-react'
import { PageHeader, Card } from '@/components/ui'
import { api, FraudNetworkResponse } from '@/lib/api'
import FraudGraph from '@/components/FraudGraph'

const LEGEND = [
  { type: 'report', label: 'Fraud report', color: '#B23A3A' },
  { type: 'phone', label: 'Phone number', color: '#C9A34E' },
  { type: 'device', label: 'Device ID', color: '#1E3A5F' },
  { type: 'account', label: 'Bank account', color: '#0B1F3A' },
  { type: 'upi', label: 'UPI ID', color: '#7A8B99' },
]

export default function FraudNetworkPage() {
  const [data, setData] = useState<FraudNetworkResponse | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  async function loadNetwork() {
    setLoading(true)
    setError(null)
    try {
      const res = await api.getFraudNetwork()
      setData(res)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Could not load fraud network.')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    loadNetwork()
  }, [])

  return (
    <div>
      <PageHeader
        eyebrow="Fraud Network Intelligence"
        title="Connected fraud reports"
        description="Reports linked by shared phone numbers, devices, bank accounts, or UPI IDs reveal coordinated fraud rings that isolated reports would miss."
      />

      <div className="px-10 py-8">
        <div className="flex items-center justify-between mb-6 max-w-4xl">
          <div className="flex gap-6">
            {data && (
              <>
                <Stat label="Reports ingested" value={data.nodes.filter((n) => n.type === 'report').length} />
                <Stat label="Clusters detected" value={data.clusters_detected} />
                <Stat
                  label="High-risk rings"
                  value={data.high_risk_clusters.length}
                  highlight={data.high_risk_clusters.length > 0}
                />
              </>
            )}
          </div>
          <button
            onClick={loadNetwork}
            disabled={loading}
            className="inline-flex items-center gap-2 text-sm text-navy/60 hover:text-navy border border-navy/20 px-3 py-1.5 rounded-sm hover:border-brass transition-colors"
          >
            <RefreshCw size={14} className={loading ? 'animate-spin' : ''} /> Refresh
          </button>
        </div>

        {error && (
          <Card className="border-alert bg-alert/5 mb-6 flex items-start gap-3 max-w-4xl">
            <AlertTriangle size={18} className="text-alert shrink-0 mt-0.5" />
            <div>
              <p className="text-sm font-medium text-alert">Could not load network</p>
              <p className="text-sm text-navy/60 mt-1">{error}</p>
              <p className="text-xs text-navy/40 mt-2">
                Ingest sample fraud reports via the backend's /graph/ingest endpoint first.
              </p>
            </div>
          </Card>
        )}

        <Card className="max-w-4xl">
          {loading ? (
            <div className="h-[480px] flex items-center justify-center text-navy/40">
              <Loader2 size={24} className="animate-spin" />
            </div>
          ) : data && data.nodes.length > 0 ? (
            <FraudGraph nodes={data.nodes} edges={data.edges} />
          ) : (
            <div className="h-[480px] flex flex-col items-center justify-center text-navy/40 gap-2">
              <Network size={28} strokeWidth={1.5} />
              <p className="text-sm">No fraud reports ingested yet.</p>
            </div>
          )}
        </Card>

        <div className="flex gap-5 mt-4 flex-wrap max-w-4xl">
          {LEGEND.map(({ type, label, color }) => (
            <div key={type} className="flex items-center gap-1.5 text-xs text-navy/60">
              <span className="w-2.5 h-2.5 rounded-full inline-block" style={{ background: color }} />
              {label}
            </div>
          ))}
        </div>

        {data && data.high_risk_clusters.length > 0 && (
          <Card className="mt-6 max-w-4xl border-alert/30 bg-alert/5">
            <p className="text-xs uppercase tracking-wide text-alert font-semibold mb-3">
              Suspected coordinated fraud rings
            </p>
            <div className="space-y-2">
              {data.high_risk_clusters.map((cluster, i) => (
                <p key={i} className="text-sm text-navy/80">
                  Ring {i + 1}: reports{' '}
                  <span className="font-medium text-navy">{cluster.join(', ')}</span> share
                  identifying infrastructure
                </p>
              ))}
            </div>
          </Card>
        )}
      </div>
    </div>
  )
}

function Stat({
  label,
  value,
  highlight = false,
}: {
  label: string
  value: number
  highlight?: boolean
}) {
  return (
    <div>
      <p className={`font-display text-2xl ${highlight ? 'text-alert' : 'text-navy'}`}>{value}</p>
      <p className="text-xs text-navy/50 uppercase tracking-wide">{label}</p>
    </div>
  )
}
