import { useState, useRef, useEffect } from 'react'
import { Send, Bot, User, MessageCircle } from 'lucide-react'
import QuickChatBar from '../../components/parent/QuickChatBar'
import { parentApi } from '../../api'
import type { ChatMessage } from '../../types'

const initialMessages: ChatMessage[] = [
  {
    id: '1',
    sender: 'ai',
    content:
      'Xin chào! Tôi là trợ lý AI của ETEST ONE. Tôi có thể giúp bạn hiểu rõ hơn về tiến độ học tập của Minh Anh. Bạn muốn biết gì ạ?',
    timestamp: new Date().toISOString(),
  },
]

const suggestions = [
  'Minh Anh đang yếu môn nào?',
  'Làm sao để cải thiện Writing?',
  'Tiến độ so với deadline?',
  'Hoạt động gần đây của con?',
]

export default function ParentChat() {
  const [messages, setMessages] = useState<ChatMessage[]>(initialMessages)
  const [inputValue, setInputValue] = useState('')
  const [isTyping, setIsTyping] = useState(false)
  const [selectedStudentId, setSelectedStudentId] = useState('student_001')
  const messagesEndRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    const loadParent = async () => {
      const response = await parentApi.getMe()
      if (response.data?.studentId) {
        setSelectedStudentId(response.data.studentId)
      }
    }

    void loadParent()
  }, [])

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  const handleSend = async (text: string) => {
    if (!text.trim() || isTyping) return

    // Add user message
    const userMessage: ChatMessage = {
      id: Date.now().toString(),
      sender: 'parent',
      content: text,
      timestamp: new Date().toISOString(),
    }
    setMessages((prev) => [...prev, userMessage])
    setInputValue('')
    setIsTyping(true)

    try {
      const response = await parentApi.chatCompletion({
        student_id: selectedStudentId,
        message: text.trim(),
      })

      const aiMessage: ChatMessage = {
        id: (Date.now() + 1).toString(),
        sender: 'ai',
        content:
          response.data?.answer ||
          response.error ||
          'Hệ thống đang bận, vui lòng thử lại sau.',
        timestamp: new Date().toISOString(),
      }

      setMessages((prev) => [...prev, aiMessage])
    } catch {
      const aiMessage: ChatMessage = {
        id: (Date.now() + 1).toString(),
        sender: 'ai',
        content: 'Không thể kết nối chatbot. Vui lòng kiểm tra backend và thử lại.',
        timestamp: new Date().toISOString(),
      }
      setMessages((prev) => [...prev, aiMessage])
    } finally {
      setIsTyping(false)
    }
  }

  return (
    <div className="space-y-4">
      {/* Chat Header */}
      <section className="bg-white rounded-3xl border border-etest-border/40 shadow-sm p-6">
        <div className="flex items-center gap-4">
          <div className="w-14 h-14 rounded-2xl bg-gradient-to-br from-etest-teal to-etest-teal-dark flex items-center justify-center shadow-lg">
            <MessageCircle className="w-7 h-7 text-white" />
          </div>
          <div>
            <h1 className="text-xl font-bold text-etest-text">Hỏi đáp AI</h1>
            <p className="text-sm text-etest-subtext mt-0.5">
              Giải đáp thắc mắc về tiến độ học tập
            </p>
          </div>
        </div>
      </section>

      {/* Chat Container */}
      <section className="bg-white rounded-3xl border border-etest-border/40 shadow-sm overflow-hidden">
        <div className="flex flex-col h-[calc(100vh-380px)] min-h-[400px]">
          {/* Chat messages */}
          <div className="flex-1 overflow-y-auto p-6 space-y-4">
            {messages.map((message) => (
              <div
                key={message.id}
                className={`flex gap-3 ${
                  message.sender === 'parent' ? 'flex-row-reverse' : ''
                } animate-slideUp`}
              >
                <div
                  className={`w-10 h-10 rounded-xl flex items-center justify-center flex-shrink-0 ${
                    message.sender === 'ai'
                      ? 'bg-etest-teal-light'
                      : 'bg-etest-red-light'
                  }`}
                >
                  {message.sender === 'ai' ? (
                    <Bot className="w-5 h-5 text-etest-teal" />
                  ) : (
                    <User className="w-5 h-5 text-etest-red" />
                  )}
                </div>
                <div
                  className={`max-w-[75%] rounded-2xl px-4 py-3 ${
                    message.sender === 'ai'
                      ? 'bg-etest-bg rounded-tl-none'
                      : 'bg-etest-red text-white rounded-tr-none'
                  }`}
                >
                  <p className="text-sm whitespace-pre-line leading-relaxed">{message.content}</p>
                </div>
              </div>
            ))}

            {/* Typing indicator */}
            {isTyping && (
              <div className="flex gap-3 animate-slideUp">
                <div className="w-10 h-10 rounded-xl bg-etest-teal-light flex items-center justify-center">
                  <Bot className="w-5 h-5 text-etest-teal" />
                </div>
                <div className="bg-etest-bg rounded-2xl rounded-tl-none px-4 py-3">
                  <div className="flex gap-1.5">
                    <span className="w-2 h-2 bg-etest-hint rounded-full animate-bounce" style={{ animationDelay: '0ms' }} />
                    <span className="w-2 h-2 bg-etest-hint rounded-full animate-bounce" style={{ animationDelay: '150ms' }} />
                    <span className="w-2 h-2 bg-etest-hint rounded-full animate-bounce" style={{ animationDelay: '300ms' }} />
                  </div>
                </div>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>

          {/* Quick suggestions */}
          <div className="border-t border-etest-border/30">
            <QuickChatBar suggestions={suggestions} onSelect={handleSend} />
          </div>

          {/* Input area */}
          <div className="p-4 border-t border-etest-border/30">
            <div className="flex gap-3">
              <input
                type="text"
                value={inputValue}
                onChange={(e) => setInputValue(e.target.value)}
                onKeyDown={(e) => {
                  if (e.key === 'Enter' && !e.shiftKey) {
                    e.preventDefault()
                    void handleSend(inputValue)
                  }
                }}
                placeholder="Nhập câu hỏi của bạn..."
                className="flex-1 h-12 px-4 bg-etest-bg rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-etest-teal/20 focus:bg-white transition-all"
              />
              <button
                onClick={() => void handleSend(inputValue)}
                disabled={!inputValue.trim() || isTyping}
                className="w-12 h-12 bg-etest-red text-white rounded-xl flex items-center justify-center disabled:opacity-50 disabled:cursor-not-allowed hover:bg-etest-red-secondary transition-colors shadow-button"
                aria-label="Gửi tin nhắn"
              >
                <Send className="w-5 h-5" />
              </button>
            </div>
          </div>
        </div>
      </section>
    </div>
  )
}
