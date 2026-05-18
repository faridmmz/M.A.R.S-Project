import { useState, useEffect, useRef } from 'react'
import { createPortal } from 'react-dom'
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
    regulatory_invest: number
    buy_spaceport: boolean
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
    regulatory_invest: number
    buy_vehicle: boolean
    buy_spaceport: boolean
    investor_offer: number
  }) => void
}

// Static competitor data — mirrors models.py GlobalConfig constants
const MARKET_INTEL = {
  Short_Suborbital: {
    segment: 'Suborbital Tourism',
    icon: '🪂',
    competitors: [
      { name: 'Virgin Galactic', price: 450_000, safety: 65, share: 25, note: 'SpaceShipIII, suspended ops 2023' },
      { name: 'Blue Origin (New Shepard)', price: 500_000, safety: 82, share: 35, note: '2022 anomaly, returned 2024' },
    ],
    playerShare: 40,  // 1 - 0.60 total comp share
  },
  Long_Orbital: {
    segment: 'Orbital Stay',
    icon: '🛸',
    competitors: [
      { name: 'SpaceX Dragon', price: 8_000_000, safety: 90, share: 45, note: 'Market leader, ISS crew & tourist runs' },
      { name: 'Blue Origin', price: 12_000_000, safety: 75, share: 25, note: 'New Glenn, orbital station ambitions' },
      { name: 'Axiom Space', price: 15_000_000, safety: 80, share: 20, note: 'ISS commercial modules, private station' },
    ],
    playerShare: 10,  // 1 - 0.90 total comp share
  },
  Scientific: {
    segment: 'Research / Industrial',
    icon: '🔬',
    competitors: [
      { name: 'SpaceX Dragon', price: 8_000_000, safety: 90, share: 45, note: 'NASA & agency primary contractor' },
      { name: 'Rocket Lab', price: 8_500_000, safety: 78, share: 20, note: 'Small-sat & micro-payload specialist' },
      { name: 'Axiom Space', price: 15_000_000, safety: 80, share: 15, note: 'Research module lease contracts' },
    ],
    playerShare: 20,
  },
}

function formatPrice(p: number) {
  return p >= 1_000_000 ? `€${(p / 1_000_000).toFixed(1)}M` : `€${(p / 1_000).toFixed(0)}k`
}

function MarketIntelTooltip({
  missionType,
  ticketPrice,
  anchorRect,
}: {
  missionType: 'Short_Suborbital' | 'Long_Orbital' | 'Scientific'
  ticketPrice: number
  anchorRect: DOMRect
}) {
  const intel = MARKET_INTEL[missionType]
  const compAvgPrice =
    intel.competitors.reduce((sum, c) => sum + c.price * c.share, 0) /
    intel.competitors.reduce((sum, c) => sum + c.share, 0)
  const belowAvg = ticketPrice < compAvgPrice

  return createPortal(
    <div
      className="w-80 rounded-xl border border-blue-700/60 bg-gradient-to-br from-blue-950/95 to-gray-900/95 backdrop-blur-sm shadow-2xl p-4 pointer-events-none"
      style={{
        position: 'fixed',
        top: anchorRect.bottom + 8,
        left: anchorRect.left,
        zIndex: 9999,
        filter: 'drop-shadow(0 0 18px rgba(0,0,0,0.7))',
      }}
    >
      <div className="absolute -top-2 left-6 w-3 h-3 rotate-45 border-l border-t border-blue-700/60 bg-gray-900" />

      {/* Header */}
      <div className="flex items-center gap-2 mb-3">
        <span className="text-xl">{intel.icon}</span>
        <div>
          <div className="text-sm font-bold text-blue-300">Market Intel — {intel.segment}</div>
          <div className="text-xs text-gray-400">Competitor reference prices for this mission type</div>
        </div>
      </div>

      <div className="h-px mb-3 bg-gradient-to-r from-transparent via-blue-700/50 to-transparent" />

      {/* Competitor rows */}
      <div className="space-y-2 mb-3">
        {intel.competitors.map((c) => (
          <div key={c.name} className="flex items-start justify-between gap-2">
            <div className="flex-1 min-w-0">
              <div className="text-xs font-semibold text-white truncate">{c.name}</div>
              <div className="text-xs text-gray-500 truncate">{c.note}</div>
            </div>
            <div className="text-right shrink-0">
              <div className="text-xs font-bold text-yellow-300">{formatPrice(c.price)}</div>
              <div className="text-xs text-gray-400">{c.share}% share · {c.safety}⚡ safety</div>
            </div>
          </div>
        ))}
      </div>

      <div className="h-px mb-3 bg-gradient-to-r from-transparent via-blue-700/50 to-transparent" />

      {/* Summary row */}
      <div className="flex items-center justify-between text-xs mb-2">
        <span className="text-gray-400">Competitor avg:</span>
        <span className="font-bold text-white">{formatPrice(compAvgPrice)}</span>
      </div>
      <div className="flex items-center justify-between text-xs mb-2">
        <span className="text-gray-400">Your price:</span>
        <span className={`font-bold ${belowAvg ? 'text-green-400' : 'text-red-400'}`}>
          {formatPrice(ticketPrice)} {belowAvg ? '▼ below avg' : '▲ above avg'}
        </span>
      </div>
      <div className="flex items-center justify-between text-xs">
        <span className="text-gray-400">Base addressable share:</span>
        <span className="font-bold text-blue-300">~{intel.playerShare}%</span>
      </div>
    </div>,
    document.body
  )
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
  const [regulatoryInvest, setRegulatoryInvest] = useState(5_000_000)
  const [buySpaceport, setBuySpaceport] = useState(false)
  const [projectedStats, setProjectedStats] = useState<any>(null)
  const [showMarketIntel, setShowMarketIntel] = useState(false)
  const [marketIntelRect, setMarketIntelRect] = useState<DOMRect | null>(null)
  const marketIntelBtnRef = useRef<HTMLButtonElement>(null)

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
           regulatory_invest: regulatoryInvest,
           buy_vehicle: false,
           buy_spaceport: buySpaceport,
           investor_offer: 0
         }
        const response = await axios.post(`${API_BASE_URL}/projected_stats`, inputs)
        setProjectedStats(response.data)

         if (onInputsChange) {
           onInputsChange({ ...inputs, investor_offer: 0 })
         }
      } catch (error) {
        console.error('Error fetching projected stats:', error)
      }
    }

    // Debounce API calls
    const timeoutId = setTimeout(fetchProjectedStats, 300)
    return () => clearTimeout(timeoutId)
  }, [missionType, ticketPrice, marketingSpend, safetyInvest, greenInvest, rdInvest, hrInvest, contingencyBudget, regulatoryInvest, buySpaceport, gameState, onInputsChange])

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
      regulatory_invest: regulatoryInvest,
      buy_spaceport: buySpaceport,
    })
    setBuySpaceport(false)
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
  
  const getMissionPriceRange = (type: 'Short_Suborbital' | 'Long_Orbital' | 'Scientific') => {
    switch (type) {
      case 'Short_Suborbital': return { min: 200_000, max: 1_000_000, default: 300_000 }
      case 'Long_Orbital':     return { min: 5_000_000, max: 25_000_000, default: 7_500_000 }
      case 'Scientific':       return { min: 1_000_000, max: 100_000_000, default: 10_000_000 }
      default:                 return { min: 1_000_000, max: 100_000_000, default: 12_000_000 }
    }
  }

  const handleMissionTypeChange = (newType: 'Short_Suborbital' | 'Long_Orbital' | 'Scientific') => {
    setMissionType(newType)
    setTicketPrice(getMissionPriceRange(newType).default)
  }

  return (
    <div className="w-80 bg-gray-800 border-r border-gray-700 p-6 h-full overflow-y-auto shrink-0">
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
        <div className="flex items-center justify-between mb-2">
          <label className="block text-sm font-medium">
            {missionType === 'Scientific' ? 'Contract Value' : 'Ticket Price'}: {formatCurrency(ticketPrice)}
          </label>
          {missionType !== 'Scientific' && (
            <div
              onMouseEnter={() => {
                if (marketIntelBtnRef.current) {
                  setMarketIntelRect(marketIntelBtnRef.current.getBoundingClientRect())
                }
                setShowMarketIntel(true)
              }}
              onMouseLeave={() => setShowMarketIntel(false)}
            >
              <button
                ref={marketIntelBtnRef}
                className="text-xs bg-blue-800 hover:bg-blue-700 text-blue-200 px-2 py-0.5 rounded font-medium transition-colors"
                tabIndex={-1}
              >
                Market Intel ℹ
              </button>
              {showMarketIntel && marketIntelRect && (
                <MarketIntelTooltip missionType={missionType} ticketPrice={ticketPrice} anchorRect={marketIntelRect} />
              )}
            </div>
          )}
        </div>
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
          <div className="flex gap-1">
            {projectedStats && (
              <span className="text-xs bg-yellow-600 text-white px-2 py-1 rounded">
                {projectedStats.projected_failure_risk_pct.toFixed(1)}% Risk
              </span>
            )}
            {projectedStats && projectedStats.safety_points > 0 && (
              <span className="text-xs bg-orange-600 text-white px-2 py-1 rounded">
                +{projectedStats.safety_points.toFixed(1)} Safety Tech
              </span>
            )}
          </div>
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
        {projectedStats && projectedStats.safety_points > 0 && (
          <div className="text-xs text-orange-400 mt-1 font-semibold">
            Safety Level: {gameState?.safety_tech_level ?? 0} → {projectedStats.projected_safety_level} (+{Math.floor(projectedStats.safety_points)} lvl)
          </div>
        )}
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

      {/* Regulatory & Licensing */}
      <div className="mb-6">
        <div className="flex items-center justify-between mb-2">
          <label className="block text-sm font-medium">
            Legal & Licensing: {formatCurrency(regulatoryInvest)}
          </label>
          {regulatoryInvest < 5_000_000 && (
            <span className="text-xs bg-red-700 text-white px-2 py-1 rounded">
              ⚠️ {regulatoryInvest === 0 ? 'None!' : 'Low'}
            </span>
          )}
        </div>
        <input
          type="range"
          min={0}
          max={30_000_000}
          step={1_000_000}
          value={regulatoryInvest}
          onChange={(e) => setRegulatoryInvest(Number(e.target.value))}
          className="w-full"
        />
        <div className="flex justify-between text-xs text-gray-400 mt-1">
          <span>€0</span>
          <span>€30M</span>
        </div>
        {regulatoryInvest < 5_000_000 && (
          <div className="text-xs text-red-400 mt-1 font-semibold">
            {regulatoryInvest === 0
              ? 'No compliance spend: reputation −3, vulnerability +15'
              : 'Below €5M minimum: vulnerability +15'}
          </div>
        )}
        {regulatoryInvest >= 5_000_000 && (
          <div className="text-xs text-green-400 mt-1">Compliant ✓</div>
        )}
      </div>

      {/* Spaceport Infrastructure */}
      {!gameState?.has_spaceport && !gameState?.spaceport_building && (
        <div className="mb-6 p-4 bg-gray-700 rounded border border-gray-600">
          <label className="flex items-center gap-3 cursor-pointer">
            <input
              type="checkbox"
              checked={buySpaceport}
              onChange={(e) => setBuySpaceport(e.target.checked)}
              className="w-4 h-4 accent-blue-500"
            />
            <div>
              <div className="text-sm font-medium">Build Dedicated Spaceport</div>
              <div className="text-xs text-gray-400 mt-1">€300M · Ready next turn</div>
              <div className="text-xs text-blue-400 mt-1">
                Unlocks Scenario B full elasticity (×2.5 vs ×1.2)
              </div>
            </div>
          </label>
        </div>
      )}
      {gameState?.spaceport_building && (
        <div className="mb-6 p-4 bg-blue-900 rounded border border-blue-700">
          <div className="text-sm font-medium text-blue-300">🏗️ Spaceport Under Construction</div>
          <div className="text-xs text-gray-400 mt-1">Operational next turn</div>
        </div>
      )}
      {gameState?.has_spaceport && (
        <div className="mb-6 p-4 bg-green-900 rounded border border-green-700">
          <div className="text-sm font-medium text-green-300">🚀 Spaceport Operational</div>
          <div className="text-xs text-gray-400 mt-1">Full Scenario B elasticity active</div>
        </div>
      )}

      {/* Total Investment Display */}
      <div className="mb-6 p-4 bg-gray-700 rounded">
        <div className="text-sm text-gray-400 mb-1">Total Investments</div>
        <div className="text-lg font-bold">
          {formatCurrency(marketingSpend + safetyInvest + greenInvest + rdInvest + hrInvest + regulatoryInvest)}
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

