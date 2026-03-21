/**
 * Parent API Module
 *
 * Handles all parent-related API calls
 * TODO: Replace mock implementations with actual backend API calls
 */

import type { ApiResponse } from '../types'
import type { Student, WellbeingAlert, DigestData } from '../../types'
import { mockStudents, mockWellbeingAlerts, mockDigestData } from '../../data/mockData'
import { apiClient } from '../client'

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
  /**
   * Unified chatbot completion endpoint.
   */
  async chatCompletion(
    payload: ChatCompletionRequest
  ): Promise<ApiResponse<ChatCompletionResponse>> {
    return apiClient.post<ChatCompletionResponse, ChatCompletionRequest>(
      '/chat/completion',
      payload
    )
  }

  /**
   * Get all children for a parent
   */
  async getChildren(_parentId: string): Promise<ApiResponse<Student[]>> {
    // TODO: Replace with actual API call
    // return apiClient.get<Student[]>(`/parents/${parentId}/children`)

    // Mock implementation with artificial delay
    await new Promise((resolve) => setTimeout(resolve, 100))

    // For now, return all mock students
    return {
      data: mockStudents,
      error: null,
      status: 200,
    }
  }

  /**
   * Get wellbeing alerts for a student
   */
  async getWellbeingAlerts(_studentId: string): Promise<ApiResponse<WellbeingAlert>> {
    // TODO: Replace with actual API call
    // return apiClient.get<WellbeingAlert>(`/students/${studentId}/wellbeing`)

    // Mock implementation with artificial delay
    await new Promise((resolve) => setTimeout(resolve, 150))

    const alert = mockWellbeingAlerts[0]
    if (!alert) {
      return {
        data: null,
        error: 'Wellbeing alert not found',
        status: 404,
      }
    }

    return {
      data: alert,
      error: null,
      status: 200,
    }
  }

  /**
   * Get digest data for a student
   */
  async getDigest(_studentId: string): Promise<ApiResponse<DigestData>> {
    // TODO: Replace with actual API call
    // return apiClient.get<DigestData>(`/students/${studentId}/digest`)

    // Mock implementation with artificial delay
    await new Promise((resolve) => setTimeout(resolve, 100))

    const digest = mockDigestData[0]
    if (!digest) {
      return {
        data: null,
        error: 'Digest data not found',
        status: 404,
      }
    }

    return {
      data: digest,
      error: null,
      status: 200,
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
