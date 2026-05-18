import { useState, useEffect, useRef } from 'react'
import axios from 'axios'
import html2canvas from 'html2canvas'
import {
  BarChart, Bar, LineChart, Line,
  XAxis, YAxis, CartesianGrid, Tooltip, Legend,
  ResponsiveContainer, ReferenceLine,
} from 'recharts'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'

const RUNS = [
  {
    key:   'run_A_status_quo',
    label: 'Run A',
    title: 'Status Quo',
    desc:  'Scenario A · Price floors · No spaceport',
    blurb: 'Structural barriers cap demand to a handful of seats across 10 years. An occasional passenger trickles through, but the market is functionally closed.',
    color: '#EF4444',
    accent: 'text-red-300',
    border: 'border-red-500',
  },
  {
    key:   'run_B_premature_evolved',
    label: 'Run B',
    title: 'Premature Evolved',
    desc:  'Scenario B · −30% pricing · No spaceport',
    blurb: 'Elastic pricing activates partial demand (×1.2 without spaceport). Real passengers, real revenue — but a hard growth ceiling.',
    color: '#F59E0B',
    accent: 'text-amber-300',
    border: 'border-amber-500',
  },
  {
    key:   'run_C_lcc_revolution',
    label: 'Run C',
    title: 'LCC Revolution',
    desc:  'Scenario B · −30% pricing · Spaceport Y3',
    blurb: 'Spaceport lifts elasticity to ×5.5; Reusable Stage 1 pushes to ×6.2. Demand was already there — supply-side infrastructure released it.',
    color: '#10B981',
    accent: 'text-emerald-300',
    border: 'border-emerald-500',
  },
]

interface HistEntry {
  year: number
  profit: number
  reputation: number
  budget: number
  revenue: number
  costs: number
  paxSold: number
  missionSuccess: boolean
  spaceportActive: boolean
  marketPenetration: number
}

interface RunPayload {
  label: string
  description: string
  market_scenario: 'A' | 'B'
  history: HistEntry[]
  final_score: Record<string, number | string | boolean | Record<string, boolean>>
  financial_metrics: Record<string, number | string>
}

const fmt = (v: number) =>
  Math.abs(v) >= 1e9 ? `€${(v / 1e9).toFixed(2)}B`
  : Math.abs(v) >= 1e6 ? `€${(v / 1e6).toFixed(0)}M`
  : `€${v.toLocaleString()}`

const fmtAxis = (v: number) =>
  Math.abs(v) >= 1e9 ? `${(v / 1e9).toFixed(1)}B`
  : Math.abs(v) >= 1e6 ? `${(v / 1e6).toFixed(0)}M`
  : `${v}`

const tooltipStyle = {
  backgroundColor: '#111827',
  border: '1px solid #374151',
  borderRadius: '10px',
  color: '#F9FAFB',
  fontSize: 12,
}

const CHART_H = 230

export default function PlaythroughViewer() {
  const [payloads, setPayloads]     = useState<(RunPayload | null)[]>([null, null, null])
  const [loading, setLoading]       = useState(true)
  const [error, setError]           = useState<string | null>(null)
  const [downloading, setDownloading] = useState(false)
  const contentRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    Promise.all(
      RUNS.map(r =>
        axios.get<RunPayload>(`${API_BASE_URL}/load_run/${r.key}`)
          .then(res => res.data)
          .catch(() => null)
      )
    ).then(results => {
      if (results.every(r => r === null))
        setError('No run data found. Run the playthrough script first.')
      setPayloads(results)
      setLoading(false)
    })
  }, [])

  const handleDownload = async () => {
    if (!contentRef.current) return
    setDownloading(true)
    try {
      const canvas = await html2canvas(contentRef.current, {
        backgroundColor: '#111827',
        scale: 2,
        useCORS: true,
        logging: false,
      })
      const link = document.createElement('a')
      link.download = `MARS_Playthrough_Results_${new Date().toISOString().slice(0, 10)}.png`
      link.href = canvas.toDataURL('image/png')
      link.click()
    } finally {
      setDownloading(false)
    }
  }

  /* ── Chart data ───────────────────────────────────────────────── */
  const numTurns = payloads[0]?.history.slice(1).length ?? 10

  const paxData = Array.from({ length: numTurns }, (_, i) => ({
    year: `Y${i + 1}`,
    'Run A': payloads[0]?.history[i + 1]?.paxSold ?? 0,
    'Run B': payloads[1]?.history[i + 1]?.paxSold ?? 0,
    'Run C': payloads[2]?.history[i + 1]?.paxSold ?? 0,
  }))

  const revenueData = Array.from({ length: numTurns }, (_, i) => ({
    year: `Y${i + 1}`,
    'Run A': Math.round((payloads[0]?.history[i + 1]?.revenue ?? 0) / 1e6),
    'Run B': Math.round((payloads[1]?.history[i + 1]?.revenue ?? 0) / 1e6),
    'Run C': Math.round((payloads[2]?.history[i + 1]?.revenue ?? 0) / 1e6),
  }))

  const profitData = Array.from({ length: numTurns }, (_, i) => ({
    year: `Y${i + 1}`,
    'Run A': Math.round((payloads[0]?.history[i + 1]?.profit ?? 0) / 1e6),
    'Run B': Math.round((payloads[1]?.history[i + 1]?.profit ?? 0) / 1e6),
    'Run C': Math.round((payloads[2]?.history[i + 1]?.profit ?? 0) / 1e6),
  }))

  const budgetData = Array.from({ length: numTurns + 1 }, (_, i) => ({
    year: i === 0 ? 'Start' : `Y${i}`,
    'Run A': +((payloads[0]?.history[i]?.budget ?? 0) / 1e9).toFixed(3),
    'Run B': +((payloads[1]?.history[i]?.budget ?? 0) / 1e9).toFixed(3),
    'Run C': +((payloads[2]?.history[i]?.budget ?? 0) / 1e9).toFixed(3),
  }))

  /* ── Loading / error ──────────────────────────────────────────── */
  if (loading) return (
    <div className="flex items-center justify-center h-64 gap-3 text-gray-400">
      <div className="w-5 h-5 border-2 border-gray-500 border-t-blue-400 rounded-full animate-spin" />
      Loading all three runs…
    </div>
  )

  if (error) return (
    <div className="p-8 flex justify-center">
      <div className="bg-red-900/40 border border-red-700 rounded-xl p-6 text-red-300 max-w-lg text-center">
        <div className="font-bold text-lg mb-2">Run data not found</div>
        <div className="text-sm mb-3">{error}</div>
        <code className="text-xs bg-red-950 px-2 py-1 rounded">
          cd backend &amp;&amp; python run_playthroughs.py
        </code>
      </div>
    </div>
  )

  /* ── KPI row data ─────────────────────────────────────────────── */
  const fms = payloads.map(p => p?.financial_metrics)

  const maxPax    = Math.max(...fms.map(fm => (fm?.total_passengers          as number) ?? 0), 1)
  const maxRev    = Math.max(...fms.map(fm => (fm?.total_revenue             as number) ?? 0), 1)
  const minNpv    = Math.min(...fms.map(fm => (fm?.npv                       as number) ?? 0))
  const maxCac    = Math.max(...fms.map(fm => (fm?.customer_acquisition_cost as number) ?? 0), 1)
  const minRoi    = Math.min(...fms.map(fm => (fm?.roi                       as number) ?? 0), -1)

  const kpiRows: {
    label: string
    sub: string
    vals: (number | null)[]
    fmt: (v: number) => string
    pct: (v: number) => number
    barColor: (v: number) => string
    note?: string
  }[] = [
    {
      label: 'Passengers Carried',
      sub: 'total across 10 years',
      vals: fms.map(fm => (fm?.total_passengers as number) ?? null),
      fmt: v => `${v} pax`,
      pct: v => Math.min(100, (v / maxPax) * 100),
      barColor: v => v === 0 ? '#1F2937' : v === maxPax ? '#10B981' : '#F59E0B',
    },
    {
      label: 'Total Revenue',
      sub: 'mission revenue earned',
      vals: fms.map(fm => (fm?.total_revenue as number) ?? null),
      fmt: v => fmt(v),
      pct: v => Math.min(100, (v / maxRev) * 100),
      barColor: v => v === 0 ? '#1F2937' : v === maxRev ? '#10B981' : '#F59E0B',
    },
    {
      label: 'NPV (5% discount rate)',
      sub: 'higher = less value destroyed',
      vals: fms.map(fm => (fm?.npv as number) ?? null),
      fmt: v => fmt(v),
      pct: v => Math.min(100, ((v - minNpv) / (Math.abs(minNpv) || 1)) * 100),
      barColor: () => '#6366F1',
    },
    {
      label: 'Return on Investment (ROI)',
      sub: 'profit ÷ investment — all runs pre-breakeven',
      vals: fms.map(fm => (fm?.roi as number) ?? null),
      fmt: v => `${v.toFixed(1)}%`,
      pct: v => Math.min(100, (Math.abs(v) / Math.abs(minRoi)) * 100),
      barColor: v => Math.abs(v) >= Math.abs(minRoi) * 0.98 ? '#EF4444' : Math.abs(v) <= Math.abs(minRoi) * 0.85 ? '#10B981' : '#F59E0B',
    },
    {
      label: 'Customer Acquisition Cost',
      sub: 'marketing spend ÷ passengers — lower is better',
      vals: fms.map(fm => (fm?.customer_acquisition_cost as number) ?? null),
      fmt: v => v >= 1e9 ? `€${(v/1e9).toFixed(1)}B` : v >= 1e6 ? `€${(v/1e6).toFixed(1)}M` : `€${v.toLocaleString()}`,
      pct: v => Math.min(100, (v / maxCac) * 100),
      barColor: v => v === maxCac ? '#EF4444' : v <= maxCac * 0.15 ? '#10B981' : '#F59E0B',
    },
  ]

  /* ── Main render ──────────────────────────────────────────────── */
  return (
    <div className="p-6">

      {/* ── Sticky toolbar (outside captured area) ────────────────── */}
      <div className="flex items-center justify-between mb-5">
        <div>
          <h2 className="text-xl font-bold text-white">Three-Run Validation Model</h2>
          <p className="text-gray-400 text-sm mt-0.5">
            Identical investments · same RNG seed · only market scenario and spaceport differ
          </p>
        </div>
        <button
          onClick={handleDownload}
          disabled={downloading}
          className="flex items-center gap-2 px-4 py-2 bg-blue-600 hover:bg-blue-500 disabled:bg-gray-700 disabled:text-gray-500 text-white font-semibold rounded-lg transition-colors text-sm"
        >
          {downloading ? (
            <>
              <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
              Capturing…
            </>
          ) : (
            <>
              <svg className="w-4 h-4" fill="none" stroke="currentColor" strokeWidth={2} viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
              </svg>
              Download PNG
            </>
          )}
        </button>
      </div>

      {/* ── Captured content ──────────────────────────────────────── */}
      <div ref={contentRef} className="space-y-6 bg-gray-900 p-2 rounded-xl">

        {/* Legend strip */}
        <div className="flex flex-wrap gap-5 px-1">
          {RUNS.map(r => (
            <div key={r.key} className="flex items-center gap-2 text-sm">
              <span className="w-3 h-3 rounded-full shrink-0" style={{ backgroundColor: r.color }} />
              <span className="font-bold text-white">{r.label}</span>
              <span className="text-gray-400">{r.title}</span>
              <span className="text-gray-600 text-xs">— {r.desc}</span>
            </div>
          ))}
        </div>

        {/* ── KPI comparison table ──────────────────────────────── */}
        <div className="bg-gray-800 rounded-xl border border-gray-700 p-5">
          <div className="mb-4">
            <h4 className="font-semibold text-white">10-Year Outcome Comparison</h4>
            <p className="text-xs text-gray-500 mt-0.5">
              Market scenario and spaceport are the only variables — all investment levels are identical across runs
            </p>
          </div>

          {/* Column headers */}
          <div className="grid grid-cols-[180px_1fr_1fr_1fr] gap-4 mb-4">
            <div />
            {RUNS.map((r, i) => (
              <div key={r.key} className="flex items-center gap-2">
                <span className="w-2.5 h-2.5 rounded-full shrink-0" style={{ backgroundColor: r.color }} />
                <div>
                  <div className="text-sm font-bold text-white">{r.label}</div>
                  <div className="text-xs text-gray-500">{r.title}</div>
                  {i > 0 && <div className="text-xs text-gray-600 mt-0.5">Δ vs Run A</div>}
                </div>
              </div>
            ))}
          </div>

          <div className="space-y-5">
            {kpiRows.map(row => {
              const baseVal = row.vals[0] ?? 0
              return (
                <div key={row.label}>
                  <div className="text-xs text-gray-400 font-medium mb-2">
                    {row.label}
                    <span className="text-gray-600 ml-1.5">· {row.sub}</span>
                  </div>
                  <div className="grid grid-cols-[180px_1fr_1fr_1fr] gap-4 items-center">
                    <div />
                    {row.vals.map((v, i) => {
                      if (v === null) return <div key={i} className="text-gray-600 text-sm">—</div>
                      const delta = i > 0 ? v - baseVal : null
                      return (
                        <div key={i}>
                          <div className="flex items-baseline gap-2 mb-1.5">
                            <span className="text-sm font-bold text-white">{row.fmt(v)}</span>
                            {delta !== null && delta !== 0 && (
                              <span className={`text-xs font-semibold ${delta > 0 ? 'text-emerald-400' : 'text-red-400'}`}>
                                {delta > 0 ? '+' : ''}{row.fmt(delta)}
                              </span>
                            )}
                            {delta !== null && delta === 0 && (
                              <span className="text-xs text-gray-600">same</span>
                            )}
                          </div>
                          <div className="h-2 bg-gray-700 rounded-full overflow-hidden">
                            <div
                              className="h-full rounded-full"
                              style={{ width: `${row.pct(v)}%`, backgroundColor: row.barColor(v) }}
                            />
                          </div>
                        </div>
                      )
                    })}
                  </div>
                  {row.note && (
                    <p className="text-xs text-gray-600 italic mt-1.5">{row.note}</p>
                  )}
                </div>
              )
            })}
          </div>
        </div>

        {/* ── Charts 2×2 ────────────────────────────────────────── */}
        <div className="grid grid-cols-2 gap-5">

          <div className="bg-gray-800 rounded-xl border border-gray-700 p-5">
            <h4 className="font-semibold text-white mb-0.5">Passengers per Turn</h4>
            <p className="text-xs text-gray-500 mb-3">Capacity cap: 7 pax/turn · Run A barely registers (4 pax/decade) vs Run C hitting the cap</p>
            <ResponsiveContainer width="100%" height={CHART_H}>
              <BarChart data={paxData} barCategoryGap="20%" barGap={2}>
                <CartesianGrid strokeDasharray="3 3" stroke="#1F2937" />
                <XAxis dataKey="year" stroke="#4B5563" tick={{ fontSize: 11 }} />
                <YAxis domain={[0, 7]} stroke="#4B5563" tick={{ fontSize: 11 }} ticks={[0,1,2,3,4,5,6,7]} />
                <Tooltip contentStyle={tooltipStyle} formatter={(v: number) => [`${v} pax`, '']} />
                <Legend wrapperStyle={{ fontSize: 12 }} />
                <Bar dataKey="Run A" fill={RUNS[0].color} opacity={0.85} radius={[3,3,0,0]} />
                <Bar dataKey="Run B" fill={RUNS[1].color} opacity={0.85} radius={[3,3,0,0]} />
                <Bar dataKey="Run C" fill={RUNS[2].color} opacity={0.85} radius={[3,3,0,0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>

          <div className="bg-gray-800 rounded-xl border border-gray-700 p-5">
            <h4 className="font-semibold text-white mb-0.5">Annual Revenue</h4>
            <p className="text-xs text-gray-500 mb-3">€M · Run A barely generates revenue — structural barriers crush conversion rate</p>
            <ResponsiveContainer width="100%" height={CHART_H}>
              <LineChart data={revenueData}>
                <CartesianGrid strokeDasharray="3 3" stroke="#1F2937" />
                <XAxis dataKey="year" stroke="#4B5563" tick={{ fontSize: 11 }} />
                <YAxis stroke="#4B5563" tick={{ fontSize: 11 }} tickFormatter={v => `€${fmtAxis(v * 1e6)}`} />
                <Tooltip contentStyle={tooltipStyle} formatter={(v: number) => [`€${v}M`, '']} />
                <Legend wrapperStyle={{ fontSize: 12 }} />
                <Line type="monotone" dataKey="Run A" stroke={RUNS[0].color} strokeWidth={2} dot={{ r: 3, fill: RUNS[0].color }} />
                <Line type="monotone" dataKey="Run B" stroke={RUNS[1].color} strokeWidth={2} dot={{ r: 3, fill: RUNS[1].color }} />
                <Line type="monotone" dataKey="Run C" stroke={RUNS[2].color} strokeWidth={2} dot={{ r: 3, fill: RUNS[2].color }} />
              </LineChart>
            </ResponsiveContainer>
          </div>

          <div className="bg-gray-800 rounded-xl border border-gray-700 p-5">
            <h4 className="font-semibold text-white mb-0.5">Budget Trajectory</h4>
            <p className="text-xs text-gray-500 mb-3">€B · Run C dips in Y3 for the €300M spaceport capex</p>
            <ResponsiveContainer width="100%" height={CHART_H}>
              <LineChart data={budgetData}>
                <CartesianGrid strokeDasharray="3 3" stroke="#1F2937" />
                <XAxis dataKey="year" stroke="#4B5563" tick={{ fontSize: 11 }} />
                <YAxis stroke="#4B5563" tick={{ fontSize: 11 }} tickFormatter={v => `${v.toFixed(1)}B`} />
                <Tooltip contentStyle={tooltipStyle} formatter={(v: number) => [`€${v.toFixed(2)}B`, '']} />
                <Legend wrapperStyle={{ fontSize: 12 }} />
                <Line type="monotone" dataKey="Run A" stroke={RUNS[0].color} strokeWidth={2} dot={false} />
                <Line type="monotone" dataKey="Run B" stroke={RUNS[1].color} strokeWidth={2} dot={false} />
                <Line type="monotone" dataKey="Run C" stroke={RUNS[2].color} strokeWidth={2} dot={false} strokeDasharray="6 3" />
              </LineChart>
            </ResponsiveContainer>
          </div>

          <div className="bg-gray-800 rounded-xl border border-gray-700 p-5">
            <h4 className="font-semibold text-white mb-0.5">Annual Profit / Loss</h4>
            <p className="text-xs text-gray-500 mb-3">€M · all runs are pre-breakeven — Run C closes gap fastest</p>
            <ResponsiveContainer width="100%" height={CHART_H}>
              <LineChart data={profitData}>
                <CartesianGrid strokeDasharray="3 3" stroke="#1F2937" />
                <XAxis dataKey="year" stroke="#4B5563" tick={{ fontSize: 11 }} />
                <YAxis stroke="#4B5563" tick={{ fontSize: 11 }} tickFormatter={v => `€${v}M`} />
                <Tooltip contentStyle={tooltipStyle} formatter={(v: number) => [`€${v}M`, '']} />
                <Legend wrapperStyle={{ fontSize: 12 }} />
                <ReferenceLine y={0} stroke="#6B7280" strokeDasharray="4 2" label={{ value: 'break-even', position: 'insideTopRight', fill: '#6B7280', fontSize: 10 }} />
                <Line type="monotone" dataKey="Run A" stroke={RUNS[0].color} strokeWidth={2} dot={{ r: 3, fill: RUNS[0].color }} />
                <Line type="monotone" dataKey="Run B" stroke={RUNS[1].color} strokeWidth={2} dot={{ r: 3, fill: RUNS[1].color }} />
                <Line type="monotone" dataKey="Run C" stroke={RUNS[2].color} strokeWidth={2} dot={{ r: 3, fill: RUNS[2].color }} />
              </LineChart>
            </ResponsiveContainer>
          </div>

        </div>

        {/* ── Insight row ───────────────────────────────────────── */}
        <div className="grid grid-cols-3 gap-4">
          {RUNS.map(r => (
            <div key={r.key} className={`rounded-xl border ${r.border} bg-gray-800/40 p-4 flex gap-3`}>
              <span className="w-2.5 h-2.5 rounded-full mt-1 shrink-0" style={{ backgroundColor: r.color }} />
              <div>
                <div className={`font-semibold text-sm mb-1 ${r.accent}`}>{r.label} — {r.title}</div>
                <div className="text-xs text-gray-400 leading-relaxed">{r.blurb}</div>
              </div>
            </div>
          ))}
        </div>

      </div>{/* end captured area */}
    </div>
  )
}
