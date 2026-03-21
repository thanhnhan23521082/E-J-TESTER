import { Link } from 'react-router-dom'
import { GraduationCap, Users, Award, CheckCircle, TrendingUp, Shield, Sparkles } from 'lucide-react'

export default function Homepage() {
  return (
    <div className="min-h-screen bg-etest-bg">
      {/* Hero Section */}
      <section className="relative overflow-hidden bg-gradient-to-br from-etest-bg via-white to-etest-bg-secondary py-20 px-4">
        <div className="max-w-7xl mx-auto">
          <div className="text-center space-y-6">
            <div className="inline-flex items-center gap-2 px-4 py-2 bg-etest-red-light rounded-full border border-etest-red/20">
              <Sparkles className="w-4 h-4 text-etest-red" />
              <span className="text-sm font-semibold text-etest-red">Nền tảng học tập thông minh</span>
            </div>

            <h1 className="text-5xl md:text-6xl font-black text-etest-text tracking-tight">
              ETEST ONE
            </h1>

            <p className="text-xl md:text-2xl text-etest-subtext max-w-3xl mx-auto leading-relaxed">
              Hệ thống quản lý học tập toàn diện cho học viên, phụ huynh và mentor
            </p>

            <div className="flex flex-col sm:flex-row gap-4 justify-center pt-4">
              <Link
                to="/login"
                className="px-8 py-4 btn-primary text-white font-bold rounded-2xl shadow-button hover:opacity-90 transition-all"
              >
                Đăng nhập ngay
              </Link>
              <a
                href="#features"
                className="px-8 py-4 bg-white text-etest-text font-bold rounded-2xl border-2 border-etest-border/30 hover:border-etest-red/50 transition-all"
              >
                Tìm hiểu thêm
              </a>
            </div>
          </div>
        </div>
      </section>

      {/* Problem Statement Section */}
      <section className="py-20 px-4 bg-etest-bg-secondary">
        <div className="max-w-7xl mx-auto">
          <div className="text-center space-y-4 mb-16">
            <h2 className="text-3xl md:text-4xl font-bold text-etest-text">
              Giải pháp học tập hiện đại
            </h2>
            <p className="text-lg text-etest-subtext max-w-2xl mx-auto">
              Kết nối học viên, phụ huynh và mentor trong một hệ sinh thái học tập thông minh
            </p>
          </div>

          <div className="grid md:grid-cols-3 gap-8">
            {/* Student Card */}
            <div className="bg-white rounded-3xl p-8 shadow-card border border-etest-border/20 hover:shadow-xl transition-all">
              <div className="w-16 h-16 bg-gradient-to-br from-etest-red to-etest-red-secondary rounded-2xl flex items-center justify-center mb-6">
                <GraduationCap className="w-8 h-8 text-white" />
              </div>
              <h3 className="text-xl font-bold text-etest-text mb-3">Học viên</h3>
              <p className="text-etest-subtext leading-relaxed">
                Theo dõi tiến độ học tập, nộp bài tập và nhận phản hồi từ mentor một cách dễ dàng
              </p>
            </div>

            {/* Parent Card */}
            <div className="bg-white rounded-3xl p-8 shadow-card border border-etest-border/20 hover:shadow-xl transition-all">
              <div className="w-16 h-16 bg-gradient-to-br from-etest-teal to-etest-teal-dark rounded-2xl flex items-center justify-center mb-6">
                <Users className="w-8 h-8 text-white" />
              </div>
              <h3 className="text-xl font-bold text-etest-text mb-3">Phụ huynh</h3>
              <p className="text-etest-subtext leading-relaxed">
                Cập nhật tiến độ con em, nhận thông báo quan trọng và trao đổi với mentor
              </p>
            </div>

            {/* Mentor Card */}
            <div className="bg-white rounded-3xl p-8 shadow-card border border-etest-border/20 hover:shadow-xl transition-all">
              <div className="w-16 h-16 bg-gradient-to-br from-etest-amber to-orange-600 rounded-2xl flex items-center justify-center mb-6">
                <Award className="w-8 h-8 text-white" />
              </div>
              <h3 className="text-xl font-bold text-etest-text mb-3">Mentor</h3>
              <p className="text-etest-subtext leading-relaxed">
                Quản lý học viên, chấm bài và đóng góp tài liệu học tập hiệu quả
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section id="features" className="py-20 px-4 bg-white">
        <div className="max-w-7xl mx-auto">
          <div className="text-center space-y-4 mb-16">
            <h2 className="text-3xl md:text-4xl font-bold text-etest-text">
              Tính năng nổi bật
            </h2>
            <p className="text-lg text-etest-subtext max-w-2xl mx-auto">
              Hệ thống được thiết kế để tối ưu trải nghiệm học tập
            </p>
          </div>

          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
            <div className="flex gap-4">
              <div className="flex-shrink-0">
                <div className="w-12 h-12 bg-etest-red-light rounded-xl flex items-center justify-center">
                  <CheckCircle className="w-6 h-6 text-etest-red" />
                </div>
              </div>
              <div>
                <h3 className="font-bold text-etest-text mb-2">Theo dõi tiến độ</h3>
                <p className="text-sm text-etest-subtext">
                  Cập nhật tiến độ học tập theo thời gian thực
                </p>
              </div>
            </div>

            <div className="flex gap-4">
              <div className="flex-shrink-0">
                <div className="w-12 h-12 bg-etest-teal-light rounded-xl flex items-center justify-center">
                  <TrendingUp className="w-6 h-6 text-etest-teal" />
                </div>
              </div>
              <div>
                <h3 className="font-bold text-etest-text mb-2">Phân tích chi tiết</h3>
                <p className="text-sm text-etest-subtext">
                  Báo cáo và thống kê học tập đầy đủ
                </p>
              </div>
            </div>

            <div className="flex gap-4">
              <div className="flex-shrink-0">
                <div className="w-12 h-12 bg-etest-amber-bg rounded-xl flex items-center justify-center">
                  <Shield className="w-6 h-6 text-etest-amber" />
                </div>
              </div>
              <div>
                <h3 className="font-bold text-etest-text mb-2">Bảo mật cao</h3>
                <p className="text-sm text-etest-subtext">
                  Dữ liệu được bảo vệ an toàn tuyệt đối
                </p>
              </div>
            </div>

            <div className="flex gap-4">
              <div className="flex-shrink-0">
                <div className="w-12 h-12 bg-etest-green-bg rounded-xl flex items-center justify-center">
                  <GraduationCap className="w-6 h-6 text-etest-green" />
                </div>
              </div>
              <div>
                <h3 className="font-bold text-etest-text mb-2">E-Tester</h3>
                <p className="text-sm text-etest-subtext">
                  Xác thực tính xác thực của bài làm
                </p>
              </div>
            </div>

            <div className="flex gap-4">
              <div className="flex-shrink-0">
                <div className="w-12 h-12 bg-etest-red-light rounded-xl flex items-center justify-center">
                  <Users className="w-6 h-6 text-etest-red" />
                </div>
              </div>
              <div>
                <h3 className="font-bold text-etest-text mb-2">Kết nối 3 bên</h3>
                <p className="text-sm text-etest-subtext">
                  Học viên, phụ huynh và mentor luôn đồng bộ
                </p>
              </div>
            </div>

            <div className="flex gap-4">
              <div className="flex-shrink-0">
                <div className="w-12 h-12 bg-etest-teal-light rounded-xl flex items-center justify-center">
                  <Award className="w-6 h-6 text-etest-teal" />
                </div>
              </div>
              <div>
                <h3 className="font-bold text-etest-text mb-2">Milestone tracking</h3>
                <p className="text-sm text-etest-subtext">
                  Theo dõi các mốc quan trọng trong học tập
                </p>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-20 px-4 bg-gradient-to-br from-etest-red to-etest-red-secondary">
        <div className="max-w-4xl mx-auto text-center space-y-6">
          <h2 className="text-3xl md:text-4xl font-bold text-white">
            Sẵn sàng bắt đầu?
          </h2>
          <p className="text-lg text-white/90">
            Đăng nhập ngay để trải nghiệm hệ thống học tập thông minh
          </p>
          <Link
            to="/login"
            className="inline-block px-8 py-4 bg-white text-etest-red font-bold rounded-2xl hover:bg-gray-50 transition-all shadow-xl"
          >
            Đăng nhập ngay
          </Link>
        </div>
      </section>
    </div>
  )
}
