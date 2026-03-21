/**
 * ETESTER API Client
 * Backend: http://localhost:8004 (SERVICE_MODE=etester)
 * All endpoints require Bearer token except badge verify.
 */

const ETESTER_BASE_URL =
  (import.meta.env.VITE_ETESTER_API_BASE_URL as string)?.trim() ||
  'http://localhost:8004'

function getAuthHeaders(): Record<string, string> {
  const token = localStorage.getItem('access_token')
  return {
    'Content-Type': 'application/json',
    ...(token ? { Authorization: `Bearer ${token}` } : {}),
  }
}

async function parseApiError(response: Response): Promise<string> {
  try {
    const payload = await response.json()
    if (typeof payload?.detail === 'string') return payload.detail
    if (Array.isArray(payload?.detail)) {
      return payload.detail
        .map((e: { msg: string; loc: string[] }) => `${e.loc.join('.')}: ${e.msg}`)
        .join('; ')
    }
    return `HTTP ${response.status}: ${response.statusText}`
  } catch {
    return `HTTP ${response.status}: ${response.statusText}`
  }
}

// ─── Response Types ────────────────────────────────────────────────────────

export interface ETESTERCoreResponse {
  student_id: string
  academic_score?: number | null
  writing_growth?: number | null
  skills?: string[]
  mentor_verifications?: number
  total_contributions?: number
  contributor_breakdown?: Record<string, number>
  pending_trace_links?: number
  pending_approvals?: number
  requirements_coverage?: Record<string, unknown>
  parent_support_level?: string
  consistency_score?: number
  narrative_en?: string | null
  narrative_vn?: string | null
  badge_issued?: boolean
  last_updated?: string
}

export interface MilestoneResponse {
  id: number
  student_id: string
  milestone_id: string
  type: string
  title: string
  date: string
  score?: number | null
  score_label?: string | null
  notes?: string | null
  status: string
  contributor_type: string
  ai_summary?: Record<string, unknown> | null
  auth_score?: number | null
  mentor_approved?: boolean | null
  created_at: string
}

export interface TraceLinkResponse {
  id: number
  from_milestone_id: number
  to_milestone_id: number
  student_id: string
  relationship_type: string
  evidence?: string | null
  confidence: number
  student_context_note?: string | null
  suggested_by_ai: boolean
  confirmed_by_mentor: boolean
  confirmed_at?: string | null
  is_active: boolean
  created_at: string
  from_milestone_title?: string | null
  from_milestone_type?: string | null
  to_milestone_title?: string | null
  to_milestone_type?: string | null
}

export interface ETESTERProfileResponse {
  core: ETESTERCoreResponse
  recent_milestones: MilestoneResponse[]
  trace_links: TraceLinkResponse[]
  narrative_en?: string | null
  narrative_vn?: string | null
}

export interface ContributionSummary {
  type: string
  count: number
  avg_score?: number | null
}

export interface ContributionsListResponse {
  student_id: string
  total: number
  milestones: MilestoneResponse[]
  summary_by_type: ContributionSummary[]
}

export interface ContributeRequest {
  student_id: string
  milestone_id: string
  type: string
  title: string
  date: string
  score?: number | null
  score_label?: string | null
  notes?: string | null
  contributor_type?: string
  activity_type: string
  form_data?: Record<string, unknown>
  artifact_text?: string | null
  skills_practiced?: string[]
  had_leadership_role?: boolean
  leadership_role_title?: string | null
  leadership_team_size?: number | null
  leadership_outcome?: string | null
}

export interface ContributeResponse {
  milestone_id: number
  artifact_id: number
  form_id: number
  suggestions_count: number
  core_updated: boolean
}

export interface MentorPendingResponse {
  pending_links: TraceLinkResponse[]
  pending_approvals: MilestoneResponse[]
}

export interface AuthScoringResultResponse {
  id: number
  milestone_id: number
  student_id: string
  auth_score: number
  verdict: string
  dimension_scores?: Record<string, number>
  explaining_artifacts?: string[]
  explanation_en?: string | null
  explanation_vn?: string | null
  scored_at: string
}

export interface BadgeResponse {
  student_id: string
  badge_uid: string
  credential_type: string
  badge_payload?: Record<string, unknown>
  issued_at: string
  expires_at?: string | null
}

export interface BadgeVerifyResponse {
  valid: boolean
  student_id?: string
  badge_uid?: string
  issued_at?: string
  expires_at?: string | null
  revoked?: boolean
  error?: string
}

// ─── API Methods ────────────────────────────────────────────────────────────

export const etesterApi = {
  // ── Profile ──────────────────────────────────────────────────────────────

  async getProfile(studentId: string): Promise<ETESTERProfileResponse> {
    const res = await fetch(`${ETESTER_BASE_URL}/api/etester/${studentId}`, {
      headers: getAuthHeaders(),
    })
    if (!res.ok) throw new Error(await parseApiError(res))
    return res.json()
  },

  async rebuildCore(studentId: string): Promise<ETESTERCoreResponse> {
    const res = await fetch(`${ETESTER_BASE_URL}/api/etester/rebuild-core/${studentId}`, {
      method: 'POST',
      headers: getAuthHeaders(),
    })
    if (!res.ok) throw new Error(await parseApiError(res))
    return res.json()
  },

  // ── Contributions ─────────────────────────────────────────────────────────

  async contribute(body: ContributeRequest): Promise<ContributeResponse> {
    const res = await fetch(`${ETESTER_BASE_URL}/api/etester/contribute`, {
      method: 'POST',
      headers: getAuthHeaders(),
      body: JSON.stringify(body),
    })
    if (!res.ok) throw new Error(await parseApiError(res))
    return res.json()
  },

  async listContributions(
    studentId: string,
    limit = 50,
  ): Promise<ContributionsListResponse> {
    const res = await fetch(
      `${ETESTER_BASE_URL}/api/etester/contributions/${studentId}?limit=${limit}`,
      { headers: getAuthHeaders() },
    )
    if (!res.ok) throw new Error(await parseApiError(res))
    return res.json()
  },

  // ── Trace Links ───────────────────────────────────────────────────────────

  async getTraceLinks(studentId: string): Promise<TraceLinkResponse[]> {
    const res = await fetch(
      `${ETESTER_BASE_URL}/api/etester/trace-links/${studentId}`,
      { headers: getAuthHeaders() },
    )
    if (!res.ok) throw new Error(await parseApiError(res))
    return res.json()
  },

  async addStudentNote(linkId: number, studentNote: string): Promise<TraceLinkResponse> {
    const res = await fetch(
      `${ETESTER_BASE_URL}/api/etester/trace-links/${linkId}/note`,
      {
        method: 'PUT',
        headers: getAuthHeaders(),
        body: JSON.stringify({ student_note: studentNote }),
      },
    )
    if (!res.ok) throw new Error(await parseApiError(res))
    return res.json()
  },

  // ── Mentor ────────────────────────────────────────────────────────────────

  async getMentorPending(mentorId: number): Promise<MentorPendingResponse> {
    const res = await fetch(
      `${ETESTER_BASE_URL}/api/etester/mentor/${mentorId}/pending`,
      { headers: getAuthHeaders() },
    )
    if (!res.ok) throw new Error(await parseApiError(res))
    return res.json()
  },

  async verifyTrace(
    linkId: number,
    body: {
      mentor_id: number
      action: 'confirm' | 'reject'
      note?: string
      new_relationship_type?: string
    },
  ): Promise<TraceLinkResponse> {
    const res = await fetch(
      `${ETESTER_BASE_URL}/api/etester/mentor/verify-trace/${linkId}`,
      {
        method: 'POST',
        headers: getAuthHeaders(),
        body: JSON.stringify(body),
      },
    )
    if (!res.ok) throw new Error(await parseApiError(res))
    return res.json()
  },

  async approveArtifact(
    milestoneId: number,
    body: { mentor_id: number; approved: boolean; note?: string },
  ): Promise<MilestoneResponse> {
    const res = await fetch(
      `${ETESTER_BASE_URL}/api/etester/mentor/approve-artifact/${milestoneId}`,
      {
        method: 'POST',
        headers: getAuthHeaders(),
        body: JSON.stringify(body),
      },
    )
    if (!res.ok) throw new Error(await parseApiError(res))
    return res.json()
  },

  // ── Authenticity Scoring ──────────────────────────────────────────────────

  async scoreAuthenticity(body: {
    student_id: string
    essay: string
  }): Promise<AuthScoringResultResponse> {
    const res = await fetch(`${ETESTER_BASE_URL}/api/etester/ai/authenticity`, {
      method: 'POST',
      headers: getAuthHeaders(),
      body: JSON.stringify(body),
    })
    if (!res.ok) throw new Error(await parseApiError(res))
    return res.json()
  },

  async getAuthResults(milestoneId: number): Promise<AuthScoringResultResponse[]> {
    const res = await fetch(
      `${ETESTER_BASE_URL}/api/etester/ai/auth-results/${milestoneId}`,
      { headers: getAuthHeaders() },
    )
    if (!res.ok) throw new Error(await parseApiError(res))
    return res.json()
  },

  // ── Badge ─────────────────────────────────────────────────────────────────

  async issueBadge(studentId: string, managerId: number): Promise<BadgeResponse> {
    const res = await fetch(
      `${ETESTER_BASE_URL}/api/etester/badge/issue/${studentId}`,
      {
        method: 'POST',
        headers: getAuthHeaders(),
        body: JSON.stringify({ manager_id: managerId }),
      },
    )
    if (!res.ok) throw new Error(await parseApiError(res))
    return res.json()
  },

  async getBadge(studentId: string): Promise<BadgeResponse> {
    const res = await fetch(
      `${ETESTER_BASE_URL}/api/etester/badge/${studentId}`,
      { headers: getAuthHeaders() },
    )
    if (!res.ok) throw new Error(await parseApiError(res))
    return res.json()
  },

  async verifyBadge(badgeUid: string): Promise<BadgeVerifyResponse> {
    const res = await fetch(
      `${ETESTER_BASE_URL}/api/etester/badge/verify/${badgeUid}`,
    )
    if (!res.ok) throw new Error(await parseApiError(res))
    return res.json()
  },
}
