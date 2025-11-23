import { useState, useEffect } from 'react'
import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'

interface GameState {
  budget: number
  reputation: number
  safety_tech_level: number
  green_tech_level: number
  tech_level: number
  hr_efficiency: number
  investor_interest: number
  [key: string]: any  // Allow additional fields
}

interface ControlPanelProps {
  onLaunch: (inputs: {
    mission_type: 'Short_Suborbital' | 'Long_Orbital' | 'Scientific'
    ticket_price: number
    marketing_spend: number
    safety_invest: number
    green_invest: number
    rd_invest: number
    hr_invest: number
    contingency_budget: number
  }) => void
  loading: boolean
  safetyTechLevel?: number
  gameState?: GameState | null
  onInputsChange?: (inputs: {
    mission_type: 'Short_Suborbital' | 'Long_Orbital' | 'Scientific'
    ticket_price: number
    marketing_spend: number
    safety_invest: number
    green_invest: number
    rd_invest: number
    hr_invest: number
    contingency_budget: number
    buy_vehicle: boolean
    investor_offer: number
  }) => void
}

export default function ControlPanel({ onLaunch, loading, safetyTechLevel = 0, gameState, onInputsChange }: ControlPanelProps) {
  const [missionType, setMissionType] = useState<'Short_Suborbital' | 'Long_Orbital' | 'Scientific'>('Short_Suborbital')
  const [ticketPrice, setTicketPrice] = useState(300_000)  // Default for Short Suborbital
  const [marketingSpend, setMarketingSpend] = useState(5_000_000)
  const [safetyInvest, setSafetyInvest] = useState(10_000_000)
  const [greenInvest, setGreenInvest] = useState(3_000_000)
  const [rdInvest, setRdInvest] = useState(8_000_000)
  const [hrInvest, setHrInvest] = useState(0)
  const [contingencyBudget, setContingencyBudget] = useState(0)
  const [projectedStats, setProjectedStats] = useState<any>(null)

  // Fetch projected stats when inputs change
  useEffect(() => {
    if (!gameState) return

    const fetchProjectedStats = async () => {
      try {
         const inputs = {
           mission_type: missionType,
           ticket_price: ticketPrice,
           marketing_spend: marketingSpend,
           safety_invest: safetyInvest,
           green_invest: greenInvest,
           rd_invest: rdInvest,
           hr_invest: hrInvest,
           contingency_budget: contingencyBudget,
           buy_vehicle: false,
           investor_offer: 0  // ControlPanel doesn't manage investor offers
         }
        const response = await axios.post(`${API_BASE_URL}/projected_stats`, inputs)
        setProjectedStats(response.data)
        
         // Notify parent of input changes for Mission Forecast sync
         if (onInputsChange) {
           onInputsChange({
             ...inputs,
             investor_offer: 0  // ControlPanel doesn't manage investor offers
           })
         }
      } catch (error) {
        console.error('Error fetching projected stats:', error)
      }
    }

    // Debounce API calls
    const timeoutId = setTimeout(fetchProjectedStats, 300)
    return () => clearTimeout(timeoutId)
  }, [missionType, ticketPrice, marketingSpend, safetyInvest, greenInvest, rdInvest, hrInvest, contingencyBudget, gameState, onInputsChange])

  const formatCurrency = (amount: number) => {
    if (amount >= 1_000_000) {
      return `€${(amount / 1_000_000).toFixed(1)}M`
    }
    return `€${amount.toLocaleString()}`
  }

  const handleLaunch = () => {
    onLaunch({
      mission_type: missionType,
      ticket_price: ticketPrice,
      marketing_spend: marketingSpend,
      safety_invest: safetyInvest,
      green_invest: greenInvest,
      rd_invest: rdInvest,
      hr_invest: hrInvest,
      contingency_budget: contingencyBudget,
    })
  }

  // Update ticket price range based on mission type
  const getTicketPriceRange = () => {
    switch (missionType) {
      case 'Short_Suborbital':
        return { min: 200_000, max: 1_000_000, default: 300_000 }  // Increased from €400k to €1M
      case 'Long_Orbital':
        return { min: 5_000_000, max: 25_000_000, default: 7_500_000 }  // Increased from €10M to €25M
      case 'Scientific':
        return { min: 1_000_000, max: 100_000_000, default: 10_000_000 }  // Increased from €50M to €100M
      default:
        return { min: 1_000_000, max: 100_000_000, default: 12_000_000 }
    }
  }

  const priceRange = getTicketPriceRange()
  
  // Update ticket price when mission type changes
  const handleMissionTypeChange = (newType: 'Short_Suborbital' | 'Long_Orbital' | 'Scientific') => {
    setMissionType(newType)
    const range = getTicketPriceRange()
    setTicketPrice(range.default)
  }

  return (
    <div className="w-80 bg-gray-800 border-r border-gray-700 p-6 h-screen overflow-y-auto">
      <h2 className="text-xl font-bold mb-6">Mission Controls</h2>

      {/* Mission Type */}
      <div className="mb-6">
        <label className="block text-sm font-medium mb-2">Mission Type</label>
        <select
          value={missionType}
          onChange={(e) => handleMissionTypeChange(e.target.value as 'Short_Suborbital' | 'Long_Orbital' | 'Scientific')}
          className="w-full bg-gray-700 border border-gray-600 rounded px-3 py-2 text-white focus:outline-none focus:border-blue-500"
        >
          <option value="Short_Suborbital">Short Suborbital/Orbital Tourist</option>
          <option value="Long_Orbital" disabled={safetyTechLevel < 5}>
            Long Orbital Stay (Tourist) {safetyTechLevel < 5 && `(Req: Safety Lvl 5)`}
          </option>
          <option value="Scientific">Scientific/Industrial</option>
        </select>
        <div className="mt-1 text-xs text-gray-400">
          {missionType === 'Short_Suborbital' && 'Low risk, €200k-€1M per pax'}
          {missionType === 'Long_Orbital' && 'Medium risk, €5M-€25M per pax, requires Safety Lvl 5'}
          {missionType === 'Scientific' && 'High risk, fixed contract (€1M-€100M), bonus R&D on success'}
        </div>
      </div>

      {/* Ticket Price / Contract Value */}
      <div className="mb-6">
        <label className="block text-sm font-medium mb-2">
          {missionType === 'Scientific' ? 'Contract Value' : 'Ticket Price'}: {formatCurrency(ticketPrice)}
        </label>
        <input
          type="range"
          min={priceRange.min}
          max={priceRange.max}
          step={missionType === 'Short_Suborbital' ? 10_000 : missionType === 'Long_Orbital' ? 100_000 : 500_000}
          value={ticketPrice}
          onChange={(e) => setTicketPrice(Number(e.target.value))}
          className="w-full"
        />
        <div className="flex justify-between text-xs text-gray-400 mt-1">
          <span>{formatCurrency(priceRange.min)}</span>
          <span>{formatCurrency(priceRange.max)}</span>
        </div>
      </div>

      {/* Marketing Spend */}
      <div className="mb-6">
        <div className="flex items-center justify-between mb-2">
          <label className="block text-sm font-medium">
            Marketing Spend: {formatCurrency(marketingSpend)}
          </label>
          {projectedStats && marketingSpend > 0 && (
            <span className="text-xs bg-yellow-600 text-white px-2 py-1 rounded">
              +{projectedStats.marketing_reputation_boost.toFixed(1)} Rep
            </span>
          )}
        </div>
        <input
          type="range"
          min={0}
          max={50_000_000}
          step={1_000_000}
          value={marketingSpend}
          onChange={(e) => setMarketingSpend(Number(e.target.value))}
          className="w-full"
        />
        <div className="flex justify-between text-xs text-gray-400 mt-1">
          <span>€0</span>
          <span>€50M</span>
        </div>
        {projectedStats && marketingSpend > 0 && (
          <div className="text-xs text-yellow-400 mt-1 font-semibold">
            Reputation: {gameState?.reputation.toFixed(1) || '50.0'} → {projectedStats.projected_reputation?.toFixed(1) || gameState?.reputation.toFixed(1) || '50.0'} (+{projectedStats.marketing_reputation_boost.toFixed(1)} from marketing)
          </div>
        )}
      </div>

      {/* Safety Investment */}
      <div className="mb-6">
        <div className="flex items-center justify-between mb-2">
          <label className="block text-sm font-medium">
            Safety Investment: {formatCurrency(safetyInvest)}
          </label>
          {projectedStats && (
            <span className="text-xs bg-yellow-600 text-white px-2 py-1 rounded">
              {projectedStats.projected_failure_risk_pct.toFixed(1)}% Risk
            </span>
          )}
        </div>
        <input
          type="range"
          min={0}
          max={50_000_000}
          step={1_000_000}
          value={safetyInvest}
          onChange={(e) => setSafetyInvest(Number(e.target.value))}
          className="w-full"
        />
        <div className="flex justify-between text-xs text-gray-400 mt-1">
          <span>€0</span>
          <span>€50M</span>
        </div>
      </div>

      {/* Green Investment */}
      <div className="mb-6">
        <div className="flex items-center justify-between mb-2">
          <label className="block text-sm font-medium">
            Green Investment: {formatCurrency(greenInvest)}
          </label>
          {projectedStats && (
            <span className="text-xs bg-green-600 text-white px-2 py-1 rounded">
              -{((1 - (projectedStats.projected_co2_impact / 100)) * 100).toFixed(0)}% CO2
            </span>
          )}
        </div>
        <input
          type="range"
          min={0}
          max={50_000_000}
          step={1_000_000}
          value={greenInvest}
          onChange={(e) => setGreenInvest(Number(e.target.value))}
          className="w-full"
        />
        <div className="flex justify-between text-xs text-gray-400 mt-1">
          <span>€0</span>
          <span>€50M</span>
        </div>
      </div>

      {/* R&D Investment */}
      <div className="mb-6">
        <div className="flex items-center justify-between mb-2">
          <label className="block text-sm font-medium">
            R&D Investment: {formatCurrency(rdInvest)}
          </label>
          {projectedStats && (
            <span className="text-xs bg-blue-600 text-white px-2 py-1 rounded">
              +{projectedStats.rd_points.toFixed(1)} Tech Points
            </span>
          )}
        </div>
        <input
          type="range"
          min={0}
          max={50_000_000}
          step={1_000_000}
          value={rdInvest}
          onChange={(e) => setRdInvest(Number(e.target.value))}
          className="w-full"
        />
        <div className="flex justify-between text-xs text-gray-400 mt-1">
          <span>€0</span>
          <span>€50M</span>
        </div>
      </div>

      {/* HR & Training Investment */}
      <div className="mb-6">
        <div className="flex items-center justify-between mb-2">
          <label className="block text-sm font-medium">
            HR & Training: {formatCurrency(hrInvest)}
          </label>
          {projectedStats && projectedStats.hr_efficiency_gain > 0 && (
            <span className="text-xs bg-purple-600 text-white px-2 py-1 rounded">
              {projectedStats.hr_efficiency_after.toFixed(2)}x Efficiency
            </span>
          )}
        </div>
        <input
          type="range"
          min={0}
          max={50_000_000}
          step={1_000_000}
          value={hrInvest}
          onChange={(e) => setHrInvest(Number(e.target.value))}
          className="w-full"
        />
        <div className="flex justify-between text-xs text-gray-400 mt-1">
          <span>€0</span>
          <span>€50M</span>
        </div>
        <div className="text-xs text-gray-500 mt-1">
          Improves staff efficiency and can save failed missions
        </div>
      </div>

      {/* Contingency Budget */}
      <div className="mb-6">
        <label className="block text-sm font-medium mb-2">
          Contingency Budget: {formatCurrency(contingencyBudget)}
        </label>
        <input
          type="range"
          min={0}
          max={100_000_000}
          step={1_000_000}
          value={contingencyBudget}
          onChange={(e) => setContingencyBudget(Number(e.target.value))}
          className="w-full"
        />
        <div className="flex justify-between text-xs text-gray-400 mt-1">
          <span>€0</span>
          <span>€100M</span>
        </div>
        <div className="text-xs text-gray-500 mt-1">
          Reserve for emergency costs during failures
        </div>
      </div>

      {/* Total Investment Display */}
      <div className="mb-6 p-4 bg-gray-700 rounded">
        <div className="text-sm text-gray-400 mb-1">Total Investments</div>
        <div className="text-lg font-bold">
          {formatCurrency(marketingSpend + safetyInvest + greenInvest + rdInvest + hrInvest)}
        </div>
        <div className="text-xs text-gray-400 mt-1">
          + Contingency: {formatCurrency(contingencyBudget)}
        </div>
      </div>

      {/* Launch Button */}
      <button
        onClick={handleLaunch}
        disabled={loading}
        className="w-full bg-blue-600 hover:bg-blue-700 disabled:bg-gray-600 disabled:cursor-not-allowed text-white font-bold py-4 px-6 rounded-lg text-lg transition-colors"
      >
        {loading ? 'LAUNCHING...' : 'LAUNCH MISSION'}
      </button>
    </div>
  )
}

