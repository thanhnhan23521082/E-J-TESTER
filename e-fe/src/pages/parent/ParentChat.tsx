import { useState, useRef, useEffect } from 'react'
import { Send, Bot, User, MessageCircle } from 'lucide-react'
import QuickChatBar from '../../components/parent/QuickChatBar'
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
  const messagesEndRef = useRef<HTMLDivElement>(null)

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  const handleSend = (text: string) => {
    if (!text.trim()) return

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

    // Simulate AI response
    setTimeout(() => {
      const aiResponses: Record<string, string> = {
        'Minh Anh đang yếu môn nào?':
          'Dựa trên dữ liệu gần nhất, Minh Anh đang yếu nhất ở kỹ năng Writing với band 6.0, thấp hơn 0.5 band so với yêu cầu của University of Melbourne. Các kỹ năng khác đều đạt hoặc vượt yêu cầu: Listening 7.0, Reading 6.5, Speaking 6.5.',
        'Làm sao để cải thiện Writing?':
          'Để cải thiện Writing từ 6.0 lên 7.0 trong 47 ngày tới, tôi khuyên:\n\n1. Tập trung vào Task 2 - chiếm 66% điểm\n2. Viết ít nhất 3 bài luận mỗi tuần\n3. Nộp qua ETESTER để kiểm tra AI\n4. Tham gia Trại hè Writing tháng 7\n\nBạn có muốn tôi gợi ý lịch học cụ thể không?',
        'Tiến độ so với deadline?':
          'Minh Anh có 47 ngày nữa đến deadline University of Melbourne (07/05/2026). Hiện tại em đủ điều kiện vào 1/2 trường mục tiêu (Monash University). Cần cải thiện thêm 0.5 band Writing để đủ điều kiện vào Melbourne.',
        'Hoạt động gần đây của con?':
          'Hoạt động gần đây của Minh Anh:\n\n• 15/03: Nộp essay "Why Melbourne" Draft 2\n• 10/03: Thi IELTS Mock Test #5 - đạt 6.5\n• 20/02: Hoạt động CSR tại Mái ấm Hoa Hồng\n\nEm đang duy trì streak học tập 12 ngày liên tiếp!',
      }

      const defaultResponse =
        'Cảm ơn bạn đã hỏi! Dựa trên dữ liệu của Minh Anh, em đang có tiến độ tốt. Bạn có thể hỏi cụ thể hơn về:\n• Điểm mạnh/điểm yếu\n• Tiến độ so với deadline\n• Gợi ý cải thiện\n• Hoạt động gần đây'

      const aiMessage: ChatMessage = {
        id: (Date.now() + 1).toString(),
        sender: 'ai',
        content: aiResponses[text] || defaultResponse,
        timestamp: new Date().toISOString(),
      }
      setMessages((prev) => [...prev, aiMessage])
      setIsTyping(false)
    }, 1500)
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
                onKeyDown={(e) => e.key === 'Enter' && handleSend(inputValue)}
                placeholder="Nhập câu hỏi của bạn..."
                className="flex-1 h-12 px-4 bg-etest-bg rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-etest-teal/20 focus:bg-white transition-all"
              />
              <button
                onClick={() => handleSend(inputValue)}
                disabled={!inputValue.trim()}
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
