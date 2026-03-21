import { useState } from 'react'

interface GraphNodeData {
  id: string
  label: string
  type: 'experience' | 'draft' | 'final' | 'mentor' | 'test' | 'award'
  x: number
  y: number
  color: string
  size?: number
}

interface GraphEdgeData {
  from: string
  to: string
  color: string
  dashed?: boolean
}

const NODES: GraphNodeData[] = [
  { id: 'camp', label: 'Writing Camp', type: 'experience', x: 80, y: 60, color: '#0D9488' },
  { id: 'csr', label: 'CSR Project', type: 'experience', x: 60, y: 160, color: '#0D9488' },
  { id: 'draft1', label: 'Draft #1', type: 'draft', x: 220, y: 80, color: '#D97706' },
  { id: 'draft2', label: 'Draft #2', type: 'draft', x: 240, y: 160, color: '#D97706' },
  { id: 'final', label: 'PS FINAL', type: 'final', x: 220, y: 250, color: '#BB0016', size: 40 },
  { id: 'session5', label: 'Session #5', type: 'mentor', x: 380, y: 60, color: '#7C3AED' },
  { id: 'session7', label: 'Session #7', type: 'mentor', x: 400, y: 150, color: '#7C3AED' },
  { id: 'ielts', label: 'IELTS 6.5', type: 'test', x: 120, y: 280, color: '#64748B' },
]

const EDGES: GraphEdgeData[] = [
  { from: 'camp', to: 'draft1', color: '#0D9488' },
  { from: 'csr', to: 'draft1', color: '#0D9488' },
  { from: 'draft1', to: 'draft2', color: '#D97706' },
  { from: 'draft2', to: 'final', color: '#D97706' },
  { from: 'session5', to: 'draft1', color: '#7C3AED' },
  { from: 'session7', to: 'draft2', color: '#7C3AED' },
  { from: 'ielts', to: 'final', color: '#64748B', dashed: true },
]

function getNode(id: string) {
  return NODES.find(n => n.id === id)
}

export default function MiniArtifactGraph() {
  const [hoveredNode, setHoveredNode] = useState<string | null>(null)
  const [activeFilter, setActiveFilter] = useState<'all' | 'essay' | 'test'>('all')

  const filters = [
    { key: 'all' as const, label: 'All' },
    { key: 'essay' as const, label: 'Essay path' },
    { key: 'test' as const, label: 'Test progress' },
  ]

  const filteredEdges = EDGES.filter(e => {
    if (activeFilter === 'all') return true
    if (activeFilter === 'essay') {
      const src = getNode(e.from)
      const tgt = getNode(e.to)
      return src?.type !== 'test' && tgt?.type !== 'test'
    }
    return e.from === 'ielts' || e.to === 'ielts'
  })

  const highlightedNodeIds = hoveredNode
    ? new Set([
        hoveredNode,
        ...filteredEdges.filter(e => e.from === hoveredNode || e.to === hoveredNode).flatMap(e => [e.from, e.to]),
      ])
    : null

  return (
    <div className="bg-etest-bg-secondary rounded-3xl overflow-hidden relative">
      <div className="flex items-center justify-between px-8 pt-8 pb-4">
        <div>
          <h3 className="font-bold text-xl text-etest-text">Learning graph</h3>
          <p className="text-sm text-etest-hint mt-0.5">How your milestones connect across disciplines.</p>
        </div>
        <div className="flex gap-1 p-1 bg-etest-surface-container rounded-xl">
          {filters.map(f => (
            <button
              key={f.key}
              onClick={() => setActiveFilter(f.key)}
              className={`px-4 py-1.5 text-xs font-semibold rounded-lg transition-all ${
                activeFilter === f.key
                  ? 'bg-white text-etest-red shadow-sm'
                  : 'text-etest-hint hover:text-etest-text'
              }`}
            >
              {f.label}
            </button>
          ))}
        </div>
      </div>

      <div className="relative w-full h-[320px] px-4">
        <svg className="absolute inset-0 w-full h-full pointer-events-none" xmlns="http://www.w3.org/2000/svg">
          <defs>
            {['teal', 'purple', 'amber', 'gray'].map(name => (
              <marker
                key={name}
                id={`arrow-${name}`}
                markerWidth="6"
                markerHeight="6"
                refX="8"
                refY="5"
                orient="auto-start-reverse"
                viewBox="0 0 10 10"
              >
                <path
                  d="M 0 0 L 10 5 L 0 10 z"
                  fill={
                    name === 'teal' ? '#0D9488' :
                    name === 'purple' ? '#7C3AED' :
                    name === 'amber' ? '#D97706' : '#64748B'
                  }
                />
              </marker>
            ))}
          </defs>
          {filteredEdges.map((edge, i) => {
            const src = getNode(edge.from)
            const tgt = getNode(edge.to)
            if (!src || !tgt) return null
            const markerColor = edge.color === '#0D9488' ? 'teal' :
                               edge.color === '#7C3AED' ? 'purple' :
                               edge.color === '#D97706' ? 'amber' : 'gray'
            const dimmed = highlightedNodeIds && (!highlightedNodeIds.has(edge.from) || !highlightedNodeIds.has(edge.to))
            return (
              <path
                key={i}
                d={`M ${src.x} ${src.y} L ${tgt.x} ${tgt.y}`}
                stroke={edge.color}
                strokeWidth={edge.dashed ? 1.5 : 2}
                strokeDasharray={edge.dashed ? '6,4' : undefined}
                fill="none"
                markerEnd={`url(#arrow-${markerColor})`}
                opacity={dimmed ? 0.15 : 0.7}
                className="transition-opacity duration-200"
              />
            )
          })}
        </svg>

        {NODES.map(node => {
          const size = node.size || 28
          const dimmed = highlightedNodeIds && !highlightedNodeIds.has(node.id)
          return (
            <div
              key={node.id}
              className={`absolute flex flex-col items-center gap-1 cursor-pointer transition-all duration-200 ${
                dimmed ? 'opacity-20' : 'opacity-100'
              }`}
              style={{ left: node.x - size / 2, top: node.y - size / 2 }}
              onMouseEnter={() => setHoveredNode(node.id)}
              onMouseLeave={() => setHoveredNode(null)}
            >
              <div
                className={`rounded-full flex items-center justify-center text-white font-bold text-[9px] shadow-md border-2 border-white ${
                  node.type === 'final' ? 'ring-4 ring-etest-red/10' : ''
                }`}
                style={{
                  width: size,
                  height: size,
                  backgroundColor: node.color,
                }}
              >
                {node.type === 'final' && '★'}
                {node.type === 'award' && '🏆'}
              </div>
              <span className="text-[9px] font-bold text-etest-text/70 whitespace-nowrap max-w-[80px] truncate">
                {node.label}
              </span>
            </div>
          )
        })}
      </div>

      <div className="px-8 pb-6 flex items-center gap-6">
        {[
          { color: '#0D9488', label: 'Experience Source' },
          { color: '#7C3AED', label: 'Mentor Guided' },
          { color: '#D97706', label: 'Revision Of' },
        ].map(item => (
          <div key={item.label} className="flex items-center gap-2">
            <div className="w-6 h-0.5 rounded-full" style={{ backgroundColor: item.color }} />
            <span className="text-[10px] font-bold text-etest-hint uppercase tracking-widest">{item.label}</span>
          </div>
        ))}
      </div>
    </div>
  )
}
