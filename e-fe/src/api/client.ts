/**
 * Base API Client
 *
 * Provides HTTP methods for making API requests
 * TODO: Replace with actual backend API calls when backend is ready
 */

import type { ApiResponse, ApiConfig } from './types'

class ApiClient {
  private config: ApiConfig = {
    baseUrl:
      import.meta.env.VITE_PARENTING_API_BASE_URL?.trim() ||
      'http://localhost:8002/api',
    timeout: 10000,
    headers: {
      'Content-Type': 'application/json',
    },
  }

  private buildHeaders(): Record<string, string> {
    const headers: Record<string, string> = { ...this.config.headers }
    const token = localStorage.getItem('access_token')

    if (token) {
      headers.Authorization = `Bearer ${token}`
    }

    return headers
  }

  private async parseApiError(response: Response): Promise<string> {
    try {
      const payload = await response.json()
      if (typeof payload?.detail === 'string') {
        return payload.detail
      }
      if (typeof payload?.message === 'string') {
        return payload.message
      }
      if (typeof payload?.error === 'string') {
        return payload.error
      }
      return `HTTP ${response.status}: ${response.statusText}`
    } catch {
      return `HTTP ${response.status}: ${response.statusText}`
    }
  }

  async get<T>(endpoint: string): Promise<ApiResponse<T>> {
    try {
      const response = await fetch(`${this.config.baseUrl}${endpoint}`, {
        method: 'GET',
        headers: this.buildHeaders(),
        signal: AbortSignal.timeout(this.config.timeout),
      })

      if (!response.ok) {
        return {
          data: null,
          error: await this.parseApiError(response),
          status: response.status,
        }
      }

      const data = await response.json()
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

  async post<T, D = unknown>(
    endpoint: string,
    body: D
  ): Promise<ApiResponse<T>> {
    try {
      const response = await fetch(`${this.config.baseUrl}${endpoint}`, {
        method: 'POST',
        headers: this.buildHeaders(),
        body: JSON.stringify(body),
        signal: AbortSignal.timeout(this.config.timeout),
      })

      if (!response.ok) {
        return {
          data: null,
          error: await this.parseApiError(response),
          status: response.status,
        }
      }

      const data = await response.json()
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

  setConfig(config: Partial<ApiConfig>) {
    this.config = { ...this.config, ...config }
  }
}

export const apiClient = new ApiClient()
