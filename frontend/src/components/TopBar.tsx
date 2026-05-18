import { useState } from 'react'

interface TopBarProps {
  gameState: {
    budget: number
    reputation: number
    year: number
    tech_level: number
    green_tech_level: number
    safety_tech_level?: number
    co2_impact: number
    hr_efficiency?: number
    has_spaceport?: boolean
    spaceport_building?: boolean
    tech_unlocks?: {
      reusable_stage1: boolean
      green_hydrogen: boolean
    }
  }
  marketScenario: 'A' | 'B'
  onScenarioChange: (s: 'A' | 'B') => void
}

const SCENARIO_INFO = {
  A: {
    label: 'A · Barriers',
    color: 'red',
    headline: 'Current Market Reality',
    icon: '🚧',
    tagline: 'Structural barriers cap demand',
    bullets: [
      { icon: '💸', text: 'Demand hard-capped — price drops don\'t unlock new buyers' },
      { icon: '🏛️', text: 'Regulatory & infrastructure friction blocks growth' },
      { icon: '🎯', text: 'Only ultra-HNW individuals & gov agencies can access LEO' },
      { icon: '📉', text: 'Market share is zero-sum with SpaceX, Blue Origin & Axiom' },
    ],
    question: 'Can you survive in a structurally limited market?',
    bg: 'from-red-950/90 to-gray-900/95',
    border: 'border-red-700/60',
    accent: 'text-red-400',
    tag: 'bg-red-900/50 text-red-300',
  },
  B: {
    label: 'B · Elastic',
    color: 'green',
    headline: 'Evolved Market Opportunity',
    icon: '🚀',
    tagline: 'Elastic demand scales with price drops',
    bullets: [
      { icon: '📈', text: 'Price reductions unlock exponentially more demand' },
      { icon: '🌍', text: 'New customer segments emerge as access widens' },
      { icon: '🔬', text: 'R&D tourism, science missions & industry all scale' },
      { icon: '🤝', text: 'Market grows faster than competition can absorb it' },
    ],
    question: 'Can you capture the LEO boom before rivals do?',
    bg: 'from-green-950/90 to-gray-900/95',
    border: 'border-green-700/60',
    accent: 'text-green-400',
    tag: 'bg-green-900/50 text-green-300',
  },
}

function ScenarioTooltip({ scenario }: { scenario: 'A' | 'B' }) {
  const info = SCENARIO_INFO[scenario]
  return (
    <div
      className={`absolute top-full left-1/2 -translate-x-1/2 mt-3 w-72 rounded-xl border ${info.border} bg-gradient-to-br ${info.bg} backdrop-blur-sm shadow-2xl z-50 p-4 pointer-events-none`}
      style={{ filter: 'drop-shadow(0 0 18px rgba(0,0,0,0.7))' }}
    >
      {/* Arrow */}
      <div className={`absolute -top-2 left-1/2 -translate-x-1/2 w-3 h-3 rotate-45 border-l border-t ${info.border} bg-gray-900`} />

      {/* Header */}
      <div className="flex items-start gap-2 mb-3">
        <span className="text-2xl shrink-0 mt-0.5">{info.icon}</span>
        <div className="flex-1 min-w-0">
          <div className={`text-sm font-bold leading-tight ${info.accent}`}>{info.headline}</div>
          <div className="text-xs text-gray-400 mt-0.5">{info.tagline}</div>
        </div>
        <span className={`shrink-0 text-xs font-bold px-2.5 py-1 rounded-lg whitespace-nowrap ${info.tag}`}>
          Scenario {scenario}
        </span>
      </div>

      {/* Divider */}
      <div className={`h-px mb-3 bg-gradient-to-r from-transparent via-${info.color}-700/50 to-transparent`} />

      {/* Bullets */}
      <ul className="space-y-1.5 mb-3">
        {info.bullets.map((b, i) => (
          <li key={i} className="flex items-start gap-2 text-xs text-gray-300">
            <span className="shrink-0 mt-0.5">{b.icon}</span>
            <span>{b.text}</span>
          </li>
        ))}
      </ul>

      {/* Footer question */}
      <div className={`text-xs font-semibold italic text-center ${info.accent} border-t ${info.border} pt-2.5`}>
        ✦ &nbsp;{info.question}&nbsp; ✦
      </div>
    </div>
  )
}

export default function TopBar({ gameState, marketScenario, onScenarioChange }: TopBarProps) {
  const [hoveredScenario, setHoveredScenario] = useState<'A' | 'B' | null>(null)

  const formatCurrency = (amount: number) => {
    if (amount >= 1_000_000_000) {
      return `€${(amount / 1_000_000_000).toFixed(2)}B`
    } else if (amount >= 1_000_000) {
      return `€${(amount / 1_000_000).toFixed(0)}M`
    } else {
      return `€${amount.toLocaleString()}`
    }
  }

  return (
    <div className="bg-gray-800 border-b border-gray-700 px-6 py-4">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-4">
          <div className="flex items-center gap-2">
            <img src="/politorbital_logo.png" alt="PoliTOrbital" className="h-8 w-auto" />
            <h1 className="text-2xl font-bold text-blue-400">M.A.R.S. Project</h1>
          </div>

          {/* Scenario toggle */}
          <div className="flex items-center gap-1.5 bg-gray-700 rounded-lg p-1 border border-gray-600">
            <span className="text-xs text-gray-400 px-1">Scenario:</span>

            {(['A', 'B'] as const).map((s) => (
              <div key={s} className="relative">
                <button
                  onClick={() => onScenarioChange(s)}
                  onMouseEnter={() => setHoveredScenario(s)}
                  onMouseLeave={() => setHoveredScenario(null)}
                  className={`px-3 py-1 rounded text-xs font-bold transition-colors ${
                    marketScenario === s
                      ? s === 'A'
                        ? 'bg-red-600 text-white shadow'
                        : 'bg-green-600 text-white shadow'
                      : 'text-gray-400 hover:text-white'
                  }`}
                >
                  {SCENARIO_INFO[s].label}
                </button>
                {hoveredScenario === s && <ScenarioTooltip scenario={s} />}
              </div>
            ))}
          </div>
        </div>

        <div className="flex gap-8 items-center">
          <div className="text-center">
            <div className="text-sm text-gray-400">Year</div>
            <div className="text-xl font-bold">{gameState.year}</div>
          </div>
          <div className="text-center">
            <div className="text-sm text-gray-400">Budget</div>
            <div className="text-xl font-bold text-green-400">{formatCurrency(gameState.budget)}</div>
          </div>
          <div className="text-center">
            <div className="text-sm text-gray-400">Reputation</div>
            <div className="text-xl font-bold text-yellow-400">{gameState.reputation.toFixed(1)}/100</div>
          </div>
          <div className="text-center">
            <div className="text-sm text-gray-400">Tech Level</div>
            <div className="text-xl font-bold text-purple-400">{gameState.tech_level}</div>
          </div>
          <div className="text-center">
            <div className="text-sm text-gray-400">Green Tech</div>
            <div className="text-xl font-bold text-emerald-400">{gameState.green_tech_level}</div>
          </div>
          {gameState.safety_tech_level !== undefined && (
            <div className="text-center">
              <div className="text-sm text-gray-400">Safety Tech</div>
              <div className="text-xl font-bold text-orange-400">{gameState.safety_tech_level}</div>
            </div>
          )}
          {gameState.hr_efficiency !== undefined && (
            <div className="text-center">
              <div className="text-sm text-gray-400">Staff Efficiency</div>
              <div className="text-xl font-bold text-cyan-400">{(gameState.hr_efficiency * 100).toFixed(0)}%</div>
            </div>
          )}
          <div className="text-center">
            <div className="text-sm text-gray-400">CO2 Impact</div>
            <div className="text-xl font-bold text-red-400">{gameState.co2_impact.toFixed(1)}</div>
          </div>
          {/* Spaceport status pill */}
          {gameState.spaceport_building && (
            <div className="text-center">
              <div className="text-sm text-gray-400">Spaceport</div>
              <div className="text-sm font-bold text-blue-400 animate-pulse">🏗️ Building…</div>
            </div>
          )}
          {gameState.has_spaceport && !gameState.spaceport_building && (
            <div className="text-center">
              <div className="text-sm text-gray-400">Spaceport</div>
              <div className="text-sm font-bold text-green-400">🚀 Active</div>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
