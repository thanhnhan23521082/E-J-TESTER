import { Outlet } from 'react-router-dom'
import { Link } from 'react-router-dom'
import { GraduationCap, Menu, X } from 'lucide-react'
import { useState } from 'react'

export default function PublicLayout() {
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false)

  return (
    <div className="min-h-screen bg-white">
      {/* Navigation */}
      <nav className="fixed top-0 left-0 right-0 z-50 bg-white border-b border-etest-border">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            {/* Logo */}
            <Link to="/" className="flex items-center gap-2">
              <div className="w-8 h-8 bg-etest-red rounded-lg flex items-center justify-center">
                <GraduationCap className="w-5 h-5 text-white" />
              </div>
              <span className="text-xl font-bold text-etest-text">ETEST ONE</span>
            </Link>

            {/* Desktop Navigation */}
            <div className="hidden md:flex items-center gap-8">
              <Link to="/" className="text-etest-subtext hover:text-etest-text transition-colors">
                Trang chủ
              </Link>
              <Link to="/login" className="px-4 py-2 bg-etest-red text-white font-semibold rounded-lg hover:bg-etest-red-dark transition-colors">
                Đăng nhập
              </Link>
            </div>

            {/* Mobile menu button */}
            <button
              onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
              className="md:hidden p-2 text-etest-subtext hover:text-etest-text"
              aria-label={mobileMenuOpen ? 'Đóng menu' : 'Mở menu'}
            >
              {mobileMenuOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
            </button>
          </div>
        </div>

        {/* Mobile Navigation */}
        {mobileMenuOpen && (
          <div className="md:hidden border-t border-etest-border bg-white">
            <div className="px-4 py-4 space-y-3">
              <Link
                to="/"
                className="block text-etest-subtext hover:text-etest-text transition-colors"
                onClick={() => setMobileMenuOpen(false)}
              >
                Trang chủ
              </Link>
              <Link
                to="/login"
                className="block px-4 py-2 bg-etest-red text-white font-semibold rounded-lg text-center"
                onClick={() => setMobileMenuOpen(false)}
              >
                Đăng nhập
              </Link>
            </div>
          </div>
        )}
      </nav>

      {/* Main content */}
      <main className="pt-16">
        <Outlet />
      </main>

      {/* Footer */}
      <footer className="bg-gray-50 border-t border-etest-border py-8 mt-auto">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center text-etest-subtext text-sm">
            <p>&copy; 2026 ETEST ONE. Bảo lưu mọi quyền.</p>
          </div>
        </div>
      </footer>
    </div>
  )
}
