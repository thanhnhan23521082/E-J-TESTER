/**
 * Base API Client
 *
 * Provides HTTP methods for making API requests
 * TODO: Replace with actual backend API calls when backend is ready
 */

import type { ApiResponse, ApiConfig } from './types'

class ApiClient {
  private config: ApiConfig = {
    baseUrl: 'http://localhost:3000/api',
    timeout: 10000,
    headers: {
      'Content-Type': 'application/json',
    },
  }

  async get<T>(endpoint: string): Promise<ApiResponse<T>> {
    try {
      const response = await fetch(`${this.config.baseUrl}${endpoint}`, {
        method: 'GET',
        headers: this.config.headers,
        signal: AbortSignal.timeout(this.config.timeout),
      })

      if (!response.ok) {
        return {
          data: null,
          error: `HTTP ${response.status}: ${response.statusText}`,
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
        headers: this.config.headers,
        body: JSON.stringify(body),
        signal: AbortSignal.timeout(this.config.timeout),
      })

      if (!response.ok) {
        return {
          data: null,
          error: `HTTP ${response.status}: ${response.statusText}`,
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
