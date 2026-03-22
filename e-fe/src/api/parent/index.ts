/**
 * Parent API Module
 *
 * Handles all parent-related API calls
 */

import type { ApiResponse } from '../types'
import type { Student, WellbeingAlert, DigestData, UpsellCourse } from '../../types'
import { apiClient } from '../client'

const CHATBOT_BASE_URL =
  import.meta.env.VITE_PARENTING_AGENT_API_BASE_URL?.trim() ||
  'http://localhost:8003/api'

interface ParentMeResponse {
  parent_id: number
  full_name: string
  email: string
  phone: string | null
  telegram_id: string | null
  student_id: string | null
}

interface BehavioralLogDto {
  date: string
  duration_min: number | null
  studied: boolean
  session_start: string | null
  is_late_night: boolean
  mood_note: string | null
}

interface BehavioralLogListDto {
  student_id: string
  days: number
  logs: BehavioralLogDto[]
}

interface StudentDigestDto {
  progress_pct: number | null
  milestones_done: number | null
  next_deadline: string | null
  next_deadline_label?: string | null
  days_left: number | null
  priority_action: string | null
  weakest_skill: string | null
}

interface WellbeingAlertDto {
  type: string
  severity: 'none' | 'low' | 'medium' | 'high'
  message: string
}

interface WellbeingApiResponseDto {
  student_id: string
  overall_score: number
  severity: 'none' | 'low' | 'medium' | 'high'
  parent_message?: string
  action_label?: string
  alerts: WellbeingAlertDto[]
  recommendations: string[]
}

interface WeeklyDigestDto {
  student_id: string
  student_name: string
  week_summary: string
}

interface UpsellItemDto {
  program_name: string
  priority: 'high' | 'medium' | 'low'
  pitch: string
}

interface UpsellResponseDto {
  student_id: string
  recommendations: UpsellItemDto[]
}

interface StudentProfileDto extends StudentDigestDto {
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

export interface ParentMe {
  parentId: number
  fullName: string
  email: string
  phone: string | null
  telegramId: string | null
  studentId: string | null
}

export interface ParentBehavioralLog {
  date: string
  durationMin: number
  studied: boolean
  sessionStart: string | null
  isLateNight: boolean
  moodNote: string | null
}

const normalizeTargetSchools = (
  schools: Array<Record<string, unknown>> | null | undefined
): Student['targetSchools'] => {
  if (!schools) return []

  return schools.map((school) => ({
    name: typeof school.name === 'string' ? school.name : 'Unknown School',
    country: typeof school.country === 'string' ? school.country : '',
    deadline: typeof school.deadline === 'string' ? school.deadline : '',
    ieltsRequired: typeof school.ieltsRequired === 'number' ? school.ieltsRequired : 0,
    satRequired: typeof school.satRequired === 'number' ? school.satRequired : null,
    daysUntilDeadline:
      typeof school.daysUntilDeadline === 'number' ? school.daysUntilDeadline : 0,
    isEligible: Boolean(school.isEligible),
    gapIelts: typeof school.gapIelts === 'number' ? school.gapIelts : 0,
    gapSat: typeof school.gapSat === 'number' ? school.gapSat : null,
  }))
}

const normalizeSkills = (
  skills: Record<string, unknown> | null | undefined
): Student['skillBreakdown'] => {
  if (!skills) {
    return { L: 0, R: 0, W: 0, S: 0 }
  }

  const readNumber = (key: string): number =>
    typeof skills[key] === 'number' ? Number(skills[key]) : 0

  return {
    L: readNumber('L') || readNumber('listening') || readNumber('math'),
    R: readNumber('R') || readNumber('reading') || readNumber('reading_writing'),
    W: readNumber('W') || readNumber('writing') || readNumber('essay'),
    S: readNumber('S') || readNumber('speaking'),
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

const mapStudent = (dto: StudentProfileDto): Student => ({
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
})

const mapDigest = (dto: StudentDigestDto): DigestData => ({
  progressPct: dto.progress_pct ?? 0,
  milestonesCompleted: dto.milestones_done ?? 0,
  nextDeadline: dto.next_deadline ?? '',
  nextDeadlineLabel: dto.next_deadline_label ?? '',
  daysLeft: dto.days_left ?? 0,
  priorityAction: dto.priority_action ?? '',
  weakestSkill: dto.weakest_skill ?? '',
})

const mapBehavioralLogs = (logs: BehavioralLogDto[]): ParentBehavioralLog[] => {
  return logs.map((log) => ({
    date: log.date,
    durationMin: log.duration_min ?? 0,
    studied: log.studied,
    sessionStart: log.session_start,
    isLateNight: log.is_late_night,
    moodNote: log.mood_note,
  }))
}

const buildWellbeingFromLogs = (logs: ParentBehavioralLog[]): WellbeingAlert => {
  const lateNightCount = logs.filter((log) => log.isLateNight && log.studied).length
  const hasAlert = lateNightCount >= 3

  return {
    alert: hasAlert,
    severity: hasAlert ? 'high' : lateNightCount > 0 ? 'medium' : 'low',
    message: hasAlert
      ? `Con học muộn ${lateNightCount} đêm liên tiếp tuần này`
      : 'Không có cảnh báo học muộn trong tuần này',
    action: 'Nhắn hỏi thăm con tối nay',
  }
}

const mapWellbeingFromAi = (dto: WellbeingApiResponseDto): WellbeingAlert => {
  const topAlert = dto.alerts[0]
  const alert = dto.severity === 'medium' || dto.severity === 'high'
  const severity = dto.severity === 'high' ? 'high' : dto.severity === 'medium' ? 'medium' : 'low'
  const friendlyMessage = dto.parent_message?.trim()
  const cta = dto.action_label?.trim()

  return {
    alert,
    severity,
    message:
      friendlyMessage ||
      topAlert?.message ||
      (alert
        ? 'Con đang có tín hiệu cần hỗ trợ học tập tuần này'
        : 'Tình hình học tập và sức khỏe học đường của con đang ổn định'),
    action: cta || dto.recommendations[0] || 'Nhắn hỏi thăm con tối nay',
  }
}

const mapUpsellItem = (item: UpsellItemDto): UpsellCourse => {
  const lowerName = item.program_name.toLowerCase()
  const tag: UpsellCourse['tag'] = lowerName.includes('summer') || lowerName.includes('camp')
    ? 'Trại hè'
    : lowerName.includes('workshop')
      ? 'Workshop'
      : 'Khóa học'

  return {
    courseName: item.program_name,
    reason: item.pitch,
    ctaUrl: '/parent/chat',
    tag,
    priority: item.priority,
  }
}

export interface ChatCompletionRequest {
  student_id: string
  message: string
}

export interface ChatCompletionResponse {
  answer: string
  tools_used: string[]
  escalated: boolean
  tool_outputs: Record<string, unknown>
}

export class ParentApi {
  async getMe(): Promise<ApiResponse<ParentMe>> {
    const response = await apiClient.get<ParentMeResponse>('/parents/me')
    if (!response.data || response.error) {
      return {
        data: null,
        error: response.error,
        status: response.status,
      }
    }

    return {
      data: {
        parentId: response.data.parent_id,
        fullName: response.data.full_name,
        email: response.data.email,
        phone: response.data.phone,
        telegramId: response.data.telegram_id,
        studentId: response.data.student_id,
      },
      error: null,
      status: response.status,
    }
  }

  async getMyStudent(): Promise<ApiResponse<Student>> {
    const meRes = await this.getMe()
    if (!meRes.data || !meRes.data.studentId) {
      return {
        data: null,
        error: meRes.error ?? 'Tài khoản phụ huynh chưa liên kết học viên',
        status: meRes.status || 404,
      }
    }

    const studentRes = await apiClient.get<StudentProfileDto>(`/students/${meRes.data.studentId}`)
    if (!studentRes.data || studentRes.error) {
      return {
        data: null,
        error: studentRes.error,
        status: studentRes.status,
      }
    }

    return {
      data: mapStudent(studentRes.data),
      error: null,
      status: studentRes.status,
    }
  }

  async getBehavioralLogs(
    studentId: string,
    days: number = 7
  ): Promise<ApiResponse<ParentBehavioralLog[]>> {
    const response = await apiClient.get<BehavioralLogListDto>(
      `/behavioral-log/${studentId}?days=${days}`
    )

    if (!response.data || response.error) {
      return {
        data: null,
        error: response.error,
        status: response.status,
      }
    }

    return {
      data: mapBehavioralLogs(response.data.logs),
      error: null,
      status: response.status,
    }
  }

  /**
   * Unified chatbot completion endpoint.
   */
  async chatCompletion(
    payload: ChatCompletionRequest
  ): Promise<ApiResponse<ChatCompletionResponse>> {
    const accessToken = localStorage.getItem('access_token')

    if (!accessToken) {
      return {
        data: null,
        error: 'Bạn chưa đăng nhập hoặc phiên đăng nhập đã hết hạn.',
        status: 401,
      }
    }

    try {
      const response = await fetch(`${CHATBOT_BASE_URL}/chat/completion`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${accessToken}`,
        },
        // Backend schema chỉ nhận 2 field: student_id, message.
        body: JSON.stringify(payload),
      })

      if (!response.ok) {
        let error = `HTTP ${response.status}: ${response.statusText}`
        try {
          const errorPayload = await response.json()
          error =
            (typeof errorPayload?.detail === 'string' && errorPayload.detail) ||
            (typeof errorPayload?.message === 'string' && errorPayload.message) ||
            (typeof errorPayload?.error === 'string' && errorPayload.error) ||
            error
        } catch {
          // Keep fallback error text.
        }

        return {
          data: null,
          error,
          status: response.status,
        }
      }

      const data = (await response.json()) as ChatCompletionResponse
      return {
        data,
        error: null,
        status: response.status,
      }
    } catch (error) {
      return {
        data: null,
        error: error instanceof Error ? error.message : 'Unknown error',
        status: 500,
      }
    }
  }

  /**
   * Get all children for a parent
   */
  async getChildren(_parentId: string): Promise<ApiResponse<Student[]>> {
    const studentRes = await this.getMyStudent()
    if (!studentRes.data || studentRes.error) {
      return {
        data: null,
        error: studentRes.error,
        status: studentRes.status,
      }
    }

    return {
      data: [studentRes.data],
      error: null,
      status: 200,
    }
  }

  /**
   * Get wellbeing alerts for a student
   */
  async getWellbeingAlerts(studentId: string): Promise<ApiResponse<WellbeingAlert>> {
    const aiResponse = await apiClient.post<WellbeingApiResponseDto, Record<string, never>>(
      `/ai/wellbeing?student_id=${studentId}&days=14`,
      {}
    )

    if (aiResponse.data && !aiResponse.error) {
      return {
        data: mapWellbeingFromAi(aiResponse.data),
        error: null,
        status: aiResponse.status,
      }
    }

    const logsRes = await this.getBehavioralLogs(studentId, 7)
    if (logsRes.data && !logsRes.error) {
      return {
        data: buildWellbeingFromLogs(logsRes.data),
        error: null,
        status: 200,
      }
    }

    return {
      data: null,
      error: aiResponse.error ?? logsRes.error,
      status: aiResponse.status || logsRes.status,
    }
  }

  /**
   * Get digest data for a student
   */
  async getDigest(studentId: string): Promise<ApiResponse<DigestData>> {
    const profileResponse = await apiClient.get<StudentDigestDto>(`/students/${studentId}`)
    if (!profileResponse.data || profileResponse.error) {
      return {
        data: null,
        error: profileResponse.error,
        status: profileResponse.status,
      }
    }

    const digest = mapDigest(profileResponse.data)
    const weeklyDigest = await apiClient.get<WeeklyDigestDto>(`/digest/${studentId}?days=7`)
    if (weeklyDigest.data && !weeklyDigest.error) {
      digest.parentSummary = weeklyDigest.data.week_summary
    }

    return {
      data: digest,
      error: null,
      status: profileResponse.status,
    }
  }

  async getUpsellSuggestion(studentId: string): Promise<ApiResponse<UpsellCourse | null>> {
    const response = await apiClient.get<UpsellResponseDto>(`/upsell/${studentId}`)
    if (!response.data || response.error) {
      return {
        data: null,
        error: response.error,
        status: response.status,
      }
    }

    const first = response.data.recommendations[0]
    return {
      data: first ? mapUpsellItem(first) : null,
      error: null,
      status: response.status,
    }
  }

  /**
   * Send message to mentor
   */
  async sendMessage(
    _parentId: string,
    _mentorId: string,
    _message: string
  ): Promise<ApiResponse<{ messageId: string }>> {
    // TODO: Replace with actual API call
    // return apiClient.post<{ messageId: string }>(`/parents/${parentId}/messages`, { mentorId, message })

    // Mock implementation with artificial delay
    await new Promise((resolve) => setTimeout(resolve, 200))

    return {
      data: {
        messageId: `msg_${Date.now()}`,
      },
      error: null,
      status: 201,
    }
  }
}

export const parentApi = new ParentApi()
