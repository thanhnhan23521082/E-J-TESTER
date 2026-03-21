import { useState, useRef, useEffect } from 'react'
import { Bell, Check, X } from 'lucide-react'

interface Notification {
  id: string
  title: string
  message: string
  time: string
  read: boolean
}

interface NotificationDropdownProps {
  notifications?: Notification[]
}

const defaultNotifications: Notification[] = [
  {
    id: '1',
    title: 'Bài viết mới',
    message: 'Mentor đã phản hồi bài essay của bạn',
    time: '5 phút trước',
    read: false,
  },
  {
    id: '2',
    title: 'ETESTER cập nhật',
    message: 'Điểm số của bạn đã được cập nhật',
    time: '1 giờ trước',
    read: false,
  },
  {
    id: '3',
    title: 'Nhắc nhở',
    message: 'Bạn có bài tập sắp đến hạn',
    time: '2 giờ trước',
    read: true,
  },
]

export default function NotificationDropdown({
  notifications = defaultNotifications,
}: NotificationDropdownProps) {
  const [isOpen, setIsOpen] = useState(false)
  const [items, setItems] = useState(notifications)
  const dropdownRef = useRef<HTMLDivElement>(null)

  const unreadCount = items.filter((n) => !n.read).length

  useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setIsOpen(false)
      }
    }

    document.addEventListener('mousedown', handleClickOutside)
    return () => document.removeEventListener('mousedown', handleClickOutside)
  }, [])

  const markAsRead = (id: string) => {
    setItems((prev) =>
      prev.map((n) => (n.id === id ? { ...n, read: true } : n))
    )
  }

  const markAllAsRead = () => {
    setItems((prev) => prev.map((n) => ({ ...n, read: true })))
  }

  const removeNotification = (id: string) => {
    setItems((prev) => prev.filter((n) => n.id !== id))
  }

  return (
    <div className="relative" ref={dropdownRef}>
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="p-2 text-etest-subtext hover:text-etest-text rounded-lg hover:bg-white/50 relative transition-colors"
        aria-label="Thông báo"
      >
        <Bell className="w-5 h-5" />
        {unreadCount > 0 && (
          <span className="absolute top-1 right-1 w-2 h-2 bg-etest-red rounded-full" />
        )}
      </button>

      {isOpen && (
        <div className="absolute right-0 top-full mt-2 w-80 bg-white rounded-2xl shadow-lg border border-etest-border/20 z-50 overflow-hidden">
          {/* Header */}
          <div className="flex items-center justify-between px-4 py-3 border-b border-etest-border/20">
            <h3 className="text-sm font-bold text-etest-text">Thông báo</h3>
            {unreadCount > 0 && (
              <button
                onClick={markAllAsRead}
                className="text-xs text-etest-teal hover:text-etest-teal-dark font-medium"
              >
                Đánh dấu đã đọc
              </button>
            )}
          </div>

          {/* Notifications List */}
          <div className="max-h-80 overflow-y-auto">
            {items.length === 0 ? (
              <div className="px-4 py-8 text-center">
                <Bell className="w-8 h-8 text-etest-hint mx-auto mb-2" />
                <p className="text-sm text-etest-subtext">Không có thông báo</p>
              </div>
            ) : (
              items.map((notification) => (
                <div
                  key={notification.id}
                  className={`relative px-4 py-3 border-b border-etest-border/10 last:border-b-0 hover:bg-etest-bg/50 transition-colors ${
                    !notification.read ? 'bg-etest-teal-light/30' : ''
                  }`}
                >
                  <div className="flex items-start gap-3">
                    <div
                      className={`w-2 h-2 rounded-full mt-2 flex-shrink-0 ${
                        notification.read ? 'bg-etest-border' : 'bg-etest-teal'
                      }`}
                    />
                    <div className="flex-1 min-w-0">
                      <p className="text-sm font-semibold text-etest-text">
                        {notification.title}
                      </p>
                      <p className="text-xs text-etest-subtext mt-0.5 line-clamp-2">
                        {notification.message}
                      </p>
                      <p className="text-xs text-etest-hint mt-1">
                        {notification.time}
                      </p>
                    </div>
                    <div className="flex items-center gap-1 flex-shrink-0">
                      {!notification.read && (
                        <button
                          onClick={() => markAsRead(notification.id)}
                          className="p-1 text-etest-subtext hover:text-etest-teal transition-colors"
                          aria-label="Đánh dấu đã đọc"
                        >
                          <Check className="w-4 h-4" />
                        </button>
                      )}
                      <button
                        onClick={() => removeNotification(notification.id)}
                        className="p-1 text-etest-subtext hover:text-etest-red transition-colors"
                        aria-label="Xóa thông báo"
                      >
                        <X className="w-4 h-4" />
                      </button>
                    </div>
                  </div>
                </div>
              ))
            )}
          </div>

          {/* Footer */}
          {items.length > 0 && (
            <div className="px-4 py-3 border-t border-etest-border/20 bg-etest-bg/30">
              <button
                onClick={() => setIsOpen(false)}
                className="w-full text-center text-sm text-etest-teal hover:text-etest-teal-dark font-medium"
              >
                Xem tất cả thông báo
              </button>
            </div>
          )}
        </div>
      )}
    </div>
  )
}
