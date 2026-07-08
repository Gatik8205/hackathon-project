'use client'

import { useState } from 'react'
import { Loader2, ShieldAlert, AlertTriangle } from 'lucide-react'
import { PageHeader, Card, PriorityBadge, ConfidenceBar } from '@/components/ui'
import { api, ScamSessionResponse } from '@/lib/api'

export default function ScamCheckPage() {
  const [transcript, setTranscript] = useState('')
  const [claimedIdentity, setClaimedIdentity] = useState('')
  const [callerNumber, setCallerNumber] = useState('')
  const [videoCall, setVideoCall] = useState(false)
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState<ScamSessionResponse | null>(null)
  const [error, setError] = useState<string | null>(null)

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    if (!transcript.trim()) return
    setLoading(true)
    setError(null)
    setResult(null)
    try {
      const res = await api.detectScamSession({
        transcript,
        claimed_identity: claimedIdentity || undefined,
        caller_number: callerNumber || undefined,
        video_call: videoCall,
      })
      setResult(res)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Something went wrong. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div>
      <PageHeader
        eyebrow="Scam Session Detector"
        title="Classify a call session"
        description="For law enforcement and telecom operators — analyze a call transcript or session description for digital arrest and impersonation scam patterns."
      />

      <div className="px-10 py-8 max-w-3xl">
        <form onSubmit={handleSubmit} className="mb-6 space-y-4">
          <div>
            <label className="block text-xs uppercase tracking-wide text-navy/50 font-semibold mb-1.5">
              Transcript / session description
            </label>
            <textarea
              value={transcript}
              onChange={(e) => setTranscript(e.target.value)}
              placeholder="Paste or describe the call transcript..."
              rows={5}
              className="w-full border border-navy/20 rounded-sm p-4 text-sm bg-white focus:border-brass outline-none resize-none placeholder:text-navy/30"
            />
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-xs uppercase tracking-wide text-navy/50 font-semibold mb-1.5">
                Claimed identity
              </label>
              <input
                value={claimedIdentity}
                onChange={(e) => setClaimedIdentity(e.target.value)}
                placeholder="e.g. CBI officer"
                className="w-full border border-navy/20 rounded-sm px-3 py-2 text-sm bg-white focus:border-brass outline-none placeholder:text-navy/30"
              />
            </div>
            <div>
              <label className="block text-xs uppercase tracking-wide text-navy/50 font-semibold mb-1.5">
                Caller number
              </label>
              <input
                value={callerNumber}
                onChange={(e) => setCallerNumber(e.target.value)}
                placeholder="Optional"
                className="w-full border border-navy/20 rounded-sm px-3 py-2 text-sm bg-white focus:border-brass outline-none placeholder:text-navy/30"
              />
            </div>
          </div>

          <label className="flex items-center gap-2 text-sm text-navy/70">
            <input
              type="checkbox"
              checked={videoCall}
              onChange={(e) => setVideoCall(e.target.checked)}
              className="accent-brass"
            />
            This was a video call
          </label>

          <button
            type="submit"
            disabled={loading || !transcript.trim()}
            className="inline-flex items-center gap-2 bg-navy text-cream px-5 py-2.5 rounded-sm text-sm font-medium hover:bg-navy-light transition-colors disabled:opacity-40 disabled:cursor-not-allowed"
          >
            {loading ? (
              <>
                <Loader2 size={16} className="animate-spin" /> Classifying...
              </>
            ) : (
              <>
                <ShieldAlert size={15} /> Classify session
              </>
            )}
          </button>
        </form>

        {error && (
          <Card className="border-alert bg-alert/5 mb-6 flex items-start gap-3">
            <AlertTriangle size={18} className="text-alert shrink-0 mt-0.5" />
            <div>
              <p className="text-sm font-medium text-alert">Could not complete classification</p>
              <p className="text-sm text-navy/60 mt-1">{error}</p>
            </div>
          </Card>
        )}

        {result && (
          <Card>
            <div className="flex items-center justify-between mb-5">
              <div className="flex items-center gap-3">
                <span
                  className={`inline-flex items-center px-3 py-1.5 rounded-sm text-sm font-semibold ${
                    result.is_scam_session ? 'bg-alert text-white' : 'bg-navy-light text-cream'
                  }`}
                >
                  {result.is_scam_session ? 'Scam Session Detected' : 'No Strong Match'}
                </span>
                <PriorityBadge priority={result.alert_priority} />
              </div>
              <div className="w-40">
                <ConfidenceBar value={result.confidence} />
              </div>
            </div>

            {result.scam_type && (
              <div className="mb-5">
                <p className="text-xs uppercase tracking-wide text-navy/50 font-semibold mb-1">
                  Scam type
                </p>
                <p className="text-sm text-navy font-medium capitalize">
                  {result.scam_type.replace(/_/g, ' ')}
                </p>
              </div>
            )}

            {result.matched_patterns.length > 0 && (
              <div>
                <p className="text-xs uppercase tracking-wide text-navy/50 font-semibold mb-2">
                  Matched patterns
                </p>
                <ul className="space-y-1.5">
                  {result.matched_patterns.map((pattern, i) => (
                    <li key={i} className="text-sm text-navy/80 flex items-start gap-2">
                      <span className="text-alert mt-1">•</span> {pattern}
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </Card>
        )}
      </div>
    </div>
  )
}
