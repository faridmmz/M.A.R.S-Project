import { useState, useEffect } from 'react'
import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'

interface GameState {
  budget: number
  reputation: number
  investor_roi_target: number
  active_investor_offers?: Array<{
    amount: number
    turn: number
    accepted: boolean
    investor_name?: string
    investor_profession?: string
  }>
  [key: string]: any
}

interface InvestorTabProps {
  gameState: GameState | null
  onMakeOffer?: (amount: number) => void
  onStateUpdate?: (newState: any) => void
}

export default function InvestorTab({ gameState, onMakeOffer, onStateUpdate }: InvestorTabProps) {
  const [offerAmount, setOfferAmount] = useState(50_000_000) // Default €50M
  const [offerChance, setOfferChance] = useState<any>(null)
  const [processing, setProcessing] = useState(false)
  const [lastResult, setLastResult] = useState<any>(null)

  useEffect(() => {
    if (!gameState) return

    const fetchChance = async () => {
      try {
        const response = await axios.get(`${API_BASE_URL}/investor_offer_chance`, {
          params: { offer_amount: offerAmount }
        })
        setOfferChance(response.data)
      } catch (error) {
        console.error('Error fetching offer chance:', error)
      }
    }

    // Debounce API calls
    const timeoutId = setTimeout(fetchChance, 300)
    return () => clearTimeout(timeoutId)
  }, [offerAmount, gameState])

  const formatCurrency = (amount: number) => {
    if (amount >= 1_000_000) {
      return `€${(amount / 1_000_000).toFixed(1)}M`
    }
    return `€${amount.toLocaleString()}`
  }

  if (!gameState) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-gray-400">Loading...</div>
      </div>
    )
  }

  const getChanceColor = (chance: number) => {
    if (chance >= 50) return 'text-green-400'
    if (chance >= 25) return 'text-yellow-400'
    return 'text-red-400'
  }

  const getChanceBgColor = (chance: number) => {
    if (chance >= 50) return 'bg-green-900/30 border-green-700'
    if (chance >= 25) return 'bg-yellow-900/30 border-yellow-700'
    return 'bg-red-900/30 border-red-700'
  }

  return (
    <div className="space-y-6 p-8">
      <h2 className="text-3xl font-bold mb-6">Investor Attraction Center</h2>

      {/* Main Offer Section */}
      <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
        <h3 className="text-xl font-bold mb-4">Make an Investment Offer</h3>
        <p className="text-gray-400 mb-6 text-sm">
          Attract investors by making an offer. Higher offers are harder to get accepted, but higher reputation increases your chances.
        </p>

        {/* Offer Amount Slider */}
        <div className="mb-6">
          <div className="flex items-center justify-between mb-2">
            <label className="block text-sm font-medium">
              Investment Offer: {formatCurrency(offerAmount)}
            </label>
            {offerChance && (
              <div className="flex items-center gap-2">
                <span className={`text-2xl font-bold px-4 py-2 rounded-lg ${getChanceBgColor(offerChance.chance_pct)} ${getChanceColor(offerChance.chance_pct)}`}>
                  {offerChance.chance_pct.toFixed(1)}%
                </span>
                {offerChance.best_chance_pct && offerChance.worst_chance_pct && (
                  <div className="text-xs text-gray-400">
                    Range: {offerChance.worst_chance_pct.toFixed(1)}% - {offerChance.best_chance_pct.toFixed(1)}%
                  </div>
                )}
              </div>
            )}
          </div>
          <input
            type="range"
            min={10_000_000}
            max={500_000_000}
            step={5_000_000}
            value={offerAmount}
            onChange={(e) => setOfferAmount(Number(e.target.value))}
            className="w-full"
          />
          <div className="flex justify-between text-xs text-gray-400 mt-1">
            <span>€10M (Min)</span>
            <span className="text-yellow-400 font-semibold">Higher offer = Lower chance</span>
            <span>€500M (Max)</span>
          </div>
          {/* Show chance change indicator */}
          {offerChance && (
            <div className="mt-2 text-xs text-gray-500">
              <div className="flex items-center gap-2">
                <span>Chance impact:</span>
                <span className={offerChance.chance_pct < 30 ? 'text-red-400 font-semibold' : offerChance.chance_pct < 50 ? 'text-yellow-400 font-semibold' : 'text-green-400 font-semibold'}>
                  {offerChance.chance_pct < 30 ? '⚠️ Low chance' : offerChance.chance_pct < 50 ? '⚡ Moderate chance' : '✅ Good chance'}
                </span>
              </div>
            </div>
          )}
        </div>

        {/* Chance Breakdown */}
        {offerChance && (
          <div className="bg-gray-700 rounded-lg p-4 mb-6">
            <h4 className="font-semibold mb-3">Acceptance Chance Preview</h4>
            <div className="space-y-2 text-sm">
              <div className="flex justify-between">
                <span className="text-gray-400">Average Chance:</span>
                <span className={getChanceColor(offerChance.chance_pct)}>
                  {offerChance.chance_pct.toFixed(1)}%
                </span>
              </div>
              {offerChance.best_investor && (
                <div className="flex justify-between">
                  <span className="text-gray-400">
                    Best Case ({offerChance.best_investor.icon} {offerChance.best_investor.profession}):
                  </span>
                  <span className="text-green-400">
                    {offerChance.best_chance_pct?.toFixed(1) || '0.0'}%
                  </span>
                </div>
              )}
              {offerChance.worst_investor && (
                <div className="flex justify-between">
                  <span className="text-gray-400">
                    Worst Case ({offerChance.worst_investor.icon} {offerChance.worst_investor.profession}):
                  </span>
                  <span className="text-yellow-400">
                    {offerChance.worst_chance_pct?.toFixed(1) || '0.0'}%
                  </span>
                </div>
              )}
              <div className="border-t border-gray-600 pt-2 mt-2 text-xs text-gray-400">
                A random investor will be selected. Each investor values different aspects of your company.
              </div>
            </div>
          </div>
        )}

        {/* Make Offer Button - Real-time processing */}
        <button
          onClick={async () => {
            if (!offerChance || offerAmount < 10_000_000 || processing) return
            
            setProcessing(true)
            setLastResult(null)
            
            try {
              const response = await axios.post(`${API_BASE_URL}/make_investor_offer`, null, {
                params: { offer_amount: offerAmount }
              })
              
              const result = response.data.result
              setLastResult(result)
              
              // Update game state if callback provided
              if (onStateUpdate) {
                onStateUpdate(response.data.new_state)
              }
              
              // Also call onMakeOffer for compatibility
              if (onMakeOffer) {
                onMakeOffer(offerAmount)
              }
            } catch (error: any) {
              console.error('Error making investor offer:', error)
              setLastResult({
                accepted: false,
                message: error.response?.data?.detail || 'Failed to process offer'
              })
            } finally {
              setProcessing(false)
            }
          }}
          disabled={!offerChance || offerAmount < 10_000_000 || processing}
          className="w-full bg-green-600 hover:bg-green-700 disabled:bg-gray-600 disabled:cursor-not-allowed text-white font-bold py-3 px-6 rounded-lg text-lg transition-colors mb-4"
        >
          {processing 
            ? 'Processing Offer...' 
            : `Make Offer Now (${offerChance?.chance_pct.toFixed(1) || 0}% chance)`}
        </button>
        
        {/* Show result message */}
        {lastResult && (
          <div className={`mb-4 p-4 rounded-lg border ${
            lastResult.accepted 
              ? 'bg-green-900/30 border-green-700 text-green-200' 
              : 'bg-red-900/30 border-red-700 text-red-200'
          }`}>
            <div className="font-semibold mb-1">
              {lastResult.accepted ? '✓ Offer Accepted!' : '✗ Offer Declined'}
            </div>
            <div className="text-sm">{lastResult.message}</div>
            {lastResult.investor && (
              <div className="text-xs text-gray-300 mt-2">
                Investor: {lastResult.investor.icon} {lastResult.investor.name} - {lastResult.investor.profession}
                {lastResult.investor.preference && (
                  <span className="ml-2 text-gray-400">
                    (Values: {lastResult.investor.preference === 'safety' ? 'Safety' : 
                              lastResult.investor.preference === 'co2' ? 'Environmental Impact' :
                              lastResult.investor.preference === 'tech' ? 'Technology' :
                              lastResult.investor.preference === 'reputation' ? 'Reputation' : 'Balanced'})
                  </span>
                )}
              </div>
            )}
            {lastResult.reputation_change !== undefined && (
              <div className={`text-sm mt-2 font-semibold ${
                lastResult.reputation_change > 0 ? 'text-green-300' : 'text-red-300'
              }`}>
                {lastResult.reputation_change > 0 ? '↑' : '↓'} Reputation: {lastResult.reputation_change > 0 ? '+' : ''}{lastResult.reputation_change.toFixed(1)}
              </div>
            )}
            {lastResult.explanation && (
              <div className="text-xs text-gray-400 mt-1 italic">
                {lastResult.explanation}
              </div>
            )}
            {lastResult.accepted && lastResult.amount && (
              <div className="text-sm mt-2 font-semibold">
                +€{(lastResult.amount / 1_000_000).toFixed(1)}M added to budget!
              </div>
            )}
          </div>
        )}

        {/* Tips */}
        <div className="bg-blue-900/30 border border-blue-700 rounded-lg p-4">
          <h4 className="font-semibold text-blue-400 mb-2">💡 Strategy Tips</h4>
          <ul className="text-sm text-blue-200 space-y-1">
            <li>• Each offer attracts a random investor with different preferences</li>
            <li>• 👩‍⚕️ Doctors/Safety Engineers value high safety tech levels</li>
            <li>• 🌱 Environmentalists value low CO2 impact</li>
            <li>• 💻 Tech Entrepreneurs value high tech levels</li>
            <li>• 💰 Financial Advisors value high reputation</li>
            <li>• ⚖️ Balanced investors consider multiple factors</li>
            <li>• Higher offers = Slightly lower chance (small penalty)</li>
            <li>• If accepted, you receive the full funding amount immediately</li>
          </ul>
        </div>
      </div>

      {/* Current Status */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="bg-gray-800 rounded-lg p-4 border border-gray-700">
          <h4 className="text-gray-400 text-sm mb-1">Current Reputation</h4>
          <div className="text-2xl font-bold text-yellow-400">
            {gameState.reputation.toFixed(1)}/100
          </div>
          <p className="text-xs text-gray-500 mt-1">
            Higher reputation = better chance
          </p>
        </div>

        <div className="bg-gray-800 rounded-lg p-4 border border-gray-700">
          <h4 className="text-gray-400 text-sm mb-1">ROI Target</h4>
          <div className="text-2xl font-bold text-orange-400">
            {formatCurrency(gameState.investor_roi_target || 0)}
          </div>
          <p className="text-xs text-gray-500 mt-1">
            Expected profit per year
          </p>
        </div>

        <div className="bg-gray-800 rounded-lg p-4 border border-gray-700">
          <h4 className="text-gray-400 text-sm mb-1">Active Offers</h4>
          <div className="text-2xl font-bold text-blue-400">
            {gameState.active_investor_offers?.length || 0}
          </div>
          <p className="text-xs text-gray-500 mt-1">
            Total offers made
          </p>
        </div>
      </div>

      {/* Offer History */}
      {gameState.active_investor_offers && gameState.active_investor_offers.length > 0 && (
        <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
          <h3 className="text-xl font-bold mb-4">Offer History</h3>
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-gray-700">
                  <th className="text-left p-2 text-gray-400">Turn</th>
                  <th className="text-left p-2 text-gray-400">Investor</th>
                  <th className="text-right p-2 text-gray-400">Amount</th>
                  <th className="text-center p-2 text-gray-400">Status</th>
                </tr>
              </thead>
              <tbody>
                {gameState.active_investor_offers.slice().reverse().map((offer, index) => (
                  <tr key={index} className="border-b border-gray-700 hover:bg-gray-700">
                    <td className="p-2">{offer.turn}</td>
                    <td className="p-2 text-sm">
                      {offer.investor_name && (
                        <div>
                          <div className="font-medium">{offer.investor_name}</div>
                          {offer.investor_profession && (
                            <div className="text-xs text-gray-400">{offer.investor_profession}</div>
                          )}
                        </div>
                      )}
                    </td>
                    <td className="p-2 text-right">{formatCurrency(offer.amount)}</td>
                    <td className="p-2 text-center">
                      <span className={`px-2 py-1 rounded text-xs ${
                        offer.accepted 
                          ? 'bg-green-600 text-white' 
                          : 'bg-red-600 text-white'
                      }`}>
                        {offer.accepted ? 'Accepted' : 'Declined'}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  )
}

