import { useState } from 'react'
import { useNavigate, Link, useLocation } from 'react-router-dom'
import { GraduationCap, Users, Award, Shield, Check } from 'lucide-react'
import { useRole } from '../hooks/useRole'
import { authApi } from '../api'
import type { AllRoles } from '../types'

const roles: { id: AllRoles; label: string; icon: typeof GraduationCap }[] = [
  { id: 'student', label: 'Học viên', icon: GraduationCap },
  { id: 'parent', label: 'Phụ huynh', icon: Users },
  { id: 'mentor', label: 'Mentor', icon: Award },
  { id: 'manager', label: 'Manager', icon: Shield },
]

export default function Login() {
  const [selectedRole, setSelectedRole] = useState<AllRoles | null>(null)
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState<string | null>(null)
  const [isSubmitting, setIsSubmitting] = useState(false)

  const { setRole } = useRole()
  const navigate = useNavigate()
  const location = useLocation()

  const registrationSuccess = (location.state as { registrationSuccess?: boolean })?.registrationSuccess

  const handleLogin = async () => {
    if (!selectedRole) return
    if (!email.trim() || !password.trim()) {
      setError('Vui lòng nhập email và mật khẩu')
      return
    }

    setError(null)
    setIsSubmitting(true)

    try {
      const token = await authApi.login({
        email: email.trim(),
        password,
      })

      localStorage.setItem('access_token', token.access_token)
      localStorage.setItem('refresh_token', token.refresh_token)

      setRole(selectedRole)

      switch (selectedRole) {
        case 'student':
          navigate('/student')
          break
        case 'parent':
          navigate('/parent')
          break
        case 'mentor':
          navigate('/mentor')
          break
        case 'manager':
          navigate('/manager')
          break
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Đăng nhập thất bại, thử lại sau.')
    } finally {
      setIsSubmitting(false)
    }
  }

  return (
    <div className="min-h-screen bg-etest-bg-login flex items-center justify-center py-[94px] px-4 relative overflow-hidden">
      {/* Decorative "ONE" text on right side */}
      <div className="absolute right-0 top-0 opacity-10 pointer-events-none">
        <span className="text-[120px] font-black text-etest-red leading-none">
          ONE
        </span>
      </div>

      {/* Main Login Container */}
      <div className="w-full max-w-[480px] flex flex-col gap-8 relative z-10">
        {/* Header Section */}
        <div className="flex flex-col gap-4">
          <h1 className="text-[36px] font-black text-etest-red tracking-[-1.8px] text-center">
            ETEST ONE
          </h1>
          <div className="flex flex-col gap-1">
            <h2 className="text-2xl font-bold text-etest-text tracking-tight text-center">
              Chào mừng trở lại
            </h2>
            <p className="text-base font-medium text-etest-subtext text-center">
              Chọn vai trò của bạn để tiếp tục
            </p>
          </div>
        </div>

        {/* Role Selector */}
        <div className="flex gap-3 h-[120px]">
          {roles.map((role) => {
            const isSelected = selectedRole === role.id
            return (
              <button
                key={role.id}
                onClick={() => setSelectedRole(role.id)}
                className={`flex-1 flex flex-col items-center justify-center gap-1 h-[120px] rounded-2xl transition-all relative ${
                  isSelected
                    ? 'bg-[#fef2f2] border-2 border-etest-red'
                    : 'bg-white border-2 border-transparent shadow-glass hover:border-etest-border/30'
                }`}
                style={{ boxShadow: '0 1px 2px 0 rgba(0, 0, 0, 0.05)' }}
              >
                {isSelected && (
                  <div className="absolute top-2.5 right-2.5 w-5 h-5 bg-etest-red rounded-full flex items-center justify-center">
                    <Check className="w-3 h-3 text-white" />
                  </div>
                )}
                <role.icon
                  className={`w-8 h-8 ${isSelected ? 'text-etest-red' : 'text-etest-subtext'}`}
                />
                <span className="text-sm font-bold text-etest-text">{role.label}</span>
              </button>
            )
          })}
        </div>

        {/* Form Section */}
        <div className="bg-white rounded-form shadow-form p-8 flex flex-col gap-6">
          {registrationSuccess && (
            <div className="px-4 py-3 bg-green-50 rounded-xl border border-green-200">
              <p className="text-sm font-medium text-green-700">
                Đăng ký thành công! Bạn có thể đăng nhập ngay bây giờ.
              </p>
            </div>
          )}

          <div className="flex flex-col gap-1.5">
            <label className="text-xs font-bold text-etest-subtext ml-1">
              Số điện thoại hoặc Email
            </label>
            <input
              type="text"
              placeholder="Nhập số điện thoại hoặc email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="w-full h-[44px] px-4 bg-etest-bg rounded-xl border border-etest-border/30 text-etest-text placeholder:text-etest-hint focus:outline-none focus:border-etest-red/50 transition-colors"
            />
          </div>

          <div className="flex flex-col gap-1.5">
            <div className="flex items-center justify-between">
              <label className="text-xs font-bold text-etest-subtext ml-1">
                Mật khẩu
              </label>
              <button className="text-xs font-medium text-etest-muted hover:text-etest-red transition-colors">
                Quên mật khẩu?
              </button>
            </div>
            <input
              type="password"
              placeholder="Nhập mật khẩu"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="w-full h-[44px] px-4 bg-etest-bg rounded-xl border border-etest-border/30 text-etest-text placeholder:text-etest-hint focus:outline-none focus:border-etest-red/50 transition-colors"
            />
          </div>

          {error && (
            <p className="text-sm font-medium text-red-600">{error}</p>
          )}

          <label className="flex items-center gap-2 cursor-pointer">
            <input
              type="checkbox"
              className="w-4 h-4 rounded border-etest-border/30 text-etest-red focus:ring-etest-red/50"
            />
            <span className="text-sm text-etest-subtext">Ghi nhớ đăng nhập</span>
          </label>

          <button
            onClick={handleLogin}
            disabled={!selectedRole || isSubmitting}
            className={`w-full h-[52px] rounded-2xl font-bold text-base transition-all ${
              selectedRole && !isSubmitting
                ? 'btn-primary text-white shadow-button hover:opacity-90'
                : 'bg-etest-border/30 text-etest-hint cursor-not-allowed'
            }`}
          >
            {isSubmitting ? 'Đang xử lý...' : 'Đăng nhập'}
          </button>

          <Link
            to="/register"
            className="w-full text-center text-sm font-semibold text-etest-red hover:opacity-80 transition-opacity"
          >
            Chưa có tài khoản? Đăng ký ngay
          </Link>

          <div className="flex items-center gap-4 py-2">
            <div className="flex-1 h-px bg-etest-border/5" />
            <span className="text-xs font-medium text-etest-hint tracking-wider px-4">
              — hoặc —
            </span>
            <div className="flex-1 h-px bg-etest-border/5" />
          </div>

          <button className="w-full h-12 bg-white rounded-2xl border border-etest-border/10 flex items-center justify-center gap-3 hover:border-etest-border/30 transition-colors">
            <svg className="w-5 h-5" viewBox="0 0 24 24">
              <path fill="#4285F4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z" />
              <path fill="#34A853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z" />
              <path fill="#FBBC05" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z" />
              <path fill="#EA4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z" />
            </svg>
            <span className="text-sm font-semibold text-etest-text">Đăng nhập với Google</span>
          </button>
        </div>

        <div className="flex flex-col gap-4">
          <p className="text-center text-sm font-medium text-etest-muted">
            Cần hỗ trợ? Liên hệ ETEST để được giúp đỡ
          </p>
          <div className="flex items-center justify-center gap-6 pt-4">
            <div className="w-6 h-6 bg-etest-border/30 rounded opacity-30" />
            <div className="w-6 h-6 bg-etest-border/30 rounded opacity-30" />
          </div>
        </div>
      </div>
    </div>
  )
}
