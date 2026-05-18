import { useState, useEffect, useRef } from 'react'
import { createPortal } from 'react-dom'

interface GameSnapshot {
  budget: number
  reputation: number
  year: number
  tech_level: number
  green_tech_level: number
  safety_tech_level?: number
  co2_impact: number
  hr_efficiency?: number
  competitor_price?: number
  tech_unlocks?: { reusable_stage1: boolean; green_hydrogen: boolean }
}

interface NewsTickerProps {
  news: string
  gameState?: GameSnapshot
}

const SUBORBITAL_COMPETITORS = [
  { name: 'Virgin Galactic',          price: 450_000,  safety: 65, share: '25%', color: 'text-pink-400',   note: 'SpaceShipIII — suspended ops 2023' },
  { name: 'Blue Origin (New Shepard)', price: 500_000,  safety: 82, share: '35%', color: 'text-cyan-400',   note: '2022 anomaly, returned 2024' },
]
const SUBORBITAL_AVG_PRICE  = Math.round((450_000 * 0.25 + 500_000 * 0.35) / 0.60)  // ~€479k
const SUBORBITAL_AVG_SAFETY = Math.round((65 * 0.25 + 82 * 0.35) / 0.60)            // ~75

const ORBITAL_COMPETITORS = [
  { name: 'SpaceX Dragon', price: 8_000_000,  safety: 90, share: '45%', color: 'text-blue-400',   note: 'Market leader, ISS crew & tourist runs' },
  { name: 'Blue Origin',   price: 12_000_000, safety: 75, share: '25%', color: 'text-sky-400',    note: 'New Glenn, orbital station ambitions' },
  { name: 'Axiom Space',   price: 15_000_000, safety: 80, share: '20%', color: 'text-violet-400', note: 'ISS commercial modules, private station' },
]
const ORBITAL_AVG_PRICE  = Math.round((8_000_000 * 0.45 + 12_000_000 * 0.25 + 15_000_000 * 0.20) / 0.90)  // ~€10.67M
const ORBITAL_AVG_SAFETY = Math.round((90 * 0.45 + 75 * 0.25 + 80 * 0.20) / 0.90)                          // ~85

function fmt(n: number) {
  if (n >= 1_000_000_000) return `€${(n / 1_000_000_000).toFixed(2)}B`
  if (n >= 1_000_000)     return `€${(n / 1_000_000).toFixed(1)}M`
  return `€${n.toLocaleString()}`
}

function getAdvisorTips(gs: GameSnapshot): { icon: string; text: string; color: string }[] {
  const tips = []
  if (gs.budget < 0)
    tips.push({ icon: '🚨', text: 'Budget is negative — bankruptcy risk next turn if costs aren\'t covered.', color: 'text-red-400' })
  else if (gs.budget < 50_000_000)
    tips.push({ icon: '⚠️', text: 'Cash reserves critical. Play a low-risk Short Suborbital to stay solvent.', color: 'text-yellow-400' })
  if (gs.reputation < 30)
    tips.push({ icon: '⚠️', text: 'Reputation in danger zone. One more failure could collapse demand entirely.', color: 'text-yellow-400' })
  if ((gs.safety_tech_level ?? 0) < 5)
    tips.push({ icon: '💡', text: `Safety Tech ${gs.safety_tech_level ?? 0}/5 — invest €10M/turn in Safety to unlock Long Orbital.`, color: 'text-blue-400' })
  if (!gs.tech_unlocks?.reusable_stage1 && gs.tech_level >= 7)
    tips.push({ icon: '💡', text: `Tech Level ${gs.tech_level}/10 — a few more R&D turns unlock Reusable Stage 1 (−20% costs).`, color: 'text-purple-400' })
  if (gs.tech_unlocks?.reusable_stage1 && !gs.tech_unlocks?.green_hydrogen)
    tips.push({ icon: '💡', text: `Tech Level ${gs.tech_level}/20 — keep investing in R&D to unlock Green Hydrogen (−50% CO₂).`, color: 'text-emerald-400' })
  if (gs.co2_impact > 400)
    tips.push({ icon: '🌍', text: 'CO₂ impact very high. Green Investment and Green Hydrogen unlock will reduce this.', color: 'text-emerald-400' })
  if (tips.length === 0)
    tips.push({ icon: '✅', text: 'Operations look healthy. Focus on growing market share and R&D investment.', color: 'text-green-400' })
  return tips
}

function MarketPanel({ gameState, top }: { gameState: GameSnapshot; top: number }) {
  const safetyTech   = gameState.safety_tech_level ?? 0
  const advisorTips  = getAdvisorTips(gameState)

  return createPortal(
    <div
      className="fixed left-0 right-0 z-[9999] px-4 pt-1"
      style={{ top, filter: 'drop-shadow(0 8px 24px rgba(0,0,0,0.85))' }}
    >
      <div className="rounded-xl border border-gray-600 bg-gray-900 p-4">
        <div className="grid grid-cols-3 gap-6">

          {/* ── Competitor Landscape ── */}
          <div>
            <div className="text-xs font-bold text-gray-400 uppercase tracking-wider mb-2">🏁 Competitor Landscape</div>

            {/* Suborbital segment */}
            <div className="mb-3">
              <div className="text-xs font-semibold text-pink-400 mb-1.5">🪂 Suborbital Market</div>
              <div className="space-y-1.5">
                {SUBORBITAL_COMPETITORS.map((c) => (
                  <div key={c.name} className="text-xs">
                    <div className="flex items-center justify-between">
                      <span className={`font-semibold ${c.color}`}>{c.name}</span>
                      <span className="text-gray-400">{c.share} share</span>
                    </div>
                    <div className="flex gap-3 text-gray-500 mt-0.5">
                      <span>Price: <span className="text-white">{fmt(c.price)}</span></span>
                      <span>Safety: <span className="text-orange-300">{c.safety}/100</span></span>
                    </div>
                    <div className="text-gray-600 text-xs">{c.note}</div>
                  </div>
                ))}
              </div>
              <div className="mt-1.5 text-xs space-y-0.5 text-gray-500">
                <div className="flex justify-between">
                  <span>Avg price</span>
                  <span className="text-white font-bold">{fmt(SUBORBITAL_AVG_PRICE)}</span>
                </div>
                <div className="flex justify-between">
                  <span>Avg safety · Combined share</span>
                  <span className="text-orange-300">{SUBORBITAL_AVG_SAFETY}/100 · 60% (you: 40%)</span>
                </div>
                <div className="text-gray-600">📈 Price below {fmt(SUBORBITAL_AVG_PRICE)} to steal suborbital share</div>
              </div>
            </div>

            <div className="border-t border-gray-700 my-2" />

            {/* Orbital segment */}
            <div>
              <div className="text-xs font-semibold text-blue-400 mb-1.5">🛸 Orbital Market</div>
              <div className="space-y-1.5">
                {ORBITAL_COMPETITORS.map((c) => (
                  <div key={c.name} className="text-xs">
                    <div className="flex items-center justify-between">
                      <span className={`font-semibold ${c.color}`}>{c.name}</span>
                      <span className="text-gray-400">{c.share} share</span>
                    </div>
                    <div className="flex gap-3 text-gray-500 mt-0.5">
                      <span>Price: <span className="text-white">{fmt(c.price)}</span></span>
                      <span>Safety: <span className="text-orange-300">{c.safety}/100</span></span>
                    </div>
                    <div className="text-gray-600 text-xs">{c.note}</div>
                  </div>
                ))}
              </div>
              <div className="mt-1.5 text-xs space-y-0.5 text-gray-500">
                <div className="flex justify-between">
                  <span>Avg price</span>
                  <span className="text-white font-bold">{fmt(ORBITAL_AVG_PRICE)}</span>
                </div>
                <div className="flex justify-between">
                  <span>Avg safety · Combined share</span>
                  <span className="text-orange-300">{ORBITAL_AVG_SAFETY}/100 · 90% (you: 10%)</span>
                </div>
                <div className="text-gray-600">📈 Price below {fmt(ORBITAL_AVG_PRICE)} · 🛡️ Safety above {ORBITAL_AVG_SAFETY} for +10% share</div>
              </div>
            </div>
          </div>

          {/* ── Advisor ── */}
          <div>
            <div className="text-xs font-bold text-gray-400 uppercase tracking-wider mb-2">💬 Advisor · Year {gameState.year}</div>
            <div className="space-y-2">
              {advisorTips.map((tip, i) => (
                <div key={i} className="flex items-start gap-2 text-xs">
                  <span className="shrink-0 mt-0.5">{tip.icon}</span>
                  <span className={tip.color}>{tip.text}</span>
                </div>
              ))}
            </div>
          </div>

          {/* ── Market Intelligence ── */}
          <div>
            <div className="text-xs font-bold text-gray-400 uppercase tracking-wider mb-2">🧠 Tech & Unlock Status</div>
            <div className="space-y-1.5 text-xs">
              <div className="flex items-start gap-1.5">
                <span className="shrink-0">{gameState.tech_unlocks?.reusable_stage1 ? '✅' : '⬜'}</span>
                <span className={gameState.tech_unlocks?.reusable_stage1 ? 'text-green-400' : 'text-gray-500'}>
                  Reusable Stage 1 {gameState.tech_unlocks?.reusable_stage1 ? '— −20% launch costs (active)' : `— needs 10 R&D pts (have ${gameState.tech_level})`}
                </span>
              </div>
              <div className="flex items-start gap-1.5">
                <span className="shrink-0">{gameState.tech_unlocks?.green_hydrogen ? '✅' : '⬜'}</span>
                <span className={gameState.tech_unlocks?.green_hydrogen ? 'text-green-400' : 'text-gray-500'}>
                  Green Hydrogen {gameState.tech_unlocks?.green_hydrogen ? '— −50% CO₂ (active)' : `— needs 20 R&D pts (have ${gameState.tech_level})`}
                </span>
              </div>
              <div className="flex items-start gap-1.5">
                <span className="shrink-0">{safetyTech >= 5 ? '✅' : '⚠️'}</span>
                <span className={safetyTech >= 5 ? 'text-green-400' : 'text-yellow-400'}>
                  Long Orbital {safetyTech >= 5 ? `— unlocked (Safety Tech ${safetyTech})` : `— needs Safety Tech 5 (have ${safetyTech})`}
                </span>
              </div>
              <div className="border-t border-gray-700 pt-1.5 space-y-1 text-gray-400">
                <div>💰 €10M R&D/turn = +1 Tech Point</div>
                <div>🛡️ €10M Safety/turn = +1 Safety Tech Level</div>
                <div>🌿 €10M Green/turn = +1 Green Tech Level (reduces variable costs)</div>
                <div>📊 Scientific missions grant bonus R&D on success</div>
              </div>
            </div>
          </div>

        </div>
      </div>
    </div>,
    document.body
  )
}

export default function NewsTicker({ news, gameState }: NewsTickerProps) {
  const [displayNews, setDisplayNews] = useState(news)
  const [fade, setFade]               = useState(false)
  const [hovered, setHovered]         = useState(false)
  const [panelTop, setPanelTop]       = useState(0)
  const barRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    if (news !== displayNews) {
      setFade(true)
      setTimeout(() => { setDisplayNews(news); setFade(false) }, 300)
    }
  }, [news, displayNews])

  const handleMouseEnter = () => {
    if (barRef.current) {
      const rect = barRef.current.getBoundingClientRect()
      setPanelTop(rect.bottom)
    }
    setHovered(true)
  }

  const isJoke        = displayNews.startsWith('💡')
  const isPriceUpdate = displayNews.includes('Market Update:')

  return (
    <div
      ref={barRef}
      onMouseEnter={handleMouseEnter}
      onMouseLeave={() => setHovered(false)}
      className={`border-t border-b py-2 px-4 cursor-default transition-colors duration-300 ${
        isJoke        ? 'bg-purple-900/30 border-purple-700' :
        isPriceUpdate ? 'bg-blue-900/30 border-blue-700'     :
        'bg-gray-800 border-gray-700'
      }`}
    >
      <div className="flex items-center gap-4">
        <span className={`font-bold text-sm whitespace-nowrap ${
          isJoke        ? 'text-purple-400' :
          isPriceUpdate ? 'text-blue-400'   :
          'text-yellow-400'
        }`}>
          {isJoke ? '😄 JOKE:' : isPriceUpdate ? '📊 MARKET:' : '📰 NEWS:'}
        </span>
        <div className="flex-1 overflow-hidden">
          <div className={`text-sm text-gray-300 whitespace-nowrap transition-opacity duration-300 ${fade ? 'opacity-0' : 'opacity-100'}`}>
            {displayNews}
          </div>
        </div>
        <span className="text-xs text-gray-600 whitespace-nowrap select-none">hover for market intel ↓</span>
      </div>

      {hovered && gameState && <MarketPanel gameState={gameState} top={panelTop} />}
    </div>
  )
}
