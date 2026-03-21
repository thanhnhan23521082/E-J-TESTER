/**
 * Student API Module
 *
 * All calls go to real ETEST ONE backend via apiClient.
 * Auth is handled automatically via HttpOnly cookie.
 */

import { apiClient } from '../client'
import type { ApiResponse } from '../types'
import type { Student, Milestone, EtesterCore } from '../../types'

export class StudentApi {
  async getStudent(studentId: string): Promise<ApiResponse<Student>> {
    return apiClient.get<Student>(`/students/${studentId}`)
  }

  async getMilestones(studentId: string): Promise<ApiResponse<Milestone[]>> {
    return apiClient.get<Milestone[]>(`/students/${studentId}/milestones`)
  }

  async getEtesterScore(studentId: string): Promise<ApiResponse<EtesterCore>> {
    return apiClient.get<EtesterCore>(`/students/${studentId}/etester`)
  }

  async submitEssay(
    studentId: string,
    essay: { milestoneId: string; content: string; wordCount: number },
  ): Promise<ApiResponse<{ submissionId: string }>> {
    return apiClient.post<{ submissionId: string }, typeof essay>(
      `/students/${studentId}/essays`,
      essay,
    )
  }
}

export const studentApi = new StudentApi()
