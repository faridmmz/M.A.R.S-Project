interface ResearchTabProps {
  techLevel: number
  greenTechLevel: number
  techUnlocks: {
    reusable_stage1: boolean
    green_hydrogen: boolean
  }
}

export default function ResearchTab({ techLevel, greenTechLevel, techUnlocks }: ResearchTabProps) {
  const reusableProgress = Math.min((techLevel / 10) * 100, 100)
  const greenHydrogenProgress = Math.min((techLevel / 20) * 100, 100)

  return (
    <div className="p-6 space-y-6">
      <h2 className="text-2xl font-bold mb-4">Research & Development</h2>

      {/* R&D Tech Tree */}
      <div className="space-y-4">
        <h3 className="text-xl font-semibold">Technology Research</h3>
        
        {/* Reusable Stage 1 */}
        <div className="bg-gray-800 rounded-lg p-4 border border-gray-700">
          <div className="flex items-center justify-between mb-2">
            <div className="flex items-center gap-3">
              <span className="text-2xl">🚀</span>
              <div>
                <div className="font-semibold text-lg">Reusable Stage 1</div>
                <div className="text-sm text-gray-400">
                  Reduces launch costs by 20%
                </div>
              </div>
            </div>
            {techUnlocks.reusable_stage1 ? (
              <span className="bg-green-600 text-white px-3 py-1 rounded text-sm font-bold">
                UNLOCKED
              </span>
            ) : (
              <span className="text-gray-500 text-sm">
                {techLevel}/10 points
              </span>
            )}
          </div>
          <div className="w-full bg-gray-700 rounded-full h-3">
            <div
              className={`h-3 rounded-full transition-all ${
                techUnlocks.reusable_stage1 ? 'bg-green-500' : 'bg-blue-500'
              }`}
              style={{ width: `${reusableProgress}%` }}
            />
          </div>
        </div>

        {/* Green Hydrogen */}
        <div className="bg-gray-800 rounded-lg p-4 border border-gray-700">
          <div className="flex items-center justify-between mb-2">
            <div className="flex items-center gap-3">
              <span className="text-2xl">🌱</span>
              <div>
                <div className="font-semibold text-lg">Green Hydrogen</div>
                <div className="text-sm text-gray-400">
                  Reduces CO2 emissions by 50%
                </div>
              </div>
            </div>
            {techUnlocks.green_hydrogen ? (
              <span className="bg-green-600 text-white px-3 py-1 rounded text-sm font-bold">
                UNLOCKED
              </span>
            ) : (
              <span className="text-gray-500 text-sm">
                {techLevel}/20 points
              </span>
            )}
          </div>
          <div className="w-full bg-gray-700 rounded-full h-3">
            <div
              className={`h-3 rounded-full transition-all ${
                techUnlocks.green_hydrogen ? 'bg-green-500' : 'bg-emerald-500'
              }`}
              style={{ width: `${greenHydrogenProgress}%` }}
            />
          </div>
        </div>
      </div>

      {/* Green Tech */}
      <div className="space-y-4">
        <h3 className="text-xl font-semibold">Green Technology</h3>
        <div className="bg-gray-800 rounded-lg p-4 border border-gray-700">
          <div className="flex items-center justify-between mb-2">
            <div className="flex items-center gap-3">
              <span className="text-2xl">♻️</span>
              <div>
                <div className="font-semibold text-lg">Green Tech Level</div>
                <div className="text-sm text-gray-400">
                  Reduces costs and CO2 per level
                </div>
              </div>
            </div>
            <span className="text-emerald-400 font-bold text-lg">
              Level {greenTechLevel}
            </span>
          </div>
          <div className="text-sm text-gray-400">
            Each level: -1% costs, -2% CO2 emissions
          </div>
        </div>
      </div>

      {/* Current Stats */}
      <div className="bg-gray-800 rounded-lg p-4 border border-gray-700">
        <h3 className="font-semibold mb-3">Research Progress</h3>
        <div className="grid grid-cols-2 gap-4 text-sm">
          <div>
            <div className="text-gray-400">R&D Points</div>
            <div className="text-xl font-bold text-purple-400">{techLevel}</div>
          </div>
          <div>
            <div className="text-gray-400">Green Tech Points</div>
            <div className="text-xl font-bold text-emerald-400">{greenTechLevel}</div>
          </div>
        </div>
        <div className="mt-3 text-xs text-gray-500">
          Invest €10M in R&D to gain 1 tech point
        </div>
      </div>
    </div>
  )
}

