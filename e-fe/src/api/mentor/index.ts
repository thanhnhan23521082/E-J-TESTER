/**
 * Mentor API Module
 *
 * All calls go to real ETEST ONE backend via apiClient.
 * Auth is handled automatically via HttpOnly cookie.
 */

import { apiClient } from '../client'
import type { ApiResponse } from '../types'
import type { Mentor, Student, Milestone } from '../../types'

export class MentorApi {
  async getMentor(mentorId: string): Promise<ApiResponse<Mentor>> {
    return apiClient.get<Mentor>(`/mentors/${mentorId}`)
  }

  async getStudents(mentorId: string): Promise<ApiResponse<Student[]>> {
    return apiClient.get<Student[]>(`/mentors/${mentorId}/students`)
  }

  async getPendingEssays(mentorId: string): Promise<ApiResponse<Milestone[]>> {
    return apiClient.get<Milestone[]>(`/mentors/${mentorId}/pending-essays`)
  }

  async submitReview(
    mentorId: string,
    milestoneId: string,
    review: { score: number; feedback: string; strengths: string[]; improvements: string[] },
  ): Promise<ApiResponse<{ success: boolean }>> {
    return apiClient.post<{ success: boolean }, typeof review & { milestoneId: string }>(
      `/mentors/${mentorId}/reviews`,
      { milestoneId, ...review },
    )
  }
}

export const mentorApi = new MentorApi()
