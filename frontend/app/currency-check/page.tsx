'use client'

import { useState, useRef } from 'react'
import { Loader2, Upload, AlertTriangle, CheckCircle2, XCircle } from 'lucide-react'
import { PageHeader, Card, ConfidenceBar } from '@/components/ui'
import { api, CurrencyVerifyResponse } from '@/lib/api'

export default function CurrencyCheckPage() {
  const [file, setFile] = useState<File | null>(null)
  const [preview, setPreview] = useState<string | null>(null)
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState<CurrencyVerifyResponse | null>(null)
  const [error, setError] = useState<string | null>(null)
  const inputRef = useRef<HTMLInputElement>(null)

  function handleFileChange(e: React.ChangeEvent<HTMLInputElement>) {
    const f = e.target.files?.[0]
    if (!f) return
    setFile(f)
    setResult(null)
    setError(null)
    setPreview(URL.createObjectURL(f))
  }

  async function handleVerify() {
    if (!file) return
    setLoading(true)
    setError(null)
    setResult(null)
    try {
      const res = await api.verifyCurrency(file)
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
        eyebrow="Currency Verification"
        title="Check a currency note"
        description="Upload a clear, well-lit photo of a currency note for a preliminary authenticity check."
      />

      <div className="px-10 py-8 max-w-3xl">
        <Card className="mb-6 border-brass/40 bg-brass/5">
          <p className="text-xs text-navy/60 leading-relaxed">
            <strong className="text-navy">Proof of concept:</strong> this check uses lightweight
            image-quality heuristics, not a model trained on labeled genuine/counterfeit note
            datasets. Treat results as indicative only — always verify through official banking
            channels for anything conclusive.
          </p>
        </Card>

        <div
          onClick={() => inputRef.current?.click()}
          className="border-2 border-dashed border-navy/20 rounded-sm p-10 text-center cursor-pointer hover:border-brass transition-colors bg-white mb-4"
        >
          <input
            ref={inputRef}
            type="file"
            accept="image/*"
            onChange={handleFileChange}
            className="hidden"
          />
          {preview ? (
            <img src={preview} alt="Note preview" className="max-h-56 mx-auto rounded-sm" />
          ) : (
            <div className="flex flex-col items-center gap-2 text-navy/50">
              <Upload size={28} strokeWidth={1.5} />
              <p className="text-sm">Click to upload a photo of the note</p>
            </div>
          )}
        </div>

        <button
          onClick={handleVerify}
          disabled={loading || !file}
          className="inline-flex items-center gap-2 bg-navy text-cream px-5 py-2.5 rounded-sm text-sm font-medium hover:bg-navy-light transition-colors disabled:opacity-40 disabled:cursor-not-allowed mb-6"
        >
          {loading ? (
            <>
              <Loader2 size={16} className="animate-spin" /> Analyzing...
            </>
          ) : (
            'Verify note'
          )}
        </button>

        {error && (
          <Card className="border-alert bg-alert/5 mb-6 flex items-start gap-3">
            <AlertTriangle size={18} className="text-alert shrink-0 mt-0.5" />
            <div>
              <p className="text-sm font-medium text-alert">Could not complete verification</p>
              <p className="text-sm text-navy/60 mt-1">{error}</p>
            </div>
          </Card>
        )}

        {result && (
          <Card>
            <div className="flex items-center justify-between mb-5">
              <div className="flex items-center gap-2">
                {result.is_likely_genuine ? (
                  <CheckCircle2 size={20} className="text-navy-light" />
                ) : (
                  <XCircle size={20} className="text-alert" />
                )}
                <span className="text-sm font-semibold text-navy">
                  {result.is_likely_genuine ? 'No issues flagged' : 'Issues flagged'}
                </span>
              </div>
              <div className="w-40">
                <ConfidenceBar value={result.confidence} />
              </div>
            </div>

            <div className="mb-5">
              <p className="text-xs uppercase tracking-wide text-navy/50 font-semibold mb-2">
                Checks performed
              </p>
              <ul className="space-y-1.5">
                {result.checks_performed.map((check, i) => (
                  <li key={i} className="text-sm text-navy/80 flex items-start gap-2">
                    <span className="text-brass-dark mt-1">•</span>{' '}
                    {check.replace(/_/g, ' ')}
                  </li>
                ))}
              </ul>
            </div>

            {result.flagged_issues.length > 0 && (
              <div className="bg-navy/5 rounded-sm p-4">
                <p className="text-xs uppercase tracking-wide text-navy/50 font-semibold mb-2">
                  Notes
                </p>
                <ul className="space-y-1.5">
                  {result.flagged_issues.map((issue, i) => (
                    <li key={i} className="text-sm text-navy/80">
                      {issue}
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
