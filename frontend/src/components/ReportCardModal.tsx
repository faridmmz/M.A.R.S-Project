interface TurnResult {
  financials: {
    profit: number
    revenue: number
    costs: {
      fixed_costs: number
      variable_costs: number
      investments: number
      total_costs: number
    }
  }
  results: {
    pax_sold: number
    mission_success: boolean
    message: string
    demand: number
    competitor_news?: string
    persona_breakdown?: {
      uhnw_tourists: number
      government: number
      research_industrial: number
    }
  }
  new_state: {
    budget: number
    reputation: number
    year: number
  }
  scenario_comparison?: {
    current_scenario: string
    shadow_scenario: string
    shadow_demand: number
    shadow_profit: number
    market_penetration_pct: number
    cac: number
    reputational_vulnerability: number
  }
  event?: {
    id: string
    title: string
    description: string
    icon: string
    color: string
    is_new: boolean
    turns_remaining: number
    effects: string[]
  } | null
}

interface ReportCardModalProps {
  result: TurnResult
  onClose: () => void
}

export default function ReportCardModal({ result, onClose }: ReportCardModalProps) {
  const formatCurrency = (amount: number) => {
    if (amount >= 1_000_000_000) {
      return `€${(amount / 1_000_000_000).toFixed(2)}B`
    } else if (amount >= 1_000_000) {
      return `€${(amount / 1_000_000).toFixed(1)}M`
    } else {
      return `€${amount.toLocaleString()}`
    }
  }

  const profitColor = result.financials.profit >= 0 ? 'text-green-400' : 'text-red-400'

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-gray-800 rounded-lg border border-gray-700 flex flex-col max-h-[90vh] w-full max-w-2xl mx-auto shadow-2xl">
        {/* Header - Fixed */}
        <div className="flex justify-between items-center p-6 border-b border-gray-700 flex-shrink-0">
          <h2 className="text-2xl font-bold">
            {result.results.mission_success ? (
              <span className="text-green-400">✓ Mission Successful!</span>
            ) : (
              <span className="text-red-400">✗ Mission Failed!</span>
            )}
          </h2>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-white text-3xl font-bold leading-none w-8 h-8 flex items-center justify-center rounded hover:bg-gray-700 transition-colors"
            aria-label="Close"
          >
            ×
          </button>
        </div>

        {/* Scrollable Content */}
        <div className="overflow-y-auto flex-1 p-6 space-y-4">
          {/* Event Card — shown prominently when an event fired */}
          {result.event && (
            <div className={`rounded-lg p-4 border-2 ${
              result.event.color === 'red' ? 'bg-red-950 border-red-600' :
              result.event.color === 'orange' ? 'bg-orange-950 border-orange-600' :
              result.event.color === 'green' ? 'bg-green-950 border-green-600' :
              result.event.color === 'blue' ? 'bg-blue-950 border-blue-600' :
              'bg-yellow-950 border-yellow-600'
            }`}>
              <div className="flex items-center gap-2 mb-2">
                <span className="text-2xl">{result.event.icon}</span>
                <div>
                  <div className="font-bold text-white">
                    {result.event.is_new ? '🔔 NEW EVENT: ' : '⏳ ONGOING: '}
                    {result.event.title}
                  </div>
                  {result.event.turns_remaining > 1 && (
                    <div className="text-xs text-gray-400">{result.event.turns_remaining} turn(s) remaining</div>
                  )}
                </div>
              </div>
              <p className="text-sm text-gray-200 leading-relaxed">{result.event.description}</p>
              {result.event.effects.length > 0 && (
                <div className="mt-2 pt-2 border-t border-white/20">
                  {result.event.effects.map((eff, i) => (
                    <div key={i} className="text-sm text-green-300 font-semibold">✓ {eff}</div>
                  ))}
                </div>
              )}
            </div>
          )}

          {/* Mission Status */}
          <div className="bg-gray-700 rounded-lg p-4">
            <div className="text-lg font-semibold mb-2">Mission Results</div>
            <div className="text-gray-300 text-sm leading-relaxed">{result.results.message}</div>
            <div className="mt-3 grid grid-cols-2 gap-3 text-sm">
              <div>
                <span className="text-gray-400">Seats Sold:</span>
                <span className="ml-2 font-semibold text-white">{result.results.pax_sold}/7</span>
              </div>
              <div>
                <span className="text-gray-400">Demand:</span>
                <span className="ml-2 font-semibold text-white">{result.results.demand.toFixed(2)}</span>
              </div>
            </div>
            {result.results.competitor_news && (
              <div className="mt-3 pt-3 border-t border-gray-600">
                <div className="text-sm text-yellow-400 font-semibold mb-1">📰 Market News:</div>
                <div className="text-sm text-gray-300 leading-relaxed">{result.results.competitor_news}</div>
              </div>
            )}
          </div>

          {/* Financials */}
          <div className="bg-gray-700 rounded-lg p-4">
            <div className="text-lg font-semibold mb-3">Financial Summary</div>
            <div className="space-y-2">
              <div className="flex justify-between items-center">
                <span className="text-gray-300">Revenue:</span>
                <span className="font-semibold text-lg">{formatCurrency(result.financials.revenue)}</span>
              </div>
              <div className="flex justify-between text-sm text-gray-400">
                <span>Fixed Costs:</span>
                <span>{formatCurrency(result.financials.costs.fixed_costs)}</span>
              </div>
              <div className="flex justify-between text-sm text-gray-400">
                <span>Variable Costs:</span>
                <span>{formatCurrency(result.financials.costs.variable_costs)}</span>
              </div>
              <div className="flex justify-between text-sm text-gray-400">
                <span>Investments:</span>
                <span>{formatCurrency(result.financials.costs.investments)}</span>
              </div>
              {(result.financials.costs as any).spaceport_cost > 0 && (
                <div className="flex justify-between text-sm text-blue-400">
                  <span>Spaceport Capex:</span>
                  <span>{formatCurrency((result.financials.costs as any).spaceport_cost)}</span>
                </div>
              )}
              <div className="flex justify-between text-sm text-gray-400">
                <span>Total Costs:</span>
                <span>{formatCurrency(result.financials.costs.total_costs)}</span>
              </div>
              <div className="border-t border-gray-600 pt-3 mt-3">
                <div className="flex justify-between items-center">
                  <span className="text-lg font-semibold">Profit:</span>
                  <span className={`text-xl font-bold ${profitColor}`}>
                    {formatCurrency(result.financials.profit)}
                  </span>
                </div>
              </div>
            </div>
          </div>

          {/* Persona demand breakdown (if available) */}
          {result.results.persona_breakdown && (
            <div className="bg-gray-700 rounded-lg p-4">
              <div className="text-lg font-semibold mb-3">Demand by Customer Persona</div>
              <div className="grid grid-cols-3 gap-3 text-sm">
                <div>
                  <div className="text-gray-400 mb-1">UHNW Tourists</div>
                  <div className="font-semibold text-violet-400">
                    {result.results.persona_breakdown.uhnw_tourists.toFixed(2)}
                  </div>
                </div>
                <div>
                  <div className="text-gray-400 mb-1">Government</div>
                  <div className="font-semibold text-sky-400">
                    {result.results.persona_breakdown.government.toFixed(2)}
                  </div>
                </div>
                <div>
                  <div className="text-gray-400 mb-1">Research/Industrial</div>
                  <div className="font-semibold text-emerald-400">
                    {result.results.persona_breakdown.research_industrial.toFixed(2)}
                  </div>
                </div>
              </div>
              {result.scenario_comparison && (
                <div className="mt-3 pt-3 border-t border-gray-600 text-xs">
                  <span className="text-gray-400">Shadow (Scenario {result.scenario_comparison.shadow_scenario}): </span>
                  <span className={result.scenario_comparison.shadow_profit > result.financials.profit ? 'text-green-400 font-semibold' : 'text-red-400 font-semibold'}>
                    {formatCurrency(result.scenario_comparison.shadow_profit)}
                  </span>
                  <span className="text-gray-500 ml-2">
                    ({result.scenario_comparison.shadow_profit > result.financials.profit ? '+' : ''}
                    {formatCurrency(result.scenario_comparison.shadow_profit - result.financials.profit)} vs actual)
                  </span>
                </div>
              )}
            </div>
          )}

          {/* Updated State */}
          <div className="bg-gray-700 rounded-lg p-4">
            <div className="text-lg font-semibold mb-3">Updated Status</div>
            <div className="grid grid-cols-3 gap-4 text-sm">
              <div>
                <div className="text-gray-400 mb-1">Budget</div>
                <div className="font-semibold text-green-400 text-lg">
                  {formatCurrency(result.new_state.budget)}
                </div>
              </div>
              <div>
                <div className="text-gray-400 mb-1">Reputation</div>
                <div className="font-semibold text-yellow-400 text-lg">
                  {result.new_state.reputation.toFixed(1)}/100
                </div>
              </div>
              <div>
                <div className="text-gray-400 mb-1">Year</div>
                <div className="font-semibold text-lg">{result.new_state.year}</div>
              </div>
            </div>
          </div>
        </div>

        {/* Footer with Button - Fixed */}
        <div className="p-6 border-t border-gray-700 flex-shrink-0 bg-gray-800">
          <button
            onClick={onClose}
            className="w-full bg-blue-600 hover:bg-blue-700 active:bg-blue-800 text-white font-bold py-4 px-6 rounded-lg text-lg transition-all duration-200 shadow-lg hover:shadow-xl focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 focus:ring-offset-gray-800"
          >
            Continue
          </button>
        </div>
      </div>
    </div>
  )
}
