import { useState, useEffect } from 'react'
import axios from 'axios'
import TopBar from './components/TopBar'
import ControlPanel from './components/ControlPanel'
import ReportCardModal from './components/ReportCardModal'
import NewsTicker from './components/NewsTicker'
import ResearchTab from './components/ResearchTab'
import AnalyticsCharts from './components/AnalyticsCharts'
import FinancialDirectorTab from './components/FinancialDirectorTab'
import InvestorTab from './components/InvestorTab'
import Advisor from './components/Advisor'
import MissionForecast from './components/MissionForecast'
import WinScreen from './components/WinScreen'
import './App.css'

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000'

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
  }
  new_state: GameState
  game_over?: boolean
  game_over_reason?: 'max_years' | 'bankruptcy'
}

interface HistoryData {
  year: number
  profit: number
  reputation: number
  budget: number
  revenue?: number
  costs?: number
}

type Tab = 'dashboard' | 'research' | 'analytics' | 'financial' | 'investor'

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
  }) => {
    // Update current inputs for Mission Forecast
    setCurrentInputs({
      ...inputs,
      buy_vehicle: false,
      investor_offer: currentInputs.investor_offer || 0
    })
    setLoading(true)
    try {
      const response = await axios.post<TurnResult>(`${API_BASE_URL}/play_turn`, inputs)
      setLastResult(response.data)
      setGameState(response.data.new_state)
      setCompetitorNews(response.data.results.competitor_news)
      
      // Add to history
      setHistory(prev => [...prev, {
        year: response.data.new_state.year,
        profit: response.data.financials.profit,
        reputation: response.data.new_state.reputation,
        budget: response.data.new_state.budget,
        revenue: response.data.financials.revenue,
        costs: response.data.financials.costs?.total_costs || 0
      }])
      
      // Check for game over
      if (response.data.game_over) {
        setGameOverReason(response.data.game_over_reason || 'max_years')
        // Fetch final score
        try {
          const scoreResponse = await axios.get(`${API_BASE_URL}/final_score`)
          setFinalScore(scoreResponse.data)
          setShowWinScreen(true)
        } catch (error) {
          console.error('Error fetching final score:', error)
          setShowWinScreen(true) // Show anyway
        }
      } else {
        setShowModal(true)
      }
    } catch (error) {
      console.error('Error playing turn:', error)
      alert('Failed to play turn. Check console for details.')
    } finally {
      setLoading(false)
    }
  }

  const closeModal = () => {
    setShowModal(false)
  }

  if (!gameState) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-900">
        <div className="text-white text-xl">Loading game...</div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-900 text-white">
      <TopBar gameState={gameState} />
      <NewsTicker news={newsFeed.length > 0 ? newsFeed[currentNewsIndex] : competitorNews} />
      <div className="flex">
        <ControlPanel 
          onLaunch={playTurn} 
          loading={loading}
          safetyTechLevel={gameState.safety_tech_level}
          gameState={gameState}
          onInputsChange={setCurrentInputs}
        />
        <div className="flex-1">
          {/* Tabs */}
          <div className="border-b border-gray-700 bg-gray-800">
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
            </div>
          </div>

          {/* Tab Content */}
          <div className="h-[calc(100vh-200px)] overflow-y-auto">
            {currentTab === 'dashboard' && (
              <div className="p-8">
                <h2 className="text-2xl font-bold mb-4">Dashboard</h2>
                <Advisor gameState={gameState} />
                <p className="text-gray-400 mb-6">
                  Welcome to M.A.R.S. - Market Analysis & Risk Simulation
                </p>
                
                {/* Mission Forecast in Dashboard */}
                <div className="mb-6">
                  <MissionForecast inputs={currentInputs} />
                </div>
                <div className="grid grid-cols-2 gap-4 mb-4">
                  <div className="bg-gray-800 rounded-lg p-4 border border-gray-700">
                    <h3 className="font-semibold mb-2">Current Status</h3>
                    <div className="space-y-2 text-sm">
                      <div className="flex justify-between">
                        <span className="text-gray-400">Budget:</span>
                        <span className="font-semibold text-green-400">
                          €{(gameState.budget / 1_000_000).toFixed(0)}M
                        </span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-gray-400">Reputation:</span>
                        <span className="font-semibold text-yellow-400">
                          {gameState.reputation.toFixed(1)}/100
                        </span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-gray-400">CO2 Impact:</span>
                        <span className="font-semibold text-red-400">
                          {gameState.co2_impact.toFixed(1)}
                        </span>
                      </div>
                    </div>
                  </div>
                  <div className="bg-gray-800 rounded-lg p-4 border border-gray-700">
                    <h3 className="font-semibold mb-2">Tech Status</h3>
                    <div className="space-y-2 text-sm">
                      <div className="flex justify-between">
                        <span className="text-gray-400">R&D Level:</span>
                        <span className="font-semibold text-purple-400">
                          {gameState.tech_level}
                        </span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-gray-400">Green Tech:</span>
                        <span className="font-semibold text-emerald-400">
                          {gameState.green_tech_level}
                        </span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-gray-400">Competitor Price:</span>
                        <span className="font-semibold">
                          €{(gameState.competitor_price / 1_000_000).toFixed(1)}M
                        </span>
                      </div>
                    </div>
                  </div>
                </div>
                
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
              <AnalyticsCharts history={history} />
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
              <div className="h-[calc(100vh-200px)] overflow-y-auto">
                <InvestorTab 
                  gameState={gameState} 
                  onStateUpdate={(newState) => {
                    // Update game state immediately with new budget and offer history
                    setGameState(prev => prev ? { ...prev, ...newState } : null)
                  }}
                />
              </div>
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

export default App
