interface FinalScore {
  years_played: number
  final_budget: number
  starting_budget: number
  budget_change: number
  budget_change_pct: number
  final_reputation: number
  total_profit: number
  avg_profit_per_year: number
  total_co2: number
  co2_per_year: number
  tech_level: number
  green_tech_level: number
  tech_unlocks: {
    reusable_stage1: boolean
    green_hydrogen: boolean
  }
  economic_score: number
  economic_grade: string
  green_score: number
  green_grade: string
  final_score: number
  final_grade: string
}

interface WinScreenProps {
  score: FinalScore
  gameOverReason: 'max_years' | 'bankruptcy'
  onClose: () => void
  onRestart: () => void
}

export default function WinScreen({ score, gameOverReason, onClose, onRestart }: WinScreenProps) {
  const formatCurrency = (amount: number) => {
    if (amount >= 1_000_000_000) {
      return `€${(amount / 1_000_000_000).toFixed(2)}B`
    } else if (amount >= 1_000_000) {
      return `€${(amount / 1_000_000).toFixed(1)}M`
    } else {
      return `€${amount.toLocaleString()}`
    }
  }

  const getGradeColor = (grade: string) => {
    if (grade.startsWith('A')) return 'text-green-400'
    if (grade.startsWith('B')) return 'text-blue-400'
    if (grade.startsWith('C')) return 'text-yellow-400'
    if (grade.startsWith('D')) return 'text-orange-400'
    return 'text-red-400'
  }

  const isBankruptcy = gameOverReason === 'bankruptcy'

  return (
    <div className="fixed inset-0 bg-black bg-opacity-75 flex items-center justify-center z-50 p-4">
      <div className="bg-gray-800 rounded-lg p-8 max-w-4xl w-full max-h-[90vh] overflow-y-auto border border-gray-700">
        <div className="text-center mb-6">
          {isBankruptcy ? (
            <>
              <h1 className="text-4xl font-bold text-red-400 mb-2">Game Over</h1>
              <p className="text-xl text-gray-300">Bankruptcy</p>
            </>
          ) : (
            <>
              <h1 className="text-4xl font-bold text-green-400 mb-2">Game Complete!</h1>
              <p className="text-xl text-gray-300">Final Results</p>
            </>
          )}
        </div>

        {/* Final Score */}
        <div className="bg-gradient-to-r from-blue-600 to-purple-600 rounded-lg p-6 mb-6 text-center">
          <div className="text-sm text-gray-200 mb-2">Final Score</div>
          <div className={`text-6xl font-bold ${getGradeColor(score.final_grade)} mb-2`}>
            {score.final_grade}
          </div>
          <div className="text-2xl text-gray-200">{score.final_score.toFixed(1)}/100</div>
        </div>

        {/* Score Breakdown */}
        <div className="grid grid-cols-2 gap-4 mb-6">
          {/* Economic Score */}
          <div className="bg-gray-700 rounded-lg p-4 border border-gray-600">
            <div className="text-sm text-gray-400 mb-2">Economic Score</div>
            <div className={`text-4xl font-bold ${getGradeColor(score.economic_grade)} mb-1`}>
              {score.economic_grade}
            </div>
            <div className="text-lg text-gray-300">{score.economic_score.toFixed(1)}/100</div>
            <div className="mt-3 text-xs text-gray-400 space-y-1">
              <div>Budget: {formatCurrency(score.final_budget)}</div>
              <div>Reputation: {score.final_reputation.toFixed(1)}/100</div>
              <div>Avg Profit/Year: {formatCurrency(score.avg_profit_per_year)}</div>
            </div>
          </div>

          {/* Green Score */}
          <div className="bg-gray-700 rounded-lg p-4 border border-gray-600">
            <div className="text-sm text-gray-400 mb-2">Green Score</div>
            <div className={`text-4xl font-bold ${getGradeColor(score.green_grade)} mb-1`}>
              {score.green_grade}
            </div>
            <div className="text-lg text-gray-300">{score.green_score.toFixed(1)}/100</div>
            <div className="mt-3 text-xs text-gray-400 space-y-1">
              <div>CO2/Year: {score.co2_per_year.toFixed(1)}</div>
              <div>Green Tech: Level {score.green_tech_level}</div>
              <div>Tech Unlocks: {Object.values(score.tech_unlocks).filter(Boolean).length}/2</div>
            </div>
          </div>
        </div>

        {/* Detailed Stats */}
        <div className="bg-gray-700 rounded-lg p-4 mb-6">
          <h3 className="font-semibold mb-3">Performance Summary</h3>
          <div className="grid grid-cols-2 gap-4 text-sm">
            <div>
              <div className="text-gray-400">Years Played</div>
              <div className="text-lg font-semibold">{score.years_played}</div>
            </div>
            <div>
              <div className="text-gray-400">Budget Change</div>
              <div className={`text-lg font-semibold ${score.budget_change >= 0 ? 'text-green-400' : 'text-red-400'}`}>
                {formatCurrency(score.budget_change)} ({score.budget_change_pct >= 0 ? '+' : ''}{score.budget_change_pct.toFixed(1)}%)
              </div>
            </div>
            <div>
              <div className="text-gray-400">Total Profit</div>
              <div className={`text-lg font-semibold ${score.total_profit >= 0 ? 'text-green-400' : 'text-red-400'}`}>
                {formatCurrency(score.total_profit)}
              </div>
            </div>
            <div>
              <div className="text-gray-400">Total CO2 Impact</div>
              <div className="text-lg font-semibold text-red-400">
                {score.total_co2.toFixed(1)}
              </div>
            </div>
            <div>
              <div className="text-gray-400">R&D Level</div>
              <div className="text-lg font-semibold text-purple-400">
                {score.tech_level}
              </div>
            </div>
            <div>
              <div className="text-gray-400">Green Tech Level</div>
              <div className="text-lg font-semibold text-emerald-400">
                {score.green_tech_level}
              </div>
            </div>
          </div>
        </div>

        {/* Tech Unlocks */}
        {Object.values(score.tech_unlocks).some(Boolean) && (
          <div className="bg-gray-700 rounded-lg p-4 mb-6">
            <h3 className="font-semibold mb-3">Technologies Unlocked</h3>
            <div className="space-y-2">
              {score.tech_unlocks.reusable_stage1 && (
                <div className="flex items-center gap-2 text-sm">
                  <span className="text-green-400">✓</span>
                  <span>Reusable Stage 1 - Launch costs reduced by 20%</span>
                </div>
              )}
              {score.tech_unlocks.green_hydrogen && (
                <div className="flex items-center gap-2 text-sm">
                  <span className="text-green-400">✓</span>
                  <span>Green Hydrogen - CO2 emissions reduced by 50%</span>
                </div>
              )}
            </div>
          </div>
        )}

        {/* Actions */}
        <div className="flex gap-4">
          <button
            onClick={onRestart}
            className="flex-1 bg-blue-600 hover:bg-blue-700 text-white font-bold py-3 px-6 rounded-lg transition-colors"
          >
            New Game
          </button>
          <button
            onClick={onClose}
            className="flex-1 bg-gray-600 hover:bg-gray-700 text-white font-bold py-3 px-6 rounded-lg transition-colors"
          >
            Close
          </button>
        </div>
      </div>
    </div>
  )
}

