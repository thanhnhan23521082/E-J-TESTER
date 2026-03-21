import { useState, useMemo, useCallback } from 'react'
import { useNavigate } from 'react-router-dom'
import { ArrowLeft, Maximize2, Filter, ZoomIn, ZoomOut } from 'lucide-react'
import { MOCK_ARTIFACTS, MOCK_TRACE_LINKS } from '../../data/mock'
import MilestoneDetailPanel from '../../components/etester/MilestoneDetailPanel'
import type { Artifact, TraceLink } from '../../types'

interface GraphNode {
  id: string
  artifactId: string
  label: string
  type: 'experience' | 'draft' | 'final' | 'mentor' | 'test' | 'award' | 'recommendation'
  x: number
  y: number
  color: string
  size: number
  icon: string
}

interface GraphEdge {
  from: string
  to: string
  color: string
  linkType: string
  dashed?: boolean
}

const NODE_MAP: Record<string, string> = {
  camp: 'art_004',
  csr: 'art_005',
  draft1: 'art_003',
  draft2: 'art_002',
  final: 'art_001',
  session5: 'art_007',
  session7: 'art_008',
  ielts: 'art_010',
  award: 'art_006',
  recletter: 'art_009',
  csr2: 'art_012',
}

const NODES: GraphNode[] = [
  { id: 'camp', artifactId: 'art_004', label: 'Writing Camp', type: 'experience', x: 120, y: 120, color: '#0D9488', size: 44, icon: '📝' },
  { id: 'csr', artifactId: 'art_005', label: 'CSR Share & Care', type: 'experience', x: 100, y: 280, color: '#0D9488', size: 40, icon: '💚' },
  { id: 'csr2', artifactId: 'art_012', label: 'Community Outreach', type: 'experience', x: 80, y: 420, color: '#0D9488', size: 36, icon: '🤝' },
  { id: 'draft1', artifactId: 'art_003', label: 'Essay Draft #1', type: 'draft', x: 340, y: 140, color: '#D97706', size: 38, icon: '✏️' },
  { id: 'draft2', artifactId: 'art_002', label: 'Essay Draft #2', type: 'draft', x: 380, y: 280, color: '#D97706', size: 38, icon: '✏️' },
  { id: 'final', artifactId: 'art_001', label: 'PS FINAL', type: 'final', x: 560, y: 220, color: '#BB0016', size: 56, icon: '★' },
  { id: 'session5', artifactId: 'art_007', label: 'Session #5', type: 'mentor', x: 550, y: 80, color: '#7C3AED', size: 36, icon: '🎓' },
  { id: 'session7', artifactId: 'art_008', label: 'Session #7', type: 'mentor', x: 580, y: 380, color: '#7C3AED', size: 36, icon: '🎓' },
  { id: 'ielts', artifactId: 'art_010', label: 'IELTS 6.5', type: 'test', x: 200, y: 420, color: '#64748B', size: 36, icon: '📊' },
  { id: 'award', artifactId: 'art_006', label: 'Writing Award', type: 'award', x: 760, y: 140, color: '#CA8A04', size: 42, icon: '🏆' },
  { id: 'recletter', artifactId: 'art_009', label: 'Rec Letter', type: 'recommendation', x: 760, y: 320, color: '#64748B', size: 36, icon: '📄' },
]

const EDGES: GraphEdge[] = [
  { from: 'camp', to: 'draft1', color: '#0D9488', linkType: 'experience_source' },
  { from: 'csr', to: 'draft1', color: '#0D9488', linkType: 'experience_source' },
  { from: 'draft1', to: 'draft2', color: '#D97706', linkType: 'revision_of' },
  { from: 'draft2', to: 'final', color: '#D97706', linkType: 'revision_of' },
  { from: 'session5', to: 'draft1', color: '#7C3AED', linkType: 'mentor_guided' },
  { from: 'session7', to: 'draft2', color: '#7C3AED', linkType: 'mentor_guided' },
  { from: 'ielts', to: 'final', color: '#64748B', linkType: 'skill_applied', dashed: true },
  { from: 'final', to: 'award', color: '#CA8A04', linkType: 'skill_applied' },
  { from: 'final', to: 'recletter', color: '#64748B', linkType: 'skill_applied', dashed: true },
  { from: 'camp', to: 'csr', color: '#0D9488', linkType: 'experience_source', dashed: true },
]

const MARKER_COLORS: Record<string, string> = {
  '#0D9488': 'teal',
  '#7C3AED': 'purple',
  '#D97706': 'amber',
  '#64748B': 'gray',
  '#CA8A04': 'gold',
  '#BB0016': 'red',
}

type FilterKey = 'all' | 'essay' | 'mentor' | 'test' | 'experience'

const FILTERS: { key: FilterKey; label: string }[] = [
  { key: 'all', label: 'All paths' },
  { key: 'essay', label: 'Essay path' },
  { key: 'mentor', label: 'Mentor guided' },
  { key: 'experience', label: 'Experiences' },
  { key: 'test', label: 'Test progress' },
]

function getNodeById(id: string) {
  return NODES.find(n => n.id === id)
}

function bezierPath(x1: number, y1: number, x2: number, y2: number) {
  const dx = x2 - x1
  const cpx = dx * 0.45
  return `M ${x1} ${y1} C ${x1 + cpx} ${y1}, ${x2 - cpx} ${y2}, ${x2} ${y2}`
}

export default function ArtifactGraphPage() {
  const navigate = useNavigate()
  const [hoveredNode, setHoveredNode] = useState<string | null>(null)
  const [selectedArtifact, setSelectedArtifact] = useState<Artifact | null>(null)
  const [activeFilter, setActiveFilter] = useState<FilterKey>('all')
  const [zoom, setZoom] = useState(1)

  const filteredEdges = useMemo(() => {
    return EDGES.filter(e => {
      if (activeFilter === 'all') return true
      const src = getNodeById(e.from)
      const tgt = getNodeById(e.to)
      if (activeFilter === 'essay') {
        return src?.type === 'draft' || src?.type === 'final' || tgt?.type === 'draft' || tgt?.type === 'final'
      }
      if (activeFilter === 'mentor') return e.linkType === 'mentor_guided'
      if (activeFilter === 'experience') return src?.type === 'experience' || tgt?.type === 'experience'
      if (activeFilter === 'test') return src?.type === 'test' || tgt?.type === 'test'
      return true
    })
  }, [activeFilter])

  const highlightedNodeIds = useMemo(() => {
    if (!hoveredNode) return null
    const ids = new Set([hoveredNode])
    filteredEdges.forEach(e => {
      if (e.from === hoveredNode || e.to === hoveredNode) {
        ids.add(e.from)
        ids.add(e.to)
      }
    })
    return ids
  }, [hoveredNode, filteredEdges])

  const handleNodeClick = useCallback((nodeId: string) => {
    const artifactId = NODE_MAP[nodeId]
    if (!artifactId) return
    const artifact = MOCK_ARTIFACTS.find(a => a.id === artifactId)
    if (artifact) setSelectedArtifact(artifact)
  }, [])

  const selectedTraceLinks: TraceLink[] = useMemo(() => {
    if (!selectedArtifact) return []
    return MOCK_TRACE_LINKS.filter(
      tl => tl.sourceArtifactId === selectedArtifact.id || tl.targetArtifactId === selectedArtifact.id
    )
  }, [selectedArtifact])

  const stats = useMemo(() => ({
    total: NODES.length,
    confirmed: EDGES.filter(e => !e.dashed).length,
    pending: EDGES.filter(e => e.dashed).length,
  }), [])

  return (
    <div className="min-h-screen bg-etest-bg">
      {/* Header */}
      <div className="sticky top-0 z-30 bg-white/80 backdrop-blur-xl border-b border-etest-border/10">
        <div className="max-w-[1400px] mx-auto px-8 h-16 flex items-center justify-between">
          <div className="flex items-center gap-4">
            <button
              onClick={() => navigate('/student/etester')}
              className="h-9 w-9 flex items-center justify-center rounded-xl hover:bg-etest-bg-secondary transition-colors text-etest-hint"
            >
              <ArrowLeft className="w-5 h-5" />
            </button>
            <div>
              <h1 className="text-lg font-bold text-etest-text">Artifact Graph</h1>
              <p className="text-xs text-etest-hint">Full learning journey visualization</p>
            </div>
          </div>

          <div className="flex items-center gap-3">
            <div className="flex items-center gap-4 mr-4 text-xs">
              <span className="text-etest-hint"><strong className="text-etest-text">{stats.total}</strong> nodes</span>
              <span className="text-etest-hint"><strong className="text-etest-green">{stats.confirmed}</strong> confirmed</span>
              <span className="text-etest-hint"><strong className="text-amber-600">{stats.pending}</strong> pending</span>
            </div>

            <div className="flex items-center bg-etest-bg-secondary rounded-xl p-1 gap-1">
              <button
                onClick={() => setZoom(z => Math.max(0.6, z - 0.15))}
                className="h-8 w-8 flex items-center justify-center rounded-lg hover:bg-white text-etest-hint transition-colors"
              >
                <ZoomOut className="w-4 h-4" />
              </button>
              <span className="text-xs font-bold text-etest-text w-10 text-center">{Math.round(zoom * 100)}%</span>
              <button
                onClick={() => setZoom(z => Math.min(1.5, z + 0.15))}
                className="h-8 w-8 flex items-center justify-center rounded-lg hover:bg-white text-etest-hint transition-colors"
              >
                <ZoomIn className="w-4 h-4" />
              </button>
              <button
                onClick={() => setZoom(1)}
                className="h-8 w-8 flex items-center justify-center rounded-lg hover:bg-white text-etest-hint transition-colors"
              >
                <Maximize2 className="w-4 h-4" />
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Filter Bar */}
      <div className="max-w-[1400px] mx-auto px-8 py-4">
        <div className="flex items-center gap-3">
          <Filter className="w-4 h-4 text-etest-hint" />
          <div className="flex gap-1.5 p-1 bg-white rounded-xl shadow-[0_2px_12px_rgba(187,0,22,0.04)]">
            {FILTERS.map(f => (
              <button
                key={f.key}
                onClick={() => setActiveFilter(f.key)}
                className={`px-4 py-2 text-xs font-semibold rounded-lg transition-all ${
                  activeFilter === f.key
                    ? 'bg-etest-red text-white shadow-sm'
                    : 'text-etest-hint hover:text-etest-text hover:bg-etest-bg-secondary'
                }`}
              >
                {f.label}
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Graph Canvas */}
      <div className="max-w-[1400px] mx-auto px-8 pb-8">
        <div className="bg-white rounded-3xl shadow-[0_12px_48px_rgba(187,0,22,0.06)] border border-etest-border/5 overflow-hidden">
          <div
            className="relative w-full transition-transform duration-200 origin-top-left"
            style={{ height: `${520 * zoom}px`, transform: `scale(${zoom})`, transformOrigin: 'top left', width: `${100 / zoom}%` }}
          >
            {/* SVG Edges */}
            <svg className="absolute inset-0 w-full h-full pointer-events-none" xmlns="http://www.w3.org/2000/svg">
              <defs>
                {Object.entries(MARKER_COLORS).map(([hex, name]) => (
                  <marker
                    key={name}
                    id={`arrow-full-${name}`}
                    markerWidth="8"
                    markerHeight="8"
                    refX="10"
                    refY="5"
                    orient="auto-start-reverse"
                    viewBox="0 0 10 10"
                  >
                    <path d="M 0 0 L 10 5 L 0 10 z" fill={hex} />
                  </marker>
                ))}
              </defs>
              {filteredEdges.map((edge, i) => {
                const src = getNodeById(edge.from)
                const tgt = getNodeById(edge.to)
                if (!src || !tgt) return null
                const markerName = MARKER_COLORS[edge.color] || 'gray'
                const dimmed = highlightedNodeIds && (!highlightedNodeIds.has(edge.from) || !highlightedNodeIds.has(edge.to))
                return (
                  <path
                    key={i}
                    d={bezierPath(src.x, src.y, tgt.x, tgt.y)}
                    stroke={edge.color}
                    strokeWidth={edge.dashed ? 1.5 : 2.5}
                    strokeDasharray={edge.dashed ? '8,5' : undefined}
                    fill="none"
                    markerEnd={`url(#arrow-full-${markerName})`}
                    opacity={dimmed ? 0.1 : 0.65}
                    className="transition-opacity duration-300"
                  />
                )
              })}
            </svg>

            {/* Nodes */}
            {NODES.map(node => {
              const dimmed = highlightedNodeIds && !highlightedNodeIds.has(node.id)
              const isHovered = hoveredNode === node.id
              const artifact = MOCK_ARTIFACTS.find(a => a.id === node.artifactId)
              return (
                <div
                  key={node.id}
                  className={`absolute flex flex-col items-center gap-1.5 cursor-pointer transition-all duration-300 ${
                    dimmed ? 'opacity-15 scale-90' : isHovered ? 'opacity-100 scale-110' : 'opacity-100'
                  }`}
                  style={{ left: node.x - node.size / 2, top: node.y - node.size / 2 }}
                  onMouseEnter={() => setHoveredNode(node.id)}
                  onMouseLeave={() => setHoveredNode(null)}
                  onClick={() => handleNodeClick(node.id)}
                >
                  <div
                    className={`rounded-full flex items-center justify-center text-white font-bold shadow-lg border-[3px] border-white transition-shadow duration-300 ${
                      node.type === 'final' ? 'ring-4 ring-etest-red/20' : ''
                    } ${isHovered ? 'shadow-xl' : ''}`}
                    style={{ width: node.size, height: node.size, backgroundColor: node.color }}
                  >
                    <span className="text-sm">{node.icon}</span>
                  </div>
                  <span className="text-[11px] font-bold text-etest-text/80 whitespace-nowrap max-w-[100px] truncate text-center">
                    {node.label}
                  </span>
                  {artifact?.score !== null && artifact?.score !== undefined && (
                    <span className="text-[9px] font-bold text-etest-hint bg-etest-bg-secondary px-2 py-0.5 rounded-full">
                      {artifact.score}pt
                    </span>
                  )}

                  {/* Tooltip on hover */}
                  {isHovered && artifact && (
                    <div className="absolute top-full mt-2 z-20 bg-white rounded-xl shadow-xl border border-etest-border/10 p-3 w-48 pointer-events-none">
                      <p className="text-xs font-bold text-etest-text truncate">{artifact.title}</p>
                      <p className="text-[10px] text-etest-hint mt-0.5">{new Date(artifact.date).toLocaleDateString('vi-VN')}</p>
                      {artifact.authScore !== null && artifact.authScore !== undefined && (
                        <div className="flex items-center gap-1.5 mt-1.5">
                          <div className="w-full h-1.5 bg-etest-bg-secondary rounded-full overflow-hidden">
                            <div className="h-full bg-etest-green rounded-full" style={{ width: `${artifact.authScore}%` }} />
                          </div>
                          <span className="text-[9px] font-bold text-etest-green">{artifact.authScore}%</span>
                        </div>
                      )}
                      <p className="text-[10px] text-etest-blue font-medium mt-1.5">Click to view details</p>
                    </div>
                  )}
                </div>
              )
            })}
          </div>

          {/* Legend */}
          <div className="px-8 py-5 border-t border-etest-border/5 flex flex-wrap items-center gap-x-8 gap-y-2">
            <span className="text-[10px] font-bold text-etest-hint uppercase tracking-widest mr-2">Legend</span>
            {[
              { color: '#0D9488', label: 'Experience Source', dash: false },
              { color: '#7C3AED', label: 'Mentor Guided', dash: false },
              { color: '#D97706', label: 'Revision Of', dash: false },
              { color: '#64748B', label: 'Skill Applied', dash: true },
              { color: '#CA8A04', label: 'Achievement', dash: false },
            ].map(item => (
              <div key={item.label} className="flex items-center gap-2">
                <svg width="24" height="4">
                  <line
                    x1="0" y1="2" x2="24" y2="2"
                    stroke={item.color}
                    strokeWidth="2.5"
                    strokeDasharray={item.dash ? '4,3' : undefined}
                  />
                </svg>
                <span className="text-[10px] font-semibold text-etest-hint">{item.label}</span>
              </div>
            ))}
            <div className="ml-auto flex items-center gap-4">
              {[
                { color: '#0D9488', label: 'Experience' },
                { color: '#D97706', label: 'Draft' },
                { color: '#BB0016', label: 'Final' },
                { color: '#7C3AED', label: 'Mentor' },
                { color: '#64748B', label: 'Test' },
                { color: '#CA8A04', label: 'Award' },
              ].map(item => (
                <div key={item.label} className="flex items-center gap-1.5">
                  <div className="w-3 h-3 rounded-full border-2 border-white shadow-sm" style={{ backgroundColor: item.color }} />
                  <span className="text-[10px] font-semibold text-etest-hint">{item.label}</span>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>

      {/* Side Panel */}
      {selectedArtifact && (
        <MilestoneDetailPanel
          artifact={selectedArtifact}
          traceLinks={selectedTraceLinks}
          onClose={() => setSelectedArtifact(null)}
        />
      )}
    </div>
  )
}
