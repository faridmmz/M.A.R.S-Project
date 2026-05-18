import { useState } from 'react'
import {
  LineChart, Line,
  BarChart, Bar,
  AreaChart, Area,
  XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer,
} from 'recharts'

// Extended history record — App.tsx populates the new fields from /play_turn
export interface HistoryData {
  year: number
  profit: number
  reputation: number
  budget: number
  revenue?: number
  costs?: number
  // Persona demand breakdown
  personaUHNW?: number
  personaGov?: number
  personaResearch?: number
  // Strategic KPIs
  marketPenetration?: number
  cac?: number
  repVulnerability?: number
  // Scenario comparison — always A vs B regardless of which was played
  scenarioAProfit?: number
  scenarioBProfit?: number
  shadowProfit?: number
  scenario?: string
}

interface AnalyticsChartsProps {
  history: HistoryData[]
  marketScenario: 'A' | 'B'
}

const fmt = (v: number) =>
  Math.abs(v) >= 1_000_000
    ? `€${(v / 1_000_000).toFixed(1)}M`
    : `€${v.toLocaleString()}`

const SCENARIO_A_COLOR = '#EF4444'   // red  — current barriers
const SCENARIO_B_COLOR = '#10B981'   // green — evolved market
const NEUTRAL_COLOR    = '#FBBF24'   // amber
const BUDGET_COLOR     = '#3B82F6'   // blue
const UHNW_COLOR       = '#A78BFA'   // violet
const GOV_COLOR        = '#60A5FA'   // sky
const RESEARCH_COLOR   = '#34D399'   // emerald

const tooltipStyle = {
  backgroundColor: '#1F2937',
  border: '1px solid #374151',
  borderRadius: '8px',
}

function KpiCard({
  label,
  value,
  sub,
  accent,
}: {
  label: string
  value: string
  sub?: string
  accent: string
}) {
  return (
    <div className="bg-gray-800 rounded-lg p-4 border border-gray-700 flex flex-col gap-1">
      <span className="text-xs text-gray-400 uppercase tracking-wide">{label}</span>
      <span className={`text-2xl font-bold ${accent}`}>{value}</span>
      {sub && <span className="text-xs text-gray-500">{sub}</span>}
    </div>
  )
}

export default function AnalyticsCharts({ history, marketScenario }: AnalyticsChartsProps) {
  const [showOverlay, setShowOverlay] = useState(false)

  if (history.length === 0) {
    return (
      <div className="p-6 text-center text-gray-400">
        No data yet. Play a turn to see analytics!
      </div>
    )
  }

  // Latest KPIs from the most recent turn
  const latest = history[history.length - 1]
  const latestMarketPen = latest.marketPenetration ?? 0
  const latestCAC = latest.cac ?? 0
  const latestRepVuln = latest.repVulnerability ?? 0
  const currentScenario = marketScenario

  // Build comparison series — use per-turn A/B assignment so colors never flip
  const comparisonData = history.map((h) => ({
    year: h.year,
    scenarioA: h.scenarioAProfit ?? h.profit,
    scenarioB: h.scenarioBProfit ?? h.profit,
  }))

  return (
    <div className="p-6 space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-bold">Analytics Dashboard</h2>
        <div className="flex items-center gap-2">
          <span className="text-sm text-gray-400">Active scenario:</span>
          <span
            className={`text-sm font-bold px-2 py-0.5 rounded ${
              currentScenario === 'A'
                ? 'bg-red-900 text-red-300'
                : 'bg-green-900 text-green-300'
            }`}
          >
            {currentScenario === 'A' ? 'A — Current Market (Barriers)' : 'B — Evolved Market (Elastic)'}
          </span>
        </div>
      </div>

      {/* ── Strategic KPI Cards ─────────────────────────────────────── */}
      <div className="grid grid-cols-3 gap-4">
        <KpiCard
          label="Market Penetration"
          value={`${latestMarketPen.toFixed(1)}%`}
          sub="Customers captured vs. total potential demand"
          accent="text-blue-400"
        />
        <KpiCard
          label="Customer Acquisition Cost"
          value={latestCAC > 0 ? fmt(latestCAC) : '—'}
          sub="Marketing spend per passenger carried"
          accent="text-purple-400"
        />
        <KpiCard
          label="Reputational Vulnerability"
          value={`${latestRepVuln.toFixed(1)}`}
          sub="0 = bulletproof, 100 = brand meltdown risk"
          accent={
            latestRepVuln < 30
              ? 'text-green-400'
              : latestRepVuln < 60
              ? 'text-yellow-400'
              : 'text-red-400'
          }
        />
      </div>

      {/* ── Scenario Comparison (A vs B overlay) ───────────────────── */}
      <div className="bg-gray-800 rounded-lg p-4 border border-gray-700">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h3 className="text-lg font-semibold">Scenario Comparison — Why isn't LEO taking off?</h3>
            <p className="text-xs text-gray-400 mt-0.5">
              Red = Scenario A (current barriers) · Green = Scenario B (evolved elastic market)
            </p>
          </div>
          <button
            onClick={() => setShowOverlay(!showOverlay)}
            className={`px-3 py-1.5 rounded text-sm font-semibold transition-colors ${
              showOverlay
                ? 'bg-green-700 text-green-100'
                : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
            }`}
          >
            {showOverlay ? 'Overlay ON' : 'Overlay OFF'}
          </button>
        </div>
        <ResponsiveContainer width="100%" height={280}>
          <AreaChart data={comparisonData}>
            <defs>
              <linearGradient id="gradA" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor={SCENARIO_A_COLOR} stopOpacity={0.3} />
                <stop offset="95%" stopColor={SCENARIO_A_COLOR} stopOpacity={0} />
              </linearGradient>
              <linearGradient id="gradB" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor={SCENARIO_B_COLOR} stopOpacity={0.3} />
                <stop offset="95%" stopColor={SCENARIO_B_COLOR} stopOpacity={0} />
              </linearGradient>
            </defs>
            <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
            <XAxis dataKey="year" stroke="#9CA3AF" label={{ value: 'Year', position: 'insideBottom', offset: -5, fill: '#9CA3AF' }} />
            <YAxis stroke="#9CA3AF" tickFormatter={fmt} />
            <Tooltip formatter={(v: number) => fmt(v)} contentStyle={tooltipStyle} />
            <Legend />
            <Area
              type="monotone"
              dataKey="scenarioA"
              name="Scenario A (barriers)"
              stroke={SCENARIO_A_COLOR}
              fill="url(#gradA)"
              strokeWidth={2}
              dot={{ r: 3 }}
            />
            {showOverlay && (
              <Area
                type="monotone"
                dataKey="scenarioB"
                name="Scenario B (elastic)"
                stroke={SCENARIO_B_COLOR}
                fill="url(#gradB)"
                strokeWidth={2}
                strokeDasharray="6 3"
                dot={{ r: 3 }}
              />
            )}
          </AreaChart>
        </ResponsiveContainer>
      </div>

      {/* ── Customer Persona Demand Breakdown ──────────────────────── */}
      <div className="bg-gray-800 rounded-lg p-4 border border-gray-700">
        <h3 className="text-lg font-semibold mb-1">Demand by Customer Persona</h3>
        <p className="text-xs text-gray-400 mb-4">
          UHNW Tourists · Government Agencies · Research/Industrial
        </p>
        <ResponsiveContainer width="100%" height={250}>
          <BarChart data={history}>
            <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
            <XAxis dataKey="year" stroke="#9CA3AF" />
            <YAxis stroke="#9CA3AF" tickFormatter={(v) => v.toFixed(1)} />
            <Tooltip
              contentStyle={tooltipStyle}
              formatter={(v: number) => v.toFixed(2)}
            />
            <Legend />
            <Bar dataKey="personaUHNW" name="UHNW Tourists" fill={UHNW_COLOR} stackId="a" />
            <Bar dataKey="personaGov" name="Government" fill={GOV_COLOR} stackId="a" />
            <Bar dataKey="personaResearch" name="Research / Industrial" fill={RESEARCH_COLOR} stackId="a" />
          </BarChart>
        </ResponsiveContainer>
      </div>

      {/* ── Market Penetration % ────────────────────────────────────── */}
      <div className="bg-gray-800 rounded-lg p-4 border border-gray-700">
        <h3 className="text-lg font-semibold mb-4">Market Penetration %</h3>
        <ResponsiveContainer width="100%" height={240}>
          <LineChart data={history}>
            <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
            <XAxis dataKey="year" stroke="#9CA3AF" label={{ value: 'Year', position: 'insideBottom', offset: -5, fill: '#9CA3AF' }} />
            <YAxis stroke="#9CA3AF" domain={[0, 100]} tickFormatter={(v) => `${v}%`} />
            <Tooltip formatter={(v: number) => `${v.toFixed(2)}%`} contentStyle={tooltipStyle} />
            <Legend />
            <Line
              type="monotone"
              dataKey="marketPenetration"
              name="Market Penetration"
              stroke={BUDGET_COLOR}
              strokeWidth={2}
              dot={{ fill: BUDGET_COLOR, r: 4 }}
            />
          </LineChart>
        </ResponsiveContainer>
      </div>

      {/* ── Reputational Vulnerability ──────────────────────────────── */}
      <div className="bg-gray-800 rounded-lg p-4 border border-gray-700">
        <h3 className="text-lg font-semibold mb-1">Reputational Vulnerability</h3>
        <p className="text-xs text-gray-400 mb-4">
          Measures how exposed future demand is to safety incidents or brand decline.
          Keep this low by investing in safety and avoiding failures.
        </p>
        <ResponsiveContainer width="100%" height={240}>
          <LineChart data={history}>
            <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
            <XAxis dataKey="year" stroke="#9CA3AF" label={{ value: 'Year', position: 'insideBottom', offset: -5, fill: '#9CA3AF' }} />
            <YAxis stroke="#9CA3AF" domain={[0, 100]} />
            <Tooltip contentStyle={tooltipStyle} />
            <Legend />
            <Line
              type="monotone"
              dataKey="repVulnerability"
              name="Rep. Vulnerability"
              stroke={SCENARIO_A_COLOR}
              strokeWidth={2}
              dot={{ fill: SCENARIO_A_COLOR, r: 4 }}
            />
          </LineChart>
        </ResponsiveContainer>
      </div>

      {/* ── Profit Over Time ────────────────────────────────────────── */}
      <div className="bg-gray-800 rounded-lg p-4 border border-gray-700">
        <h3 className="text-lg font-semibold mb-4">Profit Over Time</h3>
        <ResponsiveContainer width="100%" height={260}>
          <LineChart data={history}>
            <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
            <XAxis dataKey="year" stroke="#9CA3AF" label={{ value: 'Year', position: 'insideBottom', offset: -5, fill: '#9CA3AF' }} />
            <YAxis stroke="#9CA3AF" tickFormatter={fmt} />
            <Tooltip formatter={(v: number) => fmt(v)} contentStyle={tooltipStyle} />
            <Legend />
            <Line
              type="monotone"
              dataKey="profit"
              name="Profit"
              stroke={SCENARIO_B_COLOR}
              strokeWidth={2}
              dot={{ fill: SCENARIO_B_COLOR, r: 4 }}
            />
          </LineChart>
        </ResponsiveContainer>
      </div>

      {/* ── Reputation Over Time ────────────────────────────────────── */}
      <div className="bg-gray-800 rounded-lg p-4 border border-gray-700">
        <h3 className="text-lg font-semibold mb-4">Reputation Over Time</h3>
        <ResponsiveContainer width="100%" height={240}>
          <LineChart data={history}>
            <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
            <XAxis dataKey="year" stroke="#9CA3AF" label={{ value: 'Year', position: 'insideBottom', offset: -5, fill: '#9CA3AF' }} />
            <YAxis stroke="#9CA3AF" domain={[0, 100]} />
            <Tooltip contentStyle={tooltipStyle} />
            <Legend />
            <Line
              type="monotone"
              dataKey="reputation"
              name="Reputation"
              stroke={NEUTRAL_COLOR}
              strokeWidth={2}
              dot={{ fill: NEUTRAL_COLOR, r: 4 }}
            />
          </LineChart>
        </ResponsiveContainer>
      </div>

      {/* ── Budget Over Time ────────────────────────────────────────── */}
      <div className="bg-gray-800 rounded-lg p-4 border border-gray-700">
        <h3 className="text-lg font-semibold mb-4">Budget Over Time</h3>
        <ResponsiveContainer width="100%" height={240}>
          <LineChart data={history}>
            <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
            <XAxis dataKey="year" stroke="#9CA3AF" label={{ value: 'Year', position: 'insideBottom', offset: -5, fill: '#9CA3AF' }} />
            <YAxis stroke="#9CA3AF" tickFormatter={fmt} />
            <Tooltip formatter={(v: number) => fmt(v)} contentStyle={tooltipStyle} />
            <Legend />
            <Line
              type="monotone"
              dataKey="budget"
              name="Budget"
              stroke={BUDGET_COLOR}
              strokeWidth={2}
              dot={{ fill: BUDGET_COLOR, r: 4 }}
            />
          </LineChart>
        </ResponsiveContainer>
      </div>
    </div>
  )
}
