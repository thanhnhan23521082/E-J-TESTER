/**
 * Mentor API Module
 *
 * Handles all mentor-related API calls
 * TODO: Replace mock implementations with actual backend API calls
 */

import type { ApiResponse } from '../types'
import type { Mentor, Student, Milestone } from '../../types'
import { mockMentors, mockStudents, mockMilestones } from '../../data/mockData'

export class MentorApi {
  /**
   * Get mentor profile by ID
   */
  async getMentor(mentorId: string): Promise<ApiResponse<Mentor>> {
    // TODO: Replace with actual API call
    // return apiClient.get<Mentor>(`/mentors/${mentorId}`)

    // Mock implementation with artificial delay
    await new Promise((resolve) => setTimeout(resolve, 100))

    const mentor = mockMentors.find((m) => m.id === mentorId)
    if (!mentor) {
      return {
        data: null,
        error: 'Mentor not found',
        status: 404,
      }
    }

    return {
      data: mentor,
      error: null,
      status: 200,
    }
  }

  /**
   * Get all students assigned to a mentor
   */
  async getStudents(_mentorId: string): Promise<ApiResponse<Student[]>> {
    // TODO: Replace with actual API call
    // return apiClient.get<Student[]>(`/mentors/${mentorId}/students`)

    // Mock implementation with artificial delay
    await new Promise((resolve) => setTimeout(resolve, 150))

    // For now, return all mock students
    return {
      data: mockStudents,
      error: null,
      status: 200,
    }
  }

  /**
   * Get pending essays for review
   */
  async getPendingEssays(_mentorId: string): Promise<ApiResponse<Milestone[]>> {
    // TODO: Replace with actual API call
    // return apiClient.get<Milestone[]>(`/mentors/${mentorId}/pending-essays`)

    // Mock implementation with artificial delay
    await new Promise((resolve) => setTimeout(resolve, 100))

    // Return milestones that are in progress
    const pending = mockMilestones.filter(
      (m) => m.status === 'in_progress'
    )

    return {
      data: pending,
      error: null,
      status: 200,
    }
  }

  /**
   * Submit review for an essay
   */
  async submitReview(
    _mentorId: string,
    _milestoneId: string,
    _review: {
      score: number
      feedback: string
      strengths: string[]
      improvements: string[]
    }
  ): Promise<ApiResponse<{ success: boolean }>> {
    // TODO: Replace with actual API call
    // return apiClient.post<{ success: boolean }>(`/mentors/${mentorId}/reviews`, { milestoneId, ...review })

    // Mock implementation with artificial delay
    await new Promise((resolve) => setTimeout(resolve, 200))

    return {
      data: {
        success: true,
      },
      error: null,
      status: 201,
    }
  }
}

export const mentorApi = new MentorApi()
