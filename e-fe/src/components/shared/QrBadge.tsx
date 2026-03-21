import QRCode from 'react-qr-code'

interface QrBadgeProps {
  value: string
  size?: number
}

export default function QrBadge({ value, size = 128 }: QrBadgeProps) {
  return (
    <div className="inline-block p-3 bg-white rounded-2xl border border-etest-border/40 shadow-sm">
      <QRCode
        value={value}
        size={size}
        level="H"
        bgColor="#FFFFFF"
        fgColor="#1A1A1A"
      />
    </div>
  )
}
