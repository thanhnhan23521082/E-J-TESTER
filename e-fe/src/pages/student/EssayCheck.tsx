import { useState } from 'react'
import { Upload, FileText, AlertCircle, CheckCircle, Shield, ArrowLeft, RefreshCw } from 'lucide-react'
import { useNavigate } from 'react-router-dom'
import AuthGauge from '../../components/shared/AuthGauge'

export default function EssayCheck() {
  const navigate = useNavigate()
  const [file, setFile] = useState<File | null>(null)
  const [isAnalyzing, setIsAnalyzing] = useState(false)
  const [result, setResult] = useState<{
    authScore: number
    message: string
    patterns: string[]
  } | null>(null)

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const selectedFile = e.target.files?.[0]
    if (selectedFile) {
      setFile(selectedFile)
      setResult(null)
    }
  }

  const handleAnalyze = async () => {
    if (!file) return

    setIsAnalyzing(true)
    await new Promise((resolve) => setTimeout(resolve, 2000))
    setResult({
      authScore: Math.floor(Math.random() * 30) + 70,
      message:
        'Bài viết thể hiện giọng văn cá nhân rõ ràng với các đặc điểm nhất quán.',
      patterns: [
        'Cấu trúc câu đặc trưng',
        'Từ vựng phong phú, phù hợp trình độ',
        'Luận điểm phát triển logic',
      ],
    })
    setIsAnalyzing(false)
  }

  return (
    <div className="space-y-8">
      {/* Header */}
      <section className="bg-white rounded-3xl border border-etest-border/40 shadow-sm p-8">
        <div className="flex items-center gap-4">
          <button
            onClick={() => navigate(-1)}
            className="w-10 h-10 rounded-xl bg-etest-bg-secondary flex items-center justify-center hover:bg-etest-border/20 transition-colors"
          >
            <ArrowLeft className="w-5 h-5 text-etest-subtext" />
          </button>
          <div>
            <h1 className="text-2xl font-bold text-etest-text">Kiểm tra Essay</h1>
            <p className="text-sm text-etest-subtext mt-1">
              Xác thực bài viết trước khi nộp
            </p>
          </div>
        </div>
      </section>

      {/* Main Content Grid */}
      <section className="grid grid-cols-12 gap-8">
        {/* Left Column - Upload & Analysis */}
        <div className="col-span-8 space-y-8">
          {/* Upload Card */}
          <div className="bg-white rounded-3xl border border-etest-border/40 shadow-sm p-8">
            <h2 className="text-lg font-bold text-etest-text mb-6">Tải lên bài viết</h2>
            <div
              className={`relative border-2 border-dashed rounded-2xl p-12 text-center transition-all ${
                file
                  ? 'border-etest-green bg-etest-green-bg/30'
                  : 'border-etest-border/40 hover:border-etest-teal hover:bg-etest-bg/50 cursor-pointer'
              }`}
            >
              {file ? (
                <div className="flex items-center justify-center gap-4">
                  <div className="w-16 h-16 rounded-2xl bg-etest-green-bg flex items-center justify-center flex-shrink-0">
                    <FileText className="w-8 h-8 text-etest-green" />
                  </div>
                  <div className="text-left">
                    <p className="font-semibold text-etest-text">{file.name}</p>
                    <p className="text-sm text-etest-subtext mt-1">
                      {(file.size / 1024).toFixed(1)} KB
                    </p>
                  </div>
                  <div className="w-12 h-12 rounded-full bg-etest-green flex items-center justify-center flex-shrink-0">
                    <CheckCircle className="w-6 h-6 text-white" />
                  </div>
                </div>
              ) : (
                <>
                  <div className="w-16 h-16 rounded-2xl bg-etest-bg-secondary mx-auto mb-4 flex items-center justify-center">
                    <Upload className="w-8 h-8 text-etest-hint" />
                  </div>
                  <p className="text-base font-medium text-etest-text mb-2">
                    Kéo thả hoặc nhấp để tải essay
                  </p>
                  <p className="text-sm text-etest-hint">DOC, DOCX, PDF (tối đa 5MB)</p>
                </>
              )}
              {!file && (
                <input
                  type="file"
                  accept=".doc,.docx,.pdf"
                  onChange={handleFileChange}
                  className="absolute inset-0 opacity-0 cursor-pointer"
                />
              )}
            </div>

            {/* Analyze Button */}
            {file && !result && (
              <button
                onClick={handleAnalyze}
                disabled={isAnalyzing}
                className={`w-full mt-6 py-4 rounded-2xl font-bold text-sm transition-all flex items-center justify-center gap-2 ${
                  isAnalyzing
                    ? 'bg-etest-teal/70 text-white cursor-wait'
                    : 'btn-primary text-white shadow-button hover:opacity-90'
                }`}
              >
                {isAnalyzing ? (
                  <>
                    <div className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                    Đang phân tích...
                  </>
                ) : (
                  <>
                    <Shield className="w-5 h-5" />
                    Phân tích bài viết
                  </>
                )}
              </button>
            )}
          </div>

          {/* Results Section */}
          {result && (
            <div className="space-y-6 animate-slideDown">
              {/* Auth Score Card */}
              <div className="bg-white rounded-3xl border border-etest-border/40 shadow-sm p-8">
                <h2 className="text-lg font-bold text-etest-text mb-6">Kết quả phân tích</h2>
                <div className="flex justify-center mb-6">
                  <AuthGauge score={result.authScore} size="lg" />
                </div>
                <div
                  className={`p-4 rounded-2xl ${
                    result.authScore >= 70
                      ? 'bg-etest-green-bg'
                      : result.authScore >= 40
                      ? 'bg-etest-amber-bg'
                      : 'bg-etest-red-light'
                  }`}
                >
                  <div className="flex items-start gap-3">
                    {result.authScore >= 70 ? (
                      <CheckCircle className="w-5 h-5 text-etest-green mt-0.5 flex-shrink-0" />
                    ) : (
                      <AlertCircle className="w-5 h-5 text-etest-amber mt-0.5 flex-shrink-0" />
                    )}
                    <p className="text-sm text-etest-text leading-relaxed">{result.message}</p>
                  </div>
                </div>
              </div>

              {/* Patterns Card */}
              <div className="bg-white rounded-3xl border border-etest-border/40 shadow-sm p-8">
                <h3 className="font-bold text-etest-text mb-4">Mẫu phát hiện</h3>
                <ul className="space-y-3">
                  {result.patterns.map((pattern, index) => (
                    <li
                      key={index}
                      className="flex items-center gap-3 p-3 bg-etest-bg rounded-xl"
                    >
                      <div className="w-8 h-8 rounded-full bg-etest-green-bg flex items-center justify-center flex-shrink-0">
                        <CheckCircle className="w-4 h-4 text-etest-green" />
                      </div>
                      <span className="text-sm text-etest-text">{pattern}</span>
                    </li>
                  ))}
                </ul>
              </div>

              {/* Reset Button */}
              <button
                onClick={() => {
                  setFile(null)
                  setResult(null)
                }}
                className="w-full py-4 border border-etest-border/40 rounded-2xl text-sm font-semibold text-etest-subtext hover:bg-etest-bg transition-colors flex items-center justify-center gap-2"
              >
                <RefreshCw className="w-4 h-4" />
                Kiểm tra bài khác
              </button>
            </div>
          )}
        </div>

        {/* Right Column - Info & Tips */}
        <div className="col-span-4 space-y-8">
          {/* Why Check Card */}
          <div className="bg-etest-teal-light/50 rounded-3xl border border-etest-teal-border p-8">
            <h3 className="font-bold text-etest-text mb-4 flex items-center gap-2">
              <AlertCircle className="w-5 h-5 text-etest-teal" />
              Tại sao cần kiểm tra?
            </h3>
            <p className="text-sm text-etest-subtext leading-relaxed mb-4">
              ETESTER sử dụng AI để phân tích giọng viết cá nhân của bạn. Bài luận với
              điểm xác thực cao sẽ được ưu tiên trong hồ sơ học tập và dễ dàng được
              mentor xác nhận.
            </p>
            <div className="space-y-3">
              <div className="flex items-center gap-3">
                <div className="w-6 h-6 rounded-full bg-etest-teal flex items-center justify-center flex-shrink-0">
                  <CheckCircle className="w-3.5 h-3.5 text-white" />
                </div>
                <span className="text-sm text-etest-text">Tăng độ tin cậy hồ sơ</span>
              </div>
              <div className="flex items-center gap-3">
                <div className="w-6 h-6 rounded-full bg-etest-teal flex items-center justify-center flex-shrink-0">
                  <CheckCircle className="w-3.5 h-3.5 text-white" />
                </div>
                <span className="text-sm text-etest-text">Được mentor xác nhận nhanh hơn</span>
              </div>
              <div className="flex items-center gap-3">
                <div className="w-6 h-6 rounded-full bg-etest-teal flex items-center justify-center flex-shrink-0">
                  <CheckCircle className="w-3.5 h-3.5 text-white" />
                </div>
                <span className="text-sm text-etest-text">Phát hiện vấn đề trước khi nộp</span>
              </div>
            </div>
          </div>

          {/* Score Guide */}
          <div className="bg-white rounded-3xl border border-etest-border/40 shadow-sm p-8">
            <h3 className="font-bold text-etest-text mb-6">Hướng dẫn điểm số</h3>
            <div className="space-y-4">
              <div className="flex items-start gap-3">
                <div className="w-4 h-4 rounded-full bg-etest-green mt-1 flex-shrink-0" />
                <div>
                  <p className="text-sm font-semibold text-etest-text">70-100: Tốt</p>
                  <p className="text-xs text-etest-subtext mt-0.5">Giọng viết cá nhân rõ ràng</p>
                </div>
              </div>
              <div className="flex items-start gap-3">
                <div className="w-4 h-4 rounded-full bg-etest-amber mt-1 flex-shrink-0" />
                <div>
                  <p className="text-sm font-semibold text-etest-text">40-69: Trung bình</p>
                  <p className="text-xs text-etest-subtext mt-0.5">Cần xem lại một số phần</p>
                </div>
              </div>
              <div className="flex items-start gap-3">
                <div className="w-4 h-4 rounded-full bg-etest-red mt-1 flex-shrink-0" />
                <div>
                  <p className="text-sm font-semibold text-etest-text">0-39: Cần lưu ý</p>
                  <p className="text-xs text-etest-subtext mt-0.5">Nên viết lại các đoạn nghi vấn</p>
                </div>
              </div>
            </div>
          </div>

          {/* Tips Card */}
          <div className="bg-etest-bg-secondary rounded-3xl p-8">
            <h3 className="font-bold text-etest-text mb-4">Mẹo viết essay</h3>
            <ul className="space-y-3 text-sm text-etest-subtext">
              <li className="flex items-start gap-2">
                <span className="text-etest-teal font-bold">1.</span>
                Viết theo giọng văn tự nhiên của bạn
              </li>
              <li className="flex items-start gap-2">
                <span className="text-etest-teal font-bold">2.</span>
                Tránh sử dụng công cụ paraphrase quá nhiều
              </li>
              <li className="flex items-start gap-2">
                <span className="text-etest-teal font-bold">3.</span>
                Duy trì phong cách nhất quán trong toàn bài
              </li>
              <li className="flex items-start gap-2">
                <span className="text-etest-teal font-bold">4.</span>
                Thể hiện quan điểm cá nhân rõ ràng
              </li>
            </ul>
          </div>
        </div>
      </section>
    </div>
  )
}
