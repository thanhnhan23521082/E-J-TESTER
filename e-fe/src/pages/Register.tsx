import { useState } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import {
  GraduationCap,
  Users,
  Award,
  Shield,
  Check,
  ArrowLeft,
  Eye,
  EyeOff,
  Loader2,
  UserPlus,
  Sparkles,
} from 'lucide-react'
import { authApi } from '../api'
import { useRole } from '../hooks/useRole'
import type { AllRoles } from '../types'
import type { AuthRole } from '../api/auth'

/* ────────────────────────────────────────────────────────── */
/* Role metadata                                             */
/* ────────────────────────────────────────────────────────── */
const roles: {
  id: AllRoles
  backendRole: AuthRole
  label: string
  desc: string
  icon: typeof GraduationCap
}[] = [
  {
    id: 'student',
    backendRole: 'student',
    label: 'Học viên',
    desc: 'Đăng ký để bắt đầu hành trình học tập',
    icon: GraduationCap,
  },
  {
    id: 'parent',
    backendRole: 'parent',
    label: 'Phụ huynh',
    desc: 'Theo dõi tiến trình của con em',
    icon: Users,
  },
  {
    id: 'mentor',
    backendRole: 'mentor',
    label: 'Mentor',
    desc: 'Hướng dẫn và đánh giá học viên',
    icon: Award,
  },
  {
    id: 'manager',
    backendRole: 'manager',
    label: 'Manager',
    desc: 'Quản lý trung tâm và giám sát',
    icon: Shield,
  },
]

/* ────────────────────────────────────────────────────────── */
/* Component                                                  */
/* ────────────────────────────────────────────────────────── */
export default function Register() {
  const navigate = useNavigate()
  const { setRole } = useRole()

  // Step navigation
  const [step, setStep] = useState<1 | 2>(1)

  // Role
  const [selectedRole, setSelectedRole] = useState<AllRoles | null>(null)

  // Common fields
  const [fullName, setFullName] = useState('')
  const [email, setEmail] = useState('')
  const [phone, setPhone] = useState('')
  const [password, setPassword] = useState('')
  const [confirmPassword, setConfirmPassword] = useState('')
  const [showPassword, setShowPassword] = useState(false)

  // Parent-specific
  const [telegramId, setTelegramId] = useState('')

  // Mentor-specific
  const [specialty, setSpecialty] = useState('')
  const [bio, setBio] = useState('')

  // Student-specific
  const [program, setProgram] = useState('')

  // Manager-specific
  const [department, setDepartment] = useState('')

  // UI state
  const [error, setError] = useState<string | null>(null)
  const [isSubmitting, setIsSubmitting] = useState(false)

  const selectedMeta = roles.find((r) => r.id === selectedRole)

  /* ── Validation ─────────────────────────────────────────── */
  const validateStep2 = (): string | null => {
    if (!fullName.trim()) return 'Vui lòng nhập họ và tên'
    if (!email.trim()) return 'Vui lòng nhập email'
    if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email.trim()))
      return 'Email không hợp lệ'
    if (password.length < 8) return 'Mật khẩu phải có ít nhất 8 ký tự'
    if (password !== confirmPassword) return 'Mật khẩu xác nhận không khớp'
    return null
  }

  /* ── Submit ─────────────────────────────────────────────── */
  const handleRegister = async () => {
    const validationError = validateStep2()
    if (validationError) {
      setError(validationError)
      return
    }

    setError(null)
    setIsSubmitting(true)

    try {
      const backendRole = selectedMeta!.backendRole

      await authApi.register({
        email: email.trim(),
        password,
        role: backendRole,
        full_name: fullName.trim(),
        phone: phone.trim() || undefined,
        telegram_id: selectedRole === 'parent' ? telegramId.trim() || undefined : undefined,
        specialty: selectedRole === 'mentor' ? specialty.trim() || undefined : undefined,
        bio: selectedRole === 'mentor' ? bio.trim() || undefined : undefined,
        program: selectedRole === 'student' ? program || undefined : undefined,
        department: selectedRole === 'manager' ? department.trim() || undefined : undefined,
      })

      // Auto-login after registration
      const token = await authApi.login({
        email: email.trim(),
        password,
      })

      localStorage.setItem('access_token', token.access_token)
      localStorage.setItem('refresh_token', token.refresh_token)

      // Set role context and navigate to dashboard
      setRole(selectedRole!)

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
        default:
          navigate('/login', { state: { registrationSuccess: true } })
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Đã xảy ra lỗi')
    } finally {
      setIsSubmitting(false)
    }
  }

  /* ── Renderors ──────────────────────────────────────────── */

  const renderRoleCards = () => (
    <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
      {roles.map((role) => {
        const isSelected = selectedRole === role.id
        return (
          <button
            key={role.id}
            onClick={() => {
              setSelectedRole(role.id)
              setError(null)
            }}
            className={`relative flex flex-col items-start gap-3 p-5 rounded-2xl border-2 transition-all duration-200 text-left group ${
              isSelected
                ? 'bg-[#fef2f2] border-etest-red shadow-md'
                : 'bg-white border-transparent shadow-glass hover:border-etest-border/40 hover:shadow-md'
            }`}
          >
            {/* Selected badge */}
            {isSelected && (
              <div className="absolute top-3 right-3 w-6 h-6 bg-etest-red rounded-full flex items-center justify-center animate-slideDown">
                <Check className="w-3.5 h-3.5 text-white" />
              </div>
            )}

            {/* Icon */}
            <div
              className={`w-12 h-12 rounded-xl flex items-center justify-center transition-colors ${
                isSelected
                  ? 'bg-etest-red/10'
                  : 'bg-etest-bg-secondary group-hover:bg-etest-surface-container'
              }`}
            >
              <role.icon
                className={`w-6 h-6 ${
                  isSelected ? 'text-etest-red' : 'text-etest-subtext'
                }`}
              />
            </div>

            {/* Label + desc */}
            <div>
              <span
                className={`text-base font-bold block ${
                  isSelected ? 'text-etest-red' : 'text-etest-text'
                }`}
              >
                {role.label}
              </span>
              <span className="text-xs text-etest-muted mt-0.5 block">
                {role.desc}
              </span>
            </div>
          </button>
        )
      })}
    </div>
  )

  const renderFormFields = () => (
    <div className="flex flex-col gap-5">
      {/* Full Name */}
      <InputField
        label="Họ và tên *"
        placeholder="Nhập họ và tên đầy đủ"
        value={fullName}
        onChange={setFullName}
      />

      {/* Email */}
      <InputField
        label="Email *"
        type="email"
        placeholder="Nhập địa chỉ email"
        value={email}
        onChange={setEmail}
      />

      {/* Phone */}
      <InputField
        label="Số điện thoại"
        type="tel"
        placeholder="Nhập số điện thoại (không bắt buộc)"
        value={phone}
        onChange={setPhone}
      />

      {/* ── Role-specific fields ─── */}
      {selectedRole === 'parent' && (
        <InputField
          label="Telegram ID"
          placeholder="Nhập Telegram ID (không bắt buộc)"
          value={telegramId}
          onChange={setTelegramId}
        />
      )}

      {selectedRole === 'mentor' && (
        <>
          <InputField
            label="Chuyên môn"
            placeholder="VD: IELTS Writing, SAT Math"
            value={specialty}
            onChange={setSpecialty}
          />
          <div className="flex flex-col gap-1.5">
            <label className="text-xs font-bold text-etest-subtext ml-1">
              Giới thiệu bản thân
            </label>
            <textarea
              placeholder="Mô tả ngắn về kinh nghiệm giảng dạy..."
              value={bio}
              onChange={(e) => setBio(e.target.value)}
              rows={3}
              className="w-full px-4 py-3 bg-etest-bg rounded-xl border border-etest-border/30 text-etest-text placeholder:text-etest-hint focus:outline-none focus:border-etest-red/50 transition-colors resize-none text-sm"
            />
          </div>
        </>
      )}

      {selectedRole === 'student' && (
        <div className="flex flex-col gap-1.5">
          <label className="text-xs font-bold text-etest-subtext ml-1">
            Chương trình học
          </label>
          <select
            value={program}
            onChange={(e) => setProgram(e.target.value)}
            className="w-full h-[44px] px-4 bg-etest-bg rounded-xl border border-etest-border/30 text-etest-text focus:outline-none focus:border-etest-red/50 transition-colors text-sm appearance-none"
          >
            <option value="">-- Chọn chương trình --</option>
            <option value="AMP">AMP</option>
            <option value="IELTS">IELTS</option>
            <option value="SAT">SAT</option>
          </select>
        </div>
      )}

      {selectedRole === 'manager' && (
        <InputField
          label="Phòng ban"
          placeholder="VD: Quản lý đào tạo, Vận hành..."
          value={department}
          onChange={setDepartment}
        />
      )}

      {/* Divider */}
      <div className="flex items-center gap-4 py-1">
        <div className="flex-1 h-px bg-etest-border/10" />
        <span className="text-xs font-medium text-etest-hint">Bảo mật</span>
        <div className="flex-1 h-px bg-etest-border/10" />
      </div>

      {/* Password */}
      <div className="flex flex-col gap-1.5">
        <label className="text-xs font-bold text-etest-subtext ml-1">
          Mật khẩu *
        </label>
        <div className="relative">
          <input
            type={showPassword ? 'text' : 'password'}
            placeholder="Tối thiểu 8 ký tự"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            className="w-full h-[44px] px-4 pr-12 bg-etest-bg rounded-xl border border-etest-border/30 text-etest-text placeholder:text-etest-hint focus:outline-none focus:border-etest-red/50 transition-colors text-sm"
          />
          <button
            type="button"
            onClick={() => setShowPassword(!showPassword)}
            className="absolute right-3 top-1/2 -translate-y-1/2 text-etest-hint hover:text-etest-subtext transition-colors"
          >
            {showPassword ? (
              <EyeOff className="w-4.5 h-4.5" />
            ) : (
              <Eye className="w-4.5 h-4.5" />
            )}
          </button>
        </div>
      </div>

      {/* Confirm Password */}
      <InputField
        label="Xác nhận mật khẩu *"
        type="password"
        placeholder="Nhập lại mật khẩu"
        value={confirmPassword}
        onChange={setConfirmPassword}
      />
    </div>
  )

  /* ── Main render ────────────────────────────────────────── */
  return (
    <div className="min-h-screen bg-etest-bg-login flex items-center justify-center py-12 px-4 relative overflow-hidden">
      {/* Background decoration */}
      <div className="absolute -top-20 -right-20 w-80 h-80 bg-etest-red/5 rounded-full blur-3xl pointer-events-none" />
      <div className="absolute -bottom-20 -left-20 w-60 h-60 bg-etest-blue/5 rounded-full blur-3xl pointer-events-none" />

      {/* Main container */}
      <div className="w-full max-w-[520px] flex flex-col gap-6 relative z-10">
        {/* Header */}
        <div className="flex flex-col items-center gap-3">
          <div className="flex items-center gap-2">
            <Sparkles className="w-5 h-5 text-etest-red" />
            <h1 className="text-[32px] font-black text-etest-red tracking-[-1.5px]">
              ETEST ONE
            </h1>
          </div>
          <div className="text-center">
            <h2 className="text-xl font-bold text-etest-text tracking-tight">
              Tạo tài khoản mới
            </h2>
            <p className="text-sm font-medium text-etest-subtext mt-1">
              {step === 1
                ? 'Chọn vai trò phù hợp với bạn'
                : `Đăng ký với vai trò ${selectedMeta?.label}`}
            </p>
          </div>
        </div>

        {/* Step indicator */}
        <div className="flex items-center gap-3 px-4">
          <div className="flex items-center gap-2 flex-1">
            <div
              className={`w-8 h-8 rounded-full flex items-center justify-center text-sm font-bold transition-colors ${
                step >= 1
                  ? 'bg-etest-red text-white'
                  : 'bg-etest-border/30 text-etest-hint'
              }`}
            >
              {step > 1 ? <Check className="w-4 h-4" /> : '1'}
            </div>
            <span
              className={`text-xs font-bold ${
                step >= 1 ? 'text-etest-text' : 'text-etest-hint'
              }`}
            >
              Chọn vai trò
            </span>
          </div>
          <div
            className={`flex-1 h-0.5 rounded-full transition-colors ${
              step >= 2 ? 'bg-etest-red' : 'bg-etest-border/20'
            }`}
          />
          <div className="flex items-center gap-2 flex-1 justify-end">
            <span
              className={`text-xs font-bold ${
                step >= 2 ? 'text-etest-text' : 'text-etest-hint'
              }`}
            >
              Thông tin
            </span>
            <div
              className={`w-8 h-8 rounded-full flex items-center justify-center text-sm font-bold transition-colors ${
                step >= 2
                  ? 'bg-etest-red text-white'
                  : 'bg-etest-border/30 text-etest-hint'
              }`}
            >
              2
            </div>
          </div>
        </div>

        {/* Card body */}
        <div className="bg-white rounded-form shadow-form p-8 flex flex-col gap-6">
          {step === 1 ? (
            <>
              {renderRoleCards()}

              {/* Next btn */}
              <button
                disabled={!selectedRole}
                onClick={() => {
                  setStep(2)
                  setError(null)
                }}
                className={`w-full h-[52px] rounded-2xl font-bold text-base transition-all ${
                  selectedRole
                    ? 'btn-primary text-white shadow-button hover:opacity-90'
                    : 'bg-etest-border/30 text-etest-hint cursor-not-allowed'
                }`}
              >
                Tiếp tục
              </button>
            </>
          ) : (
            <>
              {/* Back btn */}
              <button
                onClick={() => {
                  setStep(1)
                  setError(null)
                }}
                className="flex items-center gap-1.5 text-sm font-semibold text-etest-muted hover:text-etest-red transition-colors -mt-2 mb-1 self-start"
              >
                <ArrowLeft className="w-4 h-4" />
                Quay lại chọn vai trò
              </button>

              {/* Role badge */}
              {selectedMeta && (
                <div className="flex items-center gap-3 px-4 py-3 bg-etest-red/5 rounded-xl border border-etest-red/10">
                  <selectedMeta.icon className="w-5 h-5 text-etest-red" />
                  <span className="text-sm font-bold text-etest-red">
                    {selectedMeta.label}
                  </span>
                </div>
              )}

              {renderFormFields()}

              {/* Error */}
              {error && (
                <div className="px-4 py-3 bg-red-50 rounded-xl border border-red-200">
                  <p className="text-sm font-medium text-red-600">{error}</p>
                </div>
              )}

              {/* Submit btn */}
              <button
                onClick={handleRegister}
                disabled={isSubmitting}
                className={`w-full h-[52px] rounded-2xl font-bold text-base transition-all flex items-center justify-center gap-2 ${
                  !isSubmitting
                    ? 'btn-primary text-white shadow-button hover:opacity-90'
                    : 'bg-etest-border/30 text-etest-hint cursor-not-allowed'
                }`}
              >
                {isSubmitting ? (
                  <>
                    <Loader2 className="w-5 h-5 animate-spin" />
                    Đang tạo tài khoản...
                  </>
                ) : (
                  <>
                    <UserPlus className="w-5 h-5" />
                    Đăng ký
                  </>
                )}
              </button>
            </>
          )}

          {/* Login link */}
          <Link
            to="/login"
            className="w-full text-center text-sm font-semibold text-etest-red hover:opacity-80 transition-opacity"
          >
            Đã có tài khoản? Đăng nhập ngay
          </Link>
        </div>

        {/* Footer */}
        <p className="text-center text-xs text-etest-muted">
          Bằng việc đăng ký, bạn đồng ý với{' '}
          <span className="text-etest-red font-medium cursor-pointer hover:underline">
            Điều khoản sử dụng
          </span>{' '}
          và{' '}
          <span className="text-etest-red font-medium cursor-pointer hover:underline">
            Chính sách bảo mật
          </span>
        </p>
      </div>
    </div>
  )
}

/* ────────────────────────────────────────────────────────── */
/* Reusable input field                                       */
/* ────────────────────────────────────────────────────────── */
function InputField({
  label,
  type = 'text',
  placeholder,
  value,
  onChange,
}: {
  label: string
  type?: string
  placeholder: string
  value: string
  onChange: (v: string) => void
}) {
  return (
    <div className="flex flex-col gap-1.5">
      <label className="text-xs font-bold text-etest-subtext ml-1">
        {label}
      </label>
      <input
        type={type}
        placeholder={placeholder}
        value={value}
        onChange={(e) => onChange(e.target.value)}
        className="w-full h-[44px] px-4 bg-etest-bg rounded-xl border border-etest-border/30 text-etest-text placeholder:text-etest-hint focus:outline-none focus:border-etest-red/50 transition-colors text-sm"
      />
    </div>
  )
}
