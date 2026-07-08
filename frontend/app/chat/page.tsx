'use client'

import { useState } from 'react'
import { Loader2, Send, AlertTriangle } from 'lucide-react'
import { PageHeader, Card, VerdictBadge, ConfidenceBar } from '@/components/ui'
import { api, ChatbotAssessResponse } from '@/lib/api'

export default function ChatPage() {
  const [message, setMessage] = useState('')
  const [phoneNumber, setPhoneNumber] = useState('')
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState<ChatbotAssessResponse | null>(null)
  const [error, setError] = useState<string | null>(null)

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    if (!message.trim()) return
    setLoading(true)
    setError(null)
    setResult(null)
    try {
      const res = await api.assessMessage({
        message,
        channel: 'web',
        phone_number: phoneNumber || undefined,
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
        eyebrow="Citizen Fraud Shield"
        title="Describe what happened"
        description="Tell us about a suspicious call, message, or video call. We'll assess it for common scam patterns and tell you what to do next."
      />

      <div className="max-w-3xl px-10 py-8">
        <form onSubmit={handleSubmit} className="mb-6">
          <textarea
            value={message}
            onChange={(e) => setMessage(e.target.value)}
            placeholder="e.g. Someone called claiming to be from CBI, said there's a case against me, and told me to stay on video call while they 'verify' my bank details..."
            rows={5}
            className="w-full p-4 text-sm bg-white border rounded-sm outline-none resize-none border-navy/20 focus:border-brass placeholder:text-navy/30"
          />
          <div>
            <label className="block text-xs uppercase tracking-wide text-navy/50 font-semibold mb-1.5">
              Phone number involved (optional)
            </label>
            <input
              value={phoneNumber}
              onChange={(e) => setPhoneNumber(e.target.value)}
              placeholder="e.g. +91-9876500001"
              className="w-full max-w-xs px-3 py-2 text-sm bg-white border rounded-sm outline-none border-navy/20 focus:border-brass placeholder:text-navy/30"
            />
            <p className="mt-1 text-xs text-navy/40">
              If flagged as a scam, this helps us connect it to other reports involving the same number.
            </p>
          </div>

          <button
            type="submit"
            disabled={loading || !message.trim()}
            className="mt-3 inline-flex items-center gap-2 bg-navy text-cream px-5 py-2.5 rounded-sm text-sm font-medium hover:bg-navy-light transition-colors disabled:opacity-40 disabled:cursor-not-allowed"
          >
            {loading ? (
              <>
                <Loader2 size={16} className="animate-spin" /> Assessing...
              </>
            ) : (
              <>
                <Send size={15} /> Check for scam
              </>
            )}
          </button>
        </form>

        {error && (
          <Card className="flex items-start gap-3 mb-6 border-alert bg-alert/5">
            <AlertTriangle size={18} className="text-alert shrink-0 mt-0.5" />
            <div>
              <p className="text-sm font-medium text-alert">Could not complete assessment</p>
              <p className="mt-1 text-sm text-navy/60">{error}</p>
              <p className="mt-2 text-xs text-navy/40">
                Check that the backend is running at the configured API URL.
              </p>
            </div>
          </Card>
        )}

        {result && (
          <Card>
            <div className="flex items-center justify-between mb-5">
              <VerdictBadge verdict={result.verdict} />
              <div className="w-40">
                <ConfidenceBar value={result.confidence} />
              </div>
            </div>

            {result.red_flags.length > 0 && (
              <div className="mb-5">
                <p className="mb-2 text-xs font-semibold tracking-wide uppercase text-navy/50">
                  Red flags identified
                </p>
                <ul className="space-y-1.5">
                  {result.red_flags.map((flag, i) => (
                    <li key={i} className="flex items-start gap-2 text-sm text-navy/80">
                      <span className="mt-1 text-alert">•</span> {flag}
                    </li>
                  ))}
                </ul>
              </div>
            )}

            <div className="mb-5">
              <p className="mb-2 text-xs font-semibold tracking-wide uppercase text-navy/50">
                Advice
              </p>
              <p className="text-sm leading-relaxed text-navy/80">{result.advice}</p>
            </div>

            <div className="p-4 rounded-sm bg-navy/5">
              <p className="mb-2 text-xs font-semibold tracking-wide uppercase text-navy/50">
                Recommended action
              </p>
              <p className="text-sm font-medium text-navy">{result.recommended_action}</p>
            </div>
          </Card>
        )}
      </div>
    </div>
  )
}
