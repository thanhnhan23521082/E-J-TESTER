export type AuthRole = 'parent' | 'mentor' | 'student' | 'manager'

export interface LoginPayload {
  email: string
  password: string
}

export interface RegisterPayload {
  email: string
  password: string
  role: AuthRole
  full_name: string
  phone?: string
  // Parent-specific
  telegram_id?: string
  // Mentor-specific
  specialty?: string
  bio?: string
  // Student-specific
  program?: string
  // Manager-specific
  department?: string
}

export interface TokenResponse {
  access_token: string
  refresh_token: string
  token_type: string
  expires_in: number
}

export interface UserResponse {
  id: number
  email: string
  role: AuthRole
  full_name: string | null
  phone: string | null
  created_at: string
}

const AUTH_BASE_URL =
  import.meta.env.VITE_AUTH_API_BASE_URL?.trim() || 'http://localhost:8001'

async function parseApiError(response: Response): Promise<string> {
  try {
    const payload = await response.json()
    if (typeof payload?.detail === 'string') {
      return payload.detail
    }
    if (Array.isArray(payload?.detail)) {
      // Pydantic validation errors
      return payload.detail
        .map((e: { msg: string; loc: string[] }) => `${e.loc.join('.')}: ${e.msg}`)
        .join('; ')
    }
    return `HTTP ${response.status}: ${response.statusText}`
  } catch {
    return `HTTP ${response.status}: ${response.statusText}`
  }
}

export const authApi = {
  async register(body: RegisterPayload): Promise<UserResponse> {
    const response = await fetch(`${AUTH_BASE_URL}/api/auth/register`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(body),
    })

    if (!response.ok) {
      throw new Error(await parseApiError(response))
    }

    return response.json()
  },

  async login(body: LoginPayload): Promise<TokenResponse> {
    const response = await fetch(`${AUTH_BASE_URL}/api/auth/login`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(body),
    })

    if (!response.ok) {
      throw new Error(await parseApiError(response))
    }

    return response.json()
  },
}
