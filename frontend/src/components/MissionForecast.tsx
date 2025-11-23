import { useEffect, useState } from 'react'
import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'

interface MissionForecastProps {
  inputs: {
    mission_type: 'Short_Suborbital' | 'Long_Orbital' | 'Scientific'
    ticket_price: number
    marketing_spend: number
    safety_invest: number
    green_invest: number
    rd_invest: number
    hr_invest: number
    contingency_budget: number
    buy_vehicle: boolean
  }
}

interface ProjectedStats {
  rd_points: number
  green_points: number
  safety_points: number
  projected_failure_risk_pct: number
  projected_co2_impact: number
  projected_revenue_min: number
  projected_revenue_max: number
  projected_demand: number
  projected_sales: number
  marketing_reputation_boost: number
  projected_reputation: number
  hr_efficiency_after: number
  hr_efficiency_gain: number
  contingency_mitigation_pct: number
  estimated_failure_penalty: number
  estimated_penalty_after_contingency: number
  meets_safety_requirement: boolean
}

export default function MissionForecast({ inputs }: MissionForecastProps) {
  const [stats, setStats] = useState<ProjectedStats | null>(null)
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    const fetchProjectedStats = async () => {
      setLoading(true)
      try {
        const response = await axios.post<ProjectedStats>(`${API_BASE_URL}/projected_stats`, inputs)
        setStats(response.data)
      } catch (error) {
        console.error('Error fetching projected stats:', error)
      } finally {
        setLoading(false)
      }
    }

    fetchProjectedStats()
  }, [inputs])

  if (loading || !stats) {
    return (
      <div className="bg-gray-800 rounded-lg p-4 border border-gray-700">
        <h3 className="text-lg font-bold mb-3">Mission Forecast</h3>
        <div className="text-gray-400 text-sm">Calculating...</div>
      </div>
    )
  }

  // Determine risk color
  const getRiskColor = (risk: number) => {
    if (risk < 10) return 'text-green-400'
    if (risk < 20) return 'text-yellow-400'
    return 'text-red-400'
  }

  const getRiskBgColor = (risk: number) => {
    if (risk < 10) return 'bg-green-900/30 border-green-700'
    if (risk < 20) return 'bg-yellow-900/30 border-yellow-700'
    return 'bg-red-900/30 border-red-700'
  }

  return (
    <div className="bg-gray-800 rounded-lg p-4 border border-gray-700">
      <h3 className="text-lg font-bold mb-3">Mission Forecast</h3>
      
      <div className="space-y-3">
        {/* Failure Risk */}
        <div className={`p-3 rounded border ${getRiskBgColor(stats.projected_failure_risk_pct)}`}>
          <div className="flex items-center justify-between">
            <span className="text-sm font-medium">Est. Failure Risk</span>
            <span className={`text-lg font-bold ${getRiskColor(stats.projected_failure_risk_pct)}`}>
              {stats.projected_failure_risk_pct.toFixed(1)}%
            </span>
          </div>
          {!stats.meets_safety_requirement && (
            <div className="text-xs text-red-400 mt-1">
              ⚠️ Safety requirement not met
            </div>
          )}
        </div>

        {/* Revenue Estimate */}
        <div className="p-3 rounded bg-gray-700/50 border border-gray-600">
          <div className="flex items-center justify-between">
            <span className="text-sm font-medium">💰 Est. Revenue</span>
            <span className="text-lg font-bold text-green-400">
              €{(stats.projected_revenue_min / 1_000_000).toFixed(2)}M - €{(stats.projected_revenue_max / 1_000_000).toFixed(2)}M
            </span>
          </div>
          {inputs.mission_type !== 'Scientific' && (
            <div className="text-xs text-gray-400 mt-1">
              {stats.projected_sales} passengers @ {stats.projected_demand.toFixed(1)} demand
            </div>
          )}
        </div>

        {/* Tech Gain */}
        <div className="p-3 rounded bg-gray-700/50 border border-gray-600">
          <div className="flex items-center justify-between">
            <span className="text-sm font-medium">🧪 Tech Gain</span>
            <span className="text-lg font-bold text-blue-400">
              +{stats.rd_points.toFixed(1)} R&D, +{stats.green_points.toFixed(1)} Green, +{stats.safety_points.toFixed(1)} Safety
            </span>
          </div>
        </div>

        {/* Additional Info */}
        <div className="grid grid-cols-2 gap-2 text-xs">
          <div className="text-gray-400">
            HR Efficiency: <span className="text-white font-semibold">{stats.hr_efficiency_after.toFixed(2)}x</span>
          </div>
          <div className="text-gray-400">
            CO2 Impact: <span className="text-white font-semibold">{stats.projected_co2_impact.toFixed(1)}</span>
          </div>
          <div className="text-gray-400">
            Reputation: <span className="text-yellow-400 font-semibold">{stats.projected_reputation.toFixed(1)}</span>
            {stats.marketing_reputation_boost > 0 && (
              <span className="text-green-400 ml-1">(+{stats.marketing_reputation_boost.toFixed(1)})</span>
            )}
          </div>
        </div>
        
        {/* Failure Penalty Info */}
        <div className="mt-3 p-3 rounded bg-red-900/20 border border-red-700">
          <div className="text-xs font-medium text-red-400 mb-1">Failure Penalty Estimate</div>
          <div className="flex items-center justify-between text-sm">
            <span className="text-gray-400">If mission fails:</span>
            <span className="text-red-400 font-semibold">€{(stats.estimated_failure_penalty / 1_000_000).toFixed(1)}M</span>
          </div>
          {stats.contingency_mitigation_pct > 0 && (
            <div className="flex items-center justify-between text-xs mt-1">
              <span className="text-gray-500">After contingency:</span>
              <span className="text-yellow-400">€{(stats.estimated_penalty_after_contingency / 1_000_000).toFixed(1)}M</span>
            </div>
          )}
          {stats.contingency_mitigation_pct === 0 && stats.estimated_failure_penalty > 0 && (
            <div className="text-xs text-yellow-400 mt-1">
              💡 Consider adding contingency budget to mitigate losses
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

