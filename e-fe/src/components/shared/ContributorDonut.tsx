import { PieChart, Pie, Cell, ResponsiveContainer } from 'recharts'

interface ContributorDonutProps {
  data: { name: string; value: number; color: string }[]
  size?: number
}

export default function ContributorDonut({ data, size = 120 }: ContributorDonutProps) {
  return (
    <div style={{ width: size, height: size }}>
      <ResponsiveContainer width="100%" height="100%">
        <PieChart>
          <Pie
            data={data}
            cx="50%"
            cy="50%"
            innerRadius={size * 0.3}
            outerRadius={size * 0.45}
            paddingAngle={2}
            dataKey="value"
          >
            {data.map((entry, index) => (
              <Cell key={`cell-${index}`} fill={entry.color} />
            ))}
          </Pie>
        </PieChart>
      </ResponsiveContainer>
    </div>
  )
}
