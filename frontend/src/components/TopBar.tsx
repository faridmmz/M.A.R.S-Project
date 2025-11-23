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
    tech_unlocks?: {
      reusable_stage1: boolean
      green_hydrogen: boolean
    }
  }
}

export default function TopBar({ gameState }: TopBarProps) {
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
        <h1 className="text-2xl font-bold text-blue-400">M.A.R.S. Project</h1>
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
        </div>
      </div>
    </div>
  )
}

