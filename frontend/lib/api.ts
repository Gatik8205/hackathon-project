const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://127.0.0.1:8000'

export interface ChatbotAssessRequest {
  message: string
  channel?: string
  language?: string
  phone_number?: string
}

export interface ChatbotAssessResponse {
  verdict: 'likely_scam' | 'possibly_scam' | 'likely_safe'
  confidence: number
  red_flags: string[]
  advice: string
  recommended_action: string
}

export interface ScamSessionRequest {
  transcript: string
  caller_number?: string
  claimed_identity?: string
  video_call?: boolean
}

export interface ScamSessionResponse {
  is_scam_session: boolean
  confidence: number
  scam_type: string | null
  matched_patterns: string[]
  alert_priority: 'low' | 'medium' | 'high' | 'critical'
}

export interface CurrencyVerifyResponse {
  denomination: string | null
  is_likely_genuine: boolean
  confidence: number
  checks_performed: string[]
  flagged_issues: string[]
}

export interface GraphNode {
  id: string
  type: string
  label: string
}

export interface GraphEdge {
  source: string
  target: string
  relation: string
}

export interface FraudNetworkResponse {
  nodes: GraphNode[]
  edges: GraphEdge[]
  clusters_detected: number
  high_risk_clusters: string[][]
}

async function handleResponse<T>(res: Response): Promise<T> {
  if (!res.ok) {
    const text = await res.text().catch(() => res.statusText)
    throw new Error(`API error ${res.status}: ${text}`)
  }
  return res.json()
}

export const api = {
  async assessMessage(payload: ChatbotAssessRequest): Promise<ChatbotAssessResponse> {
    const res = await fetch(`${API_BASE}/chatbot/assess`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    })
    return handleResponse<ChatbotAssessResponse>(res)
  },

  async detectScamSession(payload: ScamSessionRequest): Promise<ScamSessionResponse> {
    const res = await fetch(`${API_BASE}/scam/detect`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    })
    return handleResponse<ScamSessionResponse>(res)
  },

  async verifyCurrency(file: File): Promise<CurrencyVerifyResponse> {
    const formData = new FormData()
    formData.append('file', file)
    const res = await fetch(`${API_BASE}/currency/verify`, {
      method: 'POST',
      body: formData,
    })
    return handleResponse<CurrencyVerifyResponse>(res)
  },

  async getFraudNetwork(): Promise<FraudNetworkResponse> {
    const res = await fetch(`${API_BASE}/graph/network`)
    return handleResponse<FraudNetworkResponse>(res)
  },

  async ingestFraudReports(reports: Record<string, unknown>[]): Promise<{ status: string; ingested: number }> {
    const res = await fetch(`${API_BASE}/graph/ingest`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(reports),
    })
    return handleResponse(res)
  },
}