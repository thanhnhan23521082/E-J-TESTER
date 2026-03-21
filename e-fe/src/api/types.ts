/**
 * API Response Types
 *
 * Standard response wrapper for all API calls
 */

export interface ApiResponse<T> {
  data: T | null
  error: string | null
  status: number
}

export interface ApiConfig {
  baseUrl: string
  timeout: number
  headers: Record<string, string>
  credentials?: RequestCredentials
}
