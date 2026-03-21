/**
 * Student API Module
 *
 * Handles all student-related API calls
 * TODO: Replace mock implementations with actual backend API calls
 */

import type { ApiResponse } from '../types'
import type { Student, Milestone, EtesterCore } from '../../types'
import { mockStudents, mockMilestones, mockEtesterScores } from '../../data/mockData'

export class StudentApi {
  /**
   * Get student profile by ID
   */
  async getStudent(studentId: string): Promise<ApiResponse<Student>> {
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
   * Get student milestones
   */
  async getMilestones(studentId: string): Promise<ApiResponse<Milestone[]>> {
    // TODO: Replace with actual API call
    // return apiClient.get<Milestone[]>(`/students/${studentId}/milestones`)

    // Mock implementation with artificial delay
    await new Promise((resolve) => setTimeout(resolve, 150))

    const milestones = mockMilestones.filter((m) => m.studentId === studentId)

    return {
      data: milestones,
      error: null,
      status: 200,
    }
  }

  /**
   * Get student E-Tester score
   */
  async getEtesterScore(studentId: string): Promise<ApiResponse<EtesterCore>> {
    // TODO: Replace with actual API call
    // return apiClient.get<EtesterCore>(`/students/${studentId}/etester`)

    // Mock implementation with artificial delay
    await new Promise((resolve) => setTimeout(resolve, 100))

    const score = mockEtesterScores.find((s) => s.studentId === studentId)
    if (!score) {
      return {
        data: null,
        error: 'E-Tester score not found',
        status: 404,
      }
    }

    return {
      data: score,
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
