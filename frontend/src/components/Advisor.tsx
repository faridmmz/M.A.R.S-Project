import { useState } from 'react'

interface GameState {
  budget: number
  reputation: number
  safety_tech_level: number
  vehicles_owned: number
  [key: string]: any
}

interface AdvisorProps {
  gameState: GameState | null
  projectedRisk?: number
}

export default function Advisor({ gameState, projectedRisk }: AdvisorProps) {
  const [dismissed, setDismissed] = useState(false)

  if (!gameState || dismissed) {
    return null
  }

  const tips: string[] = []

  // Check cash reserves
  if (gameState.budget < 50_000_000) {
    tips.push("⚠️ Cash reserves critical. Consider a safe Short Tourist mission.")
  }

  // Check risk level
  if (projectedRisk && projectedRisk > 20) {
    tips.push("⚠️ Risk is high. Increase Safety Investment or switch mission types.")
  }

  // Check reputation
  if (gameState.reputation < 30) {
    tips.push("⚠️ Reputation is low. Focus on successful missions to rebuild trust.")
  }

  // Check safety tech for Long Orbital
  if (gameState.safety_tech_level < 5) {
    tips.push("💡 Invest in Safety Technology to unlock Long Orbital missions (requires Level 5).")
  }

  // Check fleet size
  if (gameState.vehicles_owned === 1) {
    tips.push("💡 Consider expanding your fleet to increase mission capacity.")
  }

  // Check investor interest
  if (gameState.investor_interest >= 80 && gameState.reputation >= 70 && !gameState.investor_funded) {
    tips.push("💰 Investor interest is high! Maintain reputation to trigger funding.")
  }

  if (tips.length === 0) {
    return null
  }

  return (
    <div className="bg-yellow-900/30 border border-yellow-700 rounded-lg p-4 mb-4">
      <div className="flex items-start justify-between">
        <div className="flex-1">
          <div className="flex items-center gap-2 mb-2">
            <span className="text-yellow-400 text-lg">💬</span>
            <h3 className="text-yellow-400 font-semibold">Advisor</h3>
          </div>
          <ul className="space-y-1 text-sm text-yellow-200">
            {tips.map((tip, index) => (
              <li key={index}>{tip}</li>
            ))}
          </ul>
        </div>
        <button
          onClick={() => setDismissed(true)}
          className="text-yellow-400 hover:text-yellow-300 ml-4"
          aria-label="Dismiss advisor"
        >
          ×
        </button>
      </div>
    </div>
  )
}

