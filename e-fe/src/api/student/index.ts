/**
 * Student API Module
 *
 * Handles all student-related API calls
 */

import type { ApiResponse } from '../types'
import type { Student, Milestone, EtesterCore } from '../../types'
import { apiClient } from '../client'

const ETESTER_BASE_URL =
  import.meta.env.VITE_ETESTER_API_BASE_URL?.trim() ||
  'http://localhost:8004/api/etester'

interface StudentProfileDto {
  student_id: string
  name: string
  program?: string | null
  months_enrolled?: number | null
  ielts_score?: number | null
  sat_score?: number | null
  gpa?: number | null
  skill_breakdown?: Record<string, unknown> | null
  target_schools?: Array<Record<string, unknown>> | null
  parent_id?: number | null
  mentor_id?: number | null
}

interface EtesterMilestoneDto {
  milestone_id: string
  student_id: string
  type: string
  title: string
  date: string
  score: number | null
  score_label: string | null
  mentor_id?: string | null
  mentor_approved?: boolean | null
  auth_score: number | null
  notes: string | null
  status: 'completed' | 'in_progress' | 'upcoming'
  contributor_type: 'student' | 'mentor' | 'parent' | 'institution'
  ai_summary:
    | {
        summary?: string
        skills_demonstrated?: string[]
        evidence_strength?: 'low' | 'medium' | 'high' | 'highest'
      }
    | string
    | null
}

interface EtesterProfileDto {
  core: {
    student_id: string
    academic_score: number | null
    writing_growth: number | null
    skills: Record<string, number> | null
    mentor_verifications: number
    parent_support_level: number | null
    institutional_stamp: string | null
    consistency_score: number | null
    total_contributions: number
    badge_issued: string | null
    last_updated: string
  }
  recent_milestones: EtesterMilestoneDto[]
  narrative: string | null
}

const normalizeTargetSchools = (
  schools: Array<Record<string, unknown>> | null | undefined
): Student['targetSchools'] => {
  if (!schools) return []

  return schools.map((school) => {
    const deadline = typeof school.deadline === 'string' ? school.deadline : ''
    return {
      name: typeof school.name === 'string' ? school.name : 'Unknown School',
      country: typeof school.country === 'string' ? school.country : '',
      deadline,
      ieltsRequired:
        typeof school.ieltsRequired === 'number' ? school.ieltsRequired : 0,
      satRequired: typeof school.satRequired === 'number' ? school.satRequired : null,
      daysUntilDeadline:
        typeof school.daysUntilDeadline === 'number' ? school.daysUntilDeadline : 0,
      isEligible: Boolean(school.isEligible),
      gapIelts: typeof school.gapIelts === 'number' ? school.gapIelts : 0,
      gapSat: typeof school.gapSat === 'number' ? school.gapSat : null,
    }
  })
}

const normalizeSkills = (
  skills: Record<string, unknown> | null | undefined
): Student['skillBreakdown'] => {
  if (!skills) {
    return { L: 0, R: 0, W: 0, S: 0 }
  }

  const fallback = (key: string) =>
    typeof skills[key] === 'number' ? Number(skills[key]) : 0

  return {
    L: fallback('L') || fallback('listening') || fallback('math'),
    R: fallback('R') || fallback('reading') || fallback('reading_writing'),
    W: fallback('W') || fallback('writing') || fallback('essay'),
    S: fallback('S') || fallback('speaking'),
  }
}

const inferProgram = (
  program: string | null | undefined,
  ieltsScore: number | null | undefined,
  satScore: number | null | undefined,
  skills: Record<string, unknown> | null | undefined
): Student['program'] => {
  const normalized = typeof program === 'string' ? program.trim().toUpperCase() : ''
  if (normalized === 'AMP' || normalized === 'IELTS' || normalized === 'SAT') {
    return normalized
  }

  const hasSatScore = typeof satScore === 'number' && satScore > 0
  const hasSatSkills =
    !!skills &&
    (typeof skills.math === 'number' ||
      typeof skills.reading_writing === 'number' ||
      typeof skills.essay === 'number')
  if (hasSatScore || hasSatSkills) {
    return 'SAT'
  }

  const hasIeltsScore = typeof ieltsScore === 'number' && ieltsScore > 0
  const hasIeltsSkills =
    !!skills &&
    (typeof skills.L === 'number' ||
      typeof skills.R === 'number' ||
      typeof skills.W === 'number' ||
      typeof skills.S === 'number' ||
      typeof skills.listening === 'number' ||
      typeof skills.reading === 'number' ||
      typeof skills.writing === 'number' ||
      typeof skills.speaking === 'number')

  if (hasIeltsScore || hasIeltsSkills) {
    return 'IELTS'
  }

  return 'IELTS'
}

const mapStudent = (dto: StudentProfileDto): Student => {
  return {
    id: dto.student_id,
    name: dto.name,
    program: inferProgram(dto.program, dto.ielts_score, dto.sat_score, dto.skill_breakdown),
    monthsEnrolled: dto.months_enrolled ?? 0,
    ieltsScore: dto.ielts_score ?? 0,
    satScore: dto.sat_score ?? null,
    gpa: dto.gpa ?? 0,
    skillBreakdown: normalizeSkills(dto.skill_breakdown),
    targetSchools: normalizeTargetSchools(dto.target_schools),
    parentId: dto.parent_id != null ? String(dto.parent_id) : '',
    mentorId: dto.mentor_id != null ? String(dto.mentor_id) : '',
  }
}

const mapMilestone = (dto: EtesterMilestoneDto): Milestone => {
  const aiSummaryObject =
    typeof dto.ai_summary === 'object' && dto.ai_summary !== null ? dto.ai_summary : null

  return {
    id: dto.milestone_id,
    studentId: dto.student_id,
    type: dto.type as Milestone['type'],
    title: dto.title,
    date: dto.date,
    score: dto.score,
    scoreLabel: dto.score_label ?? '',
    mentorId: dto.mentor_id ?? null,
    mentorApproved: Boolean(dto.mentor_approved),
    authScore: dto.auth_score,
    notes: dto.notes ?? '',
    status: dto.status,
    contributorType: dto.contributor_type,
    aiSummary: {
      summary: aiSummaryObject?.summary ?? '',
      skillsDemonstrated: aiSummaryObject?.skills_demonstrated ?? [],
      evidenceStrength: aiSummaryObject?.evidence_strength ?? 'medium',
    },
  }
}

const mapEtesterCore = (dto: EtesterProfileDto['core'], narrative: string | null): EtesterCore => {
  const supportLevelRaw = dto.parent_support_level
  const parentSupportLevel: EtesterCore['parentSupportLevel'] =
    supportLevelRaw == null
      ? 'medium'
      : supportLevelRaw >= 0.75
        ? 'high'
        : supportLevelRaw >= 0.5
          ? 'active'
          : supportLevelRaw >= 0.25
            ? 'medium'
            : 'low'

  return {
    studentId: dto.student_id,
    academicScore: dto.academic_score ?? 0,
    writingGrowth: dto.writing_growth ?? 0,
    skills: Object.keys(dto.skills ?? {}),
    mentorVerifications: dto.mentor_verifications,
    parentSupportLevel,
    institutionalStamp: Boolean(dto.institutional_stamp),
    consistencyScore: dto.consistency_score ?? 0,
    totalContributions: dto.total_contributions,
    lastUpdated: dto.last_updated,
    narrativeCache: narrative ?? '',
    badgeIssued: Boolean(dto.badge_issued),
  }
}

export class StudentApi {
  private async getEtesterProfile(studentId: string): Promise<ApiResponse<EtesterProfileDto>> {
    const token = localStorage.getItem('access_token')
    try {
      const response = await fetch(`${ETESTER_BASE_URL}/${studentId}`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
          ...(token ? { Authorization: `Bearer ${token}` } : {}),
        },
      })

      if (!response.ok) {
        let error = `HTTP ${response.status}: ${response.statusText}`
        try {
          const payload = (await response.json()) as { detail?: string; message?: string; error?: string }
          error = payload.detail || payload.message || payload.error || error
        } catch {
          // Keep fallback error text.
        }
        return { data: null, error, status: response.status }
      }

      const data = (await response.json()) as EtesterProfileDto
      return { data, error: null, status: response.status }
    } catch (error) {
      return {
        data: null,
        error: error instanceof Error ? error.message : 'Unknown error',
        status: 500,
      }
    }
  }

  /**
   * Get student profile by ID
   */
  async getStudent(studentId: string): Promise<ApiResponse<Student>> {
    const response = await apiClient.get<StudentProfileDto>(`/students/${studentId}`)
    if (!response.data || response.error) {
      return {
        data: null,
        error: response.error,
        status: response.status,
      }
    }

    return {
      data: mapStudent(response.data),
      error: null,
      status: 200,
    }
  }

  /**
   * Get student milestones
   */
  async getMilestones(studentId: string): Promise<ApiResponse<Milestone[]>> {
    const response = await this.getEtesterProfile(studentId)
    if (!response.data || response.error) {
      return {
        data: null,
        error: response.error,
        status: response.status,
      }
    }

    return {
      data: response.data.recent_milestones.map(mapMilestone),
      error: null,
      status: 200,
    }
  }

  /**
   * Get student E-Tester score
   */
  async getEtesterScore(studentId: string): Promise<ApiResponse<EtesterCore>> {
    const response = await this.getEtesterProfile(studentId)
    if (!response.data || response.error) {
      return {
        data: null,
        error: response.error,
        status: response.status,
      }
    }

    return {
      data: mapEtesterCore(response.data.core, response.data.narrative),
      error: null,
      status: 200,
    }
  }

  /**
   * Submit essay for a milestone
   */
  async submitEssay(
    _studentId: string,
    _essay: {
      milestoneId: string
      content: string
      wordCount: number
    }
  ): Promise<ApiResponse<{ submissionId: string }>> {
    // TODO: Replace with actual API call
    // return apiClient.post<{ submissionId: string }>(`/students/${studentId}/essays`, essay)

    // Mock implementation with artificial delay
    await new Promise((resolve) => setTimeout(resolve, 200))

    return {
      data: {
        submissionId: `submission_${Date.now()}`,
      },
      error: null,
      status: 201,
    }
  }
}

export const studentApi = new StudentApi()
