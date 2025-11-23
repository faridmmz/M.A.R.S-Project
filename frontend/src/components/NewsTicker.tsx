import { useState, useEffect } from 'react'

interface NewsTickerProps {
  news: string
}

export default function NewsTicker({ news }: NewsTickerProps) {
  const [displayNews, setDisplayNews] = useState(news)
  const [fade, setFade] = useState(false)

  // Fade out/in when news changes
  useEffect(() => {
    if (news !== displayNews) {
      setFade(true)
      setTimeout(() => {
        setDisplayNews(news)
        setFade(false)
      }, 300) // Fade out duration
    }
  }, [news, displayNews])

  // Determine if it's a joke (starts with 💡)
  const isJoke = displayNews.startsWith('💡')
  const isPriceUpdate = displayNews.includes('Market Update:')
  
  return (
    <div className={`border-t border-b py-2 px-4 overflow-hidden transition-colors duration-300 ${
      isJoke ? 'bg-purple-900/30 border-purple-700' : 
      isPriceUpdate ? 'bg-blue-900/30 border-blue-700' : 
      'bg-gray-800 border-gray-700'
    }`}>
      <div className="flex items-center gap-4">
        <span className={`font-bold text-sm whitespace-nowrap transition-colors duration-300 ${
          isJoke ? 'text-purple-400' : 
          isPriceUpdate ? 'text-blue-400' : 
          'text-yellow-400'
        }`}>
          {isJoke ? '😄 JOKE:' : isPriceUpdate ? '📊 MARKET:' : '📰 NEWS:'}
        </span>
        <div className="flex-1 overflow-hidden">
          <div className={`text-sm text-gray-300 whitespace-nowrap transition-opacity duration-300 ${
            fade ? 'opacity-0' : 'opacity-100'
          }`}>
            {displayNews}
          </div>
        </div>
      </div>
    </div>
  )
}

