/**
 * Shared API Module
 *
 * Handles shared API calls accessible by all roles
 * TODO: Replace mock implementations with actual backend API calls
 */

import type { ApiResponse } from '../types'
import type { Student } from '../../types'
import { mockStudents } from '../../data/mockData'

export class SharedApi {
  /**
   * Get student by ID (accessible by all roles)
   */
  async getStudentById(studentId: string): Promise<ApiResponse<Student>> {
    // TODO: Replace with actual API call
    // return apiClient.get<Student>(`/students/${studentId}`)

    // Mock implementation with artificial delay
    await new Promise((resolve) => setTimeout(resolve, 100))

    const student = mockStudents.find((s) => s.id === studentId)
    if (!student) {
      return {
        data: null,
        error: 'Student not found',
        status: 404,
      }
    }

    return {
      data: student,
      error: null,
      status: 200,
    }
  }

  /**
   * Health check endpoint
   */
  async healthCheck(): Promise<ApiResponse<{ status: string; timestamp: string }>> {
    // TODO: Replace with actual API call
    // return apiClient.get<{ status: string; timestamp: string }>('/health')

    // Mock implementation with artificial delay
    await new Promise((resolve) => setTimeout(resolve, 50))

    return {
      data: {
        status: 'ok',
        timestamp: new Date().toISOString(),
      },
      error: null,
      status: 200,
    }
  }
}

export const sharedApi = new SharedApi()
