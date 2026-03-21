/**
 * Base API Client
 *
 * HTTP client for making API requests to the ETEST ONE backend.
 * Auth: HttpOnly cookie auto-sent by the browser on every request.
 * credentials: 'include' ensures cookies are sent cross-origin.
 */

import type { ApiResponse, ApiConfig } from './types'

class ApiClient {
  private config: ApiConfig & { credentials: RequestCredentials } = {
    baseUrl: 'http://localhost:3000/api',
    timeout: 10000,
    credentials: 'include',
    headers: {
      'Content-Type': 'application/json',
    },
  }

  async get<T>(endpoint: string): Promise<ApiResponse<T>> {
    try {
      const response = await fetch(`${this.config.baseUrl}${endpoint}`, {
        method: 'GET',
        headers: this.config.headers,
        credentials: this.config.credentials,
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
        credentials: this.config.credentials,
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
