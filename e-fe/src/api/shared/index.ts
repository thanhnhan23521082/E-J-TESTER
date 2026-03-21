/**
 * Shared API Module
 *
 * Endpoints accessible by all roles.
 * All calls go to real ETEST ONE backend via apiClient.
 */

import { apiClient } from '../client'
import type { ApiResponse } from '../types'
import type { Student } from '../../types'

export class SharedApi {
  async getStudentById(studentId: string): Promise<ApiResponse<Student>> {
    return apiClient.get<Student>(`/students/${studentId}`)
  }

  async healthCheck(): Promise<ApiResponse<{ status: string; timestamp: string }>> {
    // /health is unauthenticated — no cookie needed
    return apiClient.get<{ status: string; timestamp: string }>('/health')
  }
}

export const sharedApi = new SharedApi()
