import { useState, useEffect, Component } from 'react'
import type { ErrorInfo, ReactNode } from 'react'
import axios from 'axios'
import TopBar from './components/TopBar'
import ControlPanel from './components/ControlPanel'
import ReportCardModal from './components/ReportCardModal'
import NewsTicker from './components/NewsTicker'
import ResearchTab from './components/ResearchTab'
import AnalyticsCharts from './components/AnalyticsCharts'
import FinancialDirectorTab from './components/FinancialDirectorTab'
import InvestorTab from './components/InvestorTab'
import MissionForecast from './components/MissionForecast'
import WinScreen from './components/WinScreen'
import PlaythroughViewer from './components/PlaythroughViewer'
import './App.css'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'

interface GameState {
  budget: number
  reputation: number
  year: number
  tech_level: number
  green_tech_level: number
  safety_tech_level: number
  co2_impact: number
  competitor_price: number
  tech_unlocks: {
    reusable_stage1: boolean
    green_hydrogen: boolean
  }
  hr_efficiency: number
  investor_interest: number
  investor_funded: boolean
  investor_roi_target: number
  vehicles_owned: number
  has_spaceport?: boolean
  spaceport_building?: boolean
  active_spaas_contracts?: number
  active_investor_offers?: Array<{
    amount: number
    turn: number
    accepted: boolean
  }>
}

interface TurnResult {
  financials: {
    profit: number
    revenue: number
    costs: any
  }
  results: {
    pax_sold: number
    mission_success: boolean
    message: string
    demand: number
    competitor_news: string
    persona_breakdown?: {
      uhnw_tourists: number
      government: number
      research_industrial: number
    }
  }
  new_state: GameState
  game_over?: boolean
  game_over_reason?: 'max_years' | 'bankruptcy'
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
  scenario_comparison?: {
    current_scenario: string
    shadow_scenario: string
    shadow_demand: number
    shadow_profit: number
    shadow_persona_breakdown?: {
      uhnw_tourists: number
      government: number
      research_industrial: number
    }
    market_penetration_pct: number
    cac: number
    reputational_vulnerability: number
  }
}

interface HistoryData {
  year: number
  profit: number
  reputation: number
  budget: number
  revenue?: number
  costs?: number
  personaUHNW?: number
  personaGov?: number
  personaResearch?: number
  marketPenetration?: number
  cac?: number
  repVulnerability?: number
  shadowProfit?: number
  scenario?: string
}

type Tab = 'dashboard' | 'research' | 'analytics' | 'financial' | 'investor' | 'playthrough'

class ErrorBoundary extends Component<{ children: ReactNode }, { error: Error | null }> {
  constructor(props: { children: ReactNode }) {
    super(props)
    this.state = { error: null }
  }
  static getDerivedStateFromError(error: Error) {
    return { error }
  }
  componentDidCatch(error: Error, info: ErrorInfo) {
    console.error('React render error:', error, info)
  }
  render() {
    if (this.state.error) {
      return (
        <div className="min-h-screen flex items-center justify-center bg-gray-900 p-8">
          <div className="bg-red-900/50 border border-red-700 rounded-xl p-6 max-w-2xl w-full">
            <h2 className="text-xl font-bold text-red-300 mb-2">Render Error</h2>
            <p className="text-red-400 font-mono text-sm mb-4">{this.state.error.message}</p>
            <pre className="text-xs text-gray-400 overflow-auto bg-gray-800 p-4 rounded whitespace-pre-wrap">
              {this.state.error.stack}
            </pre>
            <button
              onClick={() => this.setState({ error: null })}
              className="mt-4 px-4 py-2 bg-red-700 hover:bg-red-600 text-white rounded"
            >
              Retry
            </button>
          </div>
        </div>
      )
    }
    return this.props.children
  }
}

function App() {
  const [gameState, setGameState] = useState<GameState | null>(null)
  const [loading, setLoading] = useState(false)
  const [showModal, setShowModal] = useState(false)
  const [lastResult, setLastResult] = useState<TurnResult | null>(null)
  const [history, setHistory] = useState<HistoryData[]>([])
  const [currentTab, setCurrentTab] = useState<Tab>('dashboard')
  const [competitorNews, setCompetitorNews] = useState<string>('')
  const [newsFeed, setNewsFeed] = useState<string[]>([])
  const [currentNewsIndex, setCurrentNewsIndex] = useState(0)
  const [showWinScreen, setShowWinScreen] = useState(false)
  const [finalScore, setFinalScore] = useState<any>(null)
  const [gameOverReason, setGameOverReason] = useState<'max_years' | 'bankruptcy' | null>(null)
  const [currentInputs, setCurrentInputs] = useState({
    mission_type: 'Short_Suborbital' as 'Short_Suborbital' | 'Long_Orbital' | 'Scientific',
    ticket_price: 300_000,
    marketing_spend: 5_000_000,
    safety_invest: 10_000_000,
    green_invest: 3_000_000,
    rd_invest: 8_000_000,
    hr_invest: 0,
    contingency_budget: 0,
    buy_vehicle: false,
    investor_offer: 0
  })
  const [marketScenario, setMarketScenario] = useState<'A' | 'B'>('A')

  useEffect(() => {
    startGame()
  }, [])

  // Fetch news feed periodically (like real TV news)
  useEffect(() => {
    if (!gameState) return

    const fetchNewsFeed = async () => {
      try {
        const response = await axios.get(`${API_BASE_URL}/news_feed`)
        setNewsFeed(response.data.news_items || [])
      } catch (error) {
        console.error('Error fetching news feed:', error)
      }
    }

    // Fetch immediately
    fetchNewsFeed()
    
    // Then fetch every 8 seconds (like TV news updates)
    const interval = setInterval(fetchNewsFeed, 8000)
    return () => clearInterval(interval)
  }, [gameState])

  // Cycle through news items every 4 seconds
  useEffect(() => {
    if (newsFeed.length === 0) return

    const interval = setInterval(() => {
      setCurrentNewsIndex((prev) => (prev + 1) % newsFeed.length)
    }, 4000) // Change news item every 4 seconds

    return () => clearInterval(interval)
  }, [newsFeed])

  const startGame = async () => {
    try {
      const response = await axios.post(`${API_BASE_URL}/start_game`)
      setGameState(response.data.state)
      setHistory([{
        year: response.data.state.year,
        profit: 0,
        reputation: response.data.state.reputation,
        budget: response.data.state.budget
      }])
      setCompetitorNews('Market initialized. Competitor price: €10.0M')
    } catch (error) {
      console.error('Error starting game:', error)
      alert('Failed to start game. Make sure the API server is running!')
    }
  }

  const playTurn = async (inputs: {
    mission_type: 'Short_Suborbital' | 'Long_Orbital' | 'Scientific'
    ticket_price: number
    marketing_spend: number
    safety_invest: number
    green_invest: number
    rd_invest: number
    hr_invest: number
    contingency_budget: number
    regulatory_invest?: number
    buy_spaceport?: boolean
  }) => {
    // Update current inputs for Mission Forecast
    setCurrentInputs({
      ...inputs,
      buy_vehicle: false,
      investor_offer: currentInputs.investor_offer || 0
    })
    setLoading(true)
    try {
      const response = await axios.post<TurnResult>(`${API_BASE_URL}/play_turn`, {
        ...inputs,
        investor_offer: currentInputs.investor_offer ?? 0,
        buy_vehicle: currentInputs.buy_vehicle ?? false,
        regulatory_invest: inputs.regulatory_invest ?? 0,
        buy_spaceport: inputs.buy_spaceport ?? false,
        market_scenario: marketScenario,
      })
      setLastResult(response.data)
      setGameState(response.data.new_state)
      setCompetitorNews(response.data.results.competitor_news)
      
      // Add to history (including new market-pivot KPI fields)
      const sc = response.data.scenario_comparison
      const persona = response.data.results.persona_breakdown
      const actualProfit = response.data.financials.profit
      const shadowProfit = sc?.shadow_profit ?? actualProfit
      const playedScenario = sc?.current_scenario ?? marketScenario
      setHistory(prev => [...prev, {
        year: response.data.new_state.year,
        profit: actualProfit,
        reputation: response.data.new_state.reputation,
        budget: response.data.new_state.budget,
        revenue: response.data.financials.revenue,
        costs: response.data.financials.costs?.total_costs || 0,
        personaUHNW: persona?.uhnw_tourists ?? 0,
        personaGov: persona?.government ?? 0,
        personaResearch: persona?.research_industrial ?? 0,
        marketPenetration: sc?.market_penetration_pct ?? 0,
        cac: sc?.cac ?? 0,
        repVulnerability: sc?.reputational_vulnerability ?? 0,
        shadowProfit,
        scenario: playedScenario,
        // Always assign A vs B correctly regardless of current toggle
        scenarioAProfit: playedScenario === 'A' ? actualProfit : shadowProfit,
        scenarioBProfit: playedScenario === 'B' ? actualProfit : shadowProfit,
      }])
      
      // Check for game over — always show report card first, then WinScreen on Close
      if (response.data.game_over) {
        setGameOverReason(response.data.game_over_reason || 'max_years')
        try {
          const scoreResponse = await axios.get(`${API_BASE_URL}/final_score`)
          setFinalScore(scoreResponse.data)
        } catch (error) {
          console.error('Error fetching final score:', error)
        }
      }
      setShowModal(true)
    } catch (error) {
      console.error('Error playing turn:', error)
      alert('Failed to play turn. Check console for details.')
    } finally {
      setLoading(false)
    }
  }

  const closeModal = () => {
    setShowModal(false)
    if (gameOverReason) {
      setShowWinScreen(true)
    }
  }

  if (!gameState) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-900">
        <div className="text-white text-xl">Loading game...</div>
      </div>
    )
  }

  return (
    <div className="h-screen flex flex-col overflow-hidden bg-gray-900 text-white">
      <TopBar gameState={gameState} marketScenario={marketScenario} onScenarioChange={setMarketScenario} />
      <NewsTicker news={newsFeed.length > 0 ? newsFeed[currentNewsIndex] : competitorNews} gameState={gameState} />
      <div className="flex flex-1 overflow-hidden">
        <ControlPanel
          onLaunch={playTurn}
          loading={loading}
          safetyTechLevel={gameState.safety_tech_level}
          gameState={gameState}
          onInputsChange={setCurrentInputs}
        />
        <div className="flex flex-col flex-1 overflow-hidden">
          {/* Tabs */}
          <div className="border-b border-gray-700 bg-gray-800 shrink-0">
            <div className="flex">
              <button
                onClick={() => setCurrentTab('dashboard')}
                className={`px-6 py-3 font-semibold transition-colors ${
                  currentTab === 'dashboard'
                    ? 'border-b-2 border-blue-500 text-blue-400'
                    : 'text-gray-400 hover:text-white'
                }`}
              >
                Dashboard
              </button>
              <button
                onClick={() => setCurrentTab('research')}
                className={`px-6 py-3 font-semibold transition-colors ${
                  currentTab === 'research'
                    ? 'border-b-2 border-blue-500 text-blue-400'
                    : 'text-gray-400 hover:text-white'
                }`}
              >
                Research
              </button>
              <button
                onClick={() => setCurrentTab('analytics')}
                className={`px-6 py-3 font-semibold transition-colors ${
                  currentTab === 'analytics'
                    ? 'border-b-2 border-blue-500 text-blue-400'
                    : 'text-gray-400 hover:text-white'
                }`}
              >
                Analytics
              </button>
              <button
                onClick={() => setCurrentTab('financial')}
                className={`px-6 py-3 font-semibold transition-colors ${
                  currentTab === 'financial'
                    ? 'border-b-2 border-blue-500 text-blue-400'
                    : 'text-gray-400 hover:text-white'
                }`}
              >
                Financial Director
              </button>
              <button
                onClick={() => setCurrentTab('investor')}
                className={`px-6 py-3 font-semibold transition-colors ${
                  currentTab === 'investor'
                    ? 'border-b-2 border-blue-500 text-blue-400'
                    : 'text-gray-400 hover:text-white'
                }`}
              >
                Investor Attraction
              </button>
              <button
                onClick={() => setCurrentTab('playthrough')}
                className={`px-6 py-3 font-semibold transition-colors ${
                  currentTab === 'playthrough'
                    ? 'border-b-2 border-purple-500 text-purple-400'
                    : 'text-gray-400 hover:text-white'
                }`}
              >
                📊 Playthrough Results
              </button>
            </div>
          </div>

          {/* Tab Content */}
          <div className="flex-1 overflow-y-auto">
            {currentTab === 'dashboard' && (
              <div className="p-8">
                <h2 className="text-2xl font-bold mb-4">Dashboard</h2>
                <p className="text-gray-400 mb-6">
                  Welcome to M.A.R.S. - Market Analysis & Risk Simulation
                </p>
                
                {/* Mission Forecast in Dashboard */}
                <div className="mb-6">
                  <MissionForecast inputs={currentInputs} />
                </div>
                {/* SPaaS — Fractional Research Contracts */}
                {(() => {
                  const contracts = gameState.active_spaas_contracts ?? 0
                  const arrPerTurn = contracts * 5
                  const hasSpaceport = gameState.has_spaceport
                  const buildingSpaceport = gameState.spaceport_building
                  const maxContracts = 5

                  let statusColor = 'border-gray-700'
                  let statusBadge = null
                  let statusText = ''

                  if (contracts === maxContracts) {
                    statusColor = 'border-green-500'
                    statusBadge = <span className="text-xs bg-green-700 text-green-100 px-2 py-0.5 rounded-full">Maxed Out</span>
                    statusText = 'All 5 fractional contracts active. €25M/turn guaranteed floor income.'
                  } else if (contracts > 0) {
                    statusColor = 'border-blue-500'
                    statusBadge = <span className="text-xs bg-blue-700 text-blue-100 px-2 py-0.5 rounded-full">Active</span>
                    statusText = `Run more successful Scientific missions to add contracts (${contracts}/${maxContracts}).`
                  } else if (hasSpaceport) {
                    statusColor = 'border-yellow-600'
                    statusBadge = <span className="text-xs bg-yellow-700 text-yellow-100 px-2 py-0.5 rounded-full">Ready — No Contracts Yet</span>
                    statusText = 'Spaceport is operational. Each successful Scientific mission adds 1 contract.'
                  } else if (buildingSpaceport) {
                    statusColor = 'border-blue-700'
                    statusBadge = <span className="text-xs bg-blue-900 text-blue-200 px-2 py-0.5 rounded-full">Spaceport Building…</span>
                    statusText = 'Spaceport completes next turn. Then run Scientific missions to earn contracts.'
                  } else {
                    statusColor = 'border-gray-700'
                    statusBadge = <span className="text-xs bg-gray-700 text-gray-300 px-2 py-0.5 rounded-full">Locked</span>
                    statusText = 'Requires a Dedicated Commercial Spaceport (€300M). Order it via the control panel.'
                  }

                  return (
                    <div className={`bg-gray-800 rounded-lg p-4 border ${statusColor} mb-6`}>
                      <div className="flex items-center justify-between mb-3">
                        <div className="flex items-center gap-2">
                          <span className="text-lg">🔬</span>
                          <h3 className="font-semibold">SPaaS — Fractional Research Contracts</h3>
                        </div>
                        {statusBadge}
                      </div>

                      {/* Contract progress + ARR */}
                      <div className="grid grid-cols-2 gap-4 mb-4">
                        <div className="bg-gray-700 rounded p-3">
                          <div className="text-xs text-gray-400 mb-1">Active Contracts</div>
                          <div className="flex items-end gap-2">
                            <span className="text-3xl font-bold text-blue-400">{contracts}</span>
                            <span className="text-gray-500 text-sm mb-1">/ {maxContracts}</span>
                          </div>
                          {/* Progress dots */}
                          <div className="flex gap-1 mt-2">
                            {Array.from({ length: maxContracts }).map((_, i) => (
                              <div
                                key={i}
                                className={`h-2 flex-1 rounded-full ${i < contracts ? 'bg-blue-500' : 'bg-gray-600'}`}
                              />
                            ))}
                          </div>
                        </div>
                        <div className="bg-gray-700 rounded p-3">
                          <div className="text-xs text-gray-400 mb-1">Guaranteed ARR / Turn</div>
                          <div className="flex items-end gap-1">
                            <span className={`text-3xl font-bold ${arrPerTurn > 0 ? 'text-green-400' : 'text-gray-500'}`}>
                              €{arrPerTurn}M
                            </span>
                          </div>
                          <div className="text-xs text-gray-500 mt-2">
                            Paid every turn regardless of mission outcome
                          </div>
                        </div>
                      </div>

                      {/* How to get it */}
                      <div className="text-xs space-y-1 mb-3">
                        <div className="text-gray-400 font-semibold uppercase tracking-wide mb-2">How to unlock</div>
                        <div className="flex items-start gap-2">
                          <span className={hasSpaceport ? 'text-green-400' : buildingSpaceport ? 'text-yellow-400' : 'text-gray-500'}>
                            {hasSpaceport ? '✓' : buildingSpaceport ? '⏳' : '○'}
                          </span>
                          <span className={hasSpaceport ? 'text-green-300' : 'text-gray-400'}>
                            Step 1 — Build a Dedicated Commercial Spaceport (€300M, 1-turn build)
                          </span>
                        </div>
                        <div className="flex items-start gap-2">
                          <span className={contracts > 0 ? 'text-green-400' : hasSpaceport ? 'text-yellow-400' : 'text-gray-500'}>
                            {contracts > 0 ? '✓' : '○'}
                          </span>
                          <span className={contracts > 0 ? 'text-green-300' : 'text-gray-400'}>
                            Step 2 — Run Scientific missions. Each success adds 1 contract (max 5)
                          </span>
                        </div>
                      </div>

                      <div className="text-xs text-gray-500 border-t border-gray-700 pt-2">
                        {statusText}
                        {contracts === maxContracts && (
                          <span className="ml-1 text-green-400">At max: €25M/turn floor — mission failures no longer threaten bankruptcy.</span>
                        )}
                      </div>
                    </div>
                  )
                })()}

                {/* Cost Breakdown */}
                <div className="bg-gray-800 rounded-lg p-4 border border-gray-700">
                  <h3 className="font-semibold mb-2">Cost Breakdown (Per Mission)</h3>
                  <div className="grid grid-cols-2 gap-4 text-sm">
                    <div>
                      <div className="flex justify-between mb-1">
                        <span className="text-gray-400">Fixed Costs:</span>
                        <span className="font-semibold text-blue-400">€5.0M</span>
                      </div>
                      <div className="text-xs text-gray-500">Maintenance, salaries, facilities</div>
                    </div>
                    <div>
                      <div className="flex justify-between mb-1">
                        <span className="text-gray-400">Variable Costs:</span>
                        <span className="font-semibold text-orange-400">
                          €{(() => {
                            // Calculate variable costs based on current state
                            const baseVariable = 35_000_000; // €15M fuel + €20M launch
                            const greenReduction = 1.0 - (gameState.green_tech_level * 0.01);
                            let variable = baseVariable * greenReduction;
                            
                            // Apply reusable stage 1 reduction (20%)
                            if (gameState.tech_unlocks?.reusable_stage1) {
                              variable *= 0.8;
                            }
                            
                            // Apply HR efficiency
                            if (gameState.hr_efficiency) {
                              variable /= gameState.hr_efficiency;
                            }
                            
                            return (variable / 1_000_000).toFixed(1);
                          })()}M
                        </span>
                      </div>
                      <div className="text-xs text-gray-500">
                        Fuel + Launch (reduced by Green Tech, Reusable Stage 1, HR)
                      </div>
                    </div>
                  </div>
                  <div className="mt-3 pt-3 border-t border-gray-700 text-xs text-gray-500">
                    <div>• Fixed Costs: Constant €5M per turn (doesn't change)</div>
                    <div>• Variable Costs: Base €35M, reduced by Green Tech (-1% per level), Reusable Stage 1 (-20%), and HR Efficiency</div>
                  </div>
                </div>
              </div>
            )}

            {currentTab === 'research' && (
              <ResearchTab
                techLevel={gameState.tech_level}
                greenTechLevel={gameState.green_tech_level}
                techUnlocks={gameState.tech_unlocks}
              />
            )}

            {currentTab === 'analytics' && (
              <AnalyticsCharts history={history} marketScenario={marketScenario} />
            )}
            {currentTab === 'financial' && (
              <div className="p-8">
                <FinancialDirectorTab history={history.map(h => ({
                  year: h.year,
                  profit: h.profit,
                  revenue: h.revenue || 0,
                  costs: h.costs || 0
                }))} />
              </div>
            )}
            {currentTab === 'investor' && (
              <InvestorTab
                gameState={gameState}
                onStateUpdate={(newState) => {
                  setGameState(prev => prev ? { ...prev, ...newState } : null)
                }}
              />
            )}
            {currentTab === 'playthrough' && (
              <PlaythroughViewer />
            )}
          </div>
        </div>
      </div>
      {showModal && lastResult && (
        <ReportCardModal result={lastResult} onClose={closeModal} />
      )}
      {showWinScreen && finalScore && gameOverReason && (
        <WinScreen
          score={finalScore}
          gameOverReason={gameOverReason}
          onClose={() => setShowWinScreen(false)}
          onRestart={() => {
            setShowWinScreen(false)
            setFinalScore(null)
            setGameOverReason(null)
            startGame()
          }}
        />
      )}
    </div>
  )
}

export default function AppWithBoundary() {
  return (
    <ErrorBoundary>
      <App />
    </ErrorBoundary>
  )
}
