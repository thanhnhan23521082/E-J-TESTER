/**
 * Parent API Module
 *
 * All calls go to real ETEST ONE backend via apiClient.
 * Auth is handled automatically via HttpOnly cookie.
 */

import { apiClient } from '../client'
import type { ApiResponse } from '../types'
import type { Student, WellbeingAlert, DigestData } from '../../types'

export class ParentApi {
  async getChildren(parentId: string): Promise<ApiResponse<Student[]>> {
    return apiClient.get<Student[]>(`/parents/${parentId}/children`)
  }

  async getWellbeingAlerts(studentId: string): Promise<ApiResponse<WellbeingAlert>> {
    return apiClient.get<WellbeingAlert>(`/students/${studentId}/wellbeing`)
  }

  async getDigest(studentId: string): Promise<ApiResponse<DigestData>> {
    return apiClient.get<DigestData>(`/students/${studentId}/digest`)
  }

  async sendMessage(
    parentId: string,
    mentorId: string,
    message: string,
  ): Promise<ApiResponse<{ messageId: string }>> {
    return apiClient.post<{ messageId: string }, { mentorId: string; message: string }>(
      `/parents/${parentId}/messages`,
      { mentorId, message },
    )
  }
}

export const parentApi = new ParentApi()
